# HOB Protocol Test Generator

Hospital-Onset Bacteremia & Fungemia (HOB) test case generator for MADiE testing.

## Quick Start

```bash
cd protocols/hob
python generate_hob_tests.py
```

Output: `NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip`

## Test Cases Generated (10 Total)

### Primary HOB Event Cases

| # | Test Case | Description | Expected IP | HOB Result |
|---|-----------|-------------|-------------|------------|
| 1 | HOBPositiveDay4SAureus | S. aureus on hospital day 4 | 1 | HOB Positive |
| 2 | HOBPositiveDay5Candida | Candida (fungemia) on day 5 | 1 | HOB Positive |
| 3 | HOBExcludedMatchingCOB | E. coli on day 2 and day 5 (same organism) | 1 | HOB Excluded |
| 4 | HOBPositiveNonMatchingCOB | E. coli day 2, S. aureus day 5 | 1 | HOB Positive |

### Blood Culture Contamination Cases

| # | Test Case | Description | Expected IP | Contamination |
|---|-----------|-------------|-------------|---------------|
| 5 | HOBContamination1of2Positive | 1 of 2 paired sets positive (S. epidermidis) | 1 | Yes |
| 6 | HOBContamination2of2Positive | 2 of 2 paired sets positive (S. epidermidis) | 1 | No |

### Matching Commensal HOB Cases

| # | Test Case | Description | Expected IP | Matching Commensal |
|---|-----------|-------------|-------------|-------------------|
| 7 | HOBMatchingCommensalPositive | S. epidermidis + 4 days Vancomycin | 1 | Yes |
| 8 | HOBMatchingCommensalInsufficientAbx | S. epidermidis + 2 days Vancomycin | 1 | No (< 4 days) |

### Non-Measure HOB Cases

| # | Test Case | Description | Expected IP | Non-Measure |
|---|-----------|-------------|-------------|-------------|
| 9 | HOBNonMeasureHighRisk | E. coli + AML + Neutropenia | 1 | Yes |
| 10 | HOBMeasurableNoRiskFactors | S. aureus + Diabetes/HTN | 1 | No |

## NHSN HOB Surveillance Metrics Coverage

| Metric | Positive Test | Negative Test |
|--------|---------------|---------------|
| HOB Event | 1, 2, 4, 9, 10 | 3 |
| COB Event | 3, 4 | - |
| Blood Culture Contamination | 5 | 6 |
| Matching Commensal HOB | 7 | 8 |
| Non-Measure HOB | 9 | 10 |

## Files

- `generate_hob_tests.py` - Test case generator script (uses fhir_test_utils framework)
- `hob_protocol_summary.md` - Protocol documentation
- `HOB_Surveillance_Metrics.png` - NHSN metrics reference image
- `HOB_Additional_TestCases_Plan.md` - Test case planning document
- `README.md` - This file

## FHIR Resources by Test Case

| Test Case | Patient | Encounter | Location | Specimen | Observation | Condition | MedicationAdmin |
|-----------|---------|-----------|----------|----------|-------------|-----------|-----------------|
| 1-4 | Yes | Yes | Yes | Yes | Yes | - | - |
| 5-6 | Yes | Yes | Yes | Yes (paired) | Yes (paired) | - | - |
| 7-8 | Yes | Yes | Yes | Yes (2) | Yes (2) | - | Yes |
| 9-10 | Yes | Yes | Yes | Yes | Yes | Yes (2) | - |

## Usage in MADiE

1. Run the generator script: `python generate_hob_tests.py`
2. Import the ZIP file into MADiE
3. Execute measure against `NHSNACHMonthly1`
4. Verify all test cases show `initialPopulation = 1`
5. Use collected data for downstream HOB evaluation

## Protocol Details

See `hob_protocol_summary.md` for full protocol documentation including:
- HOB event definition (blood culture positive on hospital day 4+)
- Exclusion criteria (skin commensals, matching prior events)
- Hospital day calculation
- Organism matching algorithm
- Required FHIR resources and profiles

## Key SNOMED Codes

### Pathogenic Organisms (HOB Eligible)
| Organism | SNOMED Code |
|----------|-------------|
| Staphylococcus aureus | 3092008 |
| Escherichia coli | 112283007 |
| Candida albicans | 53326005 |

### Skin Commensals (HOB Excluded)
| Organism | SNOMED Code |
|----------|-------------|
| Staphylococcus epidermidis | 60875001 |

### Non-Preventability Conditions
| Condition | SNOMED Code |
|-----------|-------------|
| Acute myeloid leukemia | 91861009 |
| Neutropenia | 165517008 |

### Common Conditions (NOT Non-Preventability)
| Condition | SNOMED Code |
|-----------|-------------|
| Diabetes mellitus type 2 | 44054006 |
| Hypertensive disorder | 38341003 |

## Antibiotic Codes (RxNorm)

| Medication | RxNorm Code |
|------------|-------------|
| Vancomycin 1000 MG Injection | 1664986 |
