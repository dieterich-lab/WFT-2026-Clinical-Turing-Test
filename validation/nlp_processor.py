import spacy
import numpy as np
from textstat import textstat


class NLPProcessor:
    def __init__(self, model="de_core_news_md"):
        self.nlp = spacy.load(model)
        

    def extract_metrics(self, text: str):
        doc = self.nlp(text)

        # Satzlängen-Varianz (Burstiness)
        lengths = [len(s) for s in doc.sents]
        variance = np.var(lengths) if lengths else 0

        # Jaccard-Keywords (Nomen & Fachbegriffe)
        keywords = {
            t.lemma_.lower()
            for t in doc
            if t.pos_ in ["NOUN", "PROPN"]
        }

        # Nominalstil-Index (Nomen zu Verben Verhältnis)
        nouns = sum(1 for t in doc if t.pos_ == "NOUN")
        verbs = sum(1 for t in doc if t.pos_ == "VERB")
        nominal_ratio = nouns / (verbs + 1e-6)

        # lemmas
        lemmatized_text = " ".join([token.lemma_.lower() for token in doc if not token.is_punct])

        return {
            "variance": variance,
            "keywords": keywords,
            "nominal_ratio": nominal_ratio,
            "lix": textstat.lix(text), # LIX -> Lesbarkeit
            "vector": doc.vector,
            "word_count": len([t for t in doc if not t.is_punct]),
            "lemmatized_text": lemmatized_text
        }