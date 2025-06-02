# How to convert a video to live photo on MacOS?

<img align=center src="./assets/images/live.png" caption="Live photo" width="32px"   />

## What?

这是一个把视频转换为live photo的工具。

1. 前提

- MacOS 系统
- ffmpeg 工具
- Python 3.8+

2. 首先 安装下 pypi 包

```bash
pip install -U video2live
```

3. 然后运行命令

```bash
video2live ./inifity.mp4 output
```

![](./assets/images/video2live-demo.png)

4. 转换后的结果会放到指定目录下,同时默认会导入到照片中合成

## Why?

最近很
多社交平台都开始支持live图格式，而且之前看别人把非常炫酷的延时视频制作为live图，感觉非常有趣，所以就想着写个工具来玩玩。

## How?

1. 使用 moviepy 提取视频的第一帧图片作为封面
2. 使用 ffmpeg 把视频转为mov格式
3. 最终用 makelive 为 mov 和 jpeg 添加 metadata 信息，导出为同名但不同格式的文件。
4. 最后使用 apple 脚本，把文件导入到照片中合成。

## 项目地址

欢迎 star 和 fork [video2live](https://github.com/sherlockouo/video2live)
