from abc import ABC
from contextlib import contextmanager
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, ClassVar, Dict, Generator, List, Optional, Tuple, Type

from reloadium.corium.lll11l11l1ll1l11Il1l1 import l1lllllllll1ll11Il1l1, ll1ll1l1111l1l1lIl1l1
from reloadium.corium.ll11l11ll11l111lIl1l1 import ll11l111l11l111lIl1l1, ll11l11ll11l111lIl1l1
from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111ll1ll1l11llIl1l1, l1111ll1ll1l1l11Il1l1
from reloadium.corium.l11ll11l1l1llll1Il1l1 import llllll1l11lll11lIl1l1, lll11l1l11l11l1lIl1l1
from dataclasses import dataclass, field

if (TYPE_CHECKING):
    from reloadium.lib.l111ll11l11l1l1lIl1l1.l1ll1llllll11l1lIl1l1 import l1llll1ll11lll1lIl1l1


__RELOADIUM__ = True

lll1l11ll11ll11lIl1l1 = ll11l11ll11l111lIl1l1.ll1l11ll1111l111Il1l1(__name__)


@dataclass
class l11111lll111ll11Il1l1:
    l1ll1llllll11l1lIl1l1: "l1llll1ll11lll1lIl1l1"
    lll11l11l1ll1l11Il1l1: l1lllllllll1ll11Il1l1

    ll1111ll11lllll1Il1l1: ClassVar[str] = NotImplemented
    l1lll1ll1lll11llIl1l1: bool = field(init=False, default=False)

    lll11lll1lll11l1Il1l1: ll11l111l11l111lIl1l1 = field(init=False)

    ll1l1ll11111ll1lIl1l1: bool = field(init=False, default=False)

    l11lll111l11ll11Il1l1 = False

    def __post_init__(l1ll11lllllll11lIl1l1) -> None:
        l1ll11lllllll11lIl1l1.lll11lll1lll11l1Il1l1 = ll11l11ll11l111lIl1l1.ll1l11ll1111l111Il1l1(l1ll11lllllll11lIl1l1.ll1111ll11lllll1Il1l1)
        l1ll11lllllll11lIl1l1.lll11lll1lll11l1Il1l1.l1ll1l1ll11lll11Il1l1('Creating extension')
        l1ll11lllllll11lIl1l1.l1ll1llllll11l1lIl1l1.lll1llll1111lll1Il1l1.ll111ll1ll1l1l11Il1l1.l1ll1111ll111l1lIl1l1(l1ll11lllllll11lIl1l1.l1ll1l1lll1ll1llIl1l1())
        l1ll11lllllll11lIl1l1.ll1l1ll11111ll1lIl1l1 = isinstance(l1ll11lllllll11lIl1l1.lll11l11l1ll1l11Il1l1, ll1ll1l1111l1l1lIl1l1)

    def l1ll1l1lll1ll1llIl1l1(l1ll11lllllll11lIl1l1) -> List[Type[l1111ll1ll1l1l11Il1l1]]:
        l11111l11lll1l11Il1l1 = []
        llll1ll1l11lllllIl1l1 = l1ll11lllllll11lIl1l1.lllllll1l111llllIl1l1()
        for lll1llll1lll1l1lIl1l1 in llll1ll1l11lllllIl1l1:
            lll1llll1lll1l1lIl1l1.ll1lll11111lll11Il1l1 = l1ll11lllllll11lIl1l1.ll1111ll11lllll1Il1l1

        l11111l11lll1l11Il1l1.extend(llll1ll1l11lllllIl1l1)
        return l11111l11lll1l11Il1l1

    def lll1111ll11l1l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        l1ll11lllllll11lIl1l1.l1lll1ll1lll11llIl1l1 = True

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        pass

    @classmethod
    def l1ll11l11llllll1Il1l1(l111l1l1ll1111llIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> bool:
        if ( not hasattr(lll1ll1lll111ll1Il1l1, '__name__')):
            return False

        l11111l11lll1l11Il1l1 = lll1ll1lll111ll1Il1l1.__name__.split('.')[0].lower() == l111l1l1ll1111llIl1l1.ll1111ll11lllll1Il1l1.lower()
        return l11111l11lll1l11Il1l1

    def lllllll1111lllllIl1l1(l1ll11lllllll11lIl1l1) -> None:
        lll1l11ll11ll11lIl1l1.l1ll1l1ll11lll11Il1l1(''.join(['Disabling extension ', '{:{}}'.format(l1ll11lllllll11lIl1l1.ll1111ll11lllll1Il1l1, '')]))

    @contextmanager
    def l11l111ll1l1l111Il1l1(l1ll11lllllll11lIl1l1) -> Generator[None, None, None]:
        yield 

    def l1l1ll1lll111l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        pass

    def l1l1l1ll11ll1ll1Il1l1(l1ll11lllllll11lIl1l1, llll1lll11l111llIl1l1: Exception) -> None:
        pass

    def llllll1lll1ll11lIl1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str, l111ll1l1l111ll1Il1l1: bool) -> Optional[llllll1l11lll11lIl1l1]:
        return None

    async def l1llll11l1ll11l1Il1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str) -> Optional[lll11l1l11l11l1lIl1l1]:
        return None

    def lll1l11l1l1lllllIl1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str) -> Optional[llllll1l11lll11lIl1l1]:
        return None

    async def lll111ll111ll1llIl1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str) -> Optional[lll11l1l11l11l1lIl1l1]:
        return None

    def ll1llllllllllll1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        pass

    def lll1ll111l1ll1llIl1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        pass

    def l11ll11ll1ll11l1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path, l11111l11ll1l111Il1l1: List[l1111ll1ll1l11llIl1l1]) -> None:
        pass

    def __eq__(l1ll11lllllll11lIl1l1, ll1ll11l11lll1llIl1l1: Any) -> bool:
        return id(ll1ll11l11lll1llIl1l1) == id(l1ll11lllllll11lIl1l1)

    def lllllll1l111llllIl1l1(l1ll11lllllll11lIl1l1) -> List[Type[l1111ll1ll1l1l11Il1l1]]:
        return []

    def ll1l1l11llllll11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType, l1ll1lll1lll111lIl1l1: str) -> bool:
        l11111l11lll1l11Il1l1 = (hasattr(lll1ll1lll111ll1Il1l1, '__name__') and lll1ll1lll111ll1Il1l1.__name__ == l1ll1lll1lll111lIl1l1)
        return l11111l11lll1l11Il1l1


@dataclass(repr=False)
class ll111ll11llllll1Il1l1(llllll1l11lll11lIl1l1):
    lll1l1l1l11l111lIl1l1: l11111lll111ll11Il1l1

    def __repr__(l1ll11lllllll11lIl1l1) -> str:
        return 'ExtensionMemento'


@dataclass(repr=False)
class l111111ll111111lIl1l1(lll11l1l11l11l1lIl1l1):
    lll1l1l1l11l111lIl1l1: l11111lll111ll11Il1l1

    def __repr__(l1ll11lllllll11lIl1l1) -> str:
        return 'AsyncExtensionMemento'
