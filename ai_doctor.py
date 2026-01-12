import speech_recognition as sr
import pyttsx3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
# Symptom-to-disease database with doctors
disease_data = {
    "Flu": {"symptoms": ["fever", "cough", "headache", "fatigue", "hot","Flu-like symptoms"], "doctor": "General Physician"},
    "Cold": {"symptoms": ["sneezing", "cough", "sore throat", "runny nose"], "doctor": "General Physician"},
    "COVID-19": {"symptoms": ["fever", "cough", "fatigue", "loss of taste", "loss of smell", "hot"], "doctor": "Infectious Disease Specialist"},
    "Alzheimer's Disease": {"symptoms": ["Memory loss","difficulty problem-solving","confusion","mood swings", "mood swing"],"doctor": "Neurologist"},
    "Addison's Disease": {"symptoms": ["Fatigue","low blood pressure","darkened skin patches","nausea"],"doctor": "Endocrinologist"},
    "Asthma": {"symptoms": ["Wheezing","shortness of breath","coughing (worse at night)","chest tightness", 'tight chest'],"doctor": "Pulmonologist/Allergist"},
    "Bipolar Disorder": {"symptoms": [ "Mood swings", "depression", "mood swing"],"doctor": "Psychiatrist"},
    "Breast Cancer": {"symptoms": ["Lump in breast","nipple discharge","skin dimpling","breast pain"],"doctor": "Oncologist"},
    "Cataracts": {"symptoms": ["Blurry vision","sensitivity to light","faded colors","difficulty seeing at night", "hard to see at night"],"doctor": "Ophthalmologist"},
    "Cerebral Palsy": {"symptoms": ["Muscle stiffness or floppiness","lack of coordination","delays in motor skills","tremors","difficulty with precise movements"],"doctor": "Neurologist"},
    "Cervical Cancer": {"symptoms": ["Abnormal vaginal bleeding","pelvic pain","pain during intercourse", "vaginal bleeding"],"doctor": "Gynecologist/Oncologist"},
    "Chronic Obstructive Pulmonary Disease (COPD)": {"symptoms": ["Shortness of breath","chronic cough","chest tightness","wheezing"],"doctor": "Pulmonologist"},
    "Chronic Sinusitis": {"symptoms": ["Stuffy nose","facial pain","headaches", "headache", "postnasal drip","persistent congestion"],"doctor": "Otolaryngologist (ENT)"},
    "Crohn's Disease": {"symptoms": ["Diarrhea","abdominal pain","blood in stool","fever","weight loss","hot"],"doctor": "Gastroenterologist"},
    "Cushing's Syndrome": {"symptoms": ["Weight gain","thin skin","muscle weakness","high blood pressure"],"doctor": "Endocrinologist"},
    "Depression": {"symptoms": ["Persistent sadness","fatigue","loss of interest","sleep disturbances","thoughts of suicide"],"doctor": "Psychiatrist"},
    "Diabetes Mellitus Type 1": {"symptoms": ["Excessive thirst","frequent urination","extreme hunger","unintended weight loss","fatigue"],"doctor": "Endocrinologist"},
    "Eczema (Atopic Dermatitis)": {"symptoms": ["Dry skin","red patches","itching","swelling","oozing or crusting"],"doctor": "Dermatologist"},
    "Epilepsy": {"symptoms": ["Seizures","confusion","staring spells","uncontrollable jerking movements"],"doctor": "Neurologist"},
    "Glaucoma": {"symptoms": ["Gradual vision loss","tunnel vision","eye pain","halos around lights"],"doctor": "Ophthalmologist"},
    "Hearing Loss": {"symptoms": ["Muffled sounds","difficulty understanding speech","asking others to speak louder"],"doctor": "Otolaryngologist (ENT)"},
    "Heart Attack (Myocardial Infarction)": {"symptoms": ["Chest pain","shortness of breath","nausea","cold sweat", "dizziness"],"doctor": "Cardiologist"},
    "Hemophilia": {"symptoms": ["Easy bruising","excessive bleeding","joint pain and swelling","frequent nosebleeds"],"doctor": "Hematologist"},
    "Hepatitis B/C": {"symptoms": ["Fatigue","loss of appetite","dark urine","jaundice","joint pain"],"doctor": "Hepatologist/Infectious Disease Specialist"},
    "HIV/AIDS": {"symptoms": ["Flu-like symptoms","swollen lymph nodes","weight loss","night sweats","chronic diarrhea"],"doctor": "Infectious Disease Specialist"},
    "Hyperthyroidism": {"symptoms": ["Weight loss","rapid heartbeat","sweating","tremors","nervousness"],"doctor": "Endocrinologist"},
    "Hypothyroidism": {"symptoms": ["Fatigue","weight gain","dry skin","constipation","sensitivity to cold"],"doctor": "Endocrinologist"},
    "Kidney Failure (Chronic or Acute)": {"symptoms": ["Swelling in legs","fatigue","shortness of breath","nausea","confusion"],"doctor": "Nephrologist"},
    "Kidney Stones": {"symptoms": ["Severe lower back pain","pain while urinating","cloudy urine","nausea","frequent urination"],"doctor": "Urologist"},
    "Leukemia": {"symptoms": ["Fatigue","frequent infections","swollen lymph nodes","fever","hot","weight loss"],"doctor": "Hematologist/Oncologist"},
    "Liver Cirrhosis": {"symptoms": ["Fatigue","jaundice","swelling in legs","easy bruising","nausea"],"doctor": "Hepatologist/Gastroenterologist"},
    "Lymphoma (Hodgkin's, Non-Hodgkin's, etc.)": {"symptoms": ["Painless swollen lymph nodes","fever","night sweats","hot","weight loss"],"doctor": "Hematologist/Oncologist"},
    "Migraine": {"symptoms": ["Intense headaches","nausea","sensitivity to light and sound","visual disturbances", "intense headache"],"doctor": "Neurologist"},
    "Ulcerative Colitis": {"symptoms": ["Diarrhea with blood","rectal pain","abdominal cramping","weight loss","fatigue"], "doctor": "Gastroenterologist"}
}
# Symptom synonyms for better matching
synonyms = {
    "runny nose": ["nasal congestion", "stuffy nose"],
    "fatigue": ["tiredness", "exhaustion"],
    "shortness of breath": ["difficulty breathing", "breathlessness"],
    "fever": ["high temperature", "chills", "hot"],
    "cough": ["dry cough", "wet cough"],
    "headache": ["migraine", "head pain"]
}
  
# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

# Set TTS to English (US)
voices = engine.getProperty('voices')
for voice in voices:
    if "english" in voice.name.lower():  # Ensure it picks an English voice
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 160)  # Adjust speed for better clarity
engine.setProperty('volume', 2.0)  # Max volume

# Function to check symptoms
def get_synonym_match(word):
    """Finds the best synonym match for a given word."""
    for key, values in synonyms.items():
        if word in values:
            return key  # Return the main symptom name
    return word  # Return original if no match

def fuzzy_match(user_input, known_symptoms, threshold=75):
    """Uses fuzzy matching to find the best symptom match."""
    matched_symptoms = []
    for word in user_input.split():
        match, score = process.extractOne(word, known_symptoms)
        if score >= threshold:
            matched_symptoms.append(get_synonym_match(match))
    return list(set(matched_symptoms))
def check_symptoms(user_symptoms):
    """Checks symptoms and returns the top 3 possible diseases."""
    results = {}

    for disease, data in disease_data.items():
        symptoms = data["symptoms"]
        match_count = len(set(user_symptoms) & set(symptoms))
        compatibility = (match_count / len(symptoms)) * 100  

        if match_count > 0:
            results[disease] = {
                "match": round(compatibility, 2),
                "doctor": data["doctor"],
                "related_symptoms": symptoms
            }

    # Sort results by highest match percentage and limit to top 3
    sorted_results = sorted(results.items(), key=lambda x: x[1]["match"], reverse=True)[:3]
    
    return sorted_results  # Only return the top 3 matches


def listen_for_symptoms():
    """Listens to user's symptoms via voice and processes them."""
    with sr.Microphone() as source:
        print("Tell me your symptoms...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Increase noise adjustment time
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)  # Allow longer speech

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")

        # Check for known symptoms using fuzzy matching
        known_symptoms = sum([disease["symptoms"] for disease in disease_data.values()], [])
        detected_symptoms = fuzzy_match(text.lower(), known_symptoms)

        if not detected_symptoms:
            speak("I didn't catch that. Can you repeat your symptoms?")
            return listen_for_symptoms()
        
        return detected_symptoms
    except sr.UnknownValueError:
        speak("I couldn't understand you. Could you repeat that?")
        return listen_for_symptoms()
    except sr.RequestError:
        print("Could not request results, check your internet connection.")
        return []

def ask_followup_question():
    """Ask the user if they have additional symptoms."""
    speak("Do you have any other symptoms?")
    extra_symptoms = listen_for_symptoms()
    return extra_symptoms

if __name__ == "__main__":
    symptoms = listen_for_symptoms()

    if symptoms:
     matches = check_symptoms(symptoms)

    if matches:
        response = "The top possible conditions are:\n"
        for disease, details in matches:
            response += f"{disease} ({details['match']}%) - To confirm, visit a {details['doctor']}.\n"
            response += f"Common Symptoms: {', '.join(details['related_symptoms'])}\n"
        response += "If you're unsure, consult a doctor for further evaluation."
    else:
        response = "I couldn't find a match for your symptoms."

    print(response)
    speak(response)
