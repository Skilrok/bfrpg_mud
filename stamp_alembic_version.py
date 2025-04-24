#!/usr/bin/env python3
"""
Script to stamp the Alembic version to match our database state.
This is useful when tables have been created outside of Alembic or when there's a version mismatch.
"""

import argparse
import os
import sys

from alembic import command
from alembic.config import Config


def stamp_version(revision="head"):
    """
    Stamp the database with the specified Alembic revision without running migrations.

    Args:
        revision (str): Revision identifier to stamp database with
    """
    # Get directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create Alembic config
    alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))

    try:
        # Stamp the database with the given revision
        command.stamp(alembic_cfg, revision)
        print(f"Successfully stamped database with Alembic revision: {revision}")
    except Exception as e:
        print(f"Error stamping database: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Stamp the database with an Alembic revision without running migrations."
    )
    parser.add_argument(
        "--revision",
        default="head",
        help="Revision to stamp the database with (default: head)",
    )

    args = parser.parse_args()
    stamp_version(args.revision)


if __name__ == "__main__":
    main()
