import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union, cast

from reloadium.corium.ll1l111l11ll1111Il1l1 import llll1ll111ll11l1Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1
from reloadium.lib import extensions_raw
from reloadium.corium.lll1l1111111l1llIl1l1 import llll1ll1ll1l1l11Il1l1
from dataclasses import dataclass

if (TYPE_CHECKING):
    ...


__RELOADIUM__ = True


@dataclass
class l1ll1l1l11llll1lIl1l1(l11111lll111ll11Il1l1):
    ll1111ll11lllll1Il1l1 = 'Multiprocessing'

    l11lll111l11ll11Il1l1 = True

    def __post_init__(l1ll11lllllll11lIl1l1) -> None:
        super().__post_init__()

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'multiprocessing.popen_spawn_posix')):
            l1ll11lllllll11lIl1l1.l11l11llll111lllIl1l1(lll1ll1lll111ll1Il1l1)

        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'multiprocessing.popen_spawn_win32')):
            l1ll11lllllll11lIl1l1.llllll111l1ll1l1Il1l1(lll1ll1lll111ll1Il1l1)

    def l11l11llll111lllIl1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_posix
        multiprocessing.popen_spawn_posix.Popen._launch = extensions_raw.multiprocessing.posix_popen_launch  # type: ignore

    def llllll111l1ll1l1Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        import multiprocessing.popen_spawn_win32
        multiprocessing.popen_spawn_win32.Popen.__init__ = extensions_raw.multiprocessing.wind32_popen_launch  # type: ignore
