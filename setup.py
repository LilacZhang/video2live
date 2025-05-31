from setuptools import setup, find_packages

setup(
    name="video2live",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "imageio>=2.37.0",
        "Pillow>=11.1.0",
        "imageio-ffmpeg>=0.6.0",
        "makelive>=0.6.2",
    ],
    entry_points={
        "console_scripts": [
            "video2live = video2live.__main__:main",
        ],
    },
    author="SherlockOuO",
    author_email="wdf.coder@gmail.com",
    description="Convert videos to iOS Live Photos",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sherlockouo/video2live",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
