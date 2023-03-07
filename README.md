# ChatGPT-Voice-Assistant
An AI voice assistant based of OpenAI's ChatGPT API.

# Usage Instructions
1. Use the Secrets management utility of your development environment or a .env file to create an environment variable called 'OPENAI_API_KEY' and set it's value to your own API key from your OpenAI developer account page. 

2. Run the following commands
    - For GNU/Linux
    ```
        sudo apt-get install python3-pyaudio
    ```
    - For Apple macOS
    ```
        brew install portaudio
    ```
    - In all platforms
    ```
        pip install -r requirements.txt

        python main.py
    ```

3. Follow instruction at prompt.