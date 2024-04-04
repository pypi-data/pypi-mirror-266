"""CLI module."""

import argparse
from typing import Any, Dict, List

from openapi_lookup import setup_logger, verbosity_levels
from openapi_lookup.openapis import get_raw_public_apis, parse_rows


logger = setup_logger()


def filter_apis(
    apis: List[Dict[str, Any]], args: argparse.Namespace
) -> List[Dict[str, Any]]:
    """Filter APIs.

    Args:
        apis (List[Dict[str, Any]]): List of APIs to filter.
        args (argparse.Namespace): Arguments to filter by.

    Returns:
        List[Dict[str, Any]]: Filtered list of APIs.
    """
    if args.all is True:
        return apis

    if args.category is not None:
        apis = [api for api in apis if api["category"] == args.category]

    if args.auth_method is not None:
        # Convert auth_method to None if "none" is specified
        if args.auth_method == "none":
            args.auth_method = None

        apis = [api for api in apis if api["auth_method"] == args.auth_method]

    if args.https is not None:
        apis = [api for api in apis if api["https"] == args.https]

    if args.cors is not None:
        apis = [api for api in apis if api["cors"] == args.cors]

    return apis


def print_apis(
    apis: List[Any],
    list_all: bool,
    list_categories: bool,
    list_auth_methods: bool,
    list_https: bool,
    list_cors: bool,
) -> None:
    """Print APIs.

    Args:
        apis (List[Any]): List of APIs to print.
        list_all (bool): Show all results.
        list_categories (bool): Show categories in results.
        list_auth_methods (bool): Show authentication methods in results.
        list_https (bool): Show HTTPS support values in results.
        list_cors (bool): Show CORS support values in results.
    """
    if list_all:
        for api in apis:
            print(
                f"{api['name']} - {api['description']}\n"
                f"  Auth Method: {api['auth_method']}\n"
                f"  HTTPS: {api['https']}\n"
                f"  CORS: {api['cors']}\n"
                f"  Link: {api['link']}\n"
            )
    else:
        if list_categories:
            print("Categories:")
            categories = sorted(list({api["category"] for api in apis}))
            print("  " + "\n  ".join(categories))

        if list_auth_methods:
            print("Authentication Methods:")
            auth_methods = sorted(
                list({str(api["auth_method"]) for api in apis})
            )
            print("  " + "\n  ".join(auth_methods))

        if list_https:
            print("HTTPS Support:")
            https = sorted(list({str(api["https"]) for api in apis}))
            print("  " + "\n  ".join(https))

        if list_cors:
            print("CORS Support:")
            cors = sorted(list({str(api["cors"]) for api in apis}))
            print("  " + "\n  ".join(cors))

    print()


def cli() -> None:
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Open APIs CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--category",
        "-c",
        help="Filter by category",
    )
    parser.add_argument(
        "--auth-method",
        "-a",
        help="Filter by authentication method",
        choices=["apikey", "oauth", "unknown", "none"],
    )
    parser.add_argument(
        "--https",
        "-s",
        help="Filter by HTTPS support",
        choices=[True, False],
    )
    parser.add_argument(
        "--cors",
        "-o",
        help="Filter by CORS support",
        choices=[True, False],
    )
    parser.add_argument(
        "--all",
        "-A",
        help="Show all APIs",
        action="store_true",
    )
    parser.add_argument(
        "--list-categories",
        help="List all categories",
        action="store_true",
    )
    parser.add_argument(
        "--list-auth-methods",
        help="List all authentication methods",
        action="store_true",
    )
    parser.add_argument(
        "--list-https",
        help="List all HTTPS support values",
        action="store_true",
    )
    parser.add_argument(
        "--list-cors",
        help="List all CORS support values",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )
    args = parser.parse_args()

    if (
        all(
            [
                args.category is None,
                args.auth_method is None,
                args.https is None,
                args.cors is None,
                args.all is False,
            ]
        )
        is True
    ):
        print("Error: No filters specified")
        print("Specify at least one filter or use --all to show all APIs")
        exit(1)

    log_level = verbosity_levels[min(args.verbosity, len(verbosity_levels) - 1)]
    logger.setLevel(log_level)

    raw_text = get_raw_public_apis()
    apis = parse_rows(raw_text)
    apis = filter_apis(apis, args)
    print_apis(
        apis,
        list_all=args.all,
        list_categories=args.list_categories,
        list_auth_methods=args.list_auth_methods,
        list_https=args.list_https,
        list_cors=args.list_cors,
    )


if __name__ == "__main__":
    cli()
