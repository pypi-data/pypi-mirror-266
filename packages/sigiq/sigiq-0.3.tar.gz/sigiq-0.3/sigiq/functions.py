import os
import requests

def completion(model, messages, **kwargs):
    api_key = os.environ.get('SIGIQ_API_KEY')
    
    url = "http://34.171.139.50:4000/chat/completions"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    payload = {
        'model': model,
        'messages': messages,
    }
    payload.update(kwargs)

    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def embedding(model, input, **kwargs):
    api_key = os.environ.get('SIGIQ_API_KEY')
    
    url = "http://34.171.139.50:4000/v1/embeddings"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    payload = {
        'model': model,
        'input': input,
    }
    payload.update(kwargs)

    response = requests.post(url, json=payload, headers=headers)
    return response.json()