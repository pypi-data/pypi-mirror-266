from setuptools import setup, find_packages

setup(
    name                          = "LyPythonToolbox",                              # 包名
    version                       = "0.1.3",                                        # 版本号
    author                        = "Yue Lin",                                      # 作者名字
    author_email                  = "linyue3h1@gmail.com",                          # 作者邮箱
    description                   = "Ly's personal python toolbox.",                # 简短描述
    long_description              = open("README.md").read(),                       # 长描述，通常是README文件
    long_description_content_type = "text/markdown",                                # 长描述内容的格式，这里为Markdown
    url                           = "https://github.com/YueLin301/LyPythonToolbox", # 项目的URL，通常是GitHub的URL
    packages                      = find_packages(where='src'),
    package_dir                   = {'': 'src'},
    install_requires              = [
        # 'torch>=1.7.1',  # 表示安装torch时，版本需要1.7.1或更高
    ],
    classifiers=[
        "Programming Language :: Python :: 3",  # 3.x
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  # suitable for any OS.
    ],
)
