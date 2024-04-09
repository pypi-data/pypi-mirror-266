from setuptools import setup, find_packages

setup(
    name="lanQ",
    version="1.2",
    author="shijin",
    author_email="shijin@pjlab.org.cn",
    description="Language quality evaluation tool.",
    # 项目主页
    url="https://gitlab.pjlab.org.cn/qa/lanq",
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages()
)
