import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
import threading
import speech_recognition
import pyttsx3 as tts
from neuralintents import GenericAssistant
from kivy.utils import platform
from kivy.clock import Clock

recogrnizer = speech_recognition.Recognizer()

speaker = tts.init()
speaker.setProperty('rate', 150)

if platform == 'android':
    from jnius import autoclass

    PackageManager = autoclass('android.content.pm.PackageManager')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')

class MainGrid(GridLayout):
    name = ObjectProperty(None)
    email = ObjectProperty(None)

    def btn(self):
        print("Name:", self.name.text, "email:", self.email.text)
        self.name.text = "Good"
        self.email.text = "Good"

class BromaxApp(App):

    def check_and_open_youtube(self):
        if platform != 'android':
            speaker.say("This function is only for Android.")
            speaker.runAndWait()
            return

        package_name = "com.google.android.youtube"
        manager = PythonActivity.mActivity.getPackageManager()

        # Check if YouTube app is installed
        is_installed = False
        try:
            manager.getPackageInfo(package_name, 0)
            is_installed = True
        except:
            is_installed = False

        # If installed, open YouTube app
        if is_installed:
            intent = manager.getLaunchIntentForPackage(package_name)
            PythonActivity.mActivity.startActivity(intent)
        # If not installed, open YouTube in the browser
        else:
            intent = Intent(Intent.ACTION_VIEW)
            intent.setData(Uri.parse("https://www.youtube.com"))
            PythonActivity.mActivity.startActivity(intent)

    def greeting(self):
        speaker.say("Hello. What can I do for you?")
        speaker.runAndWait()

    def exit(self):
        speaker.say("Bye")
        speaker.runAndWait()

        # self.start_audio_thread()

    def create_note(self):
        speaker.say("Opening Youtube...")
        speaker.runAndWait()

        self.check_and_open_youtube()

    def read_audio(self):
        global recogrnizer
        global filenum
        print("Read auio started")
        while True:
            try:
                with speech_recognition.Microphone() as mic:
                    recogrnizer.adjust_for_ambient_noise(mic, duration=0.2)
                    audio = recogrnizer.listen(mic)
                    
                    message = recogrnizer.recognize_google(audio)
                    message = message.lower()
                    print(message)

                self.assistant.process_input(message)
            
                Clock.schedule_once(lambda dt: setattr(self.main_grid.name, 'text', message))

            except speech_recognition.UnknownValueError:
                recogrnizer = speech_recognition.Recognizer()

    def start_audio_thread(self):
        t = threading.Thread(target=self.read_audio)
        t.start()

    def on_start(self):
        print("App started")
        mapping = {'greeting': self.greeting, "exit": self.exit, "creat_note": self.create_note}
        self.assistant = GenericAssistant('intents.json', method_mappings=mapping)
        self.assistant.fit_model()
        self.assistant.save_model()
        self.start_audio_thread()

    def build(self):
        self.main_grid = MainGrid()
        return self.main_grid

if __name__ == "__main__":
    app = BromaxApp()
    app.run()