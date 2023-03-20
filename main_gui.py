import gradio as gr
import os
from main import whisper_transcribe
from main import get_chat_response
from main import get_transcript
from main import do_tts

# configure system response context and keep track of conversation thread.
msg_thread = [
    {"role": "system", "content": "you are a very knowlegable assistant. Explain concepts from first principles."},
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
    tts_engine = "gtts"
    do_tts(tts_engine, latest_resp)
    # file handle for audio response created by tts engine. To be returned by function
    audio_out_name = "out.mp3" 

    # add GPTS-3 response  to thread
    msg_thread.append({"role": "assistant", "content": latest_resp})

    # show latest transcript
    return get_transcript(msg_thread), audio_out_name
    

def main():
    with gr.Blocks() as gui:
        with gr.Box():
            gr.Markdown(
                """
                # Hello! I'm KAI
                Use the Record to microphone button to ask your question.
                """
            )
            with gr.Row():
                audio_in = gr.Audio(source="microphone",  type="filepath")
                audio_out = gr.Audio(label="Audio response playback")

            with gr.Row():
                text_out = gr.Textbox(label="Response")

            resp_btn = gr.Button("Get Response")
            resp_btn.click(fn=transcribe, inputs=audio_in, outputs=[text_out, audio_out])
            
            gui.launch()

# def main():
    # gui = gr.Interface(fn=transcribe, 
    #                    inputs=gr.Audio(source="microphone",  type="filepath"),
    #                    outputs="text", live=True)


    # gui.launch()

if __name__ == "__main__":
    main()