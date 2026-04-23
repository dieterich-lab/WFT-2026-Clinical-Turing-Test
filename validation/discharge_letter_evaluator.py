import json
import ollama
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer
from difflib import SequenceMatcher
from nlp_processor import NLPProcessor


base ="http://127.0.0.1:11434"
model = "llama3.1:8b"

class ArztbriefEvaluator:
    """
    Diese Klasse bietet Methoden zur Bewertung von synthetischen Arztbriefen im Vergleich zu Originalbriefen.
    Sie nutzt NLP-Techniken, um verschiedene Metriken zu extrahieren und vergleicht die Briefe sowohl inhaltlich als auch stilistisch.
    Dabei werden sowohl klassische NLP-Metriken (z.B. Jaccard-Index, ROUGE) als auch eine Analyse durch ein LLM (Ollama) verwendet.
    Zusätzlich ermöglicht die Klasse den Vergleich von extrahierten Informationen aus JSON-Daten, um die Konsistenz der Informationen zwischen Original und synthetischem Brief zu bewerten.
    """
    def __init__(self, model_name=model, ollama_host=base):
        # Initialisierung des LLM-Clients
        self.model_name = model_name
        self.client = ollama.Client(host=ollama_host)
        
        # NLP-Prozessor basierend auf spaCy für die Extraktion von Metriken aus den Texten
        self.nlp = NLPProcessor()
        # ROUGE-Scorer für die Bewertung der inhaltlichen Ähnlichkeit auf Basis von Lemmas (deutsche Sprache)
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ["rouge1", "rouge2", "rougeL"],
            use_stemmer=False # Statt Stemming werden Lemmas aus dem NLP-Prozessor genutzt (besser für Deutsch)
        )

    def nlp_analysis(self, original_letter, synthethic_letter):
        """
        Führt eine quantitative Analyse der beiden Briefe durch, indem verschiedene NLP-Metriken extrahiert und verglichen werden.
        Es werden folgende Metriken berechnet:
        - Jaccard-Index der Keywords (Nomen & Eigennamen)
        - Semantische Ähnlichkeit basierend auf Vektoren
        - ROUGE-Score basierend auf lemmatisierten Texten
        - LIX-Index zur Bewertung der Lesbarkeit
        - Nominalstil-Index (Nomen zu Verben Verhältnis)
        - Satzlängen-Varianz (Burstiness)
        Die Ergebnisse werden in einem Dictionary zurückgegeben, das die Ähnlichkeit und Unterschiede zwischen den beiden Briefen aufzeigt.
        """

        # Extraktion von NLP-Metriken aus beiden Briefen
        orig = self.nlp.extract_metrics(original_letter)
        syn = self.nlp.extract_metrics(synthethic_letter)
        
        # Jaccard Ähnlichkeit: Misst Überlappung der Keywords (Nomen & Eigennamen) zwischen Original und synthetischem Brief
        intersection = len(orig['keywords'].intersection(syn['keywords']))
        union = len(orig['keywords'].union(syn['keywords']))
        jaccard = intersection / union if union > 0 else 0
        
        # Semantische Ähnlichkeit (Vektoren)
        semantic_sim = cosine_similarity([orig['vector']], [syn['vector']])[0][0]

        # ROUGE mit deutschen Lemmata
        rouge_scores = self.rouge_scorer.score(orig['lemmatized_text'], syn['lemmatized_text'])

        return {
            "Semantische Ähnlichkeit": f"{semantic_sim:.2%}",
            "Inhaltliche Deckung (Jaccard)": f"{jaccard:.2%}",
            "Lesbarkeitsindex (LIX)": {
                "Original": orig['lix'],
                "Synthetisch": syn['lix'],            
                "Differenz": abs(orig['lix'] - syn['lix'])
            },
            "Nominalstil": {
                "Original": round(orig['nominal_ratio'], 2),
                "Synthetisch": round(syn['nominal_ratio'], 2),
                "Differenz": round(abs(orig['nominal_ratio'] - syn['nominal_ratio']), 2)
            },
            "Satzlängen-Varianz (Burstiness)": {
                "Original": round(orig['variance'], 2),
                "Synthetisch": round(syn['variance'], 2),
                "Verhältnis": round(orig['variance'] / (syn['variance'] + 1e-6), 2) # Verhältnis der Varianzen, um die relative Burstiness zu bewerten
            },
            "ROUGE-Scores": {
                "rouge1": rouge_scores["rouge1"].fmeasure, # F1-Score für ROUGE-1 (unigram overlap)
                "rouge2": rouge_scores["rouge2"].fmeasure, # F1-Score für ROUGE-2 (bigram overlap)
                "rougeL": rouge_scores["rougeL"].fmeasure # F1-Score für ROUGE-L (längste gemeinsame Teilfolge)
            }
        }

    def llm_analysis(self, original_letter, synthetic_letter):
        """
        Qualitative Analyse durch ein LLM zur Bewertung der Ähnlichkeit beider Briefe.
        """

        prompt = f"""
        Analysiere diese zwei Arztbriefe auf ihre stilistische Ähnlichkeit. 
        Bewerte die fachliche klinische Deckung sowie die Linguistik.

        BRIEF 1: "{original_letter}"
        BRIEF 2: "{synthetic_letter}"

        Erstelle ein JSON mit:
        - "stil_vergleich": (Wie ähnlich ist der Schreibstil in %? )
        - "medizinische_praezision": (Nutzen beide die gleiche Fachterminologie?)
        - "konsistenz_bewertung": 1-100 % (Wie konsistent sind die Informationen zwischen beiden Briefen? Gibt es Widersprüche?)
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
        """
        Vergleicht die extrahierten Informationen aus den JSON-Daten der Original- und synthetischen Briefe.
        Es wird die Ähnlichkeit der Werte für jede Schlüssel-Information berechnet, um dieKonsistenz der extrahierten Informationen zwischen beiden Briefen zu bewerten.
        Die Ergebnisse werden in einem Dictionary zurückgegeben, das die durchschnittliche Ähnlichkeit der extrahierten Informationen sowie die spezifischen Unterschiede zwischen den beiden JSON-Datensätzen aufzeigt.
        """

        differences = {}
        score_sum = 0

        # Vereinigung aller Schlüssel aus beiden JSONs
        total_keys = len(set(json_original.keys()).union(set(json_syntetic.keys())))
        if total_keys == 0: return 1.0

        for key in set(json_original.keys()).union(set(json_syntetic.keys())):
            val_orig = json_original.get(key)
            val_syn = json_syntetic.get(key)

            # Berechnung der Ähnlichkeit der einzelnen Werte (0.0 bis 1.0)
            if isinstance(val_orig, list) and isinstance(val_syn, list):
                # Listen werden als Strings zusammengeführt
                score = SequenceMatcher(None, " ".join(map(str, val_orig)), " ".join(map(str, val_syn))).ratio()
            else:
                # Alle anderen Werte werden direkt als Strings verglichen
                score = SequenceMatcher(None, str(val_orig), str(val_syn)).ratio()
            score_sum += score

            # Dokumentation der Unterschiede
            if val_orig != val_syn:
                differences[key] = {
                    "original": val_orig,
                    "synthetic": val_syn
                }

        return {"Ähnlichkeit der extrahierten Infos": score_sum / total_keys, "Unterschiedliche Werte": differences}

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

def load_json(pfad):
    with open(pfad, 'r') as f:
        return json.load(f)


paths = {
    "text_orig": "/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180.txt",
    "text_syn": "/home/sthuerwaechter/WFT-2026-Clinical-Turing-Test/validation/180s.txt",
    "json_orig": "180.json",
    "json_syn": "180s.json",
}
text_orig = load_text(paths["text_orig"])
text_syn = load_text(paths["text_syn"])
json_orig = load_json(paths["json_orig"])
json_syn = load_json(paths["json_syn"])

evaluator = ArztbriefEvaluator()

result = {
    "Text Analyse": evaluator.nlp_analysis(text_orig, text_syn),
    "LLM Analyse": evaluator.llm_analysis(text_orig, text_syn),
    "JSON Vergleich": evaluator.json_analysis(json_orig, json_syn),
}

print(json.dumps(result, indent=2, ensure_ascii=False))
