import json  # работа с json-файлами и json-строками
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)

import modules.base_voice_assistant


class Translation:
    """
    Получение вшитого в приложение перевода строк для создания мультиязычного ассистента
    """    
    def set_dependies(self, assistant: modules.base_voice_assistant.VoiceAssistant) -> None:
        self.assistant = assistant

    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    def get(self, text: str) -> str:
        """
        Получение перевода строки из файла на нужный язык (по его коду)
        :param text: текст, который требуется перевести
        :return: вшитый в приложение перевод текста
        """
        if text in self.translations:
            return self.translations[text][self.assistant.speech_language]
        else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возврат исходного текста
            print(colored("Not translated phrase: {}".format(text), "red"))
            return text
