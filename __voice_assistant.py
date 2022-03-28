import pyttsx3  # синтез речи (Text-To-Speech)
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)

import random

from translation import Translation
from owner_person import OwnerPerson


class __VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    Примечание: для мультиязычных голосовых ассистентов лучше создать отдельный класс,
    который будет брать перевод из JSON-файла с нужным языком
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""
    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()


    def setup_assistant_voice(self) -> None:
        """
        Установка голоса по умолчанию (индекс может меняться в зависимости от настроек операционной системы)
        """
        voices = self.ttsEngine.getProperty("voices")

        if self.speech_language == "en":
            self.recognition_language = "en-US"
            if self.sex == "female":
                # Microsoft Zira Desktop - English (United States)
                self.ttsEngine.setProperty("voice", voices[1].id)
            else:
                # Microsoft David Desktop - English (United States)
                self.ttsEngine.setProperty("voice", voices[2].id)
        else:
            self.recognition_language = "ru-RU"
            # Microsoft Irina Desktop - Russian
            self.ttsEngine.setProperty("voice", voices[0].id)

    def play_voice_assistant_speech(self, text_to_speech: str) -> None:
        """
        Проигрывание речи ответов голосового ассистента (без сохранения аудио)
        :param text_to_speech: текст, который нужно преобразовать в речь
        """
        self.ttsEngine.say(str(text_to_speech))
        self.ttsEngine.runAndWait()


class VoiceAssistant(__VoiceAssistant):
    def __init__(self, translator: Translation, person: OwnerPerson) -> None:
        super().__init__()
        self.translator = translator
        self.person = person


    def play_greetings(self, *args: tuple):
        """
        Проигрывание случайной приветственной речи
        """
        greetings = [
            self.translator.get("Hello, {}! How can I help you today?").format(self.person.name),
            self.translator.get("Good day to you {}! How can I help you today?").format(self.person.name)
        ]
        self.play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])
    
    def play_farewell_and_quit(self, *args: tuple):
        """
        Проигрывание прощательной речи и выход
        """
        farewells = [
            self.translator.get("Goodbye, {}! Have a nice day!").format(self.person.name),
            self.translator.get("See you soon, {}!").format(self.person.name)
        ]
        self.play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
        self.ttsEngine.stop()
        quit()

    def change_language(self, *args: tuple):
        """
        Изменение языка голосового ассистента (языка распознавания речи)
        """
        self.speech_language = "ru" if self..speech_language == "en" else "en"
        self.setup_assistant_voice()
        print(colored("Language switched to " + self.speech_language, "cyan"))
