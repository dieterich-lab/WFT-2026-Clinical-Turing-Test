import spacy
import numpy as np
from textstat import textstat
#from sentence_transformers import SentenceTransformer


class NLPProcessor:
    # Extrahiert verschiedene Metriken aus einem Text, um die stilistische und inhaltliche Qualität zu bewerten.
    
    def __init__(self, spacy_model="de_core_news_md", sentence_model="pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"):
        # Initialisiert den NLP-Prozessor mit einem deutschen Spacy-Modell. 
        # core = general purpose pipeline with tagging, parsing, lemmatiization and NER (other option: dep)
        # web = trained on web (other option: news)
        # lg = large model with word vectors (other options: md, sm, ...) -> musste doch wieder umgestellt werden...
        self.nlp = spacy.load(spacy_model)
        #self.sentence_model = SentenceTransformer(sentence_model)
        

    def extract_metrics(self, text: str):
        doc = self.nlp(text)

        # Satzlängen-Varianz (Burstiness) -> Je höher, desto menschlicher wirkt der Text
        lengths = [len(s) for s in doc.sents] # doc.sents iteriert über die Sätze im Text
        variance = np.var(lengths) if lengths else 0

        # Keywords (Nomen & Eigennamen auf Lemma-Basis)
        keywords = {
            t.lemma_.lower()
            for t in doc
            if t.pos_ in ["NOUN", "PROPN"]
        }

        # Nominalstil-Index (Nomen zu Verben Verhältnis) -> Ärzte nutzen stark nominalisierte Fachsprache
        nouns = sum(1 for t in doc if t.pos_ == "NOUN")
        verbs = sum(1 for t in doc if t.pos_ == "VERB")
        nominal_ratio = nouns / (verbs + 1e-6)

        # Lemmas -> für ROUGE-Berechnung
        lemmatized_text = " ".join([token.lemma_.lower() for token in doc if not token.is_punct])

        return {
            "variance": variance,
            "keywords": keywords,
            "nominal_ratio": nominal_ratio,
            "lix": textstat.lix(text), # LIX-Index zur Bewertung der Lesbarkeit (höher = komplexer)
            "vector": doc.vector, # zur semantischen Ähnlichkeitsberechnung
            #"vector": self.sentence_model.encode(text), # Alternative Vektorrepräsentation mit SentenceTransformer
            "word_count": len([t for t in doc if not t.is_punct]),
            "lemmatized_text": lemmatized_text
        }