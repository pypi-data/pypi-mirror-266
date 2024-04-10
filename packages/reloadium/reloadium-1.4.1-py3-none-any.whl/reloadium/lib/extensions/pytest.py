import dataclasses
import types
from reloadium.lib.extensions.extension import Extension
from reloadium.fast.extensions.pytest import Loader

from dataclasses import dataclass

__RELOADIUM__ = True

import types


@dataclass(repr=False, frozen=False)
class Pytest(Extension):
    NAME = "Pytest"

    def enable(self, module: types.ModuleType) -> None:
        if self.is_import(module, "pytest"):
            self._inject_loader(module)

    def _inject_loader(self, module: types.ModuleType) -> None:
        import _pytest.assertion.rewrite
        _pytest.assertion.rewrite.AssertionRewritingHook = Loader  # type: ignore

