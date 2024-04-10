"""Contains classes and functions to support CLI plugins"""

import os
import logging
import click

_logger = logging.getLogger(__name__)


TOOLS_FOLDER = os.path.join(os.path.dirname(__file__), "plugins")


# pylint: disable=too-many-arguments, invalid-name, broad-exception-caught, eval-used


class ToolsGroupCommand(click.MultiCommand):

    """Custom MultiCommand class that dynamically loads plugins"""

    def __init__(
        self,
        name=None,
        invoke_without_command=False,
        no_args_is_help=None,
        subcommand_metavar=None,
        chain=False,
        result_callback=None,
        **attrs,
    ):

        super().__init__(
            name=name,
            invoke_without_command=invoke_without_command,
            no_args_is_help=no_args_is_help,
            subcommand_metavar=subcommand_metavar,
            chain=chain,
            result_callback=result_callback,
            **attrs,
        )

        self.commands = self._find_all_commands()

    def list_commands(self, ctx):

        rv = list(self.commands.keys())
        rv.sort()
        return rv

    def get_command(self, ctx, cmd_name):

        if cmd_name in self.commands:
            return self.commands[cmd_name]

        return None

    def _find_all_commands(self):

        """Find all commands in the plugins folder"""

        commands = {}

        for filename in os.listdir(TOOLS_FOLDER):
            if filename.endswith(".py") and filename != "__init__.py":
                full_plugin_path = os.path.join(TOOLS_FOLDER, filename)

                try:
                    with open(full_plugin_path, encoding="utf-8") as f:

                        # First compile the plugin file module to a code object
                        code = compile(f.read(), full_plugin_path, "exec")

                        # Next, "eval" or execute the code object, and any module-level functions
                        # will be present inside ns, the namespace object
                        ns = {}
                        eval(code, ns, ns)

                        # Loop through each item in the namespace, finding functions that are
                        # instances of click.Command (functions decorated with @click.command)
                        for key, value in ns.items():
                            if isinstance(value, click.Command):
                                commands[key] = value

                except Exception as e:
                    print(e)
                    _logger.debug(
                        f"Plugin file {full_plugin_path} could not be loaded: {e}"
                    )
                    return None

        return commands
