import time
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import Word
from qa_pairs import qa_pairs

def correct_spelling_and_grammar(text):
    words = text.split()
    corrected_words = []
    familiar_words = ["eteeap", "CHED", "BTTE", "BTAET", "BTCET", "BTEET", "BTECET", "BTESET", "BTFET", "BTICET", "BTMET", "BTPPET", "BTRACET", "BTTDET"]
    for word in words:
        if word in familiar_words:
            corrected_words.append(word)
        else:
            # Correct the word using TextBlob
            corrected_word = str(Word(word).correct())
            corrected_words.append(corrected_word)
    
    corrected_text = ' '.join(corrected_words)
    return corrected_text

def find_similar_question(user_question, qa_pairs, threshold=0.5):
    user_question = correct_spelling_and_grammar(user_question)
    all_questions = [q for pair in qa_pairs for q in pair["questions"]]
    
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(all_questions)
    
    user_question_vec = vectorizer.transform([user_question])
    
    similarities = cosine_similarity(user_question_vec, vectors).flatten()
    
    most_similar_idx = similarities.argmax()
    
    if similarities[most_similar_idx] >= threshold:
        return all_questions[most_similar_idx]
    else:
        return None

def get_answer(user_question, qa_pairs, threshold=0.5):
    user_question = correct_spelling_and_grammar(user_question)
    for pair in qa_pairs:
        if user_question.lower() in [q.lower() for q in pair["questions"]]:
            if isinstance(pair["answers"], list):
                    return random.choice(pair["answers"])
            else:
                return pair["answers"]
    
    similar_question = find_similar_question(user_question, qa_pairs, threshold)
    if similar_question:
        for pair in qa_pairs:
            if similar_question in pair["questions"]:
                if isinstance(pair["answers"], list):
                    return random.choice(pair["answers"])
                else:
                    return pair["answers"]
    
    return "Sorry, I couldn't find an answer to your question. You can contact Dra. Kevien to answer your question."

def simulate_typing(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def query(question):
    while True:
        user_question = question
        answer = get_answer(user_question, qa_pairs)
        return answer