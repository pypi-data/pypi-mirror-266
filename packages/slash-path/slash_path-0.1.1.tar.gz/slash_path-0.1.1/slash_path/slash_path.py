import os
from pathlib import Path, PurePath


def trans_nt_slash_path(path: str) -> str:
    """
    param: str file path
    return: str file path with "\\" replaced by '/'
    """
    path = trans_raw_string(path)
    raw_path = r"{}".format(path)
    separator = os.path.normpath("/")
    changeSlash = lambda x: '/'.join(x.split(separator))
    if raw_path.startswith('\\'):
        return '/' + changeSlash(raw_path)
    else:
        return changeSlash(raw_path)


def trans_raw_string(path: str) -> str:
    """Returns a raw string representation of strVar.
    Will replace '\\' with '/'
    :param: str String to change to raw
    """
    if type(path) is str:
        strVarRaw = r'%s' % path
        new_string=''
        escape_dict={'\a':r'\a', '\b':r'\b', '\c':r'\c', '\f':r'\f', '\n':r'\n',
                    '\r':r'\r', '\t':r'\t', '\v':r'\v', '\'':r'\'', '\"':r'\"',
                    '\0':r'\0', '\1':r'\1', '\2':r'\2', '\3':r'\3', '\4':r'\4',
                    '\5':r'\5', '\6':r'\6', '\7':r'\7', '\8':r'\8', '\9':r'\9'}
        for char in strVarRaw:
            try: new_string+=escape_dict[char]
            except KeyError: new_string+=char
        return new_string
    else:
        return path


class SlashPath:

    def __new__(cls, path: str):
        if os.name == 'nt':
            path = trans_nt_slash_path(path)
        return Path(path)

