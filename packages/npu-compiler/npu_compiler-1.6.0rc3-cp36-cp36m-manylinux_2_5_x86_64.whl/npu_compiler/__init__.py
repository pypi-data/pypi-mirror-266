#coding: utf-8

import sys
from collections import OrderedDict
from prettytable import PrettyTable

# 编译器版本
VERSION = "1.6.0rc3"

class EnvironmentChecker(object):
    # 编译器支持的torch版本
    GRUS_PY37_SUPPORT_TORCH_VERSION = [(1, 10), (1, 11), (1, 12), (1, 13)]
    APUS_PY37_SUPPORT_TORCH_VERSION = [(1, 12), (1, 13)]

    CORE_PY37_SUPPORT_TORCH_DICT = {
        "APUS": APUS_PY37_SUPPORT_TORCH_VERSION,
        "GRUS": GRUS_PY37_SUPPORT_TORCH_VERSION,
        }

    CORE_SUPPORT_TORCH_DICT = {
        (3, 7): CORE_PY37_SUPPORT_TORCH_DICT,
        }

    # 编译器版本适配信息 (提供用户)
    COMPATIBILITY_INFO_MAP = OrderedDict([
        ("PYTHON2.7", OrderedDict([
             ("LEO",  ["TF"]),
             ("APUS", ["TF"]),
             ("GRUS", ["TF"]),
         ])),
        ("PYTHON3.6", OrderedDict([
             ("LEO",  ["TF"]),
             ("APUS", ["TF"]),
             ("GRUS", ["TF"]),
         ])),
        ("PYTHON3.7", OrderedDict([
             ("LEO",  ["TF"]),
             ("APUS", ["TF", "PT"]),
             ("GRUS", ["TF", "PT"]),
         ])),
    ])

    @classmethod
    def get_python_version(cls):
        python_major = sys.version_info[0]
        python_minor = sys.version_info[1]
        return (python_major, python_minor)

    @classmethod
    def check_python_env(cls):
        if cls.get_python_version() not in NpuVersionManager.SUPPORT_PYTHON_VERSION:
            print("[ERROR] The Python requirement is Python2.7, Python3.6 or Python3.7!")
            sys.exit(1)

    @classmethod
    def __get_torch_version(cls):
        try:
            import torch
            torch_version = torch.__version__
        except ImportError:
            print("[ERROR] Unable to import PyTorch module! Please confirm if PyTorch module has already been installed in the NPU compiler runtime environment.")
            sys.exit(1)

        version = torch_version.split(".")
        torch_major = int(version[0])
        torch_minor = int(version[1])
        return (torch_major, torch_minor)

    @classmethod
    def __torch_version_check(cls, python_version, core_version):
        torch_version  = cls.__get_torch_version()

        if torch_version not in cls.CORE_SUPPORT_TORCH_DICT[python_version][core_version]:
            print("[ERROR] NPU %s Compiler in python %s environment only support PyTorch version %s"\
                    % (core_version, python_version, str(cls.CORE_SUPPORT_TORCH_DICT[python_version][core_version])))
            print("        Now PyTorch version is %s!" % str(torch_version))
            sys.exit(1)

    @classmethod
    def check_torch_env(cls, core_version):
        # 各版本core在config中调用该接口检测
        python_version = cls.get_python_version()
        if python_version not in cls.CORE_SUPPORT_TORCH_DICT.keys():
            print("[ERROR] NPU %s Compiler in python %s environment don't support to process PyTorch framework models!"\
                    % (core_version, str(python_version)))
            sys.exit(1)
        else:
            cls.__torch_version_check(python_version, core_version)

    @classmethod
    def get_env_compatibility_info(cls):
        core_version     = NpuVersionManager.SUPPORT_CORE_VERSION
        nov_core_version = [core for core in core_version if not core.startswith("V")]
        first_row_value   = ["PYTHON VERSION(COL) \ CORE_VERSION(ROW)"]
        for core_name in nov_core_version:
            first_row_value.append(core_name)

        table = PrettyTable(first_row_value)
        for python_version, core_and_framework in cls.COMPATIBILITY_INFO_MAP.items():
            row_value = [python_version]
            for core_name, framework in core_and_framework.items():
                row_value.append(framework)

            table.add_row(row_value)

        for value in first_row_value:
            table.align[value] = "c"
        return table


class NpuVersionManager(object):
    # 编译器支持的芯片版本名称 (更新请按照版本顺序, 与COREMAP一致)
    SUPPORT_CORE_VERSION = ["LEO", "APUS", "GRUS", "V100", "V120", "V150"]
    # 编译器目前支持的前端深度学习框架
    SUPPORT_FRAMEWORKS   = ["TF", "PT"]
    # 编译器目前支持python
    SUPPORT_PYTHON_VERSION = [(2, 7), (3, 6), (3, 7)]
    # 当前运行环境下的python版本
    CURRENT_PYTHON_VERSION = EnvironmentChecker.get_python_version()

    @classmethod
    def get_npu_funcs_dict(cls):
        from npu_compiler.v100.config import Config as Config_1_0
        import npu_compiler.v100.compiler as compiler_1_0
        from npu_compiler.v120.config import Config as Config_1_2
        import npu_compiler.v120.compiler as compiler_1_2
        from npu_compiler.v150.config import Config as Config_1_5
        import npu_compiler.v150.compiler as compiler_1_5

        def load_1_0(config_dict, config_para):
            Config_1_0.load_config(config_dict, config_para)

        def load_1_2(config_dict, config_para):
            Config_1_2.load_config(config_dict, config_para)

        def load_1_5(config_dict, config_para):
            Config_1_5.load_config(config_dict, config_para)

        def run_1_0():
            compiler_1_0.run()

        def run_1_2():
            compiler_1_2.run()

        def run_1_5():
            compiler_1_5.run()

        def quant_1_2():
            compiler_1_2.quant()

        # 编译器各版本接口汇总
        COREMAP = {
            "LEO":    {"load": load_1_0, "run":run_1_0},
            "APUS":   {"load": load_1_2, "run":run_1_2, "quant":quant_1_2},
            "GRUS":   {"load": load_1_5, "run":run_1_5},
            "V100":   {"load": load_1_0, "run":run_1_0},
            "V120":   {"load": load_1_2, "run":run_1_2, "quant":quant_1_2},
            "V150":   {"load": load_1_5, "run":run_1_5},
            }

        return COREMAP

    @classmethod
    def get_ops_table_dict(cls):
        # 各版本 所支持算子导出相关
        from npu_compiler.v100.ops import OpsFactory as OpsFactory_1_0_tf
        from npu_compiler.v120.tf_ops import OpsFactory as OpsFactory_1_2_tf
        from npu_compiler.v150.tf_ops import OpsFactory as OpsFactory_1_5_tf
        if cls.CURRENT_PYTHON_VERSION == (3, 7):
            from npu_compiler.v150.pt_ops import OpsFactory as OpsFactory_1_5_pt
            from npu_compiler.v120.pt_ops import OpsFactory as OpsFactory_1_2_pt

            OPS_TABLES_DICT = {
                "LEO":  {"TF":  [OpsFactory_1_0_tf],
                         "ALL": [OpsFactory_1_0_tf]},
                "APUS": {"TF":  [OpsFactory_1_2_tf],
                         "PT":  [OpsFactory_1_2_pt],
                         "ALL": [OpsFactory_1_2_tf, OpsFactory_1_2_pt]},
                "GRUS": {"TF":  [OpsFactory_1_5_tf],
                         "PT":  [OpsFactory_1_5_pt],
                         "ALL": [OpsFactory_1_0_tf, OpsFactory_1_5_pt]},
                "V100": {"TF":  [OpsFactory_1_0_tf],
                         "ALL": [OpsFactory_1_0_tf]},
                "V120": {"TF":  [OpsFactory_1_2_tf],
                         "PT":  [OpsFactory_1_2_pt],
                         "ALL": [OpsFactory_1_2_tf, OpsFactory_1_2_pt]},
                "V150": {"TF":  [OpsFactory_1_5_tf],
                         "PT":  [OpsFactory_1_5_pt],
                         "ALL": [OpsFactory_1_0_tf, OpsFactory_1_5_pt]},
                "ALL":  {"TF":  [OpsFactory_1_0_tf, OpsFactory_1_2_tf, OpsFactory_1_5_tf],
                         "PT":  [OpsFactory_1_2_pt, OpsFactory_1_5_pt],
                         "ALL": [OpsFactory_1_0_tf, OpsFactory_1_2_tf, OpsFactory_1_2_pt, OpsFactory_1_5_tf, OpsFactory_1_5_pt]},
                }
        else:
            OPS_TABLES_DICT = {
                "LEO":  {"TF":  [OpsFactory_1_0_tf],
                         "ALL": [OpsFactory_1_0_tf]},
                "APUS": {"TF":  [OpsFactory_1_2_tf],
                         "ALL": [OpsFactory_1_2_tf]},
                "GRUS": {"TF":  [OpsFactory_1_5_tf],
                         "ALL": [OpsFactory_1_5_tf]},
                "V100": {"TF":  [OpsFactory_1_0_tf],
                         "ALL": [OpsFactory_1_0_tf]},
                "V120": {"TF":  [OpsFactory_1_2_tf],
                         "ALL": [OpsFactory_1_2_tf]},
                "V150": {"TF":  [OpsFactory_1_5_tf],
                         "ALL": [OpsFactory_1_5_tf]},
                "ALL":  {"TF":  [OpsFactory_1_0_tf, OpsFactory_1_2_tf, OpsFactory_1_5_tf],
                         "ALL": [OpsFactory_1_0_tf, OpsFactory_1_2_tf, OpsFactory_1_5_tf]},
                }
        return OPS_TABLES_DICT


EnvironmentChecker.check_python_env()

