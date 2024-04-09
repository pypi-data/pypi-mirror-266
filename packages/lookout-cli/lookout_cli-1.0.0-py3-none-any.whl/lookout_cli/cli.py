import lookout_cli.groups.misc as misc
import lookout_cli.groups.setup as setup
from lookout_cli.helpers import is_dev_version, get_version
from lookout_cli.banner import get_banner
import click
import os


def cli():
    dev_mode = is_dev_version()
    version = get_version()
    mode = "Developer" if dev_mode else "User"
    banner = get_banner(mode, version)

    os.environ["LOOKOUT_CLI_DEV_MODE"] = "true" if dev_mode else "false"

    @click.group(help=banner)
    def lookout_cli():
        pass

    lookout_cli.add_command(misc.authenticate)
    lookout_cli.add_command(misc.upgrade)
    lookout_cli.add_command(misc.build)
    lookout_cli.add_command(misc.down)
    lookout_cli.add_command(misc.up)
    lookout_cli.add_command(misc.configure)
    lookout_cli.add_command(misc.config)

    if dev_mode:
        lookout_cli.add_command(misc.lint)
        lookout_cli.add_command(misc.bake)
        lookout_cli.add_command(misc.type_generate)
        lookout_cli.add_command(setup.setup)
        setup.setup.add_command(setup.secrets)

    lookout_cli()


if __name__ == "__main__":
    cli()
