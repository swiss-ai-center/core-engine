from enum import Enum


class FieldDescriptionType(str, Enum):
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    TEXT_PLAIN = "text/plain"
    TEXT_CSV = "text/csv"
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_OGG = "audio/ogg"


class ExecutionUnitTagName(str, Enum):
    IMAGE_PROCESSING = "Image Processing"
    IMAGE_RECOGNITION = "Image Recognition"
    NATURAL_LANGUAGE_PROCESSING = "Natural Language Processing"
    ANOMALY_DETECTION = "Anomaly Detection"
    RECOMMENDATION = "Recommendation"
    TIME_SERIES = "Time Series"
    CLUSTERING = "Clustering"
    SEGMENTATION = "Segmentation"
    SPEECH_RECOGNITION = "Speech Recognition"
    DATA_PREPROCESSING = "Data Preprocessing"
    SENTIMENT_ANALYSIS = "Sentiment Analysis"


class ExecutionUnitTagAcronym(str, Enum):
    IMAGE_PROCESSING = "IP"
    IMAGE_RECOGNITION = "IR"
    NATURAL_LANGUAGE_PROCESSING = "NLP"
    ANOMALY_DETECTION = "AD"
    RECOMMENDATION = "R"
    TIME_SERIES = "TS"
    CLUSTERING = "C"
    SEGMENTATION = "S"
    SPEECH_RECOGNITION = "SR"
    DATA_PREPROCESSING = "DP"
    SENTIMENT_ANALYSIS = "SA"
