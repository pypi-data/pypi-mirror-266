from contextlib import contextmanager
from pathlib import Path
import types
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type, cast
import types

from reloadium.corium.loggium import loggium
from reloadium.corium.utils.patch import monkey_patcher
from reloadium.lib.environ import env
from reloadium.corium.exceptions import reloader_code
from reloadium.lib.extensions.server_extension import ServerExtension
from reloadium.corium.objects import Container, Object, Variable, obj_dc
from reloadium.corium.static_anal import symbols
from dataclasses import dataclass, field

__RELOADIUM__ = True

logger = loggium.factory(__name__)


@dataclass(**obj_dc)
class FlaskApp(Variable):
    TYPE_NAME = "FlaskApp"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        import flask

        if isinstance(py_obj, flask.Flask):
            return True

        return False

    def is_ignored(self) -> bool:
        return True

    @classmethod
    def get_rank(cls) -> int:
        return super().get_rank() + 10


@dataclass(**obj_dc)
class Request(Variable):
    TYPE_NAME = "Request"

    @classmethod
    def is_candidate(cls, sym: symbols.Symbol, py_obj: Any, potential_parent: Container) -> bool:
        if repr(py_obj) == "<LocalProxy unbound>":
            return True

        return False

    def is_ignored(self) -> bool:
        return True

    @classmethod
    def get_rank(cls) -> int:
        # has to be very hight priority since doing anything on flask.request raises an exception
        return int(1e10)


@dataclass
class Flask(ServerExtension):
    NAME = "Flask"

    @contextmanager
    def on_execute(self) -> Generator[None, None, None]:
        """
        Disable url registering when rewriting source.
        Changing view settings is not supported yet.
        """
        from flask import Flask as FlaskLib

        def empty_decorator(*args: Any, **kwargs: Any) -> Any:
            def decorator(f: Any) -> Any:
                return f

            return decorator

        tmp_route = FlaskLib.route
        FlaskLib.route = empty_decorator  # type: ignore

        try:
            yield
        finally:
            FlaskLib.route = tmp_route  # type: ignore

    def get_objects(self) -> List[Type[Object]]:
        return [FlaskApp, Request]

    def enable(self, py_module: types.ModuleType) -> None:
        if self.is_import(py_module, "flask.app"):
            self._patch_werkzeug()
            self._patch_waitress()
            self._patch_app_creation()

        if self.is_import(py_module, "flask.cli"):
            self._fix_locate_app()

    # fmt: off
    def patched_werkzeug_run_simple(hostname: Any, port: Any, application: Any, use_reloader: Any = False, use_debugger: Any = False, use_evalex: Any = True, extra_files: Any = None, exclude_patterns: Any = None, reloader_interval: Any = 1, reloader_type: Any = "auto", threaded: Any = False, processes: Any = 1, request_handler: Any = None, static_files: Any = None, passthrough_errors: Any = False, ssl_context: Any = None) -> Any:  # obf: ignore hostname, port, application, use_reloader, use_debugger, use_evalex, extra_files, exclude_patterns, reloader_interval, reloader_type, threaded, processes, request_handler, static_files, passthrough_errors, ssl_context
        from typing import cast
        __rw_plugin__ = cast("Flask", globals().get("__rw_plugin__"))

        __rw_plugin__.page_reloader = __rw_plugin__._page_reloader_factory(port)  # type: ignore
        if __rw_globals__["env"].page_reload_on_start:  # type: ignore
            __rw_plugin__.page_reloader.reload_with_delay(1.0)  # type: ignore
        __rw_orig__(hostname, port, application, use_reloader, use_debugger,  # type: ignore
                    use_evalex,
                    extra_files,
                    exclude_patterns,
                    reloader_interval,
                    reloader_type,
                    threaded,
                    processes,
                    request_handler,
                    static_files,
                    passthrough_errors,
                    ssl_context)
    # fmt: on

    def _patch_werkzeug(self) -> None:
        try:
            import werkzeug.serving
            import flask.cli
        except ImportError:
            return

        monkey_patcher.patch_code(werkzeug.serving.run_simple, self.patched_werkzeug_run_simple,
                                  extra_ctx={"__rw_plugin__": self})

    def _patch_app_creation(self) -> None:
        try:
            import flask
        except ImportError:
            return

        orig = flask.app.Flask.__init__

        def patched(self2: Any, *args: Any, **kwargs: Any) -> Any:
            orig(self2, *args, **kwargs)
            with reloader_code():
                self2.config["TEMPLATES_AUTO_RELOAD"] = True

        monkey_patcher.patch(flask.app.Flask, "__init__", patched)

    def _patch_waitress(self) -> None:
        try:
            import waitress  # type: ignore
        except ImportError:
            return

        orig = waitress.serve

        # Retrieve port

        def patched(*args: Any, **kwargs: Any) -> Any:
            with reloader_code():
                port = kwargs.get("port")
                if not port:
                    port = int(args[1])

                port = int(port)

                self.page_reloader = self._page_reloader_factory(port)
                if env.page_reload_on_start:
                    self.page_reloader.reload_with_delay(1.0)

            orig(*args, **kwargs)

        monkey_patcher.patch(waitress, "serve", patched)

    def _fix_locate_app(self) -> None:
        try:
            from flask import cli
        except ImportError:
            return

        src_code = Path(cli.__file__).read_text(encoding="utf-8")
        src_code = src_code.replace(".tb_next", ".tb_next.tb_next")

        exec(src_code, cli.__dict__)

    def _inject_reloader(self) -> None:
        super()._inject_reloader()
        import flask.app

        orig = flask.app.Flask.dispatch_request

        def patched(*args: Any, **kwargs: Any) -> Any:
            response = orig(*args, **kwargs)

            if not self.page_reloader:
                return response

            if isinstance(response, str):
                ret = self.page_reloader.inject_script(response)
                return ret
            elif isinstance(response, flask.app.Response) and "text/html" in response.content_type:
                response.data = self.page_reloader.inject_script(response.data.decode("utf-8")).encode("utf-8")
                return response
            else:
                return response

        flask.app.Flask.dispatch_request = patched  # type: ignore
