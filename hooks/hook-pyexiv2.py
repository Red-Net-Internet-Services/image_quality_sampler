# hooks/hook-pyexiv2.py
# pyinstaller --additional-hooks-dir hooks/ [...]
import os
import glob

from PyInstaller import compat
from PyInstaller.utils.hooks import get_package_paths


#  Modify Path for pyexiv2 to compile properly in pyinstaller.
if compat.is_win:
    binaries = []
    datas = []
    package_root_base, package_root = get_package_paths('pyexiv2')

    libs = glob.glob(os.path.join(package_root, 'lib', 'py3.*-win', '*.pyd'))
    datas += [(lib,
               os.path.dirname(os.path.relpath(lib, package_root_base)))
              for lib in libs]

    libs = glob.glob(os.path.join(package_root, 'lib', '*.dll'))
    datas += [(lib,
               os.path.dirname(os.path.relpath(lib, package_root_base)))
              for lib in libs]
