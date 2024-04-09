import kivymd.icon_definitions




from gtts import gTTS

import random
import os
import openai

import configparser
from base64 import b64decode
import webbrowser
# import openai.error
# from openai.error import OpenAIError
# from openai.error import InvalidRequestError

from moviepy.editor import *

from kivy.uix.video import Video
# from kivy.uix.video import VideoPlayer

# from kivymd.uix.videoplayer import VideoPlayer


# from kivymd.uix.videoplayer import MDVideoPlayer

#os.environ["KIVY_VIDEO"] = "ffpyplayer"

import kivy.uix.video

from kivy.uix.boxlayout import BoxLayout


from kivy.utils import get_color_from_hex

# from download_webfile import download_webfile


from kivy.graphics import RoundedRectangle

# from roundedbutton import RoundedButton

from kivy.uix.label import Label

from kivy.config import Config

#Config.set('graphics', 'video', 'ffpyplayer')

import sys
from io import StringIO

from kivy.clock import Clock

from kivy.uix.videoplayer import VideoPlayer


from pydub import AudioSegment

from kivy.core.audio import SoundLoader
from kivy.core.window import Window
import uuid
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechSynthesizer
from azure.cognitiveservices.speech import ResultReason

"""from translate import Translator"""

import asyncio

"""
from translate import Translator as TranslateLib

from mtranslate import translate as mtranslate"""

from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
import json

from kivy.uix.textinput import TextInput

import requests

# import pyrebase
from kivy.uix.button import Button

from kivy.uix.floatlayout import FloatLayout
import firebase_admin
from firebase_admin import firestore

# from kivymd.uix.videoplayer import MDVideoPlayer

from firebase_admin import credentials
from firebase_admin import initialize_app
from firebase_admin import auth

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ListProperty

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from kivy.uix.image import Image

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton

# import numpy as np
# import cv2

# from kivy.core.video import ffmpeg
# import ffpyplayer

# from ffvideo import VideoStream
# import ffmpeg
# import ffmpeg

from moviepy.video.compositing.concatenate import concatenate_videoclips

import librosa

import wave, struct

from flask import Flask, redirect, url_for, session

from flask import request, jsonify

app = Flask(__name__)

def calculate_window_size():
    screen_width = Window.width
    screen_height = Window.height

    # Set the desired aspect ratio
    desired_aspect_ratio = 9 / 16  # Portrait aspect ratio

    # Calculate the new width and height to maintain the aspect ratio
    if screen_width / screen_height > desired_aspect_ratio:
        new_width = screen_height * desired_aspect_ratio
        new_height = screen_height
    else:
        new_width = screen_width
        new_height = screen_width / desired_aspect_ratio

    return new_width, new_height

# To change window size dynamically but stretch coming
Window.size = (310,580)
#Window.size = calculate_window_size()




firebase_credentials = {
    "type": "service_account",
    "project_id": "icystrisall",
    "private_key_id": "3340d35fc5653e89b04557d7808c89c6d3899afb",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCcxS/jsurlU4x9\nTp89ObsDWjgIBh1Sa30IrLT9Y9gKZhXbCe4Ew5HyLCIMWfnqZi9fKaitcUuniBdI\n9bvmN30z4PtHzO4OX20ChDKQuQPrs3EpLx4fma5Yo2MisgJCzf4WYv6FVJOC0pbF\nNhEIHBKngCyDR9QqedPZSJZ5uD8dWPac40LI6YYuRIsZDPDuwbVtiXNWqfHLQBPg\nFqVRRzu1bBoTTgZs3JFOwJ3PX00YfRfUO4tb+5kr9manTvspksO+kjjdc/453/2v\noB6iqlNOUorgPh5KTmFRJXMLuUad5wF3wWLVjtgsB8HQ4ksz7loPoFx5bSpxNICH\n7ofPqRZ3AgMBAAECggEAHx0nrwpgglk9pdUH16/whO7P9g+4nBYHP8R/O1colo/C\nQLHM0pc6DRVjQI5PAo17U2jCOIIm4L4q2OkkfMGAkN5TIOH0UVfxG7G/E2gU9h+s\nEt9uHBl1N9RdpZIszrNxfWHyX+X0TN+c2tErOi/QJ/xRWVDVNATv3c0BSHEf3aPt\n5U8ltz+o3jxbdGuEl4p5MUJzW7FAo8aMxj2pVj9u/fyY5EaNjQ2eq/Wf9ty2hLuG\n9fj72tiC43xvWH4dtjDdj003997n+BKIvr1WfD6ZkLoi6JMLfzFZUDCLxLrA0BXQ\nTpZxjz2pQUukwaZJhO/KskjN9nEmdoZfo3ZzZi2acQKBgQDPM4kAfT0ZpMOPHw0e\nGqHuWMOCKPu5u2RrZgsIdnwskWf0knjrP+lhd6K4C9qUr3TiXnPafLYP6ikKgXWZ\nYJutXJnWNBjsKDK4SRIk7WPRHvs5xC4j2f72jW9aqYuwoh4fjnA+tYjjRZil0oqv\nOGfdDoh3PRwKCfI88FDHuZ2U7wKBgQDBsRdwZuzhGCH8nFqxms9I4ySZVg4uM2tN\n2Lm5tbel9A9ZCFAFl641OMB9V7pih7wQ+uN3FwrZvFCAo6A45mrXKWjNUKIQz1Hk\ne4OUPMhGFxldsSHyPxbcjbUcqy/buBE5hsaKJEAgQoHOUt/StoPguuD6hsA7UIyj\nU8qRfLRm+QKBgAwO7bwvjay+X/smTXchCad7VvVuOSgX9cIiUCYP7y4Q0EH1fEAE\nmipn8fpQBkp844qBALEIbPgEIptP6W4hpy2xo+pJYeHsfPcomXu4rQRwjyJPfnfr\nqeDjXkWidFS1OpePjIy5t9uyIy4TUKrd132P6PU3gzg6V/Sf77OP49HVAoGAc+5F\nMzfHrGq/XO1Qs2EPlHav3z9MuYZ5QVzovSjwxNmxnf6FtvM0iBJx1BQAMR1BCYDB\nSPR3wB8gp/5H1gbECAh2+/y5JAqS34i2FrHSxXDp89Qjl1T/n/8JWiF0QbSISsBK\ncUCFSUnFW/LqmLo5cPcp1Yl14YqywsdSRYY4jDECgYB/U4MH2CvcqOPSzK8M2Vr+\nbAo4C1fH7GJysaOkMDW66Wi2s9syNgSEYAALldYXB0UoSkd68R6Rl2166nv4qYF9\nSiV/if9irW5Av2rFIQ4DLRjT47JKBSXL1J5Sq3d8//D5ryueSqs6zNmNwmJ4Xuj3\nObNAIozjWf4V8JRVJ3TOzg==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-uy4pi@icystrisall.iam.gserviceaccount.com",
    "client_id": "109696413895302972539",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-uy4pi%40icystrisall.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Initialize Firebase app using the dictionary-based credentials
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
"""app = Flask(__illuminat__)
app.secret_key = 'icystriall"""

import datetime

import sqlite3

import time
from kivy.clock import Clock

from kivy.uix.progressbar import ProgressBar

"""class ToggleColorButton(Button):
    def __init__(self, **kwargs):
        super(ToggleColorButton, self).__init__(**kwargs)
        self.is_color_toggled = False
        self.is_color_toggled = False
    def toggle_color(self, instance):
        current_color = self.canvas.before.children[0]
        if not self.is_color_toggled:
            current_color.rgb == [0, 1, 0, 1]
        else:
            current_color.rgb == [0, 0, 0, 0]
        self.is_color_toggled = not self.is_color_toggled"""

"""class MyScreenManager(ScreenManager):
    pass

class QuestionScreen(Screen):
    def update_screen(self):
        for widget_id in ["question", "question_number", "questionbtn1", "questionbtn2", "questionbtn3", "questionbtn4", "submit_button"]:
            if widget_id in self.ids:
                self.remove_widget(self.ids[widget_id])

        # Recreate the widgets
        self.ids["question"] = MDLabel(
            text=self.question_text(),
            pos_hint={"center_y": .75},
            color= (52/255, 0, 231/255, 1),
            font_size="17sp",
            font_name="bahnschrift",
            halign="center"
        )
        self.root.add_widget(self.ids["question"])

        self.ids["question_number"] = MDLabel(
            text=self.question_number_text(),
            pos_hint={"center_y": .85},
            color=(169/255, 169/255, 169/255, 1),
            font_size="19sp",
            font_name="bahnschrift",
            halign="center"
        )
        self.root.add_widget(self.ids["question_number"])


        self.ids["questionbtn1"] = Button(
            id="questionbtn1",
            text=self.button_one_text(),
            size_hint=(.8, .08),
            background_color=(0, 0, 0, 0),
            pos_hint={"center_x": .5, "center_y": .63},
            font_name="bahnschrift",
            font_size="15sp",
            on_release=self.btnclickornot_one,
            canvas_before=[
                Color(rgb=(52/255, 0, 231/255, 1)),
                RoundedRectangle(size=self.size, pos=self.pos, radius=[5]
                                 )
            ]
        )
        self.root.add_widget(self.ids["questionbtn1"])


        self.ids["questionbtn2"] = Button(
            id="questionbtn2",
            text=self.button_two_text(),
            size_hint=(.8, .08),
            background_color=(0, 0, 0, 0),
            pos_hint={"center_x": .5, "center_y": .54},
            font_name="bahnschrift",
            font_size="15sp",
            on_release=self.btnclickornot_two,
            canvas_before=[
                Color(rgb=rgba(52/255, 0, 231/255, 1)),
                RoundedRectangle(size=self.size, pos=self.pos, radius=[5])
            ]
        )
        self.root.add_widget(self.ids["questionbtn2"])

        self.ids["questionbtn3"] = Button(
            id="questionbtn3",
            text=self.button_three_text(),
            size_hint=(.8, .08),
            background_color=(0, 0, 0, 0),
            pos_hint={"center_x": .5, "center_y": .45},
            font_name="bahnschrift",
            font_size="15sp",
            on_release=self.btnclickornot_three,
            canvas_before=[
                Color(rgb=(52/255, 0, 231/255, 1)),
                RoundedRectangle(size=self.size, pos=self.pos, radius=[5])
            ]
        )
        self.root.add_widget(self.ids["questionbtn3"])


        self.ids["questionbtn4"] = Button(
            id="questionbtn4",
            text=self.button_four_text(),
            size_hint=(.8, .08),
            background_color=(0, 0, 0, 0),
            pos_hint={"center_x": .5, "center_y": .36},
            font_name="bahnschrift",
            font_size="15sp",
            on_release=self.btnclickornot_four,
            canvas_before=[
                Color(rgb=(52/255, 0, 231/255, 1)),
                RoundedRectangle(size=self.size, pos=self.pos, radius=[5])
            ]
        )
        self.root.add_widget(self.ids["questionbtn4"])



        self.ids["submit_btn"] = Button(
            text=self.submitbtn_text(),
            size_hint=(.66, .065),
            background_color=(0, 0, 0, 0),
            pos_hint={"center_x": .505, "center_y": .2},
            color=rgba(52, 0, 231, 255),
            font_name="bahnschrift",
            on_release=self.submitbtn_whattodo,
            canvas_before=[
                Color(rgb=(52/255, 0, 231/255, 1)),
                Line(width=1.2, rounded_rectangle=[self.x, self.y, self.width, self.height, 5, 5, 5, 5, 100])
            ]
        )
        self.root.add_widget(self.ids["submit_btn"])"""

# Modify the VideoLayout class to handle video loading

kv = '''
            <VideoLayout>:
                orientation: 'vertical'
                Video:
                    id: video
                    state: 'play'
                    options: {'eos': 'loop'}
                    size_hint: 1, 0.75  # Adjusted size_hint
                    pos_hint: {"center_x": .5, "center_y": .5}
                    halign: "center"
                    source: root.generated_video_filename
            '''


class VideoLayout(BoxLayout):
    generated_video_filename = "Hindi1512BNP1.mp4"

    def __init__(self, **kwargs):
        super(VideoLayout, self).__init__(**kwargs)
        self.load_video()

    def load_video(self):
        video = Video(source=self.generated_video_filename, state='play', options={'eos': 'loop'})
        video.id = 'video'  # Set the id attribute after creating the widget
        self.add_widget(video)

    def set_generated_video_filename(self, filename):
        self.generated_video_filename = filename


"""class VideoLayout(BoxLayout, MDScreen):
    # generated_video_filename = "sciencelinearclass9poor.mp4"


    video_options = {
        'eos': 'loop',
        'size': (200, 100)
    }

    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("varscript.kv"))

    def create_video_layout(self, varname):
        layout = BoxLayout(orientation='vertical')
        video = Video(source=varname, state='play', options=self.video_options)
        layout.add_widget(video)
        return layout"""
"""
class VideoScreen(Screen):
    video_layout = None

    def __init__(self, **kwargs):
        super(self).__init__(**kwargs)
        #self.video_layout = VideoLayout()

        self.audio_playing = False
        self.video_playing = False
        self.audio_file = 'science9poorlinear.mp3'
        self.video_file = 'sciencelinearclass9poor.mp4'
        self.audio = None
        self.video = None

        i = 0
        audioduration = 0

    # open_varscript_scriptfile()

    @staticmethod
    def download_image(url, filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {filename} successfully.")
        else:
            print(f"Failed to download {filename}. Status code: {response.status_code}")

    def video_science_poor_nine(self):
        # Assuming 'scienceclass9poor.mp4' is the video path
        video_path = 'illuminat/scienceclass9poor.mp4'

        # Get the VideoLayout widget
        video_layout = self.ids.video_layout

        # Clear previous content
        video_layout.clear_widgets()

        # Load the video into the VideoLayout
        video_layout.load_video(video_path)

    def generate_and_download_images_list(self, prompt_list, filename):
        for prompt in prompt_list:
            self.generate_and_download_images(prompt, filename)

    def generate_and_download_images(self, prompt, filename):
        # Example usage with JSON-serializable prompt
        prompt_obj = {'text': prompt}
        prompt_json = json.dumps(prompt_obj)
        response_json = self.generate_image(prompt_json, num_image=1, size='256x256', output_format='url')

        # Check and print the results
        for response in [response_json]:
            if response is not None and 'created' in response and 'images' in response:
                print(response['created'])
                images = response['images']
                for Illuminat.i, image_url in enumerate(images):
                    print(Illuminat.i)
                    print(f"Downloading Image {Illuminat.make_mastervariable()}: {image_url}")
                    self.download_image(image_url, filename=f'{Illuminat.make_mastervariable()}.png')
                    self.i += 1  # Use self.i to update the class variable
                    print(self.i)

            else:
                print("Error in image generation.")

    @staticmethod
    def generate_image(prompt, num_image=1, size='256x256', output_format='url'):
        try:
            images = []
            response = openai.images.generate(
                prompt=prompt,
                n=num_image,
                size=size,
                response_format=output_format
            )

            if output_format == 'url':
                for image in response.data:
                    images.append(image.url)
            elif output_format == 'b64_json':
                for image in response.data:
                    images.append(image.b64_json)

            return {'created': datetime.datetime.fromtimestamp(response.created), 'images': images}

        except Exception as e:
            print(f"Error: {e}")
            return None

    def image_to_video_science(self):
        clips = []
        clip1 = ImageClip('microscopic_life_1.png').set_duration(91)
        clip2 = ImageClip('cell_originating_1.png').set_duration(91)
        # clip3 = ImageClip('cell_organelles.png').set_duration(91)
        # clip4 = ImageClip('research_things_to_do.png').set_duration(92)
        clips.append(clip1)
        clips.append(clip2)
        # clips.append(clip3)
        # clips.append(clip4)
        video_clip = concatenate_videoclips(clips, method='compose')

        # Set the filename for VideoLayout
        video_layout = self.ids.video_layout
        if video_layout:
            # video_layout.set_generated_video_filename("sciencelinearclass9poor.mp4")

            # Write the video file
            video_clip.write_videofile('scienceclass9poor.mp4', fps=24, remove_temp=True, codec="libx264",
                                       audio_codec="aac")

            print("Downloaded")
            # self.generated_video_filename = "sciencelinearclass9poor.mp4"
            self.VideoLayout.load_video("sciencelinearclass9poor.mp4")
        else:
            print("VideoLayout not found.")

    def convert_to_speech_science9_poor(self):
        text_to_convert = VideoScreen.content
        selected_language = "en"

        if text_to_convert and selected_language:
            self.tts = gTTS(text=text_to_convert, lang=selected_language)
            self.tts.save("science9poorlinear.mp3")
            print("Conversion done")
"""


class Question5Screen(Screen):

    def __init__(self, **kwargs):
        super(Question5Screen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        self.sciencequestiononequestionnumber = Label(
            text="Q5/5",
            color=get_color_from_hex("#000000"),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Set position hint
            size_hint=(0.8, None),  # Set size hint (width: 80%, height: None)
            height=40,
            font_name="bahnschriftlight"
        )

        layout.add_widget(self.sciencequestiononequestionnumber)

        self.sciencequestiononetext = Label(
            text="What is the control center of the \n cell that contains genetic material?",
            halign="center",
            color=get_color_from_hex("#000000"),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Set position hint
            size_hint=(0.8, None),  # Set size hint (width: 80%, height: None)
            height=40,
            font_name="bahnschrift"
        )

        layout.add_widget(self.sciencequestiononetext)

        self.sciencequestionone = TextInput(
            hint_text="Enter your text here",
            background_color=get_color_from_hex("#FFFFFF"),
            background_normal='',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Set position hint
            size_hint=(0.8, None),  # Set size hint (width: 80%, height: None)
            height=40,
            multiline=False,
            font_name="bahnschriftlight"
        )

        layout.add_widget(self.sciencequestionone)

        submit_button = Button(text='Submit',
                               background_color=get_color_from_hex("#3400e7"),  # Set background color
                               pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Set position hint
                               size_hint=(0.8, None),  # Set size hint (width: 80%, height: None)
                               height=40,
                               halign="center",
                               valign="middle"
                               )
        submit_button.bind(on_press=self.on_submit)
        layout.add_widget(submit_button)

        self.sciencequestiononetextilluminat = Label(
            text="Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. \n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat.\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat."
                 "\n Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. Illuminat. "
            ,
            halign="center",
            color=get_color_from_hex("#000000"),
            opacity=0.1,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},  # Set position hint
            size_hint=(0.8, None),  # Set size hint (width: 80%, height: None)
            font_name="bahnschrift"
        )

        layout.add_widget(self.sciencequestiononetextilluminat)

        self.add_widget(layout)

    def check_text(self):
        print("IDs:", self.ids)

        text_value = self.sciencequestionone.text
        if self.sciencequestionone.text == 'nucleus' or self.sciencequestionone.text == 'Nucleus':
            print(Illuminat.question_score_science_poor)
            Illuminat.question_score_science_poor += 1
            print(Illuminat.question_score_science_poor)
        else:
            print(Illuminat.question_score_science_poor)

    def check_which_screen_next(self):
        if 4 <= Illuminat.question_score_science_poor <= 5:
            sm = self.manager
            sm.current = 'questionend_screen'
        elif Illuminat.question_score_science_poor == 3:
            sm = self.manager
            sm.current = 'questionend3_screen'
        elif 0 <= Illuminat.question_score_science_poor <= 2:
            sm = self.manager
            sm.current = 'questionend012_screen'

    def on_submit(self, instance):
        self.check_text()
        text_value = self.sciencequestionone.text
        print(f"Text from TextInput: {text_value}")
        self.check_which_screen_next()


KV = '''
<Illuminat>:
    MDScreen:
        name: "varscript"

        MDFloatLayout:
            id: video_layout
            MDIconButton:
                id: arrowback
                icon: "arrow-left"
                pos_hint: {"center_x": .05, "center_y": .95}
                user_font_size: "30sp"
                theme_text_color: "Custom"
                text_color: rgba(26, 24, 58, 255)

            MDLabel:
                id: vidScreenHeadTxt
                text: "Default Txt"
                font_name: "bahnschriftlight"
                font_size: "15sp"
                pos_hint: {"center_x": .615, "center_y": .9477}
                color: rgba(52, 0, 231, 255)

            MDLabel:
                text: "Let us start learning about linear equations in two variables. Imagine you have two friends, let's call them x and y. A linear equation is like a rule for these friends. For example, 2x + 3y = 10. This rule says that if x has 2 things and y has 3 things, their total should be 10 things. In a linear equation with two variables, you deal with two unknowns, usually represented as x and y. The general form of a linear equation in two variables is ax+by=c, where a, b, and c are constants."
                font_name: "bahnschriftlight"
                font_size: "15sp"
                pos_hint: {"center_x": .5, "center_y": .35}
                color: rgba(68, 78, 132, 255)
                halign: "center"

            MDIconButton:
                id: play_pause_button
                icon: 'play'
                user_font_size: '56sp'
                on_press: app.change_video_source()

            Button:
                text: "CONTINUE TO QUIZ"
                size_hint: .66, .065
                background_color: 0, 0, 0, 0
                pos_hint: {"center_x": .5, "center_y": .38}
                font_name: "bahnschrift"
                on_release:
                    root.manager.transition.direction = "right"
                    root.manager.current = "question1_screen_top_var"
                canvas.before:
                    Color:
                        rgb: rgba(52, 0, 231, 255)
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius: [5]
            Video:
                id: video_player
                source: 'rdomhere.mp4'
'''


class VarScriptScreen(Screen):
    pass


def get_device_id():
    # Read device IDs from file
    existing_device_ids = set()
    try:
        with open('device_id.txt', 'r') as file:
            for line in file:
                existing_device_ids.add(line.strip())
    except FileNotFoundError:
        pass  # If the file doesn't exist yet, continue without error

    # Check if the user's device ID is in the set of existing IDs
    device_id = None
    user_device_id = None  # Replace this with the actual method to get the user's device ID
    if user_device_id in existing_device_ids:
        device_id = user_device_id
    else:
        # Generate a new device ID
        device_id = str(uuid.uuid4())
        # Write the new device ID to the file
        with open('device_id.txt', 'a') as file:
            file.write(device_id + '\n')

    return device_id

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text='Loading...')
        self.progress_bar = ProgressBar(max=100)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.progress_bar)
        self.add_widget(self.layout)

    async def start_loading(self):
        self.manager.current = 'loading_screen'
        await self.simulate_loading()

    async def simulate_loading(self):
        for i in range(1, 11):
            await asyncio.sleep(0.5)  # Simulate some heavy computation
            self.progress_bar.value = i * 10
        self.manager.switch_to_home()

class MyVideoPlayer(VideoPlayer):
    pass
class Illuminat(MDApp):
    users_ref = None
    age_what = 0

    btnClick = 0
    finalClick_lang = 0

    btnClick_hindi = 0
    finalClick_lang_hindi = 0

    btnClick_tamil = 0
    finalClick_lang_tamil = 0

    user_data = {}

    question_number = 1

    btnClick_questions = 0
    finalClick_ans_one = 0
    finalClick_ans_two = 0
    finalClick_ans_three = 0
    finalClick_ans_four = 0

    questions_score = 0

    score_final = 0

    ids = {}

    """config = configparser.ConfigParser()
    config.read('credentials.ini')
    API_KEY = config['openai']['APIKEY']"""

    openai.api_key = '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'

    SIZES = ('1024x1024', '512x512', '256x256')

    text_to_be_converted = " "

    name_video_clip = " "

    video_file_path = " "

    question_score_science_poor = 0
    question_score_science_avg = 0
    question_score_science_top = 0
    video_layout = None

    a = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stored_lang = ""
        self.stored_score = 0
        self.stored_age = 0
        self.subjectClicked = 0
        self.chapter_name = "None"
        self.questionnumber = 1
        self.mastervariable = ""
        self.mastervariabletxt = ""
        self.mastervariablemp4 = ""
        self.mastervariabletxtupdated = ""
        self.mastervariablemp3 = ""
        self.mastervariablemp3updated = ""
        # self.video_layout = VideoLayout(self.mastervariablemp4)
        self.audio_playing = False
        self.video_playing = False
        self.audio_file = 'science9poorlinear.mp3'
        self.video_file = 'sciencelinearclass9poor.mp4'
        self.audio = None
        self.video = None
        self.playvid = 0
        self.audiodurationn = 0
        self.texttnew = ""
        self.newscore = 0
        self.newtext = ""
        self.newtexteng = ""
        self.qTxtupdated = ""
        self.paraTxtupdated = ""
        self.bqquestionno = 0
        self.bqTxt = ""
        self.bqNo = ""
        self.bqBtn1 = ""
        self.bqBtn2 = ""
        self.bqBtn3 = ""
        self.bqBtn4 = ""
        self.bqNxtBtn = ""
        self.questionscreennumber = 0
        self.changemastervar = 0
        self.finfeed = ""

    i = 0
    audioduration = 0

    finalquestion_score = 0
    finalScoree = 0
    # client = OpenAI()
    # openai.api_key = ""

    """kv_string = ''' 
    MDFloatLayout:
        MDLabel:
            id: "questiontxt"
            text: "Which planet is also known as the Red Planet?"
            pos_hint: {"center_y": .75}
            color: rgba(52, 0, 231, 255)
            font_size: "17sp"
            font_name: "bahnschrift"
            halign: "center"

    Builder.load_string(kv_string)"""

    # question_widget = self.root.ids.questiontxt

    """def __init__(self, **kwargs):
        super().__init__()




        self.ids = None
        self.user_data = UserData()
        #self.user_data = {}
        #self.entered_email = """""

    screen_managerr = ScreenManager()

    """def __init__(self):
        pass

    def init_db(self):
        # Initialize SQLite database (for storing device IDs)
        conn = sqlite3.connect('session.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS devices (
                            id INTEGER PRIMARY KEY,
                            device_id TEXT UNIQUE
                        )''')
        conn.commit()
        conn.close()

    def get_device_id(self):
        # Retrieve or generate device ID
        # For example, you can use the device's UUID
        device_id = None
        # Check if device ID exists in session, otherwise generate and store one
        if 'device_id' in session:
            device_id = session['device_id']
        else:
7            device_id = str(uuid.uuid4())
            session['device_id'] = device_id
        return device_id

    def is_device_registered(self, device_id):
        # Check if device ID exists in the database
        conn = sqlite3.connect('session.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        device = cursor.fetchone()
        conn.close()
        return device is not None"""

    def build(self):
        # Initialize the database
        """self.init_db()

        Generate or retrieve device identifier
        device_id = self.get_device_id()"""

        self.screen_manager = ScreenManager()

        # Check if device identifier exists in the database
        self.screen_manager.add_widget(Builder.load_file("illuminat/main.kv"))
        self.screen_manager.add_widget(Builder.load_file("beforequestionsscreen.kv"))
        self.screen_manager.add_widget(Builder.load_file("beforequestions.kv"))
        self.screen_manager.add_widget(Builder.load_file("home.kv"))
        self.screen_manager.add_widget(Builder.load_file("prevarscriptpoor.kv"))
        self.screen_manager.add_widget(Builder.load_file("prevarscriptavg.kv"))
        self.screen_manager.add_widget(Builder.load_file("prevarscripttop.kv"))
        self.screen_manager.add_widget(Builder.load_file("varscript.kv"))
        self.screen_manager.add_widget(Builder.load_file("scorescreen.kv"))
        self.screen_manager.add_widget(Question5Screen(name='question5_screen'))
        self.screen_manager.add_widget(Builder.load_file("questionsscreen.kv"))
        self.screen_manager.add_widget(Builder.load_file("questionsolder.kv"))
        #self.screen_manager.add_widget(Builder.load_file("homecopy.kv"))
        self.screen_manager.add_widget(Builder.load_file("signupdetails.kv"))
        self.screen_manager.add_widget(Builder.load_file("signup.kv"))
        self.screen_manager.add_widget(Builder.load_file("login.kv"))
        self.screen_manager.add_widget(Builder.load_file("questions.kv"))
        self.screen_manager.add_widget(Builder.load_file("clairtybot.kv"))
        self.screen_manager.add_widget(Builder.load_file("question2.kv"))
        self.screen_manager.add_widget(Builder.load_file("question3.kv"))
        self.screen_manager.add_widget(Builder.load_file("question4.kv"))
        self.screen_manager.add_widget(Builder.load_file("question5.kv"))
        self.screen_manager.add_widget(Builder.load_file("question6.kv"))
        self.screen_manager.add_widget(Builder.load_file("question7.kv"))
        self.screen_manager.add_widget(Builder.load_file("question8.kv"))
        self.screen_manager.add_widget(Builder.load_file("question9.kv"))
        self.screen_manager.add_widget(Builder.load_file("question10.kv"))
        self.screen_manager.add_widget(LoadingScreen(name="loading"))
        self.screen_manager.add_widget(Builder.load_file("profile.kv"))


        """if self.is_device_registered(device_id):
            # Device is registered, redirect to home screen
            self.screen_manager.current = 'home'
        else:
            # Device is not registered, redirect to login/signup screen
            self.screen_manager.current = 'main'"""
        return self.screen_manager


        # return Builder.load_string(kv_sciencepoor_9)

    # Illuminat_instance = Illuminat()
    # @lru_cache(maxsize=None)

    def create_users_table(conn):
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        uid TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL
                     )''')
        conn.commit()

    def videoplay(self):
        layoutt = BoxLayout()
        layout = self.create_video_layout()
        if self.playvid == 0:
            pass
        elif self.playvid == 1:
            return layout
    def drdonothing(self):
        pass
    def handle_signupbutton(self):
        current_screen = self.root.current_screen

        if current_screen.name == "signup":
            layoutttttt = self.root.get_screen("main").ids.mdfltlaytrrtthrt
            email_input = current_screen.ids.signup_email
            entered_email = email_input.text
            #entered_email = "hello"
            password_input = current_screen.ids.signup_pass
            entered_password = password_input.text
            passLength = len(entered_password)
            print(f"passLength: {passLength}")
            if "@" in entered_email:
                if passLength > 6:
                    print("@ here")
                    try:
                        user = auth.create_user(email=entered_email, password=entered_password)
                        print(user)

                        Illuminat.users_ref = firestore.client().collection('icystriall').document(user.uid)
                        # doc_ref = users_ref.document(user.uid)

                        """doc_ref.set({
                            'email': entered_email,
                            'password': entered_password
                        })"""

                        Illuminat.users_ref.set({
                            'email': entered_email,
                            'password': entered_password,
                            'uid': user.uid
                        })

                        """conn = create_connection()
                        with conn:
                            self.create_users_table(conn)
                            c = conn.cursor()
                            c.execute("INSERT INTO users (uid, email, password) VALUES (?, ?, ?)",
                                      (user.uid, entered_email, entered_password))
    
    
                            conn.commit()
        """

                        self.user_data["email"] = entered_email
                        self.user_data["password"] = entered_password
                        self.user_data["uid"] = user.uid
                        self.entered_email = entered_email
                        self.entered_password = entered_password
                        print(f"Document reference: {Illuminat.users_ref.path}")
                        print("Success! Account Created!", entered_email)
                        self.screen_manager.current = 'signupdetails'
                    except ValueError as e:
                        print(f"Error creating user: {e}")
                        print("@ unhere")
                        """error_label = Label(
                            id='errorLabel',
                            text="Error creating user. Please \n enter a valid email address.",
                            color=(0, 0, 0, 1),
                            valign='bottom',
                            halign='right',
                            size_hint=(None, None),
                            size=(310, 30),
                            text_size=(None, None),
                            padding=(0, 20)
                        )
                        layoutttttt.add_widget(error_label)"""
                        errLabel = self.root.get_screen('main').ids.errorLabel
                        errLabel.opacity = 1

                        # Navigate to a different screen
                        self.screen_manager.current = 'main'
                        self.entered_email = entered_email
                        self.entered_password = entered_password

                    if Illuminat.users_ref is not None:
                        print("Congrats")
                    self.getEmailAndPassword()
                else:
                    print("Aww not valid mail id")
                    errLabel = self.root.get_screen('main').ids.errorLabel
                    errLabel.opacity = 1
                    errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer \n than 6 characters."
                    self.screen_manager.current = 'main'
            elif "@" not in entered_email:
                errLabel = self.root.get_screen('main').ids.errorLabel
                errLabel.opacity = 1
                # errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer than 6 characters."
                self.screen_manager.current = 'main'
                self.screen_manager.current = 'main'
                if passLength < 6:
                    print("Aww not valid mail id")
                    errLabel = self.root.get_screen('main').ids.errorLabel
                    errLabel.opacity = 1
                    errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer \n than 6 characters."

                    self.screen_manager.current = 'main'
            elif passLength < 6:
                errLabel = self.root.get_screen('main').ids.errorLabel
                errLabel.opacity = 1
                errLabel.text = "Error creating user. Please enter a \n password longer than 6 characters."

                self.screen_manager.current = 'main'


            # doc_ref = None



    """def update_screen(self, dt):
        # Access the current screen and update its content
        questions = self.root.get_screen('questions')
        questions.update_screen()"""
    def destroytheerror(self):
        errLabel = self.root.get_screen('main').ids.errorLabel
        errLabel.opacity = 0
        errLabel.text = "Error creating user. Please enter a \n valid email address."

    def fetch_user_data_from_firestore(self, uid):
        users_ref = firestore.client().collection('icystriall')
        doc_ref = users_ref.document(uid)
        doc = doc_ref.get()

        if doc.exists:
            user_data = doc.to_dict()
            print(f"User data retrieved: {user_data}")
            return user_data
        else:
            print(f"No data found for {uid}")
            return {}

    """def get_qtext_comp(self):

        uid = user.uid
        self.user_data = self.fetch_user_data_from_firestore(uid)

        selectedLang = self.user_data.get("lang")
        beforeQuestionsScoreInt = self.user_data.get("score")
        beforeQuestionsScore = int(beforeQuestionsScoreInt)
        selectedAgeInt = self.user_data.get("age")
        selectedAge = int(selectedAgeInt)

        if selectedAge == 16:
            if 0 <= beforeQuestionsScore <= 3:
                if selectedLang == "English":"""
                    #return "Data is a collection of ________ facts \n which have not been processed to \n reveal useful information."

    """def __init__(self, **kwargs):
        Builder.load_string('''
            <VideoLayout>:
                orientation: 'vertical'
                Video:
                    id: video
                    state: 'play'
                    source: "sciencelinearclass9poor.mp4"
                    size: (200, 200)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            ''')"""

    """def load_video(self):
        video = Video(source='sciencelinearclass9poor.mp4', state='play', options=video_options)
        self.add_widget(video)"""

    def chatClairty(self, prompt):
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # You can use the latest engine available
            prompt=prompt,
            max_tokens=40,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    def destroytheimg(self):
        bqImage = self.root.get_screen('beforequestionsscreen').ids.bqImg
        bqImage.opacity = 0.175
    def getResponse(self):
        tXtSent = self.root.get_screen("clairtybot").ids.textEnteredWidget
        ansTxt = self.root.get_screen("clairtybot").ids.ansTxt
        txtSenttrue = tXtSent.text
        print(txtSenttrue)
        atxtSenttrue = ansTxt.text
        # userInput = input("You:")
        """if userInput == 'quit':
            break"""

        botResponse = self.chatClairty(txtSenttrue)
        print(botResponse)
        tXtSent.text = ""
        langggg = self.stored_lang
        selLang = ""
        if langggg == "Hindi":
            selLang = "hi"
        elif langggg == "Tamil":
            selLang = "ta"

        langg = self.stored_lang
        if langg == "English":
            ansTxt.text = botResponse
            self.newtexteng = botResponse
            self.newtext = botResponse

        elif langg == "Hindi":
            self.newtexteng = botResponse
            self.aztranslate_text(botResponse, selLang)
            ansTxt.text = self.newtext
            self.newtext = ansTxt.text

            ansTxt.font_name = "tirodevanagrihindi.ttf"
        elif langg == "Tamil":
            self.newtexteng = botResponse
            self.aztranslate_text(botResponse, selLang)
            ansTxt.text = self.newtext
            self.newtext = ansTxt.text
            # self.newtext.font_name = "tirotamil.ttf"
            ansTxt.font_name = "tirotamil.ttf"

    def speaktextforai(self):
        tts = self.newtext
        """if self.azttsforai(tts) is True:
            pass
        else:"""
        self.azttsforai(tts)

    @staticmethod
    def download_image(url, filename):

        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {filename} successfully.")
        else:
            print(f"Failed to download {filename}. Status code: {response.status_code}")

    """def video_science_poor_nine(self):
        # Assuming 'scienceclass9poor.mp4' is the video path
        video_path = 'illuminat/scienceclass9poor.mp4'

        # Get the VideoLayout widget
        video_layout = self.ids.video_layout

        # Clear previous content
        video_layout.clear_widgets()

        # Load the video into the VideoLayout
        video_layout.load_video(video_path)"""

    def start_the_generate_and_download_function(self):
        filename_mastervar = self.mastervariabletxt
        endfile_mastervar = str(filename_mastervar)
        print(endfile_mastervar)
        with open(endfile_mastervar, 'r') as file:
            lines = file.readlines()
        eigthline_firstword = lines[7].split()[0]
        tenthline_firstword = lines[9].split()[0]
        text_png = ".png"
        eightline_firstword_png = str(eigthline_firstword) + str(text_png)
        tenthline_firstword_png = str(tenthline_firstword) + str(text_png)

    def generate_and_download_images_list(self):
        #self.load_screens()
        filename_mastervar = self.mastervariabletxtupdated
        endfile_mastervar = str(filename_mastervar)
        print(endfile_mastervar)
        with open(endfile_mastervar, 'r') as file:
            lines = file.readline()
            words = lines.split()
        eigthline_firstword = words[7]
        tenthline_firstword = words[9]
        text_png = ".png"
        eightline_firstword_png = str(eigthline_firstword) + str(text_png)
        tenthline_firstword_png = str(tenthline_firstword) + str(text_png)
        prompt_list = [eightline_firstword_png, tenthline_firstword_png]
        filename = eightline_firstword_png
        filename2 = tenthline_firstword_png
        print(filename)
        print(filename2)

        self.generate_and_download_images(eigthline_firstword, filename)
        self.generate_and_download_images(tenthline_firstword, filename2)
        self.image_to_video_science()
        # self.generate_and_download_images(prompt, filename2)

        """for prompt in prompt_list:
            a = 0
            if a == 0:"""

        """a +=1
             self.generate_and_download_images(prompt, filename2)"""

    def generate_and_download_images(self, prompt, filename):
        # Example usage with JSON-serializable prompt
        prompt_obj = {'text': prompt}
        prompt_json = json.dumps(prompt_obj)
        response_json = self.generate_image(prompt_json, num_image=1, size='256x256', output_format='url')

        for response in [response_json]:
            if response is not None and 'created' in response and 'images' in response:
                print(response['created'])
                images = response['images']
                for Illuminat.i, image_url in enumerate(images):
                    print(Illuminat.i)
                    print(f"Downloading Image {Illuminat.i + 1}: {image_url}")
                    self.download_image(image_url, filename=filename)
                    self.i += 1
                    print(self.i)

            else:
                print("Error in image generation.")

    @staticmethod
    def generate_image(prompt, num_image=1, size='256x256', output_format='url'):
        print("here")
        try:
            images = []
            response = openai.images.generate(
                prompt=prompt,
                n=num_image,
                size=size,
                response_format=output_format
            )

            if output_format == 'url':
                for image in response.data:
                    images.append(image.url)
            elif output_format == 'b64_json':
                for image in response.data:
                    images.append(image.b64_json)

            return {'created': datetime.datetime.fromtimestamp(response.created), 'images': images}

        except Exception as e:
            print("now here ")
            print(f"Error: {e}")
            return None

    """def play_thevideo(self):
        def __init__(self, **kwargs):
            super(Illuminat, self).__init__(**kwargs)
            video = Video(source=self.mastervariabletxt, state='play',
                          options={'eos': 'loop', 'size': (200, 480)})
            self.add_widget(video)"""
    """def play_thevideo(self):
        video = Video(source=self.mastervariabletxt, state='play',
                      options={'eos': 'loop', 'size': (200, 480)})
        self.root.add_widget(video)"""

    def create_video_layout(self, varname, target_layout):
        video_path = "Hindi1512BNP1.mp4"
        print("Showing")
        video = Video(source=varname, state='play', options={'allow_stretch': True})
        target_layout.add_widget(video)
        print("Let's see")

    def getfilenameforvideo(self):
        print("Yo, me back")
        return self.mastervariablemp4

    def image_to_video_science(self):
        try:
            filename_mastervar = self.mastervariabletxtupdated
            endfile_mastervar = str(filename_mastervar)
            with open(endfile_mastervar, 'r') as file:
                lines = file.readline()
                words = lines.split()
            eigthline_firstword = words[7]
            tenthline_firstword = words[9]
            text_png = ".png"
            eightline_firstword_png = str(eigthline_firstword) + str(text_png)
            tenthline_firstword_png = str(tenthline_firstword) + str(text_png)
            clips = []
            langgggg = self.stored_lang
            # self.convert_to_speech()
            print("Done till here")
            self.convert_to_speech()
            print("Convert To Speeched")
            self.get_audio_duration()
            print("Audio Durationed")
            # audio_filepath = self.mastervariablemp3updated
            durationn = float(self.audiodurationn)
            # durattion = float(duration)
            clip1duration = durationn / 2
            clip2duration = durationn / 2
            clip1 = ImageClip(eightline_firstword_png).set_duration(clip1duration)
            clip2 = ImageClip(tenthline_firstword_png).set_duration(clip2duration)
            clips.append(clip1)
            clips.append(clip2)
            clips_wF = [clip.fadein(duration=1).fadeout(duration=1) for clip in clips]

            print("Herething")
            video_clip = concatenate_videoclips(clips_wF, method='compose')
            # video_clip.set_audio(None)
            print("Here reached")
            audio_clip = AudioFileClip(self.mastervariablemp3updated)
            print("Reached till here now")
            video_clip = video_clip.set_audio(audio_clip)
            print("Reached here now")

            output_file = self.mastervariablemp4
            print(output_file + "I am here")
            video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)

            print("We're here")
            """player = VideoPlayer(source="rdomhere.mp4")
            player.state = 'play'
            player.options = {'eos': 'loop'}
            return player
            print("Chop chop")"""

            # Load varscript.kv only once
            # var_script_screen = Builder.load_file("varscript.kv")
            """
            # Assuming you have a BoxLayout with the id video_layout in varscript.kv
            target_layout = var_script_screen.ids.video_layout

            # Call the function to create the video and add it to the layout
            self.create_video_layout(self.mastervariablemp4, target_layout)"""

            """self.screen_manager = ScreenManager()
            Builder.load_string(kv)  # Load the kv string
            video_screen = VideoScreen(name='video_screen')
            video_layout = VideoLayout()
            video_screen.add_widget(video_layout)
            self.screen_manager.add_widget(video_screen)
            return self.screen_manager
            print("returned")"""

            # Show the root widget
            # return var_script_screen

        except Exception as e:
            print(f"Error in image_to_video_science: {e}")
            print("Woahh")
            import traceback
            traceback.print_exc()
            return None

    """def convert_to_speech_science9_poor(self):
        text_to_convert = VideoScreen.content
        selected_language = "en"

        if text_to_convert and selected_language:
            self.tts = gTTS(text=text_to_convert, lang=selected_language)
            self.tts.save("science9poorlinear.mp3")
            print("Conversion done")"""

    """def googlesignup(token):
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            # Replace with your own CLIENT_ID obtained from the Google API Console
            CLIENT_ID = "342384583627-6m1ugrlbpgpmt305o827mp5sp9ln41gu.apps.googleusercontent.com"

            # Specify the expected audience for the token
            expected_audience = CLIENT_ID

            # Verify the token
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), expected_audience)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # ID token is valid
            return idinfo
        except ValueError as e:
            # Invalid token
            print("Invalid token:", e)
            return None"""


    def handle_loginbutton(self):
        current_screen = self.root.current_screen
        if current_screen.name == "login":
            self.entered_email = current_screen.ids.login_email_input.text.strip()
            self.entered_password = current_screen.ids.login_pass_input.text.strip()
            print(self.entered_email, self.entered_password)
            passwordd = self.entered_password
            passworddLength = len(passwordd)
            print(f"passworddLength: {passworddLength}")
            if "@" in self.entered_email:
                if passworddLength > 6:
                    print("Hello")
                    user = auth.get_user_by_email(self.entered_email)
                    uid = user.uid
                    user = auth.get_user(uid)
                    print(user)
                    print("Success! Logged In")

                    uid = user.uid
                    self.user_data = self.fetch_user_data_from_firestore(uid)

                    stored_email = self.user_data.get("display_name")
                    stored_password = self.user_data.get("password")
                    self.stored_score = self.user_data.get("score")
                    self.stored_lang = self.user_data.get("lang")
                    self.stored_age = self.user_data.get("age")
                    print("Score:", self.stored_score, "Lang:", self.stored_lang, "Age:", self.stored_age)

                    print("User choices from previous screen")
                    print("Stored Email", stored_email)
                    print("Stored Password", stored_password)
                    if self.entered_password == stored_password:
                        Illuminat.a = 1
                        print(Illuminat.a)
                        print("Yes")
                        aVal = Illuminat.a
                        self.on_loginBtn_comp(aVal)
                        self.btn1_text_which()
                        self.btn4txt_which()
                        self.screen_manager.current = 'home'
                        print("Correct")
                        Illuminat.a = 0

                    else:
                        print("Pass not match, congrulations")
                        Illuminat.a = 0
                        print(Illuminat.a)
                        aVal = Illuminat.a
                        self.on_loginBtn_comp(aVal)
                        self.screen_manager.current = 'main'
                        # screennManager = ScreenManager()
                        # self.screen_managerr.current = 'main'
                    if Illuminat.users_ref is not None:
                        Illuminat.users_ref.update({
                            'email': self.entered_email,
                            'password': self.entered_password
                        })
                    self.getEmailAndPassword()
                else:
                    print("Aww not valid mail id")
                    errLabel = self.root.get_screen('main').ids.errorLabel
                    errLabel.opacity = 1
                    errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer \n than 6 characters."
                    self.screen_manager.current = 'main'
            elif "@" not in self.entered_email:
                errLabel = self.root.get_screen('main').ids.errorLabel
                errLabel.opacity = 1
                self.screen_manager.current = 'main'
                #errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer than 6 characters."

                self.screen_manager.current = 'main'
                if passworddLength < 6:
                    print("Aww not valid mail id")
                    errLabel = self.root.get_screen('main').ids.errorLabel
                    errLabel.opacity = 1
                    errLabel.text = "Error creating user. Please enter a \n valid email address and Password longer \n than 6 characters."

                    self.screen_manager.current = 'main'
            elif passworddLength < 6:
                errLabel = self.root.get_screen('main').ids.errorLabel
                errLabel.opacity = 1
                errLabel.text = "Error creating user. Please enter a \n password longer than 6 characters."

                self.screen_manager.current = 'main'






    def on_loginBtn_comp(self, aVal):
        print(aVal)

    def on_btn_press(self):
        self.btn1_text_which()

    def open_mastervartext(self):
        with open(self.mastervariabletxt, 'r') as file:
            content = file.read()

    def remove_widget_by_id(self, widget_id):
        # Get the widget using the id
        widget_to_remove = self.ids.get(widget_id)

    """def startthequiz(self):
        screen_manager.add_widget(Question5Screen(name='question5_screen_top_dman'))"""
    def getEmailAndPassword(self):
        entEmail = self.entered_email
        entPass = self.entered_password
        txtEmail = self.root.get_screen('profile').ids.txtEmail
        txtPass = self.root.get_screen('profile').ids.txtPass
        txtEmail.text = entEmail
        txtPass.text = entPass
    def prevarscript_which_poor(self, whoclicked2):
        langg = self.stored_lang
        agee = int(self.stored_age)
        self.subjectClicked = int(whoclicked2)
        scoree = int(self.stored_score)
        getchapterr = self.chapter_name
        print(langg)
        print(agee)
        print(self.subjectClicked)
        print(scoree)
        ch1button = self.root.get_screen("prevarscriptpoor").ids.whichchapter
        #quiz1button = self.root.get_screen("prevarscriptpoor").ids.whichquiz
        ch2button = self.root.get_screen("prevarscriptpoor").ids.whichchapter2
        #quiz2button = self.root.get_screen("prevarscriptpoor").ids.whichquiz2

        if agee == 13:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1button.text = "Ch - 1: Cell: The Fundamental Unit of Life"
                    ch2button.text = "Ch - 2: Matter Around Us"

                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: कोशिका: जीवन की मौलिक इकाई"
                    ch2button.text = "अध्याय - 2: हमारे चारों ओर पदार्थ"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அத்தியாயம் - 1: உயிரின் அடிப்படை அலகு"
                    ch2button.text = "அத்தியாயம் - 2: உங்கள் சுற்றுலாவின் சுற்றுகள்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1button.text = "Ch - 1: People As Resource"
                    ch2button.text = "Ch - 2: Climate"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: लोगों के रूप में संसाधन"
                    ch2button.text = "अध्याय - 2: जलवायु"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: மக்கள் உள்ளடக்கம்"
                    ch2button.text = "அகராதி - 2: காரியம்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1button.text = "Ch - 1: Computer Networking"
                    ch2button.text = "Ch - 2: Cyber Security"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: कंप्यूटर नेटवर्किंग"
                    ch2button.text = "अध्याय - 2: साइबर सुरक्षा"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: கணினி பிணையம்"
                    ch2button.text = "அகராதி - 2: சைபர் பாதுகாப்பு"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

        elif agee == 14:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1button.text = "Ch - 1: Metals & Non-Metals"
                    ch2button.text = "Ch - 2: Control & Coordination"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: धातु और अधातु"
                    ch2button.text = "अध्याय - 2: नियंत्रण और समन्वय"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அத்தியாயம் - 1: தாதுகள் மற்றும் அதாதுகள்"
                    ch2button.text = "அத்தியாயம் - 2: கட்டுப்பாடு மற்றும் ஒருங்கிணைப்பு"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1button.text = "Ch - 1: Water Resources"
                    ch2button.text = "Ch - 2: Consumer Rights"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: जल संसाधन"
                    ch2button.text = "अध्याय - 2: उपभोक्ता अधिकार"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: நீர் வளமும்"
                    ch2button.text = "அகராதி - 2: உபயோகத்தரக்காரர் உரிமைகள்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1button.text = "Ch - 1: Networking"
                    ch2button.text = "Ch - 2: Cyber Ethics"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: नेटवर्किंग"
                    ch2button.text = "अध्याय - 2: साइबर एथिक्स"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: பிணையம்"
                    ch2button.text = "அகராதி - 2: சைபர் நீதிகள்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"


        elif agee == 15:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1button.text = "Ch - 1: Oscillation"
                    ch2button.text = "Ch - 2: Kinetic Energy"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: ओसिलेशन"
                    # Illuminat_instance.remove_widget_by_id('ch2button')
                    ch2button.text = "अध्याय - 2: नगतिज ऊर्जा"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அத்தியாயம் - 1: ஓசிலேஷன்"
                    ch2button.text = "அத்தியாயம் - 2: கினெடிக் எனஜி"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1button.text = "Ch - 1: Business: Nature & Purpose"
                    ch2button.text = "Ch - 2: Business Services"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: व्यापार: प्रकृति और उद्देश्य"
                    ch2button.text = "अध्याय - 2: व्यापार सेवाएं"
                    # Illuminat_instance.remove_widget_by_id('ch2button')
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: பணியின்: இயல்பு மற்றும் பொருள்"
                    ch2button.text = "அகராதி - 2: பணியின் சேவைகள்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1button.text = "Ch - 1: Yoga"
                    ch2button.text = "Ch - 2: Psychology in Sports"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: योग"
                    ch2button.text = "अध्याय - 2: खेलों में मानसिकी"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: யோகா"
                    ch2button.text = "அகராதி - 2: கில்கியில் மானஸிகம்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

        elif agee == 16:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1button.text = "Ch - 1: Amines"
                    ch2button.text = "Ch - 2: Solutions"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: ऐमीन"
                    ch2button.text = "अध्याय - 2: समाधान"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அத்தியாயம் - 1: அமீன்கள்"
                    ch2button.text = "அத்தியாயம் - 2: தீர்வுகள்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1button.text = "Ch - 1: Diversity of Living Organisms"
                    ch2button.text = "Ch - 2: Cell: Structure and Function"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: जीव जंतुओं की विविधता"
                    ch2button.text = "अध्याय - 2: कोशिका: संरचना और कार्य"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: உயிரினங்களின் வைபாயம்"
                    ch2button.text = "அகராதி - 2: கோலாந்து: கட்டுரை மற்றும் செயல்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1button.text = "Ch - 1: Computational Thinking and Programming"

                    ch2button.text = "Ch - 2: Computer Networks"
                elif langg == "Hindi":
                    ch1button.text = "अध्याय - 1: संगणन सोच और प्रोग्रामिंग"
                    ch2button.text = "अध्याय - 2: कंप्यूटर नेटवर्क्स"
                    ch1button.font_name = "tirodevanagrihindi.ttf"
                    ch2button.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1button.text = "அகராதி - 1: கணித சிந்தனை மற்றும் குறிப்புரிமை"
                    ch2button.text = "அகராதி - 2: கணினி பிணையம்"
                    ch1button.font_name = "tirotamil.ttf"
                    ch2button.font_name = "tirotamil.ttf"

    def load_screens(self, dt):
        self.switch_to_loading()

    def switch_to_loading(self):
        self.loading_screen.start_loading()

    def switch_to_home(self):
        self.current = 'home_screen'

    def prevarscript_which_avg(self, whoclicked3):
        langg = self.stored_lang
        agee = int(self.stored_age)
        self.subjectClicked = int(whoclicked3)
        scoree = int(self.stored_score)
        print(langg)
        print(agee)
        print(self.subjectClicked)
        print(scoree)
        ch1buttonavg = self.root.get_screen("prevarscriptavg").ids.whichchapteravg
        #quiz1buttonavg = self.root.get_screen("prevarscriptavg").ids.whichquizavg
        ch2buttonavg = self.root.get_screen("prevarscriptavg").ids.whichchapter2avg
        #quiz2buttonavg = self.root.get_screen("prevarscriptavg").ids.whichquiz2avg
        ch3buttonavg = self.root.get_screen("prevarscriptavg").ids.whichchapter3avg
        #quiz3buttonavg = self.root.get_screen("prevarscriptavg").ids.whichquiz3avg
        if agee == 13:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Cell: The Fundamental Unit of Life"
                    ch2buttonavg.text = "Ch - 2: Matter Around Us"
                    ch3buttonavg.text = "Ch - 3: Tissues"
                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: कोशिका: जीवन की मौलिक इकाई"
                    ch2buttonavg.text = "अध्याय - 2: हमारे चारों ओर पदार्थ"
                    ch3buttonavg.text = "अध्याय - 3: ऊतक"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அத்தியாயம் - 1: உயிரின் அடிப்படை அலகு"
                    ch2buttonavg.text = "அத்தியாயம் - 2: உங்கள் சுற்றுலாவின் சுற்றுகள்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: உறுதி"
                    ch3buttonavg.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: People As Resource"
                    ch2buttonavg.text = "Ch - 2: Climate"
                    ch3buttonavg.text = "Ch - 3: Working of Institutions"
                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: लोगों के रूप में संसाधन"
                    ch2buttonavg.text = "अध्याय - 2: जलवायु"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: संस्थानों का कार्य"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: மக்கள் உள்ளடக்கம்"
                    ch2buttonavg.text = "அகராதி - 2: காரியம்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: அமைப்புகளின் செயல்திறன்"
                    ch3buttonavg.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Computer Networking"
                    ch2buttonavg.text = "Ch -2: Cyber Security"
                    ch2buttonavg.text = "Ch -3: Office Tools"
                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: कंप्यूटर नेटवर्किंग"
                    ch2buttonavg.text = "अध्याय - 2: साइबर सुरक्षा"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: कार्यालय साधन"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: கணினி பிணையம்"
                    ch2buttonavg.text = "அகராதி - 2: சைபர் பாதுகாப்பு"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: அலுவலக கருவிகள்"
                    ch3buttonavg.font_name = "tirotamil.ttf"


        elif agee == 14:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Metals & Non-Metals"
                    ch2buttonavg.text = "Ch - 2: Control & Coordination"
                    ch3buttonavg.text = "Ch - 3: Electricity"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: धातु और अधातु"
                    ch2buttonavg.text = "अध्याय - 2: नियंत्रण और समन्वय"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: बिजली"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அத்தியாயம் - 1: தாதுகள் மற்றும் அதாதுகள்"
                    ch2buttonavg.text = "அத்தியாயம் - 2: கட்டுப்பாடு மற்றும் ஒருங்கிணைப்பு"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: மின்சாரம்"
                    ch3buttonavg.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Water Resources"
                    ch2buttonavg.text = "Ch - 2: Consumer Rights"
                    ch3buttonavg.text = "Ch - 3: Money & Credit"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: जल संसाधन"
                    ch2buttonavg.text = "अध्याय - 2: उपभोक्ता अधिकार"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: धन और क्रेडिट"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: நீர் வளமும்"
                    ch2buttonavg.text = "அகராதி - 2: உபயோகத்தரக்காரர் உரிமைகள்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: பணமும் கடனும்"
                    ch3buttonavg.font_name = "tirotamil.ttf"


        elif self.subjectClicked == 3:
            if langg == "English":
                ch1buttonavg.text = "Ch - 1: Networking"
                ch2buttonavg.text = "Ch - 2: Cyber Ethics"
                ch3buttonavg.text = "Ch - 3: HTML"

            elif langg == "Hindi":
                ch1buttonavg.text = "अध्याय - 1: नेटवर्किंग"
                ch2buttonavg.text = "अध्याय - 2: साइबर एथिक्स"
                ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                ch3buttonavg.text = "अध्याय - 3: एचटीएमएल"
                ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

            elif langg == "Tamil":
                ch1buttonavg.text = "அகராதி - 1: பிணையம்"
                ch2buttonavg.text = "அகராதி - 2: சைபர் நீதிகள்"
                ch1buttonavg.font_name = "tirotamil.ttf"
                ch2buttonavg.font_name = "tirotamil.ttf"
                ch3buttonavg.text = "அத்தியாயம் - 3: எச்டிஎம்எல்"
                ch3buttonavg.font_name = "tirotamil.ttf"



        elif agee == 15:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Oscillation"
                    ch2buttonavg.text = "Ch - 2: Kinetic Energy"
                    ch3buttonavg.text = "Ch - 3: Gravitation"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: ओसिलेशन"
                    ch2buttonavg.text = "अध्याय - 2: नगतिज ऊर्जा"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: गुरुत्वाकर्षण"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அத்தியாயம் - 1: ஓசிலேஷன்"
                    ch2buttonavg.text = "அத்தியாயம் - 2: கினெடிக் எனஜி"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: உணர்வு"
                    ch3buttonavg.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Business: Nature & Purpose"
                    ch2buttonavg.text = "Ch - 2: Business Services"
                    ch3buttonavg.text = "Ch - 3: Internal Trade"
                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: व्यापार: प्रकृति और उद्देश्य"
                    ch2buttonavg.text = "अध्याय - 2: व्यापार सेवाएं"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: आंतरिक व्यापार"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: பணியின்: இயல்பு மற்றும் பொருள்"
                    ch2buttonavg.text = "அகராதி - 2: பணியின் சேவைகள்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: உள்ளோர் வர்த்தகம்"
                    ch3buttonavg.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Yoga"
                    ch2buttonavg.text = "Ch - 2: Psychology in Sports"
                    ch3buttonavg.text = "Ch - 3: Health and Wellness"
                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: योग"
                    ch2buttonavg.text = "अध्याय - 2: खेलों में मानसिकी"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: स्वास्थ्य और आरोग्य"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: யோகா"
                    ch2buttonavg.text = "அகராதி - 2: கில்கியில் மானஸிகம்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: ஆரோக்கியமும் உடல் நலமும்"
                    ch3buttonavg.font_name = "tirotamil.ttf"

        elif agee == 16:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Amines"
                    ch2buttonavg.text = "Ch - 2: Solutions"
                    ch3buttonavg.text = "Ch - 3: Biomolecules"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: ऐमीन"
                    ch2buttonavg.text = "अध्याय - 2: समाधान"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: जैव अणु"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttonavg.text = "அத்தியாயம் - 1: அமீன்கள்"
                    ch2buttonavg.text = "அத்தியாயம் - 2: தீர்வுகள்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: உயிரின் அணுகள்"
                    ch3buttonavg.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Diversity of Living Organisms"
                    ch2buttonavg.text = "Ch - 2: Cell: Structure and Function"
                    ch3buttonavg.text = "Ch - 3: Plant Physiology"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: जीव जंतुओं की विविधता"
                    ch2buttonavg.text = "अध्याय - 2: कोशिका: संरचना और कार्य"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: पौध भौतिकी"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: உயிரினங்களின் வைபாயம்"
                    ch2buttonavg.text = "அகராதி - 2: கோலாந்து: கட்டுரை மற்றும் செயல்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: கணிக இயக்கம்"
                    ch3buttonavg.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1buttonavg.text = "Ch - 1: Computational Thinking and Programming"
                    ch2buttonavg.text = "Ch - 2: Computer Networks"
                    ch3buttonavg.text = "Ch - 3: Database Management"

                elif langg == "Hindi":
                    ch1buttonavg.text = "अध्याय - 1: संगणन सोच और प्रोग्रामिंग"
                    ch2buttonavg.text = "अध्याय - 2: कंप्यूटर नेटवर्क्स"
                    ch1buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch2buttonavg.font_name = "tirodevanagrihindi.ttf"
                    ch3buttonavg.text = "अध्याय - 3: डेटाबेस प्रबंधन"
                    ch3buttonavg.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttonavg.text = "அகராதி - 1: கணித சிந்தனை மற்றும் குறிப்புரிமை"
                    ch2buttonavg.text = "அகராதி - 2: கணினி பிணையம்"
                    ch1buttonavg.font_name = "tirotamil.ttf"
                    ch2buttonavg.font_name = "tirotamil.ttf"
                    ch3buttonavg.text = "அத்தியாயம் - 3: தரவுத்தள நிர்வாகம்"
                    ch3buttonavg.font_name = "tirotamil.ttf"

    def prevarscript_which_top(self, whoclicked4):
        langg = self.stored_lang
        agee = int(self.stored_age)
        self.subjectClicked = int(whoclicked4)
        scoree = int(self.stored_score)
        print(langg)
        print(agee)
        print(self.subjectClicked)
        print(scoree)
        ch1buttontop = self.root.get_screen("prevarscripttop").ids.whichchaptertop
        #quiz1buttontop = self.root.get_screen("prevarscripttop").ids.whichquiztop
        ch2buttontop = self.root.get_screen("prevarscripttop").ids.whichchapter2top
        #quiz2buttontop = self.root.get_screen("prevarscripttop").ids.whichquiz2top
        ch3buttontop = self.root.get_screen("prevarscripttop").ids.whichchapter3top
        #quiz3buttontop = self.root.get_screen("prevarscripttop").ids.whichquiz3top
        ch4buttontop = self.root.get_screen("prevarscripttop").ids.whichchapter4top
        #quiz4buttontop = self.root.get_screen("prevarscripttop").ids.whichquiz3top

        if agee == 13:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Cell: The Fundamental Unit of Life"
                    ch2buttontop.text = "Ch - 2: Matter Around Us"
                    ch3buttontop.text = "Ch - 3: Tissues"
                    ch4buttontop.text = "Ch - 4: Atoms & Molecules"



                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: कोशिका: जीवन की मौलिक इकाई"
                    ch2buttontop.text = "अध्याय - 2: हमारे चारों ओर पदार्थ"
                    ch3buttontop.text = "अध्याय - 3: ऊतक"
                    ch4buttontop.text = "अध्याय - 4: परमाणु और अणु"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"


                elif langg == "Tamil":
                    ch1buttontop.text = "அத்தியாயம் - 1: உயிரின் அடிப்படை அலகு"
                    ch2buttontop.text = "அத்தியாயம் - 2: உங்கள் சுற்றுலாவின் சுற்றுகள்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: உறுதி"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: அணுக்கள் மற்றும் மூலக்கூறுகள்"
                    ch4buttontop.font_name = "tirotamil.ttf"

            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: People As Resource"
                    ch2buttontop.text = "Ch - 2: Climate"
                    ch3buttontop.text = "Ch - 3: Working of Institutions"
                    ch4buttontop.text = "Ch - 4: Nature"
                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: लोगों के रूप में संसाधन"
                    ch2buttontop.text = "अध्याय - 2: जलवायु"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: संस्थानों का कार्य"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: प्रकृति"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttontop.text = "அகராதி - 1: மக்கள் உள்ளடக்கம்"
                    ch2buttontop.text = "அகராதி - 2: காரியம்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: அமைப்புகளின் செயல்திறன்"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: இயல்பு"
                    ch4buttontop.font_name = "tirotamil.ttf"



            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Computer Networking"
                    ch2buttontop.text = "Ch -2: Cyber Security"
                    ch3buttontop.text = "Ch -3: Office Tools"
                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: कंप्यूटर नेटवर्किंग"
                    ch2buttontop.text = "अध्याय - 2: साइबर सुरक्षा"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: कार्यालय साधन"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                elif langg == "Tamil":
                    ch1buttontop.text = "அகராதி - 1: கணினி பிணையம்"
                    ch2buttontop.text = "அகராதி - 2: சைபர் பாதுகாப்பு"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: அலுவலக கருவிகள்"
                    ch3buttontop.font_name = "tirotamil.ttf"


        elif agee == 14:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Metals & Non-Metals"
                    ch2buttontop.text = "Ch - 2: Control & Coordination"
                    ch3buttontop.text = "Ch - 3: Electricity"
                    ch4buttontop.text = "Ch - 4: Sources of Energy"


                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: धातु और अधातु"
                    ch2buttontop.text = "अध्याय - 2: नियंत्रण और समन्वय"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: बिजली"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: ऊर्जा के स्रोत"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அத்தியாயம் - 1: தாதுகள் மற்றும் அதாதுகள்"
                    ch2buttontop.text = "அத்தியாயம் - 2: கட்டுப்பாடு மற்றும் ஒருங்கிணைப்பு"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: மின்சாரம்"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: காரணங்கள் உற்சாகம்"
                    ch4buttontop.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Water Resources"
                    ch2buttontop.text = "Ch - 2: Consumer Rights"
                    ch3buttontop.text = "Ch - 3: Money & Credit"
                    ch4buttontop.text = "Ch - 4: Developement"


                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: जल संसाधन"
                    ch2buttontop.text = "अध्याय - 2: उपभोक्ता अधिकार"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: धन और क्रेडिट"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: विकास"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அகராதி - 1: நீர் வளமும்"
                    ch2buttontop.text = "அகராதி - 2: உபயோகத்தரக்காரர் உரிமைகள்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: பணமும் கடனும்"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: பரவல்"
                    ch4buttontop.font_name = "tirotamil.ttf"



        elif self.subjectClicked == 3:
            if langg == "English":
                ch1buttontop.text = "Ch - 1: Networking"
                ch2buttontop.text = "Ch - 2: Cyber Ethics"
                ch3buttontop.text = "Ch - 3: HTML"

            elif langg == "Hindi":
                ch1buttontop.text = "अध्याय - 1: नेटवर्किंग"
                ch2buttontop.text = "अध्याय - 2: साइबर एथिक्स"
                ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                ch3buttontop.text = "अध्याय - 3: एचटीएमएल"
                ch3buttontop.font_name = "tirodevanagrihindi.ttf"

            elif langg == "Tamil":
                ch1buttontop.text = "அகராதி - 1: பிணையம்"
                ch2buttontop.text = "அகராதி - 2: சைபர் நீதிகள்"
                ch1buttontop.font_name = "tirotamil.ttf"
                ch2buttontop.font_name = "tirotamil.ttf"
                ch3buttontop.text = "அத்தியாயம் - 3: எச்டிஎம்எல்"
                ch3buttontop.font_name = "tirotamil.ttf"



        elif agee == 15:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Oscillation"
                    ch2buttontop.text = "Ch - 2: Kinetic Energy"
                    ch3buttontop.text = "Ch - 3: Gravitation"
                    ch4buttontop.text = "Ch - 4: Thermodynamics"


                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: ओसिलेशन"
                    ch2buttontop.text = "अध्याय - 2: नगतिज ऊर्जा"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: गुरुत्वाकर्षण"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: ऊष्म गतिविज्ञान"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அத்தியாயம் - 1: ஓசிலேஷன்"
                    ch2buttontop.text = "அத்தியாயம் - 2: கினெடிக் எனஜி"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: உணர்வு"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: உயிரினது வெப்பநிலையியல்"
                    ch4buttontop.font_name = "tirotamil.ttf"



        elif self.subjectClicked == 2:
            if langg == "English":
                ch1buttontop.text = "Ch - 1: Business: Nature & Purpose"
                ch2buttontop.text = "Ch - 2: Business Services"
                ch3buttontop.text = "Ch - 3: Internal Trade"
                ch4buttontop.text = "Ch - 4: Global Business"

            elif langg == "Hindi":
                ch1buttontop.text = "अध्याय - 1: व्यापार: प्रकृति और उद्देश्य"
                ch2buttontop.text = "अध्याय - 2: व्यापार सेवाएं"
                ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                ch3buttontop.text = "अध्याय - 3: आंतरिक व्यापार"
                ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                ch4buttontop.text = "अध्याय - 4: वैश्विक व्यापार"
                ch4buttontop.font_name = "tirodevanagrihindi.ttf"


            elif langg == "Tamil":
                ch1buttontop.text = "அகராதி - 1: பணியின்: இயல்பு மற்றும் பொருள்"
                ch2buttontop.text = "அகராதி - 2: பணியின் சேவைகள்"
                ch1buttontop.font_name = "tirotamil.ttf"
                ch2buttontop.font_name = "tirotamil.ttf"
                ch3buttontop.text = "அத்தியாயம் - 3: உள்ளோர் வர்த்தகம்"
                ch3buttontop.font_name = "tirotamil.ttf"
                ch4buttontop.text = "அத்தியாயம் - 4: உலக வணிகம்"
                ch4buttontop.font_name = "tirotamil.ttf"



        elif self.subjectClicked == 3:
            if langg == "English":
                ch1buttontop.text = "Ch - 1: Yoga"
                ch2buttontop.text = "Ch - 2: Psychology in Sports"
                ch3buttontop.text = "Ch - 3: Health and Wellness"
            elif langg == "Hindi":
                ch1buttontop.text = "अध्याय - 1: योग"
                ch2buttontop.text = "अध्याय - 2: खेलों में मानसिकी"
                ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                ch3buttontop.text = "अध्याय - 3: स्वास्थ्य और आरोग्य"
                ch3buttontop.font_name = "tirodevanagrihindi.ttf"

            elif langg == "Tamil":
                ch1buttontop.text = "அகராதி - 1: யோகா"
                ch2buttontop.text = "அகராதி - 2: கில்கியில் மானஸிகம்"
                ch1buttontop.font_name = "tirotamil.ttf"
                ch2buttontop.font_name = "tirotamil.ttf"
                ch3buttontop.text = "அத்தியாயம் - 3: ஆரோக்கியமும் உடல் நலமும்"
                ch3buttontop.font_name = "tirotamil.ttf"

        elif agee == 16:
            if self.subjectClicked == 1:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Amines"
                    ch2buttontop.text = "Ch - 2: Solutions"
                    ch3buttontop.text = "Ch - 3: Biomolecules"
                    ch4buttontop.text = "Ch - 4: Electrochemistry"


                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: ऐमीन"
                    ch2buttontop.text = "अध्याय - 2: समाधान"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: जैव अणु"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: विद्युत रसायन"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அத்தியாயம் - 1: அமீன்கள்"
                    ch2buttontop.text = "அத்தியாயம் - 2: தீர்வுகள்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: உயிரின் அணுகள்"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: மின் ராசாயனம்"
                    ch4buttontop.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 2:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Diversity of Living Organisms"
                    ch2buttontop.text = "Ch - 2: Cell: Structure and Function"
                    ch3buttontop.text = "Ch - 3: Plant Physiology"
                    ch4buttontop.text = "Ch - 4: Biological Structures"


                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: जीव जंतुओं की विविधता"
                    ch2buttontop.text = "अध्याय - 2: कोशिका: संरचना और कार्य"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: पौध भौतिकी"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch4buttontop.text = "अध्याय - 4: जैविक संरचनाएँ"
                    ch4buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அகராதி - 1: உயிரினங்களின் வைபாயம்"
                    ch2buttontop.text = "அகராதி - 2: கோலாந்து: கட்டுரை மற்றும் செயல்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: கணிக இயக்கம்"
                    ch3buttontop.font_name = "tirotamil.ttf"
                    ch4buttontop.text = "அத்தியாயம் - 4: உயிரியல் கட்டிகள்"
                    ch4buttontop.font_name = "tirotamil.ttf"


            elif self.subjectClicked == 3:
                if langg == "English":
                    ch1buttontop.text = "Ch - 1: Computational Thinking and Programming"
                    ch2buttontop.text = "Ch - 2: Computer Networks"
                    ch3buttontop.text = "Ch - 3: Database Management"

                elif langg == "Hindi":
                    ch1buttontop.text = "अध्याय - 1: संगणन सोच और प्रोग्रामिंग"
                    ch2buttontop.text = "अध्याय - 2: कंप्यूटर नेटवर्क्स"
                    ch1buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch2buttontop.font_name = "tirodevanagrihindi.ttf"
                    ch3buttontop.text = "अध्याय - 3: डेटाबेस प्रबंधन"
                    ch3buttontop.font_name = "tirodevanagrihindi.ttf"

                elif langg == "Tamil":
                    ch1buttontop.text = "அகராதி - 1: கணித சிந்தனை மற்றும் குறிப்புரிமை"
                    ch2buttontop.text = "அகராதி - 2: கணினி பிணையம்"
                    ch1buttontop.font_name = "tirotamil.ttf"
                    ch2buttontop.font_name = "tirotamil.ttf"
                    ch3buttontop.text = "அத்தியாயம் - 3: தரவுத்தள நிர்வாகம்"
                    ch3buttontop.font_name = "tirotamil.ttf"

    def prevarscriptchange(self):
        pass

    def prevarscript_which(self, whoclicked):
        screen_manger = ScreenManager()
        scoree = int(self.stored_score)
        print(scoree)
        clicked2 = int(whoclicked)
        if 0 <= scoree <= 3:
            self.prevarscript_which_poor(clicked2)
            self.screen_manager.current = 'prevarscriptpoor'
        elif 4 <= scoree <= 6:
            self.prevarscript_which_avg(clicked2)
            self.screen_manager.current = 'prevarscriptavg'
        elif 7 <= scoree <= 10:
            self.prevarscript_which_top(clicked2)
            self.screen_manager.current = 'prevarscripttop'

    def varscriptscript_name(self):
        pass
    def setsubjecttozero(self):
        self.subjectClicked = 0
    def checkvisibility(self):
        subjectt = int(self.subjectClicked)
        #whichquiz4top = self.root.get_screen('prevarscripttop').ids.whichquiz4top
        whichchapter4top = self.root.get_screen('prevarscripttop').ids.whichchapter4top
        prevartophide = self.root.get_screen('prevarscripttop').ids.prevartop3
        prevartop = self.root.get_screen('prevarscripttop').ids.prevartop

        print(f"subjectt: {subjectt}")
        if subjectt == 3:
            #whichquiz4top.opacity = 0
            whichchapter4top.opacity = 0
            prevartophide.opacity = 1
            prevartop.opacity = 0

    """def change_video_source(self):
        video_widget = self.root.ids.video_player

        # Set the new video source
        new_source = self.mastervariablemp4
        video_widget.source = new_source

        video_widget.pause()"""

    """def change_vid_aud_state(self):
        # video_widget = self.root.ids.video_player
        print("Hello")

        # video_widget.play()
        if video_widget.state == 'play':
            self.pause_audio()
            video_widget.stop()
        else:
            video_widget.play()
            self.play_audio()"""

    def load_screens(self):
        self.loading_screen.start_loading()
    def vidScreenHeadTxt(self, whoclicked):
        langg = self.stored_lang
        agee = int(self.stored_age)
        scoree = int(self.stored_score)
        self.subjectClicked = int(whoclicked)
        print(langg)
        print(agee)
        print(scoree)
        print(self.subjectClicked)
        vidScreenHeadTxt = self.root.get_screen("varscript").ids.vidScreenHeadTxt

    def gettextch1(self, btnno):
        selectedBtn = int(btnno)
        agee = int(self.stored_age)
        scoree = int(self.stored_score)
        if agee == 13:
            if 0 <= scoree <= 3:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "FUL"
                    elif selectedBtn == 2:
                        self.chapter_name = "MAT"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "NET"
                    elif selectedBtn == 2:
                        self.chapter_name = "SEC"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "PPL"
                    elif selectedBtn == 2:
                        self.chapter_name = "CLI"
            elif 4 <= scoree <= 6:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "FUL"
                    elif selectedBtn == 2:
                        self.chapter_name = "MAT"
                    elif selectedBtn == 3:
                        self.chapter_name = "TIS"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "NET"
                    elif selectedBtn == 2:
                        self.chapter_name = "SEC"
                    elif selectedBtn == 3:
                        self.chapter_name = "OFF"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "PPL"
                    elif selectedBtn == 2:
                        self.chapter_name = "CLI"
                    elif selectedBtn == 3:
                        self.chapter_name = "WOR"
            elif 7 <= scoree <= 10:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "FUL"
                    elif selectedBtn == 2:
                        self.chapter_name = "MAT"
                    elif selectedBtn == 3:
                        self.chapter_name = "TIS"
                    elif selectedBtn == 4:
                        self.chapter_name = "ATO"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "NET"
                    elif selectedBtn == 2:
                        self.chapter_name = "SEC"
                    elif selectedBtn == 3:
                        self.chapter_name = "OFF"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "PPL"
                    elif selectedBtn == 2:
                        self.chapter_name = "CLI"
                    elif selectedBtn == 3:
                        self.chapter_name = "WOR"
                    elif selectedBtn == 4:
                        self.chapter_name = "NAT"
        elif agee == 14:
            if 0 <= scoree <= 3:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "MET"
                    elif selectedBtn == 2:
                        self.chapter_name = "CON"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "WAT"
                    elif selectedBtn == 2:
                        self.chapter_name = "COR"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "NE1"

            elif 4 <= scoree <= 6:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "MET"
                    elif selectedBtn == 2:
                        self.chapter_name = "CON"
                    elif selectedBtn == 3:
                        self.chapter_name = "ELE"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "WAT"
                    elif selectedBtn == 2:
                        self.chapter_name = "COR"
                    elif selectedBtn == 3:
                        self.chapter_name = "MON"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "NE1"
                    elif selectedBtn == 2:
                        self.chapter_name = "ETH"

            elif 7 <= scoree <= 10:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "MET"
                    elif selectedBtn == 2:
                        self.chapter_name = "CON"
                    elif selectedBtn == 3:
                        self.chapter_name = "ELE"
                    elif selectedBtn == 4:
                        self.chapter_name = "SOU"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "WAT"
                    elif selectedBtn == 2:
                        self.chapter_name = "COR"
                    elif selectedBtn == 3:
                        self.chapter_name = "MON"
                    elif selectedBtn == 4:
                        self.chapter_name = "RES"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "NE1"
                    elif selectedBtn == 2:
                        self.chapter_name = "ETH"
                    elif selectedBtn == 3:
                        self.chapter_name = "HTM"
        elif agee == 15:
            if 0 <= scoree <= 3:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "OSC"
                    elif selectedBtn == 2:
                        self.chapter_name = "KIN"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "BNP"
                    elif selectedBtn == 2:
                        self.chapter_name = "BSE"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "YOG"

            elif 4 <= scoree <= 6:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "OSC"
                    elif selectedBtn == 2:
                        self.chapter_name = "KIN"
                    elif selectedBtn == 3:
                        self.chapter_name = "GRA"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "BNP"
                    elif selectedBtn == 2:
                        self.chapter_name = "BSE"
                    elif selectedBtn == 3:
                        self.chapter_name = "INT"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "YOG"
                    elif selectedBtn == 2:
                        self.chapter_name = "PSY"

            elif 7 <= scoree <= 10:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "OSC"
                    elif selectedBtn == 2:
                        self.chapter_name = "KIN"
                    elif selectedBtn == 3:
                        self.chapter_name = "GRA"
                    elif selectedBtn == 4:
                        self.chapter_name = "THE"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "BNP"
                    elif selectedBtn == 2:
                        self.chapter_name = "BSE"
                    elif selectedBtn == 3:
                        self.chapter_name = "INT"
                    elif selectedBtn == 4:
                        self.chapter_name = "GLO"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "YOG"
                    elif selectedBtn == 2:
                        self.chapter_name = "PSY"
                    elif selectedBtn == 3:
                        self.chapter_name = "HEA"
        elif agee == 16:
            if 0 <= scoree <= 3:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "AMI"
                    elif selectedBtn == 2:
                        self.chapter_name = "SOL"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "DIV"
                    elif selectedBtn == 2:
                        self.chapter_name = "CEL"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "COM"

            elif 4 <= scoree <= 6:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "AMI"
                    elif selectedBtn == 2:
                        self.chapter_name = "SOL"
                    elif selectedBtn == 3:
                        self.chapter_name = "BIO"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "DIV"
                    elif selectedBtn == 2:
                        self.chapter_name = "CEL"
                    elif selectedBtn == 3:
                        self.chapter_name = "PLA"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "COM"
                    elif selectedBtn == 2:
                        self.chapter_name = "CNE"

            elif 7 <= scoree <= 10:
                if self.subjectClicked == 1:
                    if selectedBtn == 1:
                        self.chapter_name = "AMI"
                    elif selectedBtn == 2:
                        self.chapter_name = "SOL"
                    elif selectedBtn == 3:
                        self.chapter_name = "BIO"
                    elif selectedBtn == 4:
                        self.chapter_name = "ECH"
                elif self.subjectClicked == 3:
                    if selectedBtn == 1:
                        self.chapter_name = "DIV"
                    elif selectedBtn == 2:
                        self.chapter_name = "CEL"
                    elif selectedBtn == 3:
                        self.chapter_name = "PLA"
                    elif selectedBtn == 4:
                        self.chapter_name = "BST"
                elif self.subjectClicked == 2:
                    if selectedBtn == 1:
                        self.chapter_name = "COM"
                    elif selectedBtn == 2:
                        self.chapter_name = "CNE"
                    elif selectedBtn == 3:
                        self.chapter_name = "DAT"

    def changechangemastervar(self):
        gobackchangemastervar = 0
        self.changemastervar = gobackchangemastervar
    def make_mastervariable(self):
        langg = self.stored_lang
        agee = int(self.stored_age)
        scoree = int(self.stored_score)
        # Illuminat.gettextch1()
        chapterr = self.chapter_name
        questionn = int(self.questionnumber)
        subjectt = self.subjectClicked
        txt = ".txt"
        mp4 = ".mp4"
        mp3 = ".wav"
        print(langg)
        print(agee)
        print(scoree)
        print(chapterr)
        print(self.subjectClicked)
        if self.changemastervar == 0:
            if subjectt == 2:
                subjectt = 3
            elif subjectt == 3:
                subjectt = 2
            self.changemastervar = 1
        else:
            pass
        print(questionn)
        mastervar = langg + str(agee) + str(scoree) + str(subjectt) + chapterr + str(questionn)
        self.mastervariable = mastervar
        print(mastervar)
        print(self.mastervariable)
        self.mastervariabletxt = self.mastervariable + str(txt)
        print(self.mastervariable)
        print(self.mastervariabletxt)
        mastervariablemp4 = str(self.mastervariable) + str(mp4)
        self.mastervariablemp4 = mastervariablemp4
        print(mastervariablemp4)
        print(self.mastervariablemp4)
        self.mastervariablemp3 = str(self.mastervariable) + str(mp3)
        print(mastervar)
        print(self.mastervariablemp3)
        mastervarr = langg + str(agee) + str(scoree) + str(subjectt) + chapterr + str(questionn)
        self.mastervariabletxtupdated = mastervarr
        print(mastervarr)
        print(self.mastervariabletxtupdated)
        self.mastervariabletxtupdated = self.mastervariabletxtupdated + str(txt)
        print(self.mastervariabletxtupdated)
        print(self.mastervariabletxtupdated)
        self.mastervariablemp3updated = str(mastervarr) + str(mp3)

        print(mastervarr)
        print(
            f"This includes everything, {mastervarr}, {self.mastervariabletxtupdated}, {self.mastervariablemp3updated}")
        print(self.mastervariablemp3updated)
        print(f"I am self.mastervariablemp3updated: {self.mastervariablemp3updated}")
        if langg == "Hindi":
            print("I am Hindi")
            langgnew = "English"
            agee = int(self.stored_age)
            scoree = int(self.stored_score)
            chapterr = self.chapter_name
            questionn = int(self.questionnumber)
            txt = ".txt"
            # mp4 = ".mp4"
            mp3 = ".wav"
            print(langgnew)
            print(agee)
            print(scoree)
            print(chapterr)
            print(self.subjectClicked)
            print(questionn)
            mastervarr = langgnew + str(agee) + str(scoree) + str(subjectt) + chapterr + str(questionn)
            self.mastervariabletxtupdated = mastervarr
            print(mastervarr)
            print(self.mastervariabletxtupdated)
            self.mastervariabletxtupdated = self.mastervariabletxtupdated + str(txt)
            print(self.mastervariabletxtupdated)
            print(self.mastervariabletxtupdated)
            self.mastervariablemp3updated = str(mastervarr) + str(mp3)
            print(mastervarr)
            print(
                f"This includes everything, {mastervarr}, {self.mastervariabletxtupdated}, {self.mastervariablemp3updated}")
            print(self.mastervariablemp3updated)
        elif langg == "Tamil":
            langgnew = "English"
            print("I am Tamil")
            agee = int(self.stored_age)
            scoree = int(self.stored_score)
            chapterr = self.chapter_name
            questionn = int(self.questionnumber)
            txt = ".txt"
            # mp4 = ".mp4"
            # mp3 = ".wav"
            print(langgnew)
            print(agee)
            print(scoree)
            print(chapterr)
            print(self.subjectClicked)
            print(questionn)
            mastervar = langgnew + str(agee) + str(scoree) + str(subjectt) + chapterr + str(questionn)
            self.mastervariabletxtupdated = mastervar
            print(mastervar)
            print(self.mastervariabletxtupdated)
            self.mastervariabletxtupdated = self.mastervariabletxtupdated + str(txt)
            print(self.mastervariabletxtupdated)
            print(self.mastervariabletxtupdated)
            self.mastervariablemp3updated = str(mastervar) + str(mp3)
            print(mastervar)
            print(
                f"This includes everything, {mastervar}, {self.mastervariabletxtupdated}, {self.mastervariablemp3updated}")
            print(self.mastervariablemp3updated)
        else:
            print(self.mastervariablemp4)
        self.subjectClicked = subjectt

    def btn4txt_which(self):
        langg = self.stored_lang
        homescreenbtn4 = self.root.get_screen("home").ids.btn4home
        coursebtn4 = self.root.get_screen("home").ids.coursehome
        #profbtn4 = self.root.get_screen("home").ids.profhome
        if langg == "English":
            homescreenbtn4.text = "clAIrty"
            coursebtn4.text = "Course"
            #profbtn4.text = "Profile"
        elif langg == "Hindi":
            homescreenbtn4.text = "क्लेयर्टी"
            #homescreenbtn4.font_name = "tirodevanagrihindi.ttf"
            coursebtn4.text = "कोर्स"
            #profbtn4.text = "प्रोफ़ाइल"
        elif langg == "Tamil":
            homescreenbtn4.text = "க்லைர்டி"
            coursebtn4.text = "பாடக்கோப்பு"
            #profbtn4.text = "சுயவிவரம்"
            #homescreenbtn4.font_name = "tirotamil.ttf"

    def btn1_text_which(self):
        langg = self.stored_lang
        agee = int(self.stored_age)
        print(langg)
        print(agee)
        homescreenbutton = self.root.get_screen("home").ids.btn1home
        homescreenbutton3 = self.root.get_screen("home").ids.btn2home
        homescreenbutton2 = self.root.get_screen("home").ids.btn3home
        if 13 <= agee <= 14:
            if langg == "English":
                homescreenbutton.text = "SCIENCE"
                homescreenbutton2.text = "SOCIAL SCIENCE"
                homescreenbutton3.text = "COMPUTERS"

            elif langg == "Hindi":
                homescreenbutton.text = "विज्ञान"
                homescreenbutton.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton2.text = "सामाजिक विज्ञान"
                homescreenbutton2.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton3.text = "कंप्यूटर"
                homescreenbutton3.font_name = "tirodevanagrihindi.ttf"

            elif langg == "Tamil":
                homescreenbutton.text = "அறிவியல்"
                homescreenbutton.font_name = "tirotamil.ttf"

                homescreenbutton2.text = "சமூக அறிவியல்"
                homescreenbutton2.font_name = "tirotamil.ttf"

                homescreenbutton3.text = "கணினியியல்"
                homescreenbutton3.font_name = "tirotamil.ttf"
            else:
                homescreenbutton.text = "O"
        elif agee == 15:
            if langg == "English":
                homescreenbutton.text = "PHYSICS"
                homescreenbutton2.text = "BUSINESS STUDIES"
                homescreenbutton3.text = "PHYSICAL EDUCATION"
            elif langg == "Hindi":
                homescreenbutton.text = "भौतिक विज्ञान"
                homescreenbutton.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton2.text = "व्यापार अध्ययन"
                homescreenbutton2.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton3.text = "शारीरिक शिक्षा"
                homescreenbutton3.font_name = "tirodevanagrihindi.ttf"
            elif langg == "Tamil":
                homescreenbutton.text = "இயற்பியல்"
                homescreenbutton.font_name = "tirotamil.ttf"

                homescreenbutton2.text = "வணிக ஆராய்ச்சி"
                homescreenbutton2.font_name = "tirotamil.ttf"

                homescreenbutton3.text = "உடல் கல்வி"
                homescreenbutton3.font_name = "tirotamil.ttf"

        elif agee == 16:
            if langg == "English":
                homescreenbutton.text = "Chemistry"
                homescreenbutton2.text = "Biology"
                homescreenbutton3.text = "Computers"
            elif langg == "Hindi":
                homescreenbutton.text = "रसायन विज्ञान"
                homescreenbutton.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton2.text = "जीवशास्त्र"
                homescreenbutton2.font_name = "tirodevanagrihindi.ttf"

                homescreenbutton3.text = "कंप्यूटर"
                homescreenbutton3.font_name = "tirodevanagrihindi.ttf"
            elif langg == "Tamil":
                homescreenbutton.text = "ரசாயன அறிவியல்"
                homescreenbutton.font_name = "tirotamil.ttf"

                homescreenbutton2.text = "உயிரியல்"
                homescreenbutton2.font_name = "tirotamil.ttf"

                homescreenbutton3.text = "கணினியியல்"
                homescreenbutton3.font_name = "tirotamil.ttf"

    def filter_input(self, instance, mode):
        if mode == 'int':
            instance.text = ''.join(filter(str.isdigit, instance.text))
            instance.bind(text=self.check_input_range)

    def check_input_range(self, instance, value):

        if value:
            num_value = int(value)
            if num_value < 13:
                instance.text = '13'

            elif num_value > 16:
                instance.text = '16'
            elif 13 <= num_value <= 16:
                instance.text = str(num_value)

    def on_button_click(self):
        """screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("varscript.kv"))"""
        self.make_mastervariable()

        # return Builder.load_string(KV)
        self.generate_and_download_images_list() #enable this to make video
        # self.change_video_source()
        #self.image_to_video_science()

    def change_video_source(self):
        video_player = self.root.get_screen('varscript').ids.video_player
        clicktostarttext = self.root.get_screen('varscript').ids.video_player
        # video_player.source = self.mastervariablemp4
        """video_player.source = 'Hindi1333PPL1.mp4'
        print(f"MasterVarMp4: {self.mastervariablemp4}")
        print(f"Myself Here eogjhohjtiyohjiotyjhioythiotj: {self.mastervariablemp4}")"""
        """video = Video(source="Hindi1333PPL1.mp4", state='play')
        return video"""
        video_player.source = self.mastervariablemp4
        video_player.size = (.7, .7)
        print(self.mastervariablemp4)

        video_player.state = 'play'

    def btnclickornot(self):
        if self.btnClick == 0:
            Illuminat.btnClick = 1
        else:
            Illuminat.btnClick = 0
        if self.btnClick == 1:
            Illuminat.finalClick_lang = 1
        else:
            Illuminat.finalClick_lang = 0

    def btnclickornot_hindi(self):
        if self.btnClick_hindi == 0:
            Illuminat.btnClick_hindi = 1
        else:
            Illuminat.btnClick_hindi = 0
        if self.btnClick_hindi == 1:
            Illuminat.finalClick_lang_hindi = 1
        else:
            Illuminat.finalClick_lang_hindi = 0

    def btnclickornot_tamil(self):
        if self.btnClick_tamil == 0:
            Illuminat.btnClick_tamil = 1
        else:
            Illuminat.btnClick_tamil = 0
        if self.btnClick_tamil == 1:
            Illuminat.finalClick_lang_tamil = 1
        else:
            Illuminat.finalClick_lang_tamil = 0

    def senddetailsfromsignup(self):
        current_screen = self.root.current_screen

        if Illuminat.users_ref is None:

            user = auth.create_user(self.entered_email, self.entered_password)
            uid = user.uid
            Illuminat.users_ref = firestore.client().collection('icystriall').document(uid)

        if self.finalClick_lang == 1:
            self.finalClick_lang_hindi = 0
            self.finalClick_lang_tamil = 0
            print("English")
            self.stored_lang = "English"

            additionalinfo = {
                'lang': 'English'
            }
            Illuminat.users_ref.update(additionalinfo)

            print("Added")
        elif self.finalClick_lang_hindi == 1:
            self.finalClick_lang = 0
            self.finalClick_lang_tamil = 0
            print("Hindi")
            self.stored_lang = "Hindi"
            additionalinfo = {
                'lang': 'Hindi'
            }
            Illuminat.users_ref.update(additionalinfo)

            print("Added")
        elif self.finalClick_lang_tamil == 1:
            self.finalClick_lang = 0
            self.finalClick_lang_hindi = 0
            print("Tamil")
            self.stored_lang = "Tamil"
            additionalinfo = {
                'lang': 'Tamil'
            }
            Illuminat.users_ref.update(additionalinfo)

            print("Added")
        else:
            print("Nothing")

        age_input = current_screen.ids.signup_age
        entered_age = age_input.text

        try:
            age_value = int(entered_age)
            self.stored_age = age_value
            age_final = self.stored_age
            print(age_final)
        except ValueError:
            print("Invalid age format")

        ageInput = {
            'age': entered_age
        }

        Illuminat.users_ref.update(ageInput)
        print("Debug: senddetailsfromsignup method completed")

        print("Score:", self.stored_score, "Lang:", self.stored_lang, "Age:", self.stored_age)

        self.btn1_text_which()
        self.btn4txt_which()


        """if current_screen.name == "questions":
            if  age_final == 13:
                screen_manager.current = "questions"
            elif age_final == 15:
                screen_manager.current = "questionsolder"
                """

    """def displayLang(self):
        if 'lang' == 'English':
            pass"""

    def get_question_based_on_age(self):
        print("Debug: Entered get_question_based_on_age method")

        age_in_class = int(Illuminat.age_what)

        print(age_in_class)

        if 13 <= age_in_class <= 16:
            if 13 <= age_in_class <= 14:
                return "You are in the 13-14 age group. Ask questions accordingly."
            elif 15 <= age_in_class <= 16:
                return "You are in the 15-16 age group. Ask questions accordingly."
            else:
                print("Debug: Should not reach here. Inner if conditions failed.")
                return "Invalid Age"
        else:
            print("Debug: Should not reach here. Outer if condition failed.")
            return "Invalid Age"

    def question_text(self):
        if Illuminat.question_number == 1:

            return "If the perimeter of a rectangle is 28 cm, and its length is 7 cm, what is the width?"
            # Illuminat.question_number += 1
        elif Illuminat.question_number == 2:
            """question_widget = self.root.ids.questiontxt
            question_widget.text = 'What is the process by which plants make their own food using sunlight?'"""

            return "What is the process by which plants make their own food using sunlight?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 3:
            return "Who was the first President of India?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 4:
            return "If a triangle has sides of lengths 3 cm, 4 cm, and 5 cm, what type of triangle is it?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 5:
            return "What is the largest planet in our solar system?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 6:
            return "Which ocean is the largest in terms of both area and volume?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 7:
            return "If a square has an area of 25 square units, what is the length of one side?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 8:
            return "What is the function of the human heart?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 9:
            return "In India, who is considered the head of the state?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 10:
            return "Which of the below angles is equal to 1/4 the sum of angles of any quadrilateral?"
            # Illuminat.question_number +=1
        elif Illuminat.question_number == 11:
            return "You have answered the 10 questions! Congratulations! Great"
            # Illuminat.question_number +=1

    def question_number_text(self):
        if Illuminat.question_number == 1:
            return "Q1/10"
        elif Illuminat.question_number == 2:
            return "Q2/10"
        elif Illuminat.question_number == 3:
            return "Q3/10"
        elif Illuminat.question_number == 4:
            return "Q4/10"
        elif Illuminat.question_number == 5:
            return "Q5/10"
        elif Illuminat.question_number == 6:
            return "Q6/10"
        elif Illuminat.question_number == 7:
            return "Q7/10"
        elif Illuminat.question_number == 8:
            return "Q8/10"
        elif Illuminat.question_number == 9:
            return "Q9/10"
        elif Illuminat.question_number == 10:
            return "Q10/10"
        elif Illuminat.question_number == 11:
            return "Completed!"

    def button_one_text(self):
        if Illuminat.question_number == 1:
            return "A) 3cm"
        elif Illuminat.question_number == 2:
            return "A) Respiration"
        elif Illuminat.question_number == 3:
            return "A) Jawaharlal Nehru"
        elif Illuminat.question_number == 4:
            return "A) Equilateral"
        elif Illuminat.question_number == 5:
            return "A) Earth"
        elif Illuminat.question_number == 6:
            return "A) Indian Ocean"
        elif Illuminat.question_number == 7:
            return "A) 3 units"
        elif Illuminat.question_number == 8:
            return "A) Pumping blood"
        elif Illuminat.question_number == 9:
            return "A) President"
        elif Illuminat.question_number == 10:
            return "A) 45 degrees"
        elif Illuminat.question_number == 11:
            return "W"

    def button_two_text(self):
        if Illuminat.question_number == 1:
            return "B) 5cm"
        elif Illuminat.question_number == 2:
            return "B) Photosynthesis"
        elif Illuminat.question_number == 3:
            return "B) Dr. B.R. Ambedkar"
        elif Illuminat.question_number == 4:
            return "B) Isoceles"
        elif Illuminat.question_number == 5:
            return "B) Jupiter"
        elif Illuminat.question_number == 6:
            return "B) Atlantic Ocean"
        elif Illuminat.question_number == 7:
            return "B) 5 units"
        elif Illuminat.question_number == 8:
            return "B) Digestion"
        elif Illuminat.question_number == 9:
            return "B) Prime Minister"
        elif Illuminat.question_number == 10:
            return "B) 60 degrees"
        elif Illuminat.question_number == 11:
            return "O"

    def button_three_text(self):
        if Illuminat.question_number == 1:
            return "C) 7cm"
        elif Illuminat.question_number == 2:
            return "C) Transpiration"
        elif Illuminat.question_number == 3:
            return "C) Sardar Vallabhbhai Patel"
        elif Illuminat.question_number == 4:
            return "C) Scalene"
        elif Illuminat.question_number == 5:
            return "C) Saturn"
        elif Illuminat.question_number == 6:
            return "C) Southern Ocean"
        elif Illuminat.question_number == 7:
            return "C) 6 units"
        elif Illuminat.question_number == 8:
            return "C) Filtering waste"
        elif Illuminat.question_number == 9:
            return "C) Monarch"
        elif Illuminat.question_number == 10:
            return "C) 90 degrees"
        elif Illuminat.question_number == 11:
            return "R"

    def button_four_text(self):
        if Illuminat.question_number == 1:
            return "D) 14 cm"
        elif Illuminat.question_number == 2:
            return "D) Fermentation"
        elif Illuminat.question_number == 3:
            return "D) Dr. Rajendra Prasad"
        elif Illuminat.question_number == 4:
            return "D) Right-angled"
        elif Illuminat.question_number == 5:
            return "D) Mars"
        elif Illuminat.question_number == 6:
            return "D) Pacific Ocean"
        elif Illuminat.question_number == 7:
            return "D) 25 units"
        elif Illuminat.question_number == 8:
            return "D) Storing nutrients"
        elif Illuminat.question_number == 9:
            return "D) Chief Justice"
        elif Illuminat.question_number == 10:
            return "D) 120 degrees"
        elif Illuminat.question_number == 11:
            return "K"

    def btnclickornot_one(self):
        if self.btnClick_questions == 0:
            Illuminat.btnClick_questions = 1
        else:
            Illuminat.btnClick_questions = 0
        if self.btnClick_questions == 1:
            Illuminat.finalClick_ans_one = 1
        else:
            Illuminat.finalClick_ans_one = 0

    def btnclickornot_two(self):
        if self.btnClick_questions == 0:
            Illuminat.btnClick_questions = 1
        else:
            Illuminat.btnClick_questions = 0
        if self.btnClick_questions == 1:
            Illuminat.finalClick_ans_two = 1
        else:
            Illuminat.finalClick_ans_two = 0

    def btnclickornot_three(self):
        if self.btnClick_questions == 0:
            Illuminat.btnClick_questions = 1
        else:
            Illuminat.btnClick_questions = 0
        if self.btnClick_questions == 1:
            Illuminat.finalClick_ans_three = 1
        else:
            Illuminat.finalClick_ans_three = 0

    def btnclickornot_four(self):
        if self.btnClick_questions == 0:
            Illuminat.btnClick_questions = 1
        else:
            Illuminat.btnClick_questions = 0
        if self.btnClick_questions == 1:
            Illuminat.finalClick_ans_four = 1
        else:
            Illuminat.finalClick_ans_four = 0

    def submitbtn_text(self):
        if Illuminat.question_number in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            return "Submit"
        elif Illuminat.question_number == 11:
            return "Next Step"

    def questionsscreenstartwidget(self):
        qStart = self.root.get_screen('questionsscreen').ids.questionStart
        tStart = self.root.get_screen('questionsscreen').ids.txtStart
        queStart = self.root.get_screen('questionsscreen').ids.questiontxt
        queNo = self.root.get_screen('questionsscreen').ids.questionno
        anHere = self.root.get_screen('questionsscreen').ids.ansHere
        Sbtn = self.root.get_screen('questionsscreen').ids.submitBtn
        if self.questionscreennumber == 0:
            qStart.opacity = 0
            tStart.opacity = 0
            queStart.opacity = 1
            queNo.opacity = 1
            anHere.opacity = 1
            Sbtn.opacity = 1
            self.questionscreennumber = 1



    def submitbtn_whattodo(self):
        langg = self.stored_lang
        age = int(self.stored_age)
        if Illuminat.question_number == 1:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_three == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)
               
                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_four == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")


        elif Illuminat.question_number == 2:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_three == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")


        elif Illuminat.question_number == 3:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_four == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_three == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 4:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_four == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 5:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_one == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 6:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_four == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 7:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_one == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 8:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_one == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_four == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 9:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_one == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_three == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")



        elif Illuminat.question_number == 10:
            if 13 <= age <= 14:
                if Illuminat.finalClick_ans_three == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")
                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            elif 15 <= age <= 16:
                if Illuminat.finalClick_ans_two == 1:
                    Illuminat.question_number += 1
                    """self.update_screen(dt=0)


                    self.update_screen()"""
                    Illuminat.questions_score += 1
                    print(Illuminat.questions_score)
                    print("Clicked")

                else:
                    Illuminat.questions_score += 0
                    Illuminat.question_number += 1
                    print(Illuminat.questions_score)
                    print("Clickedw")
            self.screen_manager.current = 'home'
            Illuminat.questions_score = Illuminat.score_final
            Illuminat.score_final = self.stored_score
            self.stored_score = Illuminat.score_final
            scoreinfo = {
                'score': Illuminat.score_final
            }
            Illuminat.users_ref.update(scoreinfo)
        elif Illuminat.question_number == 11:




            Illuminat.score_final = self.stored_score
            scoreinfo = {
                'score': Illuminat.score_final
            }
            Illuminat.users_ref.update(scoreinfo)

    def check_text_q2(self):
        q2_science_fundamental_ans = self.q2_science_fundamental_ans.text
        if q2_science_fundamental_ans == 'mitochondria' or q2_science_fundamental_ans == 'Mitochondria':
            Illuminat.question_score_science_poor += 1

    def check_text_q3(self):
        pass

    def check_text_q4(self):
        pass

    def check_text_q5(self):
        pass

    def marks_fundamental_9science(self):
        print(Illuminat.finalquestion_score)
        return str(Illuminat.finalquestion_score)

    """def get_audio_duration(self):
        audio = AudioSegment.from_file(self.mastervariablemp3updated)
        duration_in_seconds = len(audio) / 1000.0  # Convert milliseconds to seconds
        self.audiodurationn = duration_in_seconds"""

    """def get_audio_duration(self):
        audio_data, sample_rate = librosa.load(self.mastervariablemp3updated)
        self.audiodurationn = librosa.get_duration(y=audio_data, sr=sample_rate)
        duration = self.audiodurationn
        print(duration)
        print(self.audiodurationn)"""

    def get_audio_duration(self):
        if os.path.exists(self.mastervariablemp3updated):
            with wave.open(self.mastervariablemp3updated, 'rb') as wf:
                nFrames = wf.getnframes()
                frameRate = wf.getframerate()
                durationnnnnn = nFrames / frameRate
                self.audiodurationn = durationnnnnn
        else:
            print(f"Error: File {self.mastervariablemp3updated} not found.")

    def play_audio(self, instance):
        # Load and play the audio file
        self.sound = SoundLoader.load(self.audio_file_path)
        if self.sound:
            self.sound.play()

    def pause_audio(self, instance):
        # Pause the audio playback
        if hasattr(self, 'sound') and self.sound:
            self.sound.stop()

    """def convert_to_speech(self):
        print("here kid")
        try:
            with open(self.mastervariabletxtupdated, 'r') as file:
                lines = file.readlines()
                print(lines)

            # Join the lines into a single string
            text_to_convert = ' '.join(lines)

            langgg = ""
            if self.stored_lang == "English":
                langgg = "en"
            elif self.stored_lang == "Hindi":
                langgg = "hi"
                translator = Translator()
                translated_text = translator.translate(text_to_convert, src="en", dest="hi").text
                text_to_convert = translated_text
                print(text_to_convert)
            elif self.stored_lang == "Tamil":
                langgg = "ta"
                translator = Translator()
                translated_text = translator.translate(text_to_convert, src="en", dest="hi").text
                text_to_convert = translated_text

            selected_language = langgg

            if text_to_convert and selected_language:
                tts = gTTS(text=text_to_convert, lang=selected_language)
                tts.save(self.mastervariablemp3updated)
                print(self.mastervariablemp3updated + "saved")
                # Optional: Convert speech to video
                video_clip = VideoFileClip(self.mastervariablemp3updated).set_duration(91)
                video_clip.write_videofile(self.mastervariablemp4, fps=24, remove_temp=True, codec="libx264", audio_codec="aac")
                print("Conversion done")
        except Exception as e:
            print(f"Error in convert_to_speech: {e}")"""

    """def convert_to_speech(self, langgggg):
        print("here kid")
        try:
            with open(self.mastervariabletxtupdated, 'r') as file:
                lines = file.readlines()
                print(lines)

            # Join the lines into a single string
            text_to_convert = ' '.join(lines)
            if langgggg == "English":
                langSelected = "en"
            elif langgggg == "Hindi":
                langSelected = "hi"
            elif langgggg == "Tamil":
                langSelected = "ta"
            print("Here")

            translator = Translator()
            print("Here")

            translated_text = translator.translate(text_to_convert, src="en", dest=langSelected).text
            print("Here")
            text_to_convert = translated_text
            print("Here")

            print(text_to_convert)
            print("Here")


            langgg = ""
            if self.stored_lang == "English":
                langgg = "en"
            elif self.stored_lang == "Hindi":
                langgg = "hi"
                translator = Translator()
                translated_text = translator.translate(text_to_convert, src="en", dest="hi").text
                text_to_convert = translated_text
                print(text_to_convert)
            elif self.stored_lang == "Tamil":
                langgg = "ta"
                translator = Translator()
                translated_text = translator.translate(text_to_convert, src="en", dest="ta").text
                text_to_convert = translated_text

            selected_language = langSelected

            if text_to_convert and selected_language:
                tts = gTTS(text=text_to_convert, lang=selected_language)
                tts.save(self.mastervariablemp3updated)
                print(self.mastervariablemp3updated + " saved")
                # Optional: Convert speech to video
                video_clip = VideoFileClip(self.mastervariablemp3updated).set_duration(91)
                video_clip.write_videofile(self.mastervariablemp4, fps=24, remove_temp=True, codec="libx264", audio_codec="aac")
                print("Conversion done")
        except Exception as e:
            print(f"Error in convert_to_speech: {e}")"""

    def convert_to_speech(self):
        print("here kid")
        try:
            with open(self.mastervariabletxtupdated, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                text_to_convert = ' '.join(lines)
                print("Text to Convert:", text_to_convert)

            if self.stored_lang == "English":
                lang_selected = "en"
            elif self.stored_lang == "Hindi":
                lang_selected = "hi"

            elif self.stored_lang == "Tamil":
                lang_selected = "ta"
            else:
                print("Unsupported language")
                return

            selected_language = lang_selected

            if text_to_convert and selected_language:
                chunk_size = 500  # Adjust the chunk size based on API limits
                chunks = [text_to_convert[i:i + chunk_size] for i in range(0, len(text_to_convert), chunk_size)]

                translated_chunks = []

                for chunk in chunks:
                    try:
                        translation = self.aztranslate_text(chunk, selected_language)
                        translated_chunks.append(translation)
                        print(translation)
                        print("First in race i believe")
                    except Exception as translation_error:
                        print(f"Error during translation: {translation_error}")

                translated_text = ' '.join(translated_chunks)
                print("Translated Text:", translated_text)
                print("Done till here for aztranslatetext")
                if translated_text.strip():
                    snKey = "e9758a33cb1e44bfb26e3bdf45fb265d"
                    region = "centralindia"
                    print("Before calling aztts")
                    print(translated_text)

                    # Update the directory path
                    currentDir = os.getcwd()
                    print(currentDir)
                    output_filename = self.mastervariablemp3updated
                    patherrrr = os.path.join(currentDir, output_filename)
                    if self.stored_lang == "English":
                        langfortts = "en-US"
                    elif self.stored_lang == "Hindi":
                        langfortts = "hi-IN"
                    elif self.stored_lang == "Tamil":
                        langfortts = "ta-IN"

                    print("CRtDir:", currentDir)
                    print("Final Output Path:", patherrrr)

                    self.aztts(snKey=snKey, rGn=region, tts=translated_text, output_file=patherrrr,
                               langfortts=langfortts)
                    print("Done till here for tts")
                else:
                    print("No text to speak")

        except Exception as e:
            print(f"Error in convert_to_speech: {e}")

    def aztranslate_text(self, text, to_lang):
        sKey = '2d16e20f9dd94d9f95e69744a9370bb8'
        ePoint = 'https://api.cognitive.microsofttranslator.com/'
        path = '/translate?api-version=3.0'
        param = f'&to={to_lang}'
        url = ePoint + path + param

        headers = {
            'Ocp-Apim-Subscription-Key': sKey,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        body = [{
            'text': text
        }]

        response = requests.post(url, headers=headers, json=body)
        translated_text = response.json()[0]['translations'][0]['text']
        print("TranslateTxtWorking")
        self.newtext = translated_text
        self.qTxtupdated = translated_text
        self.paraTxtupdated = translated_text
        self.finfeed = translated_text
        return translated_text

    def aztts(self, snKey, rGn, tts, output_file, langfortts):
        try:
            print("snKey:", snKey)
            print("rGn:", rGn)
            print("tts:", tts)
            print("This is me here")
            print("langfortts", langfortts)

            # Set the appropriate region and subscription key
            speech_config = SpeechConfig(subscription=snKey, region=rGn)

            # Set the language to Hindi
            speech_config.speech_synthesis_language = langfortts

            print("That's one step for man, one giant leap for mankind")

            # Specify the output file directly with the desired format (MP3)
            audio_config = AudioConfig(filename=output_file)

            # Create SpeechSynthesizer with audio config
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            print("woah, this is synthesizer reporting from Earth-616")

            # Synthesize the text
            result = synthesizer.speak_text_async(tts).get()

            print("result done")

            if result.reason == ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesis succeeded.")
                print("Audio file saved as:", output_file)
            else:
                print(f"Speech synthesis failed: {result.reason}")
                if result.reason == ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print(f"CancellationReason: {cancellation_details.reason}")
                    print(f"ErrorDetails: {cancellation_details.error_details}")

        except Exception as e:
            print(f"Error in aztts: {e}")

    def azttsforai(self, tts):
        try:
            snKey = "e9758a33cb1e44bfb26e3bdf45fb265d"
            region = "centralindia"
            print("snKey:", snKey)
            print("rGn:", region)
            print("tts:", tts)
            currentDir = os.getcwd()
            print(currentDir)
            output_filename = "clairtybot.mp3"
            patherrrr = os.path.join(currentDir, output_filename)
            print("This is me here")
            langfortts = self.stored_lang
            if langfortts == "English":
                langfortts = "en-US"
            elif langfortts == "Hindi":
                langfortts = "hi-IN"
            elif langfortts == "Tamil":
                langfortts = "ta-IN"
            print(langfortts)
            speech_config = SpeechConfig(subscription=snKey, region=region)

            speech_config.speech_synthesis_language = langfortts

            print("That's one step for man, one giant leap for mankind")

            audio_config = AudioConfig(filename=patherrrr)

            # Create SpeechSynthesizer with audio config
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            print("woah, this is synthesizer reporting from Earth-616")

            # Synthesize the text
            result = synthesizer.speak_text_async(tts).get()

            print("result done")

            if result.reason == ResultReason.SynthesizingAudioCompleted:
                print("Speech synthesis succeeded.")
                print("Audio file saved as:", patherrrr)
            else:
                print(f"Speech synthesis failed: {result.reason}")
                if result.reason == ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print(f"CancellationReason: {cancellation_details.reason}")
                    print(f"ErrorDetails: {cancellation_details.error_details}")

        except Exception as e:
            print(f"Error in aztts: {e}")
        audio = SoundLoader.load('clairtybot.mp3')
        audio.play()


    def changevolumeofvideo(self):
        vidPlay = self.root.get_screen('varscript').ids.video_player
        vidPlay.state = 'stop'
    def checkans(self):
        aHere = self.root.get_screen('questionsscreen').ids.ansHere
        print(f"questionnbefore: {self.questionnumber}")

        # self.newscore += 1
        print("Reached till here")
        # if aHere.text in ['"nucleus",’Nucleus', 'prokaryotic’,’Prokaryotic', 'chlorophyll’,’Chlorophyll', 'mitochondria’,’Mitochondria', 'cell’,’Cell', 'condensation’,’Condensation', 'solid’,’Solid', 'atom’,’Atom’,’Atoms’,’atoms', 'evaporation’,’Evaporation', 'temperature’,’Temperature', 'education’,’Education', 'Population’,’population', 'disguised’,’Disguised', 'primary’,’Primary', 'human’,’Human', 'global warming’,’Global Warming’,’GlobalWarming’,’globalwarming', 'climate change’,’Climate Change’,’ClimateChange’,’climatechange', 'greenhouse effect’,’Greenhouse Effect’,’GreenhouseEffect’,’greenhouseeffect', 'humidity’,’Humidity', 'climate’,’Climate', 'program’,’Program', 'cookie’,’Cookie', 'hardware’,’Hardware', 'encryption’,’Encryption', 'internet’,’Internet', 'nucleus’,’Nucleus', 'ribosomes’,’Ribosomes’,’Ribosome’,’ribosome', 'cell wall’,’Cell Wall’,’cellwall’,’CellWall', 'vacuole’,’Vacuole', 'Chlorophyll', 'muscle’,’Muscle', 'xylem’,’Xylem', 'epidermis’,’Epidermis', 'ligament’,’Ligament', 'tissue’,’Tissue’,’Tissues’,’tissues', 'volume’,’Volume', 'element’,’Element', 'gas’,’Gas', 'bond’,’Bond', 'sublimation’,’Sublimation', 'developement’,’Developement', 'education’,’Education', 'population’,’Population', 'human capital’,’Human Capital’,’HumanCapital''humancapital', 'gdp’,’GDP', 'democracy’,’Democracy', 'parliament’,’Parliament', 'federalism’,’Federalism', 'election commission’,’Election Commission’,’ElectionCommission’,’electioncommission', 'constitution’,’Constitution', 'democracy’,’Democracy', 'parliament’,’Parliament', 'federalism’,’Federalism', 'election commission’,’Election Commission’,’ElectionCommission’,’electioncommission', 'constitution’,’Constitution', 'icon’,’Icon', 'mouse’,’Mouse', 'software’,’Software', 'website’,’Website', 'motherboard’,’Motherboard', 'cyber security’,’Cyber Security’,’CyberSecurity’,’cybersecurity', 'hacking’,’Hacking', 'antivirus’,’Antivirus', 'phishing’,’Phishing', 'encryption’,’Encryption', 'cytoplasm’,’Cytoplasm', 'endoplasmic reticulum’,’Endoplasmic Reticulum’,’EndoplasmicReticulum’,’endoplasmicreticulum', 'lysosome’,’Lysosome', 'phagocytosis’,’Phagocytosis', 'nucleolus’,’Nucleolus', 'sublimation’,’Sublimation', 'mole’,’Mole', 'heterogeneous’,’Heterogeneous', 'solubility’,’Solubility', 'activation energy’,’Activation Energy’,’ActivationEnergy’,’activationenergy', 'nerve’,’Nerve', 'parenchyma’,’Parenchyma', 'connective’,’Connective', 'epithelium’,’Epithelium', 'muscle’,’Muscle', 'human capital’,’Human Capital’,’HumanCapital’,’humancapital’,’Human capital’,’Humancapital', 'non market activity’,’Non-market activity’,’Nonmarket activity’,’non-market activity’,’Non-Market Activity’,’Non-market Activity’,’Non Market activity', 'secondary sector’,’Secondary sector’,’Secondary Sector’,’Secondarysector’,’SecondarySector’,’secondarysector', '74%’,’74.04%', '3’,’three''Three', 'mediterranean sea’,’Mediterranean Sea’,’Mediterranean sea’,’MediterraneanSea’,’Mediterraneansea’,’mediterraneansea', 'Khasi Hills’,’Khasi hills’,’khasi hills’,’KhasiHills’,’Khasihills’,’khasihills', 'coriolis force’,’Coriolis force’,’Coriolis Force’,’Coriolisforce’,’coriolisforce’,’CoriolisForce', 'monsoon winds’,’Monsoon Winds’,’MonsoonWinds’,’Monsoonwinds’,’monsoonwinds’,’Monsoonwinds', 'kaal baisakhi’,’Kaal Baisakhi’,’KaalBaisakhi’,’Kaalbaisakhi''kaalbaisakhi''Kaal baisakhi', 'parliament’,’Parliament', '30 years’,’30’,’30yrs’,’thirty years’,’Thirty years’,’30 years', 'Chief Minister’,’ChiefMinister’,’chief minister’,’ChiefMinister’,’Chiefminister’,’chiefminister', 'Prime Minister’,’PrimeMinister’,’Prime minister’,’prime minister’,’Primeminister’,’primeminister', 'rajya sabha’,’Rajya Sabha’,’Rajya sabha’,’RajyaSabha''Rajyasabha''rajyasabha', 'microprocessors’,’Microprocessors’,’Micro processors’,’micro processors', 'Charles Babbage’,’Charles babbage’,’charles babbage’,’CharlesBabbage’,’Charlesbabbage’,’charlesbabbage', 'loom’,’Loom', 'microphone’,’Microphone', 'byte’,’Byte', 'Steganography’,’steganography', 'Spam’,’spam', 'phreaking’,’Phreaking', 'antivirus’,’Antivirus', 'mitm’,’MITM’,’Mitm’,’M.i.t.m.’,’M.I.T.M’,’M.i.t.m.', 'home’,’Home', 'cell’,’Cell', 'Formatting’,’formatting', 'vertically’,’Vertically', 'Page break’,’Page Break’,’page break’,’Pagebreak’,’PageBreak’,’pagebreak', 'aluminium’,’Aluminium', 'galvanisation’,’Galvanisation', 'sonority’,’Sonority', 'amalgam’,’Amalgam', 'metallurgy’,’Metallurgy', 'density’,’Density', 'reduction’,’Reduction', 'negative’,’Negative', 'tartaric’,’Tartaric', 'water’,’Water', 'effector’,’Effector', 'stimulus’,’Stimulus', 'cytokinin’,’Cytokinin', 'phototropism’,’Phototropism', 'hydrotropism’,’Hydrotropism', 'axon’,’Axon', 'pituitary gland’,’Pituitary gland’,’Pituitary Gland’,’Pituitarygland’,’PituitaryGland’,’pituitarygland', 'muscle’,’Muscle', 'synapse’,’Synapse', 'brain’,’Brain', 'cerebellum’,’Cerebellum', 'pancreas’,’Pancreas', 'insulin’,’Insulin', 'hormones’,’Hormones', 'growth’,’Growth', 'length’,’Length', 'resistance’,’Resistance', 'volt’,’Volt', 'ammeter’,’Ammeter', 'ampere’,’Ampere', 'energy’,’Energy', 'conductors’,’Conductors', 'rheostat’,’Rheostat', 'voltmeter’,’Voltmeter', 'wattage’,’Wattage', 'anthracite’,’Anthracite', 'silicon’,’Silicon', 'kinetic’,’Kinetic', 'sun’,’Sun', 'potential’,’Potential', 'wireless’,’Wireless', 'ping’,’Ping', 'encrypted’,’Encrypted', 'router’,’Router', 'hostname’,’Hostname', 'information’,’Information', 'processor’,’Processor', 'propagation’,’Propagation', 'mesh’,’Mesh', 'server’,’Server', 'packets’,’Packets', 'hyperlink’,’Hyperlink', 'website’,’Website', 'hypertext’,’Hypertext', 'newsgroup’,’Newsgroup', 'proprietary’,’Proprietary', 'citation’,’Citation', 'malware’,’Malware', 'privacy’,’Privacy', 'impersonation’,’Impersonation', 'netiquettes’,’Netiquettes', 'encryption’,’Encryption', 'security’,’Security', 'patent’,’Patent', 'freeware’,’Freeware', 'container’,’Container', 'predefined’,’Predefined', 'angular’,’Angular', 'notepad’,’Notepad', 'body’,’Body', 'mahanadi’,’Mahanadi', 'tamil nadu’,’Tamil Nadu’,’Tamil nadu’,’TamilNadu’,’Tamilnadu’,’tamilnadu', 'meghalaya’,’Meghalaya', 'ganga’,’Ganga', 'ground’,’Ground', 'desalination’,’Desalination', 'damodar valley’,’Damodar Valley’,’Damodar valley’,’DamodarValley’,’Damodarvalley’,’damodarvalley', 'shillong’,’Shillong', 'gendathur’,’Gendathur', 'tankas’,’Tankas', 'krishna’,’Krishna', 'sutlej’,’Sutlej', 'himalayas’,’Himalayas', 'rajasthan’,’Rajasthan', 'hydroelectric’,’Hydroelectric', 'consumer exploitation’,’Consumer Exploitation’,’Consumer exploitation’,’Exploitation’,’exploitation’,’ConsumerExploitation’,’Consumerexploitation’,’consumerexploitation', 'adulteration’,’Adulteration', 'consumer courts’,’Consumer Courts’,’Consumer courts’,’ConsumerCourts’,’Consumercourts’,’consumercourts', 'hallmark’,’Hallmark’,’Hall mark’,’hall mark’,’Hall Mark', 'agmark’,’Agmark’,’AgMark’,’A-Mark' , 'quality’,’Quality', 'BIS’,’BIS', 'consumer court’,’Consumer Court’,’Consumer court’,’ConsumerCourt’,’Consumercourt’,’consumercourt', 'december’,’December', 'producers’,’Producers’,’producer’,’Producer', 'illiteracy’,’Illiteracy', 'district’,’District', 'ncdrc’,’NCDRC', 'consumer’,’Consumer', 'high’,’High', 'credit score’,’Credit score’,’Credit Score’,’creditscore’,’Creditscore’,’CreditScore', 'barter’,’Barter', 'collateral’,’Collateral', 'currency’,’Currency', 'moneylenders’,’Moneylenders’,’Money lenders’,’Money Lenders’,’money lenders', 'commerical banks’,’Commercial Banks’,’Commercial banks’,’Commercial bank’,’commercial bank’,’Commercial Bank’,’Commercial’,’commercial', 'creditor’,’Creditor', 'depositors’,’Depositors’,’Depositor’,’depositor', 'formal’,’Formal', 'credit’,’Credit', 'alluvial’,’Alluvial', 'sustainable’,’Sustainable', 'regur’,’Regur', 'laterite’,’Laterite', 'contour’,’Contour', 'warehousing’,’Warehousing', 'profession’,’Profession', 'tertiary’,’Tertiary', 'entreport’,’Entreport', 'industry’,’Industry', 'profit’,’Profit', 'human’,’Human', 'business’,’Business', 'profession’,’Profession', 'auxiliaries’,’Auxiliaries', 'employment’,’Employment', 'secondary’,’Secondary', 'busy’,’Busy', 'employment’,’Employment', 'analytical’,’Analytical', 'insurance’,’Insurance', 'multipurpose’,’Multipurpose’,’Multi-purpose’,’multi-purpose', 'social’,’Social', 'cooperative’,’Cooperative’,’Co-operative’,’co-operative', 'specialized’,’Specialized’,’Specialised’,’specialised', 'central’,’Central', 'bearer’,’Bearer', 'policy’,’Policy', 'premium’,’Premium', 'communication’,’Communication', 'broker’,’Broker', 'chain’,’Chain', 'departmental’,’Departmental', 'street’,’Street', 'peddlers’,’Peddlers’,’Peddler’,’peddler', 'insurer’,’Insurer', 'consolidation’,’Consolidation', 'private’,’Private', 'annuity’,’Annuity', 'mitigation’,’Mitigation', 'itinerant’,’Itinerant', 'wholesaler’,’Wholesaler', 'large’,’Large', 'location’,’Location', 'trade’,’Trade', 'performa’,’Performa', 'import’,’Import', 'invisible’,’Invisible', 'current’,’Current', 'adam smith’,’Adam Smith’,’Adam smith’,’AdamSmith’,’Adamsmith’,’adamsmith', 'union’,’Union', 'savasana’,’Savasana', 'purushav’,’Purushav', 'padmasana’,’Padmasana', 'forest’,’Forest', 'brahmi’,’Brahmi', 'krishnamacharya’,’Krishnamacharya', 'india’,’India', 'vajrasana’,’Vajrasana', 'raja’,’Raja', 'patanjali’,’Patanjali', 'enlightenment’,’Enlightenment', 'dhyana’,’Dhyana', 'pratyahara’,’Pratyahara', 'neti’,’Neti', 'instrumental’,’Instrumental', 'psychology’,’Psychology', 'experimental’,’Experimental', 'emotion’,’Emotion', 'mental’,’Mental', 'behaviour’,’Behaviour', 'drive’,’Drive', 'movere’,’Movere', 'subjective’,’Subjective', 'biological’,’Biological', 'endurance’,’Endurance', 'flexibility’,’Flexibility', 'diseases’,’Diseases’,’Disease’,’disease', 'hydrostatic’,’Hydrostatic', 'physical’,’Physical', 'false’,’False', 'displacement’,’Displacement', 'periodic’,’Periodic’,’Constant’,’constant', 'maximum’,’Maximum', 'friction’,’Friction', 'amplitude’,’Amplitude', 'forced’,’Forced', 'greatest’,’Greatest', 'maximum’,’Maximum', 'periodic’,’Periodic', 'period’,’Period', 'frequency’,’Frequency', 'resonance’,’Resonance', 'displacement’,’Displacement', 'rad’,’Rad', 'kinetic’,’Kinetic', 'thermal’,’Thermal', 'isothermal’,’Isothermal', 'moving’,’Moving', 'molecules’,’Molecules’,’Molecule’,’molecule', 'absolute’,’Absolute', 'temperature’,’Temperature', 'density’,’Density', 'increases’,’Increases’,’Increase’,’increase', 'momentum’,’Momentum', 'molecules’,’Molecules’,’Molecule’,’molecule', 'true’,’True', 'ideal’,’Ideal', 'monoatomic’,’Monoatomic’,’mono atomic’,’Mono atomic’,’Mono Atomic', 'rigid’,’Rigid', 'gravitation’,’Gravitation’,’Molecule’,’molecule', 'false’,’False', 'orbit’,’Orbit', 'perigee’,’Perigee', 'mass’,’Mass', 'apogee’,’Apogee', 'planetary’,’Planetary', 'equator’,’Equator', 'rotation’,’Rotation', 'true’,’True', 'entropy’,’Entropy', 'exergy’,’Exergy', 'enthalpy’,’Enthalpy', 'particles’,’Particles’,’Particle’,’particle', 'entropy’,’Entropy', 'mollusca’,’Mollusca', 'nephridia’,’Nephridia', 'jointed’,’Jointed', 'Echinodermata’,’echinodermata', 'platyhelminthes’,’Platyhelminthes', 'aristotle’,’Aristotle', 'biodiversity’,’Biodiversity', 'unicellular’,’Unicellular', 'thallophyte’,’Thallophyte', 'aves’,’Aves', 'agnatha’,’Agnatha', 'parasitic’,’Parasitic', 'herbarium’,’Herbarium', 'false’,’False', 'taxonomic’,’Taxonomic', 'glycine’,’Glycine', 'desmosomes’,’Desmosomes', 'endomitosis’,’Endomitosis', 'nucleolus’,’Nucleolus', 'mitoplast’,’Mitoplast', 'active’,’Active', 'histone’,’Histone', 'centrioles’,’Centrioles', 'true’,’True', 'cytoplasm’,’Cytoplasm', 'asymmetrical’,’Asymmetrical', 'mitochondria’,’Mitochondria', 'protoplast’,’Protoplast', 'cellulose’,’Cellulose', 'actin’,’Actin', 'imbibition’,’Imbibition', 'collagen’,’Collagen', 'diffusion’,’Diffusion', 'hypotonic’,’Hypotonic', 'chloroplasts’,’Chloroplasts’,’Chloroplast’,’chloroplast', 'suberin’,’Suberin', 'collenchyma’,’Collenchyma', 'secondary’,’Secondary', 'false’,’False', 'vessel’,’Vessel', 'macrophages’,’Macrophages', 'merocrine’,’Merocrine', 'connective’,’Connective', 'basophils’,’Basophils', 'glial’,’Glial', 'aniline’,’Aniline', 'ammonia’,’Ammonia', 'pyramidial’,’Pyramidial', 'true’,’True', 'false’,’False', 'false’,’False', 'alcoholic’,’Alcoholic', 'false’,’False', 'methyl’,’Methyl', 'nucleophilic’,’Nucleophilic', 'primary’,’Primary', 'fishy’,’Fishy', 'basic’,’Basic', 'white’,’White', 'nitrogen’,’Nitrogen', 'true’,’True', 'brass’,’Brass', 'false’,’False', 'solid sol’,’Solid Sol’,’Solid sol’,’Solidsol’,’SolidSol’,’solidsol', 'solid foam’,’Solid Foam’,’Solid foam’,’Solidfoam’,’SolidFoam’,’solidfoam', 'saturated’,’Saturated’,’Saturated solution’,’Saturated Solution’,’saturated solution’,’Saturatedsolution’,’SaturatedSolution’,’saturatedsolution', 'molality’,’Molality', 'solubility’,’Solubility', 'true’,’True', '1’,’one’,’One', 'element’,’Element', 'polar’,’Polar', 'true’,’True', 'boiling’,’Boiling', 'true’,’True', 'thymine’,’Thymine', 'trisaccharide’,’Trisaccharide', 'true’,’True', 'anomers’,’Anomers’,’Anomer’,’anomer', 'true’,’True', 'serine’,’Serine', 'true’,’True', 'invert’,’Invert', 'laevulose’,’Laevulose', 'true’,’True', 'false’,’False', 'hydrogen’,’Hydrogen', 'false’,’False', 'galvanic’,’Galvanic', 'william grove’,’William Grove’,’William grove’,’WilliamGrove’,’Williamgrove’,’williamgrove', 'math’,’Math', '4’,’four’,’Four', 'syntax’,’Syntax', 'exception’,’Exception', 'raised’,’Raised', 'try’,’Try', 'true’,’True', 'binary’,’Binary', 'text’,’Text', 'mutability’,’Mutability', 'explicit’,’Explicit', 'caller’,’Caller', 'pickle’,’Pickle', 'local’,’Local', 'load’,’Load', 'firewall’,’Firewall', 'wan’,’WAN’,’Wan', 'repeater’,’Repeater', 'switch’,’Switch', 'channel’,’Channel', 'hertz’,’Hertz', 'wireless’,’Wireless', 'bridge’,’Bridge', 'trojan’,’Trojan', 'router’,’Router', 'application’,’Application', 'foreign’,’Foreign', 'relational’,’Relational', 'false’,’False', 'raw’,’Raw', 'application’,’Application']:
        if aHere.text in ["cell"]:
            print("Good Morning")
            self.newscore += 1
            print(f"Scoree: {self.newscore}")
            aHere.text = ""

        print(f"Score: {self.newscore}")

        aHere.text = ""

        if self.questionnumber == 5:
            screenManager = ScreenManager()
            self.screen_manager.add_widget(Builder.load_file("scorescreen.kv"))
            self.screen_manager.current = 'scorescreen'
            print(f"EndScore: {self.newscore}")
            Illuminat.finalScoree = int(self.newscore)
            # self.questionnumber = 0

        self.questionnumber += 1
        print(f"questionnafter: {self.questionnumber}")

        """if self.questionnumber == 5 or self.questionnumber == 6:
            self.questionnumber = 0"""

    def scorescreenclick(self):
        score = float(self.stored_score)
        if 0 <= score <= 3:
            self.screen_manager.current = 'prevarscriptpoor'
        elif 4 <= score <= 6:
            self.screen_manager.current = 'prevarscriptavg'
        elif 7 <= score <= 10:
            self.screen_manager.current = 'prevarscripttop'

    def getfeedback(self):
        finFeed = self.root.get_screen('scorescreen').ids.finalfeedback
        if 0 <= self.newscore <= 2:
            finFeed.text = "Well done! With little efforts and hard work, you can achieve higher goals!"
        elif 3 <= self.newscore <= 4:
            finFeed.text = "Superb! Your consistent efforts have paid off.You must continue with your sincere efforts and aim higher"
        elif self.newscore == 5:
            finFeed.text = "Excellent! Your performance is praise worthy. Keep it up!"
            finFeed.font_name = "notosanstamil.ttf"
        langg = self.stored_lang
        if langg == "English":
            pass
        elif langg == "Hindi":
            self.aztranslate_text(finFeed.text, "hi")
            finFeed.text = self.finfeed

        elif langg == "Tamil":
            self.aztranslate_text(finFeed.text, "ta")
            finFeed.text = self.finfeed

    def reducequestiontoone(self):
        self.questionnumber = 1

    def convertText(self):
        langg = self.stored_lang
        qTxt = self.root.get_screen('questionsscreen').ids.questiontxt

        if langg == "English":
            pass
        elif langg == "Hindi":
            self.aztranslate_text(qTxt.text, "hi")
            qTxt.text = self.qTxtupdated

        elif langg == "Tamil":
            self.aztranslate_text(qTxt.text, "ta")
            qTxt.text = self.qTxtupdated

    def convertTextpara(self):
        langg = self.stored_lang
        paraTxt = self.root.get_screen('varscript').ids.paraTxt
        if langg == "English":
            pass
        elif langg == "Hindi":
            self.aztranslate_text(paraTxt.text, "hi")
            paraTxt.text = self.paraTxtupdated

        elif langg == "Tamil":
            self.aztranslate_text(paraTxt.text, "ta")
            paraTxt.text = self.paraTxtupdated
    def changetonototamil(self):
        storedLang = self.stored_lang
        if storedLang == "Tamil":
            for kv_file in ['clairtybot.kv', 'beforequestions.kv', 'beforequestionsscreen.kv', 'home.kv', 'homecopy.kv', 'login.kv', 'main.kv', 'prevarscriptavg.kv', 'prevarscriptpoor.kv', 'prevarscripttop.kv', 'profile.kv', 'question2.kv', 'question3.kv', 'question4.kv', 'question5.kv', 'question6.kv', 'question7.kv', 'question8.kv', 'question9.kv', 'question10.kv', 'questions.kv', 'questionscopy.kv', 'questionsolder.kv', 'questionsscreen.kv', 'signup.kv', 'signupdetails.kv', 'varscript.kv', 'varscriptquestions.kv', 'videoplaycode.kv']:
                with open(kv_file, encoding='utf-8') as f:
                    Builder.load_string(f.read().replace('notosans', 'notosanstamil'))
    def gettextpara(self):
        print("gettextpara")
        print(f"Current Screen: {self.root.current_screen.name}")
        print(f"IDs on Current Screen: {self.root.current_screen.ids}")
        paraTxt = self.root.get_screen('varscript').ids.paraTxt
        lang = self.stored_lang
        age = self.stored_age
        preScore = int(self.stored_score)
        chapterr = self.chapter_name
        subject = int(self.subjectClicked)

        print(age)
        print(preScore)
        print(f"chapter: {chapterr}")
        #print(f"questionn: {questionn}")
        print(subject)
        if age == "13":
            print("First")
            print(f"prescore: {preScore}")
            if 0 <= preScore <= 3:
                print("Second")
                print(f"sub: {subject}")
                if subject == 1:
                    print("Third")
                    if chapterr == "FUL":
                        print("Fourth")
                        paraTxt.text = "The cell, life's Lego brick, holds the key! It carries instructions (DNA) in its brain (nucleus) and performs tasks (functions) in its factories (organelles). From single-celled amoebas to complex humans, all living things are built one cell at a time!"

                    elif chapterr == "MAT":
                        paraTxt.text = "Everything you see, touch, or smell? That's matter! It comes in solid, liquid, or gas forms, made of tiny building blocks called atoms. Pure substances like gold have only one type of atom, while mixtures like air have many. Heat and pressure can transform these states, like ice melting to water. Remember, physical changes don't alter the basic stuff, but chemical changes create entirely new things! Dive deeper and unveil the wonders of our material world!"

                elif subject == 2:
                    if chapterr == "NET":
                        paraTxt.text = "Computer networking involves the interconnection of multiple computers or devices to share resources, information, and services. This interconnected system enables communication through the exchange of data, facilitated by various networking components like routers, switches, and protocols. It forms the backbone of the internet, connecting people, businesses, and devices worldwide for seamless information exchange."

                    elif chapterr == "SEC":
                        paraTxt.text = "Cybersecurity involves the protection of computer systems, networks, and data from potential cyber threats, including unauthorized access, attacks, and data breaches. It employs a combination of technologies, processes, and practices to ensure the confidentiality, integrity, and availability of digital information, safeguarding against cybercrime and unauthorized access. Continuous monitoring, encryption, and robust authentication measures are crucial components of effective cybersecurity strategies."

                elif subject == 3:
                    if chapterr == "PPL":
                        paraTxt.text = "People as Resource is a concept acknowledging the population as an asset rather than a liability. It recognizes that the human population, when provided with education, skills, and health, becomes a valuable resource contributing to economic growth. By investing in human capital, societies can harness the potential of individuals to drive innovation, productivity, and sustainable development, emphasizing the importance of education and healthcare in empowering people as valuable assets."
                        print("We are here")
                    elif chapterr == "CLI":
                        paraTxt.text = "Climate isn't just today's sunshine or yesterday's rain. It's the average weather pattern over a long period (30+ years) in a specific area. Think of it as the region's personality, shaped by factors like temperature, precipitation, winds, latitude and altitude. Remember, climate has a huge impact on life, shaping ecosystems, agriculture, and even our lifestyles!"


            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "FUL":
                        paraTxt.text = "Cells, the mini marvels of life, hold the blueprint (DNA) and factories (organelles) to power growth, energy, and even thought! From a single-celled speck to a roaring lion, it all starts with these fundamental units."
                    elif chapterr == "MAT":
                        paraTxt.text = "Heat and pressure can change matter's state. Think of it like changing costumes! Ice melts to water (solid to liquid), water boils to steam (liquid to gas), and steam condenses to water droplets (gas to liquid). Remember, these changes are physical, not chemical, meaning the basic matter stays the same, just in a different form. It's a fascinating world of transformation!"

                    elif chapterr == "TIS":
                        paraTxt.text = "Imagine cells joining forces! In plants, three tissue types rule: builders (parenchyma, collenchyma, sclerenchyma) for support and storage, transporters (xylem, phloem) for water and food movement, and protectors (epidermis) like the plant's skin. Teamwork makes the plant dream work!"

                elif subject == 2:
                    if chapterr == "NET":
                        paraTxt.text = "Computer networking is the practice of linking computers and other devices to enable communication and resource sharing. It encompasses both local area networks (LANs) within a confined space and wide area networks (WANs) that connect devices over longer distances."

                    elif chapterr == "SEC":
                        paraTxt.text = "Focused on maintaining the confidentiality and integrity of digital assets, cybersecurity employs technologies and protocols to defend against cyber threats. It involves proactive measures such as regular updates, awareness training, and advanced security solutions to mitigate risks in the ever-evolving digital landscape."

                    elif chapterr == "OFF":
                        paraTxt.text = "Office tools refer to a set of software applications designed to enhance productivity and streamline tasks in a professional or business setting. These tools often include word processing software for document creation, spreadsheet applications for data analysis, presentation software for effective communication, and other collaborative tools like email and calendar applications. They aim to facilitate efficient workflow management, communication, and data organization within an office environment."

                elif subject == 3:
                    if chapterr == "PPL":
                        paraTxt.text = "People as Resource underscores the idea that the population, when educated and healthy, transforms into a valuable resource for a nation's development. It emphasizes investments in education and healthcare to enhance human capital, fostering innovation, productivity, and overall societal well-being."

                    elif chapterr == "CLI":
                        paraTxt.text = "Climate refers to the long-term patterns of temperature, humidity, wind, and precipitation in a particular region. It is distinct from weather, which represents short-term atmospheric conditions. Climate influences the overall environmental conditions and ecosystems, playing a crucial role in shaping the characteristics of a geographical area over an extended period."

                    elif chapterr == "WOR":
                        paraTxt.text = "Imagine a complex symphony - that's how institutions work! Each instrument (ministries, courts, etc.) plays a specific role, following rules (constitution, laws) to achieve harmony in society.Remember, just like a symphony takes practice, institutions function best when everyone works together!"

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "FUL":
                        paraTxt.text = "From the simplest bacteria to the tallest trees, all living things share a common thread - the cell. Though they come in different shapes and sizes, each cell carries the spark of life and performs essential functions, making them the basic building blocks of the incredible diversity we see on Earth."

                    elif chapterr == "MAT":
                        paraTxt.text = "Not all matter is the same. Pure substances, like gold, have only one type of tiny building block called an atom. Think of it as a solo act on stage. Mixtures, like air (nitrogen and oxygen), combine different atoms. Picture a group performance, each type of atom playing its part."

                    elif chapterr == "TIS":
                        paraTxt.text = "Animals boast four tissue teams: cover girls (epithelial) line surfaces and organs, movers and shakers (muscle) make you move, connectors (connective) support and bind everything, and messengers (nervous) carry messages for thinking and feeling. Each plays a vital role in the animal symphony!"

                    elif chapterr == "ATO":
                        paraTxt.text = "Atoms join hands to form molecules, like complex Lego creations. Water (H2O) has two hydrogen atoms holding hands with one oxygen.Molecules can be simple (like oxygen, O2) or complex (like sugar, C12H22O11). Their arrangement determines their shape and properties, making the world so diverse!"

                elif subject == 2:
                    if chapterr == "NET":
                        paraTxt.text = "In the realm of computer networking, devices are interconnected to facilitate data transfer, communication, and collaborative activities. This interconnectedness occurs through the use of protocols and networking hardware, allowing seamless interaction between computers in a digital ecosystem."

                    elif chapterr == "SEC":
                        paraTxt.text = "Focused on maintaining the confidentiality and integrity of digital assets, cybersecurity employs technologies and protocols to defend against cyber threats. It involves proactive measures such as regular updates, awareness training, and advanced security solutions to mitigate risks in the ever-evolving digital landscape."

                    elif chapterr == "OFF":
                        paraTxt.text = "Office tools refer to a set of software applications designed to enhance productivity and streamline tasks in a professional or business setting. These tools often include word processing software for document creation, spreadsheet applications for data analysis, presentation software for effective communication, and other collaborative tools like email and calendar applications. They aim to facilitate efficient workflow management, communication, and data organization within an office environment."

                elif subject == 3:
                    if chapterr == "PPL":
                        paraTxt.text = "The concept of People as Resource views the population not as a burden but as a reservoir of skills, talents, and creativity. By providing education and healthcare, societies can unlock the immense potential within their citizens, contributing to economic growth and social progress."

                    elif chapterr == "CLI":
                        paraTxt.text = "Climate is the average atmospheric conditions, including temperature and precipitation, observed over an extended period in a specific location. It provides a comprehensive view of the region's weather patterns and influences the flora, fauna, and human activities."

                    elif chapterr == "WOR":
                        paraTxt.text = "Institutions aren't rigid robots following orders. They're like diverse teams, each player (ministries, courts, etc.) with a specific role. Think ministers as captains, bureaucrats as coaches, and citizens as active participants.No bossy kings here! Institutions follow a rulebook, the constitution, like a game's instructions. It ensures everyone plays fair and the system doesn't favor individuals."

                    elif chapterr == "NAT":
                        paraTxt.text = "Imagine a vibrant tapestry woven with animals and plants thriving in their natural homes. That's natural wildlife! It's not just cute pandas or majestic tigers, but an intricate web of life:  From soaring eagles to burrowing insects, wildlife encompasses all living things in their natural habitats. It's like a grand stage teeming with unique actors playing vital roles.Protecting natural wildlife isn't just about saving cute animals, it's about preserving the balance of life on Earth, including us!"

        elif age == 14:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "MET":
                        paraTxt.text = "Metals are elements characterized by conductivity, malleability, and ductility, commonly found on the left side of the periodic table. They generally form positive ions and exhibit metallic bonding. Non-metals, located on the right side of the periodic table, have diverse properties, often lacking metallic characteristics. They form negative ions and display covalent or ionic bonding, and include elements such as hydrogen, oxygen, and nitrogen. The stark contrast between metals and non-metals contributes to their varied applications in technology, industry, and daily life."

                    elif chapterr == "CON":
                        paraTxt.text = "Control and coordination refer to the regulatory mechanisms in living organisms that ensure the harmonious functioning of various physiological processes. In animals, the nervous system uses electrical impulses for rapid responses, while in plants, chemical signals like hormones coordinate growth and development. These intricate systems enable organisms to adapt and maintain internal balance, ensuring efficient responses to external stimuli."

                elif subject == 2:
                    if chapterr == "WAT":
                        paraTxt.text = "Water resources are vital for life on Earth, encompassing freshwater bodies like rivers, lakes, and groundwater. They sustain ecosystems, agriculture, industry, and human consumption. Managing these resources is crucial for sustainability."

                    elif chapterr == "COR":
                        paraTxt.text = "Consumer rights ensure fair treatment and protection for consumers in the marketplace. They include the right to safety, information, choice, and redress. Upholding consumer rights promotes transparency, accountability, and trust between buyers and sellers."

                elif subject == 3:
                    if chapterr == "NE1":
                        paraTxt.text = "Computer networking involves connecting devices to enable communication and resource sharing. This includes understanding different types of networks and common networking devices. Network protocols like TCP/IP facilitate communication, while security measures like authentication and encryption safeguard data."

                    elif chapterr == "ETH":
                        paraTxt.text = "Cyber ethics introduces principles for responsible and ethical behavior online, emphasizing respect for privacy, avoidance of cyberbullying, and awareness of the consequences of cybercrimes. It encourages critical thinking and skepticism towards online content while promoting positive digital citizenship."

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "MET":
                        paraTxt.text = "Metals, situated on the left side of the periodic table, are known for their luster, conductivity, and tendency to lose electrons. They typically form positive ions in chemical reactions. Non-metals, found on the right side, lack these metallic properties and tend to gain electrons, forming negative ions. The distinction between metals and non-metals is fundamental in understanding their roles in chemical bonding and reactivity."

                    elif chapterr == "CON":
                        paraTxt.text = "Control and coordination involve the intricate management of physiological activities within living organisms, ensuring a synchronized response to stimuli. The nervous system, through electrical signals, and the endocrine system, employing chemical messengers, play pivotal roles in maintaining homeostasis."

                    elif chapterr == "ELE":
                        paraTxt.text = "Electricity is a form of energy resulting from the existence of charged particles (such as electrons or protons), either statically as an accumulation of charge or dynamically as a current. It is a versatile energy source powering various devices, lighting, and appliances through the flow of electric charge in conductive materials. The principles of electricity involve voltage, current, and resistance, with electrical circuits providing a pathway for the controlled movement of electrons."

                elif subject == 2:
                    if chapterr == "WAT":
                        paraTxt.text = "Understanding water resources is essential for environmental stewardship and ensuring future generations' well-being.Effective water resource management is key to ensuring a stable and prosperous future for communities worldwide."

                    elif chapterr == "COR":
                        paraTxt.text = "Consumer rights guarantee fair treatment, safety, and transparency for buyers in the marketplace. They encompass the right to information, choice, and to seek redress for grievances. Upholding these rights fosters trust, accountability, and ethical business practices."

                    elif chapterr == "MON":
                        paraTxt.text = "Money and credit explores the roles and functions of money in the economy, as well as the mechanisms of credit. Money serves as a medium of exchange, unit of account, and store of value, facilitating  economic activity. Credit, on the other hand, enables individuals and businesses to borrow funds for various purposes."

                elif subject == 3:
                    if chapterr == "NE1":
                        paraTxt.text = "Networking connects devices via LANs, WANs, routers, and switches for data exchange. Protocols like TCP/IP manage communication, with encryption ensuring security. Internet familiarity is key for accessing online resources, enabling smooth information flow."

                    elif chapterr == "ETH":
                        paraTxt.text = "Cyber ethics offers guidelines for responsible online conduct, promoting respect, privacy, and awareness of digital consequences. It underscores the importance of ethical behavior, critical thinking, and positive digital citizenship in the online realm."

                    elif chapterr == "HTM":
                        paraTxt.text = "HTML is the language used to create web pages. It uses tags to structure content and define elements like headings, paragraphs, and links. It forms the backbone of the internet, allowing browsers to display information and interact with users."

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "MET":
                        paraTxt.text = "Metals exhibit characteristics like good conductivity, high melting points, and malleability, making them essential for various industrial applications. Non-metals, in contrast, often have lower melting points, are poor conductors, and may exist in various states at room temperature. This duality in properties defines the diverse roles of metals and non-metals in chemistry and daily life."

                    elif chapterr == "CON":
                        paraTxt.text = "In the realm of biology, control and coordination mechanisms are crucial for orchestrating various bodily functions. Nervous impulses facilitate swift responses, while hormones, acting as messengers, regulate long-term processes. Together, these systems enable organisms to navigate and adapt to their environments."

                    elif chapterr == "ELE":
                        paraTxt.text = "Derived from the flow of electrons, electricity is a versatile energy source harnessed for a myriad of applications. It enables the functioning of electronic devices, facilitates communication, and powers essential systems that drive modern."

                    elif chapterr == "SOU":
                        paraTxt.text = "Sources of energy are diverse forms of power harnessed to meet human needs. These include renewable sources like sunlight, wind, and hydroelectricity, as well as non-renewable sources such as fossil fuels (coal, oil, and natural gas) and nuclear energy. The exploration and utilization of these sources drive energy production, impacting both environmental sustainability and global economic dynamics."

                elif subject == 2:
                    if chapterr == "WAT":
                        paraTxt.text = "Water resources are essential for various purposes, including agriculture, industry, and human consumption. They comprise freshwater bodies like rivers, lakes, and aquifers. Sustainable management is crucial to address challenges such as pollution, depletion, and unequal access."

                    elif chapterr == "COR":
                        paraTxt.text = "Consumer rights are fundamental protections afforded to individuals in the marketplace. Upholding consumer rights promotes trust, accountability, and ethical business practices, ultimately empowering individuals to make informed decisions and demand high-quality goods and services."

                    elif chapterr == "MON":
                        paraTxt.text = "Money and credit delves into the core principles of monetary systems and lending practices. Money serves as a medium for transactions and a measure of value, while credit provides individuals and businesses with access to funds beyond their immediate means."

                    elif chapterr == "RES":
                        paraTxt.text = "Resource and development examines the relationship between natural resources and human progress. It explores how societies utilize resources for economic, social, and environmental advancement. Understanding resource management is vital for sustainable development."

                elif subject == 3:
                    if chapterr == "NE1":
                        paraTxt.text = "Networking also involves various components and technologies, including routers, switches, hubs, network cables, and protocols. Protocols, such as the TCP/IP (Transmission Control Protocol/Internet Protocol), govern how data is transmitted and received across networks."

                    elif chapterr == "ETH":
                        paraTxt.text = "Cyber ethics offers guidelines for responsible online conduct, promoting respect, privacy, and awareness of digital consequences. It underscores the importance of ethical behavior, critical thinking, and positive digital citizenship in the online realm."

                    elif chapterr == "HTM":
                        paraTxt.text = "HTML is the language used to create web pages. It uses tags to structure content and define elements like headings, paragraphs, and links. It forms the backbone of the internet, allowing browsers to display information and interact with users."

        elif age == 15:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "OSC":
                        paraTxt.text = "Oscillation refers to the repetitive motion or movement of an object or system around a central point or equilibrium position. It is characterised by periodic fluctuations in position, velocity, or other physical quantities.Understanding oscillation is crucial in physics and engineering, as it plays a fundamental role."

                    elif chapterr == "KIN":
                        paraTxt.text = "Understanding kinetic energy is essential for analyzing and predicting the behavior of moving objects in the physical world.Kinetic energy is the energy possessed by an object due to its motion. It depends on both the object's mass and velocity, with faster-moving objects or those with greater mass possessing more kinetic energy."

                elif subject == 2:
                    if chapterr == "BNP":
                        paraTxt.text = "The nature and purpose of business encapsulates the essence and objectives of commercial endeavours. Businesses exist to satisfy human needs and wants through the production and distribution of goods and services. Understanding the nature of business involves recognizing its diverse forms."

                    elif chapterr == "BSE":
                        paraTxt.text = "Business services encompass a wide range of activities provided to other businesses to support their operations. These services include professional services like consulting, legal, and accounting, as well as technical services such as IT support and software development."

                elif subject == 3:
                    if chapterr == "YOG":
                        paraTxt.text = "Yoga is a centuries-old practice originating from ancient India that focuses on the union of the body, mind, and spirit. It involves physical postures, breathing exercises, meditation, and relaxation techniques. Yoga aims to promote overall health and well-being."

                    elif chapterr == "PSY":
                        paraTxt.text = "The intersection of psychology and sports explores the mental aspects of athletic performance and participation. It delves into the psychological factors influencing athletes' behavior, motivation, focus, and performance under pressure."

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "OSC":
                        paraTxt.text = "Oscillation involves the rhythmic back-and-forth motion of an object around a fixed point or equilibrium. It manifests in various forms and characterized by its repetitive nature and can be described mathematically."

                    elif chapterr == "KIN":
                        paraTxt.text = "Kinetic energy is the energy of motion possessed by an object. It arises from the object's velocity and mass, with faster-moving or heavier objects having more kinetic energy. This energy is essential for understanding the dynamics of moving objects."

                    elif chapterr == "GRA":
                        paraTxt.text = "Gravitation is the force of attraction between objects with mass. It's what keeps us grounded on Earth and governs the motion of celestial bodies like planets, stars, and galaxies. It  plays a key role in understanding the structure of the universe and predicting the movements of objects in space."

                elif subject == 2:
                    if chapterr == "BNP":
                        paraTxt.text = "The nature and purpose of business delineate its fundamental characteristics and objectives. Businesses function as economic entities, and exchange activities to fulfil consumer needs and desires. They operate within legal, social, and ethical frameworks."

                    elif chapterr == "BSE":
                        paraTxt.text = "Understanding business services is crucial for efficient and effective operations, as they play a vital role in facilitating commerce and enabling businesses to focus on their core activities.They encompass a diverse array of offerings aimed at assisting other businesses in various aspects of their operations."

                    elif chapterr == "INT":
                        paraTxt.text = "Internal trade refers to the buying and selling of goods and services within the borders of a country. It involves transactions between businesses, consumers, and the government. Internal trade plays a crucial role in the economy by facilitating the exchange of goods and services, supporting businesses, generating employment, and promoting economic growth."

                elif subject == 3:
                    if chapterr == "YOG":
                        paraTxt.text = "Yoga, rooted in ancient Indian tradition, is a holistic practice that integrates physical postures, breath control, meditation, and relaxation techniques. It seeks to harmonise the body, mind, and spirit, promoting overall well-being and inner peace."

                    elif chapterr == "PSY":
                        paraTxt.text = "The integration of psychology and sports examines the mental dimensions of athletic performance and participation. It explores how psychological factors such as motivation, confidence, focus, and resilience impact athletes' abilities and outcomes."

                    elif chapterr == "HEA":
                        paraTxt.text = "Physical fitness education promotes lifelong health and well-being by emphasising the importance of regular exercise, proper nutrition, and healthy lifestyle choices. It equips individuals with knowledge and skills to engage in physical activities that enhance cardiovascular health, muscular strength, flexibility, and endurance."

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "OSC":
                        paraTxt.text = "Oscillations are characterised by their periodic nature. They play a fundamental role in various fields, including physics, engineering, and biology, where they are used to describe phenomena like wave propagation, harmonic motion, and biological rhythms."

                    elif chapterr == "KIN":
                        paraTxt.text = "Kinetic energy is the energy something has because it's moving. The faster it moves and the heavier it is, the more kinetic energy it has. It's what makes things like cars go, balls bounce, and people run."

                    elif chapterr == "GRA":
                        paraTxt.text = "Gravitation is the force that pulls objects toward each other because they have mass. It's why things fall to the ground and why planets orbit around the sun. This force was famously described by Sir Isaac Newton."

                    elif chapterr == "THE":
                        paraTxt.text = "Thermodynamics is the study of heat and energy transfer in systems. It explores how energy moves and changes forms within these systems, such as engines, refrigerators, and living organisms. Understanding thermodynamics is crucial for various fields, including engineering, physics, chemistry, and biology."

                elif subject == 2:
                    if chapterr == "BNP":
                        paraTxt.text = "Understanding the nature of business involves recognizing its entrepreneurial spirit, innovation, and risk-taking elements. The purpose of business extends beyond financial gain to encompass goals like fostering growth, providing employment opportunities, and contributing to community development."

                    elif chapterr == "BSE":
                        paraTxt.text = "Business services are different kinds of help that one business provides to another. These services can include things like giving advice (like legal or financial advice), helping with technology (like fixing computers or making software), or handling things like transportation and storing goods."

                    elif chapterr == "INT":
                        paraTxt.text = "Understanding internal trade helps in analyzing how goods and services move within a country's borders.It's important for the economy because it supports businesses, creates jobs, and helps in economic growth."

                    elif chapterr == "GLO":
                        paraTxt.text = "International business involves commercial transactions across national borders, encompassing trade in goods, services, and investments between countries. It is influenced by various factors such as political, economic, social, and cultural differences between nations."

                elif subject == 3:
                    if chapterr == "YOG":
                        paraTxt.text = "Yoga, originating from ancient India, is a holistic practice that unites the body, mind, and spirit. It involves various techniques such as physical postures (asanas), breathing exercises (pranayama), and meditation to promote overall health and well-being."

                    elif chapterr == "PSY":
                        paraTxt.text = "The integration of psychology and sports examines the mental dimensions of athletic performance and participation. It explores how psychological factors such as motivation, confidence, focus, and resilience impact athletes' abilities and outcomes."

                    elif chapterr == "HEA":
                        paraTxt.text = "Physical fitness education promotes lifelong health and well-being by emphasising the importance of regular exercise, proper nutrition, and healthy lifestyle choices. It equips individuals with knowledge and skills to engage in physical activities that enhance cardiovascular health, muscular strength, flexibility, and endurance."

        elif age == 16:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "AMI":
                        paraTxt.text = "Amines are organic compounds containing nitrogen atoms bonded to carbon atoms and hydrogen atoms. They are classified based on the number of carbon atoms attached to the nitrogen atom.They find widespread applications in pharmaceuticals, dyes, and organic synthesis due to their versatile chemical properties."

                    elif chapterr == "SOL":
                        paraTxt.text = "Solutions are homogeneous mixtures composed of two or more substances uniformly distributed at a molecular level. They consist of a solvent, which dissolves other substances, and solutes, which are dissolved in the solvent."

                elif subject == 2:
                    if chapterr == "DIV":
                        paraTxt.text = "The diversity of living organisms refers to the wide variety of species and life forms found on Earth. It encompasses everything from microscopic bacteria to towering trees and majestic mammals. This diversity is shaped by evolutionary processes  and adaptation to different environments."

                    elif chapterr == "CEL":
                        paraTxt.text = "The cell is the basic structural and functional unit of life, encompassing various organelles and structures that perform specialized functions. The cell membrane regulates the passage of materials in and out of the cell, while the nucleus houses genetic material (DNA) and controls cellular activities."

                elif subject == 3:
                    if chapterr == "COM":
                        paraTxt.text = "Computational thinking and programming involve problem-solving and designing algorithms to tackle complex issues using computers. It includes breaking down problems into smaller, manageable parts, identifying patterns, and creating step-by-step instructions to solve them."

                    elif chapterr == "CNE":
                        paraTxt.text = "Computer networks are systems that allow multiple computers to communicate and share resources, such as data, files, and devices. They can be classified based on their geographic scope, including Local Area Networks (LANs) for small areas and Wide Area Networks (WANs) for larger geographic areas."

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "AMI":
                        paraTxt.text = "Amines are organic compounds characterised by the presence of a nitrogen atom bonded to one or more alkyl or aryl groups. They can be classified as primary, secondary, or tertiary, depending on the number of carbon groups attached to the nitrogen atom. Amines play crucial roles in biological systems."

                    elif chapterr == "SOL":
                        paraTxt.text = "Solutions are mixtures where substances are uniformly distributed at a molecular level. They consist of a solvent, which dissolves other substances . Solutions can exist in different states: gas, liquid, or solid, depending on the state of the solvent and solute. They are vital in various applications."

                    elif chapterr == "BIO":
                        paraTxt.text = "Biomolecules are molecules essential for life, found in all living organisms. They include carbohydrates, lipids, proteins, and nucleic acids. Understanding biomolecules is crucial for comprehending the biochemical processes underlying life and developing treatments for diseases."

                elif subject == 2:
                    if chapterr == "DIV":
                        paraTxt.text = "Understanding the diversity of living organisms is essential for studying biology, ecology, and environmental science. It helps us appreciate the complexity of life on our planet and the interconnectedness of all living things."

                    elif chapterr == "CEL":
                        paraTxt.text = "Cells are the basic units of life, each with specialized parts called organelles. These organelles perform specific functions: the nucleus stores genetic material, the mitochondria generate energy, and the cell membrane regulates what enters and exits the cell. Together, these components enable cells to carry out essential processes for life."

                    elif chapterr == "PLA":
                        paraTxt.text = "Plant physiology is the study of how plants function and respond to their environment. It explores processes such as photosynthesis, respiration, and growth, as well as how plants adapt to factors like light, water, and temperature."

                elif subject == 3:
                    if chapterr == "COM":
                        paraTxt.text = "Computational thinking and programming skills are essential in various fields, from computer science and engineering to biology and finance. They empower individuals to analyse data, automate processes, and develop innovative solutions to real-world problems."

                    elif chapterr == "CNE":
                        paraTxt.text = "Computer networks enable the connection and communication between multiple devices, allowing them to share resources and information. They can range from small-scale setups like home networks to large-scale systems connecting organizations globally."

                    elif chapterr == "DAT":
                        paraTxt.text = "Database management involves the organisation, storage, retrieval, and manipulation of data in a systematic and efficient manner. It encompasses creating, maintaining, and optimising databases to store large volumes of structured or unstructured information."

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "AMI":
                        paraTxt.text = "Amines play crucial roles in biological processes, serving as essential components of proteins, neurotransmitters, and vitamins.They are widely used in the production of pharmaceuticals, pesticides, and dyes, as well as in organic synthesis and as intermediates in various chemical reactions."

                    elif chapterr == "SOL":
                        paraTxt.text = "Solutions are essential in chemistry for processes like dissolution, chemical reactions, and concentration measurements. They also play crucial roles in everyday life. Understanding solutions is fundamental for a wide range of scientific and practical applications."

                    elif chapterr == "BIO":
                        paraTxt.text = "Biomolecules are fundamental to understanding biological processes, from metabolism to genetic inheritance, and are crucial targets for biomedical research and drug development."

                    elif chapterr == "ECH":
                        paraTxt.text = "Electrochemistry is the branch of chemistry that deals with the relationship between electricity and chemical reactions. It involves the study of redox reactions, where one substance loses electrons  while another gains electrons . Electrochemical processes are vital in various applications."

                elif subject == 2:
                    if chapterr == "DIV":
                        paraTxt.text = "The diversity of living organisms represents the multitude of species and life forms that inhabit our planet. It encompasses a vast array of organisms, ranging from single-celled bacteria to complex multicellular organisms like plants, animals, and fungi."

                    elif chapterr == "CEL":
                        paraTxt.text = "Cells are the basic units of life, forming the foundation of all living organisms. They are incredibly small structures that perform various functions necessary for life. Understanding cells is crucial for comprehending the complexity of living organisms and the processes that sustain life."

                    elif chapterr == "PLA":
                        paraTxt.text = "Understanding plant physiology is essential for agriculture, ecology, and environmental science, as it provides insights into plant growth, development, and interactions with their surroundings."

                    elif chapterr == "BST":
                        paraTxt.text = "Structural organisation in plants and animals refers to the arrangement of cells, tissues, and organs that form their bodies. In plants, this organisation encompasses roots, stems, leaves, and reproductive structures, while in animals, it includes organs such as the heart, lungs, brain, and digestive system."

                elif subject == 3:
                    if chapterr == "COM":
                        paraTxt.text = "Computational thinking and programming encompass the systematic approach of breaking down problems into smaller, solvable parts and devising algorithms to solve them. It involves analysing data, identifying patterns, and developing logical solutions using computer programming languages."

                    elif chapterr == "CNE":
                        paraTxt.text = "Computer networks enable the connection and communication between multiple devices, allowing them to share resources and information. They can range from small-scale setups like home networks to large-scale systems connecting organisations globally."

                    elif chapterr == "DAT":
                        paraTxt.text = "Database management involves the organisation, storage, retrieval, and manipulation of data in a systematic and efficient manner. It encompasses creating, maintaining, and optimising databases to store large volumes of structured or unstructured information."


    def clickdo(self):
        print(f"Current Screen: {self.root.current_screen.name}")
        print(f"IDs on Current Screen: {self.root.current_screen.ids}")
        qTxt = self.root.get_screen('questionsscreen').ids.questiontxt
        print(f"Thank you {qTxt}")
        print(f"Current Screen: {self.root.current_screen.name}")
        print(f"Question Number: {self.questionnumber}")

        qNo = self.root.get_screen('questionsscreen').ids.questionno
        aHere = self.root.get_screen('questionsscreen').ids.ansHere
        sBtn = self.root.get_screen('questionsscreen').ids.submitBtn
        lang = self.stored_lang
        age = self.stored_age
        preScore = int(self.stored_score)
        chapterr = self.chapter_name
        qImg = self.root.get_screen('questionsscreen').ids.questionsimg
        questionn = int(self.questionnumber)
        aHere.opacity = 1
        subject = int(self.subjectClicked)
        print(age)
        print(preScore)
        print(f"chapter: {chapterr}")
        print(f"questionn: {questionn}")
        print(subject)
        qTxt.opacity = 1
        qNo.opacity = 1
        if questionn == 0:
            pass
        elif questionn == 1:
            pass
        elif questionn == 2:
            qImg.source = "questionsimg2.jpg"
        elif questionn == 3:
            qImg.source = "questionsimg3.jpg"
        elif questionn == 4:
            qImg.source = "questionsimg4.png"
        else:
            qImg.source = "questionsimg5.png"
        if age == "13":
            print("First")
            print(f"prescore: {preScore}")
            if 0 <= preScore <= 3:
                print("Second")
                print(f"sub: {subject}")
                if subject == 1:
                    print("Third")
                    if chapterr == "FUL":
                        print("Fourth")
                        if questionn == 1:
                            print("Fifth")
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = "What is the basic structural and functional \n unit of all living organisms?"
                                self.checkans()
                            else:
                                self.checkans()

                            # return "Hello"
                        elif questionn == 2:
                            qTxt.text = "Which organelle is responsible for \n the production of energy in a cell?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the green pigment responsible \n for photosynthesis in plant cells?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which type of cells lack \n a defined nucleus?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the control center of the \n cell that contains genetic material?"
                            self.checkans()
                            questionn = 1

                            qTxt.text = ""




                    elif chapterr == "MAT":
                        if questionn == 1:
                            # qTxt.text = ""

                            if qTxt.text == "":
                                qTxt.text = "What is the measure of the hotness \n or coldness of an object?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the change of a liquid into \n a gas at the surface called?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What do we call the tiny \n particles that make up matter?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the state of matter with \n a definite shape and volume?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the process of a \n gas turning into a liquid?"
                            self.checkans()

                elif subject == 2:
                    if chapterr == "NET":
                        if questionn == 1:

                            # qTxt.text = "What connects computers to the web allowing communication?"
                            if qTxt.text == "":

                                qTxt.text = "What connects computers to the web allowing communication?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the process of converting data into \n a coded form to prevent unauthorized access?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the term for the physical components \n of a computer, such as the monitor, \n keyboard, and CPU?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What do we call a small piece of data \n stored on a user's computer by a web \n browser to remember information about them?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the term for a set of instructions \n that a computer can execute to perform a \n specific task?"
                            self.checkans()

                    elif chapterr == "SEC":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = "What cybersecurity practice involves scrambling \n passwords to enhance security?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What deceptive practice aims to trick individuals \n into revealing sensitive information in \n electronic communication?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What software blocks malicious programs \n on a computer system?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What's the unauthorized access to computer \n systems with malicious intent called?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What's the term for a picture representation \n of an app on a computer?"
                            self.checkans()

                elif subject == 3:
                    if chapterr == "PPL":
                        if questionn == 1:
                            self.convertText()

                            if qTxt.text == "":
                                qTxt.text = "What is the term for a skilled \n and productive workforce?"
                                self.convertText()
                                self.checkans()
                            else:
                                self.convertText()

                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which sector includes activities \n like farming and fishing?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which type of unemployement occurs when \n someone has a job but is underpaid or \n his services are not needed?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the term for the total number \n of people in a country or region?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the organized effort to increase people's \n knowledge and skills for a purpose?"
                            self.checkans()
                            questionn = 1

                            qTxt.text = ""

                            print(self.newscore)
                    elif chapterr == "CLI":
                        if questionn == 1:
                            if qTxt.text == "":
                                qTxt.text = "What term refers to the average weather \n conditions of a region over a \n long period?"
                                self.checkans()
                            else:
                                self.checkans()

                            # qTxt.text = ""
                            # self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the measure of the amount of moisture in the air?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the name for the phenomenon of the warming up \n of the Earth due to the trapping of heat \n by certain gases in the atmosphere?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What term is used for the sudden and temporary \n change in the Earth's climate patterns?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the gradual increase in the Earth's \n average temperature over an extended period?"
                            self.checkans()
                            questionn = 1

                            qTxt.text = ""


            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "FUL":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = "What is the green pigment responsible for \n photosynthesis in plant cells?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which organelle is the storage area for water, \n waste, and nutrients in plant cells?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the protective outer layer of a \n plant cell called?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which small structures in the cell help \n in protein synthesis?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the control center of the cell \n that contains genetic information?"
                            self.checkans()

                    elif chapterr == "MAT":
                        if questionn == 1:
                            # qTxt.text = "What is the direct change from a solid to \n a gas called?"
                            if qTxt.text == "":
                                qTxt.text = "What is the direct change from a solid to \n a gas called?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the force that holds atoms \n together in a molecule?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the state of matter that has \n neither a fixed shape nor a fixed volume?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is a substance that cannot be \n broken down by chemical means?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the measure of the amount of space \n an object occupies?"
                            self.checkans()

                    elif chapterr == "TIS":
                        if questionn == 1:
                            # qTxt.text = "What is the term for a group of similar cells \n performing a specific function in \n the body?"
                            if qTxt.text == "":
                                qTxt.text = "What is the term for a group of similar cells \n performing a specific function in \n the body?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What tissue connects bones to each other \n in the human body?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the protective tissue that covers the \n surface of leaves and stems in plants?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which tissue conducts water and nutrients \n in vascular plants?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What tissue is responsible for body movement \n in animals?"
                            self.checkans()

                elif subject == 2:
                    if chapterr == "NET":
                        if questionn == 1:
                            # qTxt.text = "What's the main circuit board in a computer \n connecting essential components?"
                            if qTxt.text == "":
                                qTxt.text = "What's the main circuit board in a computer \n connecting essential components?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What's the term for a collection of \n related web pages with a common \n domain name?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What do we call a program designed for a \n specific task, like Microsoft Word?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What's the name for a device that moves \n the cursor on a computer screen?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What's the term for a picture representation \n of an app on a computer?"
                            self.checkans()

                    elif chapterr == "SEC":
                        if questionn == 1:
                            # qTxt.text = "What cybersecurity practice involves scrambling \n passwords to enhance security?"
                            if qTxt.text == "":
                                qTxt.text = "What cybersecurity practice involves scrambling \n passwords to enhance security?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What deceptive practice aims to trick individuals \n into revealing sensitive information in \n electronic communication?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What software blocks malicious programs \n on a computer system?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What's the unauthorized access to computer \n systems with malicious intent called?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What's the term for a picture representation \n of an app on a computer?"
                            self.checkans()

                    elif chapterr == "OFF":
                        if questionn == 1:
                            # qTxt.text = "_______ command is used to move the \n text to a new page."
                            if qTxt.text == "":
                                qTxt.text = "_______ command is used to move the \n text to a new page."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Portrait format changes the page \n orientation ________."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the general arrangement of \n the text in the document called?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Each individual rectangle in a table is \n called _______."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Alignment buttons are available on \n the _______ tab."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "PPL":
                        if questionn == 1:
                            # qTxt.text = "What is the total value of goods and services \n produced in a country?"
                            if qTxt.text == "":
                                qTxt.text = "What is the total value of goods and services \n produced in a country?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the term for skills and knowledge \n contributing to economic productivity?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the total number of people in \n a region?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the effort to increase knowledge \n and skills for a purpose?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the economic process of adding \n value to raw materials?"
                            self.checkans()

                    elif chapterr == "CLI":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = ""
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = ""
                            self.checkans()

                    elif chapterr == "WOR":
                        if questionn == 1:
                            # qTxt.text = "What's the written set of fundamental \n principles for a country or \n organization?"
                            if qTxt.text == "":
                                qTxt.text = "WWhat's the written set of fundamental \n principles for a country or \n organization?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Who conducts fair elections in a democracy?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What's the system with power divided \n between central and state \n governments?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Who makes laws in a parliamentary system?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What's the term for electing \n representatives to make decisions?"
                            self.checkans()

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "FUL":
                        if questionn == 1:
                            # qTxt.text = "What cellular structure is responsible for the \n synthesis of ribosomal RNA and assembly \n of ribosomes?"
                            if qTxt.text == "":
                                qTxt.text = "What cellular structure is responsible for the \n synthesis of ribosomal RNA and assembly \n of ribosomes?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the process by which cells ingest \n large particles, such as food, \n through engulfing?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What organelle contains enzymes responsible \n for breaking down waste materials in a \n cell?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the network of membranes that transport \n materials within a eukaryotic cell?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What term refers to the semi-fluid material \n inside a cell that surrounds the \n organelles?"
                            self.checkans()

                    elif chapterr == "MAT":
                        if questionn == 1:
                            # qTxt.text = "What is the minimum energy required to \n initiate a chemical reaction called?"
                            if qTxt.text == "":
                                qTxt.text = "What is the minimum energy required to \n initiate a chemical reaction called?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What term describes a substance's ability \n to dissolve in a solvent and form a \n homogeneous mixture?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "How do we classify mixtures with uneven distribution \n of components, allowing individual \n substance identification?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the unit of measurement representing \n the amount of a substance?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What scientific process involves a direct transition \n from solid to gas without an intermediate \n liquid state?"
                            self.checkans()

                    elif chapterr == "TiS":
                        if questionn == 1:
                            # qTxt.text = "What tissue type is responsible for the \n contraction and movement in animal bodies?"
                            if qTxt.text == "":
                                qTxt.text = "What tissue type is responsible for the \n contraction and movement in animal bodies?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the term for the tissue that \n covers the body's external surface and \n lines internal organs?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What tissue provides support, strength, \n and flexibility in the human body's \n structural framework?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What tissue is responsible for food storage \n and helps in buoyancy?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What tissue transmits electrical impulses \n in the nervous system?"
                            self.checkans()

                    elif chapterr == "ATO":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = "What tissue type is responsible for the \n contraction and movement in animal bodies?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = ""
                            self.checkans()

                elif subject == 2:
                    if chapterr == "NET":
                        if questionn == 1:
                            # qTxt.text = "What is the collection of eight bits \n called?"
                            if qTxt.text == "":
                                qTxt.text = "What is the collection of eight bits \n called?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which input device is used to \n record sound?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Joseph Jacquard invented the Jacquard's ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Who is known as the father of the \n modern computer?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Fourth generation computers used _______."
                            self.checkans()

                    elif chapterr == "SEC":
                        if questionn == 1:
                            # qTxt.text = "Which type of attack uses a fraudulent \n server with a relay address?"
                            if qTxt.text == "":
                                qTxt.text = "Which type of attack uses a fraudulent \n server with a relay address?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "_______ is a type of software designed to \n help the user's computer detect viruses."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which is the oldest technique used by \n hackers for phone hacking?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is considered as the unsolicited \n commercial email?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_______ can help reduce the risk of data leakage."
                            self.checkans()

                    elif chapterr == "OFF":
                        if questionn == 1:
                            # qTxt.text = "______ command is used to move the \n text to a new page."
                            if qTxt.text == "":
                                qTxt.text = "______ command is used to move the \n text to a new page."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Portrait format changes the page \n orientation ________."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the general arrangement of \n the text in the document called?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Each individual rectangle in a table is \n called _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Alignment buttons are available on \n the _______ tab."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "PPL":
                        if questionn == 1:
                            # qTxt.text = "In how many sectors have the economic \n activities been classified?"
                            if qTxt.text == "":
                                qTxt.text = "In how many sectors have the economic \n activities been classified?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The literacy rate of India during 2010-11 was ______."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Quarrying and manufacturing is included \n in the _______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Self-consumption is _______."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "When there is investment made in the form of \n education, training and medical care, \n the population becomes _______ ."
                            self.checkans()

                    elif chapterr == "CLI":
                        if questionn == 1:
                            # qTxt.text = "What are thunder storms called in \n West Bengal?"
                            if qTxt.text == "":
                                qTxt.text = "What are thunder storms called in \n West Bengal?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What influences the climate of India \n strongly?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the apparent force caused by \n the earth’s rotation called?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Where are Mawsynram hills located?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "In winter, the western cyclonic disturbances \n originate from which sea?"
                            self.checkans()

                    elif chapterr == "WOR":
                        if questionn == 1:
                            # qTxt.text = "Which office holds a term of 6 \n years in India?"
                            if qTxt.text == "":
                                qTxt.text = "Which office holds a term of 6 \n years in India?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The Council of Ministers is collectively \n responsible to:"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Who is the head of the State Government \n in India?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the minimum age requirement to become \n a member of the Rajya Sabha?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Which institution is responsible for \n making laws in India?"
                            self.checkans()

                    elif chapterr == "NAT":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = ""
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = ""
                            self.checkans()

        elif age == 14:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "MET":
                        if questionn == 1:
                            # qTxt.text = "The extraction of metals from their ores \n and then refining them for use is \n known as ___ ."
                            if qTxt.text == "":
                                qTxt.text = "The extraction of metals from their ores \n and then refining them for use is \n known as ___ ."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ is an alloy of Mercury."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which property of metals is used for making \n bells and strings of musical instruments?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ is a technique for protecting iron from \n corrosion by coating it with a thin layer \n of zinc."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Which element is very abundant in the \n earth?"
                            self.checkans()

                    elif chapterr == "CON":
                        if questionn == 1:
                            # qTxt.text = "Response of plant roots towards water \n is called _______."
                            if qTxt.text == "":
                                qTxt.text = "Response of plant roots towards water \n is called _______."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Movement of sunflower in accordance with the \n path of Sun is due to _______."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which plant hormone promotes cell \n division?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Any change in the environment to which an \n organism responds is called _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "A part of the body which responds to the \n in-structions sent from nervous system \n is called _________."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "WAT":
                        if questionn == 1:
                            # qTxt.text = "The major source of fresh water in India \n is _______water."
                            if qTxt.text == "":
                                qTxt.text = "The major source of fresh water in India \n is _______water."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which river is known as the lifeline \n of India?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Where is bamboo drip irrigation system \n prevalent?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The only State which has made rooftop rainwater \n harvesting structure compulsory to all the \n houses is _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Hirakud Dam is constructed on the river \n ____."
                            self.checkans()

                    elif chapterr == "COR":
                        if questionn == 1:
                            # qTxt.text = "Which logos is used for \n standardisation of agricultural \n products?"
                            if qTxt.text == "":
                                qTxt.text = "Which logos is used for \n standardisation of agricultural \n products?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which certification is maintained for \n standardisation of jewellery?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The agencies which look into the \n complaints of the consumers are \n popularly called ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The process of lowering the quality of food \n through the addition of another substance \n is called ___."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Taking advantage of consumers' ignorance \n or helplessness is known as ___."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "NE1":
                        if questionn == 1:
                            # qTxt.text = "The ________ command is used to \n display name of the computer."
                            if qTxt.text == "":
                                qTxt.text = "The ________ command is used to \n display name of the computer."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which device is required to connect \n multiple heterogeneous networks?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "HTTPS transfers ______ data."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The ______ command is used to verify the \n connectivity between two computers."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "An access point is used to connect to a ______ network."
                            self.checkans()

                    elif chapterr == "ETH":
                        if questionn == 1:
                            # qTxt.text = "Using someone else's twitter handle to post \n something, will be termed as ___."
                            if qTxt.text == "":
                                qTxt.text = "Using someone else's twitter handle to post \n something, will be termed as ___."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Policies of companies related to protection of \n personal information of users online are \n meant to safeguard the ____ of users."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Trojan Horse is a type of ______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ is done to avoid plagiarism."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is another name for closed software?"
                            self.checkans()

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "MET":
                        if questionn == 1:
                            # qTxt.text = ""
                            if qTxt.text == "":
                                qTxt.text = ""
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = ""
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = ""
                            self.checkans()

                    elif chapterr == "CON":
                        if questionn == 1:
                            # qTxt.text = "The highest coordinating centre in the \n human body is ______."
                            if qTxt.text == "":
                                qTxt.text = "The highest coordinating centre in the \n human body is ______."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "A microscopic gap between a pair of adjacent \n neurons over which nerve impulses \n pass is called _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which plant hormone promotes cell \n division?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which gland secretes the growth hormone?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the longest fibre on the cell body \n of a neuron called?"
                            self.checkans()

                    elif chapterr == "ELE":
                        if questionn == 1:
                            # qTxt.text = "What is the SI unit of electric current?"
                            if qTxt.text == "":
                                qTxt.text = "What is the SI unit of electric current?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Name the instrument used for measuring electric current."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The unit of e.m.f. of a cell is ______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The obstruction offered by material of \n conductor to the passage of electric \n current is known as _________."
                            self.checkans()

                        elif questionn == 5:

                            qTxt.text = "The resistance of a conductor is directly \n proportional to its ____."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "WAT":
                        if questionn == 1:
                            # qTxt.text = "Underground tanks seen in Rajasthan to \n store rainwater for drinking is \n called _____."
                            if qTxt.text == "":
                                qTxt.text = "Underground tanks seen in Rajasthan to \n store rainwater for drinking is \n called _____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Name the remote village that has earned \n the rare distinction of being rich \n in rainwater?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Rooftop rainwater harvesting is the most \n common practice in ______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The first multi-purpose project of \n India was ________."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the process of converting seawater \n into freshwater known as?"
                            self.checkans()

                    elif chapterr == "COR":
                        if questionn == 1:
                            # qTxt.text = "People who make goods and provide services \n are called____."
                            if qTxt.text == "":
                                qTxt.text = "People who make goods and provide services \n are called____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "In which month is the ‘National \n Consumers Day’ celebrated \n in India?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "In which court a consumer should file a \n case if he/she is exploited in the \n market?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The _______ was earlier known as Indian \n Standards Instituition."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The ISI, A-Mark or Hallmark \n logo on a package assures ____."
                            self.checkans()

                    elif chapterr == "MON":
                        if questionn == 1:
                            # qTxt.text = "_________ are the main informal source of \n credit for rural households in India."
                            if qTxt.text == "":
                                qTxt.text = "_________ are the main informal source of \n credit for rural households in India."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the term for the money in \n circulation?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Secured loans are guaranteed by a _______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "A system of exchanging goods or services for \n other goods or services without using \n money is known as ___."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the measure of a person's \n ability to repay a loan known as?"
                            self.checkans()

                elif subject == 3:
                    if chapterr == "NE1":
                        if questionn == 1:
                            # qTxt.text = "HTTP is a protocol which helps you to \n communicate between a Web ______ and \n a Web browser."
                            if qTxt.text == "":
                                qTxt.text = "HTTP is a protocol which helps you to \n communicate between a Web ______ and \n a Web browser."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The topology which has the highest reliability is ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The time required for a gate or inverter \n to change its state is called _____ time."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Name the hardware device that is capable \n of executing a sequence of instructions."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The basic goal of the computer process \n is to convert data into ______."
                            self.checkans()

                    elif chapterr == "ETH":
                        if questionn == 1:
                            # qTxt.text = "Using someone else's twitter handle to post \n something, will be termed as ___."
                            if qTxt.text == "":
                                qTxt.text = "Using someone else's twitter handle to post \n something, will be termed as ___."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Policies of companies related to protection of \n personal information of users online are \n meant to safeguard the ____ of users."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Trojan Horse is a type of ______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ is done to avoid plagiarism."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is another name for closed software?"
                            self.checkans()

                    elif chapterr == "HTM":
                        if questionn == 1:
                            # qTxt.text = "Which section is used for texts and tags \n that are shown directly on the web pages?"
                            if qTxt.text == "":
                                qTxt.text = "Which section is used for texts and tags \n that are shown directly on the web pages?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which is the most basic program needed \n to write HTML code?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "HTML tags are placed between \n ____ brackets."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "______ tags are used in HTML."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The tags that need both starting and \n ending tags are called _________tags."
                            self.checkans()

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "MET":
                        if questionn == 1:
                            # qTxt.text = "Where is white phosphorus stored?"
                            if qTxt.text == "":
                                qTxt.text = "Where is white phosphorus stored?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Cake does not taste bitter due to presence \n of _______acid."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Non-metals generally form ________ ions when \n they react chemically."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the process of converting an oxide \n of a metal to the metal itself \n using heat alone?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Aluminium is used in making aircraft bodies \n due to its low ________."
                            self.checkans()

                    elif chapterr == "CON":
                        if questionn == 1:
                            # qTxt.text = "Lack of ______ hormone in childhood \n leads to dwarfism in humans."
                            if qTxt.text == "":
                                qTxt.text = "Lack of ______ hormone in childhood \n leads to dwarfism in humans."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Control and coordination are the functions of \n the nervous system and _____ \n in our body."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A diabetic patient suffers from deficiency \n of which hormone?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_______ acts as both endocrine and exocrine gland."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What controls the posture and balance \n of the body?"
                            self.checkans()

                    elif chapterr == "ELE":
                        if questionn == 1:
                            # qTxt.text = "The rate at which electric energy is \n consumed or dissipated is called ____."
                            if qTxt.text == "":
                                qTxt.text = "The rate at which electric energy is \n consumed or dissipated is called ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "______ measures the potential differences \n between two points of the circuit."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Variable resistance is called _____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Materials which allow larger currents to \n flow through them are called ______."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Kilowatt hour is the unit of _____."
                            self.checkans()

                    elif chapterr == "SOU":
                        if questionn == 1:
                            # qTxt.text = "Hydro-power plant converts the ________ \n energy of flowing water into electricity."
                            if qTxt.text == "":
                                qTxt.text = "Hydro-power plant converts the ________ \n energy of flowing water into electricity."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The ultimate source of all forms of \n energy is ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Energy possessed by the body by virtue of \n its motion is called _____ energy."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Solar cells are made up of ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The variety of coal which has the \n highest carbon content is ______."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "WAT":
                        if questionn == 1:
                            # qTxt.text = "_______ power contributes approximately 22% \n of the total electricity produced in India."
                            if qTxt.text == "":
                                qTxt.text = "_______ power contributes approximately 22% \n of the total electricity produced in India."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "In which state, palar pani is considered \n the purest form of natural water?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "In which of the following regions, people \n built ‘Guls’ and ‘Kuls’ for irrigation?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The Tehri Dam is being constructed on ____ river."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The Nagarjuna Sagar Dam is built on \n which river?"
                            self.checkans()

                    elif chapterr == "COR":
                        if questionn == 1:
                            # qTxt.text = "To get justice, consumers should go \n to the ___ court."
                            if qTxt.text == "":
                                qTxt.text = "To get justice, consumers should go \n to the ___ court."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "In the market place, rules and regulations \n are required for the protection of \n the _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Under COPRA, a consumer can seek the _____ \n for redressal of consumer disputes.\n (Hint: Acronym)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The _____ centre considers cases related to \n claim up to ₹ 20 lakh."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The root cause of consumer exploitation \n is ______."
                            self.checkans()

                    elif chapterr == "MON":
                        if questionn == 1:
                            # qTxt.text = "_____ refers to an agreement in which the lender \n supplies the borrower with money, goods or services \n in return for the promise of future payment."
                            if qTxt.text == "":
                                qTxt.text = "_____ refers to an agreement in which the lender \n supplies the borrower with money, goods or services \n in return for the promise of future payment."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Organized credit is also known as \n ______ credit."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "All the banks act as mediator between \n the _________ and borrowers."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "A person who lends money is a \n ________.(creditor/debtor)"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Which banks provide loans and other financial \n services to individuals and \n businesses?"
                            self.checkans()

                    elif chapterr == "RES":
                        if questionn == 1:
                            # qTxt.text = "Ploughing along the contour lines to \n decelerate the flow of water down \n the slopes is called ____ ploughing."
                            if qTxt.text == "":
                                qTxt.text = "Ploughing along the contour lines to \n decelerate the flow of water down \n the slopes is called ____ ploughing."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ soil is very useful for growing tea, \n coffee and cashewnut."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the other name of Black soil?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Resource planning is essential for _____ \n existence of all form of life."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_______ is the most common soil of Northern \n India."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "NE1":
                        if questionn == 1:
                            # qTxt.text = "Online discussion through posts about \n various topics is called a _______."
                            if qTxt.text == "":
                                qTxt.text = "Online discussion through posts about \n various topics is called a _______."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is combination of multimedia and \n hyperlink known as?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A collection of web pages linked together \n in a random order is known as a _______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "On internet, to go to another web page \n through button, the user should use _______."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "In Internet Protocol, data is \n organised in the form of ______."
                            self.checkans()

                    elif chapterr == "ETH":
                        if questionn == 1:
                            # qTxt.text = "A _________ software is available free of cost \n and allows copying and further distribution."
                            if qTxt.text == "":
                                qTxt.text = "A _________ software is available free of cost \n and allows copying and further distribution."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is a legal document granting exclusive \n rights to an invention or process?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Authentication, authorisation and encryption \n techniques can be used for ______ of \n data."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The concept of converting a readable message \n into an unreadable form is known as _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What are the rules for online behavior \n known as?"
                            self.checkans()

                    elif chapterr == "HTM":
                        if questionn == 1:
                            # qTxt.text = "Which section is used for texts and tags \n that are shown directly on the web pages?"
                            if qTxt.text == "":
                                qTxt.text = "Which section is used for texts and tags \n that are shown directly on the web pages?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Which is the most basic program needed \n to write HTML code?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "HTML tags are placed between \n ____ brackets."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "______ tags are used in HTML."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The tags that need both starting and \n ending tags are called _________tags."
                            self.checkans()

        elif age == 15:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "OSC":
                        if questionn == 1:
                            # qTxt.text = "Damping in oscillatory motion is caused \n by ____."
                            if qTxt.text == "":
                                qTxt.text = "Damping in oscillatory motion is caused \n by ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "For an oscilllating simple pendulum, \n the tension in the string is ____ \n at mean position."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A particle moves in a circular path \n with a uniform speed. Its motion \n is ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "In SHM, the acceleration is \n directly proportional to _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Every periodic motion is oscillatory,\n but not vice versa. True or \n False?"
                            self.checkans()

                    elif chapterr == "KIN":
                        if questionn == 1:
                            # qTxt.text = "Equal volumes of two gases at the same \n temperature and pressure have the same \n number of ______."
                            if qTxt.text == "":
                                qTxt.text = "Equal volumes of two gases at the same \n temperature and pressure have the same \n number of ______."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Kinetic energy exists in ____ bodies."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Boyle’ law is applicable for an \n _________ process."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "When a gas is in ___________ equilibrium , its \n molecules have the same average kinetic \n energy of molecules."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_______ theory of gases provide a base for \n both Charle’s law and Boyle’s law."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "BNP":
                        if questionn == 1:
                            # qTxt.text = "____ creates form utility."
                            if qTxt.text == "":
                                qTxt.text = "____ creates form utility."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "A business firm in India buy toys from China \n and sell it to Nepal. Which type of \n trading activity is referred here?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The industries which provides support \n services to other industries are \n known as ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The economic activity in which specialized \n knowledge is required is known as ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Name the auxiliary to trade which \n removes the hindrance of time."
                            self.checkans()

                    elif chapterr == "BSE":
                        if questionn == 1:
                            # qTxt.text = "________ banks provide financial \n aid to foreign trade."
                            if qTxt.text == "":
                                qTxt.text = "_______ banks provide financial \n aid to foreign trade."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "______ bank is an important source \n of agricultural financing in \n India."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Services provided by NGOs come under \n the category of _________ service."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "__________ account offers multiple options \n to the account holder."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "______ is a technique that distributes the \n risk of one person among many."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "YOG":
                        if questionn == 1:
                            # .text = "Bikram yoga is a form of _____ yoga."
                            if qTxt.text == "":
                                qTxt.text = "Bikram yoga is a form of _____ yoga."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The Asana useful in diabetes is _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Yoga means maintaining the evenness of mind \n which is known as ____ for the \n efficient performance of work."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which Yoga posture is also known \n as the 'Corpse Pose'?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What does the term 'Yoga' mean \n in Sanskrit?"
                            self.checkans()

                    elif chapterr == "PSY":
                        if questionn == 1:
                            # qTxt.text = "Change in memory and perception are \n indicators of ____ development."
                            if qTxt.text == "":
                                qTxt.text = "Change in memory and perception are \n indicators of ____ development."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Growth refers to change in ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Wilhelm Wundt is known as the \n father of _____ psychology."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_____ as a study of behaviour \n was defined by JB Watson."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The aggression is displaying aggressive \n behaviour in the pursuit of non \n aggressive goal is known as ____."
                            self.checkans()

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "OSC":
                        if questionn == 1:
                            # qTxt.text = "The motion which repeat itself after \n equal interval of time is called \n as ____ motion."
                            if qTxt.text == "":
                                qTxt.text = "The motion which repeat itself after \n equal interval of time is called \n as ____ motion."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The restoring force in S.H.M. is ______ \n in magnitude when the particle is \n instantaneously at rest. \n (zero, maximum)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The magnitude of acceleration of a particle \n in S.H.M. is the _____ at the end \n points. (least, greatest)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Resonant vibrations are a special \n case of ____ vibrations."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The total energy of a particle executing \n S.H.M. is proportional to square \n of the ____."
                            self.checkans()

                    elif chapterr == "KIN":
                        if questionn == 1:
                            # qTxt.text = "The pressure exerted by the molecules \n of a gas is due to change in the \n ______."
                            if qTxt.text == "":

                                qTxt.text = "The pressure exerted by the molecules \n of a gas is due to change in the \n ______."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The number of molecules with higher most \n probable speed ______ with the rise in \n temperature."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The _______ of a gas does not change \n during collisions."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "______ is the measure of average K.E. \n of a gas."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The _______ zero is that temperature at which all \n molecular linear velocities are zero."
                            self.checkans()

                    elif chapterr == "GRA":
                        if questionn == 1:
                            # qTxt.text = "What is the measure of the total amount of \n matter in an object called?"
                            if qTxt.text == "":
                                qTxt.text = "What is the measure of the total amount of \n matter in an object called?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the point in an orbit where a \n satellite is closest to the Earth \n called?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What term describes the path followed by \n a planet around the sun?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Gravitational force is the strongest \n fundamental force.(True/ False)."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Isaac Newton introduced the Universal Law of ______."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "BNP":
                        if questionn == 1:
                            # qTxt.text = "Commerce includes activities relating \n to trade and ____to trade."
                            if qTxt.text == "":
                                qTxt.text = "Commerce includes activities relating \n to trade and ____to trade."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Economic activities may be classified \n into business, ____ and employment."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Which economic activity is directed towards \n producing or acquiring wealth through \n buying and selling of goods?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Bad debts due to non-payment of debts by \n debtors is an example of which type \n of business risk?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What reward an entrepreneur gets \n for risk bearing in business?"
                            self.checkans()

                    elif chapterr == "BSE":
                        if questionn == 1:
                            # qTxt.text = "________ services are helpful to the \n business for establishing links \n with the outside world."
                            if qTxt.text == "":
                                qTxt.text = "________ services are helpful to the \n business for establishing links \n with the outside world."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The small periodic payment in an \n insurance is known as ______."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The contract in writing while \n getting an insurance is \n called _______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_________ cheques are encashable \n immediately at bank counters."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The ________ bank controls and supervises \n the activities of a commercial bank."
                            self.checkans()

                    elif chapterr == "INT":
                        if questionn == 1:
                            # qTxt.text = "____ are considered as the oldest \n form of itinerant retailers."
                            if qTxt.text == "":
                                qTxt.text = "____ are considered as the oldest \n form of itinerant retailers."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Retailers who deal in goods on a hand \n cart near bus stops and railway\n  stations are called as _____ traders."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The phrase ‘all shopping under \n one roof defines ___ stores."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_____ stores can be defined as \n a network of retail shops."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_____ are agents who merely bring \n the buyer and the seller into \n contact."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "YOG":
                        if questionn == 1:
                            # qTxt.text = "____ Yoga is the yoga of controlling \n our mind."
                            if qTxt.text == "":
                                qTxt.text = "____ Yoga is the yoga of controlling \n our mind."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Name the asana affects the digestive \n system."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "From which country did yoga originate?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "________ is known as ‘The Father of Yoga’."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_______ Mudra destroys all diseases of the rectum \n and prevents premature death."
                            self.checkans()

                    elif chapterr == "PSY":
                        if questionn == 1:
                            # qTxt.text = "Change in memory and perception are \n indicators of ____ development."
                            if qTxt.text == "":
                                qTxt.text = "Change in memory and perception are \n indicators of ____ development."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Growth refers to change in ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Wilhelm Wundt is known as the \n father of _____ psychology."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_____ as a study of behaviour \n was defined by JB Watson."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The aggression is displaying aggressive \n behaviour in the pursuit of non \n aggressive goal is known as ____."
                            self.checkans()

                    elif chapterr == "HEA":
                        if questionn == 1:
                            # qTxt.text = "_____ wellness is an individual's \n ability to meet work demands \n and care for their health."
                            if qTxt.text == "":
                                qTxt.text = "_____ wellness is an individual's \n ability to meet work demands \n and care for their health."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ weighing is a gold standard \n  measure of body composition."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The aim of health related fitness \n is to prevent ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_____ is the ability of the body to \n execute movements with greater \n amplitude or range."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The ability to overcome resistance \n for longer duration is called ____."
                            self.checkans()

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "OSC":
                        if questionn == 1:
                            # qTxt.text = "The SI unit of phase constant is given by _____."
                            if qTxt.text == "":
                                qTxt.text = "The SI unit of phase constant is given by _____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The force acting in simple harmonic motion \n is proportional to _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The phenomenon of increase in amplitude when the \n driving force is close to the natural \n frequency of the oscillator is called \n as ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The number of oscillations per \n unit time is called as ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The smallest interval of time after \n which the motion is repeated is called \n as ____."
                            self.checkans()

                    elif chapterr == "KIN":
                        if questionn == 1:
                            # qTxt.text = "The diatomic molecule is treated as \n a ____ rotator."
                            if qTxt.text == "":
                                qTxt.text = "The diatomic molecule is treated as \n a ____ rotator."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The molecule of _____ gas has three \n translational degrees of freedom."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The gas which satisfies the equation PV = nRT \n at all pressure and temperature is called \n as an ____ gas."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The mean free path decreases with an increase in the \n pressure at a constant temperature of \n the gas.(True/ False)."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The quantity PV/kT represents the \n number of _____ in the gas."
                            self.checkans()

                    elif chapterr == "GRA":
                        if questionn == 1:
                            # qTxt.text = "The weight of an object can be zero \n but the mass of an object can \n never be zero. (True/ False)"
                            if qTxt.text == "":
                                qTxt.text = "The weight of an object can be zero \n but the mass of an object can \n never be zero. (True/ False)"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The value of acceleration due to gravity \n of earth at the equator is less \n than that of the poles due to \n shape and _______ of the Earth."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Force of gravitational attraction \n is least at the _____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "In ____ motion, the total angular \n momentum remains constant."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the point in an orbit where a \n satellite is farthest from the Earth \n called?"
                            self.checkans()

                    elif chapterr == "THE":
                        if questionn == 1:
                            # qTxt.text = "In sublimation of napthalene, maximum \n increase in ______ is observed."
                            if qTxt.text == "":
                                qTxt.text = "In sublimation of napthalene, maximum \n increase in ______ is observed."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Internal energy is the term for the \n total kinetic and protential \n energy of the _____ in a system."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What term describes the change in internal \n energy of a system at constant \n pressure?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is the term for the maximum amount \n of work a system can do as it \n approaches absolute zero?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "One mole of hydrogen gas has the \n highest _____."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "BNP":
                        if questionn == 1:
                            # qTxt.text = "Mineral oil refining is a ____ \n industry."
                            if qTxt.text == "":
                                qTxt.text = "Mineral oil refining is a ____ \n industry."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Contractual work in exchange for salary \n or wages is called _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The term ‘business’ is derived from the \n word _____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "________ sector covers oil refinery \n and sugar mills."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The occupation in which people work for \n others and get remunerated in return is \n known as _____."
                            self.checkans()

                    elif chapterr == "BSE":
                        if questionn == 1:
                            # qTxt.text = "Name the principle in which it is the \n duty of the insured to take steps \n for minimising the loss to the \n insured property."
                            if qTxt.text == "":
                                qTxt.text = "Name the principle in which it is the \n duty of the insured to take steps \n for minimising the loss to the \n insured property."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Policy beneficial for people prefer a \n regular income after a certain age \n is known as _____ policy."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Warehouses that are owned and \n controlled by a company are known \n as _____ warehouses."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The function in which the warehouse \n receives and consolidates goods from \n different plants and dispatches \n them to a single person is called _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "A person who undertakes to \n indemnify is called an ____."
                            self.checkans()

                    elif chapterr == "INT":
                        if questionn == 1:
                            # qTxt.text = "Buying and selling goods and services \n with the objective of earning profit \n is known as _____."
                            if qTxt.text == "":
                                qTxt.text = "Buying and selling goods and services \n with the objective of earning profit \n is known as _____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Trade can be classified into internal \n trade and external trade on the \n basis of geographical _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Purchase and sale of goods and services \n in _______ quantity is referred to as \n wholesale trade."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Mr. A runs a shop and sells \n large quantities of goods \n to various shopkeepers. \n Mr. A is a _____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_____ traders are the ones who do \n not have a fixed place of \n business to operate from."
                            self.checkans()

                    elif chapterr == "GLO":
                        if questionn == 1:
                            # qTxt.text = "The Theory of Absolute Cost Advantage \n is given by _____."
                            if qTxt.text == "":
                                qTxt.text = "The Theory of Absolute Cost Advantage \n is given by _____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Interest payments on loans borrowed abroad \n are recorded in ____ accounts."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Intangible aspect of services in International \n business is known as___ trade."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "A Letter of Credit is required in \n connection with an _____ transaction."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_____ invoice is issued by the exporter \n to importer."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "YOG":
                        if questionn == 1:
                            # qTxt.text = "____ is a very good kriya to \n get rid of nasal allergy."
                            if qTxt.text == "":
                                qTxt.text = "____ is a very good kriya to \n get rid of nasal allergy."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Withdrawal of senses from the \n sensory objects is known as \n _______."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "To stabilise and focus the mind \n on one object, image, \n sound or idea is called ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The purpose of yoga is to attain ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Yoga sutra was given by ____."
                            self.checkans()

                    elif chapterr == "PSY":
                        if questionn == 1:
                            # qTxt.text = "The study of how genes and heredity \n influence behaviour falls under \n which psychological perspective?"
                            if qTxt.text == "":
                                qTxt.text = "The study of how genes and heredity \n influence behaviour falls under \n which psychological perspective?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The behaviorists rejected \n introspection because it was \n too ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The terms “emotion” and “motivation” \n come from the identical Latin \n root ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "When the motive features a biological \n or physiological basis, it’s \n called ___."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Motives are never observed directly; \n but they’re inferred from ____."
                            self.checkans()

                    elif chapterr == "HEA":
                        if questionn == 1:
                            # qTxt.text = "_____ wellness is an individual's \n ability to meet work demands \n and care for their health."
                            if qTxt.text == "":
                                qTxt.text = "_____ wellness is an individual's \n ability to meet work demands \n and care for their health."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ weighing is a gold standard \n  measure of body composition."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The aim of health related fitness \n is to prevent ____."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ is the ability of the body to \n execute movements with greater \n amplitude or range."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The ability to overcome resistance \n for longer duration is called ____."
                            self.checkans()

        elif age == 16:
            if 0 <= preScore <= 3:
                if subject == 1:
                    if chapterr == "AMI":
                        if questionn == 1:
                            # qTxt.text = "An amine with two or more alkyl \n groups does not have a lone pair of \n electron on nitrogen atom. (True/False)"
                            if qTxt.text == "":
                                qTxt.text = "An amine with two or more alkyl \n groups does not have a lone pair of \n electron on nitrogen atom. (True/False)"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Phosphine has a lower melting point than Amine. (True/False)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is the geometry of ammonia \n molecule?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Amines are derivatives of ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the most basic aromatic amine’s \n common name?"
                            self.checkans()

                    elif chapterr == "SOL":
                        if questionn == 1:
                            # qTxt.text = "What is pumice stone an example of?"
                            if qTxt.text == "":
                                qTxt.text = "What is pumice stone an example of?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What type of solution is cranberry \n glass?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A supersaturated solution is not a \n metastable solution. (True/False)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What is an alloy of copper and zinc \n called?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The solution of mercury with other metals \n is called amalgam. (True/False)"
                            self.checkans()

                elif subject == 2:
                    if chapterr == "DIV":
                        if questionn == 1:
                            # qTxt.text = "Which phylum of animals is also called \n 'Flatworm'?"
                            if qTxt.text == "":
                                qTxt.text = "Which phylum of animals is also called \n 'Flatworm'?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What is the exclusive marine phylum?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Arthropod means ____ legs."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The excretory system in annelids is \n consisted of tubes called?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the phylum of Octopus?"
                            self.checkans()

                    elif chapterr == "CEL":
                        if questionn == 1:
                            # qTxt.text = "___ is mitochondria where the outer \n membranehas been removed, by \n keeping the inner membrane intact."
                            if qTxt.text == "":
                                qTxt.text = "___ is mitochondria where the outer \n membranehas been removed, by \n keeping the inner membrane intact."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The RNA is synthesized by ______."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Polythene chromosomes are found because \n of ___."
                            self.checkans()


                        elif questionn == 4:
                            qTxt.text = "Animal cells are interconnected by ___."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Which is the simplest amino acid?"
                            self.checkans()

                elif subject == 3:
                    if chapterr == "COM":
                        if questionn == 1:
                            # qTxt.text = "When an error occurs during the execution \n of a program, an exception is \n said to have been ____."
                            if qTxt.text == "":
                                qTxt.text = "When an error occurs during the execution \n of a program, an exception is \n said to have been ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "___ is a python object that \n represents an error."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "On encountering a ____ error, the \n interpreter does not execute the \n program unless we rectify errors, \n save and rerun the programs."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "If l=[11,22,33,44], then \n output of print(len(l)) will \n be?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Pow() function belongs to which \n library?"
                            self.checkans()

                    elif chapterr == "CNE":
                        if questionn == 1:
                            # qTxt.text = "Medium or path through which \n data or message travels \n between source and destination \n is ___."
                            if qTxt.text == "":
                                qTxt.text = "Medium or path through which \n data or message travels \n between source and destination \n is ___."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ is known as intelligent \n hub and provides packet \n filtering."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The device that regenerates a \n signal being transmitted \n on the network is called ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "State Bank of India is an example \n of __.(Short Form only)"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_____ in computer network is system \n designed to prevent unauthorized \n access."
                            self.checkans()

            elif 4 <= preScore <= 6:
                if subject == 1:
                    if chapterr == "AMI":
                        if questionn == 1:
                            # qTxt.text = "Ammonolysis is a type of ____ \n substitution reaction."
                            if qTxt.text == "":
                                qTxt.text = "Ammonolysis is a type of ____ \n substitution reaction."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ group is the substituent group \n in 2-methylbezebamine."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "P-tert-Butyl aniline is a tertiary \n amine. (True/False)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Ammonolysis is a reaction between an alkyl \n halide and most preferably an ____ \n solution of NH3."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Benzylamine is the IUPAC name of aniline. \n (True/False)"
                            self.checkans()

                    elif chapterr == "SOL":
                        if questionn == 1:
                            # qTxt.text = "In how number of many ways can the \n concentration of a solution be \n expressed?"
                            if qTxt.text == "":
                                qTxt.text = "In how number of many ways can the \n concentration of a solution be \n expressed?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "“The process of dissolution of solute in the \n solvent takes place even after \n saturation.” Is this True \n or False?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "What is defined as the maximum \n concentration of dissolved \n solute in a solvent?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What does the unit ‘mmole/kg’ \n represent?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is a solution called when the \n concentration of the solute equals its \n solubility in the solvent?"
                            self.checkans()

                    elif chapterr == "BIO":
                        if questionn == 1:
                            # qTxt.text = "Glucose is an aldohexose. \n (True/False)"
                            if qTxt.text == "":
                                qTxt.text = "Glucose is an aldohexose. \n (True/False)"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The α-D-glucose and β-D-glucose isomers \n of glucose are known as ____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "All monosaccharides are reducing sugars. \n (True/False)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Raffinose is an example of ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "RNA lacks the nitrogen base of \n _______."
                            self.checkans()

                elif subject == 2:
                    if chapterr == "DIV":
                        if questionn == 1:
                            # qTxt.text = "What is the class name for warm-blooded \n animals with feathers?"
                            if qTxt.text == "":
                                qTxt.text = "What is the class name for warm-blooded \n animals with feathers?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Algae come under which category?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Protista contains which kind of \n organisms?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The diversity of all life forms \n is called as?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Who classified the animals according to \n the place they lived - on whether they \n live on land, water or air?"
                            self.checkans()

                    elif chapterr == "CEL":
                        if questionn == 1:
                            # qTxt.text = "This jellylike substance inside the \n plasma membrane in which all cell \n organelles are floating is the ____."
                            if qTxt.text == "":
                                qTxt.text = "This jellylike substance inside the \n plasma membrane in which all cell \n organelles are floating is the ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Smooth muscles are also called involuntary \n muscles. (True/ False)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "______ are cylindrical structures that are composed \n of tubulin."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ octamer is an 8 protein complex that \n is found at the centre of the core \n particles of the nucleosome."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Sodium and potassium pumps are examples \n of ______ transport."
                            self.checkans()

                    elif chapterr == "PLA":
                        if questionn == 1:
                            # qTxt.text = "Main source of elements for nitrate \n reductase is ferredoxin which is \n present in ____."
                            if qTxt.text == "":
                                qTxt.text = "Main source of elements for nitrate \n reductase is ferredoxin which is \n present in ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "If a cell swells, after being placed \n in solution, the solution is called \n _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Name the physical process involved \n in the release of molecular \n oxygen from leaves."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The most abundant protein in the \n animal world is ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "In the rainy season, doors get \n swelled up due to ____."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "COM":
                        if questionn == 1:
                            # qTxt.text = "Which point can be considered as \n difference between string \n and list?"
                            if qTxt.text == "":
                                qTxt.text = "Which point can be considered as \n difference between string \n and list?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Document created in notepad is an \n example of a ____ file."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "An image is a type of ____ file."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Each try block must always be \n followed by at least one \n block that is either \n except or a finally block. \n (True/False)"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Exceptions are caught in the \n ____ block."
                            self.checkans()

                    elif chapterr == "CNE":
                        if questionn == 1:
                            # qTxt.text = "Medium or path through which \n data or message travels \n between source and destination \n is ___."
                            if qTxt.text == "":
                                qTxt.text = "Medium or path through which \n data or message travels \n between source and destination \n is ___."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "____ is known as intelligent \n hub and provides packet \n filtering."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The device that regenerates a \n signal being transmitted \n on the network is called ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "State Bank of India is an example \n of __.(Short Form only)"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "_____ in computer network is system \n designed to prevent unauthorized \n access."
                            self.checkans()

                    elif chapterr == "DAT":
                        if questionn == 1:
                            # qTxt.text = "Data is a collection of ________ facts \n which have not been processed to \n reveal useful information."
                            if qTxt.text == "":
                                qTxt.text = "Data is a collection of ________ facts \n which have not been processed to \n reveal useful information."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "A table cannot have more than \n one UNIQUE keys. (True/False)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "In RDBMS, R represents ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ key is used to represent the \n relationship between tables."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "A database management system is \n an ____ type of software."
                            self.checkans()

            elif 7 <= preScore <= 10:
                if subject == 1:
                    if chapterr == "AMI":
                        if questionn == 1:
                            # qTxt.text = "Which gas is produced when ethanamine \n reacts with nitrous acid?"
                            if qTxt.text == "":
                                qTxt.text = "Which gas is produced when ethanamine \n reacts with nitrous acid?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The reaction between methylamine and \n hydrogen  iodide results in the \n formation of a what colour solid? (Name \n only the colour)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Amines are generally _____ in nature."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "_____ odour is the characteristic odour \n of relatively lower aliphatic amines."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Hoffmann bromanide degradation reaction \n is used for preparing ____ amines."
                            self.checkans()

                    elif chapterr == "SOL":
                        if questionn == 1:
                            # qTxt.text = "Ideal solutions do not form \n azeotropes. (True/False)"
                            if qTxt.text == "":
                                qTxt.text = "Ideal solutions do not form \n azeotropes. (True/False)"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "What phenomenon occurs when a solution’s \n equilibrium vapour pressure equals the \n surrounding atmospheric pressure?"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A solution which does not obey \n Raoult’s law is called a non-ideal \n solution. (True/False)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What characteristic of water accounts \n for its unique properties as a \n solvent?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is a substance that cannot be broken \n down into simpler substances by chemical \n means?"
                            self.checkans()

                    elif chapterr == "BIO":
                        if questionn == 1:
                            # qTxt.text = "Fructose exists as both pyranose \n and furanose structures. \n (True/False)"
                            if qTxt.text == "":
                                qTxt.text = "Fructose exists as both pyranose \n and furanose structures. \n (True/False)"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Fructose is commonly known as ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A solution having equal amount of \n D-glucose and D-fructose is \n called ____ sugar."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Glucose can exist in both a \n straight chain and ring form. \n (True/False)"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Lysine is an example of a polar \n but uncharged amino acid. \n (Replace Lysine)"
                            self.checkans()

                    elif chapterr == "ECH":
                        if questionn == 1:
                            # qTxt.text = "Who invented the first fuel cell?"
                            if qTxt.text == "":
                                qTxt.text = "Who invented the first fuel cell?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Galvani and Volta invented \n the _______ cell."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A galvanic cell converts electrical \n energy into chemical energy. \n (True/False)"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "In a fuel cell, which of the following \n can be utilized as a fuel?"
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "An electrochemical cell can only \n convert electrical energy to \n chemical energy. (True/False)"
                            self.checkans()

                elif subject == 2:
                    if chapterr == "DIV":
                        if questionn == 1:
                            # qTxt.text = "________ hierarchy refers to stepwise arrangement \n of all categories for classification of \n animals and plants."
                            if qTxt.text == "":
                                qTxt.text = "________ hierarchy refers to stepwise arrangement \n of all categories for classification of \n animals and plants."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Phylum and Genus have real existence. \n (True/ False)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "The label of a _________ sheet does not \n carry information on the height of \n the plant."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "The mode of nutrition in fungi can be \n saprotrophic or ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "What is the taxonomic group that \n includes jawless fish?"
                            self.checkans()

                    elif chapterr == "CEL":
                        if questionn == 1:
                            # qTxt.text = "Microfilaments are composed of a \n protein called ____."
                            if qTxt.text == "":
                                qTxt.text = "Microfilaments are composed of a \n protein called ____."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "A plant cell wall is mainly composed \n of _____."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "A cell without a cell wall is termed \n as ______."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Which cell organelle is involved in \n apoptosis?"
                            self.checkans()

                        elif questionn == 5:

                            qTxt.text = "Distribution of intrinsic proteins in \n the plasma membrane is ____."
                            self.checkans()

                    elif chapterr == "PLA":
                        if questionn == 1:
                            # qTxt.text = "Bordered pits are found in _____ wall."
                            if qTxt.text == "":
                                qTxt.text = "Bordered pits are found in _____ wall."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Bicollateral bundles are found in the \n stem of sunflower. (True/ False)."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Wound healing in plants is initiated \n by _____ meristem."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Name aa tissue that does not \n contain lignin."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The waxy substance associated with the \n wall of the cork cell is ____."
                            self.checkans()

                    elif chapterr == "BST":
                        if questionn == 1:
                            # qTxt.text = "The non-excitable, variously shaped, \n and found between neurons are \n ____ cells."
                            if qTxt.text == "":
                                qTxt.text = "The non-excitable, variously shaped, \n and found between neurons are \n ____ cells."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "Cells that release heparin and histamine \n into the blood are ___."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "Skin has dense irregular ______ \n tissue."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "What are the glands referred to as when \n secretary granules leave cells by \n exocytosis with no loss of other \n cellular material."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "The large amoeboid cells found in areolar \n tissue and are also part of our \n innate immune system are known as \n ______."
                            self.checkans()

                elif subject == 3:
                    if chapterr == "COM":
                        if questionn == 1:
                            # qTxt.text = "Which function is used to read \n data from a binary file?"
                            if qTxt.text == "":
                                qTxt.text = "Which function is used to read \n data from a binary file?"
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "The variable declared inside the \n function is called a ___ \n variable."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "To which module does the load() function belong to?"
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "In python function, the function \n calling another function is known \n as ____."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "________ forces an expression to be \n converted into specific type."
                            self.checkans()

                    elif chapterr == "CNE":
                        if questionn == 1:
                            # qTxt.text = "Name a device that forwards data \n packet from one network to \n another."
                            if qTxt.text == "":
                                qTxt.text = "Name a device that forwards data \n packet from one network to \n another."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "___ looks like a legitimate software \n which once installed acts like \n a virus."
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "______ is used in the network \n to connect LANs."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "Unguided transmission can also be \n referred to as _____ media."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "Bandwidth is measured in ____."
                            self.checkans()

                    elif chapterr == "DAT":
                        if questionn == 1:
                            # qTxt.text = "Data is a collection of ________ facts \n which have not been processed to \n reveal useful information."
                            if qTxt.text == "":
                                qTxt.text = "Data is a collection of ________ facts \n which have not been processed to \n reveal useful information."
                                self.checkans()
                            else:
                                self.checkans()

                        elif questionn == 2:
                            qTxt.text = "A table cannot have more than \n one UNIQUE keys. (True/False)"
                            self.checkans()

                        elif questionn == 3:
                            qTxt.text = "In RDBMS, R represents ___."
                            self.checkans()

                        elif questionn == 4:
                            qTxt.text = "____ key is used to represent the \n relationship between tables."
                            self.checkans()

                        elif questionn == 5:
                            qTxt.text = "A database management system is \n an ____ type of software."

                            self.checkans()

    def bqconvertlang(self):
        bqTxt = self.root.get_screen('beforequestionsscreen').ids.bqTxt
        bqNo = self.root.get_screen('beforequestionsscreen').ids.bqNo
        bqBtn1 = self.root.get_screen('beforequestionsscreen').ids.bqBtn1
        bqBtn2 = self.root.get_screen('beforequestionsscreen').ids.bqBtn2
        bqBtn3 = self.root.get_screen('beforequestionsscreen').ids.bqBtn3
        bqBtn4 = self.root.get_screen('beforequestionsscreen').ids.bqBtn4
        bqNxtBtn = self.root.get_screen('beforequestionsscreen').ids.bgNxtBtn
        labelforTxt = self.root.get_screen('beforequestionsscreen').ids.labelforTxt
        age = int(self.stored_age)
        bqquestionno = int(self.bqquestionno)
        langg = self.stored_lang

        if langg == "English":
            pass
        elif langg == "Hindi":
            selLang = "hi"
            bqTxt.text = self.aztranslate_text(bqTxt.text, selLang)
            bqNo.text = self.aztranslate_text(bqNo.text, selLang)
            bqBtn1.text = self.aztranslate_text(bqBtn1.text, selLang)
            bqBtn2.text = self.aztranslate_text(bqBtn2.text, selLang)
            bqBtn3.text = self.aztranslate_text(bqBtn3.text, selLang)
            bqBtn4.text = self.aztranslate_text(bqBtn4.text, selLang)
            bqNxtBtn.text = self.aztranslate_text(bqNxtBtn.text, selLang)
            labelforTxt.text = self.aztranslate_text(labelforTxt.text, selLang)
        elif langg == "Tamil":
            selLang = "ta"
            bqTxt.text = self.aztranslate_text(bqTxt.text, selLang)
            bqNo.text = self.aztranslate_text(bqNo.text, selLang)
            bqBtn1.text = self.aztranslate_text(bqBtn1.text, selLang)
            bqBtn2.text = self.aztranslate_text(bqBtn2.text, selLang)
            bqBtn3.text = self.aztranslate_text(bqBtn3.text, selLang)
            bqBtn4.text = self.aztranslate_text(bqBtn4.text, selLang)
            bqNxtBtn.text = self.aztranslate_text(bqNxtBtn.text, selLang)
            labelforTxt.text = self.aztranslate_text(labelforTxt.text, selLang)

    def setbeforequestions(self):
        bqTxt = self.root.get_screen('beforequestionsscreen').ids.bqTxt
        bqNo = self.root.get_screen('beforequestionsscreen').ids.bqNo
        bqBtn1 = self.root.get_screen('beforequestionsscreen').ids.bqBtn1
        bqBtn2 = self.root.get_screen('beforequestionsscreen').ids.bqBtn2
        bqBtn3 = self.root.get_screen('beforequestionsscreen').ids.bqBtn3
        bqBtn4 = self.root.get_screen('beforequestionsscreen').ids.bqBtn4
        bqimg = self.root.get_screen('beforequestionsscreen').ids.bqImg
        #bgNxtBtn = self.root.get_screen('beforequestionsscreen').ids.bgNxtBtn
        labelforTxt = self.root.get_screen('beforequestionsscreen').ids.labelforTxt
        age = int(self.stored_age)
        bqquestionno = int(self.bqquestionno)
        print("setbeforequestions is here")
        if bqquestionno == 0:
            labelforTxt.opacity = 1
            self.bqquestionno += 1
            bqBtn1.opacity = 0
            bqBtn2.opacity = 0
            bqBtn3.opacity = 0
            bqBtn4.opacity = 0
            #bqimg.opacity = 0
        if 13 <= age <= 14:
            if bqquestionno == 1:
                print("Another step done")
                bqTxt.text = "If the perimeter of a rectangle is 28 cm, and its length is 7 cm, what is the width?"
                bqNo.text = "Q1/10"
                bqBtn1.text = "A) 3cm"
                bqBtn2.text = "B) 5cm"
                bqBtn3.text = "C) 7cm"
                bqBtn4.text = "D) 14 cm"
                self.bqquestionno += 1
                labelforTxt.opacity = 0
                #bqimg.opacity = 0.175
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqimg.source = "bqimg2.png"
                #bqBtn4.opacity = 1
            elif bqquestionno == 2:
                bqTxt.text = "What is the process by which plants make their own food using sunlight?"
                bqNo.text = "Q2/10"
                bqBtn1.text = "A) Respiration"
                bqBtn2.text = "B) Photosynthesis"
                bqBtn3.text = "C) Transpiration"
                bqBtn4.text = "D) Fermentation"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg3.png"
            elif bqquestionno == 3:
                bqTxt.text = "Who was the first President of India?"
                bqNo.text = "Q3/10"
                bqBtn1.text = "A) Jawaharlal Nehru"
                bqBtn2.text = "B) Dr. B.R. Ambedkar"
                bqBtn3.text = "C) Sardar Vallabhbhai Patel"
                bqBtn4.text = "D) Dr. Rajendra Prasad"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg4.jpg"
            elif bqquestionno == 4:
                bqTxt.text = "If a triangle has sides of lengths 3 cm, 4 cm, and 5 cm, what type of triangle is it?"
                bqNo.text = "Q4/10"
                bqBtn1.text = "A) Equilateral"
                bqBtn2.text = "B) Isoceles"
                bqBtn3.text = "C) Scalene"
                bqBtn4.text = "D) Right-angled"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg5.jpg"
            elif bqquestionno == 5:
                bqTxt.text = "What is the largest planet in our solar system?"
                bqNo.text = "Q5/10"
                bqBtn1.text = "A) Earth"
                bqBtn2.text = "B) Jupiter"
                bqBtn3.text = "C) Saturn"
                bqBtn4.text = "D) Mars"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                #bqimg.opacity = 0
                self.bqquestionno += 1
                labelforTxt.opacity = 0
                bqimg.source = "bqimg6.jpg"
            elif bqquestionno == 6:
                bqTxt.text = "Which ocean is the largest in terms of both area and volume?"
                bqNo.text = "Q6/10"
                bqBtn1.text = "A) Indian Ocean"
                bqBtn2.text = "B) Atlantic Ocean"
                bqBtn3.text = "C) Southern Ocean"
                bqBtn4.text = "D) Pacific Ocean"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                #bqimg.opacity = 0
                self.bqquestionno += 1
                labelforTxt.opacity = 0
                bqimg.source = "bqimg7.jpg"
            elif bqquestionno == 7:
                bqTxt.text = "If a square has an area of 25 square units, what is the length of one side?"
                bqNo.text = "Q7/10"
                bqBtn1.text = "A) 3 units"
                bqBtn2.text = "B) 5 units"
                bqBtn3.text = "C) 6 units"
                bqBtn4.text = "D) 25 units"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                #bqimg.opacity = 0
                self.bqquestionno += 1
                labelforTxt.opacity = 0
                bqimg.source = "bqimg8.jpg"
            elif bqquestionno == 8:
                bqTxt.text = "What is the function of the human heart?"
                bqNo.text = "Q8/10"
                bqBtn1.text = "A) Pumping blood"
                bqBtn2.text = "B) Digestion"
                bqBtn3.text = "C) Filtering waste"
                bqBtn4.text = "D) Storing nutrients"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                bqimg.source = "bqimg9.jpg"
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
            elif bqquestionno == 9:
                bqTxt.text = "In India, who is considered the head of the state?"
                bqNo.text = "Q9/10"
                bqBtn1.text = "A) President"
                bqBtn2.text = "B) Prime Minister"
                bqBtn3.text = "C) Monarch"
                bqBtn4.text = "D) Chief Justice"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg10.jpg"
            elif bqquestionno == 10:
                bqTxt.text = "Which of the following is an angle equal to 1/4 of the sum of angles of a quadrilateral?"
                bqNo.text = "Q10/10"
                bqBtn1.text = "A) 45 degrees"
                bqBtn2.text = "B) 60 degrees"
                bqBtn3.text = "C) 90 degrees"
                bqBtn4.text = "D) 120 degrees"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg11.png"
        if 15 <= age <= 16:
            if bqquestionno == 1:
                print("Anothera step done")
                bqTxt.text = "What is the molecular formula of glucose?"
                bqNo.text = "Q1/10"
                bqBtn1.text = "A) C5H12O5"
                bqBtn2.text = "B) C6H12O5"
                bqBtn3.text = "C) C6H10O6"
                bqBtn4.text = "D) C6H12O6"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                bqimg.source = "bqimg2.png"
                labelforTxt.opacity = 0
            elif bqquestionno == 2:
                bqTxt.text = "Who was the first woman Prime Minister of a country?"
                bqNo.text = "Q2/10"
                bqBtn1.text = "A) Angela Merkel"
                bqBtn2.text = "B) Margaret Thatcher"
                bqBtn3.text = "C) Indira Gandhi"
                bqBtn4.text = "D) Golda Meir"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                bqimg.source = "bqimg3.png"
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
            elif bqquestionno == 3:
                bqTxt.text = "If a circle has a diameter of 10 cm, what is its area (in square cm)?"
                bqNo.text = "Q3/10"
                bqBtn1.text = "A) 25π"
                bqBtn2.text = "B) 50π"
                bqBtn3.text = "C) 100π"
                bqBtn4.text = "D) 200π"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg4.jpg"
            elif bqquestionno == 4:
                bqTxt.text = "What is the value of 4^3 + 2^4?"
                bqNo.text = "Q4/10"
                bqBtn1.text = "A) 56"
                bqBtn2.text = "B) 64"
                bqBtn3.text = "C) 72"
                bqBtn4.text = "D) 80"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg5.jpg"
            elif bqquestionno == 5:
                bqTxt.text = "Who discovered the structure of DNA?"
                bqNo.text = "Q5/10"
                bqBtn1.text = "A) Watson and Crick"
                bqBtn2.text = "B) Louis Pasteur"
                bqBtn3.text = "C) Charles Darwin"
                bqBtn4.text = "D) Gregor Mendel"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                bqimg.source = "bqimg6.jpg"
                labelforTxt.opacity = 0
            elif bqquestionno == 6:
                bqTxt.text = "What is the value of √(9) + √(16)?"
                bqNo.text = "Q6/10"
                bqBtn1.text = "A) 5"
                bqBtn2.text = "B) 6"
                bqBtn3.text = "C) 7"
                bqBtn4.text = "D) 8"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                bqimg.source = "bqimg7.jpg"
                labelforTxt.opacity = 0
            elif bqquestionno == 7:
                bqTxt.text = "What was the ancient name of Sri Lanka?"
                bqNo.text = "Q7/10"
                bqBtn1.text = "A) Ceylon"
                bqBtn2.text = "B) Burma"
                bqBtn3.text = "C) Maldives"
                bqBtn4.text = "D) Seychelles"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg8.jpg"
            elif bqquestionno == 8:
                bqTxt.text = "Solve the equation: 3x - 7 = 14."
                bqNo.text = "Q8/10"
                bqBtn1.text = "A) x = 7"
                bqBtn2.text = "B) x = 5"
                bqBtn3.text = "C) x = 7.67"
                bqBtn4.text = "D) x = 8"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg9.jpg"
            elif bqquestionno == 9:
                bqTxt.text = "Who is known as the Father of the Indian Constitution?"
                bqNo.text = "Q9/10"
                bqBtn1.text = "A) Mahatma Gandhi"
                bqBtn2.text = "B) Jawaharlal Nehru"
                bqBtn3.text = "C) Dr. B.R. Ambedkar"
                bqBtn4.text = "D) Sardar Vallabhbhai Patel"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                labelforTxt.opacity = 0
                bqimg.source = "bqimg10.jpg"
            elif bqquestionno == 10:
                bqTxt.text = "Which planet is known as the Red Planet?"
                bqNo.text = "Q10/10"
                bqBtn1.text = "A) Venus"
                bqBtn2.text = "B) Mars"
                bqBtn3.text = "C) Jupiter"
                bqBtn4.text = "D) Saturn"
                bqBtn1.opacity = 1
                bqBtn2.opacity = 1
                bqBtn3.opacity = 1
                bqBtn4.opacity = 1
                self.bqquestionno += 1
                #bqimg.opacity = 0
                bqimg.source = "bqimg11.png"
                labelforTxt.opacity = 0
    """async def translate_chunk_async(self, chunk, lang):
        try:
            translator = Translator(to_lang=lang)
            translation = await asyncio.to_thread(translator.translate, chunk)
            return translation
        except Exception as translation_error:
            print(f"Error during translation: {translation_error}")
            return ''

    def translate_text_async(self, text, lang):
        loop = asyncio.get_event_loop()
        tasks = [self.translate_chunk_async(chunk, lang) for chunk in text.split()]
        translated_chunks = loop.run_until_complete(asyncio.gather(*tasks))
        return ' '.join(translated_chunks)

    def convert_to_speech(self):
        print("here kid")
        try:
            with open(self.mastervariabletxtupdated, 'r') as file:
                lines = file.readlines()
                print(lines)

            # Join the lines into a single string
            text_to_convert = ' '.join(lines)
            langgg = ""

            if self.stored_lang == "English":
                langgg = "en"
            elif self.stored_lang == "Hindi":
                langgg = "hi"
            elif self.stored_lang == "Tamil":
                langgg = "ta"

            selected_language = langgg

            if text_to_convert and selected_language:
                translated_text = self.translate_text_async(text_to_convert, selected_language)

                tts = gTTS(text=translated_text, lang=selected_language)
                tts.save(self.mastervariablemp3updated)
                print(self.mastervariablemp3updated + " saved")
                print("Conversion done")
        except Exception as e:
            print(f"Error in convert_to_speech: {e}")"""

    def image_to_video_file_name(self):
        current_screen = self.root.current_screen
        if current_screen == "science_poor_nine":
            Illuminat.name_video_clip = "science9poor.ch1.mp4"

    """def image_to_video(self):
        clips = []
        clip1 = ImageClip('images/image_1.png').set_duration(2)
        clip2 = ImageClip('images/image_2.png').set_duration(3)
        clip3 = ImageClip('images/image_3.png').set_duration(4)
        clips.append(clip1)
        clips.append(clip2)
        clips.append(clip3)
        video_clip = concatenate_videoclips(clips, method='compose')
        video_clip.write_videofile("clip1.mp4", fps=24, remove_temp=True, codec="libx264", audio_codec="aac")"""

    """def which_screen_science(self):
        if Illuminat.users_ref is not None:
            doc = Illuminat.users_ref.get()
            if doc.exists:
                user_score = doc.to_dict().get('score', '')
                user_email = doc.to_dict().get('email', '')
                print("doc exists correeeecttt")

                if 0 <= user_score <= 3:
                    Builder.load_string(kv_sciencepoor_9)
                    user_score_int = int(user_score)
                    print(user_score_int)
                    print(user_email)
                elif 4 <= user_score <= 6:
                    self.manager.current = 'signupdetails'
                elif 7 <= user_score <= 10:
                    self.manager.current = 'main'
        else:
            print("Users_ref is none")"""

    def check_file_permissions(file_path_video):
        if os.access(file_path_video, os.R_OK):
            print(f"Read perms for {file_path_video} is granted")
        else:
            print(f"Read perms for {file_path_video} ain't granted")

    def video_from_text(self):
        video = Video(source="scienceclass9poor.mp4")
        print("Current working directory", os.getcwd())
        print("Files in current directory", os.listdir())
        video.state = "play"
        video.options = {'eos': 'loop'}
        # video .allow_stretch = True

        return video

    def video_maker(self):
        layout = FloatLayout()
        video = Video(source='scienceclass9poor.mp4', state='play')
        video.allow_stretch = True
        layout.add_widget(video)

        return layout

    """def load_video(self):
        video_layout = VideoLayout()

        video = Video(source='scienceclass9top.mp4')
        video.state = 'play'
        video.options = {'eos': 'loop'}
        video.allow_stretch = True

        video_layout.add_widget(video)"""

    def video_science_poor_nine(self):
        video_path = 'scienceclass9poor.mp4'  # Replace with your video file path
        self.root.load_video(video_path)
def illuminatfunc():
    Illuminat().run()
if __name__ == "__main__":
    illuminatfunc()
