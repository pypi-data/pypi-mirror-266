import logging
import os
import re
import subprocess

import click
import click_log

from .yaml_tools import home_config

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


class Workshop(object):

    # regex patterns collections
    omit_re = [
        re.compile("^.*type 'quit' to exit"),
        re.compile("^Loading Steam API.*"),
        re.compile("^.*Assertion Failed: Is64BitOS.*"),
        # re.compile(''),
    ]

    def __init__(self, item_id, item_name, is_examine, beta, betapassword):
        self.item_id = item_id
        self.item_name = item_name
        self.is_examine = is_examine
        self.arma_config = home_config("arma_server.yaml")
        self.beta = beta
        self.betapassword = betapassword

    def download(self):
        click.secho(f"Downloading item {self.item_id} : {self.item_name}", fg="green")
        success = True
        steam_cmd = [
            "steamcmd",
            "+login",
            self.arma_config["username"],
            self.arma_config["password"],
            "+workshop_download_item",
            "107410",
            self.item_id,
        ]

        if self.beta:
            steam_cmd.append("-beta")
            steam_cmd.append(self.beta)

        if self.betapassword:
            steam_cmd.append("-betapassword")
            steam_cmd.append(self.betapassword)

        steam_cmd.append("validate")
        steam_cmd.append("+quit")

        process = subprocess.Popen(
            steam_cmd,
            stdout=subprocess.PIPE,
        )
        for line in iter(lambda: process.stdout.readline(), b""):

            cleaned = line.decode("utf-8").strip()
            if "..." in cleaned:
                pieces = cleaned.split("...")
                click.echo(pieces[0])
            elif "ERROR" in cleaned:
                click.secho(cleaned, fg="red")
                success = False
            elif not self.is_omit(cleaned):
                click.echo(cleaned)

        return success

    def is_omit(self, line):

        for item in self.omit_re:
            if item.match(line):
                return True
        return False

    def examine(self):
        src = os.path.join(
            self.arma_config["workshop"],
            self.item_id,
        )
        dst = os.path.join(
            self.arma_config["arma_home"],
            "mods",
            self.item_name,
        )
        if self.is_examine:
            print(f"src: {src}")
            print(f"dst: {dst}")
            files = os.listdir(src)
            for f in files:
                print(f"  {f}")

    def symlink_to_mods(self):
        src = os.path.join(
            self.arma_config["workshop"],
            self.item_id,
        )
        dst = os.path.join(
            self.arma_config["arma_home"],
            "mods",
            self.item_name,
        )
        if not os.path.exists(dst):
            os.symlink(src, dst, target_is_directory=True)

    def symlink_to_mpmissions(self):
        item_folder = os.path.join(self.arma_config["workshop"], self.item_id)
        files = os.listdir(item_folder)
        if (len(files)) == 1:
            src = os.path.join(item_folder, files[0])
            dst = os.path.join(self.arma_config["arma_home"], "mpmissions", self.item_name)
            if not os.path.exists(dst):
                os.symlink(src, dst, target_is_directory=False)
        else:
            print("!! not a packaged pbo file !!")


@click.command()
@click.option("--id", "item_id", help="workshop id of mod")
@click.option("--name", "item_name", help="name of mod")
@click.option(
    "--mission",
    "is_mission",
    is_flag=True,
    help="indicate this links to MPMissions and not mods",
)
@click.option(
    "--mod",
    "is_mod",
    is_flag=True,
    help="indicate this links to mods and not MPMissions",
)
@click.option(
    "--examine",
    "is_examine",
    is_flag=True,
    help="show filenames and folder contents to examine what is pulled down",
)
@click.option(
    "--beta",
    "beta",
    help="beta name",
)
@click.option(
    "--betapassword",
    "betapassword",
    help="betapassword",
)
@click_log.simple_verbosity_option(logger)
def main(item_id, item_name, is_mission, is_mod, is_examine, beta, betapassword):

    if item_id and item_name:
        workshop = Workshop(item_id, item_name, is_examine, beta, betapassword)

        if workshop.download():
            if is_examine:
                workshop.examine()
            if is_mission:
                workshop.symlink_to_mpmissions()
            elif is_mod:
                workshop.symlink_to_mods()


if __name__ == "__main__":
    main()
