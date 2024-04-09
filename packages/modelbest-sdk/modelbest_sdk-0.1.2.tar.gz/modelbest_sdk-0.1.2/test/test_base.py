import os
import shutil
import unittest

from modelbest_sdk.dataset.thrift_wrapper.base_doc import BaseDoc
from modelbest_sdk.dataset.thrift_wrapper.dataset_checkpoint import DatasetInfo, DatasetInfoList
from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext
from modelbest_sdk.file_format.mbtable_builder import MbTableBuilder


class TestBase(unittest.TestCase):
    def setUp(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(cur_dir, "mbtable_test_data")
        self.config_dir = os.path.join(cur_dir, "config")
        self.checkpoint_dir = os.path.join(cur_dir, "checkpoint")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.simple_dataset_config_path = os.path.join(self.config_dir , "simple_dataset_config.mbt")
        self.dist_dataset_config_path = os.path.join(self.config_dir , "dist_dataset_config.mbt")
        self.simple_dataset_checkpoint_path = os.path.join(self.checkpoint_dir, "simple_dataset_checkpoint.mbt")
        self.dist_dataset_checkpoint_path = os.path.join(self.checkpoint_dir, "dist_dataset_checkpoint.mbt")
        self.simple_dataset_context_path = os.path.join(self.config_dir, "simple_dataset_context.mbt")
        self.dist_dataset_context_path = os.path.join(self.config_dir, "dist_dataset_context.mbt")

        
        self.long_dataset_path = os.path.join(self.data_dir, "base_doc_long")
        self.short_dataset_path = os.path.join(self.data_dir, "base_doc_short")
        simple_dataset_info_list = DatasetInfoList([
            DatasetInfo(
                path=self.long_dataset_path,
                weight=1,
                max_epoch=1
            )  
        ])
        dist_dataset_info_list = DatasetInfoList([
            DatasetInfo(
                path=self.long_dataset_path,
                weight=1,
            ),
            DatasetInfo(
                path=self.short_dataset_path,
                weight=2
            )
        ])
        simple_dataset_info_list.save_to_file(self.simple_dataset_config_path)
        dist_dataset_info_list.save_to_file(self.dist_dataset_config_path)
        
        simple_dataset_context = DatasetContext(
            dataset_config_path=self.simple_dataset_config_path,
            dataset_checkpoint_path=self.simple_dataset_checkpoint_path,
        )
        dist_dataset_context = DatasetContext(
            rank=0,
            world_size=2,
            num_workers=2,
            dataset_config_path=self.dist_dataset_config_path,
            dataset_checkpoint_path=self.dist_dataset_checkpoint_path,
        )   
        simple_dataset_context.save_to_file(self.simple_dataset_context_path)
        dist_dataset_context.save_to_file(self.dist_dataset_context_path)

        os.makedirs(self.long_dataset_path, exist_ok=True)
        for i in range(2):
            builder = MbTableBuilder(os.path.join(self.long_dataset_path, f"part_{i}.mbt"))
            for j in range(10):
                doc = BaseDoc()
                doc.docid = f"doc_{i}_{j}"
                doc.token_ids = [-1, 2, 3, 4, 5, 6, 0]
                doc.mask = [False, False, False, False, False, False, True]
                doc.tag=["long"]
                doc_str = doc.serialize()
                builder.write(doc_str)
            builder.flush()
        
        builder = MbTableBuilder(self.short_dataset_path)
        for j in range(20):
            doc = BaseDoc()
            doc.docid = f"doc_{j}"
            doc.token_ids = [-1, 2, 3, 0]
            doc.mask = [False, False, False, True]
            doc.tag=["short"]
            doc_str = doc.serialize()
            builder.write(doc_str)
        builder.flush()

    def tearDown(self):
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
        if os.path.exists(self.checkpoint_dir):
            shutil.rmtree(self.checkpoint_dir)

        