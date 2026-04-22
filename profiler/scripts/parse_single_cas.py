from dataset_loader import load_case
from pathlib import Path
import re
import json

def parse_sections(case: dict) -> list[dict]:
    root = case["cas_tree"].getroot()
    text = case["cas_text"]
    sections = []
    for sec in root.findall(".//{http:///webanno/custom.ecore}Sectionsentence"):
        begin = int(sec.get("begin"))
        end = int(sec.get("end"))
        section_type = sec.get("Sectiontypes")
        span_text = text[begin:end]
        sections.append({
            "section_type": section_type,
            "begin": begin,
            "end": end,
            "text": span_text
        })
    return sections

def build_section_ranges(sections: list[dict], full_text: str) -> list[dict]:
    sorted_sections = sorted(sections, key=lambda x: x["begin"])
    ranged_sections = []

    for i, sec in enumerate(sorted_sections):
        section_begin = sec["begin"]

        if i < len(sorted_sections) - 1:
            section_end = sorted_sections[i + 1]["begin"]
        else:
            section_end = len(full_text)

        ranged_sections.append({
            "section_type": sec["section_type"],
            "begin": section_begin,
            "end": section_end,
            "text": full_text[section_begin:section_end]
        })

    return ranged_sections

def parse_medications(case: dict) -> list[dict]:
    root = case["cas_tree"].getroot()
    text = case["cas_text"]
    meds = []
    for med in root.findall(".//{http:///webanno/custom.ecore}Medication"):
        begin = int(med.get("begin"))
        end = int(med.get("end"))
        class_type = med.get("ClassType")
        in_narrative = med.get("InNarrative")
        suggested = med.get("Suggested")
        span_text = text[begin:end]
        meds.append({
            "xmi_id": med.get("{http://www.omg.org/XMI}id"),
            "class_type": class_type,
            "begin": begin,
            "end": end,
            "text": span_text,
            "in_narrative": in_narrative,
            "suggested": suggested
        })
    return meds

def parse_medrels(case: dict) -> list[dict]:
    root = case["cas_tree"].getroot()
    rels = []
    for rel in root.findall(".//{http:///webanno/custom.ecore}MedRel"):
        rels.append({
            "xmi_id": rel.get("{http://www.omg.org/XMI}id"),
            "begin": int(rel.get("begin")),
            "end": int(rel.get("end")),
            "dependent": rel.get("Dependent"),
            "governor": rel.get("Governor")
        })
    return rels

def build_medication_lookup(meds: list[dict]) -> dict:
    return {m["xmi_id"]: m for m in meds}


def reconstruct_medications(meds: list[dict], rels: list[dict]) -> list[dict]:
    med_lookup = build_medication_lookup(meds)
    grouped = {}

    for rel in rels:
        dep_id = rel["dependent"]
        gov_id = rel["governor"]

        if gov_id not in med_lookup or dep_id not in med_lookup:
            continue

        governor = med_lookup[gov_id]
        dependent = med_lookup[dep_id]

        if gov_id not in grouped:
            grouped[gov_id] = {
                "governor_id": gov_id,
                "governor_text": governor["text"],
                "governor_class": governor["class_type"],
                "components": []
            }

        grouped[gov_id]["components"].append({
            "xmi_id": dep_id,
            "class_type": dependent["class_type"],
            "text": dependent["text"]
        })

    return list(grouped.values())

def assign_section_to_offset(offset: int, ranged_sections: list[dict]) -> str | None:
    for sec in ranged_sections:
        if sec["begin"] <= offset < sec["end"]:
            return sec["section_type"]
    return None


def assign_sections_to_medications(reconstructed: list[dict], meds: list[dict], ranged_sections: list[dict]) -> list[dict]:
    med_lookup = {m["xmi_id"]: m for m in meds}
    enriched = []

    for rec in reconstructed:
        governor_id = rec["governor_id"]
        governor_med = med_lookup.get(governor_id)

        if governor_med is None:
            section_type = None
        else:
            section_type = assign_section_to_offset(governor_med["begin"], ranged_sections)

        enriched.append({
            **rec,
            "section_type": section_type
        })

    return enriched

def build_simple_medication_objects(reconstructed_with_sections: list[dict], allowed_sections=None) -> list[dict]:
    if allowed_sections is None:
        allowed_sections = ["AufnahmeMedikation", "EntlassMedikation"]

    results = []

    for rec in reconstructed_with_sections:
        if rec["section_type"] not in allowed_sections:
            continue

        med_obj = {
            "drug": rec["governor_text"],
            "dosage": None,
            "frequency": None,
            "section_type": rec["section_type"]
        }

        for comp in rec["components"]:
            if comp["class_type"] == "STRENGTH" and med_obj["dosage"] is None:
                med_obj["dosage"] = comp["text"]
            elif comp["class_type"] == "FREQUENCY" and med_obj["frequency"] is None:
                med_obj["frequency"] = comp["text"]

        results.append(med_obj)

    return results

import re

def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_corpus_artifacts(text: str) -> str:
    text = re.sub(r"<\[Pseudo\][^>]*>", "", text)
    text = text.replace("-LRB-", "(").replace("-RRB-", ")")
    text = text.replace("-UNK-", "")
    text = normalize_whitespace(text)
    text = text.rstrip(".").strip()
    return text


def simplify_for_core(text: str) -> str:
    """
    Conservative simplification for CORE only.
    Removes non-essential temporal/editorial markers,
    but keeps clinically relevant qualifiers.
    """
    text = re.sub(r"\bED\b", "", text)
    text = re.sub(r"\(\s*ED\s*\)", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = normalize_whitespace(text)
    text = text.rstrip(".").strip()
    return text


def clean_diagnosis_text(text: str, level: str = "core") -> str:
    """
    Main diagnosis normalization entry point.
    level='core' -> stronger simplification
    level='extended'/'rich' -> keep more detail
    """
    text = clean_corpus_artifacts(text)

    if level == "core":
        text = simplify_for_core(text)

    return text

def extract_age_from_text(text: str):
    match = re.search(r"Alter:\s*(\d+)", text)
    if match:
        return int(match.group(1))
    return None


def extract_gender_from_text(text: str):
    if "Patientin" in text:
        return "female"
    if "Patient" in text:
        return "male"
    return "unknown"

def extract_admission_date_from_text(text: str):
    match = re.search(r"Aufnahmedatum:\s*<\[Pseudo\]\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*>", text)
    if match:
        return match.group(1)
    return None

def get_section_text(ranged_sections: list[dict], section_type: str) -> str:
    for sec in ranged_sections:
        if sec["section_type"] == section_type:
            return sec["text"]
    return ""


def extract_primary_diagnosis_from_diagnosen_section(diagnosen_text: str):
    lines = diagnosen_text.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("- "):
            return line[2:].strip()
    return None

def extract_comorbidities_from_diagnosen_section(diagnosen_text: str, primary_diagnosis: str):
    comorbidities = []
    lines = diagnosen_text.splitlines()

    EXCLUDE_KEYWORDS = [
        "Score",
        "CHA2DS2",
        "HAS-BLED",
        "Antikoagulation",
        "Antikoagulaiton",
        "Thrombozyten",
        "Therapie",
        "ASS",
        "Rivaroxaban",
        "Xarelto"
    ]

    for line in lines:
        line = line.strip()
        if not line.startswith("- "):
            continue

        entry = line[2:].strip()

        if any(keyword in entry for keyword in EXCLUDE_KEYWORDS):
            continue

        if " mit " in entry:
            continue

        entry = clean_diagnosis_text(entry, level="core")

        if not entry:
            continue

        if primary_diagnosis is not None:
            cleaned_primary = clean_diagnosis_text(primary_diagnosis, level="core")
            if entry == cleaned_primary:
                continue

        comorbidities.append(entry)

    return comorbidities

def build_core_persona(case: dict, ranged_sections: list[dict], simple_meds: list[dict]) -> dict:
    full_text = case["txt"]
    diagnosen_text = get_section_text(ranged_sections, "Diagnosen")

    admission_date = extract_admission_date_from_text(full_text)
    age = extract_age_from_text(full_text)
    gender = extract_gender_from_text(full_text)
    primary_diagnosis = extract_primary_diagnosis_from_diagnosen_section(diagnosen_text)
    if primary_diagnosis is not None:
        primary_diagnosis = clean_diagnosis_text(primary_diagnosis, level="core")
    comorbidities = extract_comorbidities_from_diagnosen_section(diagnosen_text, primary_diagnosis)
    discharge_meds = [
        {
            "drug": m["drug"],
            "dosage": m["dosage"],
            "frequency": m["frequency"]
        }
        for m in simple_meds
        if m["section_type"] == "EntlassMedikation"
    ]

    return {
        "persona_id": f"persona_{case['doc_id']}",
        "source_document_id": case["doc_id"],
        "metadata": {
            "admission_date": admission_date,
            "discharge_date": None
        },
        "core": {
            "age": age,
            "gender": gender,
            "primary_diagnosis": primary_diagnosis,
            "comorbidities": comorbidities,
            "discharge_medications": discharge_meds
        },
        "extensions": {},
        "validation": {
            "schema_validation": {
                "is_valid": True
            },
            "annotation_validation": {
                "performed": False,
                "status": "not_checked"
            },
            "manual_validation": {
                "performed": False
            }
        }
    }

def save_persona_json(persona: dict, output_dir: str = "../outputs/personas_core"):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / f"{persona['source_document_id']}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(persona, f, ensure_ascii=False, indent=2)

    print(f"\nSaved persona JSON to: {file_path}")

if __name__ == "__main__":
    case = load_case("237", "CARDIODE400_main")
    sections = parse_sections(case)
    ranged_sections = build_section_ranges(sections, case["cas_text"])
    meds = parse_medications(case)
    rels = parse_medrels(case)
    reconstructed = reconstruct_medications(meds, rels)
    reconstructed_with_sections = assign_sections_to_medications(
        reconstructed, meds, ranged_sections
    )
    simple_meds = build_simple_medication_objects(reconstructed_with_sections)
    core_persona = build_core_persona(case, ranged_sections, simple_meds)
    save_persona_json(core_persona)
    print("\n=== SECTIONS ===")
    for s in sections:
        print(s)
    print("\n=== FULL SECTION RANGES ===")
    for rs in ranged_sections:
        print({
            "section_type": rs["section_type"],
            "begin": rs["begin"],
            "end": rs["end"],
            "preview": rs["text"][:120].replace("\n", " ")
        })
    print("\n=== MEDICATION SPANS ===")
    for m in meds[:20]:
        print(m)
    print("\n=== MEDICATION RELATIONS ===")
    for r in rels[:20]:
        print(r)
    print("\n=== RECONSTRUCTED MEDICATION GROUPS ===")
    for rec in reconstructed[:20]:
        print(rec)
    print("\n=== RECONSTRUCTED MEDICATION GROUPS WITH SECTIONS ===")
    for rec in reconstructed_with_sections[:20]:
        print(rec)
    print("\n=== SIMPLE MEDICATION OBJECTS ===")
    for med in simple_meds:
        print(med)
    print("\n=== CORE PERSONA ===")
    print(core_persona)
