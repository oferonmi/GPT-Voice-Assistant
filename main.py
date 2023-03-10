import openai
import pyttsx3 as tts
from gtts import gTTS
import speech_recognition as sr
from pygame import mixer
import time
from py_error_handler import noalsaerr # to suppress ALSA lib dumps
import os
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv() 

# get OpenAI API key
openai.api_key =  os.environ['OPENAI_API_KEY'] # os.getenv("OPENAI_API_KEY")

# activate (Tset to True) or deactivate (set to False) sound that play in idle sessions
activate_idle_state_sound = True 

# configure system response context and keep track of conversation thread
msg_thread = [
    {"role": "system", "content": "you are a very knowlegable assistant. Explain using first principles like physicist Richard Feynmann."},
]

# initialize module for loading and playing sounds
mixer.init()

# text-to-speech engine instance
tts_engine = tts.init()

# TODO add a much smoother speech synthesizer 
# voices = tts_engine.getProperty('voices')
# print("Number of voices: {}".format(len(voices)))
# tts_engine.setProperty('voice', voices[-1].id)

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
  # try:
  transcript = openai.Audio.transcribe("whisper-1", audio_data)
  return transcript["text"]
  # except:
  #   print("Ah, let's give this another try.")

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

def get_transcript(msg_thread):
  # format message thread
    chat_transcript = ""
    for message in msg_thread:
        if message["role"] != "system":
            chat_transcript += message["role"] + \
                ": " + message["content"] + "\n\n"

    return chat_transcript

# functions to transcribe text string to sound
def speak(text):
  tts_engine.say(text)
  tts_engine.runAndWait()

# TODO issue with incomplete text read out
def gtts_speak(text):
  tts = gTTS(text, lang="en", tld="co.uk")
  tts.save("out.mp3")
  play_sound("out.mp3")

# Function for handing sound file playback
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

      # initial prompt ('Kai' in this case) to begin recording
      print("Say 'Kai' to record your question...")
      
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
          speak("Yes. How may I be of help?")

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
            print("You said: '{}'.".format(transcript))
            speak("You asked, '{}'.".format(transcript))

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
            speak(response)
            speak("I hope that helped. You can ask your next question.")
            time.sleep(2)

            # reset counter
            no_activity_period_count = 0 

        except sr.RequestError: 
          print("API unavailable")
          speak("It would appear we have a problem with access to connectivity.")

        except sr.UnknownValueError:
          print("Unable to recognize speech")
          # speak("I could not hear you.") 
          # play a brief sound file for non active period
          if activate_idle_state_sound:
            play_sound("ambient-music-0036.mp3")
          
          # keep track of non activity
          no_activity_period_count += 1

    # Temporal way to end question and answer loop due to non activity
    # stops session after 3 instance of no prompts.
    if no_activity_period_count > 5:
      time.sleep(2)
      speak("Bye for now.")
      break
  
# main 
if __name__ == "__main__":
  main("gpt-3.5") # change parameter to gpt-3.5 to use the latest gpt-3.5-turbo model
