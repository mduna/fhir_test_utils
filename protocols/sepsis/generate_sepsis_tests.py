#!/usr/bin/env python3
"""
Adult Sepsis Event (ASE) Test Case Generator

Protocol: NHSN Adult Sepsis Event Surveillance
Measurement Period: 2025-01-01 to 2025-01-31

This script generates FHIR test cases for ASE protocol testing in MADiE.
"""

import sys
import os

# Add parent of fhir_test_utils to path for package imports
# This allows importing fhir_test_utils as a package
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, root_dir)

from fhir_test_utils import FHIRBundleGenerator, MADiEExporter
from fhir_test_utils.code_systems import CODE_SYSTEMS


# =============================================================================
# Protocol Constants
# =============================================================================

MEASUREMENT_PERIOD_START = "2025-01-01"
MEASUREMENT_PERIOD_END = "2025-01-31"

# Location Types
INPATIENT_LOCATIONS = {
    "trauma_critical_care": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1025-6",
        "display": "Trauma Critical Care"
    },
    "med_surg_critical_care": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1027-2",
        "display": "Medical Critical Care"
    },
    "med_cardiac_critical_care": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1028-0",
        "display": "Medical Cardiac Critical Care"
    },
    "medical_ward": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1060-3",
        "display": "Medical Ward"
    }
}

# Laboratory Codes (LOINC)
LAB_CODES = {
    "blood_culture": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "600-7",
        "display": "Bacteria identified in Blood by Culture"
    },
    "creatinine": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "2160-0",
        "display": "Creatinine [Mass/volume] in Serum or Plasma"
    },
    "bilirubin": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "1975-2",
        "display": "Bilirubin.total [Mass/volume] in Serum or Plasma"
    },
    "platelets": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "777-3",
        "display": "Platelets [#/volume] in Blood by Automated count"
    },
    "lactate": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "2524-7",
        "display": "Lactate [Moles/volume] in Serum or Plasma"
    }
}

# Vital Signs Codes (LOINC)
VITAL_CODES = {
    "sbp": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "8480-6",
        "display": "Systolic blood pressure"
    },
    "map": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "8478-0",
        "display": "Mean blood pressure"
    }
}

# Antimicrobial Medications (RxNorm)
ANTIBIOTICS = {
    "piperacillin_tazobactam": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1659149",
        "display": "Piperacillin 4000 MG / tazobactam 500 MG Injection"
    },
    "vancomycin": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1664986",
        "display": "Vancomycin 1000 MG Injection"
    },
    "ceftriaxone": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "309090",
        "display": "Ceftriaxone 1000 MG Injection"
    },
    "meropenem": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1722939",
        "display": "Meropenem 1000 MG Injection"
    },
    "levofloxacin_iv": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "311365",
        "display": "Levofloxacin 500 MG/100 ML Injectable Solution"
    }
}

# Vasopressor Medications (RxNorm)
VASOPRESSORS = {
    "norepinephrine": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1659027",
        "display": "Norepinephrine Bitartrate 4 MG/4 ML Injectable Solution"
    },
    "epinephrine": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1991339",
        "display": "Epinephrine 1 MG/ML Injectable Solution"
    },
    "vasopressin": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "1596994",
        "display": "Vasopressin 20 UNT/ML Injectable Solution"
    }
}

# Ventilation Procedures (SNOMED)
PROCEDURES = {
    "invasive_vent": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "40617009",
        "display": "Artificial respiration"
    },
    "niv": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "428311008",
        "display": "Non-invasive ventilation"
    },
    "hfnc": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "371907003",
        "display": "Oxygen administration by nasal cannula"
    }
}

# Exclusion Conditions (ICD-10)
CONDITIONS = {
    "esrd": {
        "system": CODE_SYSTEMS["ICD10CM"],
        "code": "N18.6",
        "display": "End stage renal disease"
    },
    "cirrhosis": {
        "system": CODE_SYSTEMS["ICD10CM"],
        "code": "K74.60",
        "display": "Unspecified cirrhosis of liver"
    },
    "all": {
        "system": CODE_SYSTEMS["ICD10CM"],
        "code": "C91.00",
        "display": "Acute lymphoblastic leukemia not having achieved remission"
    },
    "sepsis": {
        "system": CODE_SYSTEMS["ICD10CM"],
        "code": "A41.9",
        "display": "Sepsis, unspecified organism"
    }
}

# Organisms (SNOMED)
ORGANISMS = {
    "e_coli": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "112283007",
        "display": "Escherichia coli"
    },
    "s_aureus": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "3092008",
        "display": "Staphylococcus aureus"
    }
}


# =============================================================================
# Test Case Generator Functions
# =============================================================================

def create_sco_positive_basic_lactate():
    """
    Test Case 1: SCO Positive - Basic Metabolic Dysfunction (Lactate)

    Community-onset sepsis with blood culture on day 2, 4 QADs, and elevated lactate.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (onset day 2)
    """
    gen = FHIRBundleGenerator("SCOPositiveBasicLactate")

    # Patient
    gen.add_patient(
        given_name="SCO",
        family_name="BasicLactate",
        birth_date="1965-03-15",
        gender="male"
    )

    # Location
    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    # Encounter - Admit Day 1
    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-10T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    # Coverage
    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Lactate - Day 2 (elevated >2.0)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=3.5,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Antibiotic - 4 QADs starting Day 2
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["piperacillin_tazobactam"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_sco_positive_multiple_organ_dysfunction():
    """
    Test Case 2: SCO Positive - Multiple Organ Dysfunction

    Community-onset sepsis with cardiovascular (hypotension) AND renal dysfunction.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (onset day 2)
    """
    gen = FHIRBundleGenerator("SCOPositiveMultipleOrgan")

    gen.add_patient(
        given_name="SCO",
        family_name="MultipleOrgan",
        birth_date="1970-08-22",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-03T10:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-04T08:00:00.000Z"
    )

    # Hypotension - 2 BP readings with SBP <90 within 3h
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=85,
        diastolic=55,
        effective_datetime="2025-01-04T08:30:00.000Z"
    )
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=82,
        diastolic=52,
        effective_datetime="2025-01-04T10:00:00.000Z"
    )

    # Creatinine - baseline and elevated (2x increase)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=0.9,
        unit="mg/dL",
        effective_datetime="2025-01-03T12:00:00.000Z"
    )
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=2.2,
        unit="mg/dL",
        effective_datetime="2025-01-04T10:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{4+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{4+day}T09:00:00.000Z"
        )

    return gen


def create_sco_positive_day3_boundary():
    """
    Test Case 3: SCO Positive - Day 3 Onset (Boundary)

    Sepsis with onset exactly on day 3 (last day for SCO).

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (onset day 3 - boundary)
    """
    gen = FHIRBundleGenerator("SCOPositiveDay3Boundary")

    gen.add_patient(
        given_name="SCO",
        family_name="Day3Boundary",
        birth_date="1958-11-30",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_cardiac_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T06:00:00.000Z",
        end="2025-01-11T12:00:00.000Z",
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

    # Blood Culture - Day 3 (boundary)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-04T14:00:00.000Z"
    )

    # Lactate - Day 3
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=2.8,
        unit="mmol/L",
        effective_datetime="2025-01-04T13:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["ceftriaxone"],
            effective_start=f"2025-01-0{4+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{4+day}T09:00:00.000Z"
        )

    return gen


def create_sco_positive_principal_dx_infection():
    """
    Test Case 4: SCO Positive - Principal Diagnosis Infection (No Blood Culture)

    Community-onset sepsis meeting criteria via principal diagnosis (infection)
    instead of blood culture.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (principal dx infection + 4 QAD + organ dysfunction)
    """
    gen = FHIRBundleGenerator("SCOPositivePrincipalDxInfection")

    gen.add_patient(
        given_name="SCO",
        family_name="PrincipalDxInfection",
        birth_date="1975-04-18",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-03T14:00:00.000Z",
        end="2025-01-09T12:00:00.000Z",
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

    # Principal Diagnosis - Sepsis (Present on Admission)
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["sepsis"],
        clinical_status="active",
        verification_status="confirmed",
        onset_datetime="2025-01-03T14:00:00.000Z"
    )

    # Lactate - Day 1 (elevated >2.0)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=4.2,
        unit="mmol/L",
        effective_datetime="2025-01-03T16:00:00.000Z"
    )

    # Antibiotic - 4 QADs starting Day 1
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["levofloxacin_iv"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_sho_positive_day5_onset():
    """
    Test Case 5: SHO Positive - Day 5 Onset

    Hospital-onset sepsis with blood culture and organ dysfunction on day 5.

    Expected:
    - Initial Population: 1
    - SHO Event: Positive (onset day 5)
    """
    gen = FHIRBundleGenerator("SHOPositiveDay5Onset")

    gen.add_patient(
        given_name="SHO",
        family_name="Day5Onset",
        birth_date="1962-07-25",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
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

    # Blood Culture - Day 5
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-06T10:00:00.000Z"
    )

    # Lactate - Day 5
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=3.1,
        unit="mmol/L",
        effective_datetime="2025-01-06T09:30:00.000Z"
    )

    # Antibiotic - 4 QADs starting Day 5
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["meropenem"],
            effective_start=f"2025-01-0{6+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{6+day}T09:00:00.000Z"
        )

    return gen


def create_sho_positive_escalating_cardiovascular():
    """
    Test Case 6: SHO Positive - Escalating Cardiovascular Dysfunction

    Hospital-onset sepsis with escalating cardiovascular dysfunction
    (hypotension progressing to vasopressor).

    Expected:
    - Initial Population: 1
    - SHO Event: Positive (onset day 4, escalation day 5)
    - Cardiovascular Dysfunction: Yes (hypotension -> vasopressor escalation)
    """
    gen = FHIRBundleGenerator("SHOPositiveEscalatingCardiovascular")

    gen.add_patient(
        given_name="SHO",
        family_name="EscalatingCardio",
        birth_date="1968-02-14",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T10:00:00.000Z",
        end="2025-01-15T12:00:00.000Z",
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

    # Blood Culture - Day 5
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-06T08:00:00.000Z"
    )

    # Hypotension - Day 4 (2 BP readings with SBP <90 within 3h)
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=88,
        diastolic=58,
        effective_datetime="2025-01-05T20:00:00.000Z"
    )
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=84,
        diastolic=54,
        effective_datetime="2025-01-05T22:00:00.000Z"
    )

    # Vasopressor escalation - Day 5
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=VASOPRESSORS["norepinephrine"],
        effective_start="2025-01-06T00:00:00.000Z",
        effective_end="2025-01-06T23:59:00.000Z"
    )

    # Antibiotic - 4 QADs starting Day 4
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{5+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{5+day}T09:00:00.000Z"
        )

    return gen


def create_cardiovascular_hypotension():
    """
    Test Case 7: Cardiovascular Dysfunction - Hypotension Only

    Sepsis with hypotension meeting cardiovascular criteria
    (>=2 readings SBP<90 within 3h).

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Cardiovascular Dysfunction: Yes (3 SBP readings <90 within 3h)
    """
    gen = FHIRBundleGenerator("CardiovascularHypotension")

    gen.add_patient(
        given_name="Cardio",
        family_name="Hypotension",
        birth_date="1972-09-08",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-03T08:00:00.000Z",
        end="2025-01-11T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-04T10:00:00.000Z"
    )

    # Hypotension - 3 BP readings with SBP <90 within 3h
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=78,
        diastolic=48,
        effective_datetime="2025-01-04T10:30:00.000Z"
    )
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=82,
        diastolic=52,
        effective_datetime="2025-01-04T12:00:00.000Z"
    )
    gen.add_blood_pressure(
        encounter_id=enc_id,
        systolic=85,
        diastolic=55,
        effective_datetime="2025-01-04T13:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["piperacillin_tazobactam"],
            effective_start=f"2025-01-0{4+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{4+day}T09:00:00.000Z"
        )

    return gen


def create_cardiovascular_vasopressor():
    """
    Test Case 8: Cardiovascular Dysfunction - Vasopressor Initiation

    Sepsis with new vasopressor initiation meeting cardiovascular criteria.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Cardiovascular Dysfunction: Yes (new vasopressor)
    """
    gen = FHIRBundleGenerator("CardiovascularVasopressor")

    gen.add_patient(
        given_name="Cardio",
        family_name="Vasopressor",
        birth_date="1960-12-03",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T14:00:00.000Z",
        end="2025-01-13T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Vasopressor - new initiation on Day 2
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=VASOPRESSORS["norepinephrine"],
        effective_start="2025-01-03T11:00:00.000Z",
        effective_end="2025-01-03T23:59:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["ceftriaxone"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_respiratory_invasive_vent():
    """
    Test Case 9: Respiratory Dysfunction - Invasive Ventilation

    Sepsis with invasive mechanical ventilation.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Respiratory Dysfunction: Yes (invasive vent - any duration)
    """
    gen = FHIRBundleGenerator("RespiratoryInvasiveVent")

    gen.add_patient(
        given_name="Resp",
        family_name="InvasiveVent",
        birth_date="1955-05-20",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T08:00:00.000Z"
    )

    # Invasive Ventilation - Day 2
    gen.add_procedure(
        encounter_id=enc_id,
        performed_start="2025-01-03T06:00:00.000Z",
        performed_end="2025-01-07T12:00:00.000Z",
        procedure_code=PROCEDURES["invasive_vent"]
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["meropenem"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_respiratory_niv_hfnc():
    """
    Test Case 10: Respiratory Dysfunction - NIV/HFNC 2+ Days

    Sepsis with non-invasive ventilation for 2+ calendar days.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Respiratory Dysfunction: Yes (NIV for 2+ calendar days)
    """
    gen = FHIRBundleGenerator("RespiratoryNIVHFNC")

    gen.add_patient(
        given_name="Resp",
        family_name="NIVHFNC",
        birth_date="1978-01-15",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_cardiac_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-03T10:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-04T08:00:00.000Z"
    )

    # NIV - 2 calendar days (Day 2-3)
    gen.add_procedure(
        encounter_id=enc_id,
        performed_start="2025-01-04T10:00:00.000Z",
        performed_end="2025-01-06T10:00:00.000Z",
        procedure_code=PROCEDURES["niv"]
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{4+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{4+day}T09:00:00.000Z"
        )

    return gen


def create_metabolic_lactate_elevated():
    """
    Test Case 11: Metabolic Dysfunction - Lactate Elevated

    Sepsis with lactate >2.0 mmol/L.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Metabolic Dysfunction: Yes (lactate 2.5 > 2.0 threshold)
    """
    gen = FHIRBundleGenerator("MetabolicLactateElevated")

    gen.add_patient(
        given_name="Metabolic",
        family_name="LactateElevated",
        birth_date="1966-08-12",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-02T12:00:00.000Z",
        end="2025-01-10T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-03T14:00:00.000Z"
    )

    # Lactate - elevated >2.0
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=2.5,
        unit="mmol/L",
        effective_datetime="2025-01-03T13:30:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["levofloxacin_iv"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_renal_creatinine_increase():
    """
    Test Case 12: Renal Dysfunction - Creatinine 2x Increase

    Sepsis with creatinine doubling from baseline.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Renal Dysfunction: Yes (2x increase)
    """
    gen = FHIRBundleGenerator("RenalCreatinine2xIncrease")

    gen.add_patient(
        given_name="Renal",
        family_name="Creatinine2x",
        birth_date="1973-06-28",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-11T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Creatinine baseline - Day 1
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=0.8,
        unit="mg/dL",
        effective_datetime="2025-01-02T10:00:00.000Z"
    )

    # Creatinine elevated - Day 2 (2.25x increase)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=1.8,
        unit="mg/dL",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["ceftriaxone"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_renal_excluded_esrd():
    """
    Test Case 13: Renal Dysfunction Excluded - ESRD Diagnosis

    Patient with ESRD - renal dysfunction criteria should not apply.
    Qualifies via lactate instead.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (via lactate)
    - Renal Dysfunction: Excluded (ESRD)
    """
    gen = FHIRBundleGenerator("RenalExcludedESRD")

    gen.add_patient(
        given_name="Renal",
        family_name="ExcludedESRD",
        birth_date="1958-03-10",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-10T12:00:00.000Z",
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

    # ESRD Condition - Present on Admission
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["esrd"],
        clinical_status="active",
        verification_status="confirmed",
        onset_datetime="2024-01-01T00:00:00.000Z"
    )

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Creatinine - elevated but excluded due to ESRD
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=4.0,
        unit="mg/dL",
        effective_datetime="2025-01-02T10:00:00.000Z"
    )
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["creatinine"],
        value=8.5,
        unit="mg/dL",
        effective_datetime="2025-01-03T10:00:00.000Z"
    )

    # Lactate - qualifies instead
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=3.0,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_hepatic_bilirubin_increase():
    """
    Test Case 14: Hepatic Dysfunction - Bilirubin 2x Increase

    Sepsis with bilirubin doubling to >=2.0 mg/dL.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Hepatic Dysfunction: Yes (2x increase to >=2.0)
    """
    gen = FHIRBundleGenerator("HepaticBilirubin2xIncrease")

    gen.add_patient(
        given_name="Hepatic",
        family_name="Bilirubin2x",
        birth_date="1970-04-22",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T10:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T08:00:00.000Z"
    )

    # Bilirubin baseline - Day 1
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["bilirubin"],
        value=1.0,
        unit="mg/dL",
        effective_datetime="2025-01-02T12:00:00.000Z"
    )

    # Bilirubin elevated - Day 2 (2.5x increase to 2.5)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["bilirubin"],
        value=2.5,
        unit="mg/dL",
        effective_datetime="2025-01-03T07:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["piperacillin_tazobactam"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_hepatic_excluded_liver_disease():
    """
    Test Case 15: Hepatic Dysfunction Excluded - Liver Disease

    Patient with moderate/severe liver disease - hepatic criteria excluded.
    Qualifies via lactate instead.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (via lactate)
    - Hepatic Dysfunction: Excluded (liver disease diagnosis)
    """
    gen = FHIRBundleGenerator("HepaticExcludedLiverDisease")

    gen.add_patient(
        given_name="Hepatic",
        family_name="ExcludedLiver",
        birth_date="1965-09-14",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-11T12:00:00.000Z",
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

    # Cirrhosis Condition - Present on Admission
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["cirrhosis"],
        clinical_status="active",
        verification_status="confirmed",
        onset_datetime="2024-01-01T00:00:00.000Z"
    )

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Bilirubin - elevated but excluded due to liver disease
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["bilirubin"],
        value=2.0,
        unit="mg/dL",
        effective_datetime="2025-01-02T10:00:00.000Z"
    )
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["bilirubin"],
        value=5.0,
        unit="mg/dL",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Lactate - qualifies instead
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=2.8,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:30:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["ceftriaxone"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_coagulation_platelet_decrease():
    """
    Test Case 16: Coagulation Dysfunction - Platelets 50% Decrease

    Sepsis with platelets dropping 50% to <100.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive
    - Coagulation Dysfunction: Yes (50%+ decrease to <100)
    """
    gen = FHIRBundleGenerator("CoagulationPlatelet50Decrease")

    gen.add_patient(
        given_name="Coag",
        family_name="Platelet50Decrease",
        birth_date="1963-11-05",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Platelets baseline - Day 1
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["platelets"],
        value=180,
        unit="10*9/L",
        effective_datetime="2025-01-02T10:00:00.000Z"
    )

    # Platelets decreased - Day 2 (58% decrease to 75)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["platelets"],
        value=75,
        unit="10*9/L",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["meropenem"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_coagulation_excluded_malignancy():
    """
    Test Case 17: Coagulation Dysfunction Excluded - Malignancy

    Patient with hematologic malignancy - coagulation criteria excluded.
    Qualifies via lactate instead.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (via lactate)
    - Coagulation Dysfunction: Excluded (hematologic malignancy)
    """
    gen = FHIRBundleGenerator("CoagulationExcludedMalignancy")

    gen.add_patient(
        given_name="Coag",
        family_name="ExcludedMalignancy",
        birth_date="1960-02-28",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-11T12:00:00.000Z",
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

    # ALL Condition - Present on Admission
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["all"],
        clinical_status="active",
        verification_status="confirmed",
        onset_datetime="2024-06-01T00:00:00.000Z"
    )

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Platelets - decreased but excluded due to malignancy
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["platelets"],
        value=120,
        unit="10*9/L",
        effective_datetime="2025-01-02T10:00:00.000Z"
    )
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["platelets"],
        value=45,
        unit="10*9/L",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # Lactate - qualifies instead
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=3.2,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:30:00.000Z"
    )

    # Antibiotic - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    return gen


def create_qad_exception_death():
    """
    Test Case 18: QAD Exception - Death Before 4 QADs

    Patient dies after only 2 QADs - qualifies due to death exception.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (2 QADs sufficient - death exception)
    - Death: Yes
    """
    gen = FHIRBundleGenerator("QADExceptionDeathBefore4")

    gen.add_patient(
        given_name="QAD",
        family_name="DeathException",
        birth_date="1950-07-18",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["trauma_critical_care"])

    # Encounter ending in death
    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-04T23:59:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id,
        discharge_disposition={
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/discharge-disposition",
                "code": "exp",
                "display": "Expired"
            }]
        }
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T08:00:00.000Z"
    )

    # Lactate - severely elevated
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=6.5,
        unit="mmol/L",
        effective_datetime="2025-01-03T07:30:00.000Z"
    )

    # Antibiotic - only 2 QADs (death exception)
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=ANTIBIOTICS["piperacillin_tazobactam"],
        effective_start="2025-01-03T08:00:00.000Z",
        effective_end="2025-01-03T09:00:00.000Z"
    )
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=ANTIBIOTICS["piperacillin_tazobactam"],
        effective_start="2025-01-04T08:00:00.000Z",
        effective_end="2025-01-04T09:00:00.000Z"
    )

    return gen


def create_repeat_event_timeframe_excluded():
    """
    Test Case 19: Repeat Event Timeframe - Second Event Excluded

    Second potential ASE within 7-day RET of first event.

    Expected:
    - Initial Population: 1
    - SCO Event 1: Positive (onset day 2)
    - SCO Event 2: Excluded (within 7-day RET)
    """
    gen = FHIRBundleGenerator("RepeatEventTimeframeExcluded")

    gen.add_patient(
        given_name="Repeat",
        family_name="EventExcluded",
        birth_date="1968-05-10",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["med_surg_critical_care"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-16T12:00:00.000Z",
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

    # First Event - Blood Culture Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # First Event - Lactate
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=3.0,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:00:00.000Z"
    )

    # First Event - 4 QADs
    for day in range(4):
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["vancomycin"],
            effective_start=f"2025-01-0{3+day}T08:00:00.000Z",
            effective_end=f"2025-01-0{3+day}T09:00:00.000Z"
        )

    # Second Event (within RET) - Blood Culture Day 7
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-08T10:00:00.000Z"
    )

    # Second Event - Lactate
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=2.8,
        unit="mmol/L",
        effective_datetime="2025-01-08T09:00:00.000Z"
    )

    # Second Event - 4 QADs (Jan 8, 9, 10, 11)
    for day in range(4):
        day_num = 8 + day
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["ceftriaxone"],
            effective_start=f"2025-01-{day_num:02d}T08:00:00.000Z",
            effective_end=f"2025-01-{day_num:02d}T09:00:00.000Z"
        )

    return gen


def create_qad_with_1day_gap():
    """
    Test Case 20: QAD With 1-Day Gap - Qualifies

    Antibiotic administration with 1-day gap still counts as consecutive.

    Expected:
    - Initial Population: 1
    - SCO Event: Positive (1-day gaps tolerated - 4 QADs met)
    """
    gen = FHIRBundleGenerator("QADWith1DayGap")

    gen.add_patient(
        given_name="QAD",
        family_name="OneDayGap",
        birth_date="1975-10-22",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
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

    # Blood Culture - Day 2
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T10:00:00.000Z"
    )

    # Lactate
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=LAB_CODES["lactate"],
        value=2.3,
        unit="mmol/L",
        effective_datetime="2025-01-03T09:30:00.000Z"
    )

    # Antibiotic - 4 QADs with gaps (every other day)
    # Jan 3, Jan 5, Jan 7, Jan 9
    gap_days = [3, 5, 7, 9]
    for day in gap_days:
        gen.add_medication_administration(
            encounter_id=enc_id,
            medication_code=ANTIBIOTICS["levofloxacin_iv"],
            effective_start=f"2025-01-0{day}T08:00:00.000Z",
            effective_end=f"2025-01-0{day}T09:00:00.000Z"
        )

    return gen


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Generate all test cases and export to MADiE format."""

    print("=" * 70)
    print("Adult Sepsis Event (ASE) Test Case Generator")
    print("=" * 70)

    # Create exporter
    exporter = MADiEExporter(
        measure_name="NHSNACHMonthly1",
        version="0.0.000",
        measure_url="https://madie.cms.gov/Measure/NHSNACHMonthly1",
        measurement_period_start=MEASUREMENT_PERIOD_START,
        measurement_period_end=MEASUREMENT_PERIOD_END
    )

    # Add test cases
    test_cases = [
        # SCO Basic Cases (1-4)
        (create_sco_positive_basic_lactate, "SCO", "SCOPositiveBasicLactate",
         "Community-onset sepsis with blood culture, 4 QADs, and elevated lactate (day 2)",
         {"initialPopulation": 1}),

        (create_sco_positive_multiple_organ_dysfunction, "SCO", "SCOPositiveMultipleOrgan",
         "Community-onset sepsis with hypotension AND renal dysfunction",
         {"initialPopulation": 1}),

        (create_sco_positive_day3_boundary, "SCO", "SCOPositiveDay3Boundary",
         "Community-onset sepsis with onset on day 3 (boundary case)",
         {"initialPopulation": 1}),

        (create_sco_positive_principal_dx_infection, "SCO", "SCOPositivePrincipalDxInfection",
         "Community-onset sepsis via principal diagnosis infection (no blood culture)",
         {"initialPopulation": 1}),

        # SHO Cases (5-6)
        (create_sho_positive_day5_onset, "SHO", "SHOPositiveDay5Onset",
         "Hospital-onset sepsis with onset on day 5",
         {"initialPopulation": 1}),

        (create_sho_positive_escalating_cardiovascular, "SHO", "SHOPositiveEscalatingCardiovascular",
         "Hospital-onset sepsis with escalating cardiovascular dysfunction",
         {"initialPopulation": 1}),

        # Cardiovascular Dysfunction Cases (7-8)
        (create_cardiovascular_hypotension, "OrganDysfunction", "CardiovascularHypotension",
         "Sepsis with hypotension (>=2 SBP readings <90 within 3h)",
         {"initialPopulation": 1}),

        (create_cardiovascular_vasopressor, "OrganDysfunction", "CardiovascularVasopressor",
         "Sepsis with new vasopressor initiation (cardiovascular dysfunction)",
         {"initialPopulation": 1}),

        # Respiratory Dysfunction Cases (9-10)
        (create_respiratory_invasive_vent, "OrganDysfunction", "RespiratoryInvasiveVent",
         "Sepsis with invasive mechanical ventilation (respiratory dysfunction)",
         {"initialPopulation": 1}),

        (create_respiratory_niv_hfnc, "OrganDysfunction", "RespiratoryNIVHFNC",
         "Sepsis with NIV/HFNC for 2+ calendar days (respiratory dysfunction)",
         {"initialPopulation": 1}),

        # Metabolic Dysfunction Case (11)
        (create_metabolic_lactate_elevated, "OrganDysfunction", "MetabolicLactateElevated",
         "Sepsis with lactate >2.0 mmol/L (metabolic dysfunction)",
         {"initialPopulation": 1}),

        # Renal Dysfunction Cases (12-13)
        (create_renal_creatinine_increase, "OrganDysfunction", "RenalCreatinine2xIncrease",
         "Sepsis with creatinine 2x increase (renal dysfunction)",
         {"initialPopulation": 1}),

        (create_renal_excluded_esrd, "Exclusions", "RenalExcludedESRD",
         "ESRD patient - renal dysfunction excluded, qualifies via lactate",
         {"initialPopulation": 1}),

        # Hepatic Dysfunction Cases (14-15)
        (create_hepatic_bilirubin_increase, "OrganDysfunction", "HepaticBilirubin2xIncrease",
         "Sepsis with bilirubin 2x increase (hepatic dysfunction)",
         {"initialPopulation": 1}),

        (create_hepatic_excluded_liver_disease, "Exclusions", "HepaticExcludedLiverDisease",
         "Liver disease patient - hepatic dysfunction excluded, qualifies via lactate",
         {"initialPopulation": 1}),

        # Coagulation Dysfunction Cases (16-17)
        (create_coagulation_platelet_decrease, "OrganDysfunction", "CoagulationPlatelet50Decrease",
         "Sepsis with platelets 50% decrease (coagulation dysfunction)",
         {"initialPopulation": 1}),

        (create_coagulation_excluded_malignancy, "Exclusions", "CoagulationExcludedMalignancy",
         "Malignancy patient - coagulation dysfunction excluded, qualifies via lactate",
         {"initialPopulation": 1}),

        # QAD Exception Cases (18, 20)
        (create_qad_exception_death, "QADException", "QADExceptionDeathBefore4",
         "Patient death before 4 QADs - qualifies due to death exception",
         {"initialPopulation": 1}),

        # Repeat Event Timeframe Case (19)
        (create_repeat_event_timeframe_excluded, "RET", "RepeatEventTimeframeExcluded",
         "Second ASE within 7-day RET of first event - excluded",
         {"initialPopulation": 1}),

        # QAD Gap Case (20)
        (create_qad_with_1day_gap, "QADGap", "QADWith1DayGap",
         "Antibiotic with 1-day gaps still counts as consecutive QADs",
         {"initialPopulation": 1}),
    ]

    for func, series, title, desc, expected in test_cases:
        exporter.add_test_case(
            generator_func=func,
            series=series,
            title=title,
            description=desc,
            expected_populations=expected
        )
        print(f"  Added: {title}")

    # Export
    output_path = exporter.export(create_zip=True)

    print("\n" + "=" * 70)
    print(f"Generated {len(test_cases)} test cases")
    print(f"Output: {output_path}")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Import ZIP into MADiE")
    print("2. Run measure execution")
    print("3. Verify results match expected outcomes")


if __name__ == "__main__":
    main()
