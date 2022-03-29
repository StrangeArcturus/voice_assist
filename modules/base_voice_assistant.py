import pyttsx3  # синтез речи (Text-To-Speech)
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from num2words import num2words as nw # для проговаривания слов
import pymorphy2 # для склонения этих слов
import pyautogui # работа с курсором

import random
from time import sleep # для "сна" ассистента
from datetime import datetime as dt # работа с датой и временем

import translation
import owner_person


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
    """
    Базовая модель голосовго ассистента,
    наследующая модель с первичными данными и настройками
    """
    def set_dependies(self, translator: translation.Translation, person: owner_person.OwnerPerson) -> None:
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
        self.speech_language = "ru" if self.speech_language == "en" else "en"
        self.setup_assistant_voice()
        print(colored("Language switched to " + self.speech_language, "cyan"))

    
    def toss_coin(self, *args: tuple):
        """
        "Подбрасывание" монетки для выбора из 2 опций
        """
        flips_count, heads, tails = 3, 0, 0

        for flip in range(flips_count):
            if random.randint(0, 1) == 0:
                heads += 1

        tails = flips_count - heads
        winner = "Tails" if tails > heads else "Heads"
        self.play_voice_assistant_speech(self.translator.get(winner) + " " + self.translator.get("won"))

    def now_time(self, *args: tuple):
        """
        Сообщение нынешнего времени
        """
        now_t = dt.now().time().strftime("%H : %M")
        rnd = random.choice((0, 1))
        # случайным образом подбираем вариант фразы
        #if rnd == 0:
        #    string_time = translator.get('Now is')
        # else:
        #    string_time = translator.get("Relative to your device, time is now")
        string_time = 'Now is' if rnd == 0 else "Relative to your device, time is now"
        self.play_voice_assistant_speech(self.translator.get(string_time) + " " + str(now_t))
        print(f'{self.translator.get(string_time)} {str(now_t)}')
    
    def now_date(self, *args: tuple):
        """
        сообщение сегодняшней даты
        """
        now_d = dt.now().date().strftime("%A\t%d %B %Y")
        # получаем сегодняшнюю дату и тут же приводим её к +- норм виду
        morph = pymorphy2.MorphAnalyzer() # для преобразовашек числительных
        day_name, other_date = now_d.split('\t')
        # получаем имя дня и "остальную дату"
        if self.speech_language == 'ru':
            day_num = nw(int(other_date.split()[0]), lang='ru', to='ordinal').split()
            d_parse = morph.parse(day_num[-1])[0]
            day_num[-1] = d_parse.inflect({'neut', 'nomn'}).word
            day_num = ' '.join(day_num) # приводим числительное к одной строке через пробел
        else:
            day_num = nw(int(other_date.split()[0]), to='ordinal')
        # преобразование числа в словесное числительное, а затем для склонения, если бот на русском
        # вот тут я, кстати, затупил на НЕДЕЛЮ без продвижений
        # просто кто же мог подумать, что к порядковому числительному можно
        # приводить число прям в num2words и без всякой pymorphy2
        # а в ней уже просто менять род ААААААА
        # парсим число для смены рода
        # меняем род дня недели на средний в последнем слове числительного, даже если оно из одного слова
        # чтобы, как на момент написания этих комментов,
        # было, к примеру, двадцать четвёртОЕ июня
        if self.speech_language == 'ru':
            month_name = morph.parse(self.translator.get(other_date.split()[1]))[0].inflect({'gent'}).word
            # приводим имя месяца к родительному падежу
        else:
            month_name = self.translator.get(other_date.split()[1])
        if self.speech_language == 'ru':
            year = nw(int(other_date.split()[2]), lang='ru', to='ordinal').split()
            # преобразуем уже номер года, и тоже к ПОРЯДКОВОМУ ЧИСЛИТЕЛЬНОМУ
            # так как год мужского рода, то далее изменений не производим
            year = ' '.join(year) # соединяем в одну строку и порядковый года
        else:
            year = nw(int(other_date.split()[2]), to='ordinal')
        answer = f"{self.translator.get('Today is')} {self.translator.get(day_name)} {day_num} {month_name} {year} год"
        print(answer)
        self.play_voice_assistant_speech(answer)

    def shut_up(self, *args: tuple):
        """
        Заставляет голосового ассистента помолчать на 10 минут
        """
        answer = self.translator.get("Okey, I'll start to you again and answering in 10 minutes")
        print(answer)
        self.play_voice_assistant_speech(answer)
        sleep(600)

    def thanks(self, *args: tuple):
        """
        Ответ на благодарность пользователя
        """
        answer = random.choice((
            (self.translator.get("Glad to serve")),
            self.translator.get("Nothing to thanks"),
            self.translator.get("Created to serve")
        ))
        print(answer)
        self.play_voice_assistant_speech(answer)


class VoiceAssistantWithGUIControl(VoiceAssistant):
    """
    Модель, использующая автоматическое управление GUI'ем
    """
    def window_off(self, *args: tuple):
        """
        Закрывает все окна, хе-хе~
        """
        pyautogui.FAILSAFE = False
        size = pyautogui.size()
        x = size.width
        y = size.height
        pyautogui.moveTo(x=x, y=y, duration=1)
        pyautogui.click(clicks=1)
        self.play_voice_assistant_speech("окна закрываются")
