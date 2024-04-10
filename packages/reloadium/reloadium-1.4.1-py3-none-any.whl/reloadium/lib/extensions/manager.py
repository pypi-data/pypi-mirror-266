from contextlib import contextmanager
from pathlib import Path
import sys
import types
from threading import Timer, Thread
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Tuple, Type, Set

# keep this
import reloadium.lib.extensions.pytest_extension_guard
from reloadium.corium import audit, const, utils
from reloadium.corium.debug_environ import _env
from reloadium.corium.license import License, Features
from reloadium.corium.testing import TestType
from reloadium.corium.utils.thread import ReThread
from reloadium.lib.extensions.django import Django
from reloadium.lib.extensions.extension import Extension
from reloadium.lib.extensions.fastapi import FastApi
from reloadium.lib.extensions.flask import Flask
from reloadium.lib.extensions.graphene import Graphene
from reloadium.lib.extensions.numba import Numba
from reloadium.lib.extensions.pandas import Pandas
from reloadium.lib.extensions.pygame import PyGame
from reloadium.lib.extensions.pytest import Pytest
from reloadium.lib.extensions.sqlalchemy import Sqlalchemy
from reloadium.lib.extensions.multiprocessing import Multiprocessing
from reloadium.corium.loggium import loggium
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from reloadium.corium.core import Core
    from reloadium.corium.objects import Action


__RELOADIUM__ = True

logger = loggium.factory(__name__)


@dataclass
class ExtensionManager:
    core: "Core"

    extensions: List[Extension] = field(init=False, default_factory=list)

    already_imported: List[types.ModuleType] = field(init=False, default_factory=list)

    klasses: List[Type[Extension]] = field(
        init=False, default_factory=lambda: [Flask, Pandas, Django, Sqlalchemy, PyGame, Graphene, Pytest,
                                             Multiprocessing, FastApi, Numba]
    )

    forbidden_extensions: List[Type[Extension]] = field(init=False, default_factory=list)
    SHOW_FORBIDDEN_DIALOG_DELAY = 1 if _env().test_type in [TestType.E2E, TestType.CLUSTER] else 5

    def __post_init__(self) -> None:
        if _env().e2e.disable_pytest_extension:
            self.klasses.remove(Pytest)

        ReThread(target=self.show_forbidden_dialog, name="show-forbidden-dialog").start()

    def show_forbidden_dialog(self) -> None:
        utils.misc.sleep(self.SHOW_FORBIDDEN_DIALOG_DELAY)

        self.core.ide.wait_for_connected()

        if not self.forbidden_extensions:
            return

        extensions = [e.NAME for e in self.forbidden_extensions]
        self.core.license_mng.handle_forbidden(Features.EXTENSION_SUPPORT, const.msg.extensions_only_in_pro(extensions),
                                  msg_override="")

    def on_import(self, python_module_obj: types.ModuleType) -> None:
        for et in self.klasses.copy():
            if et.should_create(python_module_obj):
                if not et.ALLOWED_IN_FREE and self.core.license_mng.license.verify_extension_support([et.NAME]) is False:
                    self.forbidden_extensions.append(et)
                    self.klasses.remove(et)
                    continue
                self._create_extension(et)

        if python_module_obj in self.already_imported:
            return

        for p in self.extensions.copy():
            p.enable(python_module_obj)

        self.already_imported.append(python_module_obj)

    def _create_extension(self, et: Type[Extension]) -> None:
        ext = et(self, self.core.license_mng.license)

        self.core.user.run.send(audit.ExtensionUse(ext))
        ext.on_start()
        self.extensions.append(ext)

        if et in self.klasses:
            self.klasses.remove(et)

    @contextmanager
    def on_execute(self) -> Generator[None, None, None]:
        context_mans = [p.on_execute() for p in self.extensions.copy()]

        for c in context_mans:
            c.__enter__()

        yield

        for c in context_mans:
            c.__exit__(*sys.exc_info())

    def before_reload(self, path: Path) -> None:
        for p in self.extensions.copy():
            p.before_reload(path)

    def on_other_modify(self, path: Path) -> None:
        for p in self.extensions.copy():
            p.on_other_modify(path)

    def on_error(self, exc: Exception) -> None:
        for p in self.extensions.copy():
            p.on_error(exc)

    def after_reload(self, path: Path, actions: List["Action"]) -> None:
        for p in self.extensions.copy():
            p.after_reload(path, actions)

    def reset(self) -> None:
        self.extensions.clear()
