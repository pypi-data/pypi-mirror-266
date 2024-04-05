import json
import subprocess as sp
from pathlib import Path

COMMENT = "Comment"


def get_exif(file_path: str | Path) -> dict:
    """
    获取文件的EXIF信息。
    
    参数:
    file_path: str | Path - 文件的路径，可以是字符串或Path对象。
    
    返回值:
    dict - 文件的EXIF信息，以字典形式返回。
    """
    # 使用exiftool命令行工具获取文件的EXIF信息，并以JSON格式返回
    cmd = ["exiftool", "-j", file_path]
    # 解析命令行工具输出的JSON信息，返回第一个（也是唯一一个）记录
    return json.loads(sp.check_output(cmd))[0]


def ch_tag(file_path: str | Path, tag: str, value: str):
    """
    修改 exif 某个 tag 的值。

    参数:
    - file_path: 文件路径，可以是字符串或Path对象。
    - tag: 需要修改的EXIF标签名称。
    - value: 给定标签的新值。

    说明:
    该函数使用外部工具exiftool来修改指定文件的EXIF标签值。
    修改操作是直接在原文件上进行，并且会覆盖原始值。

    返回值:
    无
    """
    # 构建命令行指令，使用exiftool修改指定tag的值
    cmd = ["exiftool", f"-{tag}={value}", file_path, "-overwrite_original"]
    # 执行命令，并捕获输出
    sp.run(cmd, capture_output=True)



if __name__ == "__main__":
    pass