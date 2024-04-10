import sys

from reloadium.corium.llllllllll1lll11Il1l1.ll111ll1111l1l11Il1l1 import l1l1l1l111llll1lIl1l1

__RELOADIUM__ = True

l1l1l1l111llll1lIl1l1()


try:
    import _pytest.assertion.rewrite
except ImportError:
    class lll111ll11l11ll1Il1l1:
        pass

    _pytest = lambda :None  # type: ignore
    sys.modules['_pytest'] = _pytest

    _pytest.assertion = lambda :None  # type: ignore
    sys.modules['_pytest.assertion'] = _pytest.assertion

    _pytest.assertion.rewrite = lambda :None  # type: ignore
    _pytest.assertion.rewrite.AssertionRewritingHook = lll111ll11l11ll1Il1l1  # type: ignore
    sys.modules['_pytest.assertion.rewrite'] = _pytest.assertion.rewrite
