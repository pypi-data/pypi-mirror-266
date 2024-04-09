import torch

from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import DatasetCheckpoint, DatasetCheckpointList
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext


def get_worker_info():
    worker_info = torch.utils.data.get_worker_info()
    if worker_info is None:
        num_workers, worker_id = 1, 0
    else:
        num_workers, worker_id = worker_info.num_workers, worker_info.id
    return num_workers, worker_id
