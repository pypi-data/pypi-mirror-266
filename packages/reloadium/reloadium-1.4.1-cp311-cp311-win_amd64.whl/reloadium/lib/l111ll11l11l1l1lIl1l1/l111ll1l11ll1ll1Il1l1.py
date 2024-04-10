from dataclasses import dataclass, field
from types import CodeType, ModuleType
from typing import TYPE_CHECKING, Any, Callable, Optional
import inspect

from reloadium.lib.l111ll11l11l1l1lIl1l1.ll111ll1111lll11Il1l1 import ll1ll111111l1111Il1l1

if (TYPE_CHECKING):
    pass


__RELOADIUM__ = True


@dataclass
class l1lllll11111ll11Il1l1(ll1ll111111l1111Il1l1):
    ll1111ll11lllll1Il1l1 = 'Numba'

    l11lll111l11ll11Il1l1 = True

    def __post_init__(l1ll11lllllll11lIl1l1) -> None:
        super().__post_init__()

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'numba.core.bytecode')):
            l1ll11lllllll11lIl1l1.l1l111l11lllll1lIl1l1()

    def l1l111l11lllll1lIl1l1(l1ll11lllllll11lIl1l1) -> None:
        import numba.core.bytecode

        def l1111l111111llllIl1l1(l11l11l11ll1ll11Il1l1) -> CodeType:  # type: ignore
            import ast
            l11111l11lll1l11Il1l1 = getattr(l11l11l11ll1ll11Il1l1, '__code__', getattr(l11l11l11ll1ll11Il1l1, 'func_code', None))  # type: ignore

            if ('__rw_mode__' in l11111l11lll1l11Il1l1.co_consts):  # type: ignore
                l1llll11l1l1ll11Il1l1 = ast.parse(inspect.getsource(l11l11l11ll1ll11Il1l1))
                l111lll1ll1111l1Il1l1 = l1llll11l1l1ll11Il1l1.body[0]
                l111lll1ll1111l1Il1l1.decorator_list = []  # type: ignore

                l11111l1l1ll11l1Il1l1 = compile(l1llll11l1l1ll11Il1l1, filename=l11111l11lll1l11Il1l1.co_filename, mode='exec')  # type: ignore
                l11111l11lll1l11Il1l1 = l11111l1l1ll11l1Il1l1.co_consts[0]

            return l11111l11lll1l11Il1l1  # type: ignore

        numba.core.bytecode.get_code_object.__code__ = l1111l111111llllIl1l1.__code__
