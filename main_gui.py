import openai
import gradio as gr
from main import whisper_transcribe
from main import get_chat_response
from main import get_transcript
from main import speak, gtts_speak
import os
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv()

# get OpenAI API key
openai.api_key = os.environ['OPENAI_API_KEY']  # os.getenv("OPENAI_API_KEY")

# configure system response context and keep track of conversation thread.
msg_thread = [
    {"role": "system", "content": "you are a very knowlegable assistant. Explain from first principles."},
]

# main interface function
def transcribe(audio):
    global msg_thread

    # transcribe to text using whisper
    transcript = whisper_transcribe(audio)

    # add transcribed query to conversation thread
    msg_thread.append({"role": "user", "content": transcript})

    # get GPT-3 response
    latest_resp = get_chat_response(msg_thread)

    # read out response
    gtts_speak(latest_resp)

    # add GPTS-3 response  to thread
    msg_thread.append({"role": "assistant", "content": latest_resp})

    # show latest transcript
    return get_transcript(msg_thread)
    

def main():           
    with gr.Blocks() as gui:
        with gr.Box():
            audio_in = gr.Audio(source="microphone",  type="filepath")
            text_output = gr.Textbox(label="Response")
            resp_btn = gr.Button("Get Response")

        resp_btn.click(fn=transcribe,
                       inputs=audio_in,
                       outputs=text_output,
                       show_progress=True)

    # gui = gr.Interface(fn=transcribe, 
    #                    inputs=gr.Audio(source="microphone",  type="filepath"),
    #                    outputs="text")


    gui.launch()

if __name__ == "__main__":
    main()