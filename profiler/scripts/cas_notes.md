# CAS Notes

CAS Structure:
- cas:Sofa
  → contains full document text

- Sectionsentence
  → defines sections e.g. Diagnose, Medikation, Anamnese

- Medication
  → annotated spans with ClassType:
    - DRUG
    - STRENGTH
    - FREQUENCY
    - DURATION
    - ACTIVEING

- MedRel
  → connects medication components such as frequency or duration

Important:
- Medication is structured via spans and relations
- Diagnoses are mostly represented via sections and not entities
