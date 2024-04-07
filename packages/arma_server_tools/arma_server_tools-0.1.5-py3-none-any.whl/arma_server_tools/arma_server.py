import logging
import os
import re
import subprocess

import click
import click_log
import yaml

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


# python pull.py --id=463939057 --name=ace
# https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output
# https://docs.python.org/3/library/subprocess.html
# https://docs.python.org/3/library/shutil.html
# https://docs.python.org/dev/distutils/apiref.html#distutils.dir_util.copy_tree

# local install variables
# ARMA_HOME = '/home/steam/.steam/steamcmd/arma3/'
# ARMA_SERVER = os.path.join(ARMA_HOME, "arma3server")


class LineConsumer:

    # https://regex101.com/

    # regex patterns collections
    omit_re = [
        re.compile(r"^\d+:\d+:\d+ Updating base class.*"),
        re.compile(r"^\d+:\d+:\d+ ==== Loaded addons ===="),
        re.compile(r"^\d+:\d+:\d+\s[\/\w+\.]+\s-\s.*"),
        re.compile(r"^\d+:\d+:\d+ =+"),
        re.compile(r"^\d+:\d+:\d+ =+ List of mods =+"),
        re.compile(r"^\d+:\d+:\d+ -+"),
        re.compile(r"^\d+:\d+:\d+ +name.*fullPath"),
        re.compile(r"^.*:Some of magazines weren\'t stored in soldier Vest or Uniform\?"),
        re.compile(r"^.*: ?No geometry and no visual shape"),
        re.compile(r"^\d+:\d+:\d+ Strange convex.*"),
        re.compile(r"^\d+:\d+:\d+ ?Unsupported language.*"),
    ]

    warning_re = [
        re.compile(r"^.* Warning:.*"),
        re.compile(r"^.* Warning Message:.*"),
    ]

    green_re = [
        re.compile(r"^\d+:\d+:\d+\sBattlEye Server:.*"),
        re.compile(r".* Connected to Steam servers"),
        re.compile(r"^\d+:\d+:\d+ ? Roles assigned"),
        re.compile(r"^\d+:\d+:\d+ ? Reading mission.*"),
        re.compile(r"^\d+:\d+:\d+ ?Starting mission:"),
        re.compile(r"^\d+:\d+:\d+ ? ? Mission file:.*"),
        re.compile(r"^\d+:\d+:\d+ ? ? Mission world:.*"),
        re.compile(r"^\d+:\d+:\d+ ? ? Mission directory:.*"),
    ]

    extract_re = [
        re.compile(
            r"^\d+:\d+:\d+\s+"
            + r"(?P<name>[\w+\s\(\)-]+)\s+\|\s+"
            + r"(?P<modDir>[\w+\s]+)\s+\|\s+"
            + r"(?P<default>[\w+\s]+)\s+\|\s+"
            + r"(?P<official>[\w+\s]+)\s+\|\s+"
            + r"(?P<origin>[\w+\s]+)\s+\|\s+"
            + r"(?P<hash>[\w+\s]+)\s+\|\s+"
            + r"(?P<hashShort>[\w+\s]+)\s+\|\s+"
            + r"(?P<fullPath>[\w+\s\.\/]+)"
            # 14:21:06 Player dent connected (id=76561198017256167).
            # 14:09:27 Player dent disconnected.
        ),
    ]

    # 9:22:26 Initializing Steam server - Game Port: 2302, Steam Query Port: 2303
    # Arma 3 Console version 2.00.146766 x86 : port 2302

    def is_omit(self, line: str) -> bool:

        for item in self.omit_re:
            if item.match(line):
                return True
        return False

    def is_warning(self, line: str) -> bool:
        for item in self.warning_re:
            if item.match(line):
                return True
        return False

    def is_green(self, line: str) -> bool:
        for item in self.green_re:
            if item.match(line):
                return True
        return False

    def extract(self, line: str):
        for item in self.extract_re:
            results = item.match(line)
            if results:
                return results
        return False

    def parse(self, line: str):
        if self.is_omit(line):
            return

        if self.is_warning(line):
            click.secho(line, fg="red")
            return

        if self.is_green(line):
            click.secho(line, fg="green")
            return

        # result = self.extract(line)
        # if result:
        #     # print(result.groupdict())
        #     return

        click.echo(line)


# def serve_arma():
#     success = True
#     arma_cmd = [ARMA_SERVER, ]
#     try:
#         consumer = LineConsumer()
#         process = subprocess.Popen(
#             arma_cmd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             cwd=ARMA_HOME
#         )
#         for line in iter(lambda: process.stdout.readline(), b''):
#             cleaned = line.decode('utf-8').strip()
#             consumer.parse(cleaned)
#     except KeyboardInterrupt:
#         print("~~~EXIT~~~")
#     return success


class ArmaServer:

    name = None
    config = None
    mods = None
    port = 2302
    arma_home = "/home/steam/.steam/steamcmd/arma3/"
    arma_config = "/home/steam/arma_configs"
    arma_command = None
    # mods_folder = "mods"

    def parse_yaml(self, yaml_file):
        with open(yaml_file, "r") as stream:
            try:
                meta = yaml.safe_load(stream)

                if "name" in meta:
                    self.name = meta["name"]

                if "config" in meta:
                    self.config = os.path.join(self.arma_config, meta["config"])

                if "port" in meta:
                    self.port = meta["port"]

                if "mods" in meta:
                    self.mods = meta["mods"]

            except yaml.YAMLError as exc:
                print(exc)

    def generate_command(self):
        server_path = os.path.join(self.arma_home, "arma3server")
        command = [
            server_path,
        ]
        if self.name:
            command.append(f'-name="{self.name}"')

        command.append(f"-port={self.port}")

        if self.config:
            command.append(f'-config="{self.config}"')

        if self.mods:

            # MOD="mods/@cba_a3;mods/@ace;"  # cannot handle cdlc content

            mods_list = []
            for m in self.mods:
                # cannot handle cdlc content
                # mods_list.append(f'{self.mods_folder}/@{m};')
                mods_list.append(f"{m};")

            mods_string = "".join(mods_list)
            command.append(f"-mods={mods_string}")
        return command

    def serve(self):
        success = True
        arma_cmd = self.generate_command()
        try:
            consumer = LineConsumer()
            process = subprocess.Popen(arma_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.arma_home)
            for line in iter(lambda: process.stdout.readline(), b""):
                cleaned = line.decode("utf-8").strip()
                consumer.parse(cleaned)
        except KeyboardInterrupt:
            print("~~~EXIT~~~")
        return success


@click.option("--yaml", "yaml_file", help="path to yaml config file")
@click.command()
@click_log.simple_verbosity_option(logger)
def main(yaml_file):

    if yaml_file:
        arma = ArmaServer()
        arma.parse_yaml(yaml_file)
        print(arma.name)
        print(arma.config)
        print(arma.port)

        logger.debug(arma.generate_command())
        arma.serve()
    else:
        logger.error("yaml file is required")


if __name__ == "__main__":
    main()
