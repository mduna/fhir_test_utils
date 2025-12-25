# AUR Test Cases Specification

## Overview

This document specifies test cases for the AUR (Antimicrobial Use and Resistance) protocol, covering both AU and AR options.

**Measurement Period**: January 1, 2025 to January 31, 2025
**CQL Module**: `NHSNAcuteCareHospitalMonthlyInitialPopulation1`

---

## Part 1: Antimicrobial Use (AU) Test Cases

---

## Test Case AU-1: Basic Inpatient IV Antimicrobial

**File**: `AUBasicInpatientIV.json`

**Scenario**: Single IV antimicrobial administered during inpatient stay

**Purpose**: Validates basic antimicrobial day calculation for IV route

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1965-03-15 |
| Encounter | Admit 2025-01-05T08:00, Discharge 2025-01-08T12:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| MedicationAdministration | Meropenem 1g IV, 2025-01-05T10:00 |
| MedicationAdministration | Meropenem 1g IV, 2025-01-05T18:00 |
| MedicationAdministration | Meropenem 1g IV, 2025-01-06T02:00 |

**Expected Outcome**:
- Initial Population: 1
- Meropenem Days: **2** (Jan 5 = 1 day, Jan 6 = 1 day)
- Meropenem IV Days: **2**
- Days Present: 3 (Jan 5, 6, 7)

---

## Test Case AU-2: Multiple Antimicrobials Same Day

**File**: `AUMultipleAntimicrobialsSameDay.json`

**Scenario**: Two different antimicrobials administered on same day

**Purpose**: Validates each antimicrobial counted separately

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1972-07-20 |
| Encounter | Admit 2025-01-10T06:00, Discharge 2025-01-13T14:00, IMP |
| Location | HSLOC 1060-3 (Medical Ward) |
| MedicationAdministration | Vancomycin 1g IV, 2025-01-10T08:00 |
| MedicationAdministration | Meropenem 1g IV, 2025-01-10T09:00 |
| MedicationAdministration | Vancomycin 1g IV, 2025-01-11T08:00 |
| MedicationAdministration | Meropenem 1g IV, 2025-01-11T09:00 |

**Expected Outcome**:
- Initial Population: 1
- Vancomycin Days: **2**
- Meropenem Days: **2**
- Total Antimicrobial Days: **4** (2 Vancomycin + 2 Meropenem)

---

## Test Case AU-3: Patient Transfer Between Locations

**File**: `AUPatientTransfer.json`

**Scenario**: Patient transfers from ICU to ward, receives antimicrobial in both locations on same day

**Purpose**: Validates antimicrobial day attributed to both locations but only once to FacWideIN

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1958-11-08 |
| Encounter | Admit 2025-01-15T07:00, Discharge 2025-01-18T10:00, IMP |
| Location 1 | HSLOC 1027-2 (Medical Critical Care), 2025-01-15 to 2025-01-16T14:00 |
| Location 2 | HSLOC 1060-3 (Medical Ward), 2025-01-16T14:00 to 2025-01-18 |
| MedicationAdministration | Ceftriaxone 1g IV, 2025-01-16T08:00 (in ICU) |
| MedicationAdministration | Ceftriaxone 1g IV, 2025-01-16T20:00 (in Ward) |

**Expected Outcome**:
- Initial Population: 1
- ICU Ceftriaxone Days: **1** (Jan 16)
- Ward Ceftriaxone Days: **1** (Jan 16)
- FacWideIN Ceftriaxone Days: **1** (only counted once)

---

## Test Case AU-4: ED Encounter with Oral Antimicrobial

**File**: `AUEDOralAntimicrobial.json`

**Scenario**: ED visit with oral antimicrobial administered

**Purpose**: Validates outpatient encounter with digestive route

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1985-04-22 |
| Encounter | 2025-01-08T14:00 to 2025-01-08T18:00, EMER |
| Location | HSLOC 1108-0 (Emergency Department) |
| MedicationAdministration | Ciprofloxacin 500mg PO, 2025-01-08T15:00 |

**Expected Outcome**:
- Initial Population: 1
- ED Encounters: **1**
- Ciprofloxacin Digestive Days: **1**

---

## Test Case AU-5: Multi-Day Stay Spanning Months

**File**: `AUSpanningMonths.json`

**Scenario**: Patient admission spans December and January

**Purpose**: Validates antimicrobial days attributed to correct month

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1970-09-30 |
| Encounter | Admit 2024-12-30T10:00, Discharge 2025-01-02T12:00, IMP |
| Location | HSLOC 1030-6 (Surgical Critical Care) |
| MedicationAdministration | Piperacillin-Tazobactam 4.5g IV, 2024-12-31T08:00 |
| MedicationAdministration | Piperacillin-Tazobactam 4.5g IV, 2025-01-01T08:00 |

**Expected Outcome**:
- Initial Population (January): 1
- December Pip-Tazo Days: **1** (Dec 31)
- January Pip-Tazo Days: **1** (Jan 1)
- Admission counted in December (first inpatient day)

---

## Test Case AU-6: Inhaled Antimicrobial

**File**: `AUInhaledAntimicrobial.json`

**Scenario**: Patient receives inhaled antimicrobial

**Purpose**: Validates respiratory route tracking

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1945-02-14 |
| Encounter | Admit 2025-01-20T09:00, Discharge 2025-01-25T11:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| MedicationAdministration | Tobramycin 300mg INH, 2025-01-20T10:00 |
| MedicationAdministration | Tobramycin 300mg INH, 2025-01-21T10:00 |

**Expected Outcome**:
- Initial Population: 1
- Tobramycin Respiratory Days: **2**
- Tobramycin IV Days: **0**

---

## Test Case AU-7: No Antimicrobial Administration

**File**: `AUNoAntimicrobial.json`

**Scenario**: Inpatient encounter without any antimicrobial administration

**Purpose**: Validates patient contributes to denominator but not numerator

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1990-06-18 |
| Encounter | Admit 2025-01-12T07:00, Discharge 2025-01-14T16:00, IMP |
| Location | HSLOC 1060-3 (Medical Ward) |

**Expected Outcome**:
- Initial Population: 1
- Days Present: **2**
- Total Antimicrobial Days: **0**

---

## Part 2: Antimicrobial Resistance (AR) Test Cases

---

## Test Case AR-1: Hospital-Onset MRSA Bacteremia

**File**: `ARHospitalOnsetMRSA.json`

**Scenario**: Blood culture positive for MRSA on hospital day 5

**Purpose**: Validates HO AR event with MRSA phenotype

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1960-08-25 |
| Encounter | Admit 2025-01-02T08:00, Discharge 2025-01-12T10:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen | Blood, collected 2025-01-06T10:00 (Day 5) |
| Observation (Culture) | S. aureus (3092008), Positive |
| Observation (Susceptibility) | Oxacillin - Resistant |

**Expected Outcome**:
- Initial Population: 1
- HO AR Event: **Positive** (day 5 = hospital-onset)
- MRSA Phenotype: **Positive** (oxacillin resistant)

---

## Test Case AR-2: Community-Onset E. coli UTI

**File**: `ARCommunityOnsetEcoliUTI.json`

**Scenario**: Urine culture positive for E. coli on hospital day 2

**Purpose**: Validates CO AR event from non-invasive specimen

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1975-03-10 |
| Encounter | Admit 2025-01-10T14:00, Discharge 2025-01-14T12:00, IMP |
| Location | HSLOC 1060-3 (Medical Ward) |
| Specimen | Urine, collected 2025-01-11T09:00 (Day 2) |
| Observation (Culture) | E. coli (112283007), Positive |
| Observation (Susceptibility) | Ciprofloxacin - Susceptible |

**Expected Outcome**:
- Initial Population: 1
- CO AR Event: **Positive** (day 2 = community-onset)
- Fluoroquinolone-resistant: **Negative** (susceptible to cipro)

---

## Test Case AR-3: Carbapenem-Resistant Klebsiella (CRE)

**File**: `ARCREKlebsiella.json`

**Scenario**: Blood culture positive for carbapenem-resistant K. pneumoniae on day 6

**Purpose**: Validates HO CRE phenotype detection

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1955-12-01 |
| Encounter | Admit 2025-01-05T06:00, Discharge 2025-01-15T14:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen | Blood, collected 2025-01-10T08:00 (Day 6) |
| Observation (Culture) | K. pneumoniae (56415008), Positive |
| Observation (Susceptibility) | Meropenem - Resistant |
| Observation (Susceptibility) | Imipenem - Resistant |

**Expected Outcome**:
- Initial Population: 1
- HO AR Event: **Positive**
- CRE Phenotype: **Positive** (resistant to carbapenems)

---

## Test Case AR-4: Vancomycin-Resistant Enterococcus (VRE)

**File**: `ARVREFaecium.json`

**Scenario**: Blood culture positive for vancomycin-resistant E. faecium on day 4

**Purpose**: Validates HO VRE detection

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1968-05-22 |
| Encounter | Admit 2025-01-08T10:00, Discharge 2025-01-18T12:00, IMP |
| Location | HSLOC 1030-6 (Surgical Critical Care) |
| Specimen | Blood, collected 2025-01-11T14:00 (Day 4) |
| Observation (Culture) | E. faecium (90272000), Positive |
| Observation (Susceptibility) | Vancomycin - Resistant |

**Expected Outcome**:
- Initial Population: 1
- HO AR Event: **Positive** (day 4 = hospital-onset threshold)
- VRE Phenotype: **Positive**

---

## Test Case AR-5: Same-Day Duplicate Cultures (Blood and Urine)

**File**: `ARSameDayDuplicates.json`

**Scenario**: Same organism from blood and urine on same day

**Purpose**: Validates deduplication - blood and urine are different source types, both count

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1962-09-15 |
| Encounter | Admit 2025-01-12T08:00, Discharge 2025-01-20T10:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen 1 | Blood, collected 2025-01-15T10:00 (Day 4) |
| Observation 1 | E. coli (112283007), Positive |
| Specimen 2 | Urine, collected 2025-01-15T10:30 (Day 4) |
| Observation 2 | E. coli (112283007), Positive |

**Expected Outcome**:
- Initial Population: 1
- HO Blood Event: **Positive** (invasive)
- Non-invasive Urine Event: **Positive** (counted separately)
- Total Events: **2** (different source types)

---

## Test Case AR-6: 14-Day Window Deduplication

**File**: `AR14DayWindow.json`

**Scenario**: Two blood cultures positive for same organism 10 days apart

**Purpose**: Validates 14-day deduplication rule - second culture within window excluded

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1950-04-08 |
| Encounter | Admit 2025-01-02T07:00, Discharge 2025-01-25T12:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen 1 | Blood, collected 2025-01-06T09:00 (Day 5) |
| Observation 1 | S. aureus (3092008), Positive |
| Specimen 2 | Blood, collected 2025-01-16T09:00 (Day 15, within 14-day window) |
| Observation 2 | S. aureus (3092008), Positive |

**Expected Outcome**:
- Initial Population: 1
- First HO Event (Jan 6): **Counted**
- Second Event (Jan 16): **Excluded** (within 14-day window)
- Total HO Events: **1**

---

## Test Case AR-7: MDR Pseudomonas aeruginosa

**File**: `ARMDRPseudomonas.json`

**Scenario**: P. aeruginosa resistant to drugs in 3+ categories

**Purpose**: Validates MDR phenotype detection

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1948-11-30 |
| Encounter | Admit 2025-01-10T08:00, Discharge 2025-01-22T14:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen | Lower Respiratory, collected 2025-01-14T10:00 (Day 5) |
| Observation (Culture) | P. aeruginosa (52499004), Positive |
| Observation (Susceptibility) | Cefepime - Resistant (Cephalosporin) |
| Observation (Susceptibility) | Ciprofloxacin - Resistant (Fluoroquinolone) |
| Observation (Susceptibility) | Meropenem - Resistant (Carbapenem) |
| Observation (Susceptibility) | Amikacin - Susceptible (Aminoglycoside) |

**Expected Outcome**:
- Initial Population: 1
- HO AR Event: **Positive**
- MDR P. aeruginosa: **Positive** (I/R in 3 categories: cephalosporin, fluoroquinolone, carbapenem)

---

## Test Case AR-8: Negative Culture

**File**: `ARNegativeCulture.json`

**Scenario**: Blood culture with no growth

**Purpose**: Validates no AR event when culture is negative

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1980-02-28 |
| Encounter | Admit 2025-01-18T10:00, Discharge 2025-01-22T12:00, IMP |
| Location | HSLOC 1060-3 (Medical Ward) |
| Specimen | Blood, collected 2025-01-21T08:00 (Day 4) |
| Observation (Culture) | No growth (264868006) |

**Expected Outcome**:
- Initial Population: 1
- AR Event: **No** (negative culture)

---

## Test Case AR-9: Carbapenem-Resistant Acinetobacter

**File**: `ARCRAcinetobacter.json`

**Scenario**: A. baumannii resistant to carbapenems from respiratory specimen

**Purpose**: Validates carbapenem-non-susceptible Acinetobacter phenotype

| Resource | Details |
|----------|---------|
| Patient | Male, DOB 1942-07-14 |
| Encounter | Admit 2025-01-05T06:00, Discharge 2025-01-20T10:00, IMP |
| Location | HSLOC 1027-2 (Medical Critical Care) |
| Specimen | Lower Respiratory, collected 2025-01-10T14:00 (Day 6) |
| Observation (Culture) | A. baumannii (91288006), Positive |
| Observation (Susceptibility) | Imipenem - Intermediate |
| Observation (Susceptibility) | Meropenem - Resistant |

**Expected Outcome**:
- Initial Population: 1
- HO AR Event: **Positive**
- Carbapenem-NS Acinetobacter: **Positive** (I/R to imipenem and meropenem)

---

## Test Case AR-10: ED Encounter with Positive Culture

**File**: `AREDPositiveCulture.json`

**Scenario**: ED visit with positive urine culture

**Purpose**: Validates AR event in outpatient setting

| Resource | Details |
|----------|---------|
| Patient | Female, DOB 1988-10-05 |
| Encounter | 2025-01-15T09:00 to 2025-01-15T14:00, EMER |
| Location | HSLOC 1108-0 (Emergency Department) |
| Specimen | Urine, collected 2025-01-15T10:00 |
| Observation (Culture) | E. coli (112283007), Positive |
| Observation (Susceptibility) | Ciprofloxacin - Resistant |

**Expected Outcome**:
- Initial Population: 1
- ED Encounter: **1**
- CO AR Event: **Positive** (ED = community-onset)
- Fluoroquinolone-resistant E. coli: **Positive**

---

## FHIR Resources Summary

| Test Case | Patient | Encounter | Location | MedAdmin | Specimen | Observation |
|-----------|:-------:|:---------:|:--------:|:--------:|:--------:|:-----------:|
| AU-1 | 1 | 1 | 1 | 3 | - | - |
| AU-2 | 1 | 1 | 1 | 4 | - | - |
| AU-3 | 1 | 1 | 2 | 2 | - | - |
| AU-4 | 1 | 1 | 1 | 1 | - | - |
| AU-5 | 1 | 1 | 1 | 2 | - | - |
| AU-6 | 1 | 1 | 1 | 2 | - | - |
| AU-7 | 1 | 1 | 1 | - | - | - |
| AR-1 | 1 | 1 | 1 | - | 1 | 2 |
| AR-2 | 1 | 1 | 1 | - | 1 | 2 |
| AR-3 | 1 | 1 | 1 | - | 1 | 3 |
| AR-4 | 1 | 1 | 1 | - | 1 | 2 |
| AR-5 | 1 | 1 | 1 | - | 2 | 2 |
| AR-6 | 1 | 1 | 1 | - | 2 | 2 |
| AR-7 | 1 | 1 | 1 | - | 1 | 5 |
| AR-8 | 1 | 1 | 1 | - | 1 | 1 |
| AR-9 | 1 | 1 | 1 | - | 1 | 3 |
| AR-10 | 1 | 1 | 1 | - | 1 | 2 |

---

## Code Reference

### Antimicrobials (RxNorm)
| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Meropenem 1g Injection | 1722939 | Meropenem 1000 MG Injection |
| Vancomycin 1g Injection | 1664986 | Vancomycin 1000 MG Injection |
| Ceftriaxone 1g Injection | 309090 | Ceftriaxone 1000 MG Injection |
| Piperacillin-Tazobactam 4.5g | 1659149 | Piperacillin 4000 MG / Tazobactam 500 MG Injection |
| Ciprofloxacin 500mg Tablet | 309309 | Ciprofloxacin 500 MG Oral Tablet |
| Tobramycin 300mg Inhalation | 1165258 | Tobramycin 300 MG/5ML Inhalation Solution |
| Amikacin 1g Injection | 1665021 | Amikacin 1000 MG Injection |

### Routes of Administration (SNOMED)
| Route | SNOMED Code | Display |
|-------|-------------|---------|
| Intravenous | 47625008 | Intravenous route |
| Oral | 26643006 | Oral route |
| Inhalation | 447694001 | Respiratory tract route |

### Organisms (SNOMED)
| Organism | SNOMED Code | Display |
|----------|-------------|---------|
| Staphylococcus aureus | 3092008 | Staphylococcus aureus |
| Escherichia coli | 112283007 | Escherichia coli |
| Klebsiella pneumoniae | 56415008 | Klebsiella pneumoniae |
| Pseudomonas aeruginosa | 52499004 | Pseudomonas aeruginosa |
| Enterococcus faecium | 90272000 | Enterococcus faecium |
| Acinetobacter baumannii | 91288006 | Acinetobacter baumannii |
| No growth | 264868006 | No growth |

### Susceptibility Test Interpretations (SNOMED)
| Interpretation | SNOMED Code | Display |
|----------------|-------------|---------|
| Susceptible | 131196009 | Susceptible |
| Resistant | 30714006 | Resistant |
| Intermediate | 11896004 | Intermediate |
