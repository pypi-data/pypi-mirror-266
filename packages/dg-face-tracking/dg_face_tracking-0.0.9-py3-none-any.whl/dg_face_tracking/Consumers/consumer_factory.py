from .lancedb_writer import LanceDBWriter
from .localdb_writer import LocalDBWriter
from .embeds_writer import EmbedsWriter
from .pairwise_stats import PairwiseStats


def create_data_consumer(consumer_id: str, q_in, config_name=None):
    if consumer_id == "lancedb_writer":
        return [LanceDBWriter("vector_writer", q_in, config_name)]

    if consumer_id == "localdb_writer":
        return [LocalDBWriter("dataset_writer", q_in, config_name)]

    if consumer_id == "embeds_writer":
        return [EmbedsWriter("embeds_writer", q_in, config_name)]

    if consumer_id == "pairwise_stats":
        return [PairwiseStats("pairwise_stats", q_in, config_name)]

    raise Exception(f"create_data_consumer: {consumer_id}: No such Consumer")