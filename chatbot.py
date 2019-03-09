import requests
import nltk
import string
import pandas as pd
from time import sleep
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only

df = pd.read_excel('dataset.xlsx')
descriptions = df['overview']
titles = df['original_title']

lemmer = nltk.stem.WordNetLemmatizer()

def lem_tokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def lem_normalize(text):
    return lem_tokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def get_response(user_input, all_options, all_titles):
    user_input = user_input.lower()
    
    all_options = list(all_options)
    all_options.append(user_input)
    
    tfidf_vec = TfidfVectorizer(tokenizer=lem_normalize, stop_words='english')
    
    tfidf_matrix = tfidf_vec.fit_transform(all_options)
    values = cosine_similarity(tfidf_matrix[-1], tfidf_matrix)
    idx=values.argsort()[0][-2]
    flat = values.flatten()
    flat.sort()
    req_tfidf = flat[-2]


    response = ''
    if (req_tfidf == 0):
        response = 'Sorry, I could not find an answer'
    else:
        response = "Title: "+ all_titles[idx] + "\nDescription: " + all_options[idx]
    
    return response

url = 'https://api.telegram.org/bot785899245:AAEV9-MfC1gClhRtgOSlkBn4neL66RYh4zs/'

def get_updates_json(request):  
    response = requests.get(request + 'getUpdates')
    return response.json()

def last_update(data):
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]

def get_chat_id(update):  
    chat_id = update['message']['chat']['id']
    return chat_id

def send_message(chat, text):  
    params = {'chat_id': chat, 'text': text}
    response = requests.post(url + 'sendMessage', data=params)
    return response

update_id = last_update(get_updates_json(url))['update_id']
msg = ''
print('Hello world!')
while True:
    if update_id == last_update(get_updates_json(url))['update_id']:
        msg = last_update(get_updates_json(url))['message']
        print('Processing message:', msg)
        user_input = msg['text']
        nlp_response = get_response(user_input, descriptions, titles)
        send_message(get_chat_id(last_update(get_updates_json(url))), nlp_response)
        update_id += 1
        sleep(1)