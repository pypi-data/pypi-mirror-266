import builtins
import datetime
import os
import subprocess
import time
from pathlib import Path

import numpy as np
from typeguard import typechecked

from bec_client.plugins.cSAXS import cSAXSBeamlineChecks
from bec_client.plugins.flomni.flomni_optics_mixin import FlomniOpticsMixin
from bec_client.plugins.flomni.x_ray_eye_align import XrayEyeAlign
from bec_lib import bec_logger
from bec_lib.alarm_handler import AlarmBase
from bec_lib.pdf_writer import PDFWriter

logger = bec_logger.logger

if builtins.__dict__.get("bec") is not None:
    bec = builtins.__dict__.get("bec")
    dev = builtins.__dict__.get("dev")
    umv = builtins.__dict__.get("umv")
    umvr = builtins.__dict__.get("umvr")


class FlomniInitError(Exception):
    pass


class FlomniError(Exception):
    pass


class FlomniInitStagesMixin:

    def flomni_init_stages(self):

        user_input = input("Starting initialization of flOMNI stages. OK? [y/n]")
        if user_input == "y":
            print("staring...")
        else:
            return

        if self.check_all_axes_of_fomni_referenced():
            user_input = input("Continue anyways? [y/n]")
            if user_input == "y":
                print("ok then...")
            else:
                return

        print("Starting to drive ftransy to +y limit")
        self.drive_axis_to_limit(dev.ftransy, "forward")
        dev.ftransy.limits = [-100, 0]
        print("done")

        print("Starting to drive ftransz to -z limit")
        self.drive_axis_to_limit(dev.ftransz, "reverse")
        dev.ftransz.limits = [0, 145]
        print("done")

        print("Starting to drive ftransx to -x limit")
        self.drive_axis_to_limit(dev.ftransx, "reverse")
        dev.ftransx.limits = [0, 50]
        print("done")

        print("Starting to drive feyey to +y limit")
        self.drive_axis_to_limit(dev.feyey, "forward")
        dev.feyey.limits = [-1, -10]
        print("done")

        print("Starting to drive feyex to +x limit")
        self.drive_axis_to_limit(dev.feyex, "forward")
        dev.feyex.limits = [-30, -1]
        print("done")

        user_input = input(
            "Init of foptz. Can the stage move to the upstream limit without collision? [y/n]"
        )
        if user_input == "y":
            print("good then")
        else:
            return

        print("Starting to drive foptz to -z limit")
        self.drive_axis_to_limit(dev.foptz, "reverse")
        dev.foptz.limits = [0, 27]
        print("done")

        print("Init of Smaract stages")
        ## smaract stages
        max_repeat = 100
        repeat = 0
        axis_id_fosaz = dev.fosaz._config["deviceConfig"].get("axis_Id")
        axis_id_numeric_fosaz = self.axis_id_to_numeric(axis_id_fosaz)
        print("Moving fosaz upstream into the light curtain")
        while True:
            curtain_is_triggered = dev.foptz.controller.fosaz_light_curtain_is_triggered()
            if curtain_is_triggered:
                break
            if repeat > max_repeat:
                raise FlomniInitError("Failed to initialize fosaz within 100 repeats.")
            dev.fosaz.controller.move_open_loop_steps(
                axis_id_numeric_fosaz, -500, amplitude=4000, frequency=2000
            )
            time.sleep(1)
            repeat += 1

        print("Finding index of fosax, fosay, fosaz")
        for ii in range(3):
            dev.fosax.controller.find_reference_mark(ii, 0, 1000, 1)
            time.sleep(1)

        dev.fosax.limits = [10.2, 10.6]
        dev.fosay.limits = [-3.1, -2.9]
        dev.fosaz.limits = [-6, -4]
        # dev.fosax.controller.describe()

        print("Moving fosa stages to approximate beam positions")
        umv(dev.fosaz, -5)
        umv(dev.fosax, 10.4, dev.fosay, -3)
        print("done")

        print("Moving fheater to +y limit")
        self.drive_axis_to_limit(dev.fheater, "reverse")
        dev.fheater.limits = [-15, 0]
        print("done")

        print("Moving fsamy to -y limit")
        self.drive_axis_to_limit(dev.fsamy, "reverse")
        dev.fsamy.limits = [2, 3.1]
        print("done")

        user_input = input(
            "Init of tracking stages. Did you remove the outer laser flight tubes? [y/n]"
        )
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            return

        print("Moving tracky to -y limit")
        self.drive_axis_to_limit(dev.ftracky, "reverse")
        dev.ftracky.limits = [2.2, 2.8]
        print("done")

        print("Moving ftrackz to -z limit")
        self.drive_axis_to_limit(dev.ftrackz, "reverse")
        dev.ftrackz.limits = [4.5, 5.5]
        print("done")

        user_input = input("Init of sample stage. Is the piezo at about 0 deg? [y/n]")
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            return

        print("Moving fsamx to +x limit")
        self.drive_axis_to_limit(dev.fsamx, "forward")
        dev.fsamx.limits = [-162, 0]
        print("done")

        print("Moving ftray to IN limit")
        self.drive_axis_to_limit(dev.ftray, "reverse")
        dev.ftray.limits = [-200, 0]
        print("done")

        print("Initializing UPR stage.")
        user_input = input(
            "To ensure that the end switches work, please check that they are currently not pushed."
            " Is everything okay? [y/n]"
        )
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            return

        while True:
            low_limit, high_limit = dev.fsamroy.controller.get_motor_limit_switch("A")
            if not high_limit:
                print("Please push limit switch to the left.")
                time.sleep(1)
                continue
            break

        while True:
            low_limit, high_limit = dev.fsamroy.controller.get_motor_limit_switch("A")
            if not low_limit:
                print("Please push limit switch to the right.")
                time.sleep(1)
                continue
            break
        user_input = input("Shall I start the index search? [y/n]")
        if user_input == "y":
            print("good then. Starting index search.")
        else:
            print("Stopping.")
            return
        if dev.fsamroy.controller.is_motor_on("A"):
            raise FlomniInitError("fsamroy should be off. Something is wrong. Mirko... help!")
        dev.fsamroy.controller.socket_put_confirmed("XQ#MOTON")
        dev.fsamroy.enabled = False
        time.sleep(5)
        dev.fsamroy.enabled = True
        time.sleep(2)
        dev.fsamroy.controller.socket_put_confirmed("XQ#REFAX")
        while not dev.fsamroy.controller.all_axes_referenced():
            print("Waiting for fsamroy to be referenced.")
            time.sleep(1)
        dev.fsamroy.limits = [-5, 365]
        print("done")

        user_input = input(
            "Init of foptx. Can the stage move to the positive limit without collision? Attention:"
            " tracker flight tube! [y/n]"
        )
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            return

        print("Moving foptx to +x limit")
        self.drive_axis_to_limit(dev.foptx, "forward")
        dev.foptx.limits = [-16, -14]
        print("done")

        axis_id_fopty = dev.fopty._config["deviceConfig"].get("axis_Id")

        while True:
            low_limit, high_limit = dev.fopty.controller.get_motor_limit_switch(axis_id_fopty)
            if not low_limit:
                print(
                    "To ensure that the fopty end switch works, please push it down and hold it for"
                    " about 1 second."
                )
                time.sleep(1)
                continue
            break

        user_input = input("Start limit switch search of fopty? [y/n]")
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            return

        print("Moving fopty to -y limit")
        self.drive_axis_to_limit(dev.fopty, "reverse")
        dev.fopty.limits = [0, 4]
        print("done")

        dev.fsamx.controller.galil_show_all()

        self.set_limits()

        self._align_setup()

    def check_all_axes_of_fomni_referenced(self) -> bool:
        if (
            dev.fosax.controller.axis_is_referenced(0)
            & dev.fosax.controller.axis_is_referenced(1)
            & dev.fosax.controller.axis_is_referenced(2)
            & dev.fsamx.controller.all_axes_referenced()
            & dev.feyex.controller.all_axes_referenced()
            & dev.fsamroy.controller.all_axes_referenced()
            & dev.fsamroy.controller.is_motor_on("A")
        ):
            print("All axes of flomni are referenced.")
            return True
        else:
            return False

    def set_limits(self):
        user_input = input("Set default limits for flOMNI? [y/n]")
        if user_input == "y":
            print("setting limits...")
        else:
            print("Stopping.")
            return
        dev.ftransy.limits = [-100, 0]
        dev.ftransz.limits = [0, 145]
        dev.ftransx.limits = [0, 50]
        dev.ftray.limits = [-200, 0]
        dev.fsamy.limits = [2, 3.5]
        dev.foptz.limits = [22.5, 28]
        dev.foptx.limits = [-17, -12]
        dev.fheater.limits = [-15, 0]
        dev.feyex.limits = [-18, -1]
        dev.feyey.limits = [-12, -1]
        dev.fopty.limits = [0, 4]
        dev.fosax.limits = [7, 10]
        dev.fosay.limits = [-4.2, 7]
        dev.fosaz.limits = [-6.5, 7.5]
        # dev.rtx.limits = [-220, 220]
        # dev.rty.limits = [-180, 180]
        # dev.rtz.limits = [-220, 220]
        dev.fsamroy.limits = [-5, 365]
        dev.ftracky.limits = [2.2, 2.8]
        dev.ftrackz.limits = [4.5, 5.5]

    def _align_setup(self):
        user_input = input("Start moving stages to default initial positions? [y/n]")
        if user_input == "y":
            print("Start moving stages...")
        else:
            print("Stopping.")
            return
        # positions for optics out and 50 mm distance to sample
        umv(dev.ftrackz, 4.73, dev.ftracky, 2.5170, dev.foptx, -14.3, dev.fopty, 3.87)

        # the fopty 3.87 should put us in place for a lower FZP on the lower FZP chip

        umv(dev.foptz, 23)

        flomni_samx_in = dev.fsamx.user_parameter.get("in")
        if flomni_samx_in is None:
            raise FlomniInitError(
                "Could not find a fsamx in position. Please check your device config."
            )
        umv(dev.fsamx, flomni_samx_in)
        flomni_samy_in = dev.fsamy.user_parameter.get("in")
        if flomni_samy_in is None:
            raise FlomniInitError(
                "Could not find a fsamy in position. Please check your device config."
            )
        umv(dev.fsamy, flomni_samy_in)

        # after init reduce vertical stage speed
        dev.fsamy.controller.socket_put_confirmed("axspeed[5]=20000")

        umv(dev.feyey, -8)


class FlomniSampleTransferMixin:
    def ensure_osa_back(self):
        dev.fosaz.limits = [-12.6, -12.4]
        umv(dev.fosaz, -12.5)

        curtain_is_triggered = dev.fheater.controller.fosaz_light_curtain_is_triggered()
        if not curtain_is_triggered:
            raise FlomniError("Fosaz did not reach light curtain")

    def move_fheater_up(self):
        self.ensure_fheater_up()

    def ensure_fheater_up(self):
        axis_id = dev.fheater._config["deviceConfig"].get("axis_Id")
        axis_id_numeric = self.axis_id_to_numeric(axis_id)
        low, high = dev.fheater.controller.get_motor_limit_switch(axis_id)
        if high:
            raise FlomniError("fheater in high limit. How did we get here?? Aborting.")
        if not low:
            self.ensure_osa_back()
            if dev.fheater.readback.get() < -0.2:
                umv(dev.fheater, -0.2)

            dev.fheater.controller.drive_axis_to_limit(axis_id_numeric, "reverse")

    def move_fheater_down(self):
        axis_id = dev.fheater._config["deviceConfig"].get("axis_Id")
        axis_id_numeric = self.axis_id_to_numeric(axis_id)
        self.ensure_osa_back()

        fsamx_in = dev.fsamx.user_parameter.get("in")
        if not np.isclose(dev.fsamx.readback.get(), fsamx_in, 0.2):
            raise FlomniError("fsamx not in position. Aborting.")

        fheater_in = dev.fheater.user_parameter.get("in")
        umv(dev.fheater, fheater_in)

    def ensure_gripper_up(self):
        axis_id = dev.ftransy._config["deviceConfig"].get("axis_Id")
        axis_id_numeric = self.axis_id_to_numeric(axis_id)
        low, high = dev.ftransy.controller.get_motor_limit_switch(axis_id)
        if low:
            raise FlomniError("Ftransy in low limit. How did we get here?? Aborting.")

        if high:
            return

        if dev.ftransy.readback.get() < -0.5:
            umv(dev.ftransy, -0.5)
        dev.ftransy.controller.drive_axis_to_limit(axis_id_numeric, "forward")

    def check_tray_in(self):
        axis_id = dev.ftray._config["deviceConfig"].get("axis_Id")
        low, high = dev.ftray.controller.get_motor_limit_switch(axis_id)
        if high:
            raise FlomniError("Ftray is in the 'OUT' position. Aborting.")

        if not low:
            raise FlomniError("Ftray is not at the 'IN' position. Aborting.")

    def ftransfer_flomni_stage_in(self):
        sample_in_position = bool(float(dev.flomni_samples.sample_placed.sample0.get()))
        if not sample_in_position:
            raise FlomniError("There is no sample in the sample stage. Aborting.")
        self.reset_correction()
        dev.rtx.controller.feedback_disable()
        self.ensure_fheater_up()
        self.ensure_gripper_up()
        self.check_tray_in()

        fsamx_in = dev.fsamx.user_parameter.get("in")
        umv(dev.fsamx, fsamx_in)
        dev.fsamx.limits = [fsamx_in - 0.4, fsamx_in + 0.4]

    def laser_tracker_show_all(self):
        dev.rtx.controller.laser_tracker_show_all()

    def laser_tracker_on(self):
        dev.rtx.controller.laser_tracker_on()

    def laser_tracker_off(self):
        dev.rtx.controller.laser_tracker_off()

    def show_signal_strength_interferometer(self):
        dev.rtx.controller.show_signal_strength_interferometer()

    def rt_feedback_disable(self):
        self.device_manager.devices.rtx.controller.feedback_disable()

    def rt_feedback_enable_with_reset(self):
        self.device_manager.devices.rtx.controller.feedback_enable_with_reset()
        self.rt_feedback_status()

    def rt_feedback_enable_without_reset(self):
        self.device_manager.devices.rtx.controller.feedback_enable_without_reset()
        self.rt_feedback_status()

    def rt_feedback_status(self):
        feedback_status = self.device_manager.devices.rtx.controller.feedback_is_running()
        if feedback_status == True:
            print("The rt feedback is \x1b[92mrunning\x1b[0m.")
        else:
            print("The rt feedback is \x1b[91mNOT\x1b[0m running.")

    def lights_off(self):
        self.device_manager.devices.fsamx.controller.lights_off()

    def lights_on(self):
        self.device_manager.devices.fsamx.controller.lights_on()

    def ftransfer_flomni_stage_out(self):
        target_pos = -162
        if np.isclose(dev.fsamx.readback.get(), target_pos, 0.01):
            return

        umv(dev.fsamroy, 0)

        self.rt_feedback_disable()

        self.ensure_fheater_up()

        self.ensure_gripper_up()

        self.check_tray_in()

        self.laser_tracker_off()
        time.sleep(0.05)
        fsamy_in = dev.fsamy.user_parameter.get("in")
        if fsamy_in is None:
            raise FlomniError(
                "Could not find an 'IN' position for fsamy. Please check your config."
            )
        umv(dev.fsamy, fsamy_in)
        time.sleep(0.05)
        self.laser_tracker_on()
        time.sleep(0.05)
        self.laser_tracker_off()
        time.sleep(0.05)

        self.drive_axis_to_limit(dev.fsamx, "forward")
        dev.fsamx.limits = [-162, 0]
        dev.fsamx.controller.socket_put_confirmed("axspeed[4]=25*stppermm[4]")

        umv(dev.fsamx, target_pos)

    def check_sensor_connected(self):
        sensor_voltage_target = dev.ftransy.user_parameter.get("sensor_voltage")
        sensor_voltage = float(dev.ftransy.controller.socket_put_and_receive("MG@AN[1]").strip())

        if not np.isclose(sensor_voltage, sensor_voltage_target, 0.5):
            raise FlomniError(f"Sensor voltage is {sensor_voltage}, indicates an error. Aborting.")

    def ftransfer_get_sample(self, position: int):
        self.check_position_is_valid(position)

        self.check_tray_in()
        self.check_sensor_connected()

        sample_in_gripper = bool(float(dev.flomni_samples.sample_in_gripper.get()))
        if sample_in_gripper:
            raise FlomniError(
                "The gripper does carry a sample. Cannot proceed getting another sample."
            )

        sample_signal = getattr(dev.flomni_samples.sample_placed, f"sample{position}")
        sample_in_position = bool(float(sample_signal.get()))
        if not sample_in_position:
            raise FlomniError(f"The planned pick position [{position}] does not have a sample.")

        user_input = input(
            "Please confirm that there is currently no sample in the gripper. It would be dropped!"
            " [y/n]"
        )
        if user_input == "y":
            print("good then")
        else:
            print("Stopping.")
            raise FlomniError("The sample transfer was manually aborted.")

        self.ftransfer_gripper_move(position)

        self.ftransfer_controller_enable_mount_mode()
        if position == 0:
            sample_height = -45 + dev.fsamy.user_parameter.get("in")

        else:
            sample_height = -17.5
        dev.ftransy.controller.socket_put_confirmed(f"getaprch={sample_height:.1f}")
        dev.ftransy.controller.socket_put_confirmed("XQ#GRGET,3")

        print("The unmount process started.")

        time.sleep(1)
        while True:
            in_progress = bool(
                float(dev.ftransy.controller.socket_put_and_receive("MG mntprgs").strip())
            )
            if not in_progress:
                break
            self.ftransfer_confirm()
            time.sleep(1)
        self.ftransfer_controller_disable_mount_mode()
        self.ensure_gripper_up()

        signal_name = getattr(dev.flomni_samples.sample_names, f"sample{position}")
        self.flomni_modify_storage_non_interactive(100, 1, signal_name.get())
        self.flomni_modify_storage_non_interactive(position, 0, "-")

    def ftransfer_show_all(self):
        dev.flomni_samples.show_all()

    def ftransfer_put_sample(self, position: int):
        self.check_position_is_valid(position)

        self.check_tray_in()
        self.check_sensor_connected()

        sample_in_gripper = bool(float(dev.flomni_samples.sample_in_gripper.get()))
        if not sample_in_gripper:
            raise FlomniError("The gripper does not carry a sample.")

        sample_signal = getattr(dev.flomni_samples.sample_placed, f"sample{position}")
        sample_in_position = bool(float(sample_signal.get()))
        if sample_in_position:
            raise FlomniError(f"The planned put position [{position}] already has a sample.")

        self.ftransfer_gripper_move(position)

        self.ftransfer_controller_enable_mount_mode()
        if position == 0:
            sample_height = -45 + dev.fsamy.user_parameter.get("in")

        else:
            sample_height = -17.5
        dev.ftransy.controller.socket_put_confirmed(f"mntaprch={sample_height:.1f}")
        dev.ftransy.controller.socket_put_confirmed("XQ#GRPUT,3")

        print("The mount process started.")

        time.sleep(1)
        while True:
            in_progress = bool(
                float(dev.ftransy.controller.socket_put_and_receive("MG mntprgs").strip())
            )
            if not in_progress:
                break
            self.ftransfer_confirm()
            time.sleep(1)
        self.ftransfer_controller_disable_mount_mode()
        self.ensure_gripper_up()

        sample_name = dev.flomni_samples.sample_in_gripper.get()
        self.flomni_modify_storage_non_interactive(100, 0, "-")
        self.flomni_modify_storage_non_interactive(position, 1, sample_name)

        # TODO: flomni_stage_in if position == 0
        # bec.queue.next_dataset_number += 1

    def sample_get_name(self, position: int = 0) -> str:
        """
        Get the name of the sample currently in the given position.
        """
        signal_name = getattr(dev.flomni_samples.sample_names, f"sample{position}")
        return signal_name.get()

    def ftransfer_sample_change(self, new_sample_position: int):
        self.check_tray_in()
        sample_in_gripper = dev.flomni_samples.sample_in_gripper.get()
        if sample_in_gripper:
            raise FlomniError("There is already a sample in the gripper. Aborting.")

        self.check_position_is_valid(new_sample_position)

        sample_placed = getattr(
            dev.flomni_samples.sample_placed, f"sample{new_sample_position}"
        ).get()
        if not sample_placed:
            raise FlomniError(
                f"There is currently no sample in position [{new_sample_position}]. Aborting."
            )

        sample_in_sample_stage = dev.flomni_samples.sample_placed.sample0.get()
        if sample_in_sample_stage:
            # find a new home for the sample...
            empty_slots = []
            for name, val in dev.flomni_samples.read().items():
                if "flomni_samples_sample_placed_sample" not in name:
                    continue
                if val.get("value") == 0:
                    empty_slots.append(int(name.split("flomni_samples_sample_placed_sample")[1]))
            if not empty_slots:
                raise FlomniError("There are no empty slots available. Aborting.")

            print(f"The following slots are empty: {empty_slots}.")

            while True:
                user_input = input(f"Where shall I put the sample? Default: [{empty_slots[0]}]")
                try:
                    user_input = int(user_input)
                    if user_input not in empty_slots:
                        raise ValueError
                    break
                except ValueError:
                    print("Please specify a valid number.")
                    continue

            self.check_position_is_valid(user_input)

            self.ftransfer_get_sample(0)
            self.ftransfer_put_sample(user_input)

        self.ftransfer_get_sample(new_sample_position)
        self.ftransfer_put_sample(0)

    def ftransfer_modify_storage(self, position: int, used: int):
        if used:
            name = input("What's the name of this sample? ")
        else:
            name = "-"
        self.flomni_modify_storage_non_interactive(position, used, name)

    def flomni_modify_storage_non_interactive(self, position: int, used: int, name: str):
        if position == 100:
            dev.flomni_samples.sample_in_gripper.set(used)
            dev.flomni_samples.sample_in_gripper_name.set(name)
        else:
            signal = getattr(dev.flomni_samples.sample_placed, f"sample{position}")
            signal.set(used)
            signal_name = getattr(dev.flomni_samples.sample_names, f"sample{position}")
            signal_name.set(name)

    def check_position_is_valid(self, position: int):
        if 0 <= position < 21:
            return
        raise FlomniError(
            f"The given position number [{position}] is not in the valid range of 0-21. "
        )

    def ftransfer_controller_enable_mount_mode(self):
        dev.ftransy.controller.socket_put_confirmed("XQ#MNTMODE")
        time.sleep(0.5)
        if not self.ftransfer_controller_in_mount_mode():
            raise FlomniError("System not switched to mount mode. Aborting.")

    def ftransfer_controller_disable_mount_mode(self):
        dev.ftransy.controller.socket_put_confirmed("XQ#POSMODE")
        time.sleep(0.5)
        if self.ftransfer_controller_in_mount_mode():
            raise FlomniError("System is still in mount mode. Aborting.")

    def ftransfer_controller_in_mount_mode(self) -> bool:
        in_mount_mode = bool(
            float(dev.ftransy.controller.socket_put_and_receive("MG mntmod").strip())
        )
        return in_mount_mode

    def ftransfer_confirm(self):
        confirm = int(float(dev.ftransy.controller.socket_put_and_receive("MG confirm").strip()))

        if confirm != -1:
            return

        user_input = input("All OK? Continue? [y/n]")
        if user_input == "y":
            print("good then")
            dev.ftransy.controller.socket_put_confirmed("confirm=1")
        else:
            print("Stopping.")
            return

    def ftransfer_gripper_is_open(self) -> bool:
        status = bool(float(dev.ftransy.controller.socket_put_and_receive("MG @OUT[9]").strip()))
        return status

    def ftransfer_gripper_open(self):
        sample_in_gripper = dev.flomni_samples.sample_in_gripper.get()
        if sample_in_gripper:
            raise FlomniError(
                "Cannot open gripper. There is still a sample in the gripper! Aborting."
            )
        if not self.ftransfer_gripper_is_open():
            dev.ftransy.controller.socket_put_confirmed("XQ#GROPEN,4")

    def ftransfer_gripper_close(self):
        if self.ftransfer_gripper_is_open():
            dev.ftransy.controller.socket_put_confirmed("XQ#GRCLOS,4")

    def ftransfer_gripper_move(self, position: int):
        self.check_position_is_valid(position)

        self._ftransfer_shiftx = -0.2
        self._ftransfer_shiftz = -0.5

        fsamx_pos = dev.fsamx.readback.get()
        if position == 0 and fsamx_pos > -160:
            user_input = input(
                "May the flomni stage be moved out for the sample change? Feedback will be disabled"
                " and alignment will be lost! [y/n]"
            )
            if user_input == "y":
                print("good then")
                self.ftransfer_flomni_stage_out()
            else:
                print("Stopping.")
                return

        self.ensure_gripper_up()
        self.check_tray_in()

        if position == 0:
            umv(dev.ftransx, 10.715 + 0.2, dev.ftransz, 3.5950)
        if position == 1:
            umv(
                dev.ftransx,
                41.900 + self._ftransfer_shiftx,
                dev.ftransz,
                74.7500 + self._ftransfer_shiftz,
            )
        if position == 2:
            umv(
                dev.ftransx,
                31.900 + self._ftransfer_shiftx,
                dev.ftransz,
                74.7625 + self._ftransfer_shiftz,
            )
        if position == 3:
            umv(
                dev.ftransx,
                21.900 + self._ftransfer_shiftx,
                dev.ftransz,
                74.7750 + self._ftransfer_shiftz,
            )
        if position == 4:
            umv(
                dev.ftransx,
                11.900 + self._ftransfer_shiftx,
                dev.ftransz,
                74.7875 + self._ftransfer_shiftz,
            )
        if position == 5:
            umv(
                dev.ftransx,
                1.9000 + self._ftransfer_shiftx,
                dev.ftransz,
                74.8000 + self._ftransfer_shiftz,
            )
        if position == 6:
            umv(
                dev.ftransx,
                41.900 + self._ftransfer_shiftx,
                dev.ftransz,
                89.7500 + self._ftransfer_shiftz,
            )
        if position == 7:
            umv(
                dev.ftransx,
                31.900 + self._ftransfer_shiftx,
                dev.ftransz,
                89.7625 + self._ftransfer_shiftz,
            )
        if position == 8:
            umv(
                dev.ftransx,
                21.900 + self._ftransfer_shiftx,
                dev.ftransz,
                89.7750 + self._ftransfer_shiftz,
            )
        if position == 9:
            umv(
                dev.ftransx,
                11.900 + self._ftransfer_shiftx,
                dev.ftransz,
                89.7875 + self._ftransfer_shiftz,
            )
        if position == 10:
            umv(
                dev.ftransx,
                1.900 + self._ftransfer_shiftx,
                dev.ftransz,
                89.8000 + self._ftransfer_shiftz,
            )
        if position == 11:
            umv(
                dev.ftransx,
                41.95 + self._ftransfer_shiftx,
                dev.ftransz,
                124.75 + self._ftransfer_shiftz,
            )
        if position == 12:
            umv(
                dev.ftransx,
                31.95 + self._ftransfer_shiftx,
                dev.ftransz,
                124.7625 + self._ftransfer_shiftz,
            )
        if position == 13:
            umv(
                dev.ftransx,
                21.95 + self._ftransfer_shiftx,
                dev.ftransz,
                124.7750 + self._ftransfer_shiftz,
            )
        if position == 14:
            umv(
                dev.ftransx,
                11.95 + self._ftransfer_shiftx,
                dev.ftransz,
                124.7875 + self._ftransfer_shiftz,
            )
        if position == 15:
            umv(
                dev.ftransx,
                1.95 + self._ftransfer_shiftx,
                dev.ftransz,
                124.8000 + self._ftransfer_shiftz,
            )
        if position == 16:
            umv(
                dev.ftransx,
                41.95 + self._ftransfer_shiftx,
                dev.ftransz,
                139.7500 + self._ftransfer_shiftz,
            )
        if position == 17:
            umv(
                dev.ftransx,
                31.95 + self._ftransfer_shiftx,
                dev.ftransz,
                139.7625 + self._ftransfer_shiftz,
            )
        if position == 18:
            umv(
                dev.ftransx,
                21.95 + self._ftransfer_shiftx,
                dev.ftransz,
                139.7750 + self._ftransfer_shiftz,
            )
        if position == 19:
            umv(
                dev.ftransx,
                11.95 + self._ftransfer_shiftx,
                dev.ftransz,
                139.7875 + self._ftransfer_shiftz,
            )
        if position == 20:
            umv(
                dev.ftransx,
                1.95 + self._ftransfer_shiftx,
                dev.ftransz,
                139.8000 + self._ftransfer_shiftz,
            )


class FlomniAlignmentMixin:
    default_correction_file = "correction_flomni_20210300_360deg.txt"

    def reset_correction(self, use_default_correction=True):
        """
        Reset the correction to the default values.
        If use_default_correction is False, the correction will be set to empty values.
        Otherwise the default values will be loaded.

        Args:
            use_default_correction (bool, optional): If set to true, a call reset the correction to the default values. Defaults to True.
        """
        self.corr_pos_y = []
        self.corr_angle_y = []
        self.corr_pos_y_2 = []
        self.corr_angle_y_2 = []

        if use_default_correction:
            try:
                self.read_additional_correction_y(self.default_correction_file)
                logger.info(f"Applying default correction from {self.default_correction_file}")
            except FileNotFoundError:
                logger.warning(
                    f"Could not find default correction file {self.default_correction_file}."
                )
                logger.warning("Not applying any correction.")

    def reset_tomo_alignment_fit(self):
        self.client.delete_global_var("tomo_alignment_fit")

    def read_alignment_offset(self, dir_path=os.path.expanduser("~/Data10/specES1/internal/")):
        """
        Read the alignment offset from the given directory and set the global parameter
        tomo_alignment_fit.

        Args:
            dir_path (str, optional): The directory to read the alignment offset from. Defaults to os.path.expanduser("~/Data10/specES1/internal/").
        """
        tomo_alignment_fit = np.zeros((2, 5))
        with open(os.path.join(dir_path, "ptychotomoalign_Ax.txt"), "r") as file:
            tomo_alignment_fit[0][0] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Bx.txt"), "r") as file:
            tomo_alignment_fit[0][1] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Cx.txt"), "r") as file:
            tomo_alignment_fit[0][2] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Ay.txt"), "r") as file:
            tomo_alignment_fit[1][0] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_By.txt"), "r") as file:
            tomo_alignment_fit[1][1] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Cy.txt"), "r") as file:
            tomo_alignment_fit[1][2] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Ay3.txt"), "r") as file:
            tomo_alignment_fit[1][3] = file.readline()

        with open(os.path.join(dir_path, "ptychotomoalign_Cy3.txt"), "r") as file:
            tomo_alignment_fit[1][4] = file.readline()

        self.client.set_global_var("tomo_alignment_fit", tomo_alignment_fit.tolist())
        # x amp, phase, offset, y amp, phase, offset, 3rd order amp, 3rd order phase
        #  0 0    0 1    0 2     1 0    1 1    1 2       1 3           1 4

        print("New alignment parameters loaded")
        print(
            f"X Amplitude {tomo_alignment_fit[0][0]}, "
            f"X Phase {tomo_alignment_fit[0][1]}, "
            f"X Offset {tomo_alignment_fit[0][2]}, "
            f"Y Amplitude {tomo_alignment_fit[1][0]}, "
            f"Y Phase {tomo_alignment_fit[1][1]}, "
            f"Y Offset {tomo_alignment_fit[1][2]}, "
            f"Y 3rd Order Amplitude {tomo_alignment_fit[1][3]}, "
            f"Y 3rd Order Phase {tomo_alignment_fit[1][4]}."
        )

    def get_alignment_offset(self, angle: float):
        """
        Compute the alignment offset for the given angle.

        Args:
            angle (float): The angle to compute the alignment offset for.

        Returns:
            tuple: The alignment offset in x, y and z direction.
        """
        tomo_alignment_fit = self.client.get_global_var("tomo_alignment_fit")
        if tomo_alignment_fit is None:
            print("Not applying any alignment offsets. No tomo alignment fit data available.\n")
            return (0, 0, 0)

        # x amp, phase, offset, y amp, phase, offset
        #  0 0    0 1    0 2     1 0    1 1    1 2
        correction_x = (
            tomo_alignment_fit[0][0] * np.sin(np.radians(angle) + tomo_alignment_fit[0][1])
            + tomo_alignment_fit[0][2]
        )
        correction_y = (
            tomo_alignment_fit[1][0] * np.sin(np.radians(angle) + tomo_alignment_fit[1][1])
            + tomo_alignment_fit[1][2]
            + tomo_alignment_fit[1][3] * np.sin(3 * np.radians(angle) + tomo_alignment_fit[1][4])
        )
        correction_z = tomo_alignment_fit[0][0] * np.sin(
            np.radians(angle + 90) + tomo_alignment_fit[0][1]
        )

        print(
            f"Alignment offset x {correction_x}, y {correction_y}, z {correction_z} for angle"
            f" {angle}\n"
        )
        return (correction_x, correction_y, correction_z)

    def _read_correction_file(self, correction_file: str):
        with open(correction_file, "r") as f:
            num_elements = f.readline()
            int_num_elements = int(num_elements.split(" ")[2])
            corr_pos = []
            corr_angle = []
            for j in range(int_num_elements * 2):
                line = f.readline()
                value = line.split(" ")[2]
                name = line.split(" ")[0].split("[")[0]
                if name == "corr_pos":
                    corr_pos.append(float(value) / 1000)
                elif name == "corr_angle":
                    corr_angle.append(float(value))
        print(
            f"Loading default mirror correction from file {correction_file} containing {int_num_elements} elements."
        )
        return corr_pos, corr_angle

    def read_additional_correction_y(self, correction_file: str):
        self.corr_pos_y, self.corr_angle_y = self._read_correction_file(correction_file)

    def read_additional_correction_y_2(self, correction_file: str):
        self.corr_pos_y_2, self.corr_angle_y_2 = self._read_correction_file(correction_file)

    def compute_additional_correction_y(self, angle):
        return self._compute_additional_correction(angle, iteration=1)

    def compute_additional_correction_y_2(self, angle):
        return self._compute_additional_correction(angle, iteration=2)

    def _compute_additional_correction(self, angle, iteration=1):
        if iteration == 1:
            corr_pos = self.corr_pos_y
            corr_angle = self.corr_angle_y
        elif iteration == 2:
            corr_pos = self.corr_pos_y_2
            corr_angle = self.corr_angle_y_2
        if not corr_pos:
            print("Not applying any additional correction. No data available.\n")
            return 0

        # find index of closest angle
        for j, _ in enumerate(corr_pos):
            newangledelta = np.fabs(corr_angle[j] - angle)
            if j == 0:
                angledelta = newangledelta
                additional_correction_shift = corr_pos[j]
                continue

            if newangledelta < angledelta:
                additional_correction_shift = corr_pos[j]
                angledelta = newangledelta

        if additional_correction_shift == 0 and angle > corr_angle[-1]:
            additional_correction_shift = corr_pos[-1]
        print(f"Additional correction shift {iteration} in y: {additional_correction_shift}")
        return additional_correction_shift


class Flomni(
    FlomniInitStagesMixin,
    FlomniSampleTransferMixin,
    FlomniAlignmentMixin,
    FlomniOpticsMixin,
    cSAXSBeamlineChecks,
):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.device_manager = client.device_manager
        self.check_shutter = False
        self.check_light_available = False
        self.check_fofb = False
        self._check_msgs = []
        self.tomo_id = -1
        self.special_angles = []
        self.special_angle_repeats = 20
        self.special_angle_tolerance = 20
        self._current_special_angles = []
        self._beam_is_okay = True
        self._stop_beam_check_event = None
        self.beam_check_thread = None
        self.corr_pos_y = []
        self.corr_angle_y = []
        self.corr_pos_y_2 = []
        self.corr_angle_y_2 = []
        self.align = XrayEyeAlign(self.client, self)

    def start_x_ray_eye_alignment(self):
        user_input = input(
            "Starting Xrayeye alignment. Deleting any potential existing alignment for this sample. [Y/n]"
        )
        if user_input == "y" or user_input == "":
            self.align = XrayEyeAlign(self.client, self)
            try:
                self.align.align()
            except KeyboardInterrupt as exc:
                fsamx_in = self._get_user_param_safe(dev.fsamx, "in")
                if np.isclose(fsamx_in, dev.fsamx.readback.get(), 0.5):
                    print("Stopping alignment. Returning to fsamx in position.")
                    self.rt_feedback_disable()
                    umv(dev.fsamx, fsamx_in)
                raise exc

    def xrayeye_update_frame(self):
        self.align.update_frame()

    def xrayeye_alignment_start(self):
        self.start_x_ray_eye_alignment()

    def drive_axis_to_limit(self, device, direction):
        axis_id = device._config["deviceConfig"].get("axis_Id")
        axis_id_numeric = self.axis_id_to_numeric(axis_id)
        device.controller.drive_axis_to_limit(axis_id_numeric, direction)

    def axis_id_to_numeric(self, axis_id) -> int:
        return ord(axis_id.lower()) - 97

    def get_beamline_checks_enabled(self):
        print(
            f"Shutter: {self.check_shutter}\nFOFB: {self.check_fofb}\nLight available:"
            f" {self.check_light_available}"
        )

    @property
    def beamline_checks_enabled(self):
        return {
            "shutter": self.check_shutter,
            "fofb": self.check_fofb,
            "light available": self.check_light_available,
        }

    @beamline_checks_enabled.setter
    def beamline_checks_enabled(self, val: bool):
        self.check_shutter = val
        self.check_light_available = val
        self.check_fofb = val
        self.get_beamline_checks_enabled()

    def set_special_angles(self, angles: list, repeats: int = 20, tolerance: float = 0.5):
        """Set the special angles for a tomo

        Args:
            angles (list): List of special angles
            repeats (int, optional): Number of repeats at a special angle. Defaults to 20.
            tolerance (float, optional): Number of repeats at a special angle. Defaults to 0.5.

        """
        self.special_angles = angles
        self.special_angle_repeats = repeats
        self.special_angle_tolerance = tolerance

    def remove_special_angles(self):
        """Remove the special angles and set the number of repeats to 1"""
        self.special_angles = []
        self.special_angle_repeats = 1

    @property
    def tomo_shellstep(self):
        val = self.client.get_global_var("tomo_shellstep")
        if val is None:
            return 1
        return val

    @tomo_shellstep.setter
    def tomo_shellstep(self, val: float):
        self.client.set_global_var("tomo_shellstep", val)

    @property
    def tomo_countingtime(self):
        val = self.client.get_global_var("tomo_countingtime")
        if val is None:
            return 0.1
        return val

    @tomo_countingtime.setter
    def tomo_countingtime(self, val: float):
        self.client.set_global_var("tomo_countingtime", val)

    @property
    def manual_shift_y(self):
        val = self.client.get_global_var("manual_shift_y")
        if val is None:
            return 0.0
        return val

    @manual_shift_y.setter
    def manual_shift_y(self, val: float):
        self.client.set_global_var("manual_shift_y", val)

    @property
    def fovx(self):
        val = self.client.get_global_var("fovx")
        if val is None:
            return 20
        return val

    @fovx.setter
    def fovx(self, val: float):
        if val > 200:
            raise ValueError("FOV cannot be larger than 200 um.")
        self.client.set_global_var("fovx", val)

    @property
    def fovy(self):
        val = self.client.get_global_var("fovy")
        if val is None:
            return 20
        return val

    @fovy.setter
    def fovy(self, val: float):
        if val > 100:
            raise ValueError("FOV cannot be larger than 100 um.")
        self.client.set_global_var("fovy", val)

    @property
    def corridor_size(self):
        val = self.client.get_global_var("corridor_size")
        if val is None:
            val = -1
        return val

    @corridor_size.setter
    def corridor_size(self, val: float):
        self.client.set_global_var("corridor_size", val)

    @property
    def stitch_x(self):
        val = self.client.get_global_var("stitch_x")
        if val is None:
            return 0
        return val

    @stitch_x.setter
    @typechecked
    def stitch_x(self, val: int):
        self.client.set_global_var("stitch_x", val)

    @property
    def stitch_y(self):
        val = self.client.get_global_var("stitch_y")
        if val is None:
            return 0
        return val

    @stitch_y.setter
    @typechecked
    def stitch_y(self, val: int):
        self.client.set_global_var("stitch_y", val)

    @property
    def ptycho_reconstruct_foldername(self):
        val = self.client.get_global_var("ptycho_reconstruct_foldername")
        if val is None:
            return "ptycho_reconstruct"
        return val

    @ptycho_reconstruct_foldername.setter
    def ptycho_reconstruct_foldername(self, val: str):
        self.client.set_global_var("ptycho_reconstruct_foldername", val)

    @property
    def tomo_angle_stepsize(self):
        val = self.client.get_global_var("tomo_angle_stepsize")
        if val is None:
            return 10.0
        return val

    @tomo_angle_stepsize.setter
    def tomo_angle_stepsize(self, val: float):
        self.client.set_global_var("tomo_angle_stepsize", val)

    @property
    def tomo_stitch_overlap(self):
        val = self.client.get_global_var("tomo_stitch_overlap")
        if val is None:
            return 0.2
        return val

    @tomo_stitch_overlap.setter
    def tomo_stitch_overlap(self, val: float):
        self.client.set_global_var("tomo_stitch_overlap", val)

    @property
    def sample_name(self):
        return self.sample_get_name(0)

    def write_to_spec_log(self, content):
        try:
            with open(
                os.path.expanduser(
                    "~/Data10/specES1/log-files/specES1_started_2022_11_30_1313.log"
                ),
                "a",
            ) as log_file:
                log_file.write(content)
        except Exception:
            logger.warning("Failed to write to spec log file (omny web page).")

    def write_to_scilog(self, content, tags: list = None):
        try:
            if tags is not None:
                tags.append("BEC")
            else:
                tags = ["BEC"]
            msg = bec.logbook.LogbookMessage()
            msg.add_text(content).add_tag(tags)
            self.client.logbook.send_logbook_message(msg)
        except Exception:
            logger.warning("Failed to write to scilog.")

    def tomo_alignment_scan(self):
        """
        Performs a tomogram alignment scan.
        """
        if self.get_alignment_offset(0) == (0, 0, 0):
            print("It appears that the xrayeye alignemtn was not performend or loaded. Aborting.")
            return
        dev = builtins.__dict__.get("dev")
        bec = builtins.__dict__.get("bec")
        tags = ["BEC_alignment_tomo", self.sample_name]
        self.write_to_scilog(
            f"Starting alignment scan. First scan number: {bec.queue.next_scan_number}.", tags
        )

        start_angle = 0

        angle_end = start_angle + 180
        for angle in np.linspace(start_angle, angle_end, num=int(180 / 45) + 1, endpoint=True):
            successful = False
            error_caught = False
            if 0 <= angle < 180.05:
                print(f"Starting flOMNI scan for angle {angle}")
                while not successful:
                    self._start_beam_check()
                    try:
                        start_scan_number = bec.queue.next_scan_number
                        self.tomo_scan_projection(angle)
                        self.tomo_reconstruct()
                        error_caught = False
                    except AlarmBase as exc:
                        if exc.alarm_type == "TimeoutError":
                            bec.queue.request_queue_reset()
                            time.sleep(2)
                            error_caught = True
                        else:
                            raise exc

                    if self._was_beam_okay() and not error_caught:
                        successful = True
                    else:
                        self._wait_for_beamline_checks()
                end_scan_number = bec.queue.next_scan_number
                for scan_nr in range(start_scan_number, end_scan_number):
                    self._write_tomo_scan_number(scan_nr, angle, 0)

        print("Alignment scan finished. Please run SPEC_ptycho_align and load the new fit.")

        umv(dev.fsamroy, 0)

    def sub_tomo_scan(self, subtomo_number, start_angle=None):
        """
        Performs a sub tomogram scan.
        Args:
            subtomo_number (int): The sub tomogram number.
            start_angle (float, optional): The start angle of the scan. Defaults to None.
        """
        dev = builtins.__dict__.get("dev")
        bec = builtins.__dict__.get("bec")
        if self.tomo_id > 0:
            tags = ["BEC_subtomo", self.sample_name, f"tomo_id_{self.tomo_id}"]
        else:
            tags = ["BEC_subtomo", self.sample_name]
        self.write_to_scilog(
            f"Starting subtomo: {subtomo_number}. First scan number: {bec.queue.next_scan_number}.",
            tags,
        )

        if start_angle is None:
            if subtomo_number == 1:
                start_angle = 0
            elif subtomo_number == 2:
                start_angle = self.tomo_angle_stepsize / 8.0 * 4
            elif subtomo_number == 3:
                start_angle = self.tomo_angle_stepsize / 8.0 * 2
            elif subtomo_number == 4:
                start_angle = self.tomo_angle_stepsize / 8.0 * 6
            elif subtomo_number == 5:
                start_angle = self.tomo_angle_stepsize / 8.0 * 1
            elif subtomo_number == 6:
                start_angle = self.tomo_angle_stepsize / 8.0 * 5
            elif subtomo_number == 7:
                start_angle = self.tomo_angle_stepsize / 8.0 * 3
            elif subtomo_number == 8:
                start_angle = self.tomo_angle_stepsize / 8.0 * 7

        # _tomo_shift_angles (potential global variable)
        _tomo_shift_angles = 0
        angle_end = start_angle + 180
        for angle in np.linspace(
            start_angle + _tomo_shift_angles,
            angle_end,
            num=int(180 / self.tomo_angle_stepsize) + 1,
            endpoint=True,
        ):
            successful = False
            error_caught = False
            if 0 <= angle < 180.05:
                print(f"Starting flOMNI scan for angle {angle}")
                while not successful:
                    self._start_beam_check()
                    if not self.special_angles:
                        self._current_special_angles = []
                    if self._current_special_angles:
                        next_special_angle = self._current_special_angles[0]
                        if np.isclose(angle, next_special_angle, atol=0.5):
                            self._current_special_angles.pop(0)
                            num_repeats = self.special_angle_repeats
                    else:
                        num_repeats = 1
                    try:
                        start_scan_number = bec.queue.next_scan_number
                        for i in range(num_repeats):
                            self._at_each_angle(angle)
                        error_caught = False
                    except AlarmBase as exc:
                        if exc.alarm_type == "TimeoutError":
                            bec.queue.request_queue_reset()
                            time.sleep(2)
                            error_caught = True
                        else:
                            raise exc

                    if self._was_beam_okay() and not error_caught:
                        successful = True
                    else:
                        self._wait_for_beamline_checks()
                end_scan_number = bec.queue.next_scan_number
                for scan_nr in range(start_scan_number, end_scan_number):
                    self._write_tomo_scan_number(scan_nr, angle, subtomo_number)

    def tomo_scan(self, subtomo_start=1, start_angle=None):
        """start a tomo scan"""
        bec = builtins.__dict__.get("bec")
        scans = builtins.__dict__.get("scans")
        self._current_special_angles = self.special_angles.copy()

        if subtomo_start == 1 and start_angle is None:
            # pylint: disable=undefined-variable
            if bec.active_account != "":
                self.tomo_id = self.add_sample_database(
                    self.sample_name,
                    str(datetime.date.today()),
                    bec.active_account.decode(),
                    bec.queue.next_scan_number,
                    "flomni",
                    "test additional info",
                    "BEC",
                )
                self.write_pdf_report()
            else:
                self.tomo_id = 0
        with scans.dataset_id_on_hold:
            for ii in range(subtomo_start, 9):
                self.sub_tomo_scan(ii, start_angle=start_angle)
                start_angle = None

    def add_sample_database(
        self, samplename, date, eaccount, scan_number, setup, sample_additional_info, user
    ):
        """Add a sample to the omny sample database. This also retrieves the tomo id."""
        subprocess.run(
            f"wget --user=omny --password=samples -q -O /tmp/currsamplesnr.txt 'https://omny.web.psi.ch/samples/newmeasurement.php?sample={samplename}&date={date}&eaccount={eaccount}&scannr={scan_number}&setup={setup}&additional={sample_additional_info}&user={user}'",
            shell=True,
        )
        with open("/tmp/currsamplesnr.txt") as tomo_number_file:
            tomo_number = int(tomo_number_file.read())
        return tomo_number

    def _at_each_angle(self, angle: float) -> None:
        if "flomni_at_each_angle" in builtins.__dict__:
            # pylint: disable=undefined-variable
            flomni_at_each_angle(self, angle)
            return

        self.tomo_scan_projection(angle)
        self.tomo_reconstruct()

    def tomo_reconstruct(self, base_path="~/Data10/specES1"):
        """write the tomo reconstruct file for the reconstruction queue"""
        bec = builtins.__dict__.get("bec")
        base_path = os.path.expanduser(base_path)
        ptycho_queue_path = Path(os.path.join(base_path, self.ptycho_reconstruct_foldername))
        ptycho_queue_path.mkdir(parents=True, exist_ok=True)

        # pylint: disable=undefined-variable
        last_scan_number = bec.queue.next_scan_number - 1
        ptycho_queue_file = os.path.abspath(
            os.path.join(ptycho_queue_path, f"scan_{last_scan_number:05d}.dat")
        )
        with open(ptycho_queue_file, "w") as queue_file:
            scans = " ".join([str(scan) for scan in self._current_scan_list])
            queue_file.write(f"p.scan_number {scans}\n")
            queue_file.write("p.check_nextscan_started 1\n")

    def _write_tomo_scan_number(self, scan_number: int, angle: float, subtomo_number: int) -> None:
        tomo_scan_numbers_file = os.path.expanduser(
            "~/Data10/specES1/dat-files/tomography_scannumbers.txt"
        )
        with open(tomo_scan_numbers_file, "a+") as out_file:
            # pylint: disable=undefined-variable
            out_file.write(
                f"{scan_number} {angle} {dev.fsamroy.read()['fsamroy']['value']:.3f} {self.tomo_id} {subtomo_number} {0} {self.sample_name}\n"
            )

    def tomo_scan_projection(self, angle: float):
        scans = builtins.__dict__.get("scans")

        # additional_correction = self.align.compute_additional_correction(angle)
        # additional_correction_2 = self.align.compute_additional_correction_2(angle)
        # correction_xeye_mu = self.align.lamni_compute_additional_correction_xeye_mu(angle)
        offsets = self.get_alignment_offset(angle)
        sum_offset_x = offsets[0]
        sum_offset_y = (
            offsets[1]
            - self.compute_additional_correction_y(angle)
            - self.compute_additional_correction_y_2(angle)
        )
        sum_offset_z = offsets[2]

        self._current_scan_list = []

        for stitch_x in range(-self.stitch_x, self.stitch_x + 1):
            for stitch_y in range(-self.stitch_y, self.stitch_y + 1):
                # pylint: disable=undefined-variable
                corridor_size = self.corridor_size if self.corridor_size > 0 else None
                self._current_scan_list.append(bec.queue.next_scan_number)
                cenx = sum_offset_x + stitch_x * (self.fovx - self.tomo_stitch_overlap)
                ceny = sum_offset_y + stitch_y * (self.fovy - self.tomo_stitch_overlap)
                logger.info(
                    f"scans.flomni_fermat_scan(fovx={self.fovx}, fovy={self.fovy},"
                    f" step={self.tomo_shellstep}, cenx={cenx}, ceny={ceny},"
                    f" zshift={sum_offset_z}, angle={angle},"
                    f" exp_time={self.tomo_countingtime}, corridor_size={corridor_size})"
                )
                log_message = (
                    f"{str(datetime.datetime.now())}: flomni scan projection at angle {angle}, scan"
                    f" number {bec.queue.next_scan_number}.\n"
                )
                self.write_to_spec_log(log_message)
                # self.write_to_scilog(log_message, ["BEC_scans", self.sample_name])
                scans.flomni_fermat_scan(
                    fovx=self.fovx,
                    fovy=self.fovy,
                    step=self.tomo_shellstep,
                    cenx=cenx,
                    ceny=ceny,
                    zshift=sum_offset_z,
                    angle=angle,
                    exp_time=self.tomo_countingtime,
                    corridor_size=corridor_size,
                )

    def tomo_parameters(self):
        """print and update the tomo parameters"""
        print("Current settings:")
        print(f"Counting time           <ctime>  =  {self.tomo_countingtime} s")
        print(f"Stepsize microns         <step>  =  {self.tomo_shellstep}")
        print(f"FOV (200/100)  <microns>         =  {self.fovx}, {self.fovy}")
        print(f"Stitching number x,y             =  {self.stitch_x}, {self.stitch_y}")
        print(f"Stitching overlap                =  {self.tomo_stitch_overlap}")
        print(f"Reconstruction queue name        =  {self.ptycho_reconstruct_foldername}")
        print(f"   _manual_shift_y         <mm>  =  {self.manual_shift_y}")
        print(f"Angular step within sub-tomogram:   {self.tomo_angle_stepsize} degrees")
        print(f"Resulting in number of projections: {180/self.tomo_angle_stepsize*8}")
        print(f"Sample name: {self.sample_name}\n")

        user_input = input("Are these parameters correctly set for your scan? [Y/n]")
        if user_input == "y" or user_input == "":
            print("good then")
        else:
            self.tomo_countingtime = self._get_val("<ctime> s", self.tomo_countingtime, float)
            self.tomo_shellstep = self._get_val("<step size> um", self.tomo_shellstep, float)
            self.fovx = self._get_val("<FOV X (max 200)> um", self.fovx, float)
            self.fovy = self._get_val("<FOV Y (max 100)> um", self.fovy, float)
            self.stitch_x = self._get_val("<stitch X>", self.stitch_x, int)
            self.stitch_y = self._get_val("<stitch Y>", self.stitch_y, int)
            self.ptycho_reconstruct_foldername = self._get_val(
                "Reconstruction queue ", self.ptycho_reconstruct_foldername, str
            )
            tomo_numberofprojections = self._get_val(
                "Number of projections", 180 / self.tomo_angle_stepsize * 8, int
            )

            print(f"The angular step will be {180/tomo_numberofprojections}")
            self.tomo_angle_stepsize = 180 / tomo_numberofprojections * 8
            print(f"The angular step in a subtomogram it will be {self.tomo_angle_stepsize}")

    @staticmethod
    def _get_val(msg: str, default_value, data_type):
        return data_type(input(f"{msg} ({default_value}): ") or default_value)

    def write_pdf_report(self):
        """create and write the pdf report with the current flomni settings"""
        dev = builtins.__dict__.get("dev")
        # header = ""
        header = (
            " \n" * 3
            + "  .d888 888  .d88888b.  888b     d888 888b    888 8888888 \n"
            + ' d88P"  888 d88P" "Y88b 8888b   d8888 8888b   888   888 \n'
            + " 888    888 888     888 88888b.d88888 88888b  888   888   \n"
            + " 888888 888 888     888 888Y88888P888 888Y88b 888   888   \n"
            + " 888    888 888     888 888 Y888P 888 888 Y88b888   888   \n"
            + " 888    888 888     888 888  Y8P  888 888  Y88888   888   \n"
            + ' 888    888 Y88b. .d88P 888   "   888 888   Y8888   888   \n'
            + ' 888    888  "Y88888P"  888       888 888    Y888 8888888 \n'
        )
        padding = 20
        fovxy = f"{self.fovx:.2f}/{self.fovy:.2f}"
        stitching = f"{self.stitch_x:.2f}/{self.stitch_y:.2f}"
        dataset_id = str(self.client.queue.next_dataset_number)
        content = [
            f"{'Sample Name:':<{padding}}{self.sample_name:>{padding}}\n",
            f"{'Measurement ID:':<{padding}}{str(self.tomo_id):>{padding}}\n",
            f"{'Dataset ID:':<{padding}}{dataset_id:>{padding}}\n",
            f"{'Sample Info:':<{padding}}{'Sample Info':>{padding}}\n",
            f"{'e-account:':<{padding}}{str(self.client.username):>{padding}}\n",
            f"{'Number of projections:':<{padding}}{int(180 / self.tomo_angle_stepsize * 8):>{padding}}\n",
            f"{'First scan number:':<{padding}}{self.client.queue.next_scan_number:>{padding}}\n",
            f"{'Last scan number approx.:':<{padding}}{self.client.queue.next_scan_number + int(180 / self.tomo_angle_stepsize * 8) + 10:>{padding}}\n",
            f"{'Current photon energy:':<{padding}}{dev.mokev.read()['mokev']['value']:>{padding}.4f}\n",
            f"{'Exposure time:':<{padding}}{self.tomo_countingtime:>{padding}.2f}\n",
            f"{'Fermat spiral step size:':<{padding}}{self.tomo_shellstep:>{padding}.2f}\n",
            f"{'FOV:':<{padding}}{fovxy:>{padding}}\n",
            f"{'Stitching:':<{padding}}{stitching:>{padding}}\n",
            f"{'Number of individual sub-tomograms:':<{padding}}{8:>{padding}}\n",
            f"{'Angular step within sub-tomogram:':<{padding}}{self.tomo_angle_stepsize:>{padding}.2f}\n",
        ]
        content = "".join(content)
        user_target = os.path.expanduser(f"~/Data10/documentation/tomo_scan_ID_{self.tomo_id}.pdf")
        with PDFWriter(user_target) as file:
            file.write(header)
            file.write(content)
        subprocess.run(
            "xterm /work/sls/spec/local/XOMNY/bin/upload/upload_last_pon.sh &", shell=True
        )
        # status = subprocess.run(f"cp /tmp/spec-e20131-specES1.pdf {user_target}", shell=True)
        msg = bec.logbook.LogbookMessage()
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LamNI_logo.png")
        msg.add_file(logo_path).add_text("".join(content).replace("\n", "</p><p>")).add_tag(
            ["BEC", "tomo_parameters", f"dataset_id_{dataset_id}", "LamNI", self.sample_name]
        )
        self.client.logbook.send_logbook_message(msg)


if __name__ == "__main__":
    import builtins

    from bec_client import BECIPythonClient

    bec = BECIPythonClient()
    bec.start()
    bec.load_high_level_interface("spec_hli")
    scans = bec.scans
    dev = bec.device_manager.devices
    builtins.__dict__["scans"] = scans
    builtins.__dict__["dev"] = dev
    builtins.__dict__["bec"] = bec
    builtins.__dict__["umv"] = umv
    flomni = Flomni(bec)
    flomni.start_x_ray_eye_alignment()
