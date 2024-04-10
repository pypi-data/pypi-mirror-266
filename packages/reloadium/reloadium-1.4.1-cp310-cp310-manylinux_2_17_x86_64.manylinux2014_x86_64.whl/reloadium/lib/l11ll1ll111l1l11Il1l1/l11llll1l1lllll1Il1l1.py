from pathlib import Path
import sys
import threading
from types import CodeType, FrameType, ModuleType
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, cast

from reloadium.corium import l11l1ll1l11ll111Il1l1, ll1llllll11l1ll1Il1l1, public, lll1llllllllll11Il1l1, llllllllll1lll11Il1l1
from reloadium.corium.l1ll11lllllll111Il1l1 import l1111ll1llllll11Il1l1, l1l1ll11lll111l1Il1l1
from reloadium.corium.ll1llllll11l1ll1Il1l1 import l1l1l1lll1l1lll1Il1l1, ll1111l1ll1lll1lIl1l1, ll1l1l111111llllIl1l1
from reloadium.corium.lll1l1111111l1llIl1l1 import llll1ll1ll1l1l11Il1l1
from reloadium.corium.ll11l11ll11l111lIl1l1 import ll11l11ll11l111lIl1l1
from reloadium.corium.lll11111llll1lllIl1l1 import l1llllll11lllll1Il1l1
from reloadium.corium.l11ll11l1l1llll1Il1l1 import llllll1l11lll11lIl1l1, lll11l1l11l11l1lIl1l1
from dataclasses import dataclass, field


__RELOADIUM__ = True

__all__ = ['l1lll1l11llll1l1Il1l1', 'l1111l1111l11111Il1l1', 'll1l1111l1111l1lIl1l1']


lll1l11ll11ll11lIl1l1 = ll11l11ll11l111lIl1l1.ll1l11ll1111l111Il1l1(__name__)


class l1lll1l11llll1l1Il1l1:
    @classmethod
    def l11llll11111lll1Il1l1(l1ll11lllllll11lIl1l1) -> Optional[FrameType]:
        l11l1ll1l11l1111Il1l1: FrameType = sys._getframe(2)
        l11111l11lll1l11Il1l1 = next(llllllllll1lll11Il1l1.l11l1ll1l11l1111Il1l1.lll11ll1l1l1llllIl1l1(l11l1ll1l11l1111Il1l1))
        return l11111l11lll1l11Il1l1


class l1111l1111l11111Il1l1(l1lll1l11llll1l1Il1l1):
    @classmethod
    def ll11l1llll1lll11Il1l1(l111l1l1ll1111llIl1l1, l111l1l1ll11ll1lIl1l1: List[Any], ll1l1ll1lll1ll1lIl1l1: Dict[str, Any], l1lll11l11111lllIl1l1: List[llllll1l11lll11lIl1l1]) -> Any:  # type: ignore
        with ll1111l1ll1lll1lIl1l1():
            assert llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1
            l11l1ll1l11l1111Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1.l11lll11ll1l1l1lIl1l1.ll11l1111ll11l11Il1l1()
            l11l1ll1l11l1111Il1l1.l11111lll11lll1lIl1l1()

            l11ll11ll11l11l1Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l1lll1l1111l1ll1Il1l1.l11l1l11ll1l11l1Il1l1(l11l1ll1l11l1111Il1l1.l11111l1l1ll11l1Il1l1, l11l1ll1l11l1111Il1l1.ll1l1l111ll1ll11Il1l1.l1l1l11ll11lll1lIl1l1())
            assert l11ll11ll11l11l1Il1l1
            lll11l1ll1l1ll1lIl1l1 = l111l1l1ll1111llIl1l1.l11llll11111lll1Il1l1()

            for l1llll1ll1lll11lIl1l1 in l1lll11l11111lllIl1l1:
                l1llll1ll1lll11lIl1l1.llll11111l1ll11lIl1l1()

            for l1llll1ll1lll11lIl1l1 in l1lll11l11111lllIl1l1:
                l1llll1ll1lll11lIl1l1.l111l111l1111ll1Il1l1()


        l11111l11lll1l11Il1l1 = l11ll11ll11l11l1Il1l1(*l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1);        l11l1ll1l11l1111Il1l1.ll1111l1ll11llllIl1l1.additional_info.pydev_step_stop = lll11l1ll1l1ll1lIl1l1  # type: ignore

        return l11111l11lll1l11Il1l1

    @classmethod
    async def lllllllllll111llIl1l1(l111l1l1ll1111llIl1l1, l111l1l1ll11ll1lIl1l1: List[Any], ll1l1ll1lll1ll1lIl1l1: Dict[str, Any], l1lll11l11111lllIl1l1: List[lll11l1l11l11l1lIl1l1]) -> Any:  # type: ignore
        with ll1111l1ll1lll1lIl1l1():
            assert llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1
            l11l1ll1l11l1111Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1.l11lll11ll1l1l1lIl1l1.ll11l1111ll11l11Il1l1()
            l11l1ll1l11l1111Il1l1.l11111lll11lll1lIl1l1()

            l11ll11ll11l11l1Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l1lll1l1111l1ll1Il1l1.l11l1l11ll1l11l1Il1l1(l11l1ll1l11l1111Il1l1.l11111l1l1ll11l1Il1l1, l11l1ll1l11l1111Il1l1.ll1l1l111ll1ll11Il1l1.l1l1l11ll11lll1lIl1l1())
            assert l11ll11ll11l11l1Il1l1
            lll11l1ll1l1ll1lIl1l1 = l111l1l1ll1111llIl1l1.l11llll11111lll1Il1l1()

            for l1llll1ll1lll11lIl1l1 in l1lll11l11111lllIl1l1:
                await l1llll1ll1lll11lIl1l1.llll11111l1ll11lIl1l1()

            for l1llll1ll1lll11lIl1l1 in l1lll11l11111lllIl1l1:
                await l1llll1ll1lll11lIl1l1.l111l111l1111ll1Il1l1()


        l11111l11lll1l11Il1l1 = await l11ll11ll11l11l1Il1l1(*l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1);        l11l1ll1l11l1111Il1l1.ll1111l1ll11llllIl1l1.additional_info.pydev_step_stop = lll11l1ll1l1ll1lIl1l1  # type: ignore

        return l11111l11lll1l11Il1l1


class ll1l1111l1111l1lIl1l1(l1lll1l11llll1l1Il1l1):
    @classmethod
    def ll11l1llll1lll11Il1l1(l111l1l1ll1111llIl1l1) -> Optional[ModuleType]:  # type: ignore
        with ll1111l1ll1lll1lIl1l1():
            assert llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1
            l11l1ll1l11l1111Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.l11ll1ll111l1l11Il1l1.l11lll11ll1l1l1lIl1l1.ll11l1111ll11l11Il1l1()

            l111llll1ll1l11lIl1l1 = Path(l11l1ll1l11l1111Il1l1.l1111ll1ll1ll11lIl1l1.f_globals['__spec__'].origin).absolute()
            ll1ll1l1l11ll11lIl1l1 = l11l1ll1l11l1111Il1l1.l1111ll1ll1ll11lIl1l1.f_globals['__name__']
            l11l1ll1l11l1111Il1l1.l11111lll11lll1lIl1l1()
            l1l1l1l1l1llll11Il1l1 = llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.ll1l1l1lllll1l11Il1l1.lll1l1l1l1ll111lIl1l1(l111llll1ll1l11lIl1l1)

            if ( not l1l1l1l1l1llll11Il1l1):
                lll1l11ll11ll11lIl1l1.ll1lll11l1ll1111Il1l1('Could not retrieve src.', l111l1l11ll1llllIl1l1={'file': l1llllll11lllll1Il1l1.lllll1l1l111lll1Il1l1(l111llll1ll1l11lIl1l1), 
'fullname': l1llllll11lllll1Il1l1.ll1ll1l1l11ll11lIl1l1(ll1ll1l1l11ll11lIl1l1)})

            assert l1l1l1l1l1llll11Il1l1

        try:
            l1l1l1l1l1llll11Il1l1.ll11lllll11lll1lIl1l1()
            l1l1l1l1l1llll11Il1l1.ll1lllllllll1111Il1l1(ll111l1111l11l11Il1l1=False)
            l1l1l1l1l1llll11Il1l1.l11111l11ll1l1llIl1l1(ll111l1111l11l11Il1l1=False)
        except l1l1l1lll1l1lll1Il1l1 as l1lll11llll1111lIl1l1:
            l11l1ll1l11l1111Il1l1.llll1l1lll11ll11Il1l1(l1lll11llll1111lIl1l1)
            return None

        import importlib.util

        l11l1lllll1llll1Il1l1 = l11l1ll1l11l1111Il1l1.l1111ll1ll1ll11lIl1l1.f_locals['__spec__']
        lll1ll1lll111ll1Il1l1 = importlib.util.module_from_spec(l11l1lllll1llll1Il1l1)

        l1l1l1l1l1llll11Il1l1.l1lll1l1llll1111Il1l1(lll1ll1lll111ll1Il1l1)
        return lll1ll1lll111ll1Il1l1


l1l1ll11lll111l1Il1l1.ll111l1ll1llll1lIl1l1(l1111ll1llllll11Il1l1.ll1l1l1l1111l111Il1l1, l1111l1111l11111Il1l1.ll11l1llll1lll11Il1l1)
l1l1ll11lll111l1Il1l1.ll111l1ll1llll1lIl1l1(l1111ll1llllll11Il1l1.ll1llll11l11l1llIl1l1, l1111l1111l11111Il1l1.lllllllllll111llIl1l1)
l1l1ll11lll111l1Il1l1.ll111l1ll1llll1lIl1l1(l1111ll1llllll11Il1l1.l111lll1llllll1lIl1l1, ll1l1111l1111l1lIl1l1.ll11l1llll1lll11Il1l1)
