#!/usr/bin/env python3
"""
Script to apply the database migrations for the extended schema.
This will create all the new tables and update existing ones.
"""

import argparse
import os
import sys


def run_migration(revision="head", sql_only=False):
    """
    Run the Alembic migration to the specified revision.

    Args:
        revision (str): Revision to migrate to, defaults to 'head'
        sql_only (bool): If True, only print the SQL without applying it
    """
    import alembic.config

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create Alembic config
    alembic_args = [
        "--raiseerr",
        "-c",
        os.path.join(script_dir, "alembic.ini"),
    ]

    # Add SQL-only flag if requested
    if sql_only:
        alembic_args.extend(["upgrade", revision, "--sql"])
    else:
        alembic_args.extend(["upgrade", revision])

    # Run the migration
    alembic.config.main(alembic_args)

    if not sql_only:
        print(f"Successfully migrated database to revision: {revision}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Apply database migrations for the BFRPG MUD."
    )
    parser.add_argument(
        "--revision", default="head", help="Revision to migrate to (default: head)"
    )
    parser.add_argument(
        "--sql-only", action="store_true", help="Only print the SQL without applying it"
    )

    args = parser.parse_args()

    try:
        run_migration(args.revision, args.sql_only)
    except Exception as e:
        print(f"Error applying migration: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
