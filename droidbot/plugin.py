# plugin.py
class Plugin(object):
    """
    Classe base para plugins do DroidBot.
    Plugins podem estender essa classe para reagir a diferentes fases da execução do DroidBot.
    """

    def __init__(self):
        """
        Inicialização do plugin.
        Pode ser sobrescrita para configurar o plugin.
        """
        pass

    def on_start(self):
        """
        Chamado quando o DroidBot inicia.
        Ideal para inicialização de variáveis ou logs.
        """
        pass

    def on_device_ready(self, device):
        """
        Chamado quando o dispositivo está pronto para interagir.
        :param device: Instância do dispositivo DroidBot
        """
        pass

    def before_event(self, event, state):
        """
        Chamado antes de um evento ser executado.
        :param event: O evento que será executado
        :param state: O estado atual do app (extraído pelo DroidBot)
        """
        pass

    def after_event(self, event, state):
        """
        Chamado após um evento ser executado.
        :param event: O evento que foi executado
        :param state: O estado atual do app (extraído pelo DroidBot)
        """
        pass

    def on_stop(self):
        """
        Chamado quando o DroidBot é interrompido antes de finalizar.
        Pode ser usado para limpeza de recursos.
        """
        pass

    def on_finish(self):
        """
        Chamado quando o DroidBot finaliza com sucesso.
        Ideal para encerrar atividades ou armazenar dados finais.
        """
        pass
