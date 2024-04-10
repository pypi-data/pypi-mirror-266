from dataclasses import dataclass, field
from types import CodeType, ModuleType
from typing import TYPE_CHECKING, Any, Callable, Optional
import inspect

from reloadium.lib.extensions.server_extension import ServerExtension

if TYPE_CHECKING:
    pass


__RELOADIUM__ = True


@dataclass
class Numba(ServerExtension):
    NAME = "Numba"

    ALLOWED_IN_FREE = True

    def __post_init__(self) -> None:
        super().__post_init__()

    def enable(self, module: ModuleType) -> None:
        if self.is_import(module, "numba.core.bytecode"):
            self._patch_byte_code()

    def _patch_byte_code(self) -> None:
        import numba.core.bytecode

        def get_code_object(obj) -> CodeType:  # type: ignore
            import ast
            ret = getattr(obj, '__code__', getattr(obj, 'func_code', None))  # type: ignore

            if "__rw_mode__" in ret.co_consts:  # type: ignore
                syntax = ast.parse(inspect.getsource(obj))
                function = syntax.body[0]
                function.decorator_list = []  # type: ignore

                code = compile(syntax, filename=ret.co_filename, mode="exec")  # type: ignore
                ret = code.co_consts[0]

            return ret  # type: ignore

        numba.core.bytecode.get_code_object.__code__ = get_code_object.__code__
