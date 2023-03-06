import openai
import pyttsx3 as tts
import speech_recognition as sr
import time

import os

# get OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  #os.environ['OPENAI_API_KEY']

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
    # prompt user to say 'viki' to indicate intention to communicate
    print("Say 'VIKI' and ask your question ...")
    with sr.Microphone() as source:
      recognizer = sr.Recognizer()
      audio = recognizer.listen(source)
      try:
        transcription = recognizer.recognize_google(audio)
        if transcription.lower == "viki":
          # record user audio
          in_audio_filename = "input.wav"
          print("Ask your question ...")
          with sr.Microphone() as source:
            recognizer = sr.Recognizer()
            source.pause_threshold = 1
            audio = recognizer.listen(source,
                                      phrase_time_limit=None,
                                      timeout=None)
            with open(in_audio_filename, "wb") as f:
              f.write(audio.get_wave_data())

          # transcribe audio to text
          text = transcribe_audio_to_text(in_audio_filename)
          if text:
            print("You said: {}".format(text))

          # generate response
          response = generate_response(text)
          print("GPT-3 says: {}".format(response))

          #read out response
          speak(response)

      except Exception as e:
        print("An error occured: {}".format(e))


if __name__ == "__main__":
  main()
