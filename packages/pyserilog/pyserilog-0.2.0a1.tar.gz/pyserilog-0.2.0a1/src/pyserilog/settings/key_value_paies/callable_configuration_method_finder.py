import inspect
from inspect import FullArgSpec
from types import ModuleType

import pyserilog.settings.key_value_paies.surrogate_configuration_methods as sm


class MethodInfo:
    def __init__(self, klass_type: type, method_name: str, func, args: FullArgSpec):
        self.klass_type = klass_type
        self.method_name = method_name
        self.args = args
        self.func = func

    def __str__(self):
        return f"{self.klass_type} , {self.method_name} , {self.func}"


class CallableConfigurationMethodFinder:

    @staticmethod
    def find_configuration_methods(modules: list[ModuleType], config_type: type):
        all_modules = [sm]
        all_modules.extend(modules)
        result = []
        for module in all_modules:
            all_module_klass = inspect.getmembers(module, predicate=inspect.isclass)
            for _, klass_type in all_module_klass:
                methods = inspect.getmembers_static(klass_type, predicate=lambda x: isinstance(x, staticmethod))
                for method_name, _ in methods:
                    func = getattr(klass_type, method_name)
                    args = inspect.getfullargspec(func)

                    if len(args.args) == 0:
                        continue
                    first_arg_name = args.args[0]
                    if len(args.annotations) > 0 and first_arg_name in args.annotations and \
                            args.annotations[first_arg_name] == config_type:
                        info = MethodInfo(klass_type, method_name, func, args)
                        result.append(info)
        return result
