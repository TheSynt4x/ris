from aioconsole import ainput

from app.libs import upload


class Mega:
    name = "mega"

    async def handle(self, *args):
        if args[0] == "login":
            username = await ainput("username: ")
            password = await ainput("password: ")

            upload.login(username, password)
