import os
import openai
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS
import tempfile
import boto3
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Create a Polly client
polly_client = boto3.client('polly', region_name='us-east-1')

def generate_response(prompt, conversation_history=[]):
    try:
        system_prompt = "You are Apollo, a super chill, funny, caring, and empathetic friend 👫 Your role is to be the friend the user always wanted - an expert texter who matches their vibe and carries the convo seamlessly 💯. Use your expertise to text and speak naturally, begin with natural language as if you are speaking to them. Your ultimate goal is to help the user reflect on their life, prioritize their hobbies, and make time for activities they enjoy 🎨⚽️🎸  Above all, match their vibe, guide without lecturing, and build the friendship through an enjoyable, interactive texting experience. Begin all responses with direct language, NO * * usage. "
        
        messages = [
            *conversation_history,
            {"role": "user", "content": prompt}
        ]
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=150,
            temperature=0.6,
            messages=messages,
            system=system_prompt
        )
        
        text_response = message.content[0].text
        conversation_history.append({"role": "user", "content": prompt})
        conversation_history.append({"role": "assistant", "content": text_response})
        
        return text_response
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response."

def synthesize_speech(text):
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Matthew'  # You can change the voice ID based on your preference
    )
    
    audio_data = response['AudioStream'].read()
    return audio_data

conversation_history = []

@app.route('/api/generate_response', methods=['POST'])
def generate_response_api():
    global conversation_history  # Access the global conversation_history variable
    
    data = request.get_json()
    message = data['message']
    print('Received message from frontend:', message)
    
    response_text = generate_response(message, conversation_history)
    print('Generated response from Anthropic API:', response_text)
    
    audio_data = synthesize_speech(response_text)
    audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    return jsonify({'response': response_text, 'audio_data': audio_data_base64})

if __name__ == '__main__':
    app.run()