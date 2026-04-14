import ollama
from scipy import stats
import spacy
import json
import numpy as np
from textstat import textstat
from sklearn.metrics.pairwise import cosine_similarity
from difflib import SequenceMatcher
import os

# Laden des deutschen Sprachmodells
nlp = spacy.load("de_core_news_md")

#base = os.environ["OLLAMA_URL"]
#model = os.environ["OLLAMA_MODEL"]
base ="http://127.0.0.1:11434"
model = "llama3.1:8b"

class ArztbriefEvaluator:

    def __init__(self, model_name=model):
        self.model_name = model_name

    def get_nlp_metrics(self, text):
        doc = nlp(text)
        
        # 1. Satzlängen-Varianz (Burstiness)
        lengths = [len(s) for s in doc.sents]
        variance = np.var(lengths) if lengths else 0
        
        # 2. Jaccard-Keywords (Nomen & Fachbegriffe)
        keywords = set([t.lemma_.lower() for t in doc if t.pos_ in ["NOUN", "PROPN"]])
        
        # 3. Nominalstil-Index (Nomen zu Verben Verhältnis)
        nomen = len([t for t in doc if t.pos_ == "NOUN"])
        verben = len([t for t in doc if t.pos_ == "VERB"])
        nominal_ratio = nomen / (verben + 1e-6)
        
        # 4. Lesbarkeit (LIX)
        lix = textstat.lix(text)
        
        return {
            "variance": variance,
            "keywords": keywords,
            "nominal_ratio": nominal_ratio,
            "lix": lix,
            "vector": doc.vector,
            "word_count": len([t for t in doc if not t.is_punct])
        }

    def vergleiche_briefe(self, brief_1, brief_2):
        # Quantitative Analyse 
        m1 = self.get_nlp_metrics(brief_1)
        m2 = self.get_nlp_metrics(brief_2)
        
        # Jaccard Ähnlichkeit
        intersection = len(m1['keywords'].intersection(m2['keywords']))
        union = len(m1['keywords'].union(m2['keywords']))
        jaccard = intersection / union if union > 0 else 0
        
        # Semantische Ähnlichkeit (Vektoren)
        semantic_sim = cosine_similarity([m1['vector']], [m2['vector']])[0][0]

        stats = {
            "semantische_aehnlichkeit": f"{semantic_sim:.2%}",
            "inhaltliche_deckung_jaccard": f"{jaccard:.2%}",
            "lix_differenz": abs(m1['lix'] - m2['lix']),
            "nominalstil_differenz": round(abs(m1['nominal_ratio'] - m2['nominal_ratio']), 2),
            "satzvarianz_verhaeltnis": round(m1['variance'] / (m2['variance'] + 1e-6), 2)
        }

        # Qualitative Analyse mit Ollama
        prompt = f"""
        Analysiere diese zwei Arztbriefe auf ihre stilistische Ähnlichkeit. 
        Bewerte die fachliche klinische Deckung sowie die Linguistik.

        BRIEF 1: "{brief_1}"
        BRIEF 2: "{brief_2}"

        Erstelle ein JSON mit:
        - "stil_vergleich": (Wie ähnlich ist der Schreibstil?)
        - "medizinische_praezision": (Nutzen beide die gleiche Fachterminologie?)
        - "konsistenz_bewertung": 1-100
        """
        
        try:
            client = ollama.Client(host=base)
            response = client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0.1}
            )
            qualitative_eval = json.loads(response['message']['content'])
        except Exception as e:
            qualitative_eval = {"error": f"Ollama Fehler: {str(e)}"}

        return {"metriken": stats, "llm_analyse": qualitative_eval}
        #return {"metriken": stats}

    def vergleiche_jsons(self, json_1, json_2):
        # Vergleicht zwei JSON-Objekte und gibt die Unterschiede zurück.
        differences = {}
        for key in set(json_1.keys()).union(set(json_2.keys())):
            if json_1.get(key) != json_2.get(key):
                differences[key] = {"brief_1": json_1.get(key), "brief_2": json_2.get(key)}
        
        total_keys = len(set(json_1.keys()).union(set(json_2.keys())))
        if total_keys == 0: return 1.0
        
        # berechnet eine einfache Ähnlichkeit basierend auf der Anzahl der übereinstimmenden Werte
        score_sum = 0
        for key in set(json_1.keys()).union(set(json_2.keys())):
            val1 = str(json_1.get(key, ""))
            val2 = str(json_2.get(key, ""))
            
            # Berechnet Ähnlichkeit der einzelnen Werte (0.0 bis 1.0)
            score_sum += SequenceMatcher(None, val1, val2).ratio()
            
        return {"ähnlichkeit der extrahierten infos": score_sum / total_keys, "unterschiede": differences}
    


def datei_lesen(pfad):
        # Liest eine Textdatei ein und gibt den Inhalt als String zurück.
        try:
            with open(pfad, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Fehler: Die Datei unter '{pfad}' wurde nicht gefunden.")
            return None
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
            return None


# Texte laden
text_original = datei_lesen("/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180.txt")
text_ki = datei_lesen("/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180s.txt")

# Laden der JSON-Daten
with open('180.json', 'r') as f:
    orig = json.load(f)
with open('180s.json', 'r') as f:
    synth = json.load(f)

# Nur ausführen, wenn beide Dateien erfolgreich geladen wurden
if text_original and text_ki:
    evaluator = ArztbriefEvaluator()
    ergebnis_briefe = evaluator.vergleiche_briefe(text_original, text_ki)
    ergebnis_json = evaluator.vergleiche_jsons(orig, synth)
    
    # Ergebnis anzeigen
    print(json.dumps(ergebnis_briefe, indent=2, ensure_ascii=False))
    print(json.dumps(ergebnis_json, indent=2, ensure_ascii=False))