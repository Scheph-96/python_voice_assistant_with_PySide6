# import all necessary modules

import os
import re
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path

import pyautogui
import pyttsx3
import speech_recognition as sr
import wikipedia
from pygame import mixer
from deep_translator import GoogleTranslator

import voice_assistant.util.utilities
from voice_assistant.util.tinyDBModal import LocalStorage


class Helena:
    """
        This is Helena's class describing all her features

        :attributes: None
    """

    def __init__(self):
        """
            The constructor for Helena Class
        """
        self.__engine = pyttsx3.init()
        self.__engine.setProperty('rate', 130)
        self.__localStorage = LocalStorage()
        self.__appLanguage = self.__localStorage.getFieldValue("appData", "language")

    def change_voice(self, engine):
        """
            This function changes the voice of Helena according to the voice properties of the OS.
        :param engine: pyttsx3 instance: Helena's voice engine
        :return:
        """
        for voice in engine.getProperty('voices'):
            # If you don't have this one it will select the default voice of your os
            if voice.name == "Microsoft Zira Desktop - English (United States)":
                engine.setProperty('voice', voice.id)
                break

    def speak(self, text):
        """
            This function return a voice note of the text gave as parameter
        :param text: string: The text which helena's voice engine will return as voice note
        :return:
        """
        self.change_voice(self.__engine)
        self.__engine.say(GoogleTranslator(source="auto", target=self.__appLanguage).translate(text))
        self.__engine.runAndWait()

    def who_am_i(self):
        """
            Helena introducing function
        :return:
        """
        identity = "I am Helena, version 1.0,  your voice assistant develop by Omar. I was created to make your life" \
                   " easier and to answer your needs regarding your computer. I am only a prototype that is not completely" \
                   " perfected but I will do my best to satisfy you"
        self.speak(identity)

    # Order listening function
    def take_command(self):
        """
            This function convert user's voice input in text
        :return: string: User voice input as text
        """
        print(GoogleTranslator(source="auto", target=self.__appLanguage).translate("speak"))
        recognize = sr.Recognizer()
        with sr.Microphone() as source:
            recognize.adjust_for_ambient_noise(source)
            audio = recognize.listen(source)

        try:
            print(GoogleTranslator(source="auto", target=self.__appLanguage).translate("Recognizing..."))
            query = recognize.recognize_google(audio)
            return query
        except Exception as e:
            print(e)
            return ""

    def sound_note(self):
        """
            This function launch a sound note which say that helena is listening
        :return:
        """
        mixer.init()
        mixer.music.load(os.fspath(Path(__file__).resolve().parent / "sound/helena_sound.mp3"))
        mixer.music.play()

    def user_data(self):
        """
            Set the user name
        :return:
        """
        self.speak("May i know your name? Keep in mind that you can't change it later.")
        username = self.take_command().lower()
        self.speak("Your name is ")
        self.speak(username)
        self.speak("Are you sure you want to save it ?")
        agreement = self.take_command().lower()
        if agreement not in [GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"), GoogleTranslator(source="auto", target=self.__appLanguage).translate("no")]:
            self.speak("Just say yes or no")
        else:
            if agreement == GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"):
                localStorage = LocalStorage()
                localStorage.insertUsername(username)
            else:
                self.speak("action cancelled")

    def greet(self):
        """
            Greetings function
        :return:
        """
        hour = datetime.now().hour

        if 6 <= hour < 12:
            self.speak("Good morning")
        elif 12 <= hour < 18:
            self.speak("Good afternoon")
        elif 18 <= hour < 6:
            self.speak("Good evening")

    def current_time(self):
        """
            This function give the current time
        :return:
        """
        current_time = datetime.now().strftime("%H:%M:%S")
        self.speak("It's " + current_time)

    def current_date(self):
        """
            This function give the current date
        :return:
        """
        current_date = datetime.now().strftime("%A %d %B %Y")
        self.speak("Today's date is " + current_date)

    def current_day(self):
        """
            This function give the current day
        :return:
        """
        current_day = datetime.now().strftime("%A")
        self.speak("Today is" + current_day)

    def wikipedia_search(self):
        """
            This function makes a research on wikipedia and return the first r sentences.
        :return:
        """
        self.speak("what should i look for?")
        query = self.take_command().lower()
        print("The query in wikipedia function: ", query)
        if query == "":
            self.speak("I don't get what you are saying !")
            time.sleep(0.3)
            self.speak("Would you like to try again ?")
            while True:
                answer = self.take_command().lower()
                if answer not in [GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"), GoogleTranslator(source="auto", target=self.__appLanguage).translate("no")]:
                    self.speak("Please just say yes or no")
                else:
                    if answer == GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"):
                        self.wikipedia_search()
                        break
                    else:
                        self.speak("cancelled")
                        break
        else:
            try:
                self.speak("Searching for " + query)

                if self.__appLanguage == "english":
                    wikipedia.set_lang("en")
                elif self.__appLanguage == "french":
                    wikipedia.set_lang("fr")

                result = wikipedia.summary(query, sentences=5, auto_suggest=False, redirect=True)
                print(result)
                self.speak(result)
            except wikipedia.exceptions.WikipediaException as exception:
                print(exception)
                # if type(exception) == wikipedia.exceptions.DisambiguationError:
                self.speak("Something went wrong with your request. Would you like to start over?")
                while True:
                    query = self.take_command().lower()
                    if query not in [GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"), GoogleTranslator(source="auto", target=self.__appLanguage).translate("no")]:
                        self.speak("Please just say yes or no")
                    else:
                        if query == GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"):
                            self.wikipedia_search()
                            break
                        else:
                            self.speak("cancelled")
                            break
                # elif type(exception) == wikipedia.exceptions.HTTPTimeoutError:
                #     self.speak("Something went wrong with your request. Would you like to start over?")
                #     while True:
                #         query = self.take_command().lower()
                #         if query not in ["yes", "no"]:
                #             self.speak("Please just say yes or no")
                #         else:
                #             if query == "yes":
                #                 self.wikipedia_search()
                #             else:
                #                 self.speak("cancelled")
                #                 break

    def to_remember(self):
        """
            This function allow helena to keep in mind somethings for the user
        :return:
        """
        self.speak("What should i remember?")
        memory = self.take_command()
        if memory != "":
            memorize_pattern = {"memory": memory, "date": datetime.now().strftime("%A %B %d, %Y"),
                                "hour": datetime.now().strftime("%H:%M:%S")}
            self.__localStorage.insertMemories(memorize_pattern)
            self.speak("You told me to remember " + memorize_pattern["memory"])
        else:
            self.speak("I don't get what you are saying !")
            time.sleep(0.3)
            self.speak("Would you like to try again ?")
            while True:
                query = self.take_command().lower()
                if query not in [GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"), GoogleTranslator(source="auto", target=self.__appLanguage).translate("no")]:
                    self.speak("Please just say yes or no")
                else:
                    if query == GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"):
                        self.to_remember()
                        break
                    else:
                        self.speak("cancelled")
                        break

    # def file_launcher(self):
    #     """
    #         This function looks for a file or group of file matching your request
    #     :return:
    #     :NB: This feature is not optimized, it may take some time depending on your computer capacities,
    #      so search time will vary between 1 second and 3 hours depending on the file searched
    #     """
    #
    #     isFind = False
    #
    #     self.speak("Which file would you like to launch?")
    #     to_launch = self.take_command().lower()
    #     print(to_launch)
    #
    #     if to_launch != "":
    #         self.speak("Do you want to launch "+to_launch+"?")
    #         confirm = self.take_command().lower()
    #         if confirm in ["yes", "no"]:
    #             if confirm == "yes":
    #                 self.speak("Searching for "+to_launch)
    #
    #                 resultAvailable = threading.Event()
    #                 thread = threading.Thread(target=voice_assistant.util.utilities.search_engine,
    #                                           args=[to_launch, resultAvailable, ])
    #                 thread.start()
    #                 filesFound = voice_assistant.util.utilities.search_control(resultAvailable, self.speak)
    #
    #                 self.speak("Which one would you like to launch?")
    #                 choice = self.take_command().lower()
    #
    #                 for path in filesFound:
    #                     if choice in path:
    #                         isFind = True
    #                         os.startfile(path)
    #                         break
    #
    #                 if not isFind:
    #                     self.speak("There is no file in the result named like that")
    #
    #                 time.sleep(0.3)
    #                 self.speak("Would you like to try again to launch a file in the above list?")
    #                 while True:
    #                     query = self.take_command().lower()
    #                     if query not in ["yes", "no"]:
    #                         self.speak("Please just say yes or no")
    #                     else:
    #                         if query == "yes":
    #                             pass
    #                             # self.file_launcher()
    #                             # break
    #                         else:
    #                             self.speak("Would you like to launch another file?")
    #                             while True:
    #                                 query = self.take_command().lower()
    #                                 if query not in ["yes", "no"]:
    #                                     self.speak("Please just say yes or no")
    #                                 else:
    #                                     if query == "yes":
    #                                         self.file_launcher()
    #                                         break
    #                                     else:
    #                                         self.speak("cancelled")
    #                                         break
    #                             self.speak("cancelled")
    #                             break
    #             else:
    #                 time.sleep(0.3)
    #                 self.speak("Would you like to try again ?")
    #                 while True:
    #                     query = self.take_command().lower()
    #                     if query not in ["yes", "no"]:
    #                         self.speak("Please just say yes or no")
    #                     else:
    #                         if query == "yes":
    #                             self.file_launcher()
    #                             break
    #                         else:
    #                             self.speak("cancelled")
    #                             break
    #         else:
    #             self.speak("Please just say yes or no")
    #             while True:
    #                 query = self.take_command().lower()
    #                 if query not in ["yes", "no"]:
    #                     self.speak("Please just say yes or no")
    #                 else:
    #                     if query == "yes":
    #                         self.file_launcher()
    #                         break
    #                     else:
    #                         self.speak("cancelled")
    #     else:
    #         self.speak("I don't get what you are saying !")
    #         time.sleep(0.3)
    #         self.speak("Would you like to try again ?")
    #         while True:
    #             query = self.take_command().lower()
    #             if query not in ["yes", "no"]:
    #                 self.speak("Please just say yes or no")
    #             else:
    #                 if query == "yes":
    #                     self.file_launcher()
    #                     break
    #                 else:
    #                     self.speak("cancelled")
    #                     break

    def screenshot(self):
        """
            This function takes a screenshot
        :return:
        """
        img = pyautogui.screenshot()
        filename = voice_assistant.util.utilities.screenshots_filename_generator()
        folder_path = os.path.normpath(os.path.expanduser("~/Pictures/")) + "\\"
        file_path = folder_path + filename
        img.save(file_path)
        self.speak("screenshot took successfully")

    def string_to_binary(self):
        """
            This function convert string to binary
        :return:
        """
        asciiList, binaryList, result = [], [], ""

        self.speak("Which sentence or word would you like to convert to binary ?")
        string = self.take_command().lower()

        if string == "":
            self.speak("I don't get what you are saying !")
            time.sleep(0.3)
            self.speak("Would you like to try again ?")
            while True:
                answer = self.take_command().lower()
                if answer not in [GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"), GoogleTranslator(source="auto", target=self.__appLanguage).translate("no")]:
                    self.speak("Please just say yes or no")
                else:
                    if answer == GoogleTranslator(source="auto", target=self.__appLanguage).translate("yes"):
                        self.string_to_binary()
                        break
                    else:
                        self.speak("cancelled")
                        break
        else:
            for char in string:
                asciiList.append(ord(char))
            for asciiCode in asciiList:
                if int(bin(asciiCode)[2:]) != 100000:
                    binaryList.append(str(int(bin(asciiCode)[2:])))

            result = string + " in binary is " + "".join(binaryList)
            print(result)
            self.speak(result)

    def launch_source_code_page(self):
        """
            This function launch the source code github page
        :return:
        """
        # self.speak("Would you like to see the web page or directly download the source code?")
        # answer = self.take_command().lower()
        #
        # code = ""
        # localStorage = LocalStorage()
        # patterns = localStorage.getPatterns()
        # for pattern in patterns:
        #     if re.search(pattern['pattern'], answer):
        #         code = pattern['code']
        #         break

        # if code == "00download00source00code00":
        #     cmd = '!git clone https://github.com/Scheph-96/python_voice_assistant_with_PySide6.git '+voice_assistant.util.utilities.DOWNLOADSPATH
        #     check_output(cmd, shell=True).decode()
        # el
        # if code == "00open00source00code00":
        webbrowser.open("https://github.com/Scheph-96/python_voice_assistant_with_PySide6")

    # def shutdown(self):
    #     """
    #         This function shutdown your computer
    #     :return:
    #     """
    #     self.speak("Do you really want to shutdown?")
    #     answer = self.take_command().lower()
    #     if answer == "yes":
    #         self.speak("Shutting down the computer")
    #         os.startfile(os.fspath(Path(__file__).resolve().parent / "system/shutdown.bat"))
    #     elif answer == "no":
    #         self.speak("Process abort")
    #     else:
    #         self.speak("I do not understand. Process abort")
    #
    # def restart(self):
    #     """
    #         This function reboot your computer
    #     :return:
    #     """
    #     self.speak("Do you really want to restart?")
    #     answer = self.take_command().lower()
    #     if answer == "yes":
    #         self.speak("Reboot")
    #         os.system("shutdown /r /t 1")
    #     elif answer == "no":
    #         self.speak("Process abort")
    #     else:
    #         self.speak("I do not understand. Process abort")
    #
    # def logout(self):
    #     """
    #         This function logout from your current windows session
    #     :return:
    #     """
    #     self.speak("Do you really want to logout?")
    #     answer = self.take_command().lower()
    #     if answer == "yes":
    #         self.speak("Logout")
    #         os.startfile("shutdown -l")
    #     elif answer == "no":
    #         self.speak("Process abort")
    #     else:
    #         self.speak("I do not understand. Process abort")
