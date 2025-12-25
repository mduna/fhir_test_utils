#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hypoglycemia (Hospital-Acquired Hypoglycemia) Test Case Generator

Protocol Definition:
- Severe Hypoglycemia Event: Blood glucose < 40 mg/dL during inpatient encounter
- Hospital Day 1 = Admission date
- Measurement Period: 2025-01-01 to 2025-01-31

Test Cases Generated (10 total):
Positive Cases:
1. SevereHypoWithInsulin - Glucose 35 mg/dL after insulin
2. SevereHypoWithOralAgent - Glucose 38 mg/dL after glipizide
3. SevereHypoDay1 - Glucose 32 mg/dL on admission day
4. MultipleHypoEvents - Two severe events in same encounter

Exclusion Cases:
5. ModerateHypoExcluded - Glucose 45 mg/dL (above threshold)
6. HypoWithoutMedication - Severe hypo without antidiabetic
7. PreAdmissionHypo - Glucose before encounter start
8. OutpatientEncounter - ED visit only (not inpatient)

Edge Cases:
9. GlucoseAtThreshold - Glucose exactly 40 mg/dL
10. ICUHypoglycemia - ICU patient with insulin drip

Usage:
    cd protocols/hypoglycemia
    python generate_hypoglycemia_tests.py
    # Output: NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip
"""

import sys
import os

# Add parent of fhir_test_utils to path for package imports
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, root_dir)

from fhir_test_utils import FHIRBundleGenerator, MADiEExporter
from fhir_test_utils.code_systems import CODE_SYSTEMS


# =============================================================================
# Hypoglycemia Protocol Constants
# =============================================================================

SEVERE_HYPOGLYCEMIA_THRESHOLD = 40  # Blood glucose < 40 mg/dL
MEASUREMENT_PERIOD_START = "2025-01-01"
MEASUREMENT_PERIOD_END = "2025-01-31"

# LOINC codes for glucose measurements
GLUCOSE_CODES = {
    "blood_glucose": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "2339-0",
        "display": "Glucose [Mass/volume] in Blood"
    },
    "plasma_glucose": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "2345-7",
        "display": "Glucose [Mass/volume] in Serum or Plasma"
    },
    "poc_glucose": {
        "system": CODE_SYSTEMS["LOINC"],
        "code": "41653-7",
        "display": "Glucose [Mass/volume] in Capillary blood by Glucometer"
    },
}

# Medication RxNorm codes
MEDICATIONS = {
    "regular_insulin": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "311034",
        "display": "Insulin regular, human 100 UNT/ML Injectable Solution"
    },
    "insulin_glargine": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "261551",
        "display": "Insulin glargine 100 UNT/ML Injectable Solution"
    },
    "nph_insulin": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "311041",
        "display": "Insulin, isophane human 100 UNT/ML Injectable Suspension"
    },
    "insulin_iv": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "311033",
        "display": "Insulin regular, human 100 UNT/ML Injectable Solution"
    },
    "glipizide": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "310488",
        "display": "Glipizide 10 MG Oral Tablet"
    },
    "glyburide": {
        "system": CODE_SYSTEMS["RXNORM"],
        "code": "310534",
        "display": "Glyburide 5 MG Oral Tablet"
    },
}

# Condition SNOMED codes
CONDITIONS = {
    "diabetes_type2": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "44054006",
        "display": "Diabetes mellitus type 2"
    },
    "dka": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "420422005",
        "display": "Diabetic ketoacidosis"
    },
    "sepsis": {
        "system": CODE_SYSTEMS["SNOMED"],
        "code": "91302008",
        "display": "Sepsis"
    },
}

# HSLOC codes for locations
LOCATIONS = {
    "medical_ward": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1060-3",
        "display": "Medical Ward"
    },
    "trauma_icu": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1025-6",
        "display": "Trauma Critical Care"
    },
    "medical_icu": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1027-2",
        "display": "Medical Critical Care"
    },
    "emergency": {
        "system": CODE_SYSTEMS["HSLOC"],
        "code": "1108-0",
        "display": "Emergency Department"
    },
}


# =============================================================================
# Test Case Generator Functions
# =============================================================================

def create_severe_hypo_with_insulin():
    """
    Test Case 1: SevereHypoWithInsulin

    Adult patient admitted with diabetes, receives insulin,
    develops severe hypoglycemia (35 mg/dL) on hospital day 2.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (glucose 35 < 40)
    """
    gen = FHIRBundleGenerator("SevereHypoWithInsulin")

    gen.add_patient(
        given_name="John",
        family_name="Hypo",
        birth_date="1965-03-15",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-05T08:00:00.000Z",
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

    # Add diabetes condition
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["diabetes_type2"],
        onset_datetime="2025-01-05T08:30:00.000Z"
    )

    # Add insulin administration on day 2 morning
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-06T08:00:00.000Z",
        effective_end="2025-01-06T08:15:00.000Z"
    )

    # Add severe hypoglycemia - glucose 35 mg/dL on day 2 afternoon
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=35,
        unit="mg/dL",
        effective_datetime="2025-01-06T14:00:00.000Z"
    )

    return gen


def create_severe_hypo_with_oral_agent():
    """
    Test Case 2: SevereHypoWithOralAgent

    Patient on oral sulfonylurea (glipizide) develops severe hypoglycemia.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (glucose 38 < 40)
    """
    gen = FHIRBundleGenerator("SevereHypoWithOralAgent")

    gen.add_patient(
        given_name="Mary",
        family_name="Oral",
        birth_date="1958-07-22",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-08T10:00:00.000Z",
        end="2025-01-14T14:00:00.000Z",
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

    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["diabetes_type2"],
        onset_datetime="2025-01-08T10:30:00.000Z"
    )

    # Glipizide administration
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["glipizide"],
        effective_start="2025-01-09T08:00:00.000Z",
        effective_end="2025-01-09T08:05:00.000Z"
    )

    # Severe hypoglycemia - glucose 38 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=38,
        unit="mg/dL",
        effective_datetime="2025-01-09T16:00:00.000Z"
    )

    return gen


def create_severe_hypo_day1():
    """
    Test Case 3: SevereHypoDay1

    Patient develops severe hypoglycemia on admission day (day 1).

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (day 1 severe hypo)
    """
    gen = FHIRBundleGenerator("SevereHypoDay1")

    gen.add_patient(
        given_name="Early",
        family_name="Event",
        birth_date="1972-11-30",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["trauma_icu"])

    enc_id = gen.add_encounter(
        start="2025-01-10T14:00:00.000Z",
        end="2025-01-15T10:00:00.000Z",
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

    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["diabetes_type2"],
        onset_datetime="2025-01-10T14:30:00.000Z"
    )

    # NPH insulin on day 1
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["nph_insulin"],
        effective_start="2025-01-10T16:00:00.000Z",
        effective_end="2025-01-10T16:10:00.000Z"
    )

    # Severe hypoglycemia on day 1 - glucose 32 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=32,
        unit="mg/dL",
        effective_datetime="2025-01-10T22:00:00.000Z"
    )

    return gen


def create_multiple_hypo_events():
    """
    Test Case 4: MultipleHypoEvents

    Patient has two separate severe hypoglycemia events during stay.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Events: 2 (both < 40 mg/dL)
    """
    gen = FHIRBundleGenerator("MultipleHypoEvents")

    gen.add_patient(
        given_name="Multiple",
        family_name="Events",
        birth_date="1960-05-18",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-03T08:00:00.000Z",
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

    # Insulin glargine
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["insulin_glargine"],
        effective_start="2025-01-03T20:00:00.000Z",
        effective_end="2025-01-03T20:10:00.000Z"
    )

    # First severe hypoglycemia - glucose 36 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=36,
        unit="mg/dL",
        effective_datetime="2025-01-04T06:00:00.000Z"
    )

    # Second insulin dose
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["insulin_glargine"],
        effective_start="2025-01-06T20:00:00.000Z",
        effective_end="2025-01-06T20:10:00.000Z"
    )

    # Second severe hypoglycemia - glucose 28 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["plasma_glucose"],
        value=28,
        unit="mg/dL",
        effective_datetime="2025-01-07T05:00:00.000Z"
    )

    return gen


def create_moderate_hypo_excluded():
    """
    Test Case 5: ModerateHypoExcluded

    Patient has moderate hypoglycemia (45 mg/dL), above severe threshold.

    Expected:
    - Initial Population: 1 (qualifying encounter)
    - Hypoglycemia Event: Excluded (45 >= 40)
    """
    gen = FHIRBundleGenerator("ModerateHypoExcluded")

    gen.add_patient(
        given_name="Moderate",
        family_name="Hypo",
        birth_date="1968-09-25",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-06T09:00:00.000Z",
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

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-07T08:00:00.000Z",
        effective_end="2025-01-07T08:10:00.000Z"
    )

    # Moderate hypoglycemia - glucose 45 mg/dL (NOT severe)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=45,
        unit="mg/dL",
        effective_datetime="2025-01-07T14:00:00.000Z"
    )

    return gen


def create_hypo_without_medication():
    """
    Test Case 6: HypoWithoutMedication

    Severe hypoglycemia without antidiabetic medication (spontaneous/sepsis).

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (severe hypo, non-medication cause)
    """
    gen = FHIRBundleGenerator("HypoWithoutMedication")

    gen.add_patient(
        given_name="No",
        family_name="Meds",
        birth_date="1945-12-01",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-12T11:00:00.000Z",
        end="2025-01-17T10:00:00.000Z",
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

    # Sepsis condition (can cause hypoglycemia without diabetes meds)
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["sepsis"],
        onset_datetime="2025-01-12T11:30:00.000Z"
    )

    # Severe hypoglycemia without antidiabetic - glucose 35 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=35,
        unit="mg/dL",
        effective_datetime="2025-01-13T04:00:00.000Z"
    )

    return gen


def create_pre_admission_hypo():
    """
    Test Case 7: PreAdmissionHypo

    Glucose drawn before encounter start time (ED glucose before admission).

    Expected:
    - Initial Population: 1 (qualifying encounter)
    - Hypoglycemia Event: Excluded (glucose before encounter start)
    """
    gen = FHIRBundleGenerator("PreAdmissionHypo")

    gen.add_patient(
        given_name="Pre",
        family_name="Admission",
        birth_date="1970-04-10",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-15T14:00:00.000Z",  # Admitted at 14:00
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

    # Glucose drawn BEFORE admission (in ED) - glucose 32 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=32,
        unit="mg/dL",
        effective_datetime="2025-01-15T12:00:00.000Z"  # 2 hours before admit
    )

    return gen


def create_outpatient_encounter():
    """
    Test Case 8: OutpatientEncounter

    ED encounter only (not admitted), has severe hypoglycemia.

    Expected:
    - Initial Population: 1 (CQL includes ED locations in value set)
    - Hypoglycemia Event: Positive (glucose 30 < 40)

    CQL Note: The CQL logic includes encounters where location type is in
    "Inpatient, Emergency, and Observation Locations" value set. ED encounters
    are included even though encounter class is EMER (not inpatient). This may
    be a flaw - clinically, ED-only visits are not "hospital-acquired".
    """
    gen = FHIRBundleGenerator("OutpatientEncounter")

    gen.add_patient(
        given_name="ED",
        family_name="Only",
        birth_date="1975-08-20",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["emergency"])

    # ED encounter only - class = EMER, not IMP
    enc_id = gen.add_encounter(
        start="2025-01-18T16:00:00.000Z",
        end="2025-01-18T22:00:00.000Z",
        status="finished",
        class_code="EMER",  # Emergency, not inpatient
        type_coding=[{
            "system": CODE_SYSTEMS["SNOMED"],
            "code": "4525004",
            "display": "Emergency department visit"
        }],
        location_id=loc_id
    )

    gen.add_coverage(start="2025-01-01", end="2025-12-31")

    # Severe hypoglycemia in ED - glucose 30 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["poc_glucose"],
        value=30,
        unit="mg/dL",
        effective_datetime="2025-01-18T17:00:00.000Z"
    )

    return gen


def create_glucose_at_threshold():
    """
    Test Case 9: GlucoseAtThreshold

    Glucose exactly at 40 mg/dL (boundary condition).

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Excluded (40 is NOT < 40)
    """
    gen = FHIRBundleGenerator("GlucoseAtThreshold")

    gen.add_patient(
        given_name="At",
        family_name="Threshold",
        birth_date="1962-02-28",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-20T08:00:00.000Z",
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

    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-21T06:00:00.000Z",
        effective_end="2025-01-21T06:10:00.000Z"
    )

    # Glucose EXACTLY at 40 mg/dL (boundary - NOT severe)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=40,
        unit="mg/dL",
        effective_datetime="2025-01-21T12:00:00.000Z"
    )

    return gen


def create_icu_hypoglycemia():
    """
    Test Case 10: ICUHypoglycemia

    ICU patient with insulin drip develops severe hypoglycemia.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (severe hypo in ICU)
    """
    gen = FHIRBundleGenerator("ICUHypoglycemia")

    gen.add_patient(
        given_name="ICU",
        family_name="Patient",
        birth_date="1955-06-15",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_icu"])

    enc_id = gen.add_encounter(
        start="2025-01-22T02:00:00.000Z",
        end="2025-01-28T14:00:00.000Z",
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

    # DKA condition
    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["dka"],
        onset_datetime="2025-01-22T02:30:00.000Z"
    )

    # IV insulin infusion
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["insulin_iv"],
        effective_start="2025-01-22T04:00:00.000Z",
        effective_end="2025-01-22T04:30:00.000Z"
    )

    # Severe hypoglycemia in ICU - glucose 25 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=25,
        unit="mg/dL",
        effective_datetime="2025-01-22T10:00:00.000Z"
    )

    return gen


# =============================================================================
# New Test Cases for Surveillance Metric Coverage
# =============================================================================

def create_hypo_with_resolution():
    """
    Test Case 11: HypoWithResolution (Metric 4)

    Severe hypoglycemia followed by resolution (BG ≥70 mg/dL).
    Tests Metric 4: Severe Hypoglycemia Resolution time.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive
    - Resolution: Yes (BG 85 mg/dL 2 hours after severe hypo)
    """
    gen = FHIRBundleGenerator("HypoWithResolution")

    gen.add_patient(
        given_name="Resolution",
        family_name="Test",
        birth_date="1963-04-20",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-07T08:00:00.000Z",
        end="2025-01-12T14:00:00.000Z",
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

    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["diabetes_type2"],
        onset_datetime="2025-01-07T08:30:00.000Z"
    )

    # Insulin administration
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-08T06:00:00.000Z",
        effective_end="2025-01-08T06:10:00.000Z"
    )

    # Severe hypoglycemia - glucose 32 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=32,
        unit="mg/dL",
        effective_datetime="2025-01-08T10:00:00.000Z"
    )

    # Resolution - glucose 85 mg/dL (≥70) 2 hours later
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=85,
        unit="mg/dL",
        effective_datetime="2025-01-08T12:00:00.000Z"
    )

    return gen


def create_denominator_only_no_hypo():
    """
    Test Case 12: DenominatorOnlyNoHypo (Metric 1,2 Denominator)

    Patient receives ADD but has NO hypoglycemia event.
    Tests the denominator: encounters/days with ADD administered.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: None (denominator only)
    """
    gen = FHIRBundleGenerator("DenominatorOnlyNoHypo")

    gen.add_patient(
        given_name="Denominator",
        family_name="Only",
        birth_date="1958-11-12",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-09T10:00:00.000Z",
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

    gen.add_condition(
        encounter_id=enc_id,
        code=CONDITIONS["diabetes_type2"],
        onset_datetime="2025-01-09T10:30:00.000Z"
    )

    # Insulin administration (qualifies for denominator)
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["insulin_glargine"],
        effective_start="2025-01-10T08:00:00.000Z",
        effective_end="2025-01-10T08:10:00.000Z"
    )

    # Normal glucose - NO hypoglycemia (120 mg/dL)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=120,
        unit="mg/dL",
        effective_datetime="2025-01-10T14:00:00.000Z"
    )

    return gen


def create_ed_add_within_1_hour():
    """
    Test Case 13: EDAddWithin1Hour (Metric 1 Footnote)

    ADD administered in ED within 1 hour of inpatient admission.
    Per footnote**: Includes ADD in ED ending within 1 hour of admission.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Positive (ED ADD counts)
    """
    gen = FHIRBundleGenerator("EDAddWithin1Hour")

    gen.add_patient(
        given_name="ED",
        family_name="Insulin",
        birth_date="1966-08-05",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    # Inpatient encounter starts at 14:00
    enc_id = gen.add_encounter(
        start="2025-01-11T14:00:00.000Z",
        end="2025-01-16T10:00:00.000Z",
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

    # Insulin given in ED at 13:30 (30 min before admission - within 1 hour)
    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-11T13:30:00.000Z",
        effective_end="2025-01-11T13:40:00.000Z"
    )

    # Severe hypoglycemia after admission - glucose 34 mg/dL
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=34,
        unit="mg/dL",
        effective_datetime="2025-01-11T16:00:00.000Z"
    )

    return gen


def create_repeat_bg_exclusion():
    """
    Test Case 14: RepeatBGExclusion (Metric 1 Footnote)

    Severe hypoglycemia followed by repeat BG >80 within 5 minutes.
    Per footnote*: Excluded if repeat BG >80 mg/dL within 5 min of initial low.

    Expected:
    - Initial Population: 1
    - Hypoglycemia Event: Excluded (repeat BG >80 within 5 min)
    """
    gen = FHIRBundleGenerator("RepeatBGExclusion")

    gen.add_patient(
        given_name="Repeat",
        family_name="Test",
        birth_date="1971-02-14",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-13T08:00:00.000Z",
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

    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["regular_insulin"],
        effective_start="2025-01-14T06:00:00.000Z",
        effective_end="2025-01-14T06:10:00.000Z"
    )

    # Initial low BG - glucose 35 mg/dL at 10:00:00
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["poc_glucose"],
        value=35,
        unit="mg/dL",
        effective_datetime="2025-01-14T10:00:00.000Z"
    )

    # Repeat BG >80 within 5 minutes - glucose 95 mg/dL at 10:04:00
    # This suggests the initial reading was erroneous
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["poc_glucose"],
        value=95,
        unit="mg/dL",
        effective_datetime="2025-01-14T10:04:00.000Z"
    )

    return gen


def create_moderate_hypo_metric2():
    """
    Test Case 15: ModerateHypoMetric2 (Metric 2 Footnote***)

    Moderate hypoglycemia (40-53 mg/dL) for Metric 2 reporting.
    Per footnote***: Rate reported for moderate (40-53 mg/dL).

    Expected:
    - Initial Population: 1
    - Severe Hypoglycemia: No (not <40)
    - Moderate Hypoglycemia: Yes (47 mg/dL in 40-53 range)
    """
    gen = FHIRBundleGenerator("ModerateHypoMetric2")

    gen.add_patient(
        given_name="Moderate",
        family_name="Range",
        birth_date="1959-06-30",
        gender="female"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-15T09:00:00.000Z",
        end="2025-01-20T14:00:00.000Z",
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

    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["glipizide"],
        effective_start="2025-01-16T08:00:00.000Z",
        effective_end="2025-01-16T08:05:00.000Z"
    )

    # Moderate hypoglycemia - glucose 47 mg/dL (in 40-53 range)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=47,
        unit="mg/dL",
        effective_datetime="2025-01-16T14:00:00.000Z"
    )

    return gen


def create_mild_hypo_metric2():
    """
    Test Case 16: MildHypoMetric2 (Metric 2 Footnote***)

    Mild hypoglycemia (54-70 mg/dL) for Metric 2 reporting.
    Per footnote***: Rate reported for mild (54-70 mg/dL).

    Expected:
    - Initial Population: 1
    - Severe Hypoglycemia: No (not <40)
    - Mild Hypoglycemia: Yes (62 mg/dL in 54-70 range)
    """
    gen = FHIRBundleGenerator("MildHypoMetric2")

    gen.add_patient(
        given_name="Mild",
        family_name="Range",
        birth_date="1952-09-18",
        gender="male"
    )

    loc_id = gen.add_location(location_type=LOCATIONS["medical_ward"])

    enc_id = gen.add_encounter(
        start="2025-01-17T10:00:00.000Z",
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

    gen.add_medication_administration(
        encounter_id=enc_id,
        medication_code=MEDICATIONS["nph_insulin"],
        effective_start="2025-01-18T07:00:00.000Z",
        effective_end="2025-01-18T07:10:00.000Z"
    )

    # Mild hypoglycemia - glucose 62 mg/dL (in 54-70 range)
    gen.add_observation(
        encounter_id=enc_id,
        category="laboratory",
        code=GLUCOSE_CODES["blood_glucose"],
        value=62,
        unit="mg/dL",
        effective_datetime="2025-01-18T12:00:00.000Z"
    )

    return gen


# =============================================================================
# Main Execution
# =============================================================================

def main():
    """Generate all hypoglycemia test cases and export to MADiE format."""

    print("=" * 70)
    print("Hypoglycemia (Hospital-Acquired Hypoglycemia) Test Case Generator")
    print("=" * 70)
    print(f"Measurement Period: {MEASUREMENT_PERIOD_START} to {MEASUREMENT_PERIOD_END}")
    print(f"Severe Hypoglycemia Definition: Blood glucose < {SEVERE_HYPOGLYCEMIA_THRESHOLD} mg/dL")
    print()

    # Create exporter
    exporter = MADiEExporter(
        measure_name="NHSNACHMonthly1",
        version="0.0.000",
        measure_url="https://madie.cms.gov/Measure/NHSNACHMonthly1",
        measurement_period_start=MEASUREMENT_PERIOD_START,
        measurement_period_end=MEASUREMENT_PERIOD_END
    )

    # =========================================================================
    # Positive Cases
    # =========================================================================

    exporter.add_test_case(
        generator_func=create_severe_hypo_with_insulin,
        series="Hypoglycemia",
        title="SevereHypoWithInsulin",
        description="Severe hypoglycemia (35 mg/dL) after insulin administration on day 2",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_severe_hypo_with_oral_agent,
        series="Hypoglycemia",
        title="SevereHypoWithOralAgent",
        description="Severe hypoglycemia (38 mg/dL) after oral sulfonylurea (glipizide)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_severe_hypo_day1,
        series="Hypoglycemia",
        title="SevereHypoDay1",
        description="Severe hypoglycemia (32 mg/dL) on admission day (day 1)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_multiple_hypo_events,
        series="Hypoglycemia",
        title="MultipleHypoEvents",
        description="Two severe hypoglycemia events (36 mg/dL and 28 mg/dL) during same encounter",
        expected_populations={"initialPopulation": 1}
    )

    # =========================================================================
    # Exclusion Cases
    # =========================================================================

    exporter.add_test_case(
        generator_func=create_moderate_hypo_excluded,
        series="Hypoglycemia",
        title="ModerateHypoExcluded",
        description="Moderate hypoglycemia (45 mg/dL) - above severe threshold, excluded",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_hypo_without_medication,
        series="Hypoglycemia",
        title="HypoWithoutMedication",
        description="Severe hypoglycemia (35 mg/dL) without antidiabetic medication (sepsis)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_pre_admission_hypo,
        series="Hypoglycemia",
        title="PreAdmissionHypo",
        description="Pre-admission hypoglycemia (32 mg/dL) - glucose before encounter start",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_outpatient_encounter,
        series="Hypoglycemia",
        title="OutpatientEncounter",
        description="ED-only encounter with severe hypoglycemia - included due to CQL location value set (potential CQL flaw)",
        expected_populations={"initialPopulation": 1}
    )

    # =========================================================================
    # Edge Cases
    # =========================================================================

    exporter.add_test_case(
        generator_func=create_glucose_at_threshold,
        series="Hypoglycemia",
        title="GlucoseAtThreshold",
        description="Glucose exactly at 40 mg/dL - boundary condition (NOT < 40)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_icu_hypoglycemia,
        series="Hypoglycemia",
        title="ICUHypoglycemia",
        description="ICU patient with DKA on insulin drip, severe hypoglycemia (25 mg/dL)",
        expected_populations={"initialPopulation": 1}
    )

    # =========================================================================
    # Surveillance Metric Coverage Cases
    # =========================================================================

    exporter.add_test_case(
        generator_func=create_hypo_with_resolution,
        series="Hypoglycemia",
        title="HypoWithResolution",
        description="Metric 4: Severe hypo (32 mg/dL) with resolution (85 mg/dL) 2 hours later",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_denominator_only_no_hypo,
        series="Hypoglycemia",
        title="DenominatorOnlyNoHypo",
        description="Metric 1/2 Denominator: ADD given but no hypoglycemia (glucose 120 mg/dL)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_ed_add_within_1_hour,
        series="Hypoglycemia",
        title="EDAddWithin1Hour",
        description="Footnote**: ED insulin 30 min before admission, severe hypo after",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_repeat_bg_exclusion,
        series="Hypoglycemia",
        title="RepeatBGExclusion",
        description="Footnote*: Initial BG 35, repeat BG 95 within 5 min (erroneous reading)",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_moderate_hypo_metric2,
        series="Hypoglycemia",
        title="ModerateHypoMetric2",
        description="Footnote***: Moderate hypoglycemia (47 mg/dL) in 40-53 range",
        expected_populations={"initialPopulation": 1}
    )

    exporter.add_test_case(
        generator_func=create_mild_hypo_metric2,
        series="Hypoglycemia",
        title="MildHypoMetric2",
        description="Footnote***: Mild hypoglycemia (62 mg/dL) in 54-70 range",
        expected_populations={"initialPopulation": 1}
    )

    # Export
    output_path = exporter.export(create_zip=True)

    print("=" * 70)
    print("Hypoglycemia Test Cases Generated Successfully!")
    print("=" * 70)
    print(f"Output: {output_path}")
    print()
    print("Next steps:")
    print("1. Import the ZIP file into MADiE")
    print("2. Run measure execution against NHSNACHMonthly1")
    print("3. Verify all test cases show expected initialPopulation values")
    print("4. Use collected data for downstream hypoglycemia evaluation")


if __name__ == "__main__":
    main()
