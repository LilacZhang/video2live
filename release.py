#!/usr/bin/env python3
"""
Video2Live 发布脚本
用于构建和发布软件包，支持多种发布选项
"""

import os
import sys
import subprocess
import argparse
import shutil
from datetime import datetime


def run_command(cmd, check=True):
    """运行系统命令并返回结果"""
    try:
        print(f"运行: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令失败: {e}")
        if e.stdout:
            print("输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        sys.exit(1)


def check_dependencies():
    """检查必要的依赖是否存在"""
    print("检查依赖...")
    required = ["python", "twine", "ffmpeg"]
    missing = []

    for dep in required:
        if shutil.which(dep) is None:
            missing.append(dep)

    if missing:
        print(f"❌ 缺少必要依赖: {', '.join(missing)}")
        print("请安装:")
        if "twine" in missing:
            print("  - twine: pip install twine")
        if "ffmpeg" in missing:
            print("  - ffmpeg: brew install ffmpeg (macOS) 或 sudo apt install ffmpeg (Linux)")
        sys.exit(1)


def get_current_version():
    """从setup.py读取当前版本号"""
    with open("setup.py", "r") as f:
        for line in f:
            if "version=" in line and not line.strip().startswith("#"):
                # 提取版本号
                version = line.split("version=\"")[1].split("\"")[0]
                return version
    return None


def validate_version(new_version):
    """验证版本号格式"""
    parts = new_version.split(".")
    if len(parts) != 3:
        return False

    for part in parts:
        if not part.isdigit():
            return False
    return True


def bump_version(version_type="patch"):
    """自动递增版本号"""
    current = get_current_version()
    if not current:
        print("❌ 无法读取当前版本号")
        sys.exit(1)

    print(f"当前版本: {current}")

    parts = current.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    elif version_type == "patch":
        patch += 1
    else:
        print(f"❌ 不支持的版本类型: {version_type}")
        sys.exit(1)

    new_version = f"{major}.{minor}.{patch}"
    print(f"新版本: {new_version}")

    return new_version


def update_version_in_setup_py(new_version):
    """更新setup.py中的版本号"""
    with open("setup.py", "r") as f:
        content = f.read()

    old_version = get_current_version()
    content = content.replace(f'version="{old_version}"', f'version="{new_version}"')

    with open("setup.py", "w") as f:
        f.write(content)

    print(f"版本号已更新: {old_version} -> {new_version}")


def clean_build_artifacts():
    """清理构建产物"""
    print("清理构建产物...")
    artifacts = ["dist", "build", "video2live.egg-info", "__pycache__"]

    for artifact in artifacts:
        if os.path.exists(artifact):
            shutil.rmtree(artifact)
            print(f"已删除: {artifact}")


def build_package():
    """构建包"""
    print("构建包...")
    run_command([sys.executable, "setup.py", "sdist", "bdist_wheel"])
    print("✅ 构建完成")


def check_package():
    """检查包是否有效"""
    print("检查包...")
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        files = os.listdir(dist_dir)
        whl_files = [f for f in files if f.endswith('.whl')]
        tar_files = [f for f in files if f.endswith('.tar.gz')]

        if whl_files and tar_files:
            print(f"✅ 找到包文件: {whl_files[0]} 和 {tar_files[0]}")

            # 尝试导入检查whl包
            if whl_files:
                print("尝试检查wheel包...")
                run_command([sys.executable, "-c", f"import pkg_resources; print('包版本:', pkg_resources.get_distribution('video2live').version)"], check=False)

            return True
        else:
            print("❌ 未找到正确的包文件")
            return False
    return False


def upload_to_pypi(repository="pypi", dry_run=False):
    """上传到PyPI"""
    if dry_run:
        print("干运行模式，不上传")
        return

    print(f"上传到 {repository}...")
    cmd = ["twine", "upload", "dist/*"]

    if repository != "pypi":
        cmd.extend(["--repository", repository])

    run_command(cmd)
    print(f"✅ 上传到 {repository} 完成")


def create_tag(new_version):
    """创建git标签"""
    tag_name = f"v{new_version}"
    print(f"创建git标签: {tag_name}")

    run_command(["git", "add", "setup.py"])
    run_command(["git", "commit", "-m", f"Release version {new_version}"])
    run_command(["git", "tag", tag_name])
    print(f"✅ git标签已创建: {tag_name}")
    print(f"如需推送标签，运行: git push origin {tag_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Video2Live 发布脚本",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="自动递增版本号 (major.minor.patch)"
    )

    parser.add_argument(
        "--version",
        help="手动指定版本号 (如: 1.2.3)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="干运行模式，不上传实际发布"
    )

    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="跳过上传步骤"
    )

    parser.add_argument(
        "--skip-tag",
        action="store_true",
        help="跳过创建git标签"
    )

    parser.add_argument(
        "--repository",
        default="pypi",
        help="上传仓库（pypi或testpypi）"
    )

    parser.add_argument(
        "--check-only",
        action="store_true",
        help="只检查依赖和包，不执行发布"
    )

    parser.add_argument(
        "--build-only",
        action="store_true",
        help="只构建包，不上传或创建标签"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Video2Live 发布脚本")
    print("=" * 50)

    if args.dry_run:
        print("🧪 干运行模式")

    # 检查依赖
    check_dependencies()

    if args.check_only:
        print("✅ 依赖检查通过")
        return

    # 处理版本号
    new_version = None
    if args.bump:
        new_version = bump_version(args.bump)
        update_version_in_setup_py(new_version)
    elif args.version:
        if not validate_version(args.version):
            print(f"❌ 无效的版本号: {args.version}")
            sys.exit(1)
        new_version = args.version
        update_version_in_setup_py(new_version)
    else:
        new_version = get_current_version()
        print(f"使用当前版本: {new_version}")

    if args.build_only:
        print("只构建模式...")

    # 清理
    clean_build_artifacts()

    # 构建
    build_package()

    # 检查
    if not check_package():
        print("❌ 包检查失败")
        sys.exit(1)

    if args.build_only:
        print("✅ 构建完成")
        return

    # 上传
    if not args.skip_upload:
        try:
            upload_to_pypi(args.repository, dry_run=args.dry_run)
        except KeyboardInterrupt:
            print("\n⚠️  上传被用户中断")
            return

    # 创建标签
    if not args.skip_tag and new_version:
        try:
            create_tag(new_version)
        except KeyboardInterrupt:
            print("\n⚠️  标签创建被用户中断")

    print("=" * 50)
    print("✅ 发布脚本执行完成")
    print("=" * 50)

    if args.repository == "pypi":
        print(f"包已发布到PyPI: https://pypi.org/project/video2live/{new_version}")


if __name__ == "__main__":
    main()