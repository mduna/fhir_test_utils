# Sepsis Protocol Test Generator

Adult Sepsis Event (ASE) test case generator for MADiE testing.

## Quick Start

```bash
cd protocols/sepsis
python generate_sepsis_tests.py
```

Output: `NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip`

## Test Cases Generated (20 Total)

### Community-Onset Sepsis (SCO) Cases (1-4)

| # | Test Case | Description | Expected IP | Onset |
|---|-----------|-------------|-------------|-------|
| 1 | SCOPositiveBasicLactate | Blood culture + 4 QADs + lactate >2.0 | 1 | Day 2 |
| 2 | SCOPositiveMultipleOrgan | Hypotension + renal dysfunction | 1 | Day 2 |
| 3 | SCOPositiveDay3Boundary | Onset exactly on day 3 (boundary) | 1 | Day 3 |
| 4 | SCOPositivePrincipalDxInfection | Principal Dx infection (no blood culture) | 1 | Day 1 |

### Hospital-Onset Sepsis (SHO) Cases (5-6)

| # | Test Case | Description | Expected IP | Onset |
|---|-----------|-------------|-------------|-------|
| 5 | SHOPositiveDay5Onset | Blood culture + lactate on day 5 | 1 | Day 5 |
| 6 | SHOPositiveEscalatingCardiovascular | Hypotension -> vasopressor escalation | 1 | Day 4 |

### Cardiovascular Dysfunction Cases (7-8)

| # | Test Case | Description | Expected IP | Organ |
|---|-----------|-------------|-------------|-------|
| 7 | CardiovascularHypotension | 3 SBP readings <90 within 3h | 1 | Cardiovascular |
| 8 | CardiovascularVasopressor | New vasopressor initiation | 1 | Cardiovascular |

### Respiratory Dysfunction Cases (9-10)

| # | Test Case | Description | Expected IP | Organ |
|---|-----------|-------------|-------------|-------|
| 9 | RespiratoryInvasiveVent | Invasive mechanical ventilation | 1 | Respiratory |
| 10 | RespiratoryNIVHFNC | NIV/HFNC for 2+ calendar days | 1 | Respiratory |

### Other Organ Dysfunction Cases (11-16)

| # | Test Case | Description | Expected IP | Organ |
|---|-----------|-------------|-------------|-------|
| 11 | MetabolicLactateElevated | Lactate >2.0 mmol/L | 1 | Metabolic |
| 12 | RenalCreatinine2xIncrease | Creatinine 2x increase | 1 | Renal |
| 13 | RenalExcludedESRD | ESRD patient - renal excluded | 1 | (ESRD Exclusion) |
| 14 | HepaticBilirubin2xIncrease | Bilirubin 2x increase to >=2.0 | 1 | Hepatic |
| 15 | HepaticExcludedLiverDisease | Liver disease - hepatic excluded | 1 | (Liver Exclusion) |
| 16 | CoagulationPlatelet50Decrease | Platelets 50% decrease to <100 | 1 | Coagulation |

### Exclusion and Exception Cases (17-20)

| # | Test Case | Description | Expected IP | Category |
|---|-----------|-------------|-------------|----------|
| 17 | CoagulationExcludedMalignancy | Malignancy - coagulation excluded | 1 | Exclusion |
| 18 | QADExceptionDeathBefore4 | Death before 4 QADs - qualifies | 1 | QAD Exception |
| 19 | RepeatEventTimeframeExcluded | Second event within 7-day RET | 1 | RET |
| 20 | QADWith1DayGap | 1-day gaps tolerated (4 QADs met) | 1 | QAD Gap |

## ASE Surveillance Metrics Coverage

| Metric | Positive Test | Notes |
|--------|---------------|-------|
| Community-Onset Sepsis (SCO) | 1, 2, 3, 4 | Onset day 1-3 |
| Hospital-Onset Sepsis (SHO) | 5, 6 | Onset day 4+ |
| Cardiovascular Dysfunction | 2, 6, 7, 8 | Hypotension or vasopressor |
| Respiratory Dysfunction | 9, 10 | Ventilation (invasive or NIV/HFNC) |
| Metabolic Dysfunction | 1, 3, 5, 11 | Lactate >2.0 |
| Renal Dysfunction | 12 | Creatinine 2x |
| Hepatic Dysfunction | 14 | Bilirubin 2x |
| Coagulation Dysfunction | 16 | Platelets 50% decrease |
| Exclusion - ESRD | 13 | Renal criteria excluded |
| Exclusion - Liver Disease | 15 | Hepatic criteria excluded |
| Exclusion - Malignancy | 17 | Coagulation criteria excluded |
| QAD Exception - Death | 18 | <4 QADs with death |
| Repeat Event Timeframe | 19 | Second event within RET |
| QAD Gap Tolerance | 20 | 1-day gaps allowed |

## Files

- `generate_sepsis_tests.py` - Test case generator script (20 test cases)
- `sepsis_protocol_summary.md` - Protocol documentation
- `Sepsis_Test_Cases.md` - Detailed test case specifications
- `README.md` - This file

## Usage in MADiE

1. Run the generator script: `python generate_sepsis_tests.py`
2. Import the ZIP file into MADiE
3. Execute measure against `NHSNACHMonthly1`
4. Verify all test cases show `initialPopulation = 1`
5. Use collected data for downstream ASE evaluation

## Protocol Details

See `sepsis_protocol_summary.md` for full protocol documentation including:
- ASE event definition (infection criteria + organ dysfunction)
- Community-onset vs Hospital-onset classification
- Qualifying Antimicrobial Days (QAD) rules
- Organ dysfunction criteria and exclusions
- Sepsis window period and onset date calculation

## Key Concepts

### Sepsis Day Calculation
| Day | Description |
|-----|-------------|
| Day 1 | Date of facility presentation |
| Day 2 | Day after presentation |
| Day 3 | 2 days after (SCO boundary) |
| Day 4+ | Hospital-onset territory |

### Event Classification
| Event Type | Onset Date |
|------------|------------|
| Community-Onset (SCO) | Day 1, 2, or 3 |
| Hospital-Onset (SHO) | Day 4 or later |

### Organ Dysfunction Criteria

| Organ | Criteria | Exclusions |
|-------|----------|------------|
| Cardiovascular | SBP<90 (2+ readings in 3h) OR vasopressor | - |
| Respiratory | Invasive vent OR NIV/HFNC 2+ days | - |
| Metabolic | Lactate >2.0 mmol/L | - |
| Renal | Creatinine 2x increase | ESRD |
| Hepatic | Bilirubin 2x to >=2.0 | Liver disease |
| Coagulation | Platelets 50% decrease to <100 | Malignancy |

## Code Reference

### Laboratory Tests (LOINC)
| Test | LOINC Code |
|------|------------|
| Blood Culture | 600-7 |
| Creatinine | 2160-0 |
| Bilirubin | 1975-2 |
| Platelets | 777-3 |
| Lactate | 2524-7 |

### Vital Signs (LOINC)
| Vital | LOINC Code |
|-------|------------|
| Blood Pressure Panel | 85354-9 |
| Systolic BP (component) | 8480-6 |
| Diastolic BP (component) | 8462-4 |

### Antimicrobials (RxNorm)
| Medication | RxNorm Code |
|------------|-------------|
| Piperacillin/Tazobactam | 1659149 |
| Vancomycin | 1664986 |
| Ceftriaxone | 309090 |
| Meropenem | 1722939 |
| Levofloxacin IV | 311365 |

### Vasopressors (RxNorm)
| Medication | RxNorm Code |
|------------|-------------|
| Norepinephrine | 1659027 |
| Epinephrine | 1991339 |
| Vasopressin | 1596994 |
