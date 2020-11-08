# NLP
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

# webscraping
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

# API creation
from flask import Flask, render_template, url_for, request

# NLP model
nlp = spacy.load('en_core_web_lg')

# summarizing function
def summarize(text):
    # getting stopwords and punctuations to remove from doc
    stopwords = list(STOP_WORDS)
    punctuations = punctuation + '\n'

    # tokenization
    doc = nlp(text)

    # getting the frequency of each word in doc
    count_words = {}
    for token in doc:
        if token.text.lower() not in stopwords:
            if token.text.lower() not in punctuations:
                if token.text.lower() not in count_words.keys():
                    count_words[token.text.lower()] = 1
                else:
                    try:
                        count_words[token.text.lower()] += 1
                    except:
                        print('error')

    # normalizing count_words
    max_count = max(count_words.values())
    normalized_count = count_words
    for key in normalized_count.keys():
        normalized_count[key] = normalized_count[key] / max_count

    # getting mostly used sentences by creating sentence score with help of count_words 
    sentences = [sent for sent in doc.sents]
    sentence_score = {}
    for sent in sentences:
        for word in sent:
            if word.text.lower() in normalized_count.keys():
                if sent not in sentence_score.keys():
                    sentence_score[sent] = normalized_count[word.text.lower()]
                else:
                    sentence_score[sent] += normalized_count[word.text.lower()]

    # Creating summary
    summary_length = int(len(sentences)*0.30)
    summary = nlargest(summary_length,sentence_score,sentence_score.get)
    if len(summary) > 1:
        final_summary = ' '.join([word.text for word in summary])
    else:
        final_summary = str(summary)
    return final_summary

# reading time function
def reading_time(text):
    num_of_words = len([word.text for word in nlp(text)])
    avg_time = num_of_words / 250.0
    return avg_time

# text scraping function
def get_text(url):
    webpage = urlopen(url)
    soup = bs(webpage)
    webpage_text = ' '.join(map(lambda p:p.text,soup.find_all('p')))
    return webpage_text


app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def homepage():
    return render_template('index.html')

@app.route('/summary',methods=['GET','POST'])
def summary():
    if request.method == 'POST':
        raw_url = request.form['raw_url']
        raw_text = get_text(raw_url)
        original_time = reading_time(raw_text)
        text_summary = summarize(raw_text)
        summary_time = reading_time(text_summary)
        return render_template('summary.html',original_time=original_time,raw_text=raw_text,summary_time=summary_time,text_summary=text_summary)

if __name__ == '__main__':
    app.run(debug=False)