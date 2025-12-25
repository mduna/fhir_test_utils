# AUR (Antimicrobial Use and Resistance) Test Generator

NHSN Patient-level Antimicrobial Use and Resistance Module test case generator for MADiE testing.

## Quick Start

```bash
cd protocols/aur
python generate_aur_tests.py
```

Output: `NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip`

## Protocol Overview

The AUR module consists of two surveillance options:

### AU Option (Antimicrobial Use)
- Tracks antimicrobial days of therapy (Days of Therapy)
- Stratified by route: IV, IM, Digestive, Respiratory
- Locations: Inpatient, ED, Pediatric ED, 24-hour Observation

### AR Option (Antimicrobial Resistance)
- Tracks resistant organism events from cultures
- Hospital-Onset (HO): Day 4+ | Community-Onset (CO): Day 1-3
- Specimen sources: Blood, CSF, Urine, Lower Respiratory, Skin/Soft Tissue

## Test Cases Generated (17 total)

### AU Option Test Cases (7)

| # | Test Case | Description | Expected |
|---|-----------|-------------|----------|
| AU-1 | BasicInpatientIV | Single IV antimicrobial (Meropenem) | IP = 1 |
| AU-2 | MultipleAntimicrobials | Two drugs same day | IP = 1 |
| AU-3 | PatientTransfer | Transfer between ICU and Ward | IP = 1 |
| AU-4 | EDOralAntimicrobial | ED with oral Ciprofloxacin | IP = 1 |
| AU-5 | SpanningMonths | Admission spans Dec/Jan | IP = 1 |
| AU-6 | InhaledAntimicrobial | Inhaled Tobramycin | IP = 1 |
| AU-7 | NoAntimicrobial | Inpatient without antimicrobials | IP = 1 |

### AR Option Test Cases (10)

| # | Test Case | Description | Phenotype |
|---|-----------|-------------|-----------|
| AR-1 | HospitalOnsetMRSA | S. aureus Day 5, oxacillin-R | MRSA |
| AR-2 | CommunityOnsetEcoliUTI | E. coli urine Day 2, cipro-S | FQ-R: No |
| AR-3 | CREKlebsiella | K. pneumoniae, carbapenem-R | CRE |
| AR-4 | VREFaecium | E. faecium, vancomycin-R | VRE |
| AR-5 | SameDayDuplicates | Blood + urine same organism | 2 events |
| AR-6 | 14DayWindow | 2 blood cultures 10 days apart | 1 event |
| AR-7 | MDRPseudomonas | P. aeruginosa R to 3 categories | MDR |
| AR-8 | NegativeCulture | No growth | No event |
| AR-9 | CRAcinetobacter | A. baumannii, carbapenem I/R | CR-Acine |
| AR-10 | EDPositiveCulture | ED urine, cipro-R E. coli | FQ-R |

## Files

| File | Description |
|------|-------------|
| `generate_aur_tests.py` | Test case generator script |
| `aur_protocol_summary.md` | Protocol documentation |
| `AUR_Test_Cases.md` | Test case specifications |
| `README.md` | This file |

## Key Codes Used

### Antimicrobials (RxNorm)
- Meropenem: 1722939
- Vancomycin: 1664986
- Ceftriaxone: 309090
- Piperacillin-Tazobactam: 1659149
- Ciprofloxacin 500mg: 309309
- Tobramycin Inhaled: 1165258

### Organisms (SNOMED)
- S. aureus: 3092008
- E. coli: 112283007
- K. pneumoniae: 56415008
- P. aeruginosa: 52499004
- E. faecium: 90272000
- A. baumannii: 91288006

### Susceptibility (SNOMED)
- Susceptible: 131196009
- Resistant: 30714006
- Intermediate: 11896004

## Usage in MADiE

1. Run generator: `python generate_aur_tests.py`
2. Import ZIP into MADiE
3. Execute measure against test cases
4. Verify Initial Population = 1 for all test cases
5. Verify phenotype classifications match expected outcomes

## Validation

All codes were validated using:
```bash
python code_validator.py protocols/aur/generate_aur_tests.py --use-vsac
```
