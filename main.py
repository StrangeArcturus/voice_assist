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
from num2words import num2words as nw # для проговаривания слов
import pymorphy2 # для склонения этих слов
from dotenv import load_dotenv  # загрузка информации из .env-файла
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
import random  # генератор случайных чисел
import traceback  # вывод traceback без остановки работы программы при отлове исключений
import os  # работа с файловой системой
import pyautogui # работа с курсором

from translation import Translation, translator
from owner_person import OwnerPerson, person
from voice_assistant import VoiceAssistantWithAllSkills, assistant
from recognizer import Recognizer, recognizer


pyautogui.FAILSAFE = False


def main():
    # инициация морфологического анализатора (в частности, пока что для чисел в дате)
    morph = pymorphy2.MorphAnalyzer()

    # настройка данных пользователя
    person.name = "Пользователь"
    person.home_city = "Sterlitamak"
    person.native_language = "ru"
    person.target_language = "en"

    # настройка данных голосового помощника
    assistant.name = "Кортана"
    assistant.sex = "female"
    assistant.speech_language = "ru"

    # установка голоса по умолчанию
    assistant.setup_assistant_voice()
    # добавление возможностей перевода фраз (из заготовленного файла)

    # загрузка информации из .env-файла (там лежит API-ключ для OpenWeatherMap)
    # нет, он в соседнем файле, лень дотэнв делать :(
    load_dotenv()

    assistant.play_greetings()

    while True:
        try:
            # старт записи речи с последующим выводом распознанной речи и удалением записанного в микрофон аудио
            voice_input = recognizer.record_and_recognize_audio()
            os.remove("microphone-results.wav")
            print(colored(voice_input, "blue"))

            # отделение комманд от дополнительной информации (аргументов)
            voice_input = voice_input.split(" ")
            command = voice_input[0]
            command_options = [str(input_part) for input_part in voice_input[1:len(voice_input)]]
            execute_command_with_name(command, command_options)
        except Exception as err:
            print(f"ПРОИЗОШЛА ОШИБКА\n{err}")


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
    main()

# TODO food order
# TODO recommend film by rating/genre (use recommendation system project)
#  как насчёт "название фильма"? Вот его описание:.....
