import requests

def send_to_chatgpt(OPENAI_API_KEY, OPENAI_MODEL, output_file, response_file):
    # Po dokončení vytvoření output file, pokud je OpenAI API klíč nastaven, pošlete obsah do ChatGPT API
    if OPENAI_API_KEY:
        with open(output_file, 'r') as f:
            input_text = f.read()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        data = {
            'model': OPENAI_MODEL,
            'messages': [
                {'role': 'system', 'content': 'You are a helpful assistant designed to output markdown.'},
                {'role': 'user', 'content': input_text}
            ]
        }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()

            # Extrahování obsahu z JSON
            content = data["choices"][0]["message"]["content"]

            # Uložení obsahu do souboru
            with open(response_file, "w") as file:
                file.write(content)
            print(f"Odpověď od ChatGPT API je uložena v souboru {response_file}")
        else:
            print(f"Byla zaznamenána chyba při volání API: {response.json().get('error', {}).get('message', 'Neznámá chyba')}")
            exit(1)
    else:
        print("OpenAI API klíč není nastaven. Volání ChatGPT nebude provedeno.")
