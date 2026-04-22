### Contract

**Pipeline**
- [ ] Arztbrief liegt als txt vor
- [ ] Annotationen des Arztbrief liegen als cas vor
- [ ] Bauen eines Annotation Parser um die strukturierten Annotation auszulesen
- [ ] LLM Baseline Extraktion des txt Arztbriefs 
- [ ] Überführen in eine Clincical Persona (JSON)
- [ ] Validation (Vergleich der Extraktionsergebnisse mit den Annotationen)

**Validation**
| Typ | Prüft |
| :--- | :--- | 
| Schema Validation | Struktur & Datentypen | 
| Annotation Validation | Inhalt vs. Ground Truth / vgl. mir cas-Datei | 
| Manual Validation | menschliche Kontrolle  | 

**Contract und Extraction Levels**
-> Der Contract wurde beispielhaft auf Basis von 237.txt aufgebaut

Low-Level Template: 
{
  "persona_id": string,
  "source_document_id": string,
  "metadata": { ... },
  "core": { ... },
  "extensions": { ... },
  "validation": { ... }
}

**Top Level Felder und Meta Daten** 
persona_id: string  | eindeutig pro Persona
source_document_id: string 
metadata admission_date: date 
metadata  discharge_date: date | null

Bsp.
```json
{
  "persona_id": "persona_001",
  "source_document_id": "1",
  "metadata": {
    "admission_date": "2044-02-01",
    "discharge_date": null
  }
}
```
### 1. Extraction Level CORE
CORE enthält alle stabilen Pflichtinformationen. Die Primary Diagnose ist vereinfacht, es gibt keine Scores und Zusatzinfos wie sie im original Arztbrief vorkommen. 

age: int | null,
gender: "male" | "female" | "unknown",
primary_diagnosis: string | null,
comorbidities: list[string], die `primary_diagnosis` darf hier nicht erneut auftauchen, nicht erlaubt sind Scores oder weitere Informationen
discharge_medications: list[object]

Bsp.
```json
{
  "persona_id": "persona_001",
  "source_document_id": "1",
  "metadata": {
    "admission_date": "2044-02-01",
    "discharge_date": null
  },

  "core": {
    "age": 39,
    "gender": "male",
    "primary_diagnosis": "paroxysmalem Vorhofflimmern",
    "comorbidities": [
      "Polyzythämia vera",
      "arterielle Hypertonie"
    ],
    "discharge_medications": [
      {
        "drug": "Xarelto",
        "dosage": "20mg",
        "frequency": "1-0-0"
      }
    ]
  },

  "extensions": {},

  "validation": {
    "schema_validation": {
      "is_valid": true
    },
    "annotation_validation": {
      "performed": true,
      "status": "partial_match"
    },
    "manual_validation": {
      "performed": false
    }
  }
}
```
### 2. Extraction Level EXTENDED
Mehr als CORE, aber noch strukturiert und stabil. Die Struktur bleibt gleich wie bei CORE. Zusätzliche klinische Informationen wie frühere Diagnosen, Anamnese, Symptome und Prozeduren werden über extensions ergänzt. Scores und komplexe klinische Skalen nicht erlaubt. 

-> Die Felder sind nicht fix, gerne weiteren Input liefern!

age: int | null,
gender: "male" | "female" | "unknown",
primary_diagnosis: string | null,
comorbidities: list[string], die `primary_diagnosis` darf hier nicht erneut auftauchen, nicht erlaubt sind Scores oder weitere Informationen
discharge_medications: list[object]
**-> neu dazu kommen:**
previous_diagnoses: list[{ name: string, year: int | null }],
anamnesis: list[{ 
                        type: "risk_factor" | "family_history" | "lifestyle" | "previous_condition",
                        value: string }],
symptoms: list[string],
procedures: list[string],

Bsp. 
```json
{
  "persona_id": "persona_001",
  "source_document_id": "1",
  "metadata": {
    "admission_date": "2044-02-01",
    "discharge_date": null
  },

  "core": {
    "age": 39,
    "gender": "male",
    "primary_diagnosis": "paroxysmalem Vorhofflimmern",
    "comorbidities": [
      "Polyzythämia vera",
      "arterielle Hypertonie"
    ],
    "discharge_medications": [
      {
        "drug": "Xarelto",
        "dosage": "20mg",
        "frequency": "1-0-0"
      }
    ]
  },

  "extensions": {
    "previous_diagnoses": [
      {
        "name": "Myokardinfarkt",
        "year": 2018
      },
      {
        "name": "Schlaganfall",
        "year": 2020
      }
    ],
    "anamnesis": [
      {
        "type": "risk_factor",
        "value": "aktiver Nikotinkonsum"
      }
    ],
    "symptoms": [
      "Palpitationen"
    ],
    "procedures": [
      "Belastungs-EKG",
      "transthorakale Echokardiographie"
    ]
  },

  "validation": {
    "schema_validation": {
      "is_valid": true
    },
    "annotation_validation": {
      "performed": true,
      "status": "partial_match"
    },
    "manual_validation": {
      "performed": false
    }
  }
}
```
### 3. Extraction Level RICH
RICH enthält alle verfügbaren Informationen aus dem Arztbrief inklusive Kontext, Nachvollziehbarkeit und klinische Details. Felder dürfen zusätzliche Strukturen, Evidenz und detaillierte klinische Informationen enthalten. -> Mögliche Quelle von Fehlinterpretation. RICH enthält zudem Informationen zur evidence um maximale Nachvollziehbarkeit zu gewährleisten. Metadaten bleiben gleich. 

Im RICH Level werden vorher als einfache Felder (z.B. String) durch JSON-Objekte ersetzt um die zusätzlichen Informationen besser abbilden zu können.

Bsp.
```json
{
  "persona_id": "persona_001",
  "source_document_id": "1",
  "metadata": {
    "admission_date": "2044-02-01",
    "discharge_date": null
  },

  "core": {
    "age": {
      "value": 39,
      "evidence": [
        {
          "section": "header",
          "quote": "Alter: 39"
        }
      ]
    },
    "gender": {
      "value": "male",
      "evidence": [
        {
          "section": "intro",
          "quote": "Patient"
        }
      ]
    },
    "primary_diagnosis": {
      "name": "paroxysmales Vorhofflimmern",
      "icd10": null,
      "confidence": "confirmed",
      "severity": null,
      "evidence": [
        {
          "section": "Aktuell",
          "quote": "Mitbeurteilung bei paroxysmalem Vorhofflimmern"
        }
      ]
    },
    "comorbidities": [
      {
        "name": "arterielle Hypertonie",
        "icd10": null,
        "status": "active",
        "evidence": [
          {
            "section": "Kardiovaskuläre Risikofaktoren",
            "quote": "Arterielle Hypertonie"
          }
        ]
      },
      {
        "name": "Polyzythämia vera",
        "icd10": null,
        "status": "active",
        "evidence": [
          {
            "section": "Vorerkrankungen",
            "quote": "Polyzythämia vera"
          }
        ]
      }
    ],
    "discharge_medications": [
      {
        "drug": "Xarelto",
        "dose": "20mg",
        "frequency": "1-0-0",
        "indication": "Schlaganfallprophylaxe bei Vorhofflimmern",
        "evidence": [
          {
            "section": "Therapieempfehlung",
            "quote": "Xarelto 20mg 1-0-0"
          }
        ]
      }
    ]
  },

  "extensions": {
    "previous_diagnoses": [
      {
        "name": "Myokardinfarkt",
        "year": 2018
      },
      {
        "name": "Schlaganfall",
        "year": 2020
      }
    ],
    "anamnesis": [
      {
        "type": "risk_factor",
        "value": "aktiver Nikotinkonsum",
        "evidence": [
          {
            "section": "Anamnese",
            "quote": "aktiver Nikotinkonsum"
          }
        ]
      }
    ],
    "symptoms": [
      {
        "name": "Palpitationen",
        "severity": null,
        "temporal": "episodisch",
        "evidence": [
          {
            "section": "Aktuell",
            "quote": "Palpitationen"
          }
        ]
      }
    ],
    "procedures": [
      {
        "name": "Belastungs-EKG",
        "date": null,
        "outcome": "kein Hinweis auf Ischämie",
        "evidence": [
          {
            "section": "Diagnostik",
            "quote": "Belastungs-EKG ohne Ischämienachweis"
          }
        ]
      },
      {
        "name": "transthorakale Echokardiographie",
        "date": null,
        "outcome": "normale linksventrikuläre Funktion",
        "evidence": [
          {
            "section": "Diagnostik",
            "quote": "normale linksventrikuläre Funktion"
          }
        ]
      }
    ],
    "scores": [
      {
        "name": "CHA2DS2-VASc",
        "value": 1,
        "unit": null,
        "interpretation": "niedriges Schlaganfallrisiko",
        "evidence": [
          {
            "section": "Risikobewertung",
            "quote": "CHA2DS2-VASc Score 1"
          }
        ]
      },
      {
        "name": "HAS-BLED",
        "value": 0,
        "unit": null,
        "interpretation": "geringes Blutungsrisiko",
        "evidence": [
          {
            "section": "Risikobewertung",
            "quote": "HAS-BLED Score 0"
          }
        ]
      }
    ]
  },

  "validation": {
    "schema_validation": {
      "is_valid": true
    },
    "annotation_validation": {
      "performed": true,
      "status": "partial_match"
    },
    "manual_validation": {
      "performed": false
    }
  }
}
```
