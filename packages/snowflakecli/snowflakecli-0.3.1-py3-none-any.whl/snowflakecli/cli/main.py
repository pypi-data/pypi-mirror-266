#!/usr/bin/env python3

import typer
import ask
import configure
import scrape
import account
import database
import warehouse

main = typer.Typer()


main.add_typer(
    ask.app,
    name="ask",
    help="Ask Snowflakecli LLM about your Snowflake resources",
)
main.add_typer(
    ask.app,
    name="configure",
    help="Configure Snowflakecli",
)
main.add_typer(
    scrape.app,
    name="scrape",
    help="Generate vector embeddings from Snowflake statistics, metadata, and schemata",
)
main.add_typer(account.app, name="account", help="Manage Snowflake account")
main.add_typer(
    warehouse.app,
    name="warehouse",
    help="Manage and optimize Snowflake Virtual Warehouses",
)
main.add_typer(database.app, name="database", help="Manage Snowflake databases")

if __name__ == "__main__":
    main()
