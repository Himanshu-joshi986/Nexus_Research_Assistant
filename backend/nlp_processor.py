import re
import subprocess
import sys
from functools import cache

import nltk
import spacy
from keybert import KeyBERT
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data on first run
for pkg in ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger", "punkt_tab"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


@cache
def _get_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        return spacy.load("en_core_web_sm")


@cache
def _get_kw_model():
    return KeyBERT()


def preprocess(text: str) -> dict:
    """Full NLP pipeline: tokenize, clean, lemmatize, NER, keywords."""
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize + stopword removal + lemmatization
    tokens = [t for t in word_tokenize(text.lower()) if t.isalpha() and t not in _stop_words]
    lemmas = [_lemmatizer.lemmatize(t) for t in tokens]

    # Named Entity Recognition
    doc = _get_nlp()(text[:100000])  # spaCy limit guard
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Keyword Extraction
    try:
        keywords_raw = _get_kw_model().extract_keywords(
            text[:5000], keyphrase_ngram_range=(1, 2), stop_words="english", top_n=15
        )
        keywords = [{"word": k, "score": round(s, 4)} for k, s in keywords_raw]
    except Exception:
        keywords = []

    return {
        "tokens": lemmas[:200],
        "entities": entities[:50],
        "keywords": keywords,
        "word_count": len(tokens),
    }


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping word chunks."""
    words = text.split()
    return [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]
