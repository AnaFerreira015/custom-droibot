# ocr-test\droidbot\droidbot\plugins\screen_capture_plugin.py
import os
import json
import time

class Plugin:
    def on_device_ready(self, device): pass
    def after_event(self, event, state): pass
    def on_finish(self): pass

class ScreenCapturePlugin(Plugin):
    def __init__(self, output_dir, font_type, target_package=None):
        self.output_dir = output_dir
        self.font_type = font_type
        self.target_package = target_package
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
        state_id = state.state_str
        print(f"[PLUGIN - Droidbot] Capturando tela '{state_id}' após evento: {event}")

        screen_filename = os.path.join(self.prints_dir, f"screen_{self.font_type}_{state_id}.png")
        xml_filename = os.path.join(self.xmls_dir, f"ui_dump_{self.font_type}_{state_id}.xml")
        state_filename = os.path.join(self.states_dir, f"state_{self.font_type}_{state_id}.json")

        serializable_state = {
            k: v for k, v in state.__dict__.items()
            if isinstance(v, (str, int, float, list, dict, bool, type(None)))
        }

        serializable_state["state_str"] = state.state_str
        serializable_state["foreground_activity"] = getattr(state, "foreground_activity", "")

        print(f"[PLUGIN - Droidbot] Atividade atual: {serializable_state['foreground_activity']}")

        with open(state_filename, "w", encoding="utf-8") as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)

        # FORÇA DELAY MAIOR para garantir que a UI atualizou
        time.sleep(3)

        temp_xml = f"/sdcard/ui_dump_{state_id}.xml"
        temp_screen = f"/sdcard/screen_{state_id}.png"

        try:
            self.device.adb.shell(f"uiautomator dump --compressed /sdcard/window_dump.xml")
            self.device.adb.shell(f"mv /sdcard/window_dump.xml {temp_xml}")
            self.device.adb.pull(temp_xml, xml_filename)
            # self.device.adb.shell(f"rm {temp_xml}")
        except Exception as e:
            print(f"[PLUGIN - Droidbot] Erro ao capturar UI dump: {e}")

        self.device.adb.shell(f"screencap -p {temp_screen}")
        self.device.adb.pull(temp_screen, screen_filename)
        # self.device.adb.shell(f"rm {temp_screen}")

        print(f"[PLUGIN - Droidbot] Tela '{state_id}' capturada com sucesso.")

    def on_finish(self):
        print("[PLUGIN - Droidbot] Plugin de captura finalizado.")