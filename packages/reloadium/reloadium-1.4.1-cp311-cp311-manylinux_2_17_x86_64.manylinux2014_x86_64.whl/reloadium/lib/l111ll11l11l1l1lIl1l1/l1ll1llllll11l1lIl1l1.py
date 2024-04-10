from contextlib import contextmanager
from pathlib import Path
import sys
import types
from threading import Timer, Thread
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type, Set


import reloadium.lib.l111ll11l11l1l1lIl1l1.lll111llll1lll1lIl1l1
from reloadium.corium import ll1l1111lll1lll1Il1l1, l11l1ll1l11ll111Il1l1, llllllllll1lll11Il1l1
from reloadium.corium.l111l1l1l11lll1lIl1l1 import l11111l1ll1l1l11Il1l1
from reloadium.corium.lll11l11l1ll1l11Il1l1 import l1lllllllll1ll11Il1l1, l1l1111lllllll1lIl1l1
from reloadium.corium.lll1llllllllll11Il1l1 import l1111lll11lll1llIl1l1
from reloadium.corium.llllllllll1lll11Il1l1.ll1111l1ll11llllIl1l1 import ll1l11lllll111llIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1ll1111llll11llIl1l1 import l11l1l1111llll11Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.ll1111lll11l1l11Il1l1 import ll11l1llll11ll1lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1lllll11l11llllIl1l1 import l1l1lll1l1l1l1llIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1l11l1l1l11l11lIl1l1 import l11ll11l11111ll1Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l111ll1l11ll1ll1Il1l1 import l1lllll11111ll11Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1lll11l1l1ll1l1Il1l1 import l1llllll1111111lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1l111l11l1ll111Il1l1 import ll11lll1l11l1lllIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l1ll11l1lll1l111Il1l1 import lll1111l11ll1l1lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.l11lllllllll11l1Il1l1 import ll1ll11ll11l1l1lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.llll11lll1ll1l1lIl1l1 import l1ll1l1l11llll1lIl1l1
from reloadium.corium.ll11l11ll11l111lIl1l1 import ll11l11ll11l111lIl1l1
from dataclasses import dataclass, field

if (TYPE_CHECKING):
    from reloadium.corium.lll1llll1111lll1Il1l1 import l1l1l1ll11ll1111Il1l1
    from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111ll1ll1l11llIl1l1


__RELOADIUM__ = True

lll1l11ll11ll11lIl1l1 = ll11l11ll11l111lIl1l1.ll1l11ll1111l111Il1l1(__name__)


@dataclass
class l1llll1ll11lll1lIl1l1:
    lll1llll1111lll1Il1l1: "l1l1l1ll11ll1111Il1l1"

    l111ll11l11l1l1lIl1l1: List[l11111lll111ll11Il1l1] = field(init=False, default_factory=list)

    l11llll1l111lll1Il1l1: List[types.ModuleType] = field(init=False, default_factory=list)

    l1111lll1l1lll1lIl1l1: List[Type[l11111lll111ll11Il1l1]] = field(init=False, default_factory=lambda :[l1l1lll1l1l1l1llIl1l1, l1llllll1111111lIl1l1, l11l1l1111llll11Il1l1, ll1ll11ll11l1l1lIl1l1, ll11lll1l11l1lllIl1l1, l11ll11l11111ll1Il1l1, lll1111l11ll1l1lIl1l1, l1ll1l1l11llll1lIl1l1, ll11l1llll11ll1lIl1l1, l1lllll11111ll11Il1l1])




    ll1111l1111llll1Il1l1: List[Type[l11111lll111ll11Il1l1]] = field(init=False, default_factory=list)
    ll111lllllll111lIl1l1 = (1 if l11111l1ll1l1l11Il1l1().l1l11l11l1l11111Il1l1 in [l1111lll11lll1llIl1l1.llll111lll11ll11Il1l1, l1111lll11lll1llIl1l1.l1111111lllll11lIl1l1] else 5)

    def __post_init__(l1ll11lllllll11lIl1l1) -> None:
        if (l11111l1ll1l1l11Il1l1().ll1ll1111lll1l1lIl1l1.l1l1l1l1111l1l11Il1l1):
            l1ll11lllllll11lIl1l1.l1111lll1l1lll1lIl1l1.remove(lll1111l11ll1l1lIl1l1)

        ll1l11lllll111llIl1l1(ll1ll111llll1111Il1l1=l1ll11lllllll11lIl1l1.l11l1l11ll1ll1l1Il1l1, l1ll1lll1lll111lIl1l1='show-forbidden-dialog').start()

    def l11l1l11ll1ll1l1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        llllllllll1lll11Il1l1.l11l11l11l11l111Il1l1.l11lll1l1l1ll111Il1l1(l1ll11lllllll11lIl1l1.ll111lllllll111lIl1l1)

        l1ll11lllllll11lIl1l1.lll1llll1111lll1Il1l1.ll1lll1l1l111111Il1l1.ll1llll11l1lllllIl1l1()

        if ( not l1ll11lllllll11lIl1l1.ll1111l1111llll1Il1l1):
            return 

        l111ll11l11l1l1lIl1l1 = [l1lll11llll1111lIl1l1.ll1111ll11lllll1Il1l1 for l1lll11llll1111lIl1l1 in l1ll11lllllll11lIl1l1.ll1111l1111llll1Il1l1]
        l1ll11lllllll11lIl1l1.lll1llll1111lll1Il1l1.l1ll1lllllll1111Il1l1.ll11llll1l1111llIl1l1(l1l1111lllllll1lIl1l1.ll1l1l1ll1ll11l1Il1l1, l11l1ll1l11ll111Il1l1.lll1l11111ll11l1Il1l1.ll11ll1ll11ll111Il1l1(l111ll11l11l1l1lIl1l1), 
lll111l1l1l11l11Il1l1='')

    def l1ll111l1l111lllIl1l1(l1ll11lllllll11lIl1l1, l1llll1lllll1l11Il1l1: types.ModuleType) -> None:
        for l1lll11l1l11ll11Il1l1 in l1ll11lllllll11lIl1l1.l1111lll1l1lll1lIl1l1.copy():
            if (l1lll11l1l11ll11Il1l1.l1ll11l11llllll1Il1l1(l1llll1lllll1l11Il1l1)):
                if (( not l1lll11l1l11ll11Il1l1.l11lll111l11ll11Il1l1 and l1ll11lllllll11lIl1l1.lll1llll1111lll1Il1l1.l1ll1lllllll1111Il1l1.lll11l11l1ll1l11Il1l1.llll1l11l111ll1lIl1l1([l1lll11l1l11ll11Il1l1.ll1111ll11lllll1Il1l1]) is False)):
                    l1ll11lllllll11lIl1l1.ll1111l1111llll1Il1l1.append(l1lll11l1l11ll11Il1l1)
                    l1ll11lllllll11lIl1l1.l1111lll1l1lll1lIl1l1.remove(l1lll11l1l11ll11Il1l1)
                    continue
                l1ll11lllllll11lIl1l1.l1l1l111l111l1llIl1l1(l1lll11l1l11ll11Il1l1)

        if (l1llll1lllll1l11Il1l1 in l1ll11lllllll11lIl1l1.l11llll1l111lll1Il1l1):
            return 

        for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy():
            ll11ll1lll11ll11Il1l1.ll11lllllll11l11Il1l1(l1llll1lllll1l11Il1l1)

        l1ll11lllllll11lIl1l1.l11llll1l111lll1Il1l1.append(l1llll1lllll1l11Il1l1)

    def l1l1l111l111l1llIl1l1(l1ll11lllllll11lIl1l1, l1lll11l1l11ll11Il1l1: Type[l11111lll111ll11Il1l1]) -> None:
        ll1llll111l1l1llIl1l1 = l1lll11l1l11ll11Il1l1(l1ll11lllllll11lIl1l1, l1ll11lllllll11lIl1l1.lll1llll1111lll1Il1l1.l1ll1lllllll1111Il1l1.lll11l11l1ll1l11Il1l1)

        l1ll11lllllll11lIl1l1.lll1llll1111lll1Il1l1.ll1ll111l111l1llIl1l1.l1lll1l1111l1l11Il1l1.l1l1l1111ll111l1Il1l1(ll1l1111lll1lll1Il1l1.lllll11l11ll1l1lIl1l1(ll1llll111l1l1llIl1l1))
        ll1llll111l1l1llIl1l1.l1l1ll1lll111l11Il1l1()
        l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.append(ll1llll111l1l1llIl1l1)

        if (l1lll11l1l11ll11Il1l1 in l1ll11lllllll11lIl1l1.l1111lll1l1lll1lIl1l1):
            l1ll11lllllll11lIl1l1.l1111lll1l1lll1lIl1l1.remove(l1lll11l1l11ll11Il1l1)

    @contextmanager
    def l11l111ll1l1l111Il1l1(l1ll11lllllll11lIl1l1) -> Generator[None, None, None]:
        lll1l1lll1lllll1Il1l1 = [ll11ll1lll11ll11Il1l1.l11l111ll1l1l111Il1l1() for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy()]

        for l111l1l11l11111lIl1l1 in lll1l1lll1lllll1Il1l1:
            l111l1l11l11111lIl1l1.__enter__()

        yield 

        for l111l1l11l11111lIl1l1 in lll1l1lll1lllll1Il1l1:
            l111l1l11l11111lIl1l1.__exit__(*sys.exc_info())

    def lll1ll111l1ll1llIl1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy():
            ll11ll1lll11ll11Il1l1.lll1ll111l1ll1llIl1l1(lllll1l1l111lll1Il1l1)

    def ll1llllllllllll1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy():
            ll11ll1lll11ll11Il1l1.ll1llllllllllll1Il1l1(lllll1l1l111lll1Il1l1)

    def l1l1l1ll11ll1ll1Il1l1(l1ll11lllllll11lIl1l1, llll1lll11l111llIl1l1: Exception) -> None:
        for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy():
            ll11ll1lll11ll11Il1l1.l1l1l1ll11ll1ll1Il1l1(llll1lll11l111llIl1l1)

    def l11ll11ll1ll11l1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path, l11111l11ll1l111Il1l1: List["l1111ll1ll1l11llIl1l1"]) -> None:
        for ll11ll1lll11ll11Il1l1 in l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.copy():
            ll11ll1lll11ll11Il1l1.l11ll11ll1ll11l1Il1l1(lllll1l1l111lll1Il1l1, l11111l11ll1l111Il1l1)

    def ll11111l11lllll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        l1ll11lllllll11lIl1l1.l111ll11l11l1l1lIl1l1.clear()
