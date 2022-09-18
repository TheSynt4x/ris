from app import services
from app.utils import types


class Run:
    name = "run"

    async def handle(self, *args):
        section = args[0] if len(args) else types.NEW
        limit = int(args[1]) if len(args) == 2 else None

        await services.sync.sync_subs(section, limit)
