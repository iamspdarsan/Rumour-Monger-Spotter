import pickle
import string
import warnings

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from.phishing import simul
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')


def categorize_data(data):    
    #divide true and false
    trueset=[]
    falseset=[]
    otherset=[]
    for i in data:
        if i['claimReview'][0]['textualRating'].lower() == 'true':
            trueset.append(i)
        elif i['claimReview'][0]['textualRating'].lower() == 'false':
            falseset.append(i)
        else:
            otherset.append(i)
    print("\n======Data are Grouped======")
    print(f'{len(trueset)} - data are true')
    print(f'{len(falseset)} - data are false')
    print(f'{len(otherset)} - data are others\n')
    
    #extracting text that claimed as true
    truetext = [text['text'] for text in trueset] 
    
    #extracting text that claimed as false
    falsetext = [text['text'] for text in falseset] 

    tdf = pd.DataFrame(list(zip(len(truetext)*['true'],truetext)),columns=['label', 'text'])
    fdf = pd.DataFrame(list(zip(len(falsetext)*['false'],falsetext)),columns=['label', 'text'])
    
    dataset = pd.concat([tdf,fdf],axis=0)
    return dataset


def label_data(dataframe):
    encoder = LabelEncoder()
    dataframe['label'] = encoder.fit_transform(dataframe['label']) #1 for true, 0 for false     
    # remove duplicates
    dataframe = dataframe.drop_duplicates(keep='first')
    return dataframe

def transform_text(text):
    #lowercase
    text = text.lower()
    
    #tokenization
    text = nltk.word_tokenize(text)
    
    #removing special chars
    text = [i for i in text if i.isalnum()]

    #removing stop word and punctuation
    _stopwords = stopwords.words('english')
    text = [i for i in text if i not in _stopwords and i not in string.punctuation]
    
    #stemming
    ps = PorterStemmer()
    text = [ps.stem(i) for i in text]

    return " ".join(text)

def build_model(df):
    labelled_data = label_data(df)
    transformed_texts=[transform_text(i) for i in labelled_data['text']]
    df['transformed_text'] = transformed_texts
    
    cv = CountVectorizer()
    tfidf = TfidfVectorizer(max_features=3000)

    X = tfidf.fit_transform(df['transformed_text']).toarray()
    Y = df['label'].values

    X_train,X_test,y_train,y_test = train_test_split(X,Y,test_size=0.2,random_state=2)
    
    print("Classifier algorithm getting trained")
    mnb = MultinomialNB()

    mnb.fit(X_train,y_train)
    y_pred = mnb.predict(X_test)

    accuracy = accuracy_score(y_test,y_pred)
    precision = precision_score(y_test,y_pred)

    pickle.dump(tfidf,open('vectorizer.pkl','wb'))
    pickle.dump(mnb,open('model.pkl','wb'))
    return accuracy,precision

def classify(text):
    tfidf = pickle.load(open('vectorizer.pkl','rb'))
    model = pickle.load(open('model.pkl','rb'))

    # 1. preprocess
    transformed_sms = transform_text(text)

    # 2. vectorize
    vector_input = tfidf.transform([transformed_sms])

    # 3. predict
    result = model.predict(vector_input)[0]

    # 4. Display
    if result == 1:
        print("Tweet is less likely spam")
    else:
        print("⚠️ Tweet is spam")
        simul()
