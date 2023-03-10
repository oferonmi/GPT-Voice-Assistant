import openai
import gradio as gr
from main import whisper_transcribe_audio_to_text
from main import speak
import os
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv()

# get OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']  # os.getenv("OPENAI_API_KEY")

# for keeping track on conversation thread
convo_thread = [
    # {"role": "system", "content": "you are a very knowlegable assistant. Explain like physicist Richard Feynmann."},
    {"role": "system", "content": "you are a very knowlegable assistant. Explain from first principles."},
]

def get_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message["content"]

def transcribe(audio):
    global convo_thread

    # transcribe to text using whisper
    transcript = whisper_transcribe_audio_to_text(audio)

    # add transcribed query to conversation thread
    convo_thread.append({"role": "user", "content": transcript})

    # get GPT-3 response
    latest_resp = get_response(convo_thread)

    # read out response
    speak(latest_resp)

    # add GPTS-3 response  to thread
    convo_thread.append({"role": "assistant", "content": latest_resp})

    # format message thread
    chat_transcript = ""
    for message in convo_thread:
        if message["role"] != "system":
            chat_transcript += message["role"] + ": " + message["content"] + "\n\n"
    
    return chat_transcript
           
with gr.Blocks() as gui:
    with gr.Box():
        audio_in = gr.Audio(source="microphone",  type="filepath")
        text_output = gr.Textbox(label="Response")
        resp_btn = gr.Button("Get Response")

    resp_btn.click(fn=transcribe, inputs=audio_in, outputs=text_output)

# gui = gr.Interface(fn=transcribe, 
#                    inputs=gr.Audio(source="microphone",  type="filepath"),
#                    outputs="text")


gui.launch()



# if __name__ == "__main__":