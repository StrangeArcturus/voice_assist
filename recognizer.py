import speech_recognition  # распознавание пользовательской речи (Speech-To-Text)
from vosk import Model, KaldiRecognizer # оффлайн-распознавание от Vosk
from termcolor import colored  # вывод цветных логов (для выделения распознанной речи)

from translation import Translation, translator
from voice_assistant import VoiceAssistant, assistant


import random
import traceback
import os
import wave
import json


class Recognizer:
    # инициализация инструментов распознавания и ввода речи
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()

    def __init__(self, translator: Translation, voice_assistant: VoiceAssistant) -> None:
        self.translator = translator
        self.voice_assistant = voice_assistant

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


recognizer = Recognizer(translator, assistant)
