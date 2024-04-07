import os
import sys
import thriftpy2

cur_path = os.path.split(os.path.realpath(__file__))[0]

from modelbest_sdk.dataset.thrift_wrapper.dataset_context import DatasetContext
from modelbest_sdk.file_format.mbtable_builder import MbTableBuilder
from thriftpy2.utils import serialize


dc_thrift = thriftpy2.load(os.path.join(cur_path,"../proto/dataset_context.thrift"), module_name="context_thrift")

def test_read_from_file():
    test_path = os.path.join('/tmp', 'test_context.sstable')
    table = MbTableBuilder(test_path)

    nc = dc_thrift.DatasetContext(
        rank=1,
        world_size=10,
        dataset_config_path="/path/to/datainfo_list",
        dataset_checkpoint_path="/path/to/checkpoint_list",
    )
    table.write(serialize(nc))
    table.flush()
    print('write data to file %s', test_path)

    read_nc = DatasetContext(test_path).context
    print(read_nc)
    assert read_nc.rank == nc.rank
    assert read_nc.world_size == nc.world_size
    assert read_nc.dataset_config_path == nc.dataset_config_path
    assert read_nc.dataset_checkpoint_path == nc.dataset_checkpoint_path


if __name__ == "__main__":
  test_read_from_file()
