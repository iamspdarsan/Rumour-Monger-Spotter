import pickle
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def cleandata(dataframe):
    encoder = LabelEncoder()
    dataframe['label'] = encoder.fit_transform(dataframe['label']) #1 for true, 0 for false     
    # remove duplicates
    dataframe = dataframe.drop_duplicates(keep='first')
    #print(dataframe)

def transform_text(text):
    #lowercase
    text = text.lower()
    #tokenization
    text = nltk.word_tokenize(text)
    #removing special chars
    y = []
    for i in text:
        if i.isalnum():
            y.append(i)
    #removing stop word and punctuation
    text = y[:]
    y.clear()
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
    #stemming
    text = y[:]
    y.clear()
    ps = PorterStemmer()
    for i in text:
        y.append(ps.stem(i))
    return " ".join(y)

def build_model(df):
    cv = CountVectorizer()
    tfidf = TfidfVectorizer(max_features=3000)

    X = tfidf.fit_transform(df['transformed_text']).toarray()
    y = df['label'].values

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=2)
    print("Classifier algorithm getting trained")
    mnb = MultinomialNB()

    mnb.fit(X_train,y_train)
    y_pred = mnb.predict(X_test)
    accuracy = accuracy_score(y_test,y_pred)
    precision = precision_score(y_test,y_pred)
    pickle.dump(tfidf,open('vectorizer.pkl','wb'))
    pickle.dump(mnb,open('model.pkl','wb'))
    return accuracy,precision


def simul():
    #simulation or plan
    print("Phishing link sent to rumour monger")
    print('IP log will be available at:',end=' ')
    print('https://grabify.link/track/2CX1VQ\n\n')


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
        print("Tweet is not Spam")
    else:
        print("Tweet is Spam")
        simul()
    