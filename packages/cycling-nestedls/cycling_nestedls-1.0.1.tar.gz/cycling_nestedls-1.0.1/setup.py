import codecs  # 导入处理文件编码的模块
import os  # 导入操作系统相关功能的模块

from setuptools import find_packages, setup  # 从 setuptools 包中导入查找包和设置函数

# 获取当前脚本所在目录的绝对路径
here = os.path.abspath(os.path.dirname(__file__))

# 打开 README.md 文件并读取其中的内容，作为长描述
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# 定义常量：版本号、描述和长描述
VERSION = '1.0.1'
DESCRIPTION = 'A light weight command line menu that supports Windows, MacOS, and Linux'
LONG_DESCRIPTION = 'A light weight command line menu. Supporting Windows, MacOS, and Linux. It has support for hotkeys'

# 设置
setup(
    name="cycling_nestedls",  # 包的名称
    version=VERSION,  # 版本号
    author="aiop102",  # 作者
    author_email="3175454707@qq.com",  # 作者邮箱
    description=DESCRIPTION,  # 描述
    long_description_content_type="text/markdown",  # 长描述的内容类型
    long_description=long_description,  # 长描述
    packages=find_packages(),  # 查找并包括所有包
    install_requires=[  # 安装所需的依赖
        'getch; sys_platform=="linux" or sys_platform=="darwin"',  # 在 Linux 或 macOS 上安装 getch
        'getch; sys_platform=="win32"',  # 在 Windows 上安装 getch
    ],
    keywords=['list', 'nested', 'cycle'],  # 关键字
    classifiers=[  # 分类器
        "Development Status :: 1 - Planning",  # 开发状态
        "Intended Audience :: Developers",  # 预期受众
        "Programming Language :: Python :: 3",  # 使用的编程语言和版本
        "Operating System :: Unix",  # 支持的操作系统 - Unix
        "Operating System :: MacOS :: MacOS X",  # 支持的操作系统 - macOS
        "Operating System :: Microsoft :: Windows",  # 支持的操作系统 - Windows
    ]
)

'''
import codecs
import os

from setuptools import find_packages, setup

# these things are needed for the README.md show on pypi
here = os.path.abspath(os.path.dirname("E:\ForDocument\Code_items\ForPython\cycling_nestedls\README.md"))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '1.0.0'
DESCRIPTION = 'A light weight command line menu that supports Windows, MacOS, and Linux'
LONG_DESCRIPTION = 'A light weight command line menu. Supporting Windows, MacOS, and Linux. It has support for hotkeys'

# Setting up
setup(
    name="cycling_nestedls",
    version=VERSION,
    author="aiop102",
    author_email="3175454707@qq.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'getch; platform_system=="Unix"',
        'getch; platform_system=="Windows"',
    ],
    keywords=['list','nested','cycle'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
'''
