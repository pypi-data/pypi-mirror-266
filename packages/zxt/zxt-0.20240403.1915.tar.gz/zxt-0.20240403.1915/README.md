# zxtools

#### 介绍
zx的一个工具集，以Python为主，  
https://pypi.org/project/zxt/

#### 安装教程

1.  python -m pip install .
2.  python -m pip install zxt
3.  python -m pip install --upgrade zxt

#### 上传教程

1.  创建 .pypirc 文件  
    type NUL > %UserProfile%\.pypirc

2.  pypirc 规范  
    https://packaging.python.org/specifications/pypirc/

3.  升级工具  
    python -m pip install --upgrade build  
    python -m pip install --upgrade twine

4.  Generating distribution archives (生成档案)  
    https://packaging.python.org/en/latest/tutorials/packaging-projects/  
    切换到 pyproject.toml 的同级目录, 一般先删除 dist 目录(RMDIR /S .\dist\ /Q)  
    python -m build

5.  Uploading the distribution archives (上传档案)  
    https://packaging.python.org/en/latest/tutorials/packaging-projects/  
    python -m twine upload --repository zxt dist/*

#### 调试教程

1.  卸载 zxt 包  
    python -m pip uninstall zxt

2.  从 zxt 的源码中找到 pth.py 所在目录, 在该目录下执行如下命令:  
    python ./pth.py --dflt_opt=C

3.  源码已关联到 python 环境, 可以写代码调用 zxt 包进行调试了
