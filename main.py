"""
Проект голосового ассистента на Python 3 от восхитительной EnjiRouz :Р
(её изначальный исходник: https://github.com/EnjiRouz/Voice-Assistant-App/blob/master/app.py)
И дополненный начинающим в программировании, Arc.
Помощник умеет:
* распознавать и синтезировать речь в offline-моде (без доступа к Интернету);
* сообщать о прогнозе погоды в любой точке мира;
* производить поисковый запрос в поисковой системе Google
  (а также открывать список результатов и сами результаты данного запроса);
* производить поисковый запрос видео в системе YouTube и открывать список результатов данного запроса;
* выполнять поиск определения в Wikipedia c дальнейшим прочтением первых двух (поправка Arc.: пяти) предложений;
* искать человека по имени и фамилии в соцсетях ВКонтакте и Facebook;
* "подбрасывать монетку";
* переводить с изучаемого языка на родной язык пользователя (с учетом особенностей воспроизведения речи)
  (почему-то не работает... Arc. будет изучать...);
* воспроизводить случайное приветствие;
* воспроизводить случайное прощание с последующим завершением работы программы;
* менять настройки языка распознавания и синтеза речи;
* TODO........
(далее дополнения от Arc.)
* говорить нынешнее время;
* сообщать сегодняшнюю дату;
* молчать на 10 минут;
Голосовой ассистент использует для синтеза речи встроенные в операционную систему Windows 10 возможности
(т.е. голоса зависят от операционной системы). Для этого используется библиотека pyttsx3
Для корректной работы системы распознавания речи в сочетании с библиотекой SpeechRecognition
используется библиотека PyAudio для получения звука с микрофона.
Для установки PyAudio можно найти и скачать нужный в зависимости от архитектуры и версии Python whl-файл здесь:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
Загрузив файл в папку с проектом, установку можно будет запустить с помощью подобной команды:
pip install PyAudio-0.2.11-cp38-cp38m-win_amd64.whl
Для использования SpeechRecognition в offline-режиме (без доступа к Интернету), потребуется дополнительно установить
vosk, whl-файл для которого можно найти здесь в зависимости от требуемой архитектуры и версии Python:
https://github.com/alphacep/vosk-api/releases/
Загрузив файл в папку с проектом, установку можно будет запустить с помощью подобной команды:
pip install vosk-0.3.7-cp38-cp38-win_amd64.whl
Для получения данных прогноза погоды мною был использован сервис OpenWeatherMap, который требует API-ключ.
Получить API-ключ и ознакомиться с документацией можно после регистрации (есть Free-тариф) здесь:
https://openweathermap.org/
Команды для установки прочих сторонних библиотек:
pip install google
pip install SpeechRecognition
pip install pyttsx3
pip install wikipedia-api
pip install googletrans
pip install python-dotenv
pip install pyowm
pip install pymorphy2 #(by Arc.)
pip install num2words #(by Arc.)
Для быстрой установки всех требуемых зависимостей можно воспользоваться командой:
pip install requirements.txt
Дополнительную информацию по установке и использованию библиотек можно найти здесь:
https://pypi.org/
"""


from datetime import datetime as dt # работа с датой и временем
from time import sleep # для "сна" ассистента
from num2words import num2words as nw # для проговаривания слов
import pymorphy2 # для склонения этих слов
from vosk import Model, KaldiRecognizer  # оффлайн-распознавание от Vosk
from googlesearch import search  # поиск в Google
from pyowm import OWM  # использование OpenWeatherMap для получения данных о погоде
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from dotenv import load_dotenv  # загрузка информации из .env-файла
import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
import googletrans  # использование системы Google Translate
import pyttsx3  # синтез речи (Text-To-Speech)
import wikipediaapi  # поиск определений в Wikipedia
import random  # генератор случайных чисел
import webbrowser  # работа с использованием браузера по умолчанию (открывание вкладок с web-страницей)
import traceback  # вывод traceback без остановки работы программы при отлове исключений
import json  # работа с json-файлами и json-строками
import wave  # создание и чтение аудиофайлов формата wav
import os  # работа с файловой системой
import pyautogui # работа с курсором

from TOKEN import OWM_TOKEN


pyautogui.FAILSAFE = False


class Translation:
    """
    Получение вшитого в приложение перевода строк для создания мультиязычного ассистента
    """
    with open("translations.json", "r", encoding="UTF-8") as file:
        translations = json.load(file)

    def get(self, text: str):
        """
        Получение перевода строки из файла на нужный язык (по его коду)
        :param text: текст, который требуется перевести
        :return: вшитый в приложение перевод текста
        """
        if text in self.translations:
            return self.translations[text][assistant.speech_language]
        else:
            # в случае отсутствия перевода происходит вывод сообщения об этом в логах и возврат исходного текста
            print(colored("Not translated phrase: {}".format(text), "red"))
            return text


class OwnerPerson:
    """
    Информация о владельце, включающие имя, город проживания, родной язык речи, изучаемый язык (для переводов текста)
    """
    name = ""
    home_city = ""
    native_language = ""
    target_language = ""


class VoiceAssistant:
    """
    Настройки голосового ассистента, включающие имя, пол, язык речи
    Примечание: для мультиязычных голосовых ассистентов лучше создать отдельный класс,
    который будет брать перевод из JSON-файла с нужным языком
    """
    name = ""
    sex = ""
    speech_language = ""
    recognition_language = ""


def setup_assistant_voice():
    """
    Установка голоса по умолчанию (индекс может меняться в зависимости от настроек операционной системы)
    """
    voices = ttsEngine.getProperty("voices")

    if assistant.speech_language == "en":
        assistant.recognition_language = "en-US"
        if assistant.sex == "female":
            # Microsoft Zira Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[1].id)
        else:
            # Microsoft David Desktop - English (United States)
            ttsEngine.setProperty("voice", voices[2].id)
    else:
        assistant.recognition_language = "ru-RU"
        # Microsoft Irina Desktop - Russian
        ttsEngine.setProperty("voice", voices[0].id)


def record_and_recognize_audio(*args: tuple):
    """
    Запись и распознавание аудио
    """
    with microphone:
        recognized_data = ""

        # запоминание шумов окружения для последующей очистки звука от них
        recognizer.adjust_for_ambient_noise(microphone, duration=2)

        rnd_mic = random.choice((0, 1))
        try:
            if rnd_mic == 0:
                print(translator.get("Listening..."))
            else:
                play_voice_assistant_speech(translator.get("Listening..."))
                print(translator.get("Listening..."))
            audio = recognizer.listen(microphone, 5, 5)

            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())

        except speech_recognition.WaitTimeoutError:
            if rnd_mic == 0:
                print(translator.get("Can you check if your microphone is on, please?"))
            else:
                play_voice_assistant_speech(translator.get("Can you check if your microphone is on, please?"))
                print(translator.get("Can you check if your microphone is on, please?"))
            # то же самое, что и выше, только при ошибке
            
            traceback.print_exc()
            return

        # использование online-распознавания через Google (высокое качество распознавания)
        try:
            print("Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language=assistant.recognition_language).lower()

        except speech_recognition.UnknownValueError:
            pass  # play_voice_assistant_speech("What did you say again?")

        # в случае проблем с доступом в Интернет происходит попытка использовать offline-распознавание через Vosk
        except speech_recognition.RequestError:
            print(colored("Trying to use offline recognition...", "cyan"))
            recognized_data = use_offline_recognition()

        return recognized_data


def use_offline_recognition():
    """
    Переключение на оффлайн-распознавание речи
    :return: распознанная фраза
    """
    recognized_data = ""
    try:
        # проверка наличия модели на нужном языке в каталоге приложения
        if not os.path.exists("models/vosk-model-small-" + assistant.speech_language + "-0.4"):
            print(colored("Please download the model from:\n"
                          "https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.",
                          "red"))
            exit(1)

        # анализ записанного в микрофон аудио (чтобы избежать повторов фразы)
        wave_audio_file = wave.open("microphone-results.wav", "rb")
        model = Model("models/vosk-model-small-" + assistant.speech_language + "-0.4")
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


def play_voice_assistant_speech(text_to_speech):
    """
    Проигрывание речи ответов голосового ассистента (без сохранения аудио)
    :param text_to_speech: текст, который нужно преобразовать в речь
    """
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()


def play_greetings(*args: tuple):
    """
    Проигрывание случайной приветственной речи
    """
    greetings = [
        translator.get("Hello, {}! How can I help you today?").format(person.name),
        translator.get("Good day to you {}! How can I help you today?").format(person.name)
    ]
    play_voice_assistant_speech(greetings[random.randint(0, len(greetings) - 1)])


def play_farewell_and_quit(*args: tuple):
    """
    Проигрывание прощательной речи и выход
    """
    farewells = [
        translator.get("Goodbye, {}! Have a nice day!").format(person.name),
        translator.get("See you soon, {}!").format(person.name)
    ]
    play_voice_assistant_speech(farewells[random.randint(0, len(farewells) - 1)])
    ttsEngine.stop()
    quit()


def search_for_term_on_google(*args: tuple):
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
                        lang=assistant.speech_language,  # используется язык, на котором говорит ассистент
                        num=1,  # количество результатов на странице
                        start=0,  # индекс первого извлекаемого результата
                        stop=1,  # индекс последнего извлекаемого результата (я хочу, чтобы открывался первый результат)
                        pause=1.0,  # задержка между HTTP-запросами
                        ):
            search_results.append(_)
            webbrowser.get().open(_)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return

    print(search_results)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on google").format(search_term))


def search_for_video_on_youtube(*args: tuple):
    """
    Поиск видео на YouTube с автоматическим открытием ссылки на список результатов
    :param args: фраза поискового запроса
    """
    if not args[0]: return
    search_term = " ".join(args[0])
    url = "https://www.youtube.com/results?search_query=" + search_term
    webbrowser.get().open(url)
    play_voice_assistant_speech(translator.get("Here is what I found for {} on youtube").format(search_term))


def search_for_definition_on_wikipedia(*args: tuple):
    """
    Поиск в Wikipedia определения с последующим озвучиванием результатов и открытием ссылок
    :param args: фраза поискового запроса
    """
    if not args[0]: return

    search_term = " ".join(args[0])

    # установка языка (в данном случае используется язык, на котором говорит ассистент)
    wiki = wikipediaapi.Wikipedia(assistant.speech_language)

    # поиск страницы по запросу, чтение summary, открытие ссылки на страницу для получения подробной информации
    wiki_page = wiki.page(search_term)
    try:
        if wiki_page.exists():
            play_voice_assistant_speech(translator.get("Here is what I found for {} on Wikipedia").format(search_term))
            webbrowser.get().open(wiki_page.fullurl)

            # чтение ассистентом первых двух предложений summary со страницы Wikipedia
            # (могут быть проблемы с мультиязычностью)
            play_voice_assistant_speech(wiki_page.summary.split(".")[:5]) # количество ситаемых предложений
            # тут можно ещё однуу функцию расписать при желании
        else:
            # открытие ссылки на поисковик в браузере в случае, если на Wikipedia не удалось найти ничего по запросу
            play_voice_assistant_speech(translator.get(
                "Can't find {} on Wikipedia. But here is what I found on google").format(search_term))
            url = "https://google.com/search?q=" + search_term
            webbrowser.get().open(url)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()
        return


def get_translation(*args: tuple):
    """
    Получение перевода текста с одного языка на другой (в данном случае с изучаемого на родной язык или обратно)
    :param args: фраза, которую требуется перевести
    """
    if not args[0]: return

    search_term = " ".join(args[0])
    google_translator = googletrans.Translator()
    translation_result = ""

    old_assistant_language = assistant.speech_language
    try:
        # если язык речи ассистента и родной язык пользователя различаются, то перевод выполяется на родной язык
        if assistant.speech_language != person.native_language:
            translation_result = google_translator.translate(search_term,  # что перевести
                                                      src=person.target_language,  # с какого языка
                                                      dest=person.native_language)  # на какой язык

            play_voice_assistant_speech("The translation for {} in Russian is".format(search_term))

            # смена голоса ассистента на родной язык пользователя (чтобы можно было произнести перевод)
            assistant.speech_language = person.native_language
            setup_assistant_voice()

        # если язык речи ассистента и родной язык пользователя одинаковы, то перевод выполяется на изучаемый язык
        else:
            translation_result = google_translator.translate(search_term,  # что перевести
                                                      src=person.native_language,  # с какого языка
                                                      dest=person.target_language)  # на какой язык
            play_voice_assistant_speech("По-английски {} будет как".format(search_term))

            # смена голоса ассистента на изучаемый язык пользователя (чтобы можно было произнести перевод)
            assistant.speech_language = person.target_language
            setup_assistant_voice()

        # произнесение перевода
        play_voice_assistant_speech(translation_result.text)

    # поскольку все ошибки предсказать сложно, то будет произведен отлов с последующим выводом без остановки программы
    except:
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
        traceback.print_exc()

    finally:
        # возвращение преждних настроек голоса помощника
        assistant.speech_language = old_assistant_language
        setup_assistant_voice()


def get_weather_forecast(*args: tuple):
    """
    Получение и озвучивание прогнза погоды
    :param args: город, по которому должен выполняться запос
    """
    # в случае наличия дополнительного аргумента - запрос погоды происходит по нему,
    # иначе - используется город, заданный в настройках
    if args[0]:
        city_name = args[0][0]
    else:
        city_name = person.home_city

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
        play_voice_assistant_speech(translator.get("Seems like we have a trouble. See logs for more information"))
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
    play_voice_assistant_speech(translator.get("It is {0} in {1}").format(status, city_name))
    play_voice_assistant_speech(translator.get("The temperature is {} degrees Celsius").format(str(temperature)))
    play_voice_assistant_speech(translator.get("The wind speed is {} meters per second").format(str(wind_speed)))
    play_voice_assistant_speech(translator.get("The pressure is {} mm Hg").format(str(pressure)))


def change_language(*args: tuple):
    """
    Изменение языка голосового ассистента (языка распознавания речи)
    """
    assistant.speech_language = "ru" if assistant.speech_language == "en" else "en"
    setup_assistant_voice()
    print(colored("Language switched to " + assistant.speech_language, "cyan"))


def run_person_through_social_nets_databases(*args: tuple):
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

    play_voice_assistant_speech(translator.get("Here is what I found for {} on social nets").format(google_search_term))


def toss_coin(*args: tuple):
    """
    "Подбрасывание" монетки для выбора из 2 опций
    """
    flips_count, heads, tails = 3, 0, 0

    for flip in range(flips_count):
        if random.randint(0, 1) == 0:
            heads += 1

    tails = flips_count - heads
    winner = "Tails" if tails > heads else "Heads"
    play_voice_assistant_speech(translator.get(winner) + " " + translator.get("won"))


def now_time(*args: tuple):
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
    play_voice_assistant_speech(translator.get(string_time) + " " + str(now_t))
    print(f'{translator.get(string_time)} {str(now_t)}')
    

def now_date(*args: tuple):
    """
    сообщение сегодняшней даты
    """
    now_d = dt.now().date().strftime("%A\t%d %B %Y")
    # получаем сегодняшнюю дату и тут же приводим её к +- норм виду
    morph = pymorphy2.MorphAnalyzer() # для преобразовашек числительных
    day_name, other_date = now_d.split('\t')
    # получаем имя дня и "остальную дату"
    if assistant.speech_language == 'ru':
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
    if assistant.speech_language == 'ru':
        month_name = morph.parse(translator.get(other_date.split()[1]))[0].inflect({'gent'}).word
        # приводим имя месяца к родительному падежу
    else:
        month_name = translator.get(other_date.split()[1])
    if assistant.speech_language == 'ru':
        year = nw(int(other_date.split()[2]), lang='ru', to='ordinal').split()
        # преобразуем уже номер года, и тоже к ПОРЯДКОВОМУ ЧИСЛИТЕЛЬНОМУ
        # так как год мужского рода, то далее изменений не производим
        year = ' '.join(year) # соединяем в одну строку и порядковый года
    else:
        year = nw(int(other_date.split()[2]), to='ordinal')
    answer = f"{translator.get('Today is')} {translator.get(day_name)} {day_num} {month_name} {year} год"
    print(answer)
    play_voice_assistant_speech(answer)


def shut_up(*args: tuple):
    """
    Заставляет голосового ассистента помолчать на 10 минут
    """
    answer = translator.get("Okey, I'll start to you again and answering in 10 minutes")
    print(answer)
    play_voice_assistant_speech(answer)
    sleep(600)


def thanks(*args: tuple):
    """
    Ответ на благодарность пользователя
    """
    answer = random.choice(((translator.get("Glad to serve")), translator.get("Nothing to thanks"), translator.get("Created to serve")))
    print(answer)
    play_voice_assistant_speech(answer)


def window_off(*args: tuple):
    """
    Закрывает все окна, хе-хе~
    """
    pyautogui.FAILSAFE = False
    size = pyautogui.size()
    x = size.width
    y = size.height
    pyautogui.moveTo(x=x, y=y, duration=1)
    pyautogui.click(clicks=1)
    play_voice_assistant_speech("окна закрываются")


def execute_command_with_name(command_name: str, *args: list):
    """
    Выполнение заданной пользователем команды и аргументами
    :param command_name: название команды
    :param args: аргументы, которые будут переданы в метод
    :return:
    """
    for key in commands.keys():
        if command_name in key:
            commands[key](*args)
        else:
            pass  # print("Command not found")


# перечень команд для использования (качестве ключей словаря используется hashable-тип tuple)
# в качестве альтернативы можно использовать JSON-объект с намерениями и сценариями
# (подобно тем, что применяют для чат-ботов)
commands = {
    (
        "hello", "hi", "morning",
        "привет", "приветик", "хай", "здорово",
        "добрый день", "добрый вечер", "доброе утро"): play_greetings,
    (
        "bye", "goodbye", "quit", "exit", "stop",
        "пока", "пока-пока", "прощай", "до встречи"): play_farewell_and_quit,
    ("search", "google", "find", "найди"): search_for_term_on_google,
    (
        "video", "youtube", "watch",
        "видео", "ютуб", "ютьюб"): search_for_video_on_youtube,
    (
        "wikipedia", "definition", "about",
        "определение", "википедия", "вики"): search_for_definition_on_wikipedia,
    (
        "translate", "interpretation", "translation",
        "перевод", "перевести", "переведи"): get_translation,
    ("language", "язык"): change_language,
    ("weather", "forecast", "погода", "прогноз"): get_weather_forecast,
    ("facebook", "person", "run", "пробей", "контакт"): run_person_through_social_nets_databases,
    ("toss", "coin", "монета", "подбрось"): toss_coin,
    ("который час", "который сейчас час"): now_time,
    ("сколько время", "сколько сейчас время"): now_time,
    ("время", "время сейчас", "сейчас время"): now_time,
    ("time", "time now"): now_time,
    ("date", "date now",
    "дата", "дата сейчас",
    "сегодняшний день", "день сегодня", "день", "сегодня день"): now_date,
    ("shut up", "shut up please"): shut_up,
    ("помолчи", "молчи", "замолчи"): shut_up,
    ("помолчи 10 минут", "замолчи на 10 минут", "молчать"): shut_up,
    ("thank you", "thanks"): thanks,
    ("спасибо", "благодарю", "спасибо тебе"): thanks,
    ("close all", "close all windows", "close windows"): window_off,
    ("сверни все окна", "сверни всё", "сверни окна", "сворачивай всё"): window_off
}

if __name__ == "__main__":

    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    # инициация морфологического анализатора (в частности, пока что для чисел в дате)
    morph = pymorphy2.MorphAnalyzer()

    # инициализация инструмента синтеза речи
    ttsEngine = pyttsx3.init()

    # настройка данных пользователя
    person = OwnerPerson()
    person.name = "Пользователь"
    person.home_city = "Sterlitamak"
    person.native_language = "ru"
    person.target_language = "en"

    # настройка данных голосового помощника
    assistant = VoiceAssistant()
    assistant.name = "Кортана"
    assistant.sex = "female"
    assistant.speech_language = "ru"

    # установка голоса по умолчанию
    setup_assistant_voice()

    # добавление возможностей перевода фраз (из заготовленного файла)
    translator = Translation()

    # загрузка информации из .env-файла (там лежит API-ключ для OpenWeatherMap)
    # нет, он в соседнем файле, лень дотэнв делать :(
    load_dotenv()

    play_greetings()

    while True:
        try:
            # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
            voice_input = record_and_recognize_audio()
            os.remove("microphone-results.wav")
            print(colored(voice_input, "blue"))

            # отделение комманд от дополнительной информации (аргументов)
            voice_input = voice_input.split(" ")
            command = voice_input[0]
            command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
            execute_command_with_name(command, command_options)
        except Exception as err:
            print(f"ПРОИЗОШЛА ОШИБКА\n{err}")
# TODO food order
# TODO recommend film by rating/genre (use recommendation system project)
#  как насчёт "название фильма"? Вот его описание:.....