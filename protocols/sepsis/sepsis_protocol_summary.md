# Adult Sepsis Event (ASE) Protocol Summary

## Source Document
`source_documents/Sepsis_Protocol.docx` - Adult Sepsis Event (Proposed FHIR Draft)

## Protocol Overview

The NHSN Adult Sepsis Event (ASE) Surveillance provides a mechanism for hospitals to report and analyze sepsis data as part of patient safety and quality improvement efforts. Adult sepsis events are detected using algorithms based on data available in electronic health records.

**Primary Objective**: Provide hospitals with actionable data on the incidence and outcomes of ASEs to drive improvements in patient care.

---

## Event Definition

**Adult Sepsis Event (ASE)** = Evidence of Infection Criteria + At Least 1 Organ Dysfunction Criteria

### Evidence of Infection Criteria (MUST have BOTH)

1. **Blood Culture Order** OR Infection/Sepsis as Principal Diagnosis (community-onset sepsis only)

2. **>=4 Qualifying Antibiotic Days (QAD)** starting within +/- 1 day of infection onset date
   - First QAD: first day in sepsis window period when patient receives a NEW antimicrobial
   - NEW antimicrobial: not previously administered in prior 2 calendar days
   - Must have at least one parenteral (IV/IM) antimicrobial within window period
   - Gap of 1 calendar day between doses still counts as consecutive

### Organ Dysfunction Criteria (ANY 1 within +/- 1 calendar day of blood culture)

| Organ System | Criteria | Exclusions |
|--------------|----------|------------|
| **Cardiovascular** | New hypotension (>=2 readings of SBP<90 OR MAP<65 within 3h) OR vasopressor initiation | - |
| **Respiratory** | New NIV/HFNC for >=2 calendar days OR invasive ventilation (any duration) | - |
| **Metabolic** | Lactate >2.0 mmol/L | - |
| **Renal** | 2x increase in Creatinine (to >1.18 mg/dL males, >1.02 mg/dL females) | Exclude ESRD ICD-10 codes |
| **Hepatic** | 2x increase in Bilirubin to >=2.0 mg/dL | Exclude mod/severe liver disease or hemolytic anemia |
| **Coagulation** | 50% decrease in Platelets to <100 x 10^9/L | Exclude hematologic or solid malignancy |

**Note**: For hospital-onset sepsis, cardiovascular and respiratory dysfunction must be NEW (not present prior day) or ESCALATING on consecutive days.

---

## Timing Definitions

### Sepsis Window Period
- Center: Date blood culture is obtained
- Extends: 1 day before AND 1 day after blood culture
- Multiple sepsis window periods during hospitalization are possible
- Overlapping windows may occur with multiple blood cultures

### Sepsis Day Calculation
| Day | Description |
|-----|-------------|
| Sepsis Day 1 | Date of presentation to facility (ED presentation) |
| Sepsis Day 2 | Day after presentation |
| Sepsis Day 3 | 2 days after presentation |
| Sepsis Day 4+ | Hospital-onset territory |

### Event Types

| Event Type | Onset Date Requirement |
|------------|------------------------|
| **Community-Onset Sepsis (SCO)** | Onset date on sepsis day 1, 2, or 3 |
| **Hospital-Onset Sepsis (SHO)** | Onset date on sepsis day 4 or later |

### Onset Date
The **earliest day** in the sepsis window period when ANY of these occur:
- Blood culture obtained
- First QAD begins
- Organ dysfunction criteria met

---

## Qualifying Antimicrobial Days (QAD) Rules

1. **Minimum 4 QADs required** (with exceptions below)
2. **NEW antimicrobial**: not given in prior 2 calendar days
3. **At least one parenteral** (IV/IM) antimicrobial within window period required
4. **Gap tolerance**: 1 calendar day gap between doses still counts as consecutive
5. **Oral/IV same antimicrobial**: counted as same (EXCEPT vancomycin)

### Exceptions to 4 QAD Rule

| Scenario | QAD Requirement |
|----------|-----------------|
| Patient dies, comfort care, discharge to hospice/hospital | Consecutive QADs until day of or 1 day prior to event |
| ED/observation only + death | QAD required each day until day of or 1 day prior to death |
| Discharge alive with principal dx of infection/sepsis (CO only) | 3 QADs with consecutive until discharge or 1 day prior |

---

## Repeat Event Timeframe (RET)

- **Duration**: 7 days starting from onset date (onset date = Day 1)
- **Rule**: No new ASE reported if criteria met within RET
- **Scope**: Applies during single admission including discharge day and day after
- **Carryover**: Does NOT carry over between admissions

---

## Baseline Organ Function

### Community-Onset Events
- **Baseline values**: Best value during hospitalization
- **Assume normal if death/discharge to hospice** unless comorbidity codes present:
  - Creatinine: 1.18 (males), 1.02 (females) unless Elixhauser mod-severe renal failure
  - Bilirubin: 0.5 unless Elixhauser mod-severe liver disease
  - Platelets: 200

### Hospital-Onset Events
- **Creatinine baseline**: Lowest value within sepsis window period (+/-1 day of blood culture)
- **Bilirubin baseline**: Lowest value within sepsis window period
- **Platelet baseline**: Highest value within sepsis window period AND must be >=100 cells/uL

---

## Primary Quality Measure

### Numerator (Community-Onset Sepsis SMR)
Patients meeting SCO event criteria who:
- Expire during hospitalization, OR
- Are discharged to hospice

### Denominator
Patients meeting SCO criteria predicted to expire or discharge to hospice

---

## Vasopressor Medications

New vasopressor initiation within +/-1 calendar day of blood culture:
- Norepinephrine
- Dopamine
- Epinephrine
- Phenylephrine
- Vasopressin
- Angiotensin II

**NEW vasopressor**: Not administered in prior calendar day

---

## Required FHIR Resources

| Resource | Profile | Key Elements |
|----------|---------|--------------|
| Patient | qicore-patient | DOB, gender, race, ethnicity |
| Encounter | qicore-encounter | Class, period, location, discharge disposition |
| Location | qicore-location | HSLOC type (inpatient, ED, observation) |
| Coverage | qicore-coverage | Insurance type |
| ServiceRequest | qicore-servicerequest | Blood culture order |
| Specimen | qicore-specimen | Blood specimen, collection datetime |
| Observation (Lab) | qicore-observation-lab | Creatinine, bilirubin, platelets, lactate, WBC |
| Observation (Vitals) | us-core-vital-signs | SBP, MAP, temperature, HR, RR, SpO2 |
| MedicationAdministration | qicore-medicationadministration | Antimicrobials, vasopressors |
| Procedure | qicore-procedure | Ventilation (invasive, NIV, HFNC) |
| Condition | qicore-condition | Principal diagnosis, comorbidities (Elixhauser) |
| Device | qicore-device | Ventilator devices |

---

## Key Code Systems and Value Sets

### Laboratory Tests (LOINC)

| Test | LOINC Code | Display |
|------|------------|---------|
| Blood Culture | 600-7 | Bacteria identified in Blood by Culture |
| Creatinine (serum) | 2160-0 | Creatinine [Mass/volume] in Serum or Plasma |
| Bilirubin (total) | 1975-2 | Bilirubin.total [Mass/volume] in Serum or Plasma |
| Platelets | 777-3 | Platelets [#/volume] in Blood by Automated count |
| Lactate | 2524-7 | Lactate [Moles/volume] in Serum or Plasma |

### Vital Signs (LOINC)

| Vital | LOINC Code | Display |
|-------|------------|---------|
| Systolic BP | 8480-6 | Systolic blood pressure |
| Mean Arterial Pressure | 8478-0 | Mean blood pressure |
| Heart Rate | 8867-4 | Heart rate |
| Respiratory Rate | 9279-1 | Respiratory rate |
| Temperature | 8310-5 | Body temperature |
| SpO2 | 2708-6 | Oxygen saturation in Arterial blood |

### Antimicrobials (RxNorm - examples)

| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Vancomycin 1000 MG Injection | 1664986 | Vancomycin 1000 MG Injection |
| Piperacillin/Tazobactam 4.5 GM | 1659149 | Piperacillin 4000 MG / tazobactam 500 MG Injection |
| Levofloxacin 500 MG | 311363 | Levofloxacin 500 MG Oral Tablet |
| Ceftriaxone 1 GM | 309090 | Ceftriaxone 1000 MG Injection |

### Vasopressors (RxNorm - examples)

| Medication | RxNorm Code | Display |
|------------|-------------|---------|
| Norepinephrine | 7512 | Norepinephrine |
| Dopamine | 3628 | Dopamine |
| Epinephrine | 3992 | Epinephrine |
| Phenylephrine | 8163 | Phenylephrine |
| Vasopressin | 11149 | Vasopressin |

### Ventilation Procedures (SNOMED)

| Procedure | SNOMED Code | Display |
|-----------|-------------|---------|
| Invasive mechanical ventilation | 40617009 | Artificial respiration |
| Non-invasive ventilation | 428311008 | Non-invasive ventilation |
| High flow nasal cannula | 371907003 | Oxygen administration by nasal cannula |

---

## Test Scenarios Required

### Community-Onset Sepsis (SCO) Events
1. SCO Positive - Basic case with blood culture + 4 QAD + organ dysfunction on day 2
2. SCO Positive - Multiple organ dysfunction criteria
3. SCO Positive - Death with <4 QAD (exception rule)
4. SCO Positive - Principal diagnosis infection with 3 QAD
5. SCO Excluded - Onset date on day 4 (becomes SHO)

### Hospital-Onset Sepsis (SHO) Events
6. SHO Positive - Blood culture on day 5 with organ dysfunction
7. SHO Positive - Escalating cardiovascular dysfunction
8. SHO Excluded - Onset date on day 3 (becomes SCO)

### Organ Dysfunction Specific
9. Cardiovascular - Hypotension (2+ readings SBP<90)
10. Cardiovascular - Vasopressor initiation
11. Respiratory - Invasive ventilation
12. Respiratory - NIV/HFNC for 2+ days
13. Metabolic - Lactate >2.0
14. Renal - Creatinine 2x increase
15. Hepatic - Bilirubin 2x increase
16. Coagulation - Platelets 50% decrease

### Exclusions
17. Renal dysfunction excluded - ESRD diagnosis
18. Hepatic dysfunction excluded - Liver disease diagnosis
19. Coagulation dysfunction excluded - Malignancy diagnosis

### QAD Edge Cases
20. QAD with 1-day gap (still qualifies)
21. QAD oral only (excluded - no parenteral)
22. QAD interrupted >1 day gap (excluded)

### Repeat Event Timeframe
23. Second event within 7-day RET (excluded)
24. Second event after 7-day RET (new event)
