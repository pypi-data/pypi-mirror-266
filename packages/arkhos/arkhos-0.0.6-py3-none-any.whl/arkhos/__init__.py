from arkhos.http import HttpResponse as http, JsonResponse as json, render as render

import os

agd = os.environ.get("ARKHOS_GLOBAL_DOMAIN")
if agd:
    from arkhos.arkhos_global import _global, get, set, log
else:
    from arkhos.arkhos_local import _global, get, set, log, set_up_local

    set_up_local()
