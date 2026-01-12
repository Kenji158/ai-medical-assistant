from flask import Flask, render_template, jsonify, request
import speech_recognition as sr
import pyttsx3
from ai_doctor6 import check_symptoms
import threading
from fuzzywuzzy import process

app = Flask(__name__)

# Initialize recognizer and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

# Predefined symptom list for better matching
known_symptoms = {
    "fever", "cough", "fatigue", "headache", "chills", "sore throat",
    "shortness of breath", "loss of taste", "loss of smell", "hot",
    "sneezing", "runny nose", "memory loss", "difficulty problem-solving",
    "confusion", "mood swings", "low blood pressure", "darkened skin patches",
    "nausea", "wheezing", "chest tightness", "depression", "lump in breast",
    "nipple discharge", "skin dimpling", "breast pain", "blurry vision",
    "sensitivity to light", "difficulty seeing at night", "abnormal bleeding",
    "pelvic pain", "stuffy nose", "facial pain", "postnasal drip",
    "persistent congestion", "diarrhea", "abdominal pain", "blood in stool",
    "weight gain", "muscle weakness", "high blood pressure", "sleep disturbances",
    "excessive thirst", "frequent urination", "extreme hunger",
    "joint pain", "swollen lymph nodes", "night sweats", "chronic diarrhea"
}

# Symptom synonyms for fuzzy matching
symptom_synonyms = {
    "tired": "fatigue",
    "burning up": "fever",
    "weak": "fatigue",
    "sick": "illness",
    "pain in chest": "chest pain",
    "difficulty breathing": "shortness of breath",
    "running nose": "runny nose",
    "can't smell": "loss of smell"
}

def speak(text):
    """Speak output using pyttsx3 in a separate thread to avoid blocking."""
    def run():
        local_engine = pyttsx3.init()
        local_engine.setProperty('rate', 160)
        local_engine.setProperty('volume', 1.0)
        local_engine.say(text)
        local_engine.runAndWait()
    threading.Thread(target=run).start()

def listen_for_symptoms():
    """Capture user's speech and return recognized text."""
    with sr.Microphone() as source:
        print("Listening for symptoms...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            recognized_text = recognizer.recognize_google(audio).lower()
            print(f"Recognized Input: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            return "Could not understand the speech."
        except sr.RequestError:
            return "Error: Could not process the request."

def extract_symptoms(text):
    """Extract symptoms using exact and fuzzy matching."""
    symptoms_found = set()

    # Fuzzy matching against known symptoms
    for word in text.split():
        match, score = process.extractOne(word, known_symptoms)
        if score >= 80:
            symptoms_found.add(match)

    # Check against synonyms
    for key, value in symptom_synonyms.items():
        if key in text:
            symptoms_found.add(value)

    return list(symptoms_found)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_ai', methods=['POST'])
def run_ai():
    try:
        data = request.get_json()
        symptoms_text = data.get("symptoms", "").strip()

        if not symptoms_text:
            symptoms_text = listen_for_symptoms().strip()

        if symptoms_text in ["Could not understand the speech.", "Error: Could not process the request."]:
            message = "Sorry, I couldn't understand. Please try again."
            threading.Thread(target=speak, args=(message,)).start()
            return jsonify({"input": "Unknown", "diagnosis": message}), 200

        symptoms = extract_symptoms(symptoms_text)

        if not symptoms:
            message = "Sorry, I couldn't identify symptoms. Please try again."
            threading.Thread(target=speak, args=(message,)).start()
            return jsonify({"input": symptoms_text, "diagnosis": message}), 200

        matches = check_symptoms(symptoms)
        response = {"input": symptoms_text, "conditions": []}

        for disease, details in matches:
            response["conditions"].append({
                "disease": disease,
                "match": details["match"],
                "doctor": details["doctor"],
                "symptoms": details["related_symptoms"]
            })

        if response["conditions"]:
            diagnosis_text = "\n".join([f"{c['disease']} ({c['match']}%) - You should see: {c['doctor']}" for c in response["conditions"]])
        else:
            diagnosis_text = "No conditions matched your symptoms."

        threading.Thread(target=speak, args=(diagnosis_text,)).start()
        response["diagnosis"] = diagnosis_text  

        return jsonify(response), 200  

    except Exception as e:
        print(f"Error in /run_ai: {e}")
        return jsonify({"error": "An error occurred. Try again."}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
