# plugins/atf_scan_plugin.py
import os
import subprocess
import json

from droidbot.plugin import Plugin

HARNESS_PKG = "br.ufal.ic.atfharness"
TEST_RUNNER = f"{HARNESS_PKG}.test/androidx.test.runner.AndroidJUnitRunner"
TEST_CLASS = f"{HARNESS_PKG}.AtfScanTest#scanForegroundWindow"
DEVICE_SCANS_DIR = f"/sdcard/Android/data/{HARNESS_PKG}/files/scans"


class AtfScanPlugin(Plugin):
    """Executa um scan do atf-harness (motor de checks do Accessibility
    Scanner) apos cada evento do DroidBot, uma vez por estado unico.

    O stateId do scan e o state_str do DroidBot, entao os JSONs gerados
    casam 1:1 com os estados reportados pelo a11y-argus (screen_id do
    errors.json), dispensando heuristica de alinhamento no matching.

    Requisitos: APKs do atf-harness instalados no device
    (installDebug installDebugAndroidTest).
    """

    def __init__(self, output_dir, target_package=None, scan_timeout=120):
        super().__init__()
        self.output_dir = os.path.join(output_dir, "atf")
        os.makedirs(self.output_dir, exist_ok=True)
        self.target_package = target_package
        self.scan_timeout = scan_timeout
        self.device = None
        self.scanned = set()
        self.failures = []

    def on_device_ready(self, device):
        self.device = device

    def _adb(self):
        cmd = ["adb"]
        serial = getattr(self.device, "serial", None)
        if serial:
            cmd += ["-s", serial]
        return cmd

    def after_event(self, event, state):
        if state is None or self.device is None:
            return

        state_str = state.state_str
        structure = getattr(state, "structure_str", None) or state_str
        if structure in self.scanned:
            return  # uma tela (estrutura) e escaneada uma unica vez

        # Espelha o is_app_screen do pipeline: ignora estados fora do app alvo
        foreground = getattr(state, "foreground_activity", None) or ""
        if self.target_package and self.target_package not in foreground:
            return

        self.scanned.add(state_str)
        print(f"[ATF_PLUGIN] Scan do estado {state_str[:12]}... "
              f"({len(self.scanned)} estados)")
        # Salva o estado do droidbot junto do scan (rastreabilidade/diagnostico)
        try:
            with open(os.path.join(self.output_dir, f"{state_str}.state.json"),
                      "w", encoding="utf-8") as f:
                json.dump(state.to_dict(), f, indent=2)
        except Exception as e:
            print(f"[ATF_PLUGIN] Aviso: falha ao salvar estado: {e}")

        instrument = self._adb() + [
            "shell", "am", "instrument", "-w",
            "-e", "class", TEST_CLASS,
            "-e", "stateId", state_str,
            "-e", "saveScreenshot", "false",  # o droidbot ja salva screenshots
            TEST_RUNNER,
        ]
        try:
            proc = subprocess.run(instrument, capture_output=True, text=True,
                                  timeout=self.scan_timeout)
            if "OK (1 test)" not in proc.stdout:
                raise RuntimeError(proc.stdout[-300:])
            local_json = os.path.join(self.output_dir, f"{state_str}.json")
            subprocess.run(
                self._adb() + ["pull", f"{DEVICE_SCANS_DIR}/{state_str}.json",
                               local_json],
                capture_output=True, timeout=60, check=True)
        except Exception as e:
            self.failures.append(state_str)
            print(f"[ATF_PLUGIN] FALHA no estado {state_str[:12]}: {e}")

    def on_finish(self):
        ok = len(self.scanned) - len(self.failures)
        print(f"[ATF_PLUGIN] Finalizado: {ok} scans ok, "
              f"{len(self.failures)} falhas, saida em {self.output_dir}")
        if self.failures:
            failures_path = os.path.join(self.output_dir, "_falhas.txt")
            with open(failures_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.failures))
