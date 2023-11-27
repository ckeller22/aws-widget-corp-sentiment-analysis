import os
import pickle
import logging
import boto3
import nltk
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
SENTIMENT_KEY = "sentiment"
INPUT = 'input: {}...'
SENTIMENT = 'sentiment: {}'
ERROR = 'error: {}'

def setup_logger():
    """Setup the logger."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

def load_nltk():
    """Load NLTK resources."""
    logger.info('Setting up NLTK')
    
    nltk.data.path.append("/tmp")
    nltk.download('punkt', download_dir='/tmp')
    nltk.download('stopwords', download_dir='/tmp')
    
    logger.info('NLTK setup complete')

load_nltk()

stopword_list = stopwords.words('english')
stemmer = LancasterStemmer()

def load_model():
    """Load the sentiment analysis model from S3 bucket."""
    logger.info('Attempting to retrieve model from S3')
    
    client = boto3.client('s3', region_name=os.environ['AWS_REGION'])
    model_file = client.get_object(Bucket=os.environ['AWS_S3_BUCKET_NAME'], Key=os.environ['AWS_MODEL_FILE_NAME'])
    model = pickle.loads(model_file['Body'].read())
    
    logger.info('Model loaded successfully')
    return model

model = load_model()

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
            SENTIMENT_KEY: sentiment,
        }

        return {STATUS_CODE_KEY: 200, BODY_KEY: data}
    except Exception as e:
        logger.error(ERROR.format(e))
        return {STATUS_CODE_KEY: 500, BODY_KEY: "There was an error processing your request."}