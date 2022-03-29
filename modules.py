import os
import wave
import json  # работа с json-файлами и json-строками
import random  # генератор случайных чисел
import traceback  # вывод traceback без остановки работы программы при отлове исключений
import webbrowser  # работа с использованием браузера по умолчанию (открывание вкладок с web-страницей)
from time import sleep  # для "сна" ассистента
from datetime import datetime as dt  # работа с датой и временем

import pyttsx3  # синтез речи (Text-To-Speech)
import pyautogui  # работа с курсором
import pymorphy2  # для склонения этих слов
import googletrans  # использование системы Google Translate
import wikipediaapi  # поиск определений в Wikipedia
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
from pyowm import OWM  # использование OpenWeatherMap для получения данных о погоде
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from googlesearch import search  # поиск в Google
from num2words import num2words as nw  # для проговаривания слов
from vosk import KaldiRecognizer, Model  # оффлайн-распознавание от Vosk

from TOKEN import OWM_TOKEN


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
    def set_dependies(self, translator: "Translation", person: "OwnerPerson") -> None:
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


class OwnerPerson:
    """
    Информация о владельце, включающие имя, город проживания, родной язык речи, изучаемый язык (для переводов текста)
    """
    name = ""
    home_city = ""
    native_language = ""
    target_language = ""


class Recognizer:
    """
    Класс, используемый для обработки и распознавания речи
    """    
    def set_dependies(self, translator: "Translation", assistant: "VoiceAssistant") -> None:
        self.translator = translator
        self.voice_assistant = assistant

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    def record_and_recognize_audio(self, *args: tuple) -> str:
        """
        Запись и распознавание аудио
        """
        with self.microphone:
            recognized_data = ""

            # запоминание шумов окружения для последующей очистки звука от них
            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=2)

            rnd_mic = random.choice((0, 1))
            try:
                if rnd_mic == 0:
                    print(self.translator.get("Listening..."))
                else:
                    self.voice_assistant.play_voice_assistant_speech(self.translator.get("Listening..."))
                    print(self.translator.get("Listening..."))
                audio = self.recognizer.listen(self.microphone, 5, 5)

                with open("microphone-results.wav", "wb") as file:
                    file.write(audio.get_wav_data())

            except speech_recognition.WaitTimeoutError:
                if rnd_mic == 0:
                    print(self.translator.get("Can you check if your microphone is on, please?"))
                else:
                    self.voice_assistant.play_voice_assistant_speech(self.translator.get("Can you check if your microphone is on, please?"))
                    print(self.translator.get("Can you check if your microphone is on, please?"))
                # то же самое, что и выше, только при ошибке
                
                traceback.print_exc()
                return ''

            # использование online-распознавания через Google (высокое качество распознавания)
            try:
                print("Started recognition...")
                recognized_data = str(self.recognizer.recognize_google(
                    audio,
                    language=self.voice_assistant.recognition_language
                )).lower()

            except speech_recognition.UnknownValueError:
                pass  # play_voice_assistant_speech("What did you say again?")

            # в случае проблем с доступом в Интернет происходит попытка использовать offline-распознавание через Vosk
            except speech_recognition.RequestError:
                print(colored("Trying to use offline recognition...", "cyan"))
                recognized_data = self.use_offline_recognition()

            return recognized_data


    def use_offline_recognition(self):
        """
        Переключение на оффлайн-распознавание речи
        :return: распознанная фраза
        """
        recognized_data = ""
        try:
            # проверка наличия модели на нужном языке в каталоге приложения
            if not os.path.exists("models/vosk-model-small-" + self.voice_assistant.speech_language + "-0.4"):
                print(colored("Please download the model from:\n"
                            "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.",
                            "red"))
                exit(1)

            # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
            wave_audio_file = wave.open("microphone-results.wav", "rb")
            model = Model("models/vosk-model-small-" + self.voice_assistant.speech_language + "-0.4")
            offline_recognizer = KaldiRecognizer(model, wave_audio_file.getframerate())

            data = wave_audio_file.readframes(wave_audio_file.getnframes())
            if len(data) > 0:
                if offline_recognizer.AcceptWaveform(data):
                    recognized_data = offline_recognizer.Result()

                    # получение данных распознанного текста из JSON-строки (чтобы можно было выдать по ней ответ)
                    recognized_data = json.loads(recognized_data)
                    recognized_data = recognized_data["text"]
        except:
            traceback.print_exc()
            print(colored("Sorry, speech service is unavailable. Try again later", "red"))

        return recognized_data


class Translation:
    """
    Получение вшитого в приложение перевода строк для создания мультиязычного ассистента
    """    
    def set_dependies(self, assistant: "VoiceAssistant") -> None:
        self.assistant = assistant

    with open("./translations.json", "r", encoding="utf-8") as file:
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


class VoiceAssistantWithInternetSkills(VoiceAssistant):
    """
    Класс, наследующий базовые модели ассистента
    и дополняющий их методами с доступом в интернет
    """
    def search_for_term_on_google(self, *args: tuple):
        """
        Поиск в Google с автоматическим открытием ссылок (на список результатов и на сами результаты, если возможно)
        :param args: фраза поискового запроса
        """
        if not args[0]: return
        search_term = " ".join(args[0])

        # открытие ссылки на поисковик в браузере
        url = "https://google.com/search?q=" + search_term
        webbrowser.get().open(url)

        # альтернативный поиск с автоматическим открытием ссылок на результаты (в некоторых случаях может быть небезопасно)
        search_results = []
        try:
            for _ in search(search_term,  # что искать
                            tld="com",  # верхнеуровневый домен
                            lang=self.speech_language,  # используется язык, на котором говорит ассистент
                            num=1,  # количество результатов на странице
                            start=0,  # индекс первого извлекаемого результата
                            stop=1,  # индекс последнего извлекаемого результата (я хочу, чтобы открывался первый результат)
                            pause=1.0,  # задержка между HTTP-запросами
                            ):
                search_results.append(_)
                webbrowser.get().open(_)

        # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
        except:
            self.play_voice_assistant_speech(self.translator.get("Seems like we have a trouble. See logs for more information"))
            traceback.print_exc()
            return

        print(search_results)
        self.play_voice_assistant_speech(self.translator.get("Here is what I found for {} on google").format(search_term))

    def search_for_video_on_youtube(self, *args: tuple):
        """
        Поиск видео на YouTube с автоматическим открытием ссылки на список результатов
        :param args: фраза поискового запроса
        """
        if not args[0]: return
        search_term = " ".join(args[0])
        url = "https://www.youtube.com/results?search_query=" + search_term
        webbrowser.get().open(url)
        self.play_voice_assistant_speech(self.translator.get("Here is what I found for {} on youtube").format(search_term))

    def search_for_definition_on_wikipedia(self, *args: tuple):
        """
        Поиск в Wikipedia определения с последующим озвучиванием результатов и открытием ссылок
        :param args: фраза поискового запроса
        """
        if not args[0]: return

        search_term = " ".join(args[0])

        # установка языка (в данном случае используется язык, на котором говорит ассистент)
        wiki = wikipediaapi.Wikipedia(self.speech_language)

        # поиск страницы по запросу, чтение summary, открытие ссылки на страницу для получения подробной информации
        wiki_page = wiki.page(search_term)
        try:
            if wiki_page.exists():
                self.play_voice_assistant_speech(self.translator.get("Here is what I found for {} on Wikipedia").format(search_term))
                webbrowser.get().open(wiki_page.fullurl)

                # чтение ассистентом первых двух предложений summary со страницы Wikipedia
                # (могут быть проблемы с мультиязычностью)
                self.play_voice_assistant_speech(
                    '. '.join(wiki_page.summary.split(".")[:5])
                ) # количество ситаемых предложений
                # тут можно ещё однуу функцию расписать при желании
            else:
                # открытие ссылки на поисковик в браузере в случае, если на Wikipedia не удалось найти ничего по запросу
                self.play_voice_assistant_speech(self.translator.get(
                    "Can't find {} on Wikipedia. But here is what I found on google").format(search_term))
                url = "https://google.com/search?q=" + search_term
                webbrowser.get().open(url)

        # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
        except:
            self.play_voice_assistant_speech(self.translator.get("Seems like we have a trouble. See logs for more information"))
            traceback.print_exc()
            return

    def get_translation(self, *args: tuple):
        """
        Получение перевода текста с одного языка на другой (в данном случае с изучаемого на родной язык или обратно)
        :param args: фраза, которую требуется перевести
        """
        if not args[0]: return

        search_term = " ".join(args[0])
        google_translator = googletrans.Translator()
        translation_result = ""

        old_assistant_language = self.speech_language
        try:
            # если язык речи ассистента и родной язык пользователя различаются, то перевод выполяется на родной язык
            if self.speech_language != self.person.native_language:
                translation_result = google_translator.translate(search_term,  # что перевести
                                                        src=self.person.target_language,  # с какого языка
                                                        dest=self.person.native_language)  # на какой язык

                self.play_voice_assistant_speech("The translation for {} in Russian is".format(search_term))

                # смена голоса ассистента на родной язык пользователя (чтобы можно было произнести перевод)
                self.speech_language = self.person.native_language
                self.setup_assistant_voice()

            # если язык речи ассистента и родной язык пользователя одинаковы, то перевод выполяется на изучаемый язык
            else:
                translation_result = google_translator.translate(search_term,  # что перевести
                                                        src=self.person.native_language,  # с какого языка
                                                        dest=self.person.target_language)  # на какой язык
                self.play_voice_assistant_speech("По-английски {} будет как".format(search_term))

                # смена голоса ассистента на изучаемый язык пользователя (чтобы можно было произнести перевод)
                self.speech_language = self.person.target_language
                self.setup_assistant_voice()

            # произнесение перевода
            self.play_voice_assistant_speech(translation_result.text)

        # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
        except:
            self.play_voice_assistant_speech(self.translator.get("Seems like we have a trouble. See logs for more information"))
            traceback.print_exc()

        finally:
            # возвращение преждних настроек голоса помощника
            self.speech_language = old_assistant_language
            self.setup_assistant_voice()

    def get_weather_forecast(self, *args: tuple):
        """
        Получение и озвучивание прогнза погоды
        :param args: город, по которому должен выполняться запос
        """
        # в случае наличия дополнительного аргумента - запрос погоды происходит по нему,
        # иначе - используется город, заданный в настройках
        if args[0]:
            city_name = args[0][0]
        else:
            city_name = self.person.home_city

        try:
            # использование API-ключа, помещённого в .env-файл по примеру WEATHER_API_KEY = "01234abcd....."
            # никаких env, просто импортируем из соседнего файла
            weather_api_key = OWM_TOKEN
            open_weather_map = OWM(weather_api_key)

            # запрос данных о текущем состоянии погоды
            weather_manager = open_weather_map.weather_manager()
            observation = weather_manager.weather_at_place(city_name)
            weather = observation.weather

        # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
        except:
            self.play_voice_assistant_speech(self.translator.get("Seems like we have a trouble. See logs for more information"))
            traceback.print_exc()
            return

        # разбивание данных на части для удобства работы с ними
        status = weather.detailed_status
        temperature = weather.temperature('celsius')["temp"]
        wind_speed = weather.wind()["speed"]
        pressure = int(weather.pressure["press"] / 1.333)  # переведено из гПА в мм рт.ст.

        # вывод логов
        print(colored("Weather in " + city_name +
                    ":\n * Status: " + status +
                    "\n * Wind speed (m/sec): " + str(wind_speed) +
                    "\n * Temperature (Celsius): " + str(temperature) +
                    "\n * Pressure (mm Hg): " + str(pressure), "yellow"))

        # озвучивание текущего состояния погоды ассистентом (здесь для мультиязычности требуется дополнительная работа)
        self.play_voice_assistant_speech(self.translator.get("It is {0} in {1}").format(status, city_name))
        self.play_voice_assistant_speech(self.translator.get("The temperature is {} degrees Celsius").format(str(temperature)))
        self.play_voice_assistant_speech(self.translator.get("The wind speed is {} meters per second").format(str(wind_speed)))
        self.play_voice_assistant_speech(self.translator.get("The pressure is {} mm Hg").format(str(pressure)))

    def run_person_through_social_nets_databases(self, *args: tuple):
        """
        Поиск человека по базе данных социальных сетей ВКонтакте и Facebook
        :param args: имя, фамилия TODO город
        """
        if not args[0]: return

        google_search_term = " ".join(args[0])
        vk_search_term = "_".join(args[0])
        fb_search_term = "-".join(args[0])

        # открытие ссылки на поисковик в браузере
        url = "https://google.com/search?q=" + google_search_term + " site: vk.com"
        webbrowser.get().open(url)

        url = "https://google.com/search?q=" + google_search_term + " site: facebook.com"
        webbrowser.get().open(url)

        # открытие ссылкок на поисковики социальных сетей в браузере
        vk_url = "https://vk.com/people/" + vk_search_term
        webbrowser.get().open(vk_url)

        fb_url = "https://www.facebook.com/public/" + fb_search_term
        webbrowser.get().open(fb_url)

        self.play_voice_assistant_speech(
            self.translator.get("Here is what I found for {} on social nets").format(google_search_term)
        )


class VoiceAssistantWithAllSkills(
    VoiceAssistantWithInternetSkills,
    VoiceAssistantWithGUIControl
    ):
    """
    Класс, объединяющий все базовые модели ассистента
    """
    ...
