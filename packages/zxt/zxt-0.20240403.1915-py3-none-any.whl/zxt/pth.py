# !/usr/bin/env python3
# coding=utf8
"""
一些"代码分析工具"(比如 Pylint)能检出不符合编码风格标准和有潜在风险的代码。
由于 python 2 和 python 3 部分语法不同，"代码分析工具"会识别 .py 文件头部的解释器来判断该文件 python 版本。
如果发现 python 3 文件报出了 invalid syntax 错误，可能是由于被当成了 python 2 扫描。
此时在文件首行加上右面的代码即可：# !/usr/bin/env python3

定义编码【# coding=<encoding name>】参见: http://www.python.org/peps/pep-0263.html

为当前 python 环境添加 pth 文件, 从而添加 package, (pth 文件记录了该 package 源码的路径)
"""


import argparse
import hashlib
import logging
import os
import pathlib
import sysconfig
import typing


def check_package_path(package_path: str) -> bool:
    """
    源码目录 package_path 是不是一个包的根目录,
    package_path: 包的全路径;
    暂定: 包的根目录一定要有一个 __init__.py 文件,
    经测试, 如果一个包的根目录没有 __init__.py 也能 import 成功, 至少能部分使用,
    所以, 用 __init__.py 检查包并不严谨,
    """
    assert os.path.isabs(package_path)

    init_py: str = os.path.join(package_path, "__init__.py")

    if not os.path.isfile(init_py):
        logging.info("no __init__.py file exists in package_path=[{}]".format(package_path))
        return False
    else:
        return True


def generate_pth_info(package_path: str) -> typing.Tuple[str, str]:
    """
    package_path: 包的全路径;
    为 pth 文件的名字添加一些随机字符, 防止出现文件名一样但是文件内容不一样的情况, 导致互相覆盖,
    """
    assert os.path.isabs(package_path)

    # 要把 pth 文件放到哪个目录下,
    destpath: str = sysconfig.get_paths()["purelib"]

    # package_dir : package 所在的目录
    # package_name: package 的名字
    package_dir, package_name = os.path.split(package_path)

    # pth 文件的内容
    content: str = package_dir

    # pth 文件的文件名
    filename: str = "{0}.{1}.pth".format(
        package_name, hashlib.md5(content.encode(encoding="UTF8")).hexdigest().upper()
    )
    # pth 文件的全路径
    filepath: str = os.path.join(destpath, filename)

    return (filepath, content)


def create_file(filepath: str, content: str) -> None:
    """"""
    try:
        with open(file=filepath, mode="w", encoding="utf8") as f:
            f.write(content)
        logging.info("created successfully, {}".format(filepath))
    except Exception as ex:
        logging.info(ex)


def select_file(filepath: str, content: str) -> None:
    """"""
    try:
        with open(file=filepath, mode="r", encoding="utf8") as f:
            content_ok: bool = (f.read() == content)
        logging.info("file [v] content [{0}], {1}".format("v" if content_ok else "x", filepath))
    except Exception as ex:
        logging.info(ex)


def delete_file(filepath: str) -> None:
    """"""
    try:
        os.remove(filepath)
        logging.info("deleted successfully, {}".format(filepath))
    except Exception as ex:
        logging.info(ex)


def select_pth_by_package_name(package_name: str):
    """"""
    files: list = []

    destpath: str = sysconfig.get_paths()["purelib"]

    pathpath: pathlib.Path = pathlib.Path(destpath)

    for item in pathpath.glob("*.pth"):
        if not item.is_file():
            continue

        with open(file=item, mode="r", encoding="utf8") as f:
            for line in f.readlines():
                line: str = line.strip()

                linepath: pathlib.Path = pathlib.Path(line)
                if not linepath.exists():
                    continue

                temppath: pathlib.Path = linepath.joinpath(package_name)
                if not (temppath.exists() and temppath.is_dir()):
                    continue

                files.append(line)
                break

    for file in files:
        print(file)


def main_main(package_path: typing.Optional[str], skip_check: bool, do_while: bool, dflt_opt: str) -> None:
    """"""
    assert (do_while == False) if dflt_opt else True  # 有默认值时, 不允许开启循环,

    if package_path is None:
        # 支持切换当前目录到 package 目录下, 然后直接执行, 这样就不用输入路径了,
        package_path: str = os.getcwd()

    package_path: str = os.path.abspath(package_path)

    CREATE = "C"
    DELETE = "D"
    SELECT = "S"

    is_alive: bool = True
    while is_alive:
        is_alive: bool = do_while

        print("{0}: create pth file, {1}: delete pth file, {2}: select pth file,".format(CREATE, DELETE, SELECT))

        if dflt_opt:
            choice: str = dflt_opt
        else:
            choice: str = input("please input {0}/{1}/{2}: ".format(CREATE, DELETE, SELECT))

        choice: str = choice.upper().strip()
        if choice not in (CREATE, DELETE, SELECT):
            continue

        if not check_package_path(package_path):
            if not skip_check:
                logging.info("check_package_path failed")
                continue
            else:
                logging.info("check_package_path failed, skip")

        filepath, content = generate_pth_info(package_path)

        if False:
            pass
        elif choice == CREATE:
            create_file(filepath, content)
        elif choice == DELETE:
            delete_file(filepath)
        elif choice == SELECT:
            select_file(filepath, content)
        else:
            raise RuntimeError("logically inaccessible")


# 如果安装了 zxt, 那么执行 python -m zxt.pth --help 命令可以直接执行该文件,
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_chk", action="store_true", help="skip check_package_path")  # 默认值是 False
    parser.add_argument("--do_while", action="store_true", help="loop until you manually exit")
    parser.add_argument("--pkg_path", type=str, help="package path to create/delete/select")
    parser.add_argument("--dflt_opt", type=str, help="default option, C/D/S")
    args = parser.parse_args()

    try:
        main_main(package_path=args.pkg_path, skip_check=args.skip_chk, do_while=args.do_while, dflt_opt=args.dflt_opt)
    except KeyboardInterrupt:
        print()
        logging.info("KeyboardInterrupt, will exit")

    exit(0)
