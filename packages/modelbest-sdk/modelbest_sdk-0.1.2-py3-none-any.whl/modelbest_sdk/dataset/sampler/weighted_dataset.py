import sys
import numpy as np
import torch
from modelbest_sdk.dataset.mbtable_iterable_dataset import MBTableIterableDataset
# from modelbest_sdk.dataset.sampler.sampler import Sampler
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import *
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext

MAX_EPOCH = 2**31 - 1

class WeightedDataset(torch.utils.data.IterableDataset):
    def __init__(
        self, 
        context: DatasetContext, 
        dataset_info_list: DatasetInfoList,
        prefetch_chunk_cnt=20,
        chunk_size=1024
        ):
        
        self.context = context
        self.dataset_info_list = dataset_info_list.dataset_info_list

        self.dataset_weights = []
        self.datasets: List[MBTableIterableDataset] = []
        self.datasets_iter = []
        weights = []
        for dataset_info in self.dataset_info_list:
            path = dataset_info.path
            weight = dataset_info.weight
            if weight == 0:
                print(f"Dataset {path} has weight 0, skip it")
                continue
            max_epoch = dataset_info.max_epoch if dataset_info.max_epoch is not None else MAX_EPOCH
            dataset = MBTableIterableDataset(
                context=context,
                path=path,
                max_epoch=max_epoch,
                prefetch_chunk_cnt=prefetch_chunk_cnt,
                chunk_size=chunk_size
            )
            self.datasets.append(dataset)
            weights.append(weight)
        weights = np.array(weights)
        self.dataset_weights = weights / weights.sum()
        self.remain = len(self.datasets)
            
    def sample(self) -> int:
        choice = np.random.choice(len(self.dataset_weights), p=self.dataset_weights)
        return choice
    
    def __iter__(self):
        for dataset in self.datasets:
            self.datasets_iter.append(iter(dataset))
        while True:
            if all(d.exhausted for d in self.datasets):
                print(f"All dataset exhaust on rank {self.context.rank}")
                break
            idx = self.sample()
            if self.datasets[idx].exhausted:
                print(f"Dataset {idx} exhaust on rank {self.context.rank}")
                continue
            chosen_iter = self.datasets_iter[idx]
            try:
                data = next(chosen_iter)
                if data is None:
                    continue
                data['dataset_idx'] = idx
                yield data
            except StopIteration:
                continue


    def set_seed():
        # TODO: implement set_seed
        pass
    
    def checkpoint(self):
        checkpoint_list = [dataset.checkpoint() for dataset in self.datasets]
        return DatasetCheckpointList(
            checkpoint_list=checkpoint_list,
            world_size=self.context.world_size,
            tp_size=self.context.tp_size
        )
    
    def load_checkpoint(self, dataset_checkpoint_list: DatasetCheckpointList):
        for i, checkpoint in enumerate(dataset_checkpoint_list.checkpoint_list):
            self.datasets[i].load_checkpoint(checkpoint)
            
    def update(self, dataset_entries: Dict[int, Dict]):
        for i, entries in dataset_entries.items():
            self.datasets[i].update(entries)
    

if __name__ == '__main__':
    context = DatasetContext(world_size=1, rank=0, num_workers=1)

    dataset_info_list = [
        DatasetInfo(
            path="/home/emr-user/modelbest_sdk/test/base_doc_simple",
            weight=1,
            max_epoch=1
        ),
        DatasetInfo(
            path="/home/emr-user/modelbest_sdk/test/base_doc_easy",
            weight=2,
            max_epoch=2
        )
    ]
    
    dataset_info_list = DatasetInfoList(dataset_info_list=dataset_info_list)
    
    dataset = WeightedDataset(
        context=context,
        dataset_info_list=dataset_info_list
    )

    for data in dataset:
        print(data)