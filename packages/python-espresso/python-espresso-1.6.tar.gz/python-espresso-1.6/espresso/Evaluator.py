from .Parser import StackFrame
from .Lexer import Lexer
from .utils import Stack

from .exceptions import EspressoInvalidSyntax, EspressoTypeError, EspressoNameError

from typing import NamedTuple, List, Union


class Func(NamedTuple):
    func_call: callable
    func_name: List[str]
    func_argument_types: List[str]


class Evaluator:
    def __init__(self) -> None:
        self.namespace = {}

    def get_function(self, func_name: Union[List[str], str]) -> Func:
        func_call_chain = (
            func_name if isinstance(func_name, list) else func_name.split(".")
        )
        final_func = self.namespace
        for call in func_call_chain:
            final_func = final_func.get(call)
            if not final_func:
                raise EspressoNameError(
                    'Function "{}" is not defined in Namespace "{}"'.format(
                        func_call_chain[-1], ".".join(func_call_chain[:-1])
                    )
                )
        


        return final_func

    def define_function(self, f: Func):
        def_space = self.namespace
        for name in f.func_name[:-1]:
            def_space = self.namespace.setdefault(name, {})

        def_space[f.func_name[-1]] = f

    def is_variadic(self, func: Func, params: List[Union[str, int]]):
        return len(func.func_argument_types) > 0 and func.func_argument_types[
            0
        ].startswith("*")

    def get_typed_params(self, func: Func, params: List[Union[str, int]]):
        param_types = func.func_argument_types
        func_name = ".".join(func.func_name)
        parsed_params = []
        variadic = self.is_variadic(func, params)

        if variadic:
            param_types = [param_types[0][1:]] * len(param_types)

        # Handling overloading
        if not variadic and len(param_types) < len(params):
            raise EspressoTypeError(f"Function '{func_name}' expects {len(param_types)} parameters, but {len(params)} were provided.")

        try:
            for i, param_type in enumerate(param_types):
                param_type = param_type.strip().lower()
                if param_type.endswith("?"):
                    # if a corresponding param doesn't exist but it is an optional type
                    if len(params) <= i:
                        parsed_params.append(None)
                        continue
                    else:
                        param_type = param_type[:-1]

                if param_type == "str":
                    if not isinstance(params[i], str):
                        raise EspressoTypeError(
                            f"Expected type 'str' for parameter {i+1} of function '{func_name}', but received {type(params[i])} instead."
                        )
                elif param_type == "int":
                    if not isinstance(params[i], int):
                        raise EspressoTypeError(
                            f"Expected type 'int' for parameter {i+1} of function '{func_name}', but received {type(params[i])} instead."
                        )
                elif param_type == "any":
                    pass
                else:
                    raise EspressoNameError(
                        f"Unknown parameter type '{param_type}' for parameter {i+1} of function '{func_name}'."
                    )

                parsed_params.append(params[i])
        except IndexError:
            raise EspressoTypeError(
                f"Not enough parameters provided for function '{func_name}'."
            )

        return parsed_params

    def _eval_stack_frame(self, frame: StackFrame):
        func_def = self.get_function(frame.func_chain)
        func_params = []

        for func_param in frame.func_params:
            if isinstance(func_param, StackFrame):
                self._eval_stack_frame(func_param)
            elif isinstance(func_param, int) or isinstance(func_param, str):
                func_params.append(func_param)
            else:
                assert False, "_eval_stack_frame: Undefined stack param type {}".format(
                    type(func_param)
                )

        typed_params = self.get_typed_params(func_def, func_params)
        is_variadic = self.is_variadic(func_def, func_params)

        if is_variadic:
            return func_def.func_call(typed_params)
        else:
            return func_def.func_call(*typed_params)

    def eval(self, call_stack: Stack) -> any:
        top = call_stack.pop()
        return self._eval_stack_frame(top)
