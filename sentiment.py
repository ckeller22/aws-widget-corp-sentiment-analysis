import json
import pickle
import logging
from nltk import download
from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer
from nltk import everygrams
from string import punctuation as punctuation_list
from nltk.tokenize import word_tokenize

# Constants
MODEL_PATH = './assets/sa_classifier.pickle'
STATUS_CODE_KEY = "statusCode"
BODY_KEY = "body"
REVIEW_KEY = "review"
INPUT = 'input: {}...'
SENTIMENT = 'sentiment: {}'
ERROR = 'error: {}'

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# NLTK setup
logger.info('Setting up NLTK')
download('punkt')
download('stopwords')
stopword_list = stopwords.words('english')
stemmer = LancasterStemmer()
logger.info('NLTK setup complete')

def load_model(path):
    """Load the sentiment analysis model from a pickle file."""
    logger.info('Attempting to load model from {}'.format(path))
    with open(path, 'rb') as file:
        model = pickle.load(file)
    logger.info('Model loaded successfully')
    return model

model = load_model(MODEL_PATH)

def extract_features(input_string):
    """Extract features from the input string for sentiment analysis."""
    # Tokenize words.
    words = word_tokenize(input_string)
    
    # Second pass, remove stop words and punctuation.
    features = [stemmer.stem(word) for word in words if stemmer.stem(word) not in stopword_list and stemmer.stem(word) not in punctuation_list]

    # Third pass, generate n_grams
    n_grams = everygrams(features, max_len=3)
    
    return n_grams

def bag_of_words(words):
    """Create a bag of words from the input words."""
    bag = {}
    for word in words:
        bag[word] = bag.get(word, 0) + 1
    return bag

def get_sentiment(review):
    """Get the sentiment of a review."""
    words = extract_features(review)
    words = bag_of_words(words)
    return model.classify(words)

def analyze(event, context):
    """Analyze the sentiment of a review."""
    try:
        input = event[REVIEW_KEY]
        logger.info(INPUT.format(input[:30]))
        
        sentiment = get_sentiment(input)
        logger.info(SENTIMENT.format(sentiment))
        
        data = {
            SENTIMENT: sentiment,
        }

        return {STATUS_CODE_KEY: 200, BODY_KEY: json.dumps(data)}
    except Exception as e:
        logger.error(ERROR.format(e))
        return {STATUS_CODE_KEY: 500, BODY_KEY: "There was an error processing your request."}