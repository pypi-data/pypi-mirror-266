import sys
import os
import time

from datetime import datetime, timedelta
from typing import List, Any, Union

import names_generator
import numpy as np

import cv2
from queue import Queue, Empty as EmptyQueue
import threading

from multiprocessing import Queue as mQueue

import degirum as dg
import degirum_tools
import urllib

from names_generator import generate_name
from validators import ipv4, url

from pathlib import Path
Path(__file__).resolve()

from ..config_rt import ConfigRT
from ..Data.face_data import FaceData, FrameData, EmbeddedFaceData, LabelData
from ..Database.vectstore import VectStore

from ..norfair.tracker import Detection, Tracker, TrackedObject, set_global_count


default_config = {
    'track_selected': False,
    'use_tracker': True,
    'use_embedder': True,
    'embeddings_time_step': 0.5,
    'show_scores': False,
    'detector_score_th': 0.6,
    'face_accept_th': 0.35,
    'face_reject_th': 0.40,
    'start_paused': False,

    'show_landmarks': False,
    'use_landmarks': True,
    'use_normalization': False,

    'auto_labels': True,

    'save_video_path': "",

    'db_path': "embeds.db",

    'camera':
        {
            'camera_id': 0,
            'fps': -1,
            'loop': False,
            'max_frames': -1,
            'show_frames': True,
        },
    'detector':
        {
            'cloud_url': "https://cs.degirum.com/degirum/widerface",
            'local_zoo_path': "",
            'model': "yolov8s_relu6_widerface--640x640_quant_n2x_orca1_3",
            'image_backend': "opencv",
            'input_numpy_colorspace': 'BGR'
        }
}


def normalize_landmarks(landmarks):
    features = ['LeftEye', 'RightEye', 'Nose', 'LeftLipCorner', 'RightLipCorner']
    if isinstance(landmarks, list) and all([isinstance(p, float) for p in landmarks]):
        norm = []
        pnt = []
        i = 0
        for p in landmarks:
            pnt.append(p)
            if len(pnt) == 2:
                norm.append({
                    'category_id': i,
                    'connect': [],
                    'label': features[i],
                    'landmark': pnt,
                    'score': 1.0
                })
                pnt = []
                i += 1
        return norm
    elif isinstance(landmarks, list) and any(['label' not in pnt for pnt in landmarks]):
        return [{'category_id': i,
                 'connect': [],
                 'label': features[pnt['category_id']],
                 'landmark': pnt['landmark'],
                 'score': 1.0} for i, pnt in enumerate(landmarks)]
    else:
        return landmarks


def landmark2points(landmarks):
    flt = lambda feature: [lm['landmark'] for lm in landmarks if lm['label'] == feature][0]
    return [flt('LeftEye'),
            flt('RightEye'),
            flt('Nose'),
            flt('LeftLipCorner'),
            flt('RightLipCorner')]


def get_landmark(landmarks: list, feature: str):
    for m in landmarks:
        if m['label'] == feature:
            return m
    return None

def check_detection_quality(bbox, base, size_th, ratio_th):
    dx = abs(bbox[0] - bbox[2])
    dy = abs(bbox[1] - bbox[3])
    dmax = max(dx, dy)
    dmin = min(dx, dy)

    return dmax/(base + 1) > size_th and dmin / (dmax + 1) > ratio_th


def check_face_quality(landmarks):
    nose = get_landmark(landmarks, "Nose")
    if nose is None:
        return False
    x_nose = nose["landmark"][0]

    left_eye = get_landmark(landmarks, "LeftEye")
    if left_eye is None:
        return False

    rite_eye = get_landmark(landmarks, "RightEye")
    if rite_eye is None:
        return False

    x_left_eye = min(left_eye["landmark"][0], rite_eye["landmark"][0])
    x_rite_eye = max(left_eye["landmark"][0], rite_eye["landmark"][0])
    dx = x_rite_eye - x_left_eye
    # print(f"dx = {dx:.2f}")
    if dx < 18:
        return False

    dx *= 0.1

    return x_left_eye - dx < x_nose < x_rite_eye + dx


def result2detection(yolo_result, use_landmarks: bool = False, score_th: float = -1.0) -> Detection:
    for res_id, res in enumerate(yolo_result.results):
        face_data = FaceData()
        label: str   = res.setdefault('label', "")
        score: float = res.setdefault('score', 0.0)
        if "face" in label.lower()  and score >= score_th:
            bbox = [int(coord) for coord in res.setdefault('bbox', [])]
            if len(bbox) != 4:
                continue
            face_data.set_bbox(bbox)
            if use_landmarks:
                landmarks = res.setdefault('landmarks', [])
                landmarks = normalize_landmarks(landmarks)
                if len(landmarks) != 5:
                    continue
                if not check_detection_quality(bbox, base=max(yolo_result.image.shape), size_th=0.1, ratio_th=0.4):
                    continue
                face_data.set_landmarks(landmarks)
            # face_data.set_face_score(score)
            face_data.add_property('res_id', res_id)
            yield convert2detection(face_data)


def convert2detection(data: Any) -> Detection:
    points = data.get_bbox()
    try:
        landmarks = data.get_landmarks()
        landmarks = landmark2points(data.get_landmarks())
        for p in landmarks:
            points.extend([p[0], p[1]])
    except:
        landmarks = None

    points = np.reshape(points, (-1, 2))
    global_id = data.get_property('global_id')

    object_name = data.get_property('label', "unknown")

    try:
        face_id = data.get_face_uuid()
    except:
        face_id = None

    try:
        object_id = data.get_property('object_id')
    except:
        object_id = None

    try:
        embedding = data.get_embeddings()
    except:
        embedding = None

    try:
        face_score = data.get_face_score()
    except:
        face_score = -1.0

    dt = Detection(points=points,
                   label="face",
                   object_name=object_name,
                   object_id=face_id,
                   object_score=face_score,
                   global_id=global_id,
                   id=object_id,
                   embedding=embedding)

    return dt


def objects2results(objects: List[TrackedObject], show_landmarks: bool) -> list:
    results = []
    for obj in objects:
        points = obj.estimate.flatten().tolist()
        bbox = points[:4]
        landmarks = []
        if len(points) > 4:
            for i in range(4, len(points), 2):
                landmarks.append([points[i], points[i+1]])
        label = obj.object_name if obj.object_name != "unknown" else ""  # str(obj.id)
        res = {
            'bbox': bbox,
            'category_id': 0,
            'label': label,
            'score': 1.0,  # TODO: add TrackedObject.score computation
               }
        if show_landmarks:
            res['landmarks'] = normalize_landmarks(landmarks)
        results.append(res)
    return results


def show_scores(results) -> None:
    for res in results:
        res['label'] = str(res['score'])


def get_face_img(src_image, face_data: FaceData, use_normalization: bool):
    bbox = face_data.get_bbox()
    if bbox is None:
        return None

    landmarks = face_data.get_landmarks()
    if landmarks is None:
        use_normalization = False

    if use_normalization:
        face_shift = np.array([bbox[0], bbox[1]])

        flt = lambda feature: [lm['landmark'] for lm in landmarks if lm['label'] == feature][0]
        src_face_mask = np.array([flt('LeftEye'),
                                  flt('RightEye'),
                                  flt('Nose'),
                                  flt('LipsleftCorner'),
                                  flt('LipsRightCorner')])

        dst_face_mask = np.array(
            [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
             [41.5493, 92.3655], [70.7299, 92.2041]],
            dtype=np.float32)
        dst_face_mask += face_shift

        d = 15
        dst_face_mask -= np.array([d, 0])
        dst_dsize = (112 - 2*d, 112)

        M, tmp = cv2.estimateAffinePartial2D(src_face_mask, dst_face_mask)

        rows, cols, _ = src_image.shape
        dst_image = cv2.warpAffine(src_image, M, (cols, rows))

        face_img = dst_image[int(bbox[1]):int(bbox[1]+dst_dsize[1]-1), int(bbox[0]):int(bbox[0]+dst_dsize[0]-1)]
    else:
        face_img = src_image[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]

    return face_img


class FaceTrackerDemo(threading.Thread):
    def __init__(self, q_in=None, config_name=None):
        self.proc_id = "face_tracker"
        super(FaceTrackerDemo, self).__init__()

        self.deployment = os.environ['DG_DEPLOYMENT']
        self.cloud_token = degirum_tools.get_token() if self.deployment.lower() == "cloud" else ""

        self.stop_event = threading.Event()
        self.paused = False
        self.first_frame = True
        self.start_paused = False

        self.q_in = q_in
        self.q_out_map: dict = {}

        self.mouse_clicks_q = Queue()

        self.face_accept_th = 0.1

        self.track_selected = False

        self.use_tracker = True
        self.use_embedder = True

        self.show_scores = False
        self.detector_score_th = 0.1   # face detections acceptance threshold

        self.show_landmarks = False
        self.use_landmarks = False
        self.use_normalization = False
        self.prev_time = 0
        self.embeddings_time_step = 1
        self.auto_labels = True

        self.stream = None

        self.camera_cfg: dict = {}
        self.fps = -1
        self.loop = False
        self.max_frames = -1
        self.is_file_input = False

        self.detector_cfg: dict = {}
        self.detect_model = None

        self.tracker = Tracker(distance_function="euclidean", distance_threshold=100)
        self.result_queue = Queue()  # result queue

        self.vstore = VectStore(max_size=32)  # 32 samples per track

        # display thread
        self.display_thread = threading.Thread(target=self.result_process, args=())

        self.video_writer = None

        self.db_path = ""

        print(f"FaceTrackerDemo: Starting name generator: {names_generator.generate_name(seed=42)}")

        # Starting real-time config tracking service
        if config_name is None:
            config_name = self.__class__.__name__
        try:
            self.config = ConfigRT(config_name)
            self.apply_config()
        except Exception as e:
            self.config.stop()
            raise e

        self.frames_processed = 0
        self.start_time = 0

    @property
    def camera_id(self):
        return self.camera_cfg['camera_id']

    @property
    def show_frames(self):
        return self.camera_cfg['show_frames']

    def display_paused(self):
        blank_image = np.zeros((40, 300, 3), np.uint8)
        cv2.putText(blank_image,
                    "Paused...press 'Space' to continue",
                    (5, 32),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255))
        cv2.imshow("paused", blank_image)
        key = cv2.waitKey(0) & 0xFF
        if key == 32:
            cv2.destroyWindow("paused")
            self.paused = False

    def get_id(self):
        """
        Returns source id
        :return: str
        """
        return self.proc_id

    def apply_config(self):
        """
        Try to apply config.
        If failed, but there is a valid configuration setup already, the new one will be ignored
        """
        if not self.config.is_modified():
            return

        self.track_selected = self.config.get('track_selected',  default_config["track_selected"])
        self.use_tracker  = self.config.get('use_tracker',  default_config["use_tracker"])
        self.use_embedder = self.config.get('use_embedder', default_config["use_embedder"])
        self.embeddings_time_step = self.config.get('embeddings_time_step', default_config["embeddings_time_step"])
        self.show_scores = self.config.get('show_scores', default_config["show_scores"])
        self.detector_score_th = self.config.get('detector_score_th', default_config["detector_score_th"])
        self.face_accept_th = self.config.get('face_accept_th', default_config["face_accept_th"])
        self.face_reject_th = self.config.get('face_reject_th', default_config["face_reject_th"])

        self.start_paused = self.config.get('start_paused', default_config["start_paused"])

        self.show_landmarks = self.config.get('show_landmarks', default_config["show_landmarks"])
        self.use_landmarks = self.config.get('use_landmarks', default_config["use_landmarks"])
        self.use_normalization = self.config.get('use_normalization', default_config["use_normalization"])

        self.auto_labels = self.config.get('auto_labels', default_config["auto_labels"])

        self.db_path = self.config.get('db_path', default_config["db_path"])
        try:
            vstore = VectStore.load(self.db_path)
            if vstore is not None:
                global_id = vstore.max_metadata('global_id')
                if global_id is not None:
                    set_global_count(global_id + 1)
                self.vstore = vstore

        except Exception as e:
            print(f"FaceTrackerDemo: apply_config: cannot load embeddings db: {e}")


        if self.video_writer is None:
            save_video_path = self.config.get('save_video_path', default_config["save_video_path"])
            if save_video_path != "":
                self.video_writer = degirum_tools.create_video_writer(save_video_path, 640, 480)

        camera_cfg = self.config.get('camera', default_config["camera"])
        camera_id = camera_cfg['camera_id']

        # get frames from camera or video file
        try:
            self.init_camera(camera_cfg)
        except Exception as e:
            if self.stream is None:
                raise Exception(f"CameraSource: apply_config: Unable to init camera {camera_cfg['camera_id']}: {str(e)}")

        detector_cfg = self.config.get('detector', default_config["detector"])
        try:
            self.init_detector(detector_cfg)
        except Exception as e:
            raise Exception("CameraSource: apply_config: Unable to init detector: " + str(e))

    def init_camera(self, camera_cfg: dict):
        """
        Apply camera-related config
        """
        if camera_cfg != self.camera_cfg:
            default_cfg = default_config['camera']
            camera_id = camera_cfg.setdefault('camera_id', default_cfg['camera_id'])
            if self.stream is None or camera_id != self.camera_id:
                #stream = cv2.VideoCapture(camera_id)
                self.open_video_stream(camera_id)

            self.fps = camera_cfg.setdefault('fps', default_cfg['fps'])
            self.loop = camera_cfg.setdefault('loop', default_cfg['loop'])
            self.max_frames = camera_cfg.setdefault('max_frames', default_cfg['max_frames'])
            self.is_file_input = os.path.exists(camera_id)

            # successfully applied camera_cfg
            self.camera_cfg = camera_cfg
            print(f"*********** Applied data source {self.camera_id} with {self.fps} fps **********************")

    def init_detector(self, detector_cfg: dict):
        """
        Apply camera-related config
        """
        if detector_cfg != self.detector_cfg:
            # zoo = dg.connect(dg.CLOUD, "https://cs.degirum.com", "dg_aR2PQzJ8rH2xG8tqFDXVR9MiEia1boxSAUn3c")
            # self.model = zoo.load_model("yolo_v5s_face_det--512x512_quant_n2x_orca1_1")
            # self.model.image_backend = 'opencv'

            default_cfg = default_config['detector']
            cloud_url = detector_cfg.setdefault('cloud_url', default_cfg['cloud_url'])
            local_zoo_path = detector_cfg.setdefault('local_zoo_path', default_cfg['local_zoo_path'])
            model_name = detector_cfg.setdefault('model', default_cfg['model'])
            image_backend = detector_cfg.setdefault('image_backend', default_cfg['image_backend'])
            input_numpy_colorspace = detector_cfg.setdefault('input_numpy_colorspace', default_cfg['input_numpy_colorspace'])

            if "cloud" in self.deployment:
                zoo = dg.connect(dg.CLOUD, cloud_url, self.cloud_token)
            elif "local" in self.deployment:
                model_path = os.path.join(local_zoo_path, model_name, model_name+'.json')
                zoo = dg.connect(dg.LOCAL, model_path)
            elif ipv4(self.deployment):
                zoo = dg.connect(self.deployment)
            elif "docker" in self.deployment:
                zoo = dg.connect("127.0.0.1")
            else:
                raise Exception(f"FaceTracker Demo: init_detector: unknown deployment: {self.deployment}")

            self.detect_model = zoo.load_model(model_name)
            self.detect_model.image_backend = image_backend
            self.detect_model.input_numpy_colorspace = input_numpy_colorspace

            self.detector_cfg = detector_cfg
            print(f"*********** Applied Face Detector {model_name} with {self.fps} fps **********************")

    def open_video_stream(self, video_source: Union[int, str, Path]) -> cv2.VideoCapture:
        """Open OpenCV video stream from camera with given identifier.

        video_source - 0-based index for local cameras
           or IP camera URL in the format "rtsp://<user>:<password>@<ip or hostname>",
           or local video file path,
           or URL to mp4 video file,
           or YouTube video URL

        Returns video stream object and closing it on exit
        """

        if isinstance(video_source, Path):
            video_source = str(video_source)

        if isinstance(video_source, str) and urllib.parse.urlparse(
                video_source
        ).hostname in (
                "www.youtube.com",
                "youtube.com",
                "youtu.be",
        ):  # if source is YouTube video
            import pafy

            video_source = pafy.new(video_source).getbest(preftype="mp4").url

        stream = cv2.VideoCapture(video_source)  # type: ignore[arg-type]
        if not stream.isOpened():
            raise Exception(f"Error opening '{video_source}' video stream")
        else:
            print(f"Successfully opened video stream '{video_source}'")

        # Check if the video capturing object was initialized correctly
        if not stream.isOpened():
            raise Exception(f"FaceTrackerDemo: {video_source} cannot be initialized")
        if self.stream is not None:
            self.stream.release()
        self.stream = stream

    def add_q_out(self, destination, q_out):
        self.q_out_map[destination] = q_out

    def start(self):
        self.display_thread.start()
        super(FaceTrackerDemo, self).start()
        self.start_time = time.time()

    def stop(self):
        """
        Stop Face Tracker Demo service
        """
        self.vstore.dump("embeds.db")

        if self.video_writer is not None:
            self.video_writer.release()
        elapsed_time = time.time() - self.start_time
        fps = self.frames_processed / elapsed_time
        print("\n=========== Stopping FaceTrackerDemo ===========")
        print(f"FaceTracker Demo: {self.frames_processed} frames processed in {elapsed_time:.1f} sec ({fps:.1f} fps)")
        self.config.stop()
        self.stop_event.set()

    def is_stopped(self) -> bool:
        """
        Check if the service is stopped
        :return: bool
        """
        return self.stop_event.is_set()

    def run(self):
        while not self.is_stopped():
            for res in self.detect_model.predict_batch(self.video_source()):
                self.result_queue.put(res)
        self.result_queue.put(None)
        self.display_thread.join()

    def video_source(self):
        prev_time = 0.0
        try:
            while not self.is_stopped():
                self.apply_config()

                curr_time = time.time()
                time_passed = curr_time - prev_time
                time_lag = 1.0 / self.fps
                if self.paused:
                    self.display_paused()
                    continue
                if self.fps <= 0 or time_passed > time_lag:
                    prev_time = curr_time
                    ret, frame = self.stream.read()
                    if not ret:
                        if self.loop and self.is_file_input:
                            self.stream.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        print(f"Video Source: missing frame. Frames processed: {self.frames_processed}")
                        self.stream.release()
                        self.stream = None
                        self.open_video_stream(self.camera_id)
                        continue
                    self.frames_processed += 1
                    if self.frames_processed >= self.max_frames > 0:
                        raise EmptyQueue
                    if self.video_writer is not None:
                        self.video_writer.write(frame)
                    yield frame
                elif self.fps > 0 and time_passed < time_lag:
                    time.sleep(time_lag - time_passed)

        except EmptyQueue:
            # No more data in dataset or max frames reached
            self.stop()
        finally:
            print("Video Source: finally: releasing stream")
            self.stream.release()
            print("Video Source: finally: dumping embeds.db")
            self.vstore.dump(self.db_path)

    def result_process(self):
        win_capt = "Faces"
        cv2.namedWindow(win_capt, cv2.WINDOW_NORMAL)
        while not self.is_stopped():
            result = self.result_queue.get()
            if result is None:
                break

            self.re_id()

            if self.use_tracker:
                detections = [d for d in result2detection(result, self.use_landmarks, self.detector_score_th) if d is not None]
                objects = self.tracker.update(detections=detections)
                result._inference_results = objects2results(objects, self.show_landmarks)
            else:
                if self.show_scores:
                    show_scores(result._inference_results)
                objects = result._inference_results

            cv2.imshow(win_capt, result.image_overlay)

            if self.first_frame and self.start_paused:
                self.first_frame = False
                self.paused = True

            cv2.setMouseCallback(win_capt, mouse_click, param=self)
            if self.use_tracker:
                self.process_mouse_clicks(objects)
                if self.use_embedder:
                    self.send_out(objects, result.image)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("x") or key == ord("q"):
                cv2.destroyWindow(win_capt)
                self.send_data(None, "all")
                self.stop()
                break
            elif key == 32:
                self.paused = True

    def objects2results(objects: List[TrackedObject]) -> list:
        results = []
        for obj in objects:
            points = obj.estimate.flatten().tolist()
            bbox = points[:4]

    def process_mouse_clicks(self, objects: List[TrackedObject]):
        for _ in range(self.mouse_clicks_q.qsize()):
            try:
                click = self.mouse_clicks_q.get_nowait()
                if 'event' in click and 'pos' in click and click['event'] == cv2.EVENT_LBUTTONDOWN:
                    x, y = click['pos']
                    for obj in objects:
                        points = obj.estimate.flatten().tolist()
                        bbox = points[:4]
                        if bbox[0] <= x <= bbox[2] and bbox[1] <= y <= bbox[3]:
                            obj.selected = True
                            self.tracker.select_object(global_id=obj.global_id,  selected=True)

            except EmptyQueue:
                break
            except Exception as e:
                print("FaceTrackerDemo: process_mouse_clicks: " + str(e))

    def re_id(self):
        if self.q_in is None:
            return
        while True:
            data = None
            try:
                data = self.q_in.get_nowait()
                global_id = data.get_property('global_id', "")
                object_id = data.get_property('object_id', "")
                #print(f"++++++++++++++++++ Received in re-id: global_id: {global_id}; object_id: {object_id}")
                pass
            except EmptyQueue:
                # no data in q, just exit
                break
            except Exception as e:
                # something is wrong, log and exit
                print("FaceTrackerDemo:re_id failed to get data from queue: " + str(e))
                break

            if data is not None:
                try:
                    self.update_object_id(data, self.vstore, self.auto_labels)
                    detection = convert2detection(data)
                    self.tracker.re_id(detection)
                except Exception as e:
                    print("FaceTrackerDemo:re_id failed to apply to tracker: " + str(e))

    def send2dataset(self, frame):
        frame_data = FrameData()
        frame_data.set_source_image(frame)
        self.send_data(frame_data, 'dataset_writer')

    def send_out(self, tracked_objects: List[TrackedObject], src_img):
        src_img_time = datetime.now().timestamp()
        need2send = False
        if src_img_time - self.prev_time > self.embeddings_time_step:
            need2send = True
            if len(tracked_objects) > 0:  # there is some stuff in tracker
                self.prev_time = src_img_time

        if need2send:
            frame_data = FrameData()
            frame_data.set_source_image(src_img)
            self.send_data(frame_data, 'labeller')

        for obj in tracked_objects:
            if need2send:  # and (obj.tracking_score < 0.5 or obj.object_name == "unknown" or obj.selected):
                face_data = FaceData()
                # Prepare face_data for face_embedder
                points = obj.estimate.flatten().tolist()
                bbox = points[:4]
                face_data.set_bbox(bbox)
                if len(points) > 4:
                    landmarks = normalize_landmarks(points[4:])
                    face_data.set_landmarks(landmarks)

                if not check_face_quality(landmarks):
                    continue

                face_img = get_face_img(src_img, face_data, self.use_normalization)
                face_data.set_face_image(face_img)
                face_data.set_source_image_time(datetime.now().timestamp())
                face_data.add_property('global_id', obj.global_id)
                face_data.add_property('object_id', obj.id)
                face_data.add_property('selected', obj.selected)

                self.send_data(face_data, "face_embedder")
                if False: # obj.selected and obj.object_name == "unknown":
                    print("+++++++++++++ Sending to Labeller!!!! +++++++++++++++++++")
                    label_data = LabelData()
                    label_data.from_data(face_data)
                    self.send_data(label_data, "labeller")

    def send_data(self, data, destination):
        if data is None:
            for q_out in self.q_out_map.values():
                if q_out is not None:
                    q_out.put_nowait(data)

        q_out = self.q_out_map.setdefault(destination, None)
        if q_out is not None:
            try:
                q_out.put_nowait(data)
            except:
                print("FaceTrackerDemo: send_data: failed to put to output queue")

    def update_object_id(self, data, vstore: VectStore, auto_labels: bool):
        embeds = data.get_embeddings()
        stored_global_id = None
        global_id = data.get_property('global_id')

        need2add = True
        if embeds is not None:
            embeds = np.array(embeds)
            # search in saved face embeddings db
            results = vstore.search(embeds, 5)
            if len(results) > 0:
                score, object_id, label, meta = results[0]
                stored_global_id = meta['global_id']
                # print(f"update_object_id search: score: {score:.3f}; object_id: {object_id}; label: {label}")
                if score < self.face_accept_th:
                    label = label  # f"{label} {score:.2f}"
                    data.add_property('object_id', object_id)
                    data.add_property("label", label)
                    data.add_property('face_score', score)
                    need2add = True
                    if stored_global_id != global_id:
                        need2add = False
                    # if self.track_selected and label != "" and label != "unknown":          # face identified!
                    #    data.add_property("label", label)
                elif score > self.face_reject_th:
                    if stored_global_id == global_id:
                        need2add = False
                    data.add_property('object_id', global_id)
                    #n_samples = vstore.class_size(object_id)
                    #face_image = data.get_face_image()
                    #cv2.imwrite(f"c:/Tmp/{object_id}_{n_samples}.jpg", face_image)
                else:
                    need2add = False
            else:
                need2add = True


        label = data.get_property("label", "")
        if label == "" and auto_labels:
            label = generate_name(style='capital')
        object_id = data.get_property('object_id', global_id)

        # n_samples = vstore.class_size(object_id)
        # face_image = data.get_face_image()
        # cv2.imwrite(f"c:/Tmp/{object_id}_{n_samples}.jpg", face_image)

        if embeds is not None:
            # is_from_selected_track = data.get_property('selected', False)
            # if not self.track_selected or (self.track_selected and is_from_selected_track):
            if need2add: #(stored_global_id is None or (stored_global_id == global_id)):
                # print(f"update_object_id: vstore.add object_id: {object_id},  label: {label}")
                vstore.add(object_id, embeds, label, global_id=global_id)
                #if stored_global_id is None:
                vstore.add_metadata(object_id, global_id=global_id)
        else:
            # print(f"update_object_id: vstore.update object_id: {object_id},  label: {label}")
            vstore.update(object_id, label)


def mouse_click(event, x, y,  flags, param: FaceTrackerDemo):
    if not isinstance(param, FaceTrackerDemo):
        raise ValueError("mouse_click: FaceTracker object must be passed in param")
    if event == cv2.EVENT_LBUTTONDOWN:
        param.mouse_clicks_q.put_nowait({'event': cv2.EVENT_LBUTTONDOWN, 'pos': (x,y)})


if __name__ == "__main__":
    os.chdir("..")
    ft = FaceTrackerDemo(config_name="track/FaceTrackerCamera")
    ft.start()
    while not ft.is_stopped():
        time.sleep(0.1)
