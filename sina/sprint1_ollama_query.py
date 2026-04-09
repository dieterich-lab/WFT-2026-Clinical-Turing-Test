import json
import os
import urllib.request

base = os.environ["OLLAMA_URL"]
model = os.environ["OLLAMA_MODEL"]

zeroshotprompt = """Du bist eine Ärztin und sollst einen Vorschlag für einen Entlassbrief für eine deiner Patientinnen schreiben.
            Verfasse einen klaren, strukturierten, realistischen und professionellen Entlassbrief für eine
            75-jährige Patientin mit Herzinsuffizienz. Beachte dabei die aktuellen medizinischen Leitlinien."""

fewshotprompt = """Du bist eine Ärztin und sollst einen Entlassbrief für eine deiner Patientinnen schreiben. Hier ist ein Beispiel für einen gut strukturierten Entlassbrief: 

---

Patientendaten:
Alter: 68 Jahre
Geschlecht: männlich

Aufnahmediagnose:
Ambulant erworbene Pneumonie

Krankenhausverlauf:
Der Patient wurde mit Fieber, Husten und Dyspnoe aufgenommen. Im Röntgen-Thorax zeigte sich eine Pneumonie. Unter intravenöser Antibiotikatherapie kam es innerhalb von 5 Tagen zu einer klinischen Besserung.

Therapie:
IV Ceftriaxon und Azithromycin, Sauerstofftherapie

Entlassmedikation:
Amoxicillin/Clavulansäure oral für 5 Tage

Nachsorge / Empfehlungen:
Vorstellung beim Hausarzt in 1 Woche. Bei Verschlechterung erneute Vorstellung.

---

Verfasse einen klaren, strukturierten, realistischen und professionellen Entlassbrief für eine
75-jährige Patientin mit Herzinsuffizienz. Beachte dabei die aktuellen medizinischen Leitlinien.

Behalte die gleiche Struktur und Detailtiefe bei. Übernimm keine Inhalte aus dem Beispiel."""

payload = {
  "model": model,
  "prompt": fewshotprompt,
  "stream": False,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
  f"{base}/api/generate",
  data=data,
  headers={"Content-Type": "application/json"},
  method="POST",
)

with urllib.request.urlopen(req, timeout=120) as resp:
  body = json.loads(resp.read().decode("utf-8"))

print("Model:", model)
print("Response:", body.get("response", "").strip())