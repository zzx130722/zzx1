"""distutils.spawn.find_executable 的替身。

标准库里它就是「在 PATH 里找可执行文件」，shutil.which 功能完全一样。
"""

import shutil


def find_executable(executable, path=None):
    return shutil.which(executable, path=path)
