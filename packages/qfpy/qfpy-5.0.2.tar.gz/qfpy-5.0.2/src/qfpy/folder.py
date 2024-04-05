from collections import Counter
from pathlib import Path


def count_suffix(folder: str) -> Counter:
    """
    统计文件夹中所有文件后缀
    :param file_path: 文件路径
    :return: 字典
    """
    suffix_counter = Counter()
    for file in Path(folder).rglob("*"):
        if file.is_dir():
            continue
        if file.is_symlink(): # 忽略符号链接
            continue
        suffix_counter[file.suffix.lower()] += 1
    return suffix_counter