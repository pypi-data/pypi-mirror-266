import os

from modelbest_sdk.file_format.mbtable import MbTable, MbTableIterator

'''
MbTablePartition is designed to manage a directory of mbtable files, and provide a way to iterate over the rows of the files.
Note that each file can contain max 2 << 30 records.
'''
class MbTablePartition:
    def __init__(self, partition_path: str):
        """
        calculate total count of rows in mbtable partition
        """
        self.partition_path = partition_path
        self.total_count = 0
        self.file_name_list = [file for file in os.listdir(partition_path)]
        self.file_name_list.sort()
        self.abs_path_list = [os.path.join(partition_path, file) for file in self.file_name_list]
        self.abs_path_index_dict = {file: i for i, file in enumerate(self.abs_path_list)}
        self.file_handle_list = [MbTable(file) for file in self.abs_path_list]
        self.file_row_counts = []
        self.cumulative_row_counts = []

        cumulative_count = 0
        for handle in self.file_handle_list:
            count = handle.get_entry_count()
            self.total_count += count
            self.file_row_counts.append(count)
            
            cumulative_count += count
            self.cumulative_row_counts.append(cumulative_count)

    def get_file_index_and_position(self, n):
        """
        根据行号n找到对应的文件以及该行在文件中的位置
        """
        if n > self.total_count:
            return None, None  # n 超出总行数

        # 确定n在哪个文件中
        for i, cumulative in enumerate(self.cumulative_row_counts):
            if n <= cumulative:
                # 确定在当前文件中的具体位置
                position_in_file = n - (self.cumulative_row_counts[i-1] if i > 0 else 0)
                return i, position_in_file
        
        return None, None  # 如果没有找到，返回None
    
    def get_total_count(self) -> int:
        return self.total_count
    
    def get_file_path(self, file_index):
        return self.abs_path_list[file_index]

    def get_next_file_index(self, file_index):
        if file_index == len(self.abs_path_list) - 1:
            return None
        else:
            return file_index + 1
        
    
class MbTablePartitionIterator:
    def __init__(self, mbtable_partition: MbTablePartition, start_index=0, max_iterations=None):
        self.mbtable_partition = mbtable_partition
        self.max_iterations = max_iterations
        self.iterations_count = 0
        assert start_index >= 0 and start_index <= mbtable_partition.get_total_count()
        self.current_file_index, self.current_pos = mbtable_partition.get_file_index_and_position(start_index)
        self.iterator = None
        
    def __iter__(self):
        return self
    
    def __enter__(self):
        if self.iterator is None:
            self.iterator = MbTableIterator(self.mbtable_partition.get_file_path(self.current_file_index), self.current_pos, self.max_iterations)
            self.iterator.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.iterator.__exit__(exc_type, exc_val, exc_tb)
    
    def __next__(self):
        if self.max_iterations is not None and self.iterations_count >= self.max_iterations:
            raise StopIteration

        # 检查是否需要初始化或重置迭代器
        if self.iterator is None:
            # 计算剩余的迭代次数，如果 max_iterations 未定义，则不限制迭代器
            remaining_iterations = None if self.max_iterations is None else self.max_iterations - self.iterations_count
            self.iterator = MbTableIterator(self.mbtable_partition.get_file_path(self.current_file_index), self.current_pos, remaining_iterations)
            self.iterator.__enter__()

        try:
            record = self.iterator.__next__()
            self.iterations_count += 1  # 更新已迭代的数量
            return record
        except StopIteration:
            self.current_file_index = self.mbtable_partition.get_next_file_index(self.current_file_index)
            if self.current_file_index is None:
                raise StopIteration
            self.current_pos = 0
            self.iterator = None  # 重置迭代器以便于下次调用时重新初始化
            return self.__next__()


if __name__ == '__main__':
    mbtable_partition = MbTablePartition('test/partition_data')
    total_count = mbtable_partition.get_total_count()
    print(f"total count: {total_count}")
    with MbTablePartitionIterator(mbtable_partition, start_index=9, max_iterations=11) as iterator:
        for row in iterator:
            print(f"row: {row}")