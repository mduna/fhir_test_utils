# HOB Test Cases Specification

## Overview

This document specifies all test cases for the HOB (Hospital-Onset Bacteremia & Fungemia) protocol, supporting the NHSN HOB Surveillance Metrics.

**Measurement Period**: January 1, 2025 to January 31, 2025
**CQL Module**: `NHSNAcuteCareHospitalMonthlyInitialPopulation1`
**HOB Definition**: Blood culture positive on hospital day 4+ (admission = day 1)

---

## NHSN HOB Surveillance Metrics Coverage

| Metric | Description | Positive Test | Negative Test |
|--------|-------------|---------------|---------------|
| HOB Event | Pathogenic bacteria/fungi on day 4+ | 1, 2, 4, 9, 10 | 3, 11 |
| Blood Culture Contamination | 1 of 2 sets positive for skin commensal | 5 | 6 |
| Matching Commensal HOB | Skin commensal + ≥4 days antibiotics | 7 | 8 |
| Non-Measure HOB | HOB in patient with non-preventability conditions | 9 | 10 |
| Species Code Matching | Same species with different SNOMED codes (base vs. phenotype) | - | 11 |

---

## Test Case 1: HOB Positive - Day 4 S. aureus

**File**: `HOBPositiveDay4SAureus.json`

**Scenario**: Basic HOB positive event with pathogenic organism on hospital day 4

**Purpose**: Validates primary HOB Event metric - blood culture positive on day 4+

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1970-01-15 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Specimen | Blood, collected 2025-01-05T10:00 (Day 4) |
| Observation | LOINC 600-7, S. aureus (3092008), Positive |

**Expected Outcome**:
- Initial Population: 1
- HOB Event: **Positive** (pathogenic organism on day 4)

---

## Test Case 2: HOB Positive - Day 5 Candida (Fungemia)

**File**: `HOBPositiveDay5Candida.json`

**Scenario**: HOB positive event with fungal organism (fungemia)

**Purpose**: Validates HOB Event metric includes fungemia

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1965-06-20 |
| Encounter | Admit 2025-01-03T14:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Specimen | Blood, collected 2025-01-07T09:00 (Day 5) |
| Observation | LOINC 600-7, Candida albicans (53326005), Positive |

**Expected Outcome**:
- Initial Population: 1
- HOB Event: **Positive** (fungemia qualifies as HOB)

---

## Test Case 3: HOB Excluded - Matching COB Organism

**File**: `HOBExcludedMatchingCOB.json`

**Scenario**: Same organism on COB (day 2) and potential HOB (day 5) - excluded

**Purpose**: Validates HOB exclusion when organism matches prior COB event

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1980-03-10 |
| Encounter | Admit 2025-01-02T10:00 (Day 1), Discharge 2025-01-11 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Specimen 1 | Blood, collected 2025-01-03T08:00 (Day 2) |
| Observation 1 | E. coli (112283007), Positive - **COB Event** |
| Specimen 2 | Blood, collected 2025-01-06T09:00 (Day 5) |
| Observation 2 | E. coli (112283007), Positive - **Same organism** |

**Expected Outcome**:
- Initial Population: 1
- COB Event: **Positive** (day 2 culture)
- HOB Event: **Excluded** (matches prior COB organism)

---

## Test Case 4: HOB Positive - Non-Matching Prior COB

**File**: `HOBPositiveNonMatchingCOB.json`

**Scenario**: Different organisms on COB (day 2) and HOB (day 5) - HOB qualifies

**Purpose**: Validates HOB counts when organism differs from prior COB

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1975-09-25 |
| Encounter | Admit 2025-01-02T06:00 (Day 1), Discharge 2025-01-12 |
| Location | HSLOC 1025-6 (Trauma Critical Care) |
| Specimen 1 | Blood, collected 2025-01-03T07:00 (Day 2) |
| Observation 1 | E. coli (112283007), Positive - **COB Event** |
| Specimen 2 | Blood, collected 2025-01-06T10:00 (Day 5) |
| Observation 2 | S. aureus (3092008), Positive - **Different organism** |

**Expected Outcome**:
- Initial Population: 1
- COB Event: **Positive** (E. coli on day 2)
- HOB Event: **Positive** (S. aureus on day 5 - different organism)

---

## Test Case 5: Blood Culture Contamination - 1 of 2 Positive

**File**: `HOBContamination1of2Positive.json`

**Scenario**: Paired blood culture sets; only 1 set positive for skin commensal

**Purpose**: Validates Blood Culture Contamination metric numerator

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1972-11-08 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-09 |
| Location | HSLOC 1060-3 (Medical Ward) |
| Specimen (Set A) | Blood, collected 2025-01-05T10:00 (Day 4) |
| Observation (Set A) | S. epidermidis (60875001), **Positive** |
| Specimen (Set B) | Blood, collected 2025-01-05T10:05 (Day 4) |
| Observation (Set B) | No growth (264868006), **Negative** |

**Expected Outcome**:
- Initial Population: 1
- Blood Culture Contamination: **Yes** (1 of 2 sets positive for skin commensal)
- HOB Event: **Excluded** (skin commensal only, likely contamination)

---

## Test Case 6: Blood Culture - 2 of 2 Positive (NOT Contamination)

**File**: `HOBContamination2of2Positive.json`

**Scenario**: Both paired culture sets positive for same skin commensal

**Purpose**: Validates that 2/2 positive does NOT count as contamination

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1980-05-22 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10 |
| Location | HSLOC 1033-0 (Surgical Ward) |
| Specimen (Set A) | Blood, collected 2025-01-05T14:00 (Day 4) |
| Observation (Set A) | S. epidermidis (60875001), **Positive** |
| Specimen (Set B) | Blood, collected 2025-01-05T14:05 (Day 4) |
| Observation (Set B) | S. epidermidis (60875001), **Positive** |

**Expected Outcome**:
- Initial Population: 1
- Blood Culture Contamination: **No** (both sets positive = true bacteremia)
- HOB Event: **Excluded** (skin commensal, but may qualify for Matching Commensal)

---

## Test Case 7: Matching Commensal HOB - Positive

**File**: `HOBMatchingCommensalPositive.json`

**Scenario**: Skin commensal from ≥2 blood cultures AND ≥4 days antibiotic treatment

**Purpose**: Validates Matching Commensal HOB Event metric numerator

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1965-03-20 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-14 (12 days) |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen 1 | Blood, collected 2025-01-06T10:00 (Day 5) |
| Observation 1 | S. epidermidis (60875001), Positive |
| Specimen 2 | Blood, collected 2025-01-08T14:00 (Day 7) |
| Observation 2 | S. epidermidis (60875001), Positive |
| MedicationAdministration | Vancomycin (1664986), 2025-01-06 to 2025-01-10 (**4 days**) |

**Expected Outcome**:
- Initial Population: 1
- Matching Commensal HOB: **Positive** (≥2 cultures + ≥4 days antibiotics)
- Standard HOB Event: **Excluded** (skin commensal)

---

## Test Case 8: Matching Commensal HOB - Insufficient Antibiotics

**File**: `HOBMatchingCommensalInsufficientAbx.json`

**Scenario**: Skin commensal from ≥2 cultures but <4 days antibiotics

**Purpose**: Validates exclusion from Matching Commensal when treatment threshold not met

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1955-09-15 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-11 (9 days) |
| Location | HSLOC 1028-0 (Medical Cardiac Critical Care) |
| Specimen 1 | Blood, collected 2025-01-06T08:00 (Day 5) |
| Observation 1 | S. epidermidis (60875001), Positive |
| Specimen 2 | Blood, collected 2025-01-08T10:00 (Day 7) |
| Observation 2 | S. epidermidis (60875001), Positive |
| MedicationAdministration | Vancomycin (1664986), 2025-01-06 to 2025-01-08 (**2 days**) |

**Expected Outcome**:
- Initial Population: 1
- Matching Commensal HOB: **Excluded** (<4 days antibiotics)
- Standard HOB Event: **Excluded** (skin commensal)

---

## Test Case 9: Non-Measure HOB - High Risk (Non-Preventability)

**File**: `HOBNonMeasureHighRisk.json`

**Scenario**: HOB event in patient with conditions predicting non-preventability

**Purpose**: Validates Non-Measure HOB Event metric numerator

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1958-07-12 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-12 (10 days) |
| Location | HSLOC 1060-3 (Medical Ward - Oncology) |
| Condition 1 | Acute myeloid leukemia (91861009) - **Non-preventability factor** |
| Condition 2 | Neutropenia (165517008) - **Non-preventability factor** |
| Specimen | Blood, collected 2025-01-06T14:00 (Day 5) |
| Observation | E. coli (112283007), Positive |

**Expected Outcome**:
- Initial Population: 1
- HOB Event: **Positive** (pathogenic organism on day 4+)
- Non-Measure HOB: **Positive** (AML + neutropenia = high non-preventability)

---

## Test Case 10: Measurable HOB - No Risk Factors

**File**: `HOBMeasurableNoRiskFactors.json`

**Scenario**: HOB event in patient without non-preventability conditions

**Purpose**: Validates standard HOB counted, NOT Non-Measure HOB

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1968-12-03 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10 (8 days) |
| Location | HSLOC 1060-3 (Medical Ward) |
| Condition 1 | Diabetes mellitus type 2 (44054006) - **NOT a non-preventability factor** |
| Condition 2 | Hypertensive disorder (38341003) - **NOT a non-preventability factor** |
| Specimen | Blood, collected 2025-01-06T09:00 (Day 5) |
| Observation | S. aureus (3092008), Positive |

**Expected Outcome**:
- Initial Population: 1
- HOB Event: **Positive** (pathogenic organism on day 4+)
- Non-Measure HOB: **Excluded** (no non-preventability conditions)

---

## Test Case 11: HOB Excluded - Different SNOMED Codes, Same Species

**File**: `HOBExcludedSameSpeciesDifferentCodes.json`

**Scenario**: Patient with differing SNOMED codes of the same species on day 2 and day 6

**Purpose**: Validates HOB code matching correctly identifies same species across different SNOMED codes (base organism vs. resistance phenotype)

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1972-11-30 |
| Encounter | Admit 2025-01-02T08:00 (Day 1), Discharge 2025-01-10T12:00 (8 days) |
| Location 1 | HSLOC 1108-0 (Emergency Department), 08:00-12:00 |
| Location 2 | HSLOC 1162-7 (24 Hour Observation Area), 12:05-20:00 |
| Location 3 | HSLOC 1060-3 (Medical Ward), 20:05 onwards |
| Location 4 | Room 123 (physicalType: Room) |
| Location 5 | Room 1 / Bed 2 (physicalType: Bed) |
| Specimen 1 | Blood, collected 2025-01-03T18:43 (Day 2) |
| Specimen 2 | Blood, collected 2025-01-07T18:43 (Day 6) |
| Observation 1 | Pseudomonas aeruginosa (52499004), Positive |
| Observation 2 | Carbapenem resistant Pseudomonas aeruginosa (726492000), Positive |

**Expected Outcome**:
- Initial Population: 1
- HOB Event: **Negative** (matching pathogenic organisms on day 2 and 6 - same species despite different codes)
- Community-Onset Bacteremia & Fungemia Event: **Positive** (day 2 culture)

**Key Insight**: The CQL measure must recognize that SNOMED 52499004 (Pseudomonas aeruginosa) and 726492000 (Carbapenem resistant Pseudomonas aeruginosa) represent the same bacterial species. The resistance phenotype does not change organism identity for COB exclusion purposes.

---

## FHIR Resources by Test Case

| Test Case | Patient | Encounter | Location | Specimen | Observation | Condition | MedicationAdmin |
|-----------|:-------:|:---------:|:--------:|:--------:|:-----------:|:---------:|:---------------:|
| 1 | ✓ | ✓ | ✓ | 1 | 1 | - | - |
| 2 | ✓ | ✓ | ✓ | 1 | 1 | - | - |
| 3 | ✓ | ✓ | ✓ | 2 | 2 | - | - |
| 4 | ✓ | ✓ | ✓ | 2 | 2 | - | - |
| 5 | ✓ | ✓ | ✓ | 2 | 2 | - | - |
| 6 | ✓ | ✓ | ✓ | 2 | 2 | - | - |
| 7 | ✓ | ✓ | ✓ | 2 | 2 | - | 1 |
| 8 | ✓ | ✓ | ✓ | 2 | 2 | - | 1 |
| 9 | ✓ | ✓ | ✓ | 1 | 1 | 2 | - |
| 10 | ✓ | ✓ | ✓ | 1 | 1 | 2 | - |
| 11 | ✓ | ✓ | ✓ | 2 | 2 | - | - |

---

## Code Reference

### Pathogenic Organisms (HOB Eligible)

| Organism | SNOMED Code | Display |
|----------|-------------|---------|
| Staphylococcus aureus | 3092008 | Staphylococcus aureus |
| Escherichia coli | 112283007 | Escherichia coli |
| Candida albicans | 53326005 | Candida albicans |
| Pseudomonas aeruginosa | 52499004 | Pseudomonas aeruginosa |
| Carbapenem resistant Pseudomonas aeruginosa | 726492000 | Carbapenem resistant Pseudomonas aeruginosa |

### Skin Commensals (Standard HOB Excluded)

| Organism | SNOMED Code | Display |
|----------|-------------|---------|
| Staphylococcus epidermidis | 60875001 | Staphylococcus epidermidis |

### Non-Preventability Conditions

| Condition | SNOMED Code | Display |
|-----------|-------------|---------|
| Acute myeloid leukemia | 91861009 | Acute myeloid leukemia |
| Neutropenia | 165517008 | Neutropenia |

### Common Conditions (NOT Non-Preventability)

| Condition | SNOMED Code | Display |
|-----------|-------------|---------|
| Diabetes mellitus type 2 | 44054006 | Diabetes mellitus type 2 |
| Hypertensive disorder | 38341003 | Hypertensive disorder |

### Antibiotic Medications (RxNorm)

| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Vancomycin 1000 MG Injection | 1664986 | Vancomycin 1000 MG Injection |

### Blood Culture Observation

| Element | Code System | Code | Display |
|---------|-------------|------|---------|
| Observation Code | LOINC | 600-7 | Bacteria identified in Blood by Culture |
| Specimen Type | SNOMED | 119297000 | Blood specimen |
| No Growth Result | SNOMED | 264868006 | No growth |

---

## Hospital Day Calculation

| Admission Date | Day 1 | Day 2 | Day 3 | Day 4 (HOB eligible) |
|----------------|-------|-------|-------|----------------------|
| 2025-01-02 | Jan 2 | Jan 3 | Jan 4 | **Jan 5** |
| 2025-01-03 | Jan 3 | Jan 4 | Jan 5 | **Jan 6** |
