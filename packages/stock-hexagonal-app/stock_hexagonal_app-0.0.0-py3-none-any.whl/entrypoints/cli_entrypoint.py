import logging
import typer
from typing_extensions import Annotated

from helpers.logger import logger


app = typer.Typer(help="CLI Application for analyzing stock data.")

statistics_app = typer.Typer()
app.add_typer(statistics_app, name="count-statistics", help="Calculate selected statistics.")


@app.command()
def search_for_company(
    phrase: Annotated[
        str,
        typer.Option(
            help="Search for company by passed phrase.",
        ),
    ],
    debug: Annotated[bool, typer.Option("Switch logger debug mode.")] = False,
):
    if debug:
        logger.setLevel(logging.DEBUG)
    print(f"Searching for comapny by phrase: {phrase}")


@app.command()
def draw_stock_graph(
    company_symbol: Annotated[
        str,
        typer.Option(
            help="Company stock symbol.",
        ),
    ],
    debug: Annotated[bool, typer.Option("Switch logger debug mode.")] = False,
):
    if debug:
        logger.setLevel(logging.DEBUG)
    print(f"Drawing stock graph for comapny: {company_symbol}")


@statistics_app.command()
def value_at_risk(
    company_symbol: Annotated[
        str,
        typer.Option(
            help="Company stock symbol.",
        ),
    ],
    debug: Annotated[bool, typer.Option("Switch logger debug mode.")] = False,
):
    if debug:
        logger.setLevel(logging.DEBUG)
    print(f"Calculating value at risk for: {company_symbol}")


if __name__ == "__main__":
    app()
