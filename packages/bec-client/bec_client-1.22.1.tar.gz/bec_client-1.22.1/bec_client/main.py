import argparse
import sys
from importlib.metadata import version

from IPython.terminal.ipapp import TerminalIPythonApp

from bec_client.bec_ipython_client import BECIPythonClient
from bec_lib import RedisConnector, ServiceConfig, bec_logger

# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=unused-import
# pylint: disable=ungrouped-imports

try:
    from bec_plugins.bec_client import startup
except ImportError:
    startup = None

try:
    from bec_widgets.cli import BECFigure
except ImportError:
    BECFigure = None

logger = bec_logger.logger


def main():
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

    app = TerminalIPythonApp()
    app.interact = True
    app.initialize(argv=[])

    bec = BECIPythonClient(config, RedisConnector)
    bec.load_high_level_interface("spec_hli")
    bec.start()

    dev = bec.device_manager.devices
    scans = bec.scans

    if not args.nogui and BECFigure is not None:
        fig = bec.fig = BECFigure()
        fig.show()

    ####################### END OF INIT #############################
    #################################################################

    # MODIFY THE SECTIONS BELOW TO CUSTOMIZE THE BEC

    ################################################################
    ################################################################
    import numpy as np  # not needed but always nice to have

    bec._ip.prompts.status = 1

    # SETUP BEAMLINE INFO
    from bec_client.plugins.SLS.sls_info import OperatorInfo, SLSInfo

    bec._beamline_mixin._bl_info_register(SLSInfo)
    bec._beamline_mixin._bl_info_register(OperatorInfo)

    if startup:
        # check if post-startup.py script exists
        file_name = os.path.join(os.path.dirname(startup.__file__), "post_startup.py")
        if os.path.isfile(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                # pylint: disable=exec-used
                exec(file.read())

    try:
        app.start()
    finally:
        bec.shutdown()


if __name__ == "__main__":
    main()
