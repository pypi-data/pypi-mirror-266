import re
from dataclasses import dataclass
from typing import Any

import click
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Item:
    name: str
    steam_url: str
    steam_id: str

    def __str__(self) -> str:
        return f"{self.steam_id:>11} : {self.name}"


def clean(target: str) -> str:
    """Remove spaces and symbols from name.
    Symbols:
    [] () ! . - _ / ' " :
    """
    pattern = r"\s|\[|]|\(|\)|\!|\.|-|_|/|'|\"|:|;"
    product = re.sub(pattern, "", target)
    return product


class PresetParser(object):

    def __init__(self, html_file: str):
        self.html_file: str = html_file

    def parse(self, mods: bool = False) -> None:
        with open(self.html_file, encoding="ISO-8859-1") as fp:
            soup = BeautifulSoup(fp, features="html.parser")

        rows = soup.findAll("tr", {"data-type": "ModContainer"})

        if not mods:
            for r in rows:
                item = self.parse_row(r)
                click.echo(item)
            return

        # -mod=CUPTCore;@CUPTMaps;
        product = []
        for r in rows:
            item = self.parse_row(r)
            product.append(f"@{clean(item.name)};")

        product_string = "".join(product)
        click.echo(product_string)

    @staticmethod
    def parse_row(row: Any) -> Item:
        name = row.find("td", {"data-type": "DisplayName"}).text
        steam_url = row.find("a", {"data-type": "Link"}).get("href")
        steam_id = steam_url.split("id=")[-1]
        item = Item(
            name=name,
            steam_url=steam_url,
            steam_id=steam_id,
        )
        return item


@click.command()
@click.argument(
    "html_file",
    required=True,
)
@click.option(
    "--mods",
    is_flag=True,
    default=False,
)
def main(html_file: str, mods: bool) -> None:
    pp = PresetParser(html_file)
    pp.parse(mods)


if __name__ == "__main__":
    main()
