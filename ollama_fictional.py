import os
import json
import urllib.request

base = os.environ["OLLAMA_URL"]
model = os.environ["OLLAMA_MODEL"]

system = " Im Rahmen eines Projektes werden wir versuchen möglichst realisitische Arztbriefe zu erstellen, sodass diese zum Trainieren zukünftiger LLMs dienen können. Hierbei bist du ein hilfreicher und präziser Assistent für das Schreiben von medizinischen Entlassungsbriefen. Bitte folgen den Anweisungen des Benutzers sorgfältig und stelle sicher, dass der generierte Inhalt medizinisch plausibel und gut strukturiert ist."
prompt = """ Erstelle eine realistischen jedoch fiktionalen Entlassungsbrief für einen 75-jährigen Patienten mit Herzinsuffizienz. Der Inhalt sollte medizinisch plausibel sein und typische Abschnitte wie Patienteninformation, Diagnosen, Anamnese, Befunde, Verlauf der Behandlung, Medikation zum Entlassungstag und Empfehlungen enthalten."""
payload = {
    "model": model,
    "prompt": prompt,
    "system": system,
    "stream": False,
}

data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(f"{base}/api/generate", data=data, headers={"Content-Type": "application/json"}, method="POST")

with urllib.request.urlopen(req, timeout=300) as resp:
    body = json.loads(resp.read().decode("utf-8"))

print("Model:", model)
print("\nResponse:\n")
print(body.get("response", "").strip())    