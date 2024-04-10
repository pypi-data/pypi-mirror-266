from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type, cast
import types

from reloadium.corium.ll11l11ll11l111lIl1l1 import ll11l11ll11l111lIl1l1
from reloadium.corium.llllllllll1lll11Il1l1.l1ll11l1ll1lll1lIl1l1 import l111llll1111ll11Il1l1
from reloadium.lib.environ import env
from reloadium.corium.ll1llllll11l1ll1Il1l1 import ll1111l1ll1lll1lIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.ll111ll1111lll11Il1l1 import ll1ll111111l1111Il1l1
from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111l1l1ll11111Il1l1, l1111ll1ll1l1l11Il1l1, ll1l1ll11111l1llIl1l1, l1l1111l1ll11ll1Il1l1
from reloadium.corium.l111ll11l11l111lIl1l1 import ll1l1llll11l11llIl1l1
from dataclasses import dataclass, field

__RELOADIUM__ = True

lll1l11ll11ll11lIl1l1 = ll11l11ll11l111lIl1l1.ll1l11ll1111l111Il1l1(__name__)


@dataclass(**l1l1111l1ll11ll1Il1l1)
class l1l1lll1llll11l1Il1l1(ll1l1ll11111l1llIl1l1):
    llllll11lll1ll11Il1l1 = 'FlaskApp'

    @classmethod
    def ll1l1lllll1l1l1lIl1l1(l111l1l1ll1111llIl1l1, l11ll111l1l1ll1lIl1l1: ll1l1llll11l11llIl1l1.ll11l1ll1l11l11lIl1l1, l1111ll1ll1ll11lIl1l1: Any, l1lll1lllllll11lIl1l1: l1111l1l1ll11111Il1l1) -> bool:
        import flask

        if (isinstance(l1111ll1ll1ll11lIl1l1, flask.Flask)):
            return True

        return False

    def l1l1l11l11ll11l1Il1l1(l1ll11lllllll11lIl1l1) -> bool:
        return True

    @classmethod
    def l111l111l1llll1lIl1l1(l111l1l1ll1111llIl1l1) -> int:
        return (super().l111l111l1llll1lIl1l1() + 10)


@dataclass(**l1l1111l1ll11ll1Il1l1)
class ll111l11111l1111Il1l1(ll1l1ll11111l1llIl1l1):
    llllll11lll1ll11Il1l1 = 'Request'

    @classmethod
    def ll1l1lllll1l1l1lIl1l1(l111l1l1ll1111llIl1l1, l11ll111l1l1ll1lIl1l1: ll1l1llll11l11llIl1l1.ll11l1ll1l11l11lIl1l1, l1111ll1ll1ll11lIl1l1: Any, l1lll1lllllll11lIl1l1: l1111l1l1ll11111Il1l1) -> bool:
        if (repr(l1111ll1ll1ll11lIl1l1) == '<LocalProxy unbound>'):
            return True

        return False

    def l1l1l11l11ll11l1Il1l1(l1ll11lllllll11lIl1l1) -> bool:
        return True

    @classmethod
    def l111l111l1llll1lIl1l1(l111l1l1ll1111llIl1l1) -> int:

        return int(10000000000.0)


@dataclass
class l1l1lll1l1l1l1llIl1l1(ll1ll111111l1111Il1l1):
    ll1111ll11lllll1Il1l1 = 'Flask'

    @contextmanager
    def l11l111ll1l1l111Il1l1(l1ll11lllllll11lIl1l1) -> Generator[None, None, None]:




        from flask import Flask as FlaskLib 

        def ll1l11ll1lllllllIl1l1(*l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> Any:
            def l11111ll1l111lllIl1l1(l11ll1l11l1ll1l1Il1l1: Any) -> Any:
                return l11ll1l11l1ll1l1Il1l1

            return l11111ll1l111lllIl1l1

        ll1llllll1l1l1l1Il1l1 = FlaskLib.route
        FlaskLib.route = ll1l11ll1lllllllIl1l1  # type: ignore

        try:
            yield 
        finally:
            FlaskLib.route = ll1llllll1l1l1l1Il1l1  # type: ignore

    def lllllll1l111llllIl1l1(l1ll11lllllll11lIl1l1) -> List[Type[l1111ll1ll1l1l11Il1l1]]:
        return [l1l1lll1llll11l1Il1l1, ll111l11111l1111Il1l1]

    def ll11lllllll11l11Il1l1(l1ll11lllllll11lIl1l1, l111ll11lll1l1llIl1l1: types.ModuleType) -> None:
        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(l111ll11lll1l1llIl1l1, 'flask.app')):
            l1ll11lllllll11lIl1l1.llll1l1l1l11ll11Il1l1()
            l1ll11lllllll11lIl1l1.l111l1l11111ll11Il1l1()
            l1ll11lllllll11lIl1l1.l1111lll11l1ll11Il1l1()

        if (l1ll11lllllll11lIl1l1.ll1l1l11llllll11Il1l1(l111ll11lll1l1llIl1l1, 'flask.cli')):
            l1ll11lllllll11lIl1l1.l11111l1111ll111Il1l1()


    def l11ll11l1llll1l1Il1l1(hostname: Any, port: Any, application: Any, use_reloader: Any = False, use_debugger: Any = False, use_evalex: Any = True, extra_files: Any = None, exclude_patterns: Any = None, reloader_interval: Any = 1, reloader_type: Any = 'auto', threaded: Any = False, processes: Any = 1, request_handler: Any = None, static_files: Any = None, passthrough_errors: Any = False, ssl_context: Any = None) -> Any:
        from typing import cast
        __rw_plugin__ = cast('Flask', globals().get('__rw_plugin__'))

        __rw_plugin__.ll1l1l11l1l111l1Il1l1 = __rw_plugin__.ll111lll111l1lllIl1l1(port)  # type: ignore
        if (__rw_globals__['env'].page_reload_on_start):  # type: ignore
            __rw_plugin__.ll1l1l11l1l111l1Il1l1.l11llllllll1l11lIl1l1(1.0)  # type: ignore
        __rw_orig__(hostname, port, application, use_reloader, use_debugger, use_evalex, extra_files, exclude_patterns, reloader_interval, reloader_type, threaded, processes, request_handler, static_files, passthrough_errors, ssl_context)  # type: ignore













    def llll1l1l1l11ll11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        try:
            import werkzeug.serving
            import flask.cli
        except ImportError:
            return 

        l111llll1111ll11Il1l1.l11111l1l111llllIl1l1(werkzeug.serving.run_simple, l1ll11lllllll11lIl1l1.l11ll11l1llll1l1Il1l1, ll11lllll111111lIl1l1={'__rw_plugin__': l1ll11lllllll11lIl1l1})


    def l1111lll11l1ll11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        try:
            import flask
        except ImportError:
            return 

        ll11l1ll1l1111l1Il1l1 = flask.app.Flask.__init__

        def lll1l1l11ll11l11Il1l1(l1lllllll11l11llIl1l1: Any, *l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> Any:
            ll11l1ll1l1111l1Il1l1(l1lllllll11l11llIl1l1, *l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1)
            with ll1111l1ll1lll1lIl1l1():
                l1lllllll11l11llIl1l1.config['TEMPLATES_AUTO_RELOAD'] = True

        l111llll1111ll11Il1l1.l1ll11l1ll1lll1lIl1l1(flask.app.Flask, '__init__', lll1l1l11ll11l11Il1l1)

    def l111l1l11111ll11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        try:
            import waitress  # type: ignore
        except ImportError:
            return 

        ll11l1ll1l1111l1Il1l1 = waitress.serve



        def lll1l1l11ll11l11Il1l1(*l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> Any:
            with ll1111l1ll1lll1lIl1l1():
                l111l1lll11111l1Il1l1 = ll1l1ll1lll1ll1lIl1l1.get('port')
                if ( not l111l1lll11111l1Il1l1):
                    l111l1lll11111l1Il1l1 = int(l111l1l1ll11ll1lIl1l1[1])

                l111l1lll11111l1Il1l1 = int(l111l1lll11111l1Il1l1)

                l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1 = l1ll11lllllll11lIl1l1.ll111lll111l1lllIl1l1(l111l1lll11111l1Il1l1)
                if (env.page_reload_on_start):
                    l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l11llllllll1l11lIl1l1(1.0)

            ll11l1ll1l1111l1Il1l1(*l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1)

        l111llll1111ll11Il1l1.l1ll11l1ll1lll1lIl1l1(waitress, 'serve', lll1l1l11ll11l11Il1l1)

    def l11111l1111ll111Il1l1(l1ll11lllllll11lIl1l1) -> None:
        try:
            from flask import cli
        except ImportError:
            return 

        llll1llll1l11lllIl1l1 = Path(cli.__file__).read_text(encoding='utf-8')
        llll1llll1l11lllIl1l1 = llll1llll1l11lllIl1l1.replace('.tb_next', '.tb_next.tb_next')

        exec(llll1llll1l11lllIl1l1, cli.__dict__)

    def l1ll1l1l1lll1ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        super().l1ll1l1l1lll1ll1Il1l1()
        import flask.app

        ll11l1ll1l1111l1Il1l1 = flask.app.Flask.dispatch_request

        def lll1l1l11ll11l11Il1l1(*l111l1l1ll11ll1lIl1l1: Any, **ll1l1ll1lll1ll1lIl1l1: Any) -> Any:
            lll11l11ll1ll11lIl1l1 = ll11l1ll1l1111l1Il1l1(*l111l1l1ll11ll1lIl1l1, **ll1l1ll1lll1ll1lIl1l1)

            if ( not l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
                return lll11l11ll1ll11lIl1l1

            if (isinstance(lll11l11ll1ll11lIl1l1, str)):
                l11111l11lll1l11Il1l1 = l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l1111ll11l1l11l1Il1l1(lll11l11ll1ll11lIl1l1)
                return l11111l11lll1l11Il1l1
            elif ((isinstance(lll11l11ll1ll11lIl1l1, flask.app.Response) and 'text/html' in lll11l11ll1ll11lIl1l1.content_type)):
                lll11l11ll1ll11lIl1l1.data = l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l1111ll11l1l11l1Il1l1(lll11l11ll1ll11lIl1l1.data.decode('utf-8')).encode('utf-8')
                return lll11l11ll1ll11lIl1l1
            else:
                return lll11l11ll1ll11lIl1l1

        flask.app.Flask.dispatch_request = lll1l1l11ll11l11Il1l1  # type: ignore
