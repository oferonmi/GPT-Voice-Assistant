import openai
import pyttsx3 as tts
from gtts import gTTS
import torch
# from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan, set_seed
import speech_recognition as sr
from pygame import mixer
import time
from py_error_handler import noalsaerr # to suppress ALSA lib dumps
import os
import requests
import random
import json
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv() 

# get OpenAI API key
openai.api_key =  os.environ['OPENAI_API_KEY'] 
# get eleven labs API key
elevenlabs_api_key = os.environ['ELEVENLABS_API_KEY']
# get fastsppech API token from huggingface
hf_api_token = os.environ['HF_API_TOKEN']

# activate (Tset to True) or deactivate (set to False) sound that play in idle sessions
activate_idle_state_sound = True 

# configure system response context and keep track of conversation thread
msg_thread = [
    {"role": "system", "content": "you are a very knowlegable assistant. Explain using first principles like physicist Richard Feynmann."},
]

# initialize module for loading and playing sounds
mixer.init()

# text-to-speech engine instance
tts_engine = tts.init() # TODO add a much smoother speech synthesizer 

# functions for transcribing sound from file to text
def sr_transcribe(file_name):
  recognizer = sr.Recognizer()
  with sr.AudioFile(file_name) as source:
    audio_data = recognizer.record(source)
  try:
    return recognizer.recognize_google(audio_data)
  except:
    print("Ah, let's give this another try.")

def whisper_transcribe(file_name):
  audio_data= open(file_name, "rb")
  transcript = openai.Audio.transcribe("whisper-1", audio_data)
  return transcript["text"]


# functions using OpenAI API to generate reponse to user query
def get_prompt_response(prompt):
  response = openai.Completion.create(engine="text-davinci-003",
                                      prompt=prompt,
                                      max_tokens=4000,
                                      n=1,
                                      stop=None,
                                      temperature=0.5)
  return response["choices"][0]["text"]

def get_chat_response(messages):
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
  )
  return response["choices"][0]["message"]["content"]


# fetches updated transcript for each session
def get_transcript(msg_thread):
  # format message thread
    chat_transcript = ""
    for message in msg_thread:
        if message["role"] != "system":
            chat_transcript += message["role"] + \
                ": " + message["content"] + "\n\n"

    return chat_transcript


# functions for text-to-speech synthesis
def pyttsx3_tts(text):
  tts_engine.say(text)
  tts_engine.runAndWait()

# TODO issues with incomplete and slow text read out
def gTranslate_tts(text):
  tts = gTTS(text, lang="en", tld="co.uk")
  tts.save("out.mp3")
  play_sound("out.mp3") #os.system("mpg123 out.mp3") 

def elevenlabs_tts(text):
  # get list of eleven labs voices
  response = requests.get('https://api.elevenlabs.io/v1/voices', 
                        headers={
                          'accept': 'application/json',
                          'xi-api-key': elevenlabs_api_key,
                        }
                      )
  resp_jdata=json.loads(response.content)
 
  # randomly pick one the premade voices by eleven labs
  v_id = random.randrange(0, len(resp_jdata["voices"])-1, 1)
  voice_id = resp_jdata["voices"][v_id]["voice_id"]

  # configure voice and feed text to remote eleven labs speech synthesis engine
  response = requests.post(
                'https://api.elevenlabs.io/v1/text-to-speech/{}'.format(voice_id), 
                headers = {
                  'accept': 'audio/mpeg',
                  'xi-api-key': elevenlabs_api_key,
                  'Content-Type': 'application/json',
                },
                json = {'text': text,}
              )

  # create and playback sound file
  with open('out.mp3', 'wb') as f:
      f.write(response.content)

  play_sound("out.mp3") # os.system("mpg123 out.mp3")

def hf_tts_query(payload, model_id, api_token):
  # feed text to remote speech synthesis model
  API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
  headers = {
              "Authorization": f"Bearer {api_token}",
              "accept": "audio/mpeg", 
              "Content-Type": "application/json", 
            }

  response = requests.post(API_URL, headers=headers, json={"inputs": payload})

  # create and playback sound file
  with open('out.mp3', 'wb') as f:
      f.write(response.content)

  os.system("mpg123 out.mp3") # TODO issue with writing response content to audio file 
  return response.content.json()

# binds all TTS function above to one call
def do_tts(tts_engine_name: str, text: str):
  '''
  Multi text-to-speech synthesis utility.\n
  tts_engine_name - takes any of string values 'pyttsx3','gtts','elevenlabs', 'fastspeech2' and 'speecht5_tts'.\n
  text - input text string to be converted to speech.
  '''
  if  tts_engine_name=="pyttsx3":
    pyttsx3_tts(text)
  elif tts_engine_name == "gtts":
    gTranslate_tts(text)
  elif tts_engine_name == "elevenlabs":
    elevenlabs_tts(text)
  elif tts_engine_name == "fastspeech2":
    tts_data = hf_tts_query(text, "facebook/fastspeech2-en-ljspeech", hf_api_token) 
    print(f"fastspeech2 tts_data: {tts_data}")
  elif tts_engine_name == "speech5":
      # TODO fix error speech5 tts_data: {'error': 'text-to-speech is not a valid pipeline'}
      tts_data = hf_tts_query(text, "microsoft/speecht5_tts", hf_api_token)
      print(f"speecht5 tts_data: {tts_data}")
  else:
    gTranslate_tts(text)


# Functions for handing sound file playback
def play_sound(sound_file):
  # input - sound_file specifies path to sound file in string
  # mixer.init()
  mixer.music.load(sound_file)
  mixer.music.play()

def stop_sound_gracefully():
  mixer.music.fadeout(2)


# main
def main(gpt_version): 
  # Input - gpt_version takes valid values of 'gpt-3' and 'gpt-3.5'
  global msg_thread

  no_activity_period_count = 0 # for traking idle convo sessions

  while True:
    # TODO find and fix cause of the ALSA dumps
    with noalsaerr():  # suppress ALSA lib dumps for now. remove when dump issues are fixed
      recognizer = sr.Recognizer()

      # initial prompt ('KAI' in this case) to begin recording
      print("Say 'KAI' to record your question...")
      
      with sr.Microphone() as source:
        source.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
          transcription = recognizer.recognize_google(audio)

          # stop sound  triggered by possible previous inactivity
          if no_activity_period_count > 0:
            if activate_idle_state_sound:
              stop_sound_gracefully()

          #if transcription.lower == "kai":
          print("Yes. How may I be of help?")
          pyttsx3_tts("Yes. How may I be of help?")

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
          # text = sr_transcribe(in_audio_filename)
          transcript = whisper_transcribe(in_audio_filename)
          # add transcribed query to conversation thread
          msg_thread.append({"role": "user", "content": transcript})

          if transcript:
            print("You asked: '{}'.".format(transcript))
            pyttsx3_tts("You asked, '{}'.".format(transcript))

            # generate response
            if gpt_version == "gpt-3":
              response = get_prompt_response(transcript)
              print("GPT response: {}".format(response))
            elif gpt_version == "gpt-3.5":
              response = get_chat_response(msg_thread)
              # add GPT-3 response  to thread
              msg_thread.append({"role": "assistant", "content": response})
              # display message thread
              print("Messages: \n\n{}".format(get_transcript(msg_thread)))

            #read out response
            pyttsx3_tts(response)
            pyttsx3_tts("I hope that helped. You can ask your next question.")
            time.sleep(2)

            # reset counter
            no_activity_period_count = 0 

        except sr.RequestError: 
          print("API unavailable")
          pyttsx3_tts("It would appear we have a problem with access to connectivity.")

        except sr.UnknownValueError:
          print("Unable to recognize speech")
          # speak("I could not hear you.") 
          # play a brief sound file for non active period
          if activate_idle_state_sound:
            play_sound("ambient-music-0036.mp3")
          
          # keep track of non activity
          no_activity_period_count += 1

    # stops session after 5 session loops with no voice prompts from user.
    if no_activity_period_count > 5:
      time.sleep(2)
      pyttsx3_tts("Bye for now.")
      break
  
# main 
if __name__ == "__main__":
  main("gpt-3.5") # change parameter to gpt-3.5 to use the latest gpt-3.5-turbo model
