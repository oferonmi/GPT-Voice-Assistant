from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from kai import process_prompt
import os

kaiApp = Flask(__name__)
# limit the maximum allowed payload to 16 megabytes
kaiApp.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


@kaiApp.route("/", methods=['GET'])
def kai_home():
  global convo_text

  return render_template(
    'kai.html',
    transcript=convo_text,
  )


@kaiApp.route("/kai/prompt_processor", methods=['POST'])
def kai_process_prompt():

  global convo_text

  if request.method == 'POST':
    # prompt handles
    audio_prompt_path = ''
    text_prompt = ''
    # path to audio response
    audio_resp_path = os.path.join(kaiApp.static_folder, "out.mp3")

    # get prompt
    if len(request.form.getlist('text')):
      # other text prompt
      text_prompt = request.form.getlist('text')  #list
      #text_prompt = request.form.get('text')
    else:
      # get audio prompt
      file = request.files['audio']

      if file:
        audiofilename = secure_filename(file.filename)
        audio_prompt_path = os.path.join(kaiApp.static_folder,
                                         audiofilename)
        file.save(audio_prompt_path)

    # get AI response to either text or audio prompt
    convo_text = process_prompt(audio_prompt_path, text_prompt,
                                audio_resp_path)

  return redirect(url_for('kai_home'))

if __name__ == "__main__":
  kaiApp.run(host="0.0.0.0", debug=True)
