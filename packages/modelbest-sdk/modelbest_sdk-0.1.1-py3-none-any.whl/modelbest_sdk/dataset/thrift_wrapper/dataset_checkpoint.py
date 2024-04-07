import logging
from typing import Dict, List, Set
import thriftpy2
from thriftpy2.utils import deserialize, serialize
import os

from modelbest_sdk.dataset.thrift_wrapper.utils import Utils

proto_dir = os.path.join(os.path.dirname(__file__), "../..", "proto")

dc_thrift = thriftpy2.load(os.path.join(proto_dir, "dataset_checkpoint.thrift"), module_name="checkpoint_thrift")
dc_thrift.Chunk.__hash__ = lambda self: hash((self.epoch, self.start, self.stop))

logger = logging.getLogger(__name__)


class DatasetCheckpointList:
    def __init__(self, checkpoint_list, world_size=None, tp_size=None):
        self.checkpoint_list = checkpoint_list
        self.world_size = world_size
        self.tp_size = tp_size
        
    @staticmethod
    def load_from_file(path):
        return DatasetCheckpointList.from_thrift(deserialize(dc_thrift.DatasetCheckpointList(), Utils.load_from_file(path)))

    def save_to_file(self, path):
        Utils.save_to_file(path, serialize(self.to_thrift()))

    def to_thrift(self):
        thrift_checkpoints = [checkpoint.to_thrift() for checkpoint in self.checkpoint_list]
        return dc_thrift.DatasetCheckpointList(
            checkpoint_list=thrift_checkpoints,
            world_size=self.world_size,
            tp_size=self.tp_size
        )

    @staticmethod
    def from_thrift(thrift_checkpoint_list):
        checkpoint = [DatasetCheckpoint.from_thrift(checkpoint) for checkpoint in thrift_checkpoint_list.checkpoint_list]
        return DatasetCheckpointList(
            checkpoint_list=checkpoint,
            world_size=thrift_checkpoint_list.world_size,
            tp_size=thrift_checkpoint_list.tp_size
        )
        
    def __repr__(self) -> str:
        return f"DatasetCheckpointList(checkpoint_list={self.checkpoint_list}, world_size={self.world_size}, tp_size={self.tp_size})"
        


class DatasetCheckpoint:
    def __init__(self, dataset_info, used=None, chunk_size=None, num_chunks=None):
        self.dataset_info = dataset_info
        self.used: Used = used
        self.chunk_size = chunk_size
        self.num_chunks = num_chunks

    def to_thrift(self):
        thrift_dataset_info = self.dataset_info.to_thrift() if self.dataset_info else None
        thrift_used = self.used.to_thrift() if self.used else None
        return dc_thrift.DatasetCheckpoint(
            dataset_info=thrift_dataset_info,
            used=thrift_used,
            chunk_size=self.chunk_size,
            num_chunks=self.num_chunks
        )

    @staticmethod
    def from_thrift(thrift_checkpoint):
        dataset_info = DatasetInfo.from_thrift(thrift_checkpoint.dataset_info) if thrift_checkpoint.dataset_info else None
        used_ = Used.from_thrift(thrift_checkpoint.used) if thrift_checkpoint.used else None
        return DatasetCheckpoint(
            dataset_info=dataset_info,
            used=used_,
            chunk_size=thrift_checkpoint.chunk_size,
            num_chunks=thrift_checkpoint.num_chunks
        )
        
    def __repr__(self) -> str:
        return f"DatasetCheckpoint(dataset_info={self.dataset_info}, used={self.used}, chunk_size={self.chunk_size}, num_chunks={self.num_chunks})"


class DatasetInfoList:
    def __init__(self, dataset_info_list=None):
        self.dataset_info_list: List[DatasetInfo] = dataset_info_list if dataset_info_list is not None else []

    @staticmethod
    def load_from_file(path):
        return DatasetInfoList.from_thrift(deserialize(dc_thrift.DatasetInfoList(), Utils.load_from_file(path)))

    def save_to_file(self, path):
        Utils.save_to_file(path, serialize(self.to_thrift()))

    def to_thrift(self):
        return dc_thrift.DatasetInfoList(
            dataset_info_list=[info.to_thrift() for info in self.dataset_info_list]
        )

    @staticmethod
    def from_thrift(thrift_dataset_info_list):
        dataset_info_list = [DatasetInfo.from_thrift(info) for info in thrift_dataset_info_list.dataset_info_list]
        return DatasetInfoList(dataset_info_list=dataset_info_list)

    def __repr__(self) -> str:
        return f"DatasetInfoList(dataset_info_list={self.dataset_info_list})"

class DatasetInfo:
    def __init__(self, path, weight=None, max_epoch=None):
        self.path = path
        self.weight = weight
        self.max_epoch = max_epoch

    def to_thrift(self):
        return dc_thrift.DatasetInfo(
            path=self.path,
            weight=self.weight,
            max_epoch=self.max_epoch
        )

    @staticmethod
    def from_thrift(thrift_dataset_info):
        return DatasetInfo(
            path=thrift_dataset_info.path,
            weight=thrift_dataset_info.weight,
            max_epoch=thrift_dataset_info.max_epoch
        )
        
    def __repr__(self) -> str:
        return f"DatasetInfo(path={self.path}, weight={self.weight}, max_epoch={self.max_epoch})"


class Used:
    def __init__(self):
        self.active: Dict[Chunk, Set[int]] = {}
        self.done: Dict[int, Set[Chunk]] = {}
        self.epoch: int = 0

    def to_thrift(self):
        thrift_active = {chunk.to_thrift(): index_set for chunk, index_set in self.active.items()}
        thrift_done = {epoch: {chunk.to_thrift() for chunk in chunk_set} for epoch, chunk_set in self.done.items()}
        return dc_thrift.Used(active=thrift_active, done=thrift_done, epoch=self.epoch)

    @staticmethod
    def from_thrift(thrift_used):
        used = Used()
        used.epoch = thrift_used.epoch
        for thrift_chunk, index_set in thrift_used.active.items():
            used.active[Chunk.from_thrift(thrift_chunk)] = set(index_set)
        for epoch, thrift_chunk_set in thrift_used.done.items():
            used.done[epoch] = {Chunk.from_thrift(chunk) for chunk in thrift_chunk_set}
        return used
    
    def __repr__(self) -> str:
        return f"Used(active={self.active}, done={self.done}, epoch={self.epoch})"


class Chunk:
    def __init__(self, epoch, start, stop):
        self.epoch = epoch
        self.start = start
        self.stop = stop

    def to_thrift(self):
        return dc_thrift.Chunk(epoch=self.epoch, start=self.start, stop=self.stop)

    @staticmethod
    def from_thrift(thrift_chunk):
        return Chunk(epoch=thrift_chunk.epoch, start=thrift_chunk.start, stop=thrift_chunk.stop)
    
    def __repr__(self) -> str:
        return f"Chunk(epoch={self.epoch}, start={self.start}, stop={self.stop})"

    def __hash__(self) -> int:
        return hash((self.epoch, self.start, self.stop))
    
    def __eq__(self, other) -> bool:
        return self.epoch == other.epoch and self.start == other.start and self.stop == other.stop