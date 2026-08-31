# 提供统一的绝对路径

import os

def get_project_root() ->str:
    return os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))

def get_abs_path(relative_path:str) ->str:
    return os.path.join(get_project_root(), relative_path)

if __name__ == '__main__':
    print(get_project_root())