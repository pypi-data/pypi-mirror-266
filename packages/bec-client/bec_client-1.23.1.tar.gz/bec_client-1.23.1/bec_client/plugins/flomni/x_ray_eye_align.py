from __future__ import annotations

import builtins
import os
import time
from typing import TYPE_CHECKING

from bec_client.plugins.cSAXS import epics_get, epics_put, fshopen
from bec_lib import bec_logger

logger = bec_logger.logger
# import builtins to avoid linter errors
bec = builtins.__dict__.get("bec")
dev = builtins.__dict__.get("dev")
umv = builtins.__dict__.get("umv")
umvr = builtins.__dict__.get("umvr")

if TYPE_CHECKING:
    from bec_client.plugins.flomni import Flomni


class XrayEyeAlign:
    # pixel calibration, multiply to get mm
    PIXEL_CALIBRATION = 0.1 / 113  # .2 with binning

    def __init__(self, client, flomni: Flomni) -> None:
        self.client = client
        self.flomni = flomni
        self.device_manager = client.device_manager
        self.scans = client.scans
        self.alignment_values = {}
        self.flomni.reset_correction()
        self.flomni.reset_tomo_alignment_fit()

    def _reset_init_values(self):
        self.shift_xy = [0, 0]
        self._xray_fov_xy = [0, 0]

    def save_frame(self):
        epics_put("XOMNYI-XEYE-SAVFRAME:0", 1)

    def update_frame(self):
        epics_put("XOMNYI-XEYE-ACQDONE:0", 0)
        # start live
        epics_put("XOMNYI-XEYE-ACQ:0", 1)
        # wait for start live
        while epics_get("XOMNYI-XEYE-ACQDONE:0") == 0:
            time.sleep(0.5)
            print("waiting for live view to start...")
        fshopen()

        epics_put("XOMNYI-XEYE-ACQDONE:0", 0)

        while epics_get("XOMNYI-XEYE-ACQDONE:0") == 0:
            print("waiting for new frame...")
            time.sleep(0.5)

        time.sleep(0.5)
        # stop live view
        epics_put("XOMNYI-XEYE-ACQ:0", 0)
        time.sleep(1)
        # fshclose
        print("got new frame")

    def tomo_rotate(self, val: float):
        # pylint: disable=undefined-variable
        umv(self.device_manager.devices.fsamroy, val)

    def get_tomo_angle(self):
        return self.device_manager.devices.fsamroy.readback.get()

    def update_fov(self, k: int):
        self._xray_fov_xy[0] = max(epics_get(f"XOMNYI-XEYE-XWIDTH_X:{k}"), self._xray_fov_xy[0])
        self._xray_fov_xy[1] = max(0, self._xray_fov_xy[0])

    @property
    def movement_buttons_enabled(self):
        return [epics_get("XOMNYI-XEYE-ENAMVX:0"), epics_get("XOMNYI-XEYE-ENAMVY:0")]

    @movement_buttons_enabled.setter
    def movement_buttons_enabled(self, enabled: bool):
        enabled = int(enabled)
        epics_put("XOMNYI-XEYE-ENAMVX:0", enabled)
        epics_put("XOMNYI-XEYE-ENAMVY:0", enabled)

    def send_message(self, msg: str):
        epics_put("XOMNYI-XEYE-MESSAGE:0.DESC", msg)

    def align(self):
        # reset shift xy and fov params
        self._reset_init_values()

        self.flomni.lights_off()

        self.tomo_rotate(0)
        epics_put("XOMNYI-XEYE-ANGLE:0", 0)

        self.flomni.feye_in()

        self.flomni.laser_tracker_on()

        self.flomni.rt_feedback_enable_with_reset()

        # disable movement buttons
        self.movement_buttons_enabled = False

        sample_name = self.flomni.sample_get_name(0)
        epics_put("XOMNYI-XEYE-SAMPLENAME:0.DESC", sample_name)

        # this makes sure we are in a defined state
        self.flomni.rt_feedback_disable()

        epics_put("XOMNYI-XEYE-PIXELSIZE:0", self.PIXEL_CALIBRATION)

        self.flomni.fosa_out()

        fsamx_in = self.flomni._get_user_param_safe("fsamx", "in")
        umv(dev.fsamx, fsamx_in - 0.25)

        self.flomni.ffzp_in()
        self.update_frame()

        # enable submit buttons
        self.movement_buttons_enabled = False
        epics_put("XOMNYI-XEYE-SUBMIT:0", 0)
        epics_put("XOMNYI-XEYE-STEP:0", 0)
        self.send_message("Submit center value of FZP.")

        k = 0
        while True:
            if epics_get("XOMNYI-XEYE-SUBMIT:0") == 1:
                val_x = epics_get(f"XOMNYI-XEYE-XVAL_X:{k}") / 2 * self.PIXEL_CALIBRATION  # in mm
                self.alignment_values[k] = val_x
                print(f"Clicked position {k}: x {self.alignment_values[k]}")
                rtx_position = dev.rtx.readback.get() / 1000
                print(f"Current rtx position {rtx_position}")
                self.alignment_values[k] -= rtx_position
                print(f"Corrected position {k}: x {self.alignment_values[k]}")

                if k == 0:  # received center value of FZP
                    self.send_message("please wait ...")
                    self.movement_buttons_enabled = False
                    epics_put("XOMNYI-XEYE-SUBMIT:0", -1)  # disable submit button

                    self.flomni.rt_feedback_disable()
                    fsamx_in = self.flomni._get_user_param_safe("fsamx", "in")
                    umv(dev.fsamx, fsamx_in)

                    self.flomni.foptics_out()

                    self.flomni.rt_feedback_disable()
                    umv(dev.fsamx, fsamx_in - 0.25)

                    self.update_frame()
                    epics_put("XOMNYI-XEYE-RECBG:0", 1)
                    while epics_get("XOMNYI-XEYE-RECBG:0") == 1:
                        time.sleep(0.5)
                        print("waiting for background frame...")

                    umv(dev.fsamx, fsamx_in)
                    time.sleep(0.5)
                    self.flomni.rt_feedback_enable_with_reset()

                    self.update_frame()
                    self.send_message("Adjust sample height and submit center")
                    epics_put("XOMNYI-XEYE-SUBMIT:0", 0)
                    self.movement_buttons_enabled = True

                elif 1 <= k < 5:  # received sample center value at samroy 0 ... 315
                    self.send_message("please wait ...")
                    epics_put("XOMNYI-XEYE-SUBMIT:0", -1)
                    self.movement_buttons_enabled = False

                    umv(dev.rtx, 0)
                    self.tomo_rotate(k * 45)
                    epics_put("XOMNYI-XEYE-ANGLE:0", self.get_tomo_angle())
                    self.update_frame()
                    self.send_message("Submit sample center")
                    epics_put("XOMNYI-XEYE-SUBMIT:0", 0)
                    epics_put("XOMNYI-XEYE-ENAMVX:0", 1)
                    self.update_fov(k)

                elif k == 5:  # received sample center value at samroy 270 and done
                    self.send_message("done...")
                    epics_put("XOMNYI-XEYE-SUBMIT:0", -1)  # disable submit button
                    self.movement_buttons_enabled = False
                    self.update_fov(k)
                    break

                k += 1
                epics_put("XOMNYI-XEYE-STEP:0", k)

            _xrayeyalignmvx = epics_get("XOMNYI-XEYE-MVX:0")
            if _xrayeyalignmvx != 0:
                umvr(dev.rtx, _xrayeyalignmvx)
                print(f"Current rtx position {dev.rtx.readback.get() / 1000}")
                epics_put("XOMNYI-XEYE-MVX:0", 0)
                if k > 0:
                    epics_put(f"XOMNYI-XEYE-STAGEPOSX:{k}", dev.rtx.readback.get() / 1000)
                time.sleep(3)
                self.update_frame()

            if k < 2:
                # allow movements, store movements to calculate center
                _xrayeyalignmvy = epics_get("XOMNYI-XEYE-MVY:0")
                if _xrayeyalignmvy != 0:
                    self.flomni.rt_feedback_disable()
                    umvr(dev.fsamy, _xrayeyalignmvy / 1000)
                    time.sleep(2)
                    epics_put("XOMNYI-XEYE-MVY:0", 0)
                    self.flomni.rt_feedback_enable_with_reset()
                    self.update_frame()
            time.sleep(0.2)

        self.write_output()
        fovx = self._xray_fov_xy[0] * self.PIXEL_CALIBRATION * 1000 / 2
        fovy = self._xray_fov_xy[1] * self.PIXEL_CALIBRATION * 1000 / 2

        self.tomo_rotate(0)

        umv(dev.rtx, 0)

        # free camera
        epics_put("XOMNYI-XEYE-ACQ:0", 2)

        print(
            f"The largest field of view from the xrayeyealign was \nfovx = {fovx:.0f} microns, fovy"
            f" = {fovy:.0f} microns"
        )
        print("Use the matlab routine to FIT the current alignment...")

        print("Then LOAD ALIGNMENT PARAMETERS by running flomni.read_alignment_offset()\n")

    def write_output(self):
        file = os.path.expanduser("~/Data10/specES1/internal/xrayeye_alignmentvalues")
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as alignment_values_file:
            alignment_values_file.write("angle\thorizontal\n")
            for k in range(1, 6):
                fovx_offset = self.alignment_values[0] - self.alignment_values[k]
                print(f"Writing to file new alignment: number {k}, value x {fovx_offset}")
                alignment_values_file.write(f"{(k-1)*45}\t{fovx_offset*1000}\n")
