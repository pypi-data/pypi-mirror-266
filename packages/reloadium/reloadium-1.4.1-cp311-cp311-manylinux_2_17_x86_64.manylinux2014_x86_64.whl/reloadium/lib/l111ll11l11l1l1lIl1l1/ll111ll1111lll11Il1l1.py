from reloadium.corium.vendored import logging
from pathlib import Path
from threading import Thread
import time
from typing import TYPE_CHECKING, List, Optional

from reloadium.corium import llllllllll1lll11Il1l1
from reloadium.corium.llllllllll1lll11Il1l1.ll1111l1ll11llllIl1l1 import ll1l11lllll111llIl1l1
from reloadium.lib.l111ll11l11l1l1lIl1l1.lll1l1l1l11l111lIl1l1 import l11111lll111ll11Il1l1
from reloadium.corium.lll1l1111111l1llIl1l1 import llll1ll1ll1l1l11Il1l1
from reloadium.corium.ll11l11ll11l111lIl1l1 import ll11l111l11l111lIl1l1
from reloadium.corium.llll1ll1l11lllllIl1l1 import l1111ll1ll1l11llIl1l1
from reloadium.corium.lll1llllllllll11Il1l1 import lll1llllllllll11Il1l1
from dataclasses import dataclass, field

if (TYPE_CHECKING):
    from reloadium.vendored.websocket_server import WebsocketServer


__RELOADIUM__ = True

__all__ = ['lll1111l1lllll1lIl1l1']



ll1l1l11l1l111l1Il1l1 = '\n<!--{info}-->\n<script type="text/javascript">\n   // <![CDATA[  <-- For SVG support\n     function refreshCSS() {\n        var sheets = [].slice.call(document.getElementsByTagName("link"));\n        var head = document.getElementsByTagName("head")[0];\n        for (var i = 0; i < sheets.length; ++i) {\n           var elem = sheets[i];\n           var parent = elem.parentElement || head;\n           parent.removeChild(elem);\n           var rel = elem.rel;\n           if (elem.href && typeof rel != "string" || rel.length === 0 || rel.toLowerCase() === "stylesheet") {\n              var url = elem.href.replace(/(&|\\?)_cacheOverride=\\d+/, \'\');\n              elem.href = url + (url.indexOf(\'?\') >= 0 ? \'&\' : \'?\') + \'_cacheOverride=\' + (new Date().valueOf());\n           }\n           parent.appendChild(elem);\n        }\n     }\n     let protocol = window.location.protocol === \'http:\' ? \'ws://\' : \'wss://\';\n     let address = protocol + "{address}:{port}";\n     let socket = undefined;\n     let lost_connection = false;\n\n     function connect() {\n        socket = new WebSocket(address);\n         socket.onmessage = function (msg) {\n            if (msg.data === \'reload\') window.location.href = window.location.href;\n            else if (msg.data === \'refreshcss\') refreshCSS();\n         };\n     }\n\n     function checkConnection() {\n        if ( socket.readyState === socket.CLOSED ) {\n            lost_connection = true;\n            connect();\n        }\n     }\n\n     connect();\n     setInterval(checkConnection, 500)\n\n   // ]]>\n</script>\n'














































@dataclass
class lll1111l1lllll1lIl1l1:
    ll11111111l1ll11Il1l1: str
    l111l1lll11111l1Il1l1: int
    lll1l11ll11ll11lIl1l1: ll11l111l11l111lIl1l1

    l111ll11ll11lll1Il1l1: Optional["WebsocketServer"] = field(init=False, default=None)
    llllll111l1l111lIl1l1: str = field(init=False, default='')

    l1ll1l1ll11lll11Il1l1 = 'Reloadium page reloader'

    def lll1l1l1lll1llllIl1l1(l1ll11lllllll11lIl1l1) -> None:
        from reloadium.vendored.websocket_server import WebsocketServer

        l1ll11lllllll11lIl1l1.lll1l11ll11ll11lIl1l1.l1ll1l1ll11lll11Il1l1(''.join(['Starting reload websocket server on port ', '{:{}}'.format(l1ll11lllllll11lIl1l1.l111l1lll11111l1Il1l1, '')]))

        l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1 = WebsocketServer(host=l1ll11lllllll11lIl1l1.ll11111111l1ll11Il1l1, port=l1ll11lllllll11lIl1l1.l111l1lll11111l1Il1l1)
        l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1.run_forever(threaded=True)

        l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1 = ll1l1l11l1l111l1Il1l1

        l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1 = l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1.replace('{info}', str(l1ll11lllllll11lIl1l1.l1ll1l1ll11lll11Il1l1))
        l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1 = l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1.replace('{port}', str(l1ll11lllllll11lIl1l1.l111l1lll11111l1Il1l1))
        l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1 = l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1.replace('{address}', l1ll11lllllll11lIl1l1.ll11111111l1ll11Il1l1)

    def l1111ll11l1l11l1Il1l1(l1ll11lllllll11lIl1l1, l11l111111lll111Il1l1: str) -> str:
        lllll111lll1l1llIl1l1 = l11l111111lll111Il1l1.find('<head>')
        if (lllll111lll1l1llIl1l1 ==  - 1):
            lllll111lll1l1llIl1l1 = 0
        l11111l11lll1l11Il1l1 = ((l11l111111lll111Il1l1[:lllll111lll1l1llIl1l1] + l1ll11lllllll11lIl1l1.llllll111l1l111lIl1l1) + l11l111111lll111Il1l1[lllll111lll1l1llIl1l1:])
        return l11111l11lll1l11Il1l1

    def l111l1l11ll1l111Il1l1(l1ll11lllllll11lIl1l1) -> None:
        try:
            l1ll11lllllll11lIl1l1.lll1l1l1lll1llllIl1l1()
        except Exception as l1lll11llll1111lIl1l1:
            l1ll11lllllll11lIl1l1.lll1l11ll11ll11lIl1l1.lll1l11llll1l11lIl1l1('Could not start page reload server', ll111ll111l111l1Il1l1=True)

    def lll11lll11l11111Il1l1(l1ll11lllllll11lIl1l1) -> None:
        if ( not l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1):
            return 

        l1ll11lllllll11lIl1l1.lll1l11ll11ll11lIl1l1.l1ll1l1ll11lll11Il1l1('Reloading page')
        l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1.send_message_to_all('reload')
        lll1llllllllll11Il1l1.l1111l1l1llll1llIl1l1()

    def l1llll1l1l111l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        if ( not l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1):
            return 

        l1ll11lllllll11lIl1l1.lll1l11ll11ll11lIl1l1.l1ll1l1ll11lll11Il1l1('Stopping reload server')
        l1ll11lllllll11lIl1l1.l111ll11ll11lll1Il1l1.shutdown()

    def l11llllllll1l11lIl1l1(l1ll11lllllll11lIl1l1, lll1l11l1111l1l1Il1l1: float) -> None:
        def l1l111111lll1l1lIl1l1() -> None:
            time.sleep(lll1l11l1111l1l1Il1l1)
            l1ll11lllllll11lIl1l1.lll11lll11l11111Il1l1()

        ll1l11lllll111llIl1l1(ll1ll111llll1111Il1l1=l1l111111lll1l1lIl1l1, l1ll1lll1lll111lIl1l1='page-reloader').start()


@dataclass
class ll1ll111111l1111Il1l1(l11111lll111ll11Il1l1):
    ll1l1l11l1l111l1Il1l1: Optional[lll1111l1lllll1lIl1l1] = field(init=False, default=None)

    lllll11ll11llll1Il1l1 = '127.0.0.1'
    l1l11l11ll1l1lllIl1l1 = 4512

    def l1l1ll1lll111l11Il1l1(l1ll11lllllll11lIl1l1) -> None:
        llll1ll1ll1l1l11Il1l1.lll1llll1111lll1Il1l1.ll1lll1lll111ll1Il1l1.l1lll1lll1lllll1Il1l1('html')

    def l11ll11ll1ll11l1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path, l11111l11ll1l111Il1l1: List[l1111ll1ll1l11llIl1l1]) -> None:
        if ( not l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
            return 

        from reloadium.corium.l11ll1ll111l1l11Il1l1.ll11llll1ll11l1lIl1l1 import lll1l1llllllll11Il1l1

        if ( not any((isinstance(l11l1111l1ll1111Il1l1, lll1l1llllllll11Il1l1) for l11l1111l1ll1111Il1l1 in l11111l11ll1l111Il1l1))):
            if (l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
                l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.lll11lll11l11111Il1l1()

    def ll1llllllllllll1Il1l1(l1ll11lllllll11lIl1l1, lllll1l1l111lll1Il1l1: Path) -> None:
        if ( not l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
            return 
        l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.lll11lll11l11111Il1l1()

    def ll111lll111l1lllIl1l1(l1ll11lllllll11lIl1l1, l111l1lll11111l1Il1l1: int) -> lll1111l1lllll1lIl1l1:
        while True:
            l1lll1ll1lllllllIl1l1 = (l111l1lll11111l1Il1l1 + l1ll11lllllll11lIl1l1.l1l11l11ll1l1lllIl1l1)
            try:
                l11111l11lll1l11Il1l1 = lll1111l1lllll1lIl1l1(ll11111111l1ll11Il1l1=l1ll11lllllll11lIl1l1.lllll11ll11llll1Il1l1, l111l1lll11111l1Il1l1=l1lll1ll1lllllllIl1l1, lll1l11ll11ll11lIl1l1=l1ll11lllllll11lIl1l1.lll11lll1lll11l1Il1l1)
                l11111l11lll1l11Il1l1.l111l1l11ll1l111Il1l1()
                l1ll11lllllll11lIl1l1.l1ll1l1l1lll1ll1Il1l1()
                break
            except OSError:
                l1ll11lllllll11lIl1l1.lll11lll1lll11l1Il1l1.l1ll1l1ll11lll11Il1l1(''.join(["Couldn't create page reloader on ", '{:{}}'.format(l1lll1ll1lllllllIl1l1, ''), ' port']))
                l1ll11lllllll11lIl1l1.l1l11l11ll1l1lllIl1l1 += 1

        return l11111l11lll1l11Il1l1

    def l1ll1l1l1lll1ll1Il1l1(l1ll11lllllll11lIl1l1) -> None:
        l1ll11lllllll11lIl1l1.lll11lll1lll11l1Il1l1.l1ll1l1ll11lll11Il1l1('Injecting page reloader')

    def lllllll1111lllllIl1l1(l1ll11lllllll11lIl1l1) -> None:
        super().lllllll1111lllllIl1l1()

        if (l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1):
            l1ll11lllllll11lIl1l1.ll1l1l11l1l111l1Il1l1.l1llll1l1l111l11Il1l1()
