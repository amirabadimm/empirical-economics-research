from .build_monthly_dataset import build
from .fetch_us_cpi import fetch
from .prepare_iran_cpi import prepare as prepare_cpi
from .prepare_liquidity import prepare as prepare_liquidity
from .prepare_usd import prepare as prepare_usd
from .update_usd import update as update_usd
from .validate import validate


def main() -> None:
    fetch()
    update_usd()
    prepare_liquidity()
    prepare_cpi()
    prepare_usd()
    build()
    validate()


if __name__ == "__main__":
    main()
