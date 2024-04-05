from collections import Counter
from pathlib import Path


def get_suffixes(folder: str) -> Counter:
    """
    统计文件夹中所有文件后缀
    :param file_path: 文件路径
    :return: 字典
    """
    suffixes_counter = Counter()
    for file in Path(folder).rglob("*"):
        if file.is_dir():
            continue
        suffixes_counter[file.suffix.lower()] += 1
    return suffixes_counter