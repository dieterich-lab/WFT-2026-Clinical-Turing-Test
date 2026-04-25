import json
import os
import urllib.request

base = os.environ["OLLAMA_URL"]
model = os.environ["OLLAMA_MODEL"]

sample_letter = """
Entlassungsbrief

Patient: Max Mustermann, geb. 01.03.1952
Aufnahme: 10.04.2024, Entlassung: 17.04.2024

Diagnosen:
- Akutes Koronarsyndrom (NSTEMI)
- Arterielle Hypertonie
- Hypercholesterinämie

Anamnese:
Der Patient stellte sich mit seit zwei Tagen zunehmenden Brustschmerzen und Belastungsdyspnoe vor.
Bekannte arterielle Hypertonie, bisher medikamentös eingestellt.

Befunde:
EKG: ST-Senkungen in V4-V6. Troponin I initial 1.2 ng/ml, im Verlauf ansteigend auf 4.7 ng/ml.
Echokardiographie: Leichtgradig eingeschränkte LV-Funktion, EF 48%.
Koronarangiographie: Signifikante Stenose der LAD (75%), PTCA mit Stentimplantation durchgeführt.

Verlauf:
Interventionell unkomplizierter Verlauf. Unter medikamentöser Therapie beschwerdefrei.

Medikation bei Entlassung:
- Aspirin 100mg 1-0-0
- Clopidogrel 75mg 1-0-0
- Metoprolol 47.5mg 1-0-1
- Ramipril 5mg 1-0-0
- Atorvastatin 40mg 0-0-1

Empfehlungen:
Kardiologische Nachkontrolle in 4 Wochen. Herzgesunde Lebensführung empfohlen.
"""

prompt = f"""Here is a real cardiology discharge letter:

{sample_letter}

If I asked you to generate a new, realistic discharge letter in the same style, what structured information would you need as input? List only what is essential."""

payload = {
    "model": model,
    "prompt": prompt,
    "stream": False,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{base}/api/generate",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=300) as resp:
    body = json.loads(resp.read().decode("utf-8"))

print("Model:", model)
print("\nResponse:\n")
print(body.get("response", "").strip())