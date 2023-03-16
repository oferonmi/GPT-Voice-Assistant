# ChatGPT-Voice-Assistant
An AI voice assistant based of OpenAI's ChatGPT API.

# Usage Instructions
1. Use the Secrets management utility of your development environment or a .env file to create environment variables OPENAI_API_KEY and ELEVENLABS_API_KEY and set their values to your own OpenAI and Eleven Labs API keys respectively. 

2. Run the following commands
    - For GNU/Linux
    ```
    apt-get install python3-pyaudio
    ```
    - For Apple macOS
    ```
    brew install portaudio
    ```
    - On all platforms, install dependencies
    ```
    pip install -r requirements.txt

    ```
    - To use app in command line
    ```
    python main.py
    ```
    - To use app with graphical interface
    ```
    python main_gui.py
    ```

3. Follow instruction at prompt.
