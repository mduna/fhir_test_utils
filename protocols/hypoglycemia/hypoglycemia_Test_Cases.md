# Hypoglycemia Test Cases Specification

## Overview

This document specifies all test cases for the Hypoglycemia (Hospital-Acquired Hypoglycemia) protocol, supporting the NHSN Glycemic Control Surveillance Metrics.

**Measurement Period**: January 1, 2025 to January 31, 2025
**CQL Module**: `NHSNAcuteCareHospitalMonthlyInitialPopulation1`
**Severe Hypoglycemia Definition**: Blood glucose < 40 mg/dL during inpatient encounter

---

## NHSN Hypoglycemia Surveillance Metrics Coverage

| Metric | Description | Numerator | Denominator |
|--------|-------------|-----------|-------------|
| **Metric 1** | Hospital Harm, Severe Hypoglycemia (NQF 3503e) | Encounters with BG <40 + ADD within 24h | Encounters with ≥1 ADD |
| **Metric 2** | Severe Hypoglycemia Days | Days with BG <40 + ADD within 24h | Days with ≥1 ADD |
| **Metric 3** | Recurrent Hypoglycemia | Hypo day preceded by hypo within 24h | - |
| **Metric 4** | Severe Hypoglycemia Resolution | Time from BG <40 to BG ≥70 | - |

**Footnotes from Protocol:**
- \* Excludes if repeat BG >80 mg/dL within 5 minutes of initial low BG
- \*\* Includes ADD in ED/observation ending within 1 hour of admission
- \*\*\* Also reports moderate (40-53 mg/dL) and mild (54-70 mg/dL) rates

## Test Case Summary

| # | Test Case | Category | Expected IP | Metric | Description |
|---|-----------|----------|-------------|--------|-------------|
| 1 | SevereHypoWithInsulin | Positive | 1 | 1,2 | Glucose 35 mg/dL after insulin |
| 2 | SevereHypoWithOralAgent | Positive | 1 | 1,2 | Glucose 38 mg/dL after glipizide |
| 3 | SevereHypoDay1 | Positive | 1 | 1,2 | Glucose 32 mg/dL on admission day |
| 4 | MultipleHypoEvents | Positive | 1 | 1,2,3 | Two severe hypoglycemia events |
| 5 | ModerateHypoExcluded | Exclusion | 1 | - | Glucose 45 mg/dL (above threshold) |
| 6 | HypoWithoutMedication | Positive | 1 | - | Glucose 35 mg/dL, no antidiabetic |
| 7 | PreAdmissionHypo | Exclusion | 1 | - | Glucose before encounter start |
| 8 | OutpatientEncounter | CQL Quirk | 1 | - | ED encounter only (see CQL note) |
| 9 | GlucoseAtThreshold | Edge | 1 | - | Glucose exactly 40 mg/dL |
| 10 | ICUHypoglycemia | Positive | 1 | 1,2 | ICU patient with severe hypo |
| 11 | HypoWithResolution | Positive | 1 | 4 | Severe hypo with resolution BG ≥70 |
| 12 | DenominatorOnlyNoHypo | Denominator | 1 | 1,2 Denom | ADD given, no hypoglycemia |
| 13 | EDAddWithin1Hour | Positive | 1 | 1** | ED insulin within 1h of admission |
| 14 | RepeatBGExclusion | Exclusion | 1 | 1* | Repeat BG >80 within 5 min |
| 15 | ModerateHypoMetric2 | Moderate | 1 | 2*** | Glucose 47 mg/dL (40-53 range) |
| 16 | MildHypoMetric2 | Mild | 1 | 2*** | Glucose 62 mg/dL (54-70 range) |

---

## Test Case 1: SevereHypoWithInsulin

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaSevereHypoWithInsulin.json`

**Scenario**: Adult patient admitted with diabetes, receives insulin, develops severe hypoglycemia on hospital day 2.

**Purpose**: Validates detection of medication-associated severe hypoglycemia event.

| Resource | Details |
|----------|---------|
| Patient | John Hypo, DOB 1965-03-15, Male |
| Encounter | Admit 2025-01-05 08:00, Discharge 2025-01-10, Inpatient |
| Location | Medical Ward (1060-3) |
| Condition | Diabetes mellitus type 2 (44054006) |
| MedicationAdministration | Regular insulin 10 units, 2025-01-06 08:00 |
| Observation | Glucose 35 mg/dL, 2025-01-06 14:00 |

**Expected Outcome**:
- Initial Population: **1** (qualifying inpatient encounter)
- Hypoglycemia Event: **Positive** (glucose 35 < 40, medication within 24h)

---

## Test Case 2: SevereHypoWithOralAgent

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaSevereHypoWithOralAgent.json`

**Scenario**: Patient on oral sulfonylurea (glipizide) develops severe hypoglycemia.

**Purpose**: Validates detection with oral antidiabetic medications.

| Resource | Details |
|----------|---------|
| Patient | Mary Oral, DOB 1958-07-22, Female |
| Encounter | Admit 2025-01-08 10:00, Discharge 2025-01-14, Inpatient |
| Location | Medical Ward (1060-3) |
| Condition | Diabetes mellitus type 2 (44054006) |
| MedicationAdministration | Glipizide 10 MG, 2025-01-09 08:00 |
| Observation | Glucose 38 mg/dL, 2025-01-09 16:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive** (glucose 38 < 40, oral agent within 24h)

---

## Test Case 3: SevereHypoDay1

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaSevereHypoDay1.json`

**Scenario**: Patient develops severe hypoglycemia on admission day (day 1).

**Purpose**: Validates detection of day 1 hypoglycemia events.

| Resource | Details |
|----------|---------|
| Patient | Early Event, DOB 1972-11-30, Male |
| Encounter | Admit 2025-01-10 14:00, Discharge 2025-01-15, Inpatient |
| Location | Trauma Critical Care (1025-6) |
| Condition | Diabetes mellitus type 2 (44054006) |
| MedicationAdministration | NPH Insulin 20 units, 2025-01-10 16:00 |
| Observation | Glucose 32 mg/dL, 2025-01-10 22:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive** (severe hypo on admission day)

---

## Test Case 4: MultipleHypoEvents

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaMultipleHypoEvents.json`

**Scenario**: Patient has two separate severe hypoglycemia events during stay.

**Purpose**: Validates counting of multiple events per encounter.

| Resource | Details |
|----------|---------|
| Patient | Multiple Events, DOB 1960-05-18, Female |
| Encounter | Admit 2025-01-03 08:00, Discharge 2025-01-12, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Insulin glargine, 2025-01-03 20:00 |
| Observation #1 | Glucose 36 mg/dL, 2025-01-04 06:00 |
| Observation #2 | Glucose 28 mg/dL, 2025-01-07 05:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Events: **2** (both < 40 mg/dL)

---

## Test Case 5: ModerateHypoExcluded

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaModerateHypoExcluded.json`

**Scenario**: Patient has moderate hypoglycemia (45 mg/dL), above severe threshold.

**Purpose**: Validates exclusion of glucose values >= 40 mg/dL.

| Resource | Details |
|----------|---------|
| Patient | Moderate Hypo, DOB 1968-09-25, Male |
| Encounter | Admit 2025-01-06 09:00, Discharge 2025-01-11, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Regular insulin, 2025-01-07 08:00 |
| Observation | Glucose 45 mg/dL, 2025-01-07 14:00 |

**Expected Outcome**:
- Initial Population: **1** (qualifying encounter)
- Hypoglycemia Event: **Excluded** (45 >= 40, not severe)

---

## Test Case 6: HypoWithoutMedication

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaHypoWithoutMedication.json`

**Scenario**: Severe hypoglycemia without antidiabetic medication (spontaneous).

**Purpose**: Validates detection of non-medication-associated hypoglycemia.

| Resource | Details |
|----------|---------|
| Patient | No Meds, DOB 1945-12-01, Female |
| Encounter | Admit 2025-01-12 11:00, Discharge 2025-01-17, Inpatient |
| Location | Medical Ward (1060-3) |
| Condition | Sepsis (91302008) |
| Observation | Glucose 35 mg/dL, 2025-01-13 04:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive** (severe hypo, non-medication cause)
- Medication Association: **No**

---

## Test Case 7: PreAdmissionHypo

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaPreAdmissionHypo.json`

**Scenario**: Glucose drawn before encounter start time (ED glucose before admission).

**Purpose**: Validates exclusion of pre-admission events.

| Resource | Details |
|----------|---------|
| Patient | Pre Admission, DOB 1970-04-10, Male |
| Encounter | Admit 2025-01-15 14:00, Discharge 2025-01-20, Inpatient |
| Location | Medical Ward (1060-3) |
| Observation | Glucose 32 mg/dL, 2025-01-15 12:00 (before admit) |

**Expected Outcome**:
- Initial Population: **1** (qualifying encounter)
- Hypoglycemia Event: **Excluded** (glucose before encounter start)

---

## Test Case 8: OutpatientEncounter

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaOutpatientEncounter.json`

**Scenario**: ED encounter only (not admitted), has severe hypoglycemia.

**Purpose**: Documents CQL behavior for ED-only encounters.

| Resource | Details |
|----------|---------|
| Patient | ED Only, DOB 1975-08-20, Female |
| Encounter | ED visit 2025-01-18 16:00 to 2025-01-18 22:00, class=EMER |
| Location | Emergency Department (1108-0) |
| Observation | Glucose 30 mg/dL, 2025-01-18 17:00 |

**Expected Outcome**:
- Initial Population: **1** (included due to CQL logic - see note below)
- Hypoglycemia Event: **Positive** (glucose 30 < 40)

**CQL Note**: The current CQL definition "Encounters with Patient Hospital Locations" includes encounters where the location type is in "Inpatient, Emergency, and Observation Locations" value set. Since Emergency Department (1108-0) is in this value set, ED-only encounters are included in the initial population even though the encounter class is EMER (not inpatient). This may be a flaw in the CQL logic - clinically, an ED-only visit without admission is not "hospital-acquired" hypoglycemia. However, this test case documents the CQL behavior as implemented.

---

## Test Case 9: GlucoseAtThreshold

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaGlucoseAtThreshold.json`

**Scenario**: Glucose exactly at 40 mg/dL (boundary condition).

**Purpose**: Validates handling of threshold boundary (< 40 vs <= 40).

| Resource | Details |
|----------|---------|
| Patient | At Threshold, DOB 1962-02-28, Male |
| Encounter | Admit 2025-01-20 08:00, Discharge 2025-01-25, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Regular insulin, 2025-01-21 06:00 |
| Observation | Glucose 40 mg/dL, 2025-01-21 12:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Excluded** (40 is NOT < 40, at boundary)

---

## Test Case 10: ICUHypoglycemia

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaICUHypoglycemia.json`

**Scenario**: ICU patient with insulin drip develops severe hypoglycemia.

**Purpose**: Validates detection in ICU setting with continuous insulin.

| Resource | Details |
|----------|---------|
| Patient | ICU Patient, DOB 1955-06-15, Male |
| Encounter | Admit 2025-01-22 02:00, Discharge 2025-01-28, Inpatient |
| Location | Medical Critical Care (1027-2) |
| Condition | Diabetic ketoacidosis (420422005) |
| MedicationAdministration | Insulin IV infusion, 2025-01-22 04:00 |
| Observation | Glucose 25 mg/dL, 2025-01-22 10:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive** (severe hypo in ICU)
- Medication Association: **Yes** (insulin within 24h)

---

## Test Case 11: HypoWithResolution

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaHypoWithResolution.json`

**Scenario**: Severe hypoglycemia followed by resolution glucose ≥70 mg/dL.

**Purpose**: Validates Metric 4 (Severe Hypoglycemia Resolution) - measures time from severe hypo to resolution.

| Resource | Details |
|----------|---------|
| Patient | Resolution Test, DOB 1963-04-20, Female |
| Encounter | Admit 2025-01-07 08:00, Discharge 2025-01-12, Inpatient |
| Location | Medical Ward (1060-3) |
| Condition | Diabetes mellitus type 2 (44054006) |
| MedicationAdministration | Regular insulin, 2025-01-08 06:00 |
| Observation #1 | Glucose 32 mg/dL, 2025-01-08 10:00 (severe hypo) |
| Observation #2 | Glucose 85 mg/dL, 2025-01-08 12:00 (resolution) |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive**
- Resolution Time: **2 hours** (from 10:00 to 12:00)

---

## Test Case 12: DenominatorOnlyNoHypo

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaDenominatorOnlyNoHypo.json`

**Scenario**: Patient receives antidiabetic drug but has NO hypoglycemia event.

**Purpose**: Validates Metric 1/2 denominator - encounters/days with ADD administered (without numerator event).

| Resource | Details |
|----------|---------|
| Patient | Denominator Only, DOB 1958-11-12, Male |
| Encounter | Admit 2025-01-09 10:00, Discharge 2025-01-14, Inpatient |
| Location | Medical Ward (1060-3) |
| Condition | Diabetes mellitus type 2 (44054006) |
| MedicationAdministration | Insulin glargine, 2025-01-10 08:00 |
| Observation | Glucose 120 mg/dL, 2025-01-10 14:00 (normal) |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **None** (glucose 120 > 40)
- Denominator Inclusion: **Yes** (ADD administered)

---

## Test Case 13: EDAddWithin1Hour

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaEDAddWithin1Hour.json`

**Scenario**: Insulin administered in ED within 1 hour before inpatient admission.

**Purpose**: Validates Footnote** - ADD in ED ending within 1 hour of admission counts for association.

| Resource | Details |
|----------|---------|
| Patient | ED Insulin, DOB 1966-08-05, Female |
| Encounter | Admit 2025-01-11 14:00, Discharge 2025-01-16, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Regular insulin, 2025-01-11 13:30 (30 min before admit) |
| Observation | Glucose 34 mg/dL, 2025-01-11 16:00 |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Positive**
- Medication Association: **Yes** (ED insulin within 1 hour of admission)

---

## Test Case 14: RepeatBGExclusion

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaRepeatBGExclusion.json`

**Scenario**: Initial severe hypoglycemia followed by repeat BG >80 mg/dL within 5 minutes.

**Purpose**: Validates Footnote* - excludes event if repeat BG >80 within 5 min (likely erroneous reading).

| Resource | Details |
|----------|---------|
| Patient | Repeat Test, DOB 1971-02-14, Male |
| Encounter | Admit 2025-01-13 08:00, Discharge 2025-01-18, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Regular insulin, 2025-01-14 06:00 |
| Observation #1 | Glucose 35 mg/dL, 2025-01-14 10:00:00 (initial low) |
| Observation #2 | Glucose 95 mg/dL, 2025-01-14 10:04:00 (repeat within 5 min) |

**Expected Outcome**:
- Initial Population: **1**
- Hypoglycemia Event: **Excluded** (repeat BG >80 within 5 minutes)
- Note: Suggests initial reading was erroneous (POC glucometer error)

---

## Test Case 15: ModerateHypoMetric2

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaModerateHypoMetric2.json`

**Scenario**: Moderate hypoglycemia (40-53 mg/dL range) for Metric 2 supplemental reporting.

**Purpose**: Validates Footnote*** - moderate hypoglycemia (40-53 mg/dL) is reported separately.

| Resource | Details |
|----------|---------|
| Patient | Moderate Range, DOB 1959-06-30, Female |
| Encounter | Admit 2025-01-15 09:00, Discharge 2025-01-20, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | Glipizide 10 MG, 2025-01-16 08:00 |
| Observation | Glucose 47 mg/dL, 2025-01-16 14:00 |

**Expected Outcome**:
- Initial Population: **1**
- Severe Hypoglycemia: **No** (47 >= 40)
- Moderate Hypoglycemia: **Yes** (47 in 40-53 range)

---

## Test Case 16: MildHypoMetric2

**File**: `NHSNACHMonthly1-v0.0.000-HypoglycemiaMildHypoMetric2.json`

**Scenario**: Mild hypoglycemia (54-70 mg/dL range) for Metric 2 supplemental reporting.

**Purpose**: Validates Footnote*** - mild hypoglycemia (54-70 mg/dL) is reported separately.

| Resource | Details |
|----------|---------|
| Patient | Mild Range, DOB 1952-09-18, Male |
| Encounter | Admit 2025-01-17 10:00, Discharge 2025-01-22, Inpatient |
| Location | Medical Ward (1060-3) |
| MedicationAdministration | NPH Insulin, 2025-01-18 07:00 |
| Observation | Glucose 62 mg/dL, 2025-01-18 12:00 |

**Expected Outcome**:
- Initial Population: **1**
- Severe Hypoglycemia: **No** (62 >= 40)
- Mild Hypoglycemia: **Yes** (62 in 54-70 range)
