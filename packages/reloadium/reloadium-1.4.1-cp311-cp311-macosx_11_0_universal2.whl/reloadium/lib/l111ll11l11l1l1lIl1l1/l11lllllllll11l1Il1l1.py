import re
from contextlib import contextmanager
import os
import sys
import types
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from reloadium.corium.ll1llllll11l1ll1Il1l1 import ll1111l1ll1lll1lIl1l1
from reloadium.corium.llllllllll1lll11Il1l1.l1ll11l1ll1lll1lIl1l1 import l111llll1111ll11Il1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1, ll111ll11llllll1Il1l1
from reloadium.corium.l11ll11l1l1llll1Il1l1 import llllll1l11lll11lIl1l1
from reloadium.corium.llllllllll1lll11Il1l1 import l11l11l11l11l111Il1l1
from dataclasses import dataclass, field

if (TYPE_CHECKING):
    from sqlalchemy.engine.base import Engine, Transaction
    from sqlalchemy.orm.session import Session


__RELOADIUM__ = True


@dataclass(repr=False)
class l1ll1ll1111111l1Il1l1(ll111ll11llllll1Il1l1):
    lll1l1l1l11l111lIl1l1: "ll1ll11ll11l1l1lIl1l1"
    ll1ll1l111ll1111Il1l1: List["Transaction"] = field(init=False, default_factory=list)

    def ll11lllll11ll1llIl1l1(l1ll11lllllll11lIl1l1) -> None:
        from sqlalchemy.orm.session import _sessions

        super().ll11lllll11ll1llIl1l1()

        ll11l11lll1lllllIl1l1 = list(_sessions.values())

        for lll1lll1111l111lIl1l1 in ll11l11lll1lllllIl1l1:
            if ( not lll1lll1111l111lIl1l1.is_active):
                continue

            l11l1lll11l11111Il1l1 = lll1lll1111l111lIl1l1.begin_nested()
            l1ll11lllllll11lIl1l1.ll1ll1l111ll1111Il1l1.append(l11l1lll11l11111Il1l1)

    def __repr__(l1ll11lllllll11lIl1l1) -> str:
        return 'DbMemento'

    def llll11111l1ll11lIl1l1(l1ll11lllllll11lIl1l1) -> None:
        super().llll11111l1ll11lIl1l1()

        while l1ll11lllllll11lIl1l1.ll1ll1l111ll1111Il1l1:
            l11l1lll11l11111Il1l1 = l1ll11lllllll11lIl1l1.ll1ll1l111ll1111Il1l1.pop()
            if (l11l1lll11l11111Il1l1.is_active):
                try:
                    l11l1lll11l11111Il1l1.rollback()
                except :
                    pass

    def l111l111l1111ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        super().l111l111l1111ll1Il1l1()

        while l1ll11lllllll11lIl1l1.ll1ll1l111ll1111Il1l1:
            l11l1lll11l11111Il1l1 = l1ll11lllllll11lIl1l1.ll1ll1l111ll1111Il1l1.pop()
            if (l11l1lll11l11111Il1l1.is_active):
                try:
                    l11l1lll11l11111Il1l1.commit()
                except :
                    pass


@dataclass
class ll1ll11ll11l1l1lIl1l1(l11111lll111ll11Il1l1):
    ll1111ll11lllll1Il1l1 = 'Sqlalchemy'

    lll1l111llll111lIl1l1: List["Engine"] = field(init=False, default_factory=list)
    ll11l11lll1lllllIl1l1: Set["Session"] = field(init=False, default_factory=set)
    ll111ll11l1l11l1Il1l1: Tuple[int, ...] = field(init=False)

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'sqlalchemy')):
            l1ll11lllllll11lIl1l1.l11111111ll11ll1Il1l1(lll1ll1lll111ll1Il1l1)

        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'sqlalchemy.engine.base')):
            l1ll11lllllll11lIl1l1.ll11llll1111l11lIl1l1(lll1ll1lll111ll1Il1l1)

    def l11111111ll11ll1Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: Any) -> None:
        l111lllllll11l11Il1l1 = Path(lll1ll1lll111ll1Il1l1.__file__).read_text(encoding='utf-8')
        __version__ = re.findall('__version__\\s*?=\\s*?"(.*?)"', l111lllllll11l11Il1l1)[0]

        ll1l11111l1l1lllIl1l1 = [int(ll1l111l11ll11l1Il1l1) for ll1l111l11ll11l1Il1l1 in __version__.split('.')]
        l1ll11lllllll11lIl1l1.ll111ll11l1l11l1Il1l1 = tuple(ll1l11111l1l1lllIl1l1)

    def llllll1lll1ll11lIl1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str, l111ll1l1l111ll1Il1l1: bool) -> Optional["llllll1l11lll11lIl1l1"]:
        l11111l11lll1l11Il1l1 = l1ll1ll1111111l1Il1l1(l1ll1lll1lll111lIl1l1=l1ll1lll1lll111lIl1l1, lll1l1l1l11l111lIl1l1=l1ll11lllllll11lIl1l1)
        l11111l11lll1l11Il1l1.ll11lllll11ll1llIl1l1()
        return l11111l11lll1l11Il1l1

    def ll11llll1111l11lIl1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: Any) -> None:
        l11l111ll1111ll1Il1l1 = locals().copy()

        l11l111ll1111ll1Il1l1.update({'original': lll1ll1lll111ll1Il1l1.Engine.__init__, 'reloader_code': ll1111l1ll1lll1lIl1l1, 'engines': l1ll11lllllll11lIl1l1.lll1l111llll111lIl1l1})





        ll1l1lllll11l1llIl1l1 = dedent('\n            def patched(\n                    self2: Any,\n                    pool: Any,\n                    dialect: Any,\n                    url: Any,\n                    logging_name: Any = None,\n                    echo: Any = None,\n                    proxy: Any = None,\n                    execution_options: Any = None,\n                    hide_parameters: Any = None,\n            ) -> Any:\n                original(self2,\n                         pool,\n                         dialect,\n                         url,\n                         logging_name,\n                         echo,\n                         proxy,\n                         execution_options,\n                         hide_parameters\n                         )\n                with reloader_code():\n                    engines.append(self2)')
























        l111ll11l1ll111lIl1l1 = dedent('\n            def patched(\n                    self2: Any,\n                    pool: Any,\n                    dialect: Any,\n                    url: Any,\n                    logging_name: Any = None,\n                    echo: Any = None,\n                    query_cache_size: Any = 500,\n                    execution_options: Any = None,\n                    hide_parameters: Any = False,\n            ) -> Any:\n                original(self2,\n                         pool,\n                         dialect,\n                         url,\n                         logging_name,\n                         echo,\n                         query_cache_size,\n                         execution_options,\n                         hide_parameters)\n                with reloader_code():\n                    engines.append(self2)\n        ')
























        if (l1ll11lllllll11lIl1l1.ll111ll11l1l11l1Il1l1 <= (1, 3, 24, )):
            exec(ll1l1lllll11l1llIl1l1, {**globals(), **l11l111ll1111ll1Il1l1}, l11l111ll1111ll1Il1l1)
        else:
            exec(l111ll11l1ll111lIl1l1, {**globals(), **l11l111ll1111ll1Il1l1}, l11l111ll1111ll1Il1l1)

        l111llll1111ll11Il1l1.l1ll11l1ll1lll1lIl1l1(lll1ll1lll111ll1Il1l1.Engine, '__init__', l11l111ll1111ll1Il1l1['patched'])
