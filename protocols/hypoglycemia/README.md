# Hypoglycemia Test Generator

Hospital-Acquired Hypoglycemia (HAH) test case generator for MADiE testing.

## Quick Start

```bash
cd protocols/hypoglycemia
python generate_hypoglycemia_tests.py
```

Output: `NHSNACHMonthly1-v0.0.000-FHIR-TestCases.zip`

## Protocol Definition

**Severe Hypoglycemia Event**: Blood glucose < 40 mg/dL during an inpatient encounter.

### Qualifying Criteria
- Patient has an inpatient encounter (class = IMP)
- Blood glucose laboratory result < 40 mg/dL
- Glucose measurement collected during the encounter period

### Medication Association
Events are often associated with antidiabetic medications:
- Insulin (regular, NPH, glargine, IV)
- Sulfonylureas (glipizide, glyburide)

## Test Cases Generated

| # | Test Case | Category | Expected IP | Description |
|---|-----------|----------|-------------|-------------|
| 1 | SevereHypoWithInsulin | Positive | 1 | Glucose 35 mg/dL after insulin |
| 2 | SevereHypoWithOralAgent | Positive | 1 | Glucose 38 mg/dL after glipizide |
| 3 | SevereHypoDay1 | Positive | 1 | Glucose 32 mg/dL on admission day |
| 4 | MultipleHypoEvents | Positive | 1 | Two severe hypoglycemia events |
| 5 | ModerateHypoExcluded | Exclusion | 1 | Glucose 45 mg/dL (above threshold) |
| 6 | HypoWithoutMedication | Positive | 1 | Glucose 35 mg/dL, no antidiabetic |
| 7 | PreAdmissionHypo | Exclusion | 1 | Glucose before encounter start |
| 8 | OutpatientEncounter | Exclusion | 0 | ED encounter only |
| 9 | GlucoseAtThreshold | Edge | 1 | Glucose exactly 40 mg/dL |
| 10 | ICUHypoglycemia | Positive | 1 | ICU patient with severe hypo |

## Files

| File | Description |
|------|-------------|
| `generate_hypoglycemia_tests.py` | Test case generator script |
| `hypoglycemia_protocol_summary.md` | Protocol documentation |
| `hypoglycemia_Test_Cases.md` | Detailed test case specifications |
| `README.md` | This file |

## LOINC Codes Used

| Code | Description |
|------|-------------|
| 2339-0 | Glucose [Mass/volume] in Blood |
| 2345-7 | Glucose [Mass/volume] in Serum or Plasma |
| 41653-7 | Glucose [Mass/volume] in Capillary blood by Glucometer |

## Medications Used

| RxNorm Code | Medication |
|-------------|------------|
| 311034 | Regular Insulin 100 UNT/ML |
| 261551 | Insulin Glargine 100 UNT/ML |
| 311041 | NPH Insulin 100 UNT/ML |
| 310488 | Glipizide 10 MG Tablet |
| 310534 | Glyburide 5 MG Tablet |

## Usage in MADiE

1. Run generator script to create test cases
2. Import the generated ZIP file into MADiE
3. Execute measure against NHSNACHMonthly1
4. Verify each test case shows expected `initialPopulation` value
5. Review hypoglycemia event detection in downstream evaluation

## Severity Classification Reference

| Classification | Blood Glucose | Surveillance Status |
|---------------|---------------|---------------------|
| Severe | < 40 mg/dL | Primary event |
| Moderate | 40-54 mg/dL | Not counted as severe |
| Mild | 55-70 mg/dL | Not counted |
