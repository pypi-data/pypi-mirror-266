import argparse
import os
import sys
from importlib.metadata import version

from IPython.terminal.ipapp import TerminalIPythonApp

from bec_lib import ServiceConfig

# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=unused-import
# pylint: disable=ungrouped-imports

try:
    from bec_plugins.bec_client import startup
except ImportError:
    startup = None

main_dict = {"startup": startup}


def main(wait_for_server=True):
    parser = argparse.ArgumentParser(
        prog="BEC IPython client", description="BEC command line interface"
    )
    parser.add_argument("--version", action="store_true", default=False)
    parser.add_argument("--nogui", action="store_true", default=False)
    parser.add_argument("--config", action="store", default=None)
    args, left_args = parser.parse_known_args()

    # remove already parsed args from command line args
    sys.argv = sys.argv[:1] + left_args

    if args.version:
        print(f"BEC IPython client: {version('bec_client')}")
        sys.exit(0)

    config_file = args.config
    if config_file:
        if not os.path.isfile(config_file):
            raise FileNotFoundError("Config file not found.")
        print("Using config file: ", config_file)
        config = ServiceConfig(config_file)

    if startup and "config" not in locals():
        # check if pre-startup.py script exists
        file_name = os.path.join(os.path.dirname(startup.__file__), "pre_startup.py")
        if os.path.isfile(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                # exec the pre-startup.py script and pass the arguments
                # pylint: disable=exec-used
                exec(file.read(), globals(), locals())

    # check if config was defined in pre-startup.py
    if "config" not in locals():
        config = ServiceConfig()

    main_dict["config"] = config
    main_dict["args"] = args
    main_dict["wait_for_server"] = wait_for_server

    app = TerminalIPythonApp()
    app.interact = True
    app.initialize(argv=["-i", os.path.join(os.path.dirname(__file__), "bec_startup.py")])

    try:
        app.start()
    finally:
        if "bec" in main_dict:
            # bec object is inserted into main_dict by bec_startup
            main_dict["bec"].shutdown()


if __name__ == "__main__":
    main()
