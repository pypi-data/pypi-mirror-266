import builtins
import datetime
import threading
import time

from bec_lib import bec_logger

logger = bec_logger.logger

if builtins.__dict__.get("bec"):
    bec = builtins.__dict__.get("bec")


class cSAXSBeamlineChecks:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_shutter = True
        self.check_light_available = True
        self.check_fofb = True
        self._check_msgs = []
        self._beam_is_okay = True
        self._stop_beam_check_event = None
        self.beam_check_thread = None

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

    def _run_beamline_checks(self):
        msgs = []
        dev = builtins.__dict__.get("dev")
        try:
            if self.check_shutter:
                shutter_val = dev.x12sa_es1_shutter_status.read(cached=True)
                if shutter_val["value"].lower() != "open":
                    self._beam_is_okay = False
                    msgs.append("Check beam failed: Shutter is closed.")
            if self.check_light_available:
                machine_status = dev.sls_machine_status.read(cached=True)
                if machine_status["value"] not in ["Light Available", "Light-Available"]:
                    self._beam_is_okay = False
                    msgs.append("Check beam failed: Light not available.")
            if self.check_fofb:
                fast_orbit_feedback = dev.sls_fast_orbit_feedback.read(cached=True)
                if fast_orbit_feedback["value"] != "running":
                    self._beam_is_okay = False
                    msgs.append("Check beam failed: Fast orbit feedback is not running.")
        except Exception:
            logger.warning("Failed to check beam.")
        return msgs

    def _check_beam(self):
        while not self._stop_beam_check_event.is_set():
            self._check_msgs = self._run_beamline_checks()

            if not self._beam_is_okay:
                self._stop_beam_check_event.set()
            time.sleep(1)

    def _start_beam_check(self):
        self._beam_is_okay = True
        self._stop_beam_check_event = threading.Event()

        self.beam_check_thread = threading.Thread(target=self._check_beam, daemon=True)
        self.beam_check_thread.start()

    def _was_beam_okay(self):
        self._stop_beam_check_event.set()
        self.beam_check_thread.join()
        return self._beam_is_okay

    def _print_beamline_checks(self):
        for msg in self._check_msgs:
            logger.warning(msg)

    def _wait_for_beamline_checks(self):
        self._print_beamline_checks()
        try:
            msg = bec.logbook.LogbookMessage()
            msg.add_text(
                "<p><mark class='pen-red'><strong>Beamline checks failed at"
                f" {str(datetime.datetime.now())}: {''.join(self._check_msgs)}</strong></mark></p>"
            ).add_tag(["BEC", "beam_check"])
            bec.logbook.send_logbook_message(msg)
        except Exception:
            logger.warning("Failed to send update to SciLog.")

        while True:
            self._beam_is_okay = True
            self._check_msgs = self._run_beamline_checks()
            if self._beam_is_okay:
                break
            self._print_beamline_checks()
            time.sleep(1)

        try:
            msg = bec.logbook.LogbookMessage()
            msg.add_text(
                "<p><mark class='pen-red'><strong>Operation resumed at"
                f" {str(datetime.datetime.now())}.</strong></mark></p>"
            ).add_tag(["BEC", "beam_check"])
            bec.logbook.send_logbook_message(msg)
        except Exception:
            logger.warning("Failed to send update to SciLog.")
