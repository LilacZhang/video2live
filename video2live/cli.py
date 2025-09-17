#!/usr/bin/env python3
"""
视频转Live Photo命令行工具
依赖: ffmpeg, moviepy, makelive
安装: pip install moviepy makelive
"""

import os
import sys
import argparse
import subprocess
import shutil
from moviepy import VideoFileClip
from makelive import make_live_photo


def check_dependencies():
    """检查必要的依赖是否安装"""
    required = ["ffmpeg"]
    missing = []

    for dep in required:
        if shutil.which(dep) is None:
            missing.append(dep)

    if missing:
        print(f"❌ 缺少必要依赖: {', '.join(missing)}")
        print("请安装以下工具:")
        print(
            "  - ffmpeg: brew install ffmpeg (macOS) 或 sudo apt install ffmpeg (Linux)"
        )
        sys.exit(1)

    try:
        import makelive
    except ImportError:
        print("❌ 缺少Python依赖: makelive")
        print("请安装: pip install makelive")
        sys.exit(1)


def convert_video_to_mov(input_path, output_path, duration=3.0, start_time=None, end_time=None):
    """转换视频为兼容Live Photo的MOV格式"""
    cmd = [
        "ffmpeg",
        "-y",
    ]

    # 添加时间截取参数 (类似ffmpeg -ss和-to)
    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])

    cmd.extend(["-i", input_path])

    if end_time is not None:
        cmd.extend(["-to", str(end_time)])

    # 视频编码参数
    cmd.extend([
        "-c:v",
        "h264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        "-pix_fmt",
        "yuv420p",
    ])

    # 如果没有指定结束时间，使用持续时长
    if end_time is None and start_time is not None:
        cmd.extend(["-t", str(duration)])

    cmd.append(output_path)
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 视频转换失败: {e.stderr.decode()}")
        return False


def video_to_live_photo(video_path, output_dir, duration=3.0, start_time=None, end_time=None, cover_time=None):
    """将视频转换为Live Photo"""
    if not os.path.exists(video_path):
        sys.exit("❌ 错误: 视频文件不存在")

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    # 提取封面图
    try:
        clip = VideoFileClip(video_path)
        jpg_path = os.path.join(output_dir, f"{base_name}.jpg")
        # 默认使用截取片段的第一帧作为封面，如果指定了cover_time则使用指定时间
        if cover_time is not None:
            frame_time = cover_time
        else:
            frame_time = start_time if start_time is not None else 0.0
        clip.save_frame(jpg_path, t=frame_time)
        print(f"✅ 已提取封面图: {jpg_path} (时间: {frame_time}秒)")
    except Exception as e:
        sys.exit(f"❌ 封面提取失败: {str(e)}")

    # 转换视频格式
    mov_path = os.path.join(output_dir, f"{base_name}.mov")
    if not convert_video_to_mov(video_path, mov_path, duration, start_time, end_time):
        sys.exit(1)

    # 创建Live Photo
    try:
        asset_id = make_live_photo(jpg_path, mov_path)
        print(f"✅ 已生成Live Photo资源: {mov_path} (asset_id: {asset_id})")
        return jpg_path, mov_path
    except Exception as e:
        sys.exit(f"❌ 创建Live Photo失败: {str(e)}")


def import_to_photos(jpg_path, mov_path):
    """将文件导入苹果Photos应用"""
    if sys.platform != "darwin":
        print("⚠️ 导入Photos功能仅支持macOS系统")
        return

    script = f"""
    tell application "Photos"
        activate
        launch
        set jpgFile to POSIX file "{jpg_path}" as alias
        set movFile to POSIX file "{mov_path}" as alias
        import [jpgFile, movFile] with skip check duplicates
    end tell
    """
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print("✅ 已导入Photos应用 - 请稍候系统处理Live Photo")
    except subprocess.CalledProcessError:
        print("⚠️ 导入Photos失败 - 请确保已安装Photos应用")


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(
        description="将视频转换为苹果Live Photo格式",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("video", help="输入视频文件路径")
    parser.add_argument("output", help="输出目录")
    parser.add_argument(
        "-d", "--duration", type=float, default=3.0, help="Live Photo视频时长（秒）"
    )
    parser.add_argument(
        "-ss", type=float, help="开始时间（秒），类似ffmpeg -ss参数"
    )
    parser.add_argument(
        "-to", type=float, help="结束时间（秒），类似ffmpeg -to参数"
    )
    parser.add_argument(
        "-c", "--cover-time", type=float, help="指定封面图时间（秒），默认使用截取片段的第一帧"
    )
    parser.add_argument(
        "--no-import", action="store_true", help="不自动导入到Photos应用"
    )

    args = parser.parse_args()

    # 验证时间参数
    if args.ss is not None and args.to is not None:
        if args.to <= args.ss:
            sys.exit("❌ 错误: -to 时间必须大于 -ss 时间")
        if args.duration is not None and args.duration > (args.to - args.ss):
            print(f"⚠️  警告: 指定时长 {args.duration} 大于截取片段长度 {args.to - args.ss}，将使用截取片段长度")
            args.duration = args.to - args.ss

    jpg, mov = video_to_live_photo(args.video, args.output, args.duration, args.ss, args.to, args.cover_time)

    if not args.no_import and sys.platform == "darwin":
        import_to_photos(jpg, mov)


if __name__ == "__main__":
    main()
