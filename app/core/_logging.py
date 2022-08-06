import logging
from datetime import date

logging.basicConfig(
    filename=f"logs/{date.today()}.txt",
    filemode="a",
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
console.setFormatter(formatter)

logging.getLogger("").addHandler(console)

logging.info("Running RIS")

logger = logging.getLogger("RIS")
