from app import services


class Run:
    name = "run"

    async def handle(self, *args):
        section = args[0] if len(args) else None
        limit = int(args[1]) if len(args) == 2 else None

        await services.sync.sync_subs(section, limit)
