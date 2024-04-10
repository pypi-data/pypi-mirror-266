import asyncio
from contextlib import contextmanager
import os
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, List, Optional, Tuple, Type

from reloadium.corium.lll1l1111111l1llIl1l1 import llll1ll1ll1l1l11Il1l1
from reloadium.corium.lll11l11l1ll1l11Il1l1 import ll1ll1l1111l1l1lIl1l1
from reloadium.corium.llllllllll1lll11Il1l1.l1ll11l1ll1lll1lIl1l1 import l111llll1111ll11Il1l1
from reloadium.lib.environ import env
from reloadium.corium.ll1llllll11l1ll1Il1l1 import ll1111l1ll1lll1lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import ll111ll11llllll1Il1l1, l111111ll111111lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.ll111ll1111lll11Il1l1 import ll1ll111111l1111Il1l1
from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111ll1ll1l11llIl1l1, l1111l1l1ll11111Il1l1, l1111ll1ll1l1l11Il1l1, ll1l1ll11111l1llIl1l1, l1l1111l1ll11ll1Il1l1
from reloadium.corium.l11ll11l1l1llll1Il1l1 import llllll1l11lll11lIl1l1, lll11l1l11l11l1lIl1l1
from reloadium.corium.l111ll11l11l111lIl1l1 import ll1l1llll11l11llIl1l1
from reloadium.corium.llllllllll1lll11Il1l1 import l11l11l11l11l111Il1l1
from dataclasses import dataclass, field


if (TYPE_CHECKING):
    from django.db import transaction
    from django.db.transaction import Atomic


__RELOADIUM__ = True


@dataclass(**l1l1111l1ll11ll1Il1l1)
class l11ll1ll1l1l11llIl1l1(ll1l1ll11111l1llIl1l1):
    llllll11lll1ll11Il1l1 = 'Field'

    @classmethod
    def ll1l1lllll1l1l1lIl1l1(l111l1l1ll1111llIl1l1, l11ll111l1l1ll1lIl1l1: ll1l1llll11l11llIl1l1.ll11l1ll1l11l11lIl1l1, l1111ll1ll1ll11lIl1l1: Any, l1lll1lllllll11lIl1l1: l1111l1l1ll11111Il1l1) -> bool:
        from django.db.models.fields import Field

        if ((hasattr(l1111ll1ll1ll11lIl1l1, 'field') and isinstance(l1111ll1ll1ll11lIl1l1.field, Field))):
            return True

        return False

    def l11l111ll111l1l1Il1l1(l1ll11lllllll11lIl1l1, l1l11lll11l1111lIl1l1: l1111ll1ll1l1l11Il1l1) -> bool:
        return True

    @classmethod
    def l111l111l1llll1lIl1l1(l111l1l1ll1111llIl1l1) -> int:
        return 200


@dataclass(repr=False)
class l1ll1ll1111111l1Il1l1(ll111ll11llllll1Il1l1):
    lll1llll111l11llIl1l1: "Atomic" = field(init=False)

    l11l1l11l1l1ll11Il1l1: bool = field(init=False, default=False)

    def ll11lllll11ll1llIl1l1(l1ll11lllllll11lIl1l1) -> None:
        super().ll11lllll11ll1llIl1l1()
        from django.db import transaction

        l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1 = transaction.atomic()
        l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__enter__()

    def llll11111l1ll11lIl1l1(l1ll11lllllll11lIl1l1) -> None:
        super().llll11111l1ll11lIl1l1()
        if (l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1):
            return 

        l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1 = True
        from django.db import transaction

        transaction.set_rollback(True)
        l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__exit__(None, None, None)

    def l111l111l1111ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        super().l111l111l1111ll1Il1l1()

        if (l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1):
            return 

        l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1 = True
        l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__exit__(None, None, None)

    def __repr__(l1ll11lllllll11lIl1l1) -> str:
        return 'DbMemento'


@dataclass(repr=False)
class l111l1ll1ll11l11Il1l1(l111111ll111111lIl1l1):
    lll1llll111l11llIl1l1: "Atomic" = field(init=False)

    l11l1l11l1l1ll11Il1l1: bool = field(init=False, default=False)

    async def ll11lllll11ll1llIl1l1(l1ll11lllllll11lIl1l1) -> None:
        await super().ll11lllll11ll1llIl1l1()
        from django.db import transaction
        from asgiref.sync import sync_to_async

        l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1 = transaction.atomic()


        with llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.ll1l1l1111l1lll1Il1l1.ll1111l1111ll1l1Il1l1(False):
            await sync_to_async(l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__enter__)()

    async def llll11111l1ll11lIl1l1(l1ll11lllllll11lIl1l1) -> None:
        from asgiref.sync import sync_to_async

        await super().llll11111l1ll11lIl1l1()
        if (l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1):
            return 

        l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1 = True
        from django.db import transaction

        def lll1l1lll11ll1l1Il1l1() -> None:
            transaction.set_rollback(True)
            l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__exit__(None, None, None)
        with llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.ll1l1l1111l1lll1Il1l1.ll1111l1111ll1l1Il1l1(False):
            await sync_to_async(lll1l1lll11ll1l1Il1l1)()

    async def l111l111l1111ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        from asgiref.sync import sync_to_async

        await super().l111l111l1111ll1Il1l1()

        if (l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1):
            return 

        l1ll11lllllll11lIl1l1.l11l1l11l1l1ll11Il1l1 = True
        with llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.ll1l1l1111l1lll1Il1l1.ll1111l1111ll1l1Il1l1(False):
            await sync_to_async(l1ll11lllllll11lIl1l1.lll1llll111l11llIl1l1.__exit__)(None, None, None)

    def __repr__(l1ll11lllllll11lIl1l1) -> str:
        return 'AsyncDbMemento'


@dataclass
class l11l1l1111llll11Il1l1(ll1ll111111l1111Il1l1):
    ll1111ll11lllll1Il1l1 = 'Django'

    lll11l11lll1111lIl1l1: Optional[int] = field(init=False)
    l1l111l111lll11lIl1l1: Optional[Callable[..., Any]] = field(init=False, default=None)

    l1111l1ll11ll1llIl1l1: Any = field(init=False, default=None)
    l11ll111llll1l1lIl1l1: Any = field(init=False, default=None)
    ll11llll11111ll1Il1l1: Any = field(init=False, default=None)

    l11lll111l11ll11Il1l1 = True

    def __post_init__(l1ll11lllllll11lIl1l1) -> None:
        super().__post_init__()
        l1ll11lllllll11lIl1l1.lll11l11lll1111lIl1l1 = None

    def lllllll1l111llllIl1l1(l1ll11lllllll11lIl1l1) -> List[Type[l1111ll1ll1l1l11Il1l1]]:
        return [l11ll1ll1l1l11llIl1l1]

    def l1l1ll1lll111l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        super().l1l1ll1lll111l11Il1l1()
        if ('runserver' in sys.argv):
            sys.argv.append('--noreload')

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, lll1ll1lll111ll1Il1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(lll1ll1lll111ll1Il1l1, 'django.core.management.commands.runserver')):
            l1ll11lllllll11lIl1l1.l1ll1ll111ll111lIl1l1()
            if ( not l1ll11lllllll11lIl1l1.ll1l1ll11111ll1lIl1l1):
                l1ll11lllllll11lIl1l1.l11111l111ll1lllIl1l1()

    def lllllll1111lllllIl1l1(l1ll11lllllll11lIl1l1) -> None:
        import django.core.management.commands.runserver

        django.core.management.commands.runserver.Command.handle = l1ll11lllllll11lIl1l1.l1111l1ll11ll1llIl1l1
        django.core.management.commands.runserver.Command.get_handler = l1ll11lllllll11lIl1l1.ll11llll11111ll1Il1l1
        django.core.handlers.base.BaseHandler.get_response = l1ll11lllllll11lIl1l1.l11ll111llll1l1lIl1l1

    def llllll1lll1ll11lIl1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str, l111ll1l1l111ll1Il1l1: bool) -> Optional["llllll1l11lll11lIl1l1"]:
        if (l1ll11lllllll11lIl1l1.ll1l1ll11111ll1lIl1l1):
            return None

        if ( not os.environ.get('DJANGO_SETTINGS_MODULE')):
            return None

        if (l111ll1l1l111ll1Il1l1):
            return None
        else:
            l11111l11lll1l11Il1l1 = l1ll1ll1111111l1Il1l1(l1ll1lll1lll111lIl1l1=l1ll1lll1lll111lIl1l1, lll1l1l1l11l111lIl1l1=l1ll11lllllll11lIl1l1)
            l11111l11lll1l11Il1l1.ll11lllll11ll1llIl1l1()

        return l11111l11lll1l11Il1l1

    async def l1llll11l1ll11l1Il1l1(l1ll11lllllll11lIl1l1, l1ll1lll1lll111lIl1l1: str) -> Optional["lll11l1l11l11l1lIl1l1"]:
        if (l1ll11lllllll11lIl1l1.ll1l1ll11111ll1lIl1l1):
            return None

        if ( not os.environ.get('DJANGO_SETTINGS_MODULE')):
            return None

        l11111l11lll1l11Il1l1 = l111l1ll1ll11l11Il1l1(l1ll1lll1lll111lIl1l1=l1ll1lll1lll111lIl1l1, lll1l1l1l11l111lIl1l1=l1ll11lllllll11lIl1l1)
        await l11111l11lll1l11Il1l1.ll11lllll11ll1llIl1l1()
        return l11111l11lll1l11Il1l1

    def l1ll1ll111ll111lIl1l1(l1ll11lllllll11lIl1l1) -> None:
        import django.core.management.commands.runserver

        l1ll11lllllll11lIl1l1.l1111l1ll11ll1llIl1l1 = django.core.management.commands.runserver.Command.handle

        def lll1l1l11ll11l11Il1l1(*l111l1l1ll11ll1lIl1l1: Any, **l11111l1lll1l111Il1l1: Any) -> Any:
            with ll1111l1ll1lll1lIl1l1():
                l111l1lll11111l1Il1l1 = l11111l1lll1l111Il1l1.get('addrport')
                if ( not l111l1lll11111l1Il1l1):
                    l111l1lll11111l1Il1l1 = django.core.management.commands.runserver.Command.default_port

                l111l1lll11111l1Il1l1 = l111l1lll11111l1Il1l1.split(':')[ - 1]
                l111l1lll11111l1Il1l1 = int(l111l1lll11111l1Il1l1)
                l1ll11lllllll11lIl1l1.lll11l11lll1111lIl1l1 = l111l1lll11111l1Il1l1

            return l1ll11lllllll11lIl1l1.l1111l1ll11ll1llIl1l1(*l111l1l1ll11ll1lIl1l1, **l11111l1lll1l111Il1l1)

        l111llll1111ll11Il1l1.l1ll11l1ll1lll1lIl1l1(django.core.management.commands.runserver.Command, 'handle', lll1l1l11ll11l11Il1l1)

    def l11111l111ll1lllIl1l1(l1ll11lllllll11lIl1l1) -> None:
        import django.core.management.commands.runserver

        l1ll11lllllll11lIl1l1.ll11llll11111ll1Il1l1 = django.core.management.commands.runserver.Command.get_handler

        def lll1l1l11ll11l11Il1l1(*l111l1l1ll11ll1lIl1l1: Any, **l11111l1lll1l111Il1l1: Any) -> Any:
            with ll1111l1ll1lll1lIl1l1():
                assert l1ll11lllllll11lIl1l1.lll11l11lll1111lIl1l1
                l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1 = l1ll11lllllll11lIl1l1.ll111lll111l1lllIl1l1(l1ll11lllllll11lIl1l1.lll11l11lll1111lIl1l1)
                if (env.page_reload_on_start):
                    l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l11llllllll1l11lIl1l1(2.0)

            return l1ll11lllllll11lIl1l1.ll11llll11111ll1Il1l1(*l111l1l1ll11ll1lIl1l1, **l11111l1lll1l111Il1l1)

        l111llll1111ll11Il1l1.l1ll11l1ll1lll1lIl1l1(django.core.management.commands.runserver.Command, 'get_handler', lll1l1l11ll11l11Il1l1)

    def l1ll1l1l1lll1ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        super().l1ll1l1l1lll1ll1Il1l1()

        import django.core.handlers.base

        l1ll11lllllll11lIl1l1.l11ll111llll1l1lIl1l1 = django.core.handlers.base.BaseHandler.get_response

        def lll1l1l11ll11l11Il1l1(ll1lllll11l1l111Il1l1: Any, lll111l1lllll1l1Il1l1: Any) -> Any:
            lll11l11ll1ll11lIl1l1 = l1ll11lllllll11lIl1l1.l11ll111llll1l1lIl1l1(ll1lllll11l1l111Il1l1, lll111l1lllll1l1Il1l1)

            if ( not l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
                return lll11l11ll1ll11lIl1l1

            lll11l11lll11lllIl1l1 = lll11l11ll1ll11lIl1l1.get('content-type')

            if (( not lll11l11lll11lllIl1l1 or 'text/html' not in lll11l11lll11lllIl1l1)):
                return lll11l11ll1ll11lIl1l1

            l111lllllll11l11Il1l1 = lll11l11ll1ll11lIl1l1.content

            if (isinstance(l111lllllll11l11Il1l1, bytes)):
                l111lllllll11l11Il1l1 = l111lllllll11l11Il1l1.decode('utf-8')

            l11l1lllllll1l11Il1l1 = l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l1111ll11l1l11l1Il1l1(l111lllllll11l11Il1l1)

            lll11l11ll1ll11lIl1l1.content = l11l1lllllll1l11Il1l1.encode('utf-8')
            lll11l11ll1ll11lIl1l1['content-length'] = str(len(lll11l11ll1ll11lIl1l1.content)).encode('ascii')
            return lll11l11ll1ll11lIl1l1

        django.core.handlers.base.BaseHandler.get_response = lll1l1l11ll11l11Il1l1  # type: ignore

    def lll1ll111l1ll1llIl1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        super().lll1ll111l1ll1llIl1l1(lllll1l1l111lll1Il1l1)

        from django.apps.registry import Apps

        l1ll11lllllll11lIl1l1.l1l111l111lll11lIl1l1 = Apps.register_model

        def l111l1lll1l1l1llIl1l1(*l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> Any:
            pass

        Apps.register_model = l111l1lll1l1l1llIl1l1

    def l11ll11ll1ll11l1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path, l11111l11ll1l111Il1l1: List[l1111ll1ll1l11llIl1l1]) -> None:
        super().l11ll11ll1ll11l1Il1l1(lllll1l1l111lll1Il1l1, l11111l11ll1l111Il1l1)

        if ( not l1ll11lllllll11lIl1l1.l1l111l111lll11lIl1l1):
            return 

        from django.apps.registry import Apps

        Apps.register_model = l1ll11lllllll11lIl1l1.l1l111l111lll11lIl1l1
