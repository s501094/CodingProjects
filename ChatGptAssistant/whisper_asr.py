import openai

def get_transcription(audio_file_path):
    # Set up OpenAI API client (use your own API key)
    openai.api_key = 'YOUR_OPENAI_API_KEY'

    # Load audio file and send to OpenAI for transcription
    # You might need to adjust this based on the Whisper ASR API specifics
    with open(audio_file_path, 'rb') as audio_file:
        response = openai.Whisper.transcribe(file=audio_file)
    
    return response.get('text', '')
