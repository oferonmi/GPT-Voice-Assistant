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
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[-1].id)

def sr_transcribe_audio_to_text(file_name):
  recognizer = sr.Recognizer()
  with sr.AudioFile(file_name) as source:
    audio = recognizer.record(source)
  try:
    return recognizer.recognize_google(audio)
  except:
    print("Ah, let's give this another try.")


def whisper_transcribe_audio_to_text(file_name):
  audio_file = open(file_name, "rb")
  try:
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]
  except:
    print("Ah, let's give this another try.")


def generate_prompt_response(prompt):
  response = openai.Completion.create(engine="text-davinci-003",
                                      prompt=prompt,
                                      max_tokens=4000,
                                      n=1,
                                      stop=None,
                                      temperature=0.5)
  return response["choices"][0]["text"]


def generate_chat_response(msg):
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
          {"role": "user", "content": msg}
      ]
  )
  return response.choices[0].message["content"]
  # return response["choices"][0]["message"]["content"]


def speak(text):
  engine.say(text)
  engine.runAndWait()


# main
def main(gpt_version): 
  # Input - gpt_version takes valid values of 'gpt-3' and 'gpt-3.5'
  while True:
    # TODO find and fix cause of the ALSA dumps
    with noalsaerr():  # suppress ALSA lib dumps for now. remove when dump issues are fixed
      recognizer = sr.Recognizer()
      # initial prompt ('Hey! Kai' in this case) to begin recording
      print("Say 'Hey Kai' to record your question...")
      time.sleep(1)
      with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
          transcription = recognizer.recognize_google(audio)
          #if transcription.lower == "lex":

          print("I am listening. Ask your question ...")
          speak("Yes. Ask your question")

          # record audio
          in_audio_filename = "input.wav"

          with sr.Microphone() as source:
            source.pause_threshold = 1
            recognizer.adjust_for_ambient_noise(source)
            
            audio = recognizer.listen(source,
                                      phrase_time_limit=None,
                                      timeout=None)  

            with open(in_audio_filename, "wb") as f:
              f.write(audio.get_wav_data())

          # transcribe audio to text
          # text = sr_transcribe_audio_to_text(in_audio_filename)
          text = whisper_transcribe_audio_to_text(in_audio_filename)
          if text:
            print("You said: '{}'.".format(text))

            # generate response
            if gpt_version == "gpt-3":
              response = generate_prompt_response(text)
            elif gpt_version == "gpt-3.5":
              response = generate_chat_response(text)

            print("GPT response: {}".format(response))

            #read out response
            speak(response)

        except sr.RequestError: 
          print("API unavailable")

        except sr.UnknownValueError:
          print("Unable to recognize speech")
          speak("I could not hear you.")

        # except sr.RequestError:  # Exception as e:
        #   print("An error occured: {}".format(e))
    # TODO create way to end question and answer loop smoothly


if __name__ == "__main__":
  main("gpt-3") # change parameter to gpt-3.5 to use the latest gpt-3.5-turbo model
