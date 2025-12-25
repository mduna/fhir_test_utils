# Sepsis Test Cases Specification

## Overview

This document specifies test cases for the Adult Sepsis Event (ASE) protocol, supporting NHSN ASE Surveillance Metrics.

**Measurement Period**: January 1, 2025 to January 31, 2025
**CQL Module**: `NHSNACHMonthly1`

---

## ASE Surveillance Metrics Coverage

| Metric | Description | Positive Test | Negative Test |
|--------|-------------|---------------|---------------|
| Community-Onset Sepsis (SCO) | Onset on sepsis day 1-3 | 1, 2, 3, 4 | 5 |
| Hospital-Onset Sepsis (SHO) | Onset on sepsis day 4+ | 5, 6 | 1 |
| Cardiovascular Dysfunction | Hypotension or vasopressor | 7, 8 | - |
| Respiratory Dysfunction | Ventilation (invasive, NIV, HFNC) | 9, 10 | - |
| Metabolic Dysfunction | Lactate >2.0 mmol/L | 1, 11 | - |
| Renal Dysfunction | Creatinine 2x increase | 12 | 13 |
| Hepatic Dysfunction | Bilirubin 2x increase | 14 | 15 |
| Coagulation Dysfunction | Platelets 50% decrease | 16 | 17 |
| QAD Exception - Death | <4 QADs with death | 18 | - |
| Repeat Event Timeframe | No new event within 7 days | - | 19 |

---

## Test Case 1: SCO Positive - Basic Metabolic Dysfunction (Lactate)

**File**: `SCOPositiveBasicLactate.json`

**Scenario**: Community-onset sepsis with blood culture on day 2, 4 QADs, and elevated lactate

**Purpose**: Validates basic SCO event detection with metabolic organ dysfunction

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1965-03-15 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Lactate) | 2025-01-03T09:00 (Day 2), Value: 3.5 mmol/L |
| MedicationAdmin 1 | Piperacillin/Tazobactam IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (onset day 2, blood culture + 4 QAD + lactate >2.0)
- Onset Date: 2025-01-03 (day 2)

---

## Test Case 2: SCO Positive - Multiple Organ Dysfunction

**File**: `SCOPositiveMultipleOrganDysfunction.json`

**Scenario**: Community-onset sepsis with cardiovascular (hypotension) AND renal dysfunction

**Purpose**: Validates SCO detection with multiple organ dysfunction criteria

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1970-08-22 |
| Encounter | Admit 2025-01-03T10:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture | Collected 2025-01-04T08:00 (Day 2) |
| Observation (Blood Pressure) 1 | 2025-01-04T08:30, SBP: 85 mmHg, DBP: 55 mmHg |
| Observation (Blood Pressure) 2 | 2025-01-04T10:00, SBP: 82 mmHg, DBP: 52 mmHg |
| Observation (Creatinine baseline) | 2025-01-03T12:00, Value: 0.9 mg/dL |
| Observation (Creatinine elevated) | 2025-01-04T10:00, Value: 2.2 mg/dL (>2x) |
| MedicationAdmin | Vancomycin IV, 2025-01-04 to 2025-01-07 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (onset day 2)
- Cardiovascular Dysfunction: **Yes** (2 SBP readings <90 within 3h)
- Renal Dysfunction: **Yes** (creatinine 2.4x increase to >1.02)

---

## Test Case 3: SCO Positive - Day 3 Onset (Boundary)

**File**: `SCOPositiveDay3Boundary.json`

**Scenario**: Sepsis with onset exactly on day 3 (last day for SCO)

**Purpose**: Validates SCO boundary condition at day 3

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1958-11-30 |
| Encounter | Admit 2025-01-02T06:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1028-0 (Medical Cardiac Critical Care) |
| Blood Culture | Collected 2025-01-04T14:00 (Day 3) |
| Observation (Lactate) | 2025-01-04T13:00 (Day 3), Value: 2.8 mmol/L |
| MedicationAdmin | Ceftriaxone IV, 2025-01-04 to 2025-01-07 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (onset day 3 - within SCO window)
- Onset Date: 2025-01-04 (day 3)

---

## Test Case 4: SCO Positive - Principal Diagnosis Infection (No Blood Culture)

**File**: `SCOPositivePrincipalDxInfection.json`

**Scenario**: Community-onset sepsis meeting criteria via principal diagnosis (infection) instead of blood culture

**Purpose**: Validates SCO detection with principal diagnosis alternative pathway

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1975-04-18 |
| Encounter | Admit 2025-01-03T14:00 (Day 1), Discharge 2025-01-09 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Condition (Principal Dx) | Sepsis (A41.9) - Present on Admission |
| Observation (Lactate) | 2025-01-03T16:00 (Day 1), Value: 4.2 mmol/L |
| MedicationAdmin | Levofloxacin IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (principal dx infection + 4 QAD + organ dysfunction)
- Onset Date: 2025-01-03 (day 1)

---

## Test Case 5: SHO Positive - Day 5 Onset

**File**: `SHOPositiveDay5Onset.json`

**Scenario**: Hospital-onset sepsis with blood culture and organ dysfunction on day 5

**Purpose**: Validates SHO event detection (onset on day 4+)

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1962-07-25 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-14 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-06T10:00 (Day 5) |
| Observation (Lactate) | 2025-01-06T09:30 (Day 5), Value: 3.1 mmol/L |
| MedicationAdmin | Meropenem IV, 2025-01-06 to 2025-01-09 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SHO Event: **Positive** (onset day 5)
- SCO Event: **Excluded** (onset not on day 1-3)

---

## Test Case 6: SHO Positive - Escalating Cardiovascular Dysfunction

**File**: `SHOPositiveEscalatingCardiovascular.json`

**Scenario**: Hospital-onset sepsis with escalating cardiovascular dysfunction (hypotension to vasopressor)

**Purpose**: Validates SHO with escalating organ dysfunction requirement

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1968-02-14 |
| Encounter | Admit 2025-01-02T10:00 (Day 1), Discharge 2025-01-15 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture | Collected 2025-01-06T08:00 (Day 5) |
| Observation (Blood Pressure) 1 | 2025-01-05T20:00 (Day 4), SBP: 88 mmHg, DBP: 58 mmHg |
| Observation (Blood Pressure) 2 | 2025-01-05T22:00 (Day 4), SBP: 84 mmHg, DBP: 54 mmHg |
| MedicationAdmin (Vasopressor) | Norepinephrine IV, 2025-01-06T00:00 (Day 5) - Escalation |
| MedicationAdmin (Antibiotic) | Vancomycin IV, 2025-01-05 to 2025-01-08 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SHO Event: **Positive** (onset day 4, escalation day 5)
- Cardiovascular Dysfunction: **Yes** (hypotension -> vasopressor escalation)

---

## Test Case 7: Cardiovascular Dysfunction - Hypotension Only

**File**: `CardiovascularHypotension.json`

**Scenario**: Sepsis with hypotension meeting cardiovascular criteria (>=2 readings SBP<90 within 3h)

**Purpose**: Validates cardiovascular dysfunction via hypotension pathway

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1972-09-08 |
| Encounter | Admit 2025-01-03T08:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-04T10:00 (Day 2) |
| Observation (Blood Pressure) 1 | 2025-01-04T10:30, SBP: 78 mmHg, DBP: 48 mmHg |
| Observation (Blood Pressure) 2 | 2025-01-04T12:00, SBP: 82 mmHg, DBP: 52 mmHg |
| Observation (Blood Pressure) 3 | 2025-01-04T13:00, SBP: 85 mmHg, DBP: 55 mmHg |
| MedicationAdmin | Piperacillin/Tazobactam IV, 2025-01-04 to 2025-01-07 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Cardiovascular Dysfunction: **Yes** (3 SBP readings <90 within 3h)

---

## Test Case 8: Cardiovascular Dysfunction - Vasopressor Initiation

**File**: `CardiovascularVasopressor.json`

**Scenario**: Sepsis with new vasopressor initiation meeting cardiovascular criteria

**Purpose**: Validates cardiovascular dysfunction via vasopressor pathway

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1960-12-03 |
| Encounter | Admit 2025-01-02T14:00 (Day 1), Discharge 2025-01-13 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| MedicationAdmin (Vasopressor) | Norepinephrine IV, started 2025-01-03T11:00 (Day 2) |
| MedicationAdmin (Antibiotic) | Ceftriaxone IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Cardiovascular Dysfunction: **Yes** (new vasopressor within +/-1 day of blood culture)

---

## Test Case 9: Respiratory Dysfunction - Invasive Ventilation

**File**: `RespiratoryInvasiveVent.json`

**Scenario**: Sepsis with invasive mechanical ventilation

**Purpose**: Validates respiratory dysfunction via invasive ventilation (any duration)

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1955-05-20 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-14 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-03T08:00 (Day 2) |
| Procedure (Invasive Vent) | 2025-01-03T06:00 to 2025-01-07T12:00 |
| MedicationAdmin | Meropenem IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Respiratory Dysfunction: **Yes** (invasive ventilation - any duration)

---

## Test Case 10: Respiratory Dysfunction - NIV/HFNC 2+ Days

**File**: `RespiratoryNIVHFNC.json`

**Scenario**: Sepsis with non-invasive ventilation for 2+ calendar days

**Purpose**: Validates respiratory dysfunction via NIV/HFNC (requires 2+ days)

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1978-01-15 |
| Encounter | Admit 2025-01-03T10:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1028-0 (Medical Cardiac Critical Care) |
| Blood Culture | Collected 2025-01-04T08:00 (Day 2) |
| Procedure (NIV) | 2025-01-04T10:00 to 2025-01-06T10:00 (2 calendar days) |
| MedicationAdmin | Vancomycin IV, 2025-01-04 to 2025-01-07 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Respiratory Dysfunction: **Yes** (NIV for 2+ calendar days)

---

## Test Case 11: Metabolic Dysfunction - Lactate Elevated

**File**: `MetabolicLactateElevated.json`

**Scenario**: Sepsis with lactate >2.0 mmol/L

**Purpose**: Validates metabolic dysfunction via lactate threshold

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1966-08-12 |
| Encounter | Admit 2025-01-02T12:00 (Day 1), Discharge 2025-01-10 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Blood Culture | Collected 2025-01-03T14:00 (Day 2) |
| Observation (Lactate) | 2025-01-03T13:30, Value: 2.5 mmol/L (>2.0 threshold) |
| MedicationAdmin | Levofloxacin IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Metabolic Dysfunction: **Yes** (lactate 2.5 > 2.0 threshold)

---

## Test Case 12: Renal Dysfunction - Creatinine 2x Increase

**File**: `RenalCreatinine2xIncrease.json`

**Scenario**: Sepsis with creatinine doubling from baseline

**Purpose**: Validates renal dysfunction criteria (2x increase to threshold)

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1973-06-28 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Creatinine baseline) | 2025-01-02T10:00 (Day 1), Value: 0.8 mg/dL |
| Observation (Creatinine elevated) | 2025-01-03T09:00 (Day 2), Value: 1.8 mg/dL (2.25x) |
| MedicationAdmin | Ceftriaxone IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Renal Dysfunction: **Yes** (2.25x increase to 1.8, >1.02 threshold for female)

---

## Test Case 13: Renal Dysfunction Excluded - ESRD Diagnosis

**File**: `RenalExcludedESRD.json`

**Scenario**: Patient with ESRD - renal dysfunction criteria should not apply

**Purpose**: Validates ESRD exclusion from renal dysfunction

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1958-03-10 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Condition | End-stage renal disease (N18.6) - Present on Admission |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Creatinine baseline) | 2025-01-02T10:00, Value: 4.0 mg/dL |
| Observation (Creatinine elevated) | 2025-01-03T10:00, Value: 8.5 mg/dL (2.1x) |
| Observation (Lactate) | 2025-01-03T09:00, Value: 3.0 mmol/L |
| MedicationAdmin | Vancomycin IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (via lactate, NOT renal)
- Renal Dysfunction: **Excluded** (ESRD diagnosis present)
- Metabolic Dysfunction: **Yes** (lactate qualifies)

---

## Test Case 14: Hepatic Dysfunction - Bilirubin 2x Increase

**File**: `HepaticBilirubin2xIncrease.json`

**Scenario**: Sepsis with bilirubin doubling to >=2.0 mg/dL

**Purpose**: Validates hepatic dysfunction criteria

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1970-04-22 |
| Encounter | Admit 2025-01-02T10:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture | Collected 2025-01-03T08:00 (Day 2) |
| Observation (Bilirubin baseline) | 2025-01-02T12:00 (Day 1), Value: 1.0 mg/dL |
| Observation (Bilirubin elevated) | 2025-01-03T07:00 (Day 2), Value: 2.5 mg/dL (2.5x) |
| MedicationAdmin | Piperacillin/Tazobactam IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Hepatic Dysfunction: **Yes** (2.5x increase to 2.5, >=2.0 threshold)

---

## Test Case 15: Hepatic Dysfunction Excluded - Liver Disease

**File**: `HepaticExcludedLiverDisease.json`

**Scenario**: Patient with moderate/severe liver disease - hepatic criteria excluded

**Purpose**: Validates liver disease exclusion from hepatic dysfunction

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1965-09-14 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Condition | Cirrhosis of liver (K74.60) - Present on Admission |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Bilirubin baseline) | 2025-01-02T10:00, Value: 2.0 mg/dL |
| Observation (Bilirubin elevated) | 2025-01-03T09:00, Value: 5.0 mg/dL (2.5x) |
| Observation (Lactate) | 2025-01-03T09:30, Value: 2.8 mmol/L |
| MedicationAdmin | Ceftriaxone IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (via lactate, NOT hepatic)
- Hepatic Dysfunction: **Excluded** (liver disease diagnosis)
- Metabolic Dysfunction: **Yes** (lactate qualifies)

---

## Test Case 16: Coagulation Dysfunction - Platelets 50% Decrease

**File**: `CoagulationPlatelet50Decrease.json`

**Scenario**: Sepsis with platelets dropping 50% to <100

**Purpose**: Validates coagulation dysfunction criteria

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1963-11-05 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Platelets baseline) | 2025-01-02T10:00 (Day 1), Value: 180 x10^9/L |
| Observation (Platelets decreased) | 2025-01-03T09:00 (Day 2), Value: 75 x10^9/L (58% decrease) |
| MedicationAdmin | Meropenem IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive**
- Coagulation Dysfunction: **Yes** (58% decrease to 75, <100 threshold)

---

## Test Case 17: Coagulation Dysfunction Excluded - Malignancy

**File**: `CoagulationExcludedMalignancy.json`

**Scenario**: Patient with hematologic malignancy - coagulation criteria excluded

**Purpose**: Validates malignancy exclusion from coagulation dysfunction

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1960-02-28 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Condition | Acute lymphoblastic leukemia (C91.00) - Present on Admission |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Platelets baseline) | 2025-01-02T10:00, Value: 120 x10^9/L |
| Observation (Platelets decreased) | 2025-01-03T09:00, Value: 45 x10^9/L (62% decrease) |
| Observation (Lactate) | 2025-01-03T09:30, Value: 3.2 mmol/L |
| MedicationAdmin | Vancomycin IV, 2025-01-03 to 2025-01-06 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (via lactate, NOT coagulation)
- Coagulation Dysfunction: **Excluded** (hematologic malignancy)
- Metabolic Dysfunction: **Yes** (lactate qualifies)

---

## Test Case 18: QAD Exception - Death Before 4 QADs

**File**: `QADExceptionDeathBefore4.json`

**Scenario**: Patient dies after only 2 QADs - qualifies due to death exception

**Purpose**: Validates QAD exception rule for patient death

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1950-07-18 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-04T23:59 (Death) |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Blood Culture | Collected 2025-01-03T08:00 (Day 2) |
| Observation (Lactate) | 2025-01-03T07:30, Value: 6.5 mmol/L (severe) |
| MedicationAdmin | Piperacillin/Tazobactam IV, 2025-01-03 to 2025-01-04 (2 QADs) |
| Encounter Discharge | Died - 2025-01-04T23:59 |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (2 QADs sufficient - death exception)
- Death: Yes (qualifies for SMR numerator)

---

## Test Case 19: Repeat Event Timeframe - Second Event Excluded

**File**: `RepeatEventTimeframeExcluded.json`

**Scenario**: Second potential ASE within 7-day RET of first event

**Purpose**: Validates Repeat Event Timeframe exclusion rule

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1968-05-10 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-16 |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Blood Culture 1 | Collected 2025-01-03T10:00 (Day 2) - First event |
| Observation (Lactate) 1 | 2025-01-03T09:00, Value: 3.0 mmol/L |
| MedicationAdmin 1 | Vancomycin IV, 2025-01-03 to 2025-01-06 (4 QADs) |
| Blood Culture 2 | Collected 2025-01-08T10:00 (Day 7) - Within RET |
| Observation (Lactate) 2 | 2025-01-08T09:00, Value: 2.8 mmol/L |
| MedicationAdmin 2 | Ceftriaxone IV, 2025-01-08 to 2025-01-11 (4 QADs) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event 1: **Positive** (onset day 2, RET days 2-8)
- SCO Event 2: **Excluded** (within 7-day RET of first event)

---

## Test Case 20: QAD With 1-Day Gap - Qualifies

**File**: `QADWith1DayGap.json`

**Scenario**: Antibiotic administration with 1-day gap still counts as consecutive

**Purpose**: Validates QAD gap tolerance rule

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1975-10-22 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Blood Culture | Collected 2025-01-03T10:00 (Day 2) |
| Observation (Lactate) | 2025-01-03T09:30, Value: 2.3 mmol/L |
| MedicationAdmin | Levofloxacin IV: 2025-01-03, 2025-01-05, 2025-01-07, 2025-01-09 (every other day) |

**Expected Outcome**:
- Initial Population: 1
- SCO Event: **Positive** (1-day gaps tolerated - 4 QADs met)

---

## FHIR Resources by Test Case

| Test Case | Patient | Encounter | Location | Blood Culture | Observation (Lab) | Observation (BP) | MedicationAdmin | Procedure | Condition |
|-----------|:-------:|:---------:|:--------:|:-------------:|:-----------------:|:----------------:|:---------------:|:---------:|:---------:|
| 1 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 1 | - | - |
| 2 | Yes | Yes | Yes | 1 | 2 (Cr) | 2 | 1 | - | - |
| 3 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 1 | - | - |
| 4 | Yes | Yes | Yes | - | 1 (Lactate) | - | 1 | - | 1 (Dx) |
| 5 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 1 | - | - |
| 6 | Yes | Yes | Yes | 1 | - | 2 | 2 | - | - |
| 7 | Yes | Yes | Yes | 1 | - | 3 | 1 | - | - |
| 8 | Yes | Yes | Yes | 1 | - | - | 2 | - | - |
| 9 | Yes | Yes | Yes | 1 | - | - | 1 | 1 (Vent) | - |
| 10 | Yes | Yes | Yes | 1 | - | - | 1 | 1 (NIV) | - |
| 11 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 1 | - | - |
| 12 | Yes | Yes | Yes | 1 | 2 (Cr) | - | 1 | - | - |
| 13 | Yes | Yes | Yes | 1 | 3 (Cr, Lactate) | - | 1 | - | 1 (ESRD) |
| 14 | Yes | Yes | Yes | 1 | 2 (Bili) | - | 1 | - | - |
| 15 | Yes | Yes | Yes | 1 | 3 (Bili, Lactate) | - | 1 | - | 1 (Liver) |
| 16 | Yes | Yes | Yes | 1 | 2 (Plt) | - | 1 | - | - |
| 17 | Yes | Yes | Yes | 1 | 3 (Plt, Lactate) | - | 1 | - | 1 (ALL) |
| 18 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 1 | - | - |
| 19 | Yes | Yes | Yes | 2 | 2 (Lactate) | - | 2 | - | - |
| 20 | Yes | Yes | Yes | 1 | 1 (Lactate) | - | 4 | - | - |

---

## Code Reference

### Laboratory Tests (LOINC)

| Test | LOINC Code | Display | Unit |
|------|------------|---------|------|
| Blood Culture | 600-7 | Bacteria identified in Blood by Culture | - |
| Creatinine | 2160-0 | Creatinine [Mass/volume] in Serum or Plasma | mg/dL |
| Bilirubin Total | 1975-2 | Bilirubin.total [Mass/volume] in Serum or Plasma | mg/dL |
| Platelets | 777-3 | Platelets [#/volume] in Blood | 10^9/L |
| Lactate | 2524-7 | Lactate [Moles/volume] in Serum or Plasma | mmol/L |

### Vital Signs (LOINC)

| Vital | LOINC Code | Display | Unit |
|-------|------------|---------|------|
| Blood Pressure Panel | 85354-9 | Blood pressure panel with all children optional | - |
| Systolic BP (component) | 8480-6 | Systolic blood pressure | mm[Hg] |
| Diastolic BP (component) | 8462-4 | Diastolic blood pressure | mm[Hg] |
| Mean Arterial Pressure | 8478-0 | Mean blood pressure | mm[Hg] |

**Note**: Blood Pressure observations use US Core Blood Pressure Profile with panel code 85354-9 and systolic/diastolic as components. UCUM code for unit is `mm[Hg]`.

### Antimicrobials (RxNorm)

| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Piperacillin/Tazobactam 4.5 GM | 1659149 | Piperacillin 4000 MG / tazobactam 500 MG Injection |
| Vancomycin 1000 MG | 1664986 | Vancomycin 1000 MG Injection |
| Ceftriaxone 1 GM | 309090 | Ceftriaxone 1000 MG Injection |
| Meropenem 1 GM | 1722939 | Meropenem 1000 MG Injection |
| Levofloxacin 500 MG IV | 311365 | Levofloxacin 500 MG/100 ML Injectable Solution |

### Vasopressors (RxNorm)

| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Norepinephrine 4 MG/4 ML | 1659027 | Norepinephrine Bitartrate 4 MG/4 ML Injectable Solution |
| Epinephrine 1 MG/ML | 1991339 | Epinephrine 1 MG/ML Injectable Solution |
| Vasopressin 20 Units/ML | 1596994 | Vasopressin 20 UNT/ML Injectable Solution |

### Ventilation Procedures (SNOMED)

| Procedure | SNOMED Code | Display |
|-----------|-------------|---------|
| Invasive mechanical ventilation | 40617009 | Artificial respiration |
| Non-invasive ventilation | 428311008 | Non-invasive ventilation |
| High flow nasal cannula | 371907003 | Oxygen administration by nasal cannula |

### Exclusion Diagnoses (ICD-10)

| Condition | ICD-10 Code | Display |
|-----------|-------------|---------|
| End-stage renal disease | N18.6 | End stage renal disease |
| Cirrhosis of liver | K74.60 | Unspecified cirrhosis of liver |
| Acute lymphoblastic leukemia | C91.00 | Acute lymphoblastic leukemia not having achieved remission |
| Sepsis unspecified | A41.9 | Sepsis, unspecified organism |

---

## Sepsis Day Calculation Reference

| Admission Date | Day 1 | Day 2 | Day 3 (SCO boundary) | Day 4+ (SHO) |
|----------------|-------|-------|----------------------|--------------|
| 2025-01-02 | Jan 2 | Jan 3 | Jan 4 | **Jan 5+** |
| 2025-01-03 | Jan 3 | Jan 4 | Jan 5 | **Jan 6+** |
