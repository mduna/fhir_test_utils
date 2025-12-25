#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUR (Antimicrobial Use and Resistance) Test Case Generator

Protocol Definition:
- AU Option: Tracks antimicrobial days of therapy
- AR Option: Tracks antimicrobial resistance events
- Hospital Day 1 = Admission date
- HO (Hospital-Onset) = Day 4+
- CO (Community-Onset) = Day 1-3
- Measurement Period: 2025-01-01 to 2025-01-31

Test Cases Generated (17 total):
AU Option (7):
1. Basic inpatient IV antimicrobial
2. Multiple antimicrobials same day
3. Patient transfer between locations
4. ED encounter with oral antimicrobial
5. Multi-day stay spanning months
6. Inhaled antimicrobial
7. No antimicrobial administration

AR Option (10):
1. Hospital-onset MRSA bacteremia
2. Community-onset E. coli UTI
3. Carbapenem-resistant Klebsiella (CRE)
4. Vancomycin-resistant Enterococcus (VRE)
5. Same-day duplicate cultures
6. 14-day window deduplication
7. MDR Pseudomonas aeruginosa
8. Negative culture
9. Carbapenem-resistant Acinetobacter
10. ED encounter with positive culture

Usage:
    cd protocols/aur
    python generate_aur_tests.py
    # Output: NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip
"""

import sys
import os

# Add parent of fhir_test_utils to path for package imports
# Path: fhir_test_utils/protocols/aur/generate_aur_tests.py
# We need to go up 3 levels to fhir_test_utils, then 1 more to its parent
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, root_dir)

from fhir_test_utils import FHIRBundleGenerator, MADiEExporter
from fhir_test_utils.code_systems import CODE_SYSTEMS


# =============================================================================
# AUR Protocol Constants
# =============================================================================

HO_TIMING_THRESHOLD = 4  # Hospital day 4+ qualifies as hospital-onset
MEASUREMENT_PERIOD_START = "2025-01-01"
MEASUREMENT_PERIOD_END = "2025-01-31"

# LOINC code for blood culture
BLOOD_CULTURE_LOINC = "600-7"
BLOOD_SPECIMEN_SNOMED = "119297000"
URINE_SPECIMEN_SNOMED = "122575003"
SPUTUM_SPECIMEN_SNOMED = "119334006"

# Antimicrobial RxNorm codes
ANTIMICROBIALS = {
    "meropenem": {"code": "1722939", "display": "Meropenem 1000 MG Injection"},
    "vancomycin": {"code": "1664986", "display": "Vancomycin 1000 MG Injection"},
    "ceftriaxone": {"code": "309090", "display": "Ceftriaxone 1000 MG Injection"},
    "pip_tazo": {"code": "1659149", "display": "Piperacillin 4000 MG / Tazobactam 500 MG Injection"},
    "ciprofloxacin_oral": {"code": "309309", "display": "Ciprofloxacin 500 MG Oral Tablet"},
    "tobramycin_inh": {"code": "1165258", "display": "Tobramycin 300 MG/5ML Inhalation Solution"},
    "amikacin": {"code": "1665021", "display": "Amikacin 1000 MG Injection"},
}

# Routes of Administration (SNOMED)
ROUTES = {
    "iv": {"code": "47625008", "display": "Intravenous route"},
    "oral": {"code": "26643006", "display": "Oral route"},
    "inhalation": {"code": "447694001", "display": "Respiratory tract route"},
    "im": {"code": "78421000", "display": "Intramuscular route"},
}

# Organism SNOMED codes
ORGANISMS = {
    "s_aureus": {"code": "3092008", "display": "Staphylococcus aureus"},
    "e_coli": {"code": "112283007", "display": "Escherichia coli"},
    "k_pneumoniae": {"code": "56415008", "display": "Klebsiella pneumoniae"},
    "p_aeruginosa": {"code": "52499004", "display": "Pseudomonas aeruginosa"},
    "e_faecium": {"code": "90272000", "display": "Enterococcus faecium"},
    "a_baumannii": {"code": "91288006", "display": "Acinetobacter baumannii"},
    "no_growth": {"code": "264868006", "display": "No growth"},
}

# Susceptibility test interpretations (SNOMED)
SUSCEPTIBILITY = {
    "susceptible": {"code": "131196009", "display": "Susceptible"},
    "resistant": {"code": "30714006", "display": "Resistant"},
    "intermediate": {"code": "11896004", "display": "Intermediate"},
}

# Antimicrobial agents for susceptibility testing (LOINC)
AST_DRUGS = {
    "oxacillin": {"code": "18964-1", "display": "Oxacillin [Susceptibility]"},
    "vancomycin": {"code": "19000-9", "display": "Vancomycin [Susceptibility]"},
    "meropenem": {"code": "18944-3", "display": "Meropenem [Susceptibility]"},
    "imipenem": {"code": "18932-8", "display": "Imipenem [Susceptibility]"},
    "ciprofloxacin": {"code": "18906-2", "display": "Ciprofloxacin [Susceptibility]"},
    "cefepime": {"code": "18879-1", "display": "Cefepime [Susceptibility]"},
    "amikacin": {"code": "18860-1", "display": "Amikacin [Susceptibility]"},
}

# HSLOC codes for locations
LOCATIONS = {
    "micu": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1027-2",
        "display": "Medical Critical Care"
    },
    "sicu": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1030-6",
        "display": "Surgical Critical Care"
    },
    "medical_ward": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1060-3",
        "display": "Medical Ward"
    },
    "ed": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1108-0",
        "display": "Emergency Department"
    },
}


# =============================================================================
# AU Option Test Case Functions
# =============================================================================

def create_au_basic_inpatient_iv():
    """
    Test Case AU-1: Basic Inpatient IV Antimicrobial

    Patient admitted with IV Meropenem over 2 days.
    Expected: 2 Meropenem antimicrobial days
    """
    gen = FHIRBundleGenerator("AU1_BasicInpatientIV")

    gen.add_patient(
        given_name="AUBasic",
        family_name="InpatientIV",
        birth_date="1965-03-15",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-05T08:00:00.000Z",
        end="2025-01-08T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Meropenem Day 1 (3 doses on Jan 5)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-05T10:00:00.000Z",
        effective_end="2025-01-05T10:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["meropenem"]["code"],
            "display": ANTIMICROBIALS["meropenem"]["display"]
        }
    )
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-05T18:00:00.000Z",
        effective_end="2025-01-05T18:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["meropenem"]["code"],
            "display": ANTIMICROBIALS["meropenem"]["display"]
        }
    )

    # Meropenem Day 2 (1 dose on Jan 6)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-06T02:00:00.000Z",
        effective_end="2025-01-06T02:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["meropenem"]["code"],
            "display": ANTIMICROBIALS["meropenem"]["display"]
        }
    )

    return gen


def create_au_multiple_antimicrobials():
    """
    Test Case AU-2: Multiple Antimicrobials Same Day

    Patient receives Vancomycin and Meropenem on same days.
    Expected: 2 Vancomycin days + 2 Meropenem days = 4 total
    """
    gen = FHIRBundleGenerator("AU2_MultipleAntimicrobials")

    gen.add_patient(
        given_name="AUMultiple",
        family_name="Antimicrobials",
        birth_date="1972-07-20",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-10T06:00:00.000Z",
        end="2025-01-13T14:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Day 1: Vancomycin + Meropenem
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-10T08:00:00.000Z",
        effective_end="2025-01-10T09:00:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["vancomycin"]["code"],
            "display": ANTIMICROBIALS["vancomycin"]["display"]
        }
    )
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-10T09:00:00.000Z",
        effective_end="2025-01-10T09:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["meropenem"]["code"],
            "display": ANTIMICROBIALS["meropenem"]["display"]
        }
    )

    # Day 2: Vancomycin + Meropenem
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-11T08:00:00.000Z",
        effective_end="2025-01-11T09:00:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["vancomycin"]["code"],
            "display": ANTIMICROBIALS["vancomycin"]["display"]
        }
    )
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-11T09:00:00.000Z",
        effective_end="2025-01-11T09:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["meropenem"]["code"],
            "display": ANTIMICROBIALS["meropenem"]["display"]
        }
    )

    return gen


def create_au_patient_transfer():
    """
    Test Case AU-3: Patient Transfer Between Locations

    Patient transfers from ICU to ward, receives Ceftriaxone in both on same day.
    Expected: 1 day to ICU, 1 day to Ward, 1 day to FacWideIN
    """
    gen = FHIRBundleGenerator("AU3_PatientTransfer")

    gen.add_patient(
        given_name="AUTransfer",
        family_name="BetweenUnits",
        birth_date="1958-11-08",
        gender="male"
    )

    loc_id_icu = gen.add_location(location_type=LOCATIONS["micu"])
    loc_id_ward = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-15T07:00:00.000Z",
        end="2025-01-18T10:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id_icu  # Initial location
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Ceftriaxone in ICU (morning of Jan 16)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-16T08:00:00.000Z",
        effective_end="2025-01-16T08:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["ceftriaxone"]["code"],
            "display": ANTIMICROBIALS["ceftriaxone"]["display"]
        }
    )

    # Ceftriaxone in Ward (evening of Jan 16 - after transfer)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-16T20:00:00.000Z",
        effective_end="2025-01-16T20:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["ceftriaxone"]["code"],
            "display": ANTIMICROBIALS["ceftriaxone"]["display"]
        }
    )

    return gen


def create_au_ed_oral():
    """
    Test Case AU-4: ED Encounter with Oral Antimicrobial

    ED visit with oral Ciprofloxacin.
    Expected: 1 ED encounter, 1 Ciprofloxacin digestive day
    """
    gen = FHIRBundleGenerator("AU4_EDOralAntimicrobial")

    gen.add_patient(
        given_name="AUED",
        family_name="OralAntibiotic",
        birth_date="1985-04-22",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["ed"])

    enc_id = gen.add_encounter(
        start="2025-01-08T14:00:00.000Z",
        end="2025-01-08T18:00:00.000Z",
        status="finished",
        class_code="EMER",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "4525004",
            "display": "Emergency department patient visit"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-08T15:00:00.000Z",
        effective_end="2025-01-08T15:05:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["ciprofloxacin_oral"]["code"],
            "display": ANTIMICROBIALS["ciprofloxacin_oral"]["display"]
        }
    )

    return gen


def create_au_spanning_months():
    """
    Test Case AU-5: Multi-Day Stay Spanning Months

    Patient admitted Dec 30, discharged Jan 2. Pip-Tazo on Dec 31 and Jan 1.
    Expected: 1 day to December, 1 day to January
    """
    gen = FHIRBundleGenerator("AU5_SpanningMonths")

    gen.add_patient(
        given_name="AUSpanning",
        family_name="Months",
        birth_date="1970-09-30",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["sicu"])

    enc_id = gen.add_encounter(
        start="2024-12-30T10:00:00.000Z",
        end="2025-01-02T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2024-12-01", end="2025-12-31")

    # Pip-Tazo Dec 31
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2024-12-31T08:00:00.000Z",
        effective_end="2024-12-31T08:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["pip_tazo"]["code"],
            "display": ANTIMICROBIALS["pip_tazo"]["display"]
        }
    )

    # Pip-Tazo Jan 1
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-01T08:00:00.000Z",
        effective_end="2025-01-01T08:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["pip_tazo"]["code"],
            "display": ANTIMICROBIALS["pip_tazo"]["display"]
        }
    )

    return gen


def create_au_inhaled():
    """
    Test Case AU-6: Inhaled Antimicrobial

    Patient receives inhaled Tobramycin.
    Expected: 2 Tobramycin respiratory days
    """
    gen = FHIRBundleGenerator("AU6_InhaledAntimicrobial")

    gen.add_patient(
        given_name="AUInhaled",
        family_name="Tobramycin",
        birth_date="1945-02-14",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-20T09:00:00.000Z",
        end="2025-01-25T11:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Tobramycin Day 1
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-20T10:00:00.000Z",
        effective_end="2025-01-20T10:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["tobramycin_inh"]["code"],
            "display": ANTIMICROBIALS["tobramycin_inh"]["display"]
        }
    )

    # Tobramycin Day 2
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-21T10:00:00.000Z",
        effective_end="2025-01-21T10:30:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIMICROBIALS["tobramycin_inh"]["code"],
            "display": ANTIMICROBIALS["tobramycin_inh"]["display"]
        }
    )

    return gen


def create_au_no_antimicrobial():
    """
    Test Case AU-7: No Antimicrobial Administration

    Inpatient encounter without any antimicrobials.
    Expected: Contributes to denominator only
    """
    gen = FHIRBundleGenerator("AU7_NoAntimicrobial")

    gen.add_patient(
        given_name="AUNo",
        family_name="Antimicrobial",
        birth_date="1990-06-18",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    gen.add_encounter(
        start="2025-01-12T07:00:00.000Z",
        end="2025-01-14T16:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    return gen


# =============================================================================
# AR Option Test Case Functions
# =============================================================================

def create_ar_ho_mrsa():
    """
    Test Case AR-1: Hospital-Onset MRSA Bacteremia

    Blood culture positive for S. aureus on day 5, oxacillin resistant.
    Expected: HO event, MRSA phenotype positive
    """
    gen = FHIRBundleGenerator("AR1_HospitalOnsetMRSA")

    gen.add_patient(
        given_name="ARHO",
        family_name="MRSA",
        birth_date="1960-08-25",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-12T10:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood culture positive for S. aureus on Day 5
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-06T10:00:00.000Z"
    )

    # Oxacillin susceptibility - Resistant (MRSA)
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["oxacillin"]["code"],
            "display": AST_DRUGS["oxacillin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-06T12:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_co_ecoli_uti():
    """
    Test Case AR-2: Community-Onset E. coli UTI

    Urine culture positive for E. coli on day 2, ciprofloxacin susceptible.
    Expected: CO event, FQ-resistant negative
    """
    gen = FHIRBundleGenerator("AR2_CommunityOnsetEcoliUTI")

    gen.add_patient(
        given_name="ARCO",
        family_name="EcoliUTI",
        birth_date="1975-03-10",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-10T14:00:00.000Z",
        end="2025-01-14T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Urine culture positive for E. coli on Day 2
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": "630-4",
            "display": "Bacteria identified in Urine by Culture"
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": ORGANISMS["e_coli"]["code"],
            "display": ORGANISMS["e_coli"]["display"]
        },
        effective_datetime="2025-01-11T09:00:00.000Z"
    )

    # Ciprofloxacin susceptibility - Susceptible
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["ciprofloxacin"]["code"],
            "display": AST_DRUGS["ciprofloxacin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["susceptible"]["code"],
            "display": SUSCEPTIBILITY["susceptible"]["display"]
        },
        effective_datetime="2025-01-11T12:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_cre_klebsiella():
    """
    Test Case AR-3: Carbapenem-Resistant Klebsiella (CRE)

    Blood culture positive for K. pneumoniae on day 6, carbapenem resistant.
    Expected: HO event, CRE phenotype positive
    """
    gen = FHIRBundleGenerator("AR3_CREKlebsiella")

    gen.add_patient(
        given_name="ARCRE",
        family_name="Klebsiella",
        birth_date="1955-12-01",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-05T06:00:00.000Z",
        end="2025-01-15T14:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood culture positive for K. pneumoniae on Day 6
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["k_pneumoniae"]["code"],
        organism_display=ORGANISMS["k_pneumoniae"]["display"],
        collected_datetime="2025-01-10T08:00:00.000Z"
    )

    # Meropenem - Resistant
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["meropenem"]["code"],
            "display": AST_DRUGS["meropenem"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-10T14:00:00.000Z",
        include_specimen=False
    )

    # Imipenem - Resistant
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["imipenem"]["code"],
            "display": AST_DRUGS["imipenem"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-10T14:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_vre():
    """
    Test Case AR-4: Vancomycin-Resistant Enterococcus (VRE)

    Blood culture positive for E. faecium on day 4, vancomycin resistant.
    Expected: HO event, VRE phenotype positive
    """
    gen = FHIRBundleGenerator("AR4_VREFaecium")

    gen.add_patient(
        given_name="ARVRE",
        family_name="Faecium",
        birth_date="1968-05-22",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["sicu"])

    enc_id = gen.add_encounter(
        start="2025-01-08T10:00:00.000Z",
        end="2025-01-18T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood culture positive for E. faecium on Day 4
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_faecium"]["code"],
        organism_display=ORGANISMS["e_faecium"]["display"],
        collected_datetime="2025-01-11T14:00:00.000Z"
    )

    # Vancomycin - Resistant
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["vancomycin"]["code"],
            "display": AST_DRUGS["vancomycin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-11T18:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_same_day_duplicates():
    """
    Test Case AR-5: Same-Day Duplicate Cultures

    Blood and urine cultures with same organism on same day.
    Expected: 2 events (different source types)
    """
    gen = FHIRBundleGenerator("AR5_SameDayDuplicates")

    gen.add_patient(
        given_name="ARSameDay",
        family_name="Duplicates",
        birth_date="1962-09-15",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-12T08:00:00.000Z",
        end="2025-01-20T10:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood culture E. coli on Day 4
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-15T10:00:00.000Z"
    )

    # Urine culture E. coli same day
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": "630-4",
            "display": "Bacteria identified in Urine by Culture"
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": ORGANISMS["e_coli"]["code"],
            "display": ORGANISMS["e_coli"]["display"]
        },
        effective_datetime="2025-01-15T10:30:00.000Z"
    )

    return gen


def create_ar_14day_window():
    """
    Test Case AR-6: 14-Day Window Deduplication

    Two blood cultures with same organism 10 days apart.
    Expected: First event counted, second excluded (within 14-day window)
    """
    gen = FHIRBundleGenerator("AR6_14DayWindow")

    gen.add_patient(
        given_name="AR14Day",
        family_name="Window",
        birth_date="1950-04-08",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-02T07:00:00.000Z",
        end="2025-01-25T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # First blood culture S. aureus on Day 5
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-06T09:00:00.000Z"
    )

    # Second blood culture S. aureus on Day 15 (10 days later, within 14-day window)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-16T09:00:00.000Z"
    )

    return gen


def create_ar_mdr_pseudomonas():
    """
    Test Case AR-7: MDR Pseudomonas aeruginosa

    P. aeruginosa resistant to drugs in 3+ categories.
    Expected: HO event, MDR phenotype positive
    """
    gen = FHIRBundleGenerator("AR7_MDRPseudomonas")

    gen.add_patient(
        given_name="ARMDR",
        family_name="Pseudomonas",
        birth_date="1948-11-30",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-10T08:00:00.000Z",
        end="2025-01-22T14:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Respiratory culture P. aeruginosa on Day 5
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": "6460-0",
            "display": "Bacteria identified in Sputum by Culture"
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": ORGANISMS["p_aeruginosa"]["code"],
            "display": ORGANISMS["p_aeruginosa"]["display"]
        },
        effective_datetime="2025-01-14T10:00:00.000Z"
    )

    # Cefepime - Resistant (Cephalosporin category)
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["cefepime"]["code"],
            "display": AST_DRUGS["cefepime"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-14T14:00:00.000Z",
        include_specimen=False
    )

    # Ciprofloxacin - Resistant (Fluoroquinolone category)
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["ciprofloxacin"]["code"],
            "display": AST_DRUGS["ciprofloxacin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-14T14:00:00.000Z",
        include_specimen=False
    )

    # Meropenem - Resistant (Carbapenem category)
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["meropenem"]["code"],
            "display": AST_DRUGS["meropenem"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-14T14:00:00.000Z",
        include_specimen=False
    )

    # Amikacin - Susceptible (Aminoglycoside category)
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["amikacin"]["code"],
            "display": AST_DRUGS["amikacin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["susceptible"]["code"],
            "display": SUSCEPTIBILITY["susceptible"]["display"]
        },
        effective_datetime="2025-01-14T14:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_negative_culture():
    """
    Test Case AR-8: Negative Culture

    Blood culture with no growth.
    Expected: No AR event
    """
    gen = FHIRBundleGenerator("AR8_NegativeCulture")

    gen.add_patient(
        given_name="ARNegative",
        family_name="Culture",
        birth_date="1980-02-28",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-18T10:00:00.000Z",
        end="2025-01-22T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Negative blood culture on Day 4
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["no_growth"]["code"],
        organism_display=ORGANISMS["no_growth"]["display"],
        collected_datetime="2025-01-21T08:00:00.000Z"
    )

    return gen


def create_ar_cr_acinetobacter():
    """
    Test Case AR-9: Carbapenem-Resistant Acinetobacter

    A. baumannii I/R to carbapenems from respiratory specimen.
    Expected: HO event, carbapenem-NS Acinetobacter positive
    """
    gen = FHIRBundleGenerator("AR9_CRAcinetobacter")

    gen.add_patient(
        given_name="ARCR",
        family_name="Acinetobacter",
        birth_date="1942-07-14",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["micu"])

    enc_id = gen.add_encounter(
        start="2025-01-05T06:00:00.000Z",
        end="2025-01-20T10:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Respiratory culture A. baumannii on Day 6
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": "6460-0",
            "display": "Bacteria identified in Sputum by Culture"
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": ORGANISMS["a_baumannii"]["code"],
            "display": ORGANISMS["a_baumannii"]["display"]
        },
        effective_datetime="2025-01-10T14:00:00.000Z"
    )

    # Imipenem - Intermediate
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["imipenem"]["code"],
            "display": AST_DRUGS["imipenem"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["intermediate"]["code"],
            "display": SUSCEPTIBILITY["intermediate"]["display"]
        },
        effective_datetime="2025-01-10T18:00:00.000Z",
        include_specimen=False
    )

    # Meropenem - Resistant
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["meropenem"]["code"],
            "display": AST_DRUGS["meropenem"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-10T18:00:00.000Z",
        include_specimen=False
    )

    return gen


def create_ar_ed_positive():
    """
    Test Case AR-10: ED Encounter with Positive Culture

    ED visit with positive urine culture, fluoroquinolone resistant.
    Expected: CO event, FQ-resistant E. coli positive
    """
    gen = FHIRBundleGenerator("AR10_EDPositiveCulture")

    gen.add_patient(
        given_name="ARED",
        family_name="PositiveCulture",
        birth_date="1988-10-05",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["ed"])

    enc_id = gen.add_encounter(
        start="2025-01-15T09:00:00.000Z",
        end="2025-01-15T14:00:00.000Z",
        status="finished",
        class_code="EMER",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "4525004",
            "display": "Emergency department patient visit"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Urine culture E. coli
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": "630-4",
            "display": "Bacteria identified in Urine by Culture"
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": ORGANISMS["e_coli"]["code"],
            "display": ORGANISMS["e_coli"]["display"]
        },
        effective_datetime="2025-01-15T10:00:00.000Z"
    )

    # Ciprofloxacin - Resistant
    gen.add_simple_observation(
        encounter_id=enc_id,
        category="laboratory",
        code={
            "system": CODE_SYSTEMS["LOINC"],
            "code": AST_DRUGS["ciprofloxacin"]["code"],
            "display": AST_DRUGS["ciprofloxacin"]["display"]
        },
        value_codeable_concept={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": SUSCEPTIBILITY["resistant"]["code"],
            "display": SUSCEPTIBILITY["resistant"]["display"]
        },
        effective_datetime="2025-01-15T14:00:00.000Z",
        include_specimen=False
    )

    return gen


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Generate all AUR test cases and export to MADiE format."""

    print("=" * 70)
    print("AUR (Antimicrobial Use and Resistance) Test Case Generator")
    print("=" * 70)

    # Create exporter
    exporter = MADiEExporter(
        measure_name="NHSNACHMonthly1",
        version="0.0.000",
        measure_url="https://madie.cms.gov/Measure/NHSNACHMonthly1",
        measurement_period_start=MEASUREMENT_PERIOD_START,
        measurement_period_end=MEASUREMENT_PERIOD_END
    )

    # AU Option Test Cases
    print("\nAdding AU Option test cases...")

    exporter.add_test_case(
        generator_func=create_au_basic_inpatient_iv,
        series="AUOption",
        title="AU1_BasicInpatientIV",
        description="Basic inpatient with IV antimicrobial administration",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_multiple_antimicrobials,
        series="AUOption",
        title="AU2_MultipleAntimicrobials",
        description="Multiple antimicrobials administered on same day",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_patient_transfer,
        series="AUOption",
        title="AU3_PatientTransfer",
        description="Patient transfer between locations with antimicrobial",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_ed_oral,
        series="AUOption",
        title="AU4_EDOralAntimicrobial",
        description="ED encounter with oral antimicrobial",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_spanning_months,
        series="AUOption",
        title="AU5_SpanningMonths",
        description="Multi-day stay spanning December and January",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_inhaled,
        series="AUOption",
        title="AU6_InhaledAntimicrobial",
        description="Inhaled antimicrobial (respiratory route)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_au_no_antimicrobial,
        series="AUOption",
        title="AU7_NoAntimicrobial",
        description="Inpatient without antimicrobial administration",
        expected_populations={"initialPopulation": 1}
    )

    # AR Option Test Cases
    print("Adding AR Option test cases...")

    exporter.add_test_case(
        generator_func=create_ar_ho_mrsa,
        series="AROption",
        title="AR1_HospitalOnsetMRSA",
        description="Hospital-onset MRSA bacteremia (day 5)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_co_ecoli_uti,
        series="AROption",
        title="AR2_CommunityOnsetEcoliUTI",
        description="Community-onset E. coli UTI (day 2)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_cre_klebsiella,
        series="AROption",
        title="AR3_CREKlebsiella",
        description="Carbapenem-resistant Klebsiella pneumoniae",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_vre,
        series="AROption",
        title="AR4_VREFaecium",
        description="Vancomycin-resistant Enterococcus faecium",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_same_day_duplicates,
        series="AROption",
        title="AR5_SameDayDuplicates",
        description="Same-day blood and urine cultures (both counted)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_14day_window,
        series="AROption",
        title="AR6_14DayWindow",
        description="14-day window deduplication test",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_mdr_pseudomonas,
        series="AROption",
        title="AR7_MDRPseudomonas",
        description="MDR Pseudomonas aeruginosa (3+ categories)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_negative_culture,
        series="AROption",
        title="AR8_NegativeCulture",
        description="Negative blood culture (no AR event)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_cr_acinetobacter,
        series="AROption",
        title="AR9_CRAcinetobacter",
        description="Carbapenem-resistant Acinetobacter baumannii",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ar_ed_positive,
        series="AROption",
        title="AR10_EDPositiveCulture",
        description="ED encounter with FQ-resistant E. coli",
        expected_populations={"initialPopulation": 1}
    )

    # Export
    print("\nExporting to MADiE format...")
    output_path = exporter.export(create_zip=True)

    print(f"\n{'='*70}")
    print(f"Output: {output_path}")
    print(f"Total test cases: 17 (7 AU + 10 AR)")
    print(f"{'='*70}")
    print("\nNext steps:")
    print("1. Import ZIP into MADiE")
    print("2. Run measure execution")
    print("3. Verify results match expected outcomes")


if __name__ == "__main__":
    main()
