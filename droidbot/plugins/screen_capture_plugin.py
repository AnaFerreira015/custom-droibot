# screen_capture_plugin.py
import os
import json
import time

class Plugin:
    def on_device_ready(self, device): pass
    def after_event(self, event, state): pass
    def on_finish(self): pass

class ScreenCapturePlugin(Plugin):
    def __init__(self, output_dir, font_type):
        self.output_dir = output_dir
        self.font_type = font_type
        self.device = None

        self.prints_dir = os.path.join(output_dir, "prints")
        self.xmls_dir = os.path.join(output_dir, "xmls")
        self.states_dir = os.path.join(output_dir, "states")

        os.makedirs(self.prints_dir, exist_ok=True)
        os.makedirs(self.xmls_dir, exist_ok=True)
        os.makedirs(self.states_dir, exist_ok=True)

    def on_device_ready(self, device):
        self.device = device

    def after_event(self, event, state):
        state_id = state.state_str  # identificador único da tela atual
        print(f"[PLUGIN] Capturando tela '{state_id}' após evento: {event}")

        # Nomes dos arquivos
        screen_filename = os.path.join(self.prints_dir, f"screen_{self.font_type}_{state_id}.png")
        xml_filename = os.path.join(self.xmls_dir, f"ui_dump_{self.font_type}_{state_id}.xml")
        state_filename = os.path.join(self.states_dir, f"state_{self.font_type}_{state_id}.json")

        # 🔐 Filtra apenas os atributos serializáveis
        serializable_state = {
            k: v for k, v in state.__dict__.items()
            if isinstance(v, (str, int, float, list, dict, bool, type(None)))
        }

        # ✅ Garante campos críticos
        serializable_state["state_str"] = state.state_str
        serializable_state["foreground_activity"] = getattr(state, "foreground_activity", "")

        # Salva o JSON
        with open(state_filename, "w", encoding="utf-8") as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)

        # Captura XML
        self.device.adb.shell("uiautomator dump /sdcard/ui_dump.xml")
        self.device.adb.pull("/sdcard/ui_dump.xml", xml_filename)

        # Captura screenshot
        self.device.adb.shell("screencap -p /sdcard/screen.png")
        self.device.adb.pull("/sdcard/screen.png", screen_filename)

        print(f"[PLUGIN] Tela '{state_id}' capturada com sucesso.")

    def on_finish(self):
        print("[PLUGIN] Plugin de captura finalizado.")