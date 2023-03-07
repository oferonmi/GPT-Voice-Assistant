import openai
import pyttsx3 as tts
import speech_recognition as sr
import time

from py_error_handler import noalsaerr # to suppress ALSA lib dumps

import os

from dotenv import load_dotenv
load_dotenv() # load environment variable from .env file

# get OpenAI API key
openai.api_key =  os.environ['OPENAI_API_KEY'] # os.getenv("OPENAI_API_KEY")

# text-to-speech engine instance
engine = tts.init()


def transcribe_audio_to_text(file_name):
  recognizer = sr.Recognizer()
  with sr.AudioFile(file_name) as source:
    audio = recognizer.record(source)
  try:
    return recognizer.recognize_google(audio)
  except:
    print("Ah, let's give this another try.")


def generate_response(prompt):
  response = openai.Completion.create(engine="text-davinci-003",
                                      prompt=prompt,
                                      max_tokens=4000,
                                      n=1,
                                      stop=None,
                                      temperature=0.5)
  return response["choices"][0]["text"]


def speak(text):
  engine.say(text)
  engine.runAndWait()


def main(): 
  while True:
    # TODO find and fix cause for the dumps
    with noalsaerr():  # suppress ALSA lib dumps for now. remove when dump issues are fixed
      recognizer = sr.Recognizer()
      # initial prompt ('Hey! Kai' in this case) to begin recording
      print("Say 'Hey Kai' to record your question...")
      #time.sleep(2)
      with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
          transcription = recognizer.recognize_google(audio)
          #if transcription.lower == "lex":
          # record audio
          in_audio_filename = "input.wav"
          print("I am listening. Ask your question ...")
          with sr.Microphone() as source:
            source.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source,
                                      phrase_time_limit=None,
                                      timeout=None)
            with open(in_audio_filename, "wb") as f:
              f.write(audio.get_wav_data())

          # transcribe audio to text
          text = transcribe_audio_to_text(in_audio_filename)
          if text:
            print("You said: '{}'.".format(text))

            # generate response
            response = generate_response(text)
            print("GPT-3 response: {}".format(response))

            #read out response
            speak(response)

        except sr.RequestError: 
          print("API unavailable")

        except sr.UnknownValueError:
          print("Unable to recognize speech")

        # except sr.RequestError:  # Exception as e:
        #   print("An error occured: {}".format(e))


if __name__ == "__main__":
  main()
