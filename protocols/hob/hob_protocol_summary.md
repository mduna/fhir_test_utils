# HOB (Hospital-Onset Bacteremia & Fungemia) Protocol Summary

## Source Document
Bacteremia and Fungemia Protocol_Draft_MVP_V2_clean_use this one.docx

## Protocol Overview

HOB (Hospital-Onset Bacteremia & Fungemia) is one of three event types in the CDC NHSN Bacteremia & Fungemia Surveillance Module. It tracks bloodstream infections that develop during hospitalization.

## Event Definition

### HOB Event Criteria
- **Timing**: Blood culture positive on **hospital day 4 or later**
- **Hospital Day 1** = Date admitted to inpatient location
- **Limit**: One HOB event per hospital stay
- **Infection Timeframe**: Subsequent positive cultures within 14 days are part of same HOB event

### Qualifying Blood Culture
- Specimen type: Blood
- Result: Positive for bacterial or fungal organism
- Collection datetime: Hospital day 4+

## Exclusions

### 1. Bacterial Skin Commensals
Blood cultures positive ONLY for skin commensal organisms are excluded:
- Staphylococcus epidermidis (SNOMED: 60875001)
- Other coagulase-negative staphylococci
- Corynebacterium species
- Other skin flora

### 2. Matching Prior Event Organisms
HOB is excluded when the organism matches a prior:
- **O-COB** (Outpatient Community-Onset) event
- **COB** (Community-Onset, Days 1-3) event

### Organism Matching Algorithm
1. Compare SNOMED codes - if identical, organisms match
2. If both have species-level ID and species match, organisms match
3. If neither has species-level ID but both have genus-level ID and genus matches, organisms match

## Hospital Day Calculation

| Admission Date | Day 1 | Day 2 | Day 3 | Day 4 (HOB eligible) |
|---------------|-------|-------|-------|---------------------|
| Jan 2, 2025   | Jan 2 | Jan 3 | Jan 4 | Jan 5               |
| Jan 3, 2025   | Jan 3 | Jan 4 | Jan 5 | Jan 6               |

## Data Requirements for HOB

### Required FHIR Resources
| Resource | Profile | Key Elements |
|----------|---------|--------------|
| Patient | qicore-patient | DOB, gender |
| Encounter | qicore-encounter | Class (IMP), period, location |
| Location | qicore-location | HSLOC code |
| Specimen | us-core-specimen | Type (blood), collection datetime |
| Observation | qicore-observation-lab | Blood culture result, organism code |

### Key Value Sets
- **Encounter Class**: IMP, ACUTE, NONAC, SS (from ActCode)
- **Location Type**: HSLOC codes for inpatient locations
- **Specimen Type**: SNOMED 119297000 (Blood specimen)
- **Blood Culture Code**: LOINC 600-7

### Organism SNOMED Codes (for testing)
| Organism | SNOMED Code | HOB Eligible |
|----------|-------------|--------------|
| Staphylococcus aureus | 3092008 | Yes |
| Escherichia coli | 112283007 | Yes |
| Candida albicans | 53326005 | Yes (fungemia) |
| S. epidermidis | 60875001 | No (skin commensal) |

## Test Scenarios

### Positive HOB Cases
1. **Day 4 S. aureus**: Basic HOB positive case
2. **Day 5 Candida**: Fungemia HOB case

### Exclusion Cases
3. **Matching COB**: Same organism on day 2 (COB) and day 5 (excluded)
4. **Non-matching COB**: Different organisms - day 5 qualifies as HOB

## Measurement Period
- **Start**: 2025-01-01
- **End**: 2025-01-31

## CQL Initial Population

The CQL module `NHSNAcuteCareHospitalMonthlyInitialPopulation1` evaluates:
- Qualifying encounters during measurement period
- Valid patient hospital locations
- Encounter status (in-progress, finished, triaged, onleave, entered-in-error)

**Note**: The CQL does NOT calculate HOB. It collects data for downstream applications to evaluate HOB events.

## Expected Results

For MADiE testing, all HOB test cases should:
- Meet Initial Population criteria: `count: 1`
- HOB evaluation is performed by downstream application
