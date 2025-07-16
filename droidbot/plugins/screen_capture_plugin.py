# C:\Projetos\droidbot\droidbot\plugins\screen_capture_plugin.py

import os
import json
import re
import time

class Plugin:
    def on_device_ready(self, device): pass
    def after_event(self, event, state): pass
    def on_finish(self): pass

class ScreenCapturePlugin(Plugin):
    def __init__(self, output_dir, font_type, target_package):
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

    # def is_user_app(self, device):
    #     try:
    #         output = device.adb.shell("dumpsys activity activities | findstr mResumedActivity")
    #         match = re.search(r"mResumedActivity:\s+ActivityRecord\{.*?\s(\S+)/", output)
    #         if match:
    #             package_name = match.group(1)
    #             print(f"[PLUGIN] Pacote atual: {package_name}")
    #
    #             # Agora testamos palavras-chave
    #             system_keywords = [
    #                 "launcher",
    #                 "systemui",
    #                 "settings",
    #                 "phone",
    #                 "googlequicksearchbox",
    #                 "gms",
    #                 "android.contacts",
    #                 "android.dialer",
    #             ]
    #
    #             if any(keyword in package_name.lower() for keyword in system_keywords):
    #                 print(f"[PLUGIN] Tela do sistema detectada ({package_name}), será ignorada.")
    #                 return False
    #
    #             return True  # Não é sistema = pode capturar
    #
    #     except Exception as e:
    #         print(f"[PLUGIN] Erro ao verificar pacote atual: {e}")
    #     return False

    def is_user_app(self, device):
        try:
            output = device.adb.shell("dumpsys window")
            lines = output.splitlines()
            focus_lines = [line for line in lines if 'mCurrentFocus' in line or 'mFocusedApp' in line]

            if not focus_lines:
                print("[PLUGIN] Nenhuma linha de foco encontrada no dumpsys.")
                return False

            for line in focus_lines:
                print(f"[PLUGIN] Linha de foco encontrada: {line}")
                match = re.search(r"(mCurrentFocus|mFocusedApp)=.*\s(\S+)/", line)
                if match:
                    package_name = match.group(2).split('/')[0]
                    print(f"[PLUGIN] Pacote atual detectado: {package_name}")
                    if package_name == self.target_package:
                        return True
                    else:
                        print(f"[PLUGIN] Pacote diferente do app alvo ({self.target_package}), será ignorado.")
                        return False

            print("[PLUGIN] Não foi possível extrair pacote de nenhuma linha de foco.")
            return False
        except Exception as e:
            print(f"[PLUGIN] Erro ao verificar pacote atual: {e}")
            return False

    def after_event(self, event, state):
        state_id = state.state_str
        print(f"[PLUGIN] Tentando capturar tela '{state_id}' após evento: {event}")

        if not self.is_user_app(self.device):
            print("[PLUGIN] Ignorando tela do sistema.")
            return

        # Nomes dos arquivos
        screen_filename = os.path.join(self.prints_dir, f"screen_{self.font_type}_{state_id}.png")
        xml_filename = os.path.join(self.xmls_dir, f"ui_dump_{self.font_type}_{state_id}.xml")
        state_filename = os.path.join(self.states_dir, f"state_{self.font_type}_{state_id}.json")

        # Filtra apenas os atributos serializáveis
        serializable_state = {
            k: v for k, v in state.__dict__.items()
            if isinstance(v, (str, int, float, list, dict, bool, type(None)))
        }

        serializable_state["state_str"] = state.state_str
        serializable_state["foreground_activity"] = getattr(state, "foreground_activity", "")

        # Salva o JSON do estado (pode manter mesmo se falhar)
        with open(state_filename, "w", encoding="utf-8") as f:
            json.dump(serializable_state, f, indent=2, ensure_ascii=False)

        time.sleep(2)

        temp_xml = f"/sdcard/ui_dump_{state_id}.xml"
        temp_screen = f"/sdcard/screen_{state_id}.png"

        try:
            # Tenta capturar o dump
            dump_result = self.device.adb.shell(f"uiautomator dump --compressed /sdcard/window_dump.xml")
            print(f"[PLUGIN] Resultado do dump: '{dump_result.strip()}'")

            if "UI hierchary dumped to" not in dump_result:
                print(f"[PLUGIN] Erro no dump, ignorando tela '{state_id}'.")
                return  # IGNORA esta tela completamente!

            # Se deu certo, continua com a captura
            self.device.adb.shell(f"mv /sdcard/window_dump.xml {temp_xml}")
            self.device.adb.pull(temp_xml, xml_filename)
            self.device.adb.shell(f"rm {temp_xml}")

            # Captura screenshot
            self.device.adb.shell(f"screencap -p {temp_screen}")
            self.device.adb.pull(temp_screen, screen_filename)
            self.device.adb.shell(f"rm {temp_screen}")

            print(f"[PLUGIN] Tela '{state_id}' capturada com sucesso.")

        except Exception as e:
            print(f"[PLUGIN] Exceção ao capturar tela '{state_id}': {e}")
            # Também ignora a tela nesse caso

    def on_finish(self):
        print("[PLUGIN] Plugin de captura finalizado.")