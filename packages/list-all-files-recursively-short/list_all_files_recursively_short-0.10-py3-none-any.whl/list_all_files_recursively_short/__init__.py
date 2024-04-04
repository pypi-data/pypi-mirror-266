import ctypes
import sys
from functools import cache
from ctypes import wintypes
import os
from collections import namedtuple
import pathlib

bufferconfig = sys.modules[__name__]
bufferconfig.buffer_long_path = 4096
fields_cor = "folder file path ext name83"
classname_cor = "files"
FilePathInfos = namedtuple(classname_cor, fields_cor)
windll = ctypes.LibraryLoader(ctypes.WinDLL)
ntdll = windll.ntdll
kernel32 = windll.kernel32
_GetShortPathNameW = kernel32.GetShortPathNameW
_GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
_GetShortPathNameW.restype = wintypes.DWORD


@cache
def is_long_path():
    if hasattr(ntdll, "RtlAreLongPathsEnabled"):
        ntdll.RtlAreLongPathsEnabled.restype = ctypes.c_ubyte
        ntdll.RtlAreLongPathsEnabled.argtypes = ()

        def are_long_paths_enabled():
            return bool(ntdll.RtlAreLongPathsEnabled())
    else:

        def are_long_paths_enabled():
            return False


def get_short_path_name(long_name):
    try:
        if not is_long_path():
            output_buf_size = 270
        else:
            output_buf_size = bufferconfig.buffer_long_path
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        return output_buf.value
    except Exception as e:
        sys.stderr.write(f"{e}\n")
    return long_name


@cache
def get_short_path_name_cached(long_name):
    try:
        if not is_long_path():
            output_buf_size = 270
        else:
            output_buf_size = bufferconfig.buffer_long_path
        output_buf = ctypes.create_unicode_buffer(output_buf_size)
        _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
        return output_buf.value
    except Exception as e:
        sys.stderr.write(f"{e}\n")
    return long_name


def get_folder_file_complete_path(folders, maxsubfolders=-1, use_cache=False):
    if isinstance(folders, str):
        folders = [folders]
    folders = list(set([os.path.normpath(x) for x in folders]))
    folders = [x for x in folders if os.path.exists(x)]
    folders = [x for x in folders if os.path.isdir(x)]

    listOfFiles2 = []
    limit = 1000000000000
    checkdepth = False
    for dirName in folders:
        if maxsubfolders > -1:
            sepa = dirName.count("\\") + dirName.count("/")
            limit = sepa + maxsubfolders
        if limit < 1000000000000:
            checkdepth = True
        for dirpath, dirnames, filenames in os.walk(dirName):
            if checkdepth:
                depthok = dirpath.count("\\") + dirpath.count("/") <= limit
            else:
                depthok = True
            ra = [
                FilePathInfos(
                    dirpath,
                    file,
                    (j := os.path.normpath(os.path.join(dirpath, file))),
                    pathlib.Path(file).suffix,
                    get_short_path_name(j)
                    if use_cache
                    else get_short_path_name_cached(j),
                )
                for file in filenames
                if depthok
            ]
            if ra:
                listOfFiles2.extend(ra)
    return listOfFiles2
