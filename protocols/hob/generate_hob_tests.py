#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOB (Hospital-Onset Bacteremia & Fungemia) Test Case Generator

Protocol Definition:
- HOB Event: Blood culture positive for bacterial/fungal organism on hospital day 4+
- Hospital Day 1 = Admission date
- Measurement Period: 2025-01-01 to 2025-01-31

Test Cases Generated (11 total):
Primary HOB Cases:
1. HOB Positive - Day 4 S. aureus
2. HOB Positive - Day 5 Candida (fungemia)
3. HOB Excluded - Matching COB organism (E. coli on day 2 and day 5)
4. HOB Positive - Non-matching prior COB (E. coli day 2, S. aureus day 5)

Blood Culture Contamination Cases:
5. Contamination 1 of 2 - Only 1 paired set positive (S. epidermidis)
6. Contamination 2 of 2 - Both paired sets positive (NOT contamination)

Matching Commensal HOB Cases:
7. Matching Commensal Positive - S. epidermidis + 4 days antibiotics
8. Matching Commensal Excluded - S. epidermidis + <4 days antibiotics

Non-Measure HOB Cases:
9. Non-Measure High Risk - E. coli + AML + Neutropenia
10. Measurable No Risk - S. aureus + Diabetes/HTN (no non-preventability)

Species Code Matching Cases:
11. HOB Excluded - Same species with different SNOMED codes (P. aeruginosa vs CR P. aeruginosa)

Usage:
    cd protocols/hob
    python generate_hob_tests.py
    # Output: NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip
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
# HOB Protocol Constants
# =============================================================================

HOB_TIMING_THRESHOLD = 4  # Hospital day 4+ qualifies as HOB
MEASUREMENT_PERIOD_START = "2025-01-01"
MEASUREMENT_PERIOD_END = "2025-01-31"

# LOINC code for blood culture
BLOOD_CULTURE_LOINC = "600-7"
BLOOD_SPECIMEN_SNOMED = "119297000"

# Organism SNOMED codes for testing
ORGANISMS = {
    "s_aureus": {"code": "3092008", "display": "Staphylococcus aureus"},
    "e_coli": {"code": "112283007", "display": "Escherichia coli"},
    "candida": {"code": "53326005", "display": "Candida albicans"},
    "s_epidermidis": {"code": "60875001", "display": "Staphylococcus epidermidis"},  # Excluded skin commensal
    "no_growth": {"code": "264868006", "display": "No growth"},
    "p_aeruginosa": {"code": "52499004", "display": "Pseudomonas aeruginosa"},
    "p_aeruginosa_cr": {"code": "726492000", "display": "Carbapenem resistant Pseudomonas aeruginosa"},
}

# Antibiotic RxNorm codes
ANTIBIOTICS = {
    "vancomycin": {"code": "1664986", "display": "Vancomycin 1000 MG Injection"},
}

# Condition SNOMED codes for non-preventability
CONDITIONS = {
    "aml": {"code": "91861009", "display": "Acute myeloid leukemia"},
    "neutropenia": {"code": "165517008", "display": "Neutropenia"},
    "diabetes": {"code": "44054006", "display": "Diabetes mellitus type 2"},
    "hypertension": {"code": "38341003", "display": "Hypertensive disorder"},
}

# HSLOC codes for inpatient locations
INPATIENT_LOCATION = {
    "system": CODE_SYSTEMS["HSLOC"],
    "code": "1025-6",
    "display": "Trauma Critical Care"
}


# =============================================================================
# Test Case Generator Functions
# =============================================================================

def create_hob_positive_day4_saureus():
    """
    Test Case 1: HOB Positive - S. aureus on Day 4

    Patient admitted January 2, 2025 (Day 1)
    Blood culture collected January 5, 2025 (Day 4)
    Organism: Staphylococcus aureus

    Expected:
    - Initial Population: 1 (qualifying inpatient encounter)
    - HOB Evaluation (downstream): Qualifies as HOB event
    """
    gen = FHIRBundleGenerator("HOBPositive_Day4SAureus")

    # Add patient (adult)
    gen.add_patient(
        given_name="HOBPositive",
        family_name="Day4SAureus",
        birth_date="1970-01-15",
        gender="male"
    )

    # Add inpatient location
    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    # Add inpatient encounter - Day 1 = January 2, 2025
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

    # Add coverage
    gen.add_coverage(
        start="2025-01-01",
        end="2025-12-31"
    )

    # Add blood culture on Day 4 (January 5, 2025)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-05T10:00:00.000Z"
    )

    return gen


def create_hob_positive_day5_candida():
    """
    Test Case 2: HOB Positive - Candida on Day 5 (Fungemia)

    Patient admitted January 3, 2025 (Day 1)
    Blood culture collected January 7, 2025 (Day 5)
    Organism: Candida albicans (fungemia)

    Expected:
    - Initial Population: 1 (qualifying inpatient encounter)
    - HOB Evaluation (downstream): Qualifies as HOB event (fungemia)
    """
    gen = FHIRBundleGenerator("HOBPositive_Day5Candida")

    # Add patient (adult)
    gen.add_patient(
        given_name="HOBPositive",
        family_name="Day5Candida",
        birth_date="1965-06-20",
        gender="female"
    )

    # Add inpatient location
    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    # Add inpatient encounter - Day 1 = January 3, 2025
    enc_id = gen.add_encounter(
        start="2025-01-03T14:00:00.000Z",
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

    # Add coverage
    gen.add_coverage(
        start="2025-01-01",
        end="2025-12-31"
    )

    # Add blood culture on Day 5 (January 7, 2025) - Fungemia
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["candida"]["code"],
        organism_display=ORGANISMS["candida"]["display"],
        collected_datetime="2025-01-07T09:00:00.000Z"
    )

    return gen


def create_hob_excluded_matching_cob():
    """
    Test Case 3: HOB Excluded - Matching COB Organism

    Patient admitted January 2, 2025 (Day 1)
    Blood culture on Day 2 (January 3): E. coli (COB event)
    Blood culture on Day 5 (January 6): E. coli (same organism)

    Expected:
    - Initial Population: 1 (qualifying inpatient encounter)
    - HOB Evaluation (downstream): Day 5 culture EXCLUDED from HOB
      (same organism as prior COB event)
    """
    gen = FHIRBundleGenerator("HOBExcluded_MatchingCOB")

    # Add patient (adult)
    gen.add_patient(
        given_name="HOBExcluded",
        family_name="MatchingCOB",
        birth_date="1980-03-10",
        gender="male"
    )

    # Add inpatient location
    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    # Add inpatient encounter - Day 1 = January 2, 2025
    enc_id = gen.add_encounter(
        start="2025-01-02T10:00:00.000Z",
        end="2025-01-11T14:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    # Add coverage
    gen.add_coverage(
        start="2025-01-01",
        end="2025-12-31"
    )

    # Blood culture on Day 2 (January 3, 2025) - COB event
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T08:00:00.000Z"
    )

    # Blood culture on Day 5 (January 6, 2025) - Same organism (excluded from HOB)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-06T09:00:00.000Z"
    )

    return gen


def create_hob_positive_nonmatching_cob():
    """
    Test Case 4: HOB Positive - Non-matching Prior COB

    Patient admitted January 2, 2025 (Day 1)
    Blood culture on Day 2 (January 3): E. coli (COB event)
    Blood culture on Day 5 (January 6): S. aureus (different organism)

    Expected:
    - Initial Population: 1 (qualifying inpatient encounter)
    - HOB Evaluation (downstream): Day 5 qualifies as HOB
      (different organism from prior COB event)
    """
    gen = FHIRBundleGenerator("HOBPositive_NonMatchingCOB")

    # Add patient (adult)
    gen.add_patient(
        given_name="HOBPositive",
        family_name="NonMatchingCOB",
        birth_date="1975-09-25",
        gender="female"
    )

    # Add inpatient location
    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    # Add inpatient encounter - Day 1 = January 2, 2025
    enc_id = gen.add_encounter(
        start="2025-01-02T06:00:00.000Z",
        end="2025-01-12T16:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "183452005",
            "display": "Emergency hospital admission"
        }],
        location_id=loc_id
    )

    # Add coverage
    gen.add_coverage(
        start="2025-01-01",
        end="2025-12-31"
    )

    # Blood culture on Day 2 (January 3, 2025) - COB event with E. coli
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-03T07:00:00.000Z"
    )

    # Blood culture on Day 5 (January 6, 2025) - Different organism (S. aureus)
    # This qualifies as HOB because organism doesn't match COB
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-06T10:00:00.000Z"
    )

    return gen


# =============================================================================
# Test Case 5: Blood Culture Contamination - 1 of 2 Positive
# =============================================================================

def create_contamination_1of2_positive():
    """
    Test Case 5: Blood Culture Contamination - 1 of 2 Positive

    Patient admitted January 2, 2025 (Day 1)
    Paired blood cultures on Day 4 (January 5):
    - Set A: S. epidermidis (Positive)
    - Set B: No growth (Negative)

    Expected:
    - Initial Population: 1
    - Blood Culture Contamination: Yes (1 of 2 sets positive for skin commensal)
    - HOB Event: No (skin commensal only, likely contamination)
    """
    gen = FHIRBundleGenerator("HOBContamination_1of2Positive")

    gen.add_patient(
        given_name="HOBContamination",
        family_name="OneOfTwo",
        birth_date="1972-11-08",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
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

    # Set A: Positive for S. epidermidis (skin commensal)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-05T10:00:00.000Z"
    )

    # Set B: Negative (no growth)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["no_growth"]["code"],
        organism_display=ORGANISMS["no_growth"]["display"],
        collected_datetime="2025-01-05T10:05:00.000Z"
    )

    return gen


# =============================================================================
# Test Case 6: Blood Culture Contamination - 2 of 2 Positive (NOT Contamination)
# =============================================================================

def create_contamination_2of2_positive():
    """
    Test Case 6: Blood Culture - 2 of 2 Positive (NOT Contamination)

    Patient admitted January 2, 2025 (Day 1)
    Paired blood cultures on Day 4 (January 5):
    - Set A: S. epidermidis (Positive)
    - Set B: S. epidermidis (Positive)

    Expected:
    - Initial Population: 1
    - Blood Culture Contamination: No (both sets positive = true bacteremia)
    - HOB Event: No (skin commensal, but may qualify for Matching Commensal)
    """
    gen = FHIRBundleGenerator("HOBContamination_2of2Positive")

    gen.add_patient(
        given_name="HOBContamination",
        family_name="TwoOfTwo",
        birth_date="1980-05-22",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-10T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "32485007",
            "display": "Hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Set A: Positive for S. epidermidis
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-05T14:00:00.000Z"
    )

    # Set B: Also Positive for S. epidermidis
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-05T14:05:00.000Z"
    )

    return gen


# =============================================================================
# Test Case 7: Matching Commensal HOB - Positive (≥4 days antibiotics)
# =============================================================================

def create_matching_commensal_positive():
    """
    Test Case 7: Matching Commensal HOB - Positive

    Patient admitted January 2, 2025 (Day 1)
    Blood cultures: S. epidermidis on Day 5 and Day 7
    Antibiotic: Vancomycin for 4 days (Jan 6-10)

    Expected:
    - Initial Population: 1
    - Matching Commensal HOB: Yes (≥2 cultures + ≥4 days antibiotics)
    - Standard HOB Event: No (skin commensal)
    """
    gen = FHIRBundleGenerator("HOBMatchingCommensal_Positive")

    gen.add_patient(
        given_name="HOBMatchingCommensal",
        family_name="Positive",
        birth_date="1965-03-20",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

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

    # First blood culture - Day 5 (January 6)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-06T10:00:00.000Z"
    )

    # Second blood culture - Day 7 (January 8)
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-08T14:00:00.000Z"
    )

    # Vancomycin for 4 days (meets threshold)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-06T12:00:00.000Z",
        effective_end="2025-01-10T12:00:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIBIOTICS["vancomycin"]["code"],
            "display": ANTIBIOTICS["vancomycin"]["display"]
        }
    )

    return gen


# =============================================================================
# Test Case 8: Matching Commensal HOB - Excluded (Insufficient Antibiotics)
# =============================================================================

def create_matching_commensal_insufficient_abx():
    """
    Test Case 8: Matching Commensal HOB - Excluded (Insufficient Antibiotics)

    Patient admitted January 2, 2025 (Day 1)
    Blood cultures: S. epidermidis on Day 5 and Day 7
    Antibiotic: Vancomycin for only 2 days (< 4 day threshold)

    Expected:
    - Initial Population: 1
    - Matching Commensal HOB: No (< 4 days antibiotics)
    - Standard HOB Event: No (skin commensal)
    """
    gen = FHIRBundleGenerator("HOBMatchingCommensal_InsufficientAbx")

    gen.add_patient(
        given_name="HOBMatchingCommensal",
        family_name="InsufficientAbx",
        birth_date="1955-09-15",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

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

    # First blood culture - Day 5
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-06T08:00:00.000Z"
    )

    # Second blood culture - Day 7
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_epidermidis"]["code"],
        organism_display=ORGANISMS["s_epidermidis"]["display"],
        collected_datetime="2025-01-08T10:00:00.000Z"
    )

    # Vancomycin for only 2 days (does NOT meet threshold)
    gen.add_medication_administration(
        encounter_id=enc_id,
        effective_start="2025-01-06T12:00:00.000Z",
        effective_end="2025-01-08T12:00:00.000Z",
        medication_code={
            "system": CODE_SYSTEMS["RXNORM"],
            "code": ANTIBIOTICS["vancomycin"]["code"],
            "display": ANTIBIOTICS["vancomycin"]["display"]
        }
    )

    return gen


# =============================================================================
# Test Case 9: Non-Measure HOB Event - High Risk (Non-Preventability)
# =============================================================================

def create_non_measure_high_risk():
    """
    Test Case 9: Non-Measure HOB Event - High Risk

    Patient admitted January 2, 2025 (Day 1)
    Conditions: Acute myeloid leukemia (AML) + Neutropenia
    Blood culture: E. coli on Day 5

    Expected:
    - Initial Population: 1
    - HOB Event: Yes (pathogenic organism on day 4+)
    - Non-Measure HOB: Yes (AML + neutropenia = high non-preventability)
    """
    gen = FHIRBundleGenerator("HOBNonMeasure_HighRisk")

    gen.add_patient(
        given_name="HOBNonMeasure",
        family_name="HighRisk",
        birth_date="1958-07-12",
        gender="male"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-12T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "32485007",
            "display": "Hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Condition: Acute myeloid leukemia (non-preventability factor)
    gen.add_condition(
        encounter_id=enc_id,
        code={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": CONDITIONS["aml"]["code"],
            "display": CONDITIONS["aml"]["display"]
        },
        onset_datetime="2024-10-15T00:00:00.000Z"
    )

    # Condition: Neutropenia (non-preventability factor)
    gen.add_condition(
        encounter_id=enc_id,
        code={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": CONDITIONS["neutropenia"]["code"],
            "display": CONDITIONS["neutropenia"]["display"]
        },
        onset_datetime="2025-01-03T00:00:00.000Z"
    )

    # Blood culture - Day 5 with pathogenic organism
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["e_coli"]["code"],
        organism_display=ORGANISMS["e_coli"]["display"],
        collected_datetime="2025-01-06T14:00:00.000Z"
    )

    return gen


# =============================================================================
# Test Case 10: Measurable HOB Event - No Risk Factors
# =============================================================================

def create_measurable_no_risk_factors():
    """
    Test Case 10: Measurable HOB Event - No Non-Preventability Risk Factors

    Patient admitted January 2, 2025 (Day 1)
    Conditions: Diabetes + Hypertension (common, NOT non-preventability factors)
    Blood culture: S. aureus on Day 5

    Expected:
    - Initial Population: 1
    - HOB Event: Yes (pathogenic organism on day 4+)
    - Non-Measure HOB: No (no non-preventability conditions)
    """
    gen = FHIRBundleGenerator("HOBMeasurable_NoRiskFactors")

    gen.add_patient(
        given_name="HOBMeasurable",
        family_name="NoRiskFactors",
        birth_date="1968-12-03",
        gender="female"
    )

    loc_id = gen.add_location(location_type=INPATIENT_LOCATION)

    enc_id = gen.add_encounter(
        start="2025-01-02T08:00:00.000Z",
        end="2025-01-10T12:00:00.000Z",
        status="finished",
        class_code="IMP",
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "32485007",
            "display": "Hospital admission"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Condition: Diabetes (common condition, NOT a non-preventability factor)
    gen.add_condition(
        encounter_id=enc_id,
        code={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": CONDITIONS["diabetes"]["code"],
            "display": CONDITIONS["diabetes"]["display"]
        },
        onset_datetime="2015-06-10T00:00:00.000Z"
    )

    # Condition: Hypertension (common condition, NOT a non-preventability factor)
    gen.add_condition(
        encounter_id=enc_id,
        code={
            "system": CODE_SYSTEMS["SNOMED"],
            "code": CONDITIONS["hypertension"]["code"],
            "display": CONDITIONS["hypertension"]["display"]
        },
        onset_datetime="2018-03-15T00:00:00.000Z"
    )

    # Blood culture - Day 5 with pathogenic organism
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["s_aureus"]["code"],
        organism_display=ORGANISMS["s_aureus"]["display"],
        collected_datetime="2025-01-06T09:00:00.000Z"
    )

    return gen


# =============================================================================
# Test Case 11: HOB Excluded - Same Species, Different SNOMED Codes
# =============================================================================

def create_hob_excluded_same_species_different_codes():
    """
    Test Case 11: HOB Excluded - Same Species with Different SNOMED Codes

    Patient admitted January 2, 2025 (Day 1)
    Blood culture on Day 2 (January 3): Pseudomonas aeruginosa (52499004) - COB event
    Blood culture on Day 6 (January 7): Carbapenem resistant P. aeruginosa (726492000)

    Location transfers:
    - Emergency Dept (1108-0): 08:00-12:00
    - 24 Hour Observation Area (1162-7): 12:05-20:00
    - Medical Ward (1060-3): 20:05 onwards

    Key Insight: Both codes represent the SAME SPECIES (Pseudomonas aeruginosa).
    The resistance phenotype does not change organism identity for COB exclusion.

    Expected:
    - Initial Population: 1 (qualifying inpatient encounter)
    - COB Event: Positive (day 2 culture)
    - HOB Event: Excluded (same species as prior COB, despite different SNOMED code)
    """
    gen = FHIRBundleGenerator("HOBExcluded_SameSpeciesDifferentCodes")

    # Add patient (adult male)
    gen.add_patient(
        given_name="HOBExcluded",
        family_name="SameSpeciesDiffCodes",
        birth_date="1972-11-30",
        gender="male"
    )

    # Add multiple locations for patient transfers
    # Location 1: Emergency Department
    loc_ed = gen.add_location(location_type={
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1108-0",
        "display": "Emergency Department"
    })

    # Location 2: 24 Hour Observation Area
    loc_obs = gen.add_location(location_type={
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1162-7",
        "display": "24 Hour Observation Area"
    })

    # Location 3: Medical Ward
    loc_med = gen.add_location(location_type={
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1060-3",
        "display": "Medical Ward"
    })

    # Add inpatient encounter - Day 1 = January 2, 2025
    # With multiple locations showing patient transfers
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
        locations=[
            {
                "location_id": loc_ed,
                "display": "Emergency Dept.",
                "period": {
                    "start": "2025-01-02T08:00:00.000Z",
                    "end": "2025-01-02T12:00:00.000Z"
                }
            },
            {
                "location_id": loc_obs,
                "display": "Adult Observation Department",
                "period": {
                    "start": "2025-01-02T12:05:00.000Z",
                    "end": "2025-01-02T20:00:00.000Z"
                }
            },
            {
                "location_id": loc_med,
                "display": "General Medicine Ward",
                "period": {
                    "start": "2025-01-02T20:05:00.000Z",
                    "end": "2025-01-10T08:00:00.000Z"
                }
            },
            {
                "location_id": loc_med,
                "display": "Room 123",
                "physicalType": {"code": "ro", "display": "Room"}
            },
            {
                "location_id": loc_med,
                "display": "Room 1 / Bed 2",
                "physicalType": {"code": "bd", "display": "Bed"}
            }
        ]
    )

    # Add coverage
    gen.add_coverage(
        start="2025-01-01",
        end="2025-12-31"
    )

    # Blood culture on Day 2 (January 3, 2025) - COB event with P. aeruginosa
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["p_aeruginosa"]["code"],
        organism_display=ORGANISMS["p_aeruginosa"]["display"],
        collected_datetime="2025-01-03T18:43:00.000Z"
    )

    # Blood culture on Day 6 (January 7, 2025) - Carbapenem resistant P. aeruginosa
    # This should be EXCLUDED from HOB because it's the same species as prior COB
    gen.add_blood_culture(
        encounter_id=enc_id,
        organism_code=ORGANISMS["p_aeruginosa_cr"]["code"],
        organism_display=ORGANISMS["p_aeruginosa_cr"]["display"],
        collected_datetime="2025-01-07T18:43:00.000Z"
    )

    return gen


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Generate all HOB test cases and export to MADiE-compatible format."""

    print("=" * 70)
    print("HOB (Hospital-Onset Bacteremia & Fungemia) Test Case Generator")
    print("=" * 70)
    print(f"Measurement Period: {MEASUREMENT_PERIOD_START} to {MEASUREMENT_PERIOD_END}")
    print(f"HOB Definition: Blood culture positive on hospital day {HOB_TIMING_THRESHOLD}+")
    print()

    # Create MADiE exporter
    exporter = MADiEExporter(
        measure_name="NHSNACHMonthly1",
        version="0.0.000",
        measure_url="https://madie.cms.gov/Measure/NHSNACHMonthly1",
        measurement_period_start=MEASUREMENT_PERIOD_START,
        measurement_period_end=MEASUREMENT_PERIOD_END
    )

    # Add test cases
    # All test cases should have initialPopulation: 1 (qualifying encounter during MP)

    exporter.add_test_case(
        generator_func=create_hob_positive_day4_saureus,
        series="HOBPositive",
        title="Day4SAureus",
        description="HOB positive event: S. aureus blood culture on hospital day 4",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_hob_positive_day5_candida,
        series="HOBPositive",
        title="Day5Candida",
        description="HOB positive event: Candida albicans (fungemia) on hospital day 5",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_hob_excluded_matching_cob,
        series="HOBExcluded",
        title="MatchingCOB",
        description="HOB excluded: Same E. coli organism on day 2 (COB) and day 5",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_hob_positive_nonmatching_cob,
        series="HOBPositive",
        title="NonMatchingCOB",
        description="HOB positive: E. coli on day 2 (COB), S. aureus on day 5 (HOB)",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 5: Blood Culture Contamination - 1 of 2 Positive
    exporter.add_test_case(
        generator_func=create_contamination_1of2_positive,
        series="HOBContamination",
        title="1of2Positive",
        description="Blood culture contamination: 1 of 2 paired sets positive for S. epidermidis",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 6: Blood Culture - 2 of 2 Positive (NOT Contamination)
    exporter.add_test_case(
        generator_func=create_contamination_2of2_positive,
        series="HOBContamination",
        title="2of2Positive",
        description="NOT contamination: Both paired sets positive for S. epidermidis (true bacteremia)",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 7: Matching Commensal HOB - Positive
    exporter.add_test_case(
        generator_func=create_matching_commensal_positive,
        series="HOBMatchingCommensal",
        title="Positive",
        description="Matching Commensal HOB: S. epidermidis from 2 cultures + 4 days Vancomycin",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 8: Matching Commensal HOB - Excluded (Insufficient Antibiotics)
    exporter.add_test_case(
        generator_func=create_matching_commensal_insufficient_abx,
        series="HOBMatchingCommensal",
        title="InsufficientAbx",
        description="Matching Commensal excluded: S. epidermidis from 2 cultures but only 2 days antibiotics",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 9: Non-Measure HOB Event - High Risk
    exporter.add_test_case(
        generator_func=create_non_measure_high_risk,
        series="HOBNonMeasure",
        title="HighRisk",
        description="Non-Measure HOB: E. coli bacteremia in patient with AML and neutropenia",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 10: Measurable HOB Event - No Risk Factors
    exporter.add_test_case(
        generator_func=create_measurable_no_risk_factors,
        series="HOBMeasurable",
        title="NoRiskFactors",
        description="Measurable HOB: S. aureus bacteremia in patient with diabetes/HTN (no non-preventability)",
        expected_populations={"initialPopulation": 1}
    )

    # Test Case 11: HOB Excluded - Same Species, Different SNOMED Codes
    exporter.add_test_case(
        generator_func=create_hob_excluded_same_species_different_codes,
        series="HOBExcluded",
        title="SameSpeciesDiffCodes",
        description="HOB excluded: P. aeruginosa (day 2) and CR P. aeruginosa (day 6) - same species, different codes",
        expected_populations={"initialPopulation": 1}
    )

    # Export test cases
    output_path = exporter.export(create_zip=True)

    print()
    print("=" * 70)
    print("HOB Test Cases Generated Successfully!")
    print("=" * 70)
    print(f"Output: {output_path}")
    print()
    print("Next steps:")
    print("1. Import the ZIP file into MADiE")
    print("2. Run measure execution against NHSNACHMonthly1")
    print("3. Verify all test cases show initialPopulation = 1")
    print("4. Use collected data for downstream HOB evaluation")


if __name__ == "__main__":
    main()
