import logging
import os
import thriftpy2
from thriftpy2.utils import deserialize, serialize

from modelbest_sdk.dataset.thrift_wrapper.utils import Utils

proto_dir = os.path.join(os.path.dirname(__file__), "../..", "proto")

dc_thrift = thriftpy2.load(os.path.join(proto_dir, "dataset_context.thrift"), module_name="context_thrift")
logger = logging.getLogger(__name__)


class DatasetContext:
    def __init__(self, rank=0, world_size=1, tp_size=1, tp_rank=0, num_workers=1, dataset_config_path=None, dataset_checkpoint_path=None):
        self.rank = rank
        self.world_size = world_size
        self.tp_size = tp_size
        self.tp_rank = tp_rank
        self.num_workers = num_workers
        self.dataset_config_path = dataset_config_path
        self.dataset_checkpoint_path = dataset_checkpoint_path

    @staticmethod
    def load_from_file(path):
        return DatasetContext.from_thrift(deserialize(dc_thrift.DatasetContext(), Utils.load_from_file(path)))

    def save_to_file(self, path):
        Utils.save_to_file(path, serialize(self.to_thrift()))

    def to_thrift(self):
        return dc_thrift.DatasetContext(
            rank=self.rank,
            world_size=self.world_size,
            tp_size=self.tp_size,
            tp_rank=self.tp_rank,
            num_workers=self.num_workers,
            dataset_config_path=self.dataset_config_path,
            dataset_checkpoint_path=self.dataset_checkpoint_path
        )

    @staticmethod
    def from_thrift(thrift_context):
        return DatasetContext(
            rank=thrift_context.rank,
            world_size=thrift_context.world_size,
            tp_size=thrift_context.tp_size,
            tp_rank=thrift_context.tp_rank,
            num_workers=thrift_context.num_workers,
            dataset_config_path=thrift_context.dataset_config_path,
            dataset_checkpoint_path=thrift_context.dataset_checkpoint_path
        )
    
    def __repr__(self) -> str:
        return f"DatasetContext(rank={self.rank}, world_size={self.world_size}, tp_size={self.tp_size}, tp_rank={self.tp_rank}, num_workers={self.num_workers}, dataset_config_path={self.dataset_config_path}, dataset_checkpoint_path={self.dataset_checkpoint_path})"
