import typing

from app.admin.views import AdminCurrentView
from app.blackjack.views import CashAddView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/blackjack.add_cash", CashAddView)