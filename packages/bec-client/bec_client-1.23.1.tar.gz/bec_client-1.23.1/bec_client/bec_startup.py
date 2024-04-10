import os
import sys

import numpy as np  # not needed but always nice to have

from bec_client.bec_ipython_client import BECIPythonClient as _BECIPythonClient
from bec_client.main import main_dict as _main_dict
from bec_lib import RedisConnector as _RedisConnector
from bec_lib import bec_logger as _bec_logger

try:
    from bec_widgets.cli import BECFigure as _BECFigure
except ImportError:
    _BECFigure = None

logger = _bec_logger.logger

bec = _BECIPythonClient(
    _main_dict["config"], _RedisConnector, wait_for_server=_main_dict["wait_for_server"]
)
_main_dict["bec"] = bec

bec.load_high_level_interface("spec_hli")

if not _main_dict["args"].nogui and _BECFigure is not None:
    fig = bec.fig = _BECFigure()
    fig.show()

try:
    bec.start()
except Exception:
    sys.excepthook(*sys.exc_info())
else:
    dev = bec.device_manager.devices
    scans = bec.scans

    bec._ip.prompts.status = 1

    # SETUP BEAMLINE INFO
    from bec_client.plugins.SLS.sls_info import OperatorInfo, SLSInfo

    bec._beamline_mixin._bl_info_register(SLSInfo)
    bec._beamline_mixin._bl_info_register(OperatorInfo)

if _main_dict["startup"]:
    # check if post-startup.py script exists
    file_name = os.path.join(os.path.dirname(_main_dict["startup"].__file__), "post_startup.py")
    if os.path.isfile(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            # pylint: disable=exec-used
            exec(file.read())
