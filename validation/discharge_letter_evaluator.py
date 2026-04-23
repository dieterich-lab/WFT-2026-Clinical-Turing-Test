
import json

import ollama
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer
from difflib import SequenceMatcher

from validation.nlp_processor import NLPProcessor


base ="http://127.0.0.1:11434"
model = "llama3.1:8b"

class ArztbriefEvaluator:
    def __init__(self, model_name=model, ollama_host=base):
        self.model_name = model_name
        self.client = ollama.Client(host=ollama_host)

        self.nlp = NLPProcessor()
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"],
            use_stemmer=False # ROUGE soll mit deutschen Lemmas berechnet werden
        )

    def nlp_analysis(self, original_letter, synthethic_letter):
        orig = self.nlp.extract_metrics(original_letter)
        syn = self.nlp.extract_metrics(synthethic_letter)
        
        # Jaccard Ähnlichkeit
        intersection = len(orig['keywords'].intersection(syn['keywords']))
        union = len(orig['keywords'].union(syn['keywords']))
        jaccard = intersection / union if union > 0 else 0
        
        # Semantische Ähnlichkeit (Vektoren)
        semantic_sim = cosine_similarity([orig['vector']], [syn['vector']])[0][0]

        # ROUGE mit deutschen Lemmas
        rouge_scores = self.rouge.score(orig['lemmatized_text'], syn['lemmatized_text'])

        return {
            "semantische_aehnlichkeit": f"{semantic_sim:.2%}",
            "inhaltliche_deckung_jaccard": f"{jaccard:.2%}",
            "lix_original": orig['lix'],
            "lix_synthetisch": syn['lix'],
            "lix_differenz": abs(orig['lix'] - syn['lix']),
            "nominalstil_original": round(orig['nominal_ratio'], 2),
            "nominalstil_synthetisch": round(syn['nominal_ratio'], 2),
            "nominalstil_differenz": round(abs(orig['nominal_ratio'] - syn['nominal_ratio']), 2),
            "satzvarianz_original": round(orig['variance'], 2),
            "satzvarianz_synthetisch": round(syn['variance'], 2),
            "satzvarianz_verhaeltnis": round(orig['variance'] / (syn['variance'] + 1e-6), 2),
            "rouge1": rouge_scores["rouge1"].fmeasure,
            "rouge2": rouge_scores["rouge2"].fmeasure,
            "rougeL": rouge_scores["rougeL"].fmeasure
        }

    def llm_analysis(self, original_letter, synthetic_letter):
        prompt = f"""
        Analysiere diese zwei Arztbriefe auf ihre stilistische Ähnlichkeit. 
        Bewerte die fachliche klinische Deckung sowie die Linguistik.

        BRIEF 1: "{original_letter}"
        BRIEF 2: "{synthetic_letter}"

        Erstelle ein JSON mit:
        - "stil_vergleich": (Wie ähnlich ist der Schreibstil?)
        - "medizinische_praezision": (Nutzen beide die gleiche Fachterminologie?)
        - "konsistenz_bewertung": 1-100
        """
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0.1}
            )
            return json.loads(response['message']['content'])
        except Exception as e:
            return {"error": f"Ollama Fehler: {str(e)}"}
    
    def json_analysis(self, json_original, json_syntetic):
        differences = {}
        score_sum = 0
        total_keys = len(set(json_original.keys()).union(set(json_syntetic.keys())))
        if total_keys == 0: return 1.0

        for key in set(json_original.keys()).union(set(json_syntetic.keys())):
            val_orig = json_original.get(key)
            val_syn = json_syntetic.get(key)

            # Berechnet Ähnlichkeit der einzelnen Werte (0.0 bis 1.0)
            score_sum += SequenceMatcher(None, val_orig, val_syn).ratio()

            # Dokumentiert unterschiedliche Werte
            if val_orig != val_syn:
                differences[key] = {
                    "original": val_orig,
                    "synthetic": val_syn
                }

        return {"ähnlichkeit_der_extrahierten_infos": score_sum / total_keys, "unterschiedliche_werte": differences}

def load_text(pfad):
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
    

def main():
    paths = {
        "text_orig": "/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180.txt",
        "text_syn": "/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180s.txt",
        "json_orig": "180.json",
        "json_syn": "180s.json",
    }
    text_orig = load_text(paths["text_orig"])
    text_syn = load_text(paths["text_syn"])
    json_orig = json.load(paths["json_orig"])
    json_syn = json.load(paths["json_syn"])

    evaluator = ArztbriefEvaluator()

    result = {
        "Text Analyse": evaluator.nlp_analysis(text_orig, text_syn),
        "LLM Analyse": evaluator.llm_analysis(text_orig, text_syn),
        "JSON Vergleich": evaluator.json_analysis(json_orig, json_syn),
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()