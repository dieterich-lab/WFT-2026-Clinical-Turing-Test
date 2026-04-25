import json
import os
import urllib.request

base = os.environ["OLLAMA_URL"]
extract_model = "llama3.1:8b"
generate_model = os.environ["OLLAMA_MODEL"]  # your generation model

sample_letter = """
Entlassungsbrief
Aufnahmedatum: <[Pseudo] 2040-01-01 >
Geburtsdatum: <[Pseudo] 1962-12-02 >
Alter: 77

über Ihren Patienten B-SALUTE B-PER I-PER geboren am <[Pseudo] 02/12/1962> wh. B-PLZ B-LOC I-ADDR I-ADDR I-ADDR der sich am in unserer Ambulanz vorstellte.

Aktuell:
- Verlaufskontrolle bei bikuspider Aortenklappe und Aneurysma der Aorta ascendens
-UNK- Echokardiographisch Aorta ascendens 50mm Durchmesser
-UNK- Echokardiographisch gute biventrikuläre Funktion -LRB- LV EF: 54% -RRB-
-UNK- Ad ambulante Verlaufskontrolle in 6 Monaten

Diagnosen:
- Aneurysma der Aorta ascendens ED B-DATE
-UNK- TTE B-DATE: Aorta ascendens 50mm -LRB- Wachstum 5mm in 2 Jahren -RRB-
-UNK- MRT B-DATE: Aorta ascendens 52mm -LRB- in domo mit 51mm beschrieben -RRB-
-UNK- TTE B-DATE: Aorta ascendens 50mm
-UNK- TTE B-DATE: Aorta ascendens 48mm -LRB- anamnestisch -RRB-
-UNK- TTE B-DATE: Aorta ascendens 45mm -LRB- anamnestisch -RRB-
- Bikuspide Aortenklappe ED <[Pseudo] 2036>
-UNK- Echokardiographisch bikuspide Aortenklappe mit Raphe zwischen der rechts- und linkskoronaren Aortentasche
-UNK- regelrechte Funktion -LRB- keine AI, keine AS -RRB- -LRB- <[Pseudo] 06/2039> -RRB-
Kardiovaskuläre Risikofaktoren: Arterielle Hypertonie

Allergien: keine bekannt
Anamnese:


Die ambulante Vorstellung erfolgt zur kardiologischen Verlaufskontrolle bei bekanntem Aneurysma der Aorta ascendens sowie funktionell bikuspider Aortenklappe. Im Alltag bestehe eine uneingeschränkte Belastbarkeit -LRB- mehrere Etagen Treppensteigen möglich -RRB- . Es bestehen keine pectanginösen Beschwerden in Ruhe oder bei Belastung. Palpitationen, Schwindel sowie stattgehabte Synkopen werden verneint. Es bestehe keine relevante Nykturie. Periphere Ödeme seien bei Gewichtskonstanz -LRB- 80 kg -RRB- nicht aufgefallen. Die regelmäßigen häuslichen Blutdruckmessungen -LRB- 2x täglich -RRB- ergäben Werte um 120/60mmHg. Subjektiv bestehe seit der letzten Vorstellung ein stabiler kardialer Verlauf.
Bisherige Medikation:

Candesartan/HCT 16mg/12,5mg 1-0-0
Körperliche Untersuchung:

AZ: gut
EZ: 176 cm 80 kg
HF: 60/min, regelmäßig
RR: 120/80 mmHg
Keine Cyanose, Anämiezeichen, Ikterus.
HT: rein, keine path. Geräusche
Lunge: vesikuläres AG, keine NG
Periphere Ödeme: keine
sonstige Auffälligkeiten: keine
Ruhe-EKG:

Normofrequenter Sinusrhythmus, Hf 62/min, überdrehter Linkstyp. PQ194 ms, QRS 115 ms, QTc 418 ms. Regelrechte R-Progression, R/S Umschlag in V5/V6, LAHB. Keine signifikanten Erregungsrückbildungsstörungen.
Transthorakale Echokardiographie:

Normal großer, septal betont hypertrophierter linker Ventrikel mit guter systolischer Pumpfunktion ohne abgrenzbare regionale Kontraktionsstörungen. Erhaltene longitudinale Funktion. Relaxationsstörung des LV. LA dilatiert, RA und RV normal groß, gute RV-Funktion. Hypermobiles Vorhofseptum. Kein Perikarderguss nachweisbar. Vena cava inferior nicht gestaut. Ektasie der Aortenwurzel -LRB- 45 mm -RRB- , Aneurysma der Aorta ascendens -LRB- max. 50 mm, soweit einsehbar -RRB- . Aortenklappe verdickt mit guter Separation. Mitralklappe leicht verdickt mit guter Separation. Übrige Klappen sonographisch und dopplersonographisch regelrecht. Systolischer PA-Druck in Ruhe ist normal -LRB- ca. 25mmHg -RRB- . Im Vergleich zur Voruntersuchung vom <[Pseudo] 26/06/2039:> Keine wesentliche Befundänderung.
Zusammenfassung:

Die Vorstellung in der B-ORG I-ORG erfolgte zur Verlaufskontrolle bei bekanntem Aneurysma der Aorta ascendens sowie bei bikuspider Aortenklappe -LRB- ED <[Pseudo] 2036> -RRB- . Vor 6 Monaten sei in der interdisziplinären Herzkatheter-Konferenz <[Pseudo] 06/2039> bei biskupider Aortenklappe und grenzwertigem Aneurysma-Durchmesser -LRB- 50mm -RRB- ohne zusätzliche Risikofaktoren ein konservatives Procedere festgelegt worden.

Echokardiographisch zeigte sich das Aneurysma in der Aorta ascendens mit 50mm zur Voruntersuchung vom <[Pseudo] 26/06/2039> unverändert. Es zeigte sich zudem ein septal betont hypertrophierter linker Ventrikel mit guter systolischer Pumpfunktion. Es besteht eine diastolische Relaxationsstörung. Sonst zeigten sich keine weiteren Auffälligkeiten.

Bei Aneurysma der Aorta ascendens mit bikuspider Aortenklappe besteht im Falle eines Durchmessers von ≥ 50mm mit bestehendem Risikofaktor -LRB- u.a. hypertone Blutdruckwerte, Wachstumsgeschwindigkeit 3mm/Jahr -RRB- nach aktuellen Leitlinien ein 2a Empfehlungsgrad zur operativen Versorgung des Aneurysmas. Bei Befundkonstanz -LRB- weiterhin grenzwertiger Durchmesser der Aorta ascendens mit 50 mm im TTE -RRB- , klinisch vollständiger Beschwerdefreiheit sowie engmaschig dokumentierten normotensiven Blutdruckwerten empfehlen wir eine echokardiographische Verlaufskontrolle des Aorta ascendens Aneurysmas in 6 Monaten, gerne wie bereits vereinbart ambulant.

Wir bitten um eine weiterhin strenge Blutdruckeinstellung mit Blutdruckwerten <130/80mmHg und um eine Fortführung der häuslichen Blutdruckmessungen -LRB- mind. 2x/Tag -RRB- . Maximale Belastungsspitzen sind zu vermeiden, während moderate körperliche Aktivitäten präventiv wirken.

Bei Auftreten von Beschwerden sind wir jederzeit gerne bereit, B-SALUTE B-PER wiederzusehen, in Notfällen über unsere B-ORG I-ORG I-ORG unter B-PHONE
Aktuelle Medikation:

Candesartan/HCT 16mg/12,5mg 1-0-0

Selbstverständlich können Präparate mit gleichem Wirkstoff und gleicher Wirkung von anderen Herstellern verordnet werden.

Wir danken für die vertrauensvolle Zusammenarbeit und stehen bei Rückfragen selbstverständlich jederzeit gerne zur Verfügung.
Mit freundlichen Grüßen


B-PER
B-TITLE I-TITLE I-TITLE B-PER I-PER B-TITLE I-TITLE I-TITLE B-PER I-PER B-PER I-PER
Ärztlicher Direktor Oberarzt Assistenzarzt

"""

def query_ollama(model, prompt):
    payload = {"model": model, "prompt": prompt, "stream": False}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body.get("response", "").strip()

# Step 1: Extract structured info
extract_prompt = f"""Extrahiere folgende Felder aus diesem Entlassungsbrief als JSON, ohne Erklärung:
- Patienten_Alter
- Aufnahme_Datum
- Entlassungs_Datum
- Diagnose(Liste)
- Risiko_Faktoren (Liste)
- Medikamente (Liste mit Dosis)
- ekg (Herzfrequenz
        * PQ-Zeit, QRS-Zeit, QTc-Zeit)
- echo (EF, Befund)
- labor (relevante Werte)
- anamnesis (1-2 Sätze)
- Empfehlungen

Brief:
{sample_letter}

Antworte nur mit validem JSON."""

print("Step 1: Extracting structured data...")
extracted_json = query_ollama(extract_model, extract_prompt)
print("Extracted:\n", extracted_json)

# Step 2: Generate new letter
generate_prompt = f"""Im Rahmen eines Turing-Test Experiments, sollst du die Rolle eines deutschen Kardiologen einnehmen und einen Entlassungsbrief generieren.
Erstelle auf Basis der folgenden strukturierten Daten einen realistischen, professionellen kardiologischen Entlassungsbrief auf Deutsch. Kopiere nicht das Original - Generiere plausible, jedoch funktionale Patienten Details.

Strukturierte Daten:
{extracted_json}

"""

print("\nStep 2: Generating synthetic letter...")
synthetic_letter = query_ollama(generate_model, generate_prompt)
print("\nSynthetic Letter:\n", synthetic_letter)
