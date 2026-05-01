from flask import Flask, request
from google import genai
import requests

app = Flask(__name__)
client = genai.Client(api_key="AIzaSyA3PjMxEd3sbU94ywnENa7jxIaxgZh86sg")

ULTRAMSG_INSTANCE = "instance172688"
ULTRAMSG_TOKEN = "92hzn3m8pgvr9foq"

conversations = {}

SYSTEM_PROMPT = """
Tu es l'assistant IA d'Atlas AI Studio, agence IA basée à Rabat.
Qualifie le prospect en posant ces questions UNE PAR UNE :
1. Quel est votre secteur d'activité ?
2. Quel service vous intéresse ? (site web, chatbot, automatisation)
3. Quel est votre budget approximatif ?
4. Quand souhaitez-vous démarrer ?
Réponds en français, sois chaleureux et professionnel. Max 3 phrases par réponse.
"""

def envoyer_message(numero, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {"token": ULTRAMSG_TOKEN, "to": numero, "body": message}
    r = requests.post(url, json=payload)
    print("UltraMsg response:", r.json())  # ← pour déboguer

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}

    # ✅ Extraction correcte depuis data["data"]
    msg_data = data.get("data", {})
    message = msg_data.get("body", "")
    numero = msg_data.get("from", "")
    from_me = msg_data.get("fromMe", False)

    print(f"De: {numero} | Message: {message} | FromMe: {from_me}")

    # Ignorer les messages du bot lui-même
    if from_me or not message or not numero:
        return "OK", 200

    if numero not in conversations:
        conversations[numero] = []

    conversations[numero].append(f"Client: {message}")
    contexte = "\n".join(conversations[numero][-10:])

    prompt = f"{SYSTEM_PROMPT}\n\nHistorique:\n{contexte}\n\nRéponds maintenant:"
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    reponse = response.text
    conversations[numero].append(f"Agent: {reponse}")

    envoyer_message(numero, reponse)
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)