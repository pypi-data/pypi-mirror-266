from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, List

from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1
from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111ll1ll1l11llIl1l1
from reloadium.corium.llllllllll1lll11Il1l1 import l11l11l11l11l111Il1l1
from dataclasses import dataclass, field


__RELOADIUM__ = True


@dataclass
class ll11lll1l11l1lllIl1l1(l11111lll111ll11Il1l1):
    ll1111ll11lllll1Il1l1 = 'PyGame'

    l11lll111l11ll11Il1l1 = True

    l1llll1l1l1lllllIl1l1: bool = field(init=False, default=False)

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, l111ll11lll1l1llIl1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(l111ll11lll1l1llIl1l1, 'pygame.base')):
            l1ll11lllllll11lIl1l1.l1lllll1llll1l11Il1l1()

    def l1lllll1llll1l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        import pygame.display

        lll11111l11l1lllIl1l1 = pygame.display.update

        def l1l111111lll1111Il1l1(*l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> None:
            if (l1ll11lllllll11lIl1l1.l1llll1l1l1lllllIl1l1):
                l11l11l11l11l111Il1l1.l11lll1l1l1ll111Il1l1(0.1)
                return None
            else:
                return lll11111l11l1lllIl1l1(*l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1)

        pygame.display.update = l1l111111lll1111Il1l1

    def lll1ll111l1ll1llIl1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        l1ll11lllllll11lIl1l1.l1llll1l1l1lllllIl1l1 = True

    def l11ll11ll1ll11l1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path, l11111l11ll1l111Il1l1: List[l1111ll1ll1l11llIl1l1]) -> None:
        l1ll11lllllll11lIl1l1.l1llll1l1l1lllllIl1l1 = False

    def l1l1l1ll11ll1ll1Il1l1(l1ll11lllllll11lIl1l1, llll1lll11l111llIl1l1: Exception) -> None:
        l1ll11lllllll11lIl1l1.l1llll1l1l1lllllIl1l1 = False
