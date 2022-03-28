from googlesearch import search  # поиск в Google
import wikipediaapi  # поиск определений в Wikipedia
import googletrans  # использование системы Google Translate
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)
from pyowm import OWM  # использование OpenWeatherMap для получения данных о погоде

import webbrowser  # работа с использованием браузера по умолчанию (открывание вкладок с web-страницей)
import traceback

from __voice_assistant import VoiceAssistant

from TOKEN import OWM_TOKEN


class VoiceAssistantWithInternetSkills(VoiceAssistant):
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
