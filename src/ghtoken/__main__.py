from __future__ import annotations
import argparse
import sys
from . import GHTokenNotFound, __version__, get_ghtoken


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrieve GitHub access tokens from various sources"
    )
    parser.add_argument("-E", "--env", help="Use specified .env file", metavar="FILE")
    parser.add_argument(
        "--no-dotenv",
        dest="dotenv",
        action="store_false",
        help="Do not consult .env file",
    )
    parser.add_argument(
        "--no-environ",
        dest="environ",
        action="store_false",
        help="Do not consult environment variables",
    )
    parser.add_argument(
        "--no-gh", dest="gh", action="store_false", help="Do not consult gh"
    )
    parser.add_argument(
        "--no-hub",
        dest="hub",
        action="store_false",
        help="Do not consult hub configuration file",
    )
    parser.add_argument(
        "--no-hub-oauthtoken",
        dest="hub_oauthtoken",
        action="store_false",
        help="Do not consult hub.oauthtoken Git config option",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    args = parser.parse_args()
    dotenv: bool | str = args.dotenv
    if dotenv and args.env is not None:
        dotenv = args.env
    environ: bool = args.environ
    gh: bool = args.gh
    hub: bool = args.hub
    hub_oauthtoken: bool = args.hub_oauthtoken
    try:
        token = get_ghtoken(
            dotenv=dotenv,
            environ=environ,
            gh=gh,
            hub=hub,
            hub_oauthtoken=hub_oauthtoken,
        )
    except GHTokenNotFound as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    else:
        print(token)


if __name__ == "__main__":
    main()  # pragma: no cover
