"""
函数

concat_video：合并视频

———————————

类 FFprobe

duration：获取视频时长

codec：获取视频编码

size：获取视频大小
"""

import json
import subprocess as sp
from pathlib import Path

from moviepy.editor import VideoFileClip, concatenate_videoclips


def concat_video(files: list[str], output_file: str):
    """
    合并视频文件列表中的所有视频成一个视频。

    参数:
    files: list[str] - 包含要合并的视频文件路径的列表。
    output_file: str - 合并后的视频文件输出路径。

    后处理：合并完成后，删除原始视频文件。

    注意：该函数仅使用CPU进行视频合并，如果合并大量视频文件，可能会非常慢。
    """
    # 加载所有指定的视频文件为VideoFileClip对象
    clips = [VideoFileClip(f) for f in files]
    # 将所有VideoFileClip对象合并为一个final_clip
    final_clip = concatenate_videoclips(clips)
    # 将合并后的视频写入指定的输出文件
    final_clip.write_videofile(output_file)
    # 删除所有原始视频文件
    for f in files:
        f.unlink()


class MetadataParsedError(OSError):
    """
    metadata 解析错误
    """

    pass


class FFprobe:
    """
    方法

    duration：获取视频时长

    codec：获取视频编码

    size：获取视频大小
    """
    def __init__(self, file: str):
        self.metadata = self.__ffprobe(file)
        if not self.metadata:
            raise MetadataParsedError(file)

    def __repr__(self):
        return str(self.metadata)

    def __ffprobe(self, file: str) -> dict:
        """
        私有方法：获取视频的元数据信息。

        参数:
        - file: 字符串，指定要分析的视频文件的路径。

        返回值:
        - 返回一个字典，包含视频的元数据信息，如格式、流信息等。
        """
        # 构造ffprobe命令行字符串，并执行命令获取视频元数据
        cmd = f'ffprobe -print_format json -show_format -show_streams -v quiet "{file}"'
        output = sp.check_output(cmd, shell=True)  # 执行命令并获取输出结果
        return json.loads(output)  # 将命令输出的JSON字符串解析为字典并返回

    def duration(self) -> str:
        return self.metadata["format"]["duration"]

    def codec_name(self) -> str:
        return self.metadata["streams"][0]["codec_name"]

    def size(self) -> str:
        return self.metadata["format"]["size"]

def is_hevc(file: Path) -> bool:
    """
    编码为 hevc 返回 True
    """
    return True if FFprobe(file).codec_name() == "hevc" else False

def is_not_hevc(file: Path) -> bool:
    """
    编码不是 hevc 返回 True
    """
    return True if FFprobe(file).codec_name() != "hevc" else False


if __name__ == "__main__":
    print(
        FFprobe(
            r"C:\Users\qf\Videos\大明王朝\大明王朝-03.mp4"
        )
    )
