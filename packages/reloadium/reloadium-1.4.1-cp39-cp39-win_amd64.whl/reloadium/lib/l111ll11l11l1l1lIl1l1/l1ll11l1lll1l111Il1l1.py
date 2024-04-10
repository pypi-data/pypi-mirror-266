import dataclasses
import types
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1
from reloadium.fast.l111ll11l11l1l1lIl1l1.l1ll11l1lll1l111Il1l1 import lllll1l1l1ll1l1lIl1l1

from dataclasses import dataclass

__RELOADIUM__ = True

import types


@dataclass(repr=False, frozen=False)
class lll1111l11ll1l1lIl1l1(l11111lll111ll11Il1l1):
    ll1111ll11lllll1Il1l1 = 'Pytest'

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'pytest')):
            l1ll11lllllll11lIl1l1.l1l11ll111l1l111Il1l1(lll1ll1lll111ll1Il1l1)

    def l1l11ll111l1l111Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        import _pytest.assertion.rewrite
        _pytest.assertion.rewrite.AssertionRewritingHook = lllll1l1l1ll1l1lIl1l1  # type: ignore

