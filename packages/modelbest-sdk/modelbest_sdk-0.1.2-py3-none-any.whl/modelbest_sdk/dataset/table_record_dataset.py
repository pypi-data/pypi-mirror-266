import os
import torch
from modelbest_sdk.dataset.collater.batched_dataset import BatchedDataset
from modelbest_sdk.dataset.sampler.weighted_dataset import WeightedDataset
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import DatasetCheckpointList, DatasetInfo, DatasetInfoList
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext


class TableRecordDataset(torch.utils.data.IterableDataset):
    def __init__(
        self,
        context: DatasetContext,
        batch_size=1,
        max_len=4096,
        prefetch_chunk_cnt=20,
        chunk_size=1024,
        num_workers=1,
        prefetch_factor=20,
        cuda_prefetch=True
    ):
        self.context = context
        dataset_info_list = DatasetInfoList.load_from_file(context.dataset_config_path)
        
        self.weighted_dataset = WeightedDataset(
            context=context, 
            dataset_info_list=dataset_info_list,
            prefetch_chunk_cnt=prefetch_chunk_cnt,
            chunk_size=chunk_size
        )
        
        self.batched_dataset = BatchedDataset(
            context=context,
            weighted_dataset=self.weighted_dataset,
            batch_size=batch_size,  
            max_len=max_len
        )
        
        self.dataloader = torch.utils.data.DataLoader(
            dataset=self.batched_dataset, 
            num_workers=num_workers,
            prefetch_factor=prefetch_factor,
            collate_fn=BatchedDataset.collate_fn,
        )
        
        self.cuda_prefetch = cuda_prefetch
        
        if self.cuda_prefetch:
            from modelbest_sdk.dataset.cuda_prefetcher import CudaPrefetcher
            self.cuda_prefetcher = CudaPrefetcher(
                context,
                self.dataloader
            )
        
    
    def __iter__(self):
        if not self.cuda_prefetch:
            for batch in self.dataloader:
                yield batch
        else:
            for batch in self.cuda_prefetcher:
                yield batch
    
    def checkpoint(self):
        return self.weighted_dataset.checkpoint()
    
    def load_checkpoint(self, checkpoint):
        self.weighted_dataset.load_checkpoint(checkpoint)
        
    def update(self, dataset_entries):
        self.weighted_dataset.update(dataset_entries)
    
    def save(self):
        path = os.path.join(self.context.dataset_checkpoint_path, f"dataset_ckpt_rank_{self.context.rank}.mbt")
        self.checkpoint().save_to_file(path)
        
    def resume(self):
        new_world_size = self.context.world_size
        first_rank_ckpt_path = os.path.join(self.context.dataset_checkpoint_path, f"dataset_ckpt_rank_0.mbt")
        cur_rank_ckpt_path = os.path.join(self.context.dataset_checkpoint_path, f"dataset_ckpt_rank_{self.context.rank}.mbt")
        old_world_size = DatasetCheckpointList.load_from_file(first_rank_ckpt_path).world_size
        if new_world_size == old_world_size:
            self.weighted_dataset.load_checkpoint(DatasetCheckpointList.load_from_file(cur_rank_ckpt_path))
        else:
            merged_ckpt = None
            for path in os.listdir(self.context.dataset_checkpoint_path):
                abs_path = os.path.join(self.context.dataset_checkpoint_path, path)
                if merged_ckpt is None:
                    merged_ckpt = DatasetCheckpointList.load_from_file(abs_path)
                else:
                    merged_ckpt.merge(DatasetCheckpointList.load_from_file(abs_path))
            self.load_checkpoint(merged_ckpt)