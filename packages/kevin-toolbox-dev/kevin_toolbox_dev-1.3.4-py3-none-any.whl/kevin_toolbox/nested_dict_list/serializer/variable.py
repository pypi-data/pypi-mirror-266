import os
from kevin_toolbox.computer_science.algorithm.registration import Registry

SERIALIZER_BACKEND = Registry(uid="SERIALIZER_BACKEND")

# 从 kevin_toolbox/nested_dict_list/serializer/backends 下收集被注册的 backend
SERIALIZER_BACKEND.collect_from_paths(path_ls=[os.path.join(os.path.dirname(__file__), "backends"), ],
                                      b_execute_now=False)
