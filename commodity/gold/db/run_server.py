"""Server adapter: use existing Docker environment settings without exposing credentials."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

from psycopg.conninfo import make_conninfo

PROJECT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=("live", "daily", "full"))
    parser.add_argument("--env-file", type=Path, default=Path("/opt/investment-dashboard/.env"))
    parser.add_argument("--container", default="investment_postgres")
    args = parser.parse_args()
    if "GOLD_DATABASE_URL" not in os.environ:
        settings = {}
        for line in args.env_file.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                parts = shlex.split(value, comments=False)
                if len(parts) > 1:
                    raise ValueError("Quote environment values containing spaces")
                settings[key.strip()] = parts[0] if parts else ""
        networks = json.loads(subprocess.check_output([
            "docker", "inspect", args.container, "--format", "{{json .NetworkSettings.Networks}}"
        ], text=True))
        host = next(iter(networks.values()))["IPAddress"]
        os.environ["GOLD_DATABASE_URL"] = make_conninfo(
            host=host, dbname=settings["POSTGRES_DB"], user=settings["POSTGRES_USER"],
            password=settings["POSTGRES_PASSWORD"], connect_timeout=10)
    if args.job == "live":
        subprocess.run([sys.executable, str(PROJECT / "db/live_gold.py")], check=True)
    else:
        full = ["--full"] if args.job == "full" else []
        for script in ("collect_daily.py", "collect_fipiran_nav.py"):
            subprocess.run([sys.executable, str(PROJECT / script), *full], check=True)
        subprocess.run([sys.executable, str(PROJECT / "db/load_gold.py")], check=True)


if __name__ == "__main__":
    main()
