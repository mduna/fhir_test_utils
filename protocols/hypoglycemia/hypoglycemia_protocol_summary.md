# Hypoglycemia Protocol Summary

## Source Document
NHSN Glycemic Control Surveillance Protocol

## Protocol Overview
Hospital-acquired hypoglycemia (HAH) surveillance measures severe hypoglycemic events occurring during inpatient hospital stays. Severe hypoglycemia is defined as blood glucose < 40 mg/dL and is a patient safety indicator often associated with insulin or other antidiabetic medication administration.

## Event Definition

### Severe Hypoglycemia Event
A blood glucose measurement < 40 mg/dL occurring during an inpatient encounter.

### Timing
- **Hospital Day 1** = Admission date
- Events tracked throughout the entire inpatient stay
- Measurement period: Monthly reporting cycle

### Qualifying Criteria
1. Patient has an inpatient encounter (class = IMP)
2. Blood glucose laboratory result < 40 mg/dL
3. Glucose measurement collected during the encounter period

## Medication Association

### Antidiabetic Medications (commonly associated)
- **Insulin** (short-acting, intermediate, long-acting, mixed)
- **Sulfonylureas** (glipizide, glyburide, glimepiride)
- **Meglitinides** (repaglinide, nateglinide)

### Medication Timing
- Hypoglycemia within 24 hours of antidiabetic medication administration is considered medication-associated

## Severity Classification

| Classification | Blood Glucose | Definition |
|---------------|---------------|------------|
| Severe Hypoglycemia | < 40 mg/dL | Primary surveillance event |
| Moderate Hypoglycemia | 40-54 mg/dL | May trigger additional monitoring |
| Mild Hypoglycemia | 55-70 mg/dL | Clinically significant but not severe |

## Exclusions

1. **Pre-admission hypoglycemia** - Glucose < 40 mg/dL before encounter start
2. **Outpatient events** - Events during ED or outpatient visits only
3. **Non-inpatient encounters** - Observation stays, outpatient procedures

## Data Requirements

### Required FHIR Resources
| Resource | Profile | Key Elements |
|----------|---------|--------------|
| Patient | qicore-patient | DOB, gender |
| Encounter | qicore-encounter | Class (IMP), period, location |
| Observation | qicore-observation-lab | Glucose result, effectiveDateTime |
| MedicationAdministration | qicore-medicationadministration | Insulin/antidiabetic, effectiveDateTime |
| Coverage | qicore-coverage | Payer information |
| Location | qicore-location | HSLOC type |

### Key Value Sets / Codes

#### Laboratory Codes (LOINC)
| Element | Code | Display |
|---------|------|---------|
| Blood Glucose | 2339-0 | Glucose [Mass/volume] in Blood |
| Plasma Glucose | 2345-7 | Glucose [Mass/volume] in Serum or Plasma |
| POC Glucose | 41653-7 | Glucose [Mass/volume] in Capillary blood by Glucometer |

#### Medication Codes (RxNorm)
| Medication | Code | Display |
|------------|------|---------|
| Regular Insulin | 311034 | Insulin regular, human 100 UNT/ML Injectable Solution |
| Insulin Glargine | 261551 | Insulin glargine 100 UNT/ML Injectable Solution |
| NPH Insulin | 311041 | Insulin, isophane human 100 UNT/ML Injectable Suspension |
| Glipizide | 310488 | Glipizide 10 MG Oral Tablet |
| Glyburide | 310534 | Glyburide 5 MG Oral Tablet |

#### Units (UCUM)
| Measurement | Unit | UCUM Code |
|-------------|------|-----------|
| Glucose | mg/dL | mg/dL |

## Test Scenarios

### Positive Cases (Hypoglycemia Event Detected)
1. Severe hypoglycemia (< 40 mg/dL) with insulin administration
2. Severe hypoglycemia (< 40 mg/dL) with oral antidiabetic
3. Severe hypoglycemia on hospital day 1 (admission day)
4. Multiple hypoglycemic events during same encounter

### Exclusion Cases (No Event Counted)
5. Moderate hypoglycemia (glucose = 45 mg/dL) - above threshold
6. Hypoglycemia without antidiabetic medication
7. Pre-admission hypoglycemia (glucose drawn before encounter start)
8. Outpatient/observation encounter only

### Edge Cases (Boundary Conditions)
9. Glucose exactly at 40 mg/dL (at threshold)
10. Hypoglycemia at exact encounter start time

## Metrics

### Primary Measures
- **Severe Hypoglycemia Rate**: Events per 1,000 patient days
- **Medication-Associated Hypoglycemia Rate**: Events with antidiabetic within 24 hours

### Stratification
- By location type (ICU vs. general floor)
- By medication type (insulin vs. oral agents)
- By patient population (diabetes vs. non-diabetes)
