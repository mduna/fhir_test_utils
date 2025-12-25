# AUR Protocol Summary

## Source Document
NHSN Patient-level Antimicrobial Use and Resistance (AUR) Surveillance Module Protocol

## Protocol Overview
The Patient-level AUR Module consists of two surveillance options:
1. **Antimicrobial Use (AU) Option** - Tracks antimicrobial administration (days of therapy)
2. **Antimicrobial Resistance (AR) Option** - Tracks resistant organism events from cultures

---

## Part 1: Antimicrobial Use (AU) Option

### Event Definition
**Antimicrobial Days (Days of Therapy)**: The aggregate sum of days for which any amount of a specific antimicrobial agent was administered to individual patients.

### Initial Population
All encounters for patients of any age in:
- Emergency Department (ED)
- Pediatric Emergency Department
- 24-hour Observation Area
- Inpatient locations

### Eligible Routes of Administration
| Route | Definition |
|-------|------------|
| Intravenous (IV) | Intravascular route beginning with a vein |
| Intramuscular (IM) | Route beginning within a muscle |
| Digestive Tract | Route anywhere from mouth through rectum |
| Respiratory Tract | Route within respiratory tract including oropharynx/nasopharynx |

**Excluded**: Topical, antibiotic locks, intraperitoneal, intrapleural, intraventricular, irrigation

### Key Calculation Rules
1. One patient contributes only **one antimicrobial day per drug per calendar day** regardless of number of doses
2. If patient transfers between locations, antimicrobial day is attributed to **both locations**
3. For facility-wide inpatient (FacWideIN), patient contributes only **one day per drug per calendar day**
4. Admissions counted when patient arrives in NHSN-designated inpatient location

### Denominators
- **Days Present**: Days patient is at risk for antimicrobial exposure in a location
- **Admissions**: Number of patients admitted to inpatient locations

### Primary Metrics
- **Rate of Antimicrobial Days per 1,000 Days Present** (location-specific and facility-wide)
- **SAAR (Standardized Antimicrobial Administration Ratio)**: Observed AU / Predicted AU

---

## Part 2: Antimicrobial Resistance (AR) Option

### Event Definition
An AR event occurs when:
1. Positive culture grows eligible AR organism, OR
2. Eligible AR organism detected through culture-independent rapid diagnostics
AND at least 1 drug or AR gene was tested

### Specimen Sources
- Blood
- CSF (Cerebrospinal Fluid)
- Urine
- Lower Respiratory
- Skin/Soft Tissue

### Onset Classification
- **Hospital-Onset (HO)**: Culture collected on hospital day 4+ (admission = day 1)
- **Community-Onset (CO)**: Culture collected on hospital day 1-3

### Deduplication Rules
**Invasive specimens**: 14 days between positive cultures for same organism
**Non-invasive specimens**: First isolate per patient, per month, per organism

### Same-Day Duplicate Selection
1. CSF over blood (invasive)
2. Lower respiratory over urine (non-invasive)
3. Eliminate isolates without susceptibility results
4. Keep most resistant isolate (NS > R > I > S-DD > S > NA)

### Key Phenotype Definitions
| Phenotype | Code | Definition |
|-----------|------|------------|
| MRSA | MRSA_AR | S. aureus resistant to oxacillin or cefoxitin |
| CRE | CREall_AR | E. coli, Klebsiella, or Enterobacter resistant to carbapenems |
| VRE | VREgeneral_AR | Enterococcus resistant to vancomycin |
| MDR P. aeruginosa | MDR_PA_AR | P. aeruginosa I/R to drugs in 3+ of 6 categories |
| CR Acinetobacter | carbNS_Acine_AR | Acinetobacter I/R to imipenem, meropenem, or doripenem |

### Primary Metrics
- **Incidence Rate**: HO events per patient days
- **Prevalence Rate**: CO events per admissions/encounters
- **% Susceptible (%S)**: Susceptible isolates / Total tested
- **SRIR (Standardized Resistant Infection Ratio)**: Observed resistant / Predicted resistant
- **pSIR (Pathogen-specific SIR)**: Observed pathogen / Predicted pathogen

---

## Data Requirements

### Required FHIR Resources
| Resource | Profile | Key Elements |
|----------|---------|--------------|
| Patient | qicore-patient | DOB, gender, race, ethnicity |
| Encounter | qicore-encounter | Class, period, location, status |
| Location | qicore-location | CDC Location code (HSLOC) |
| MedicationAdministration | qicore-medicationadministration | Medication, route, effectiveDateTime (AU) |
| MedicationRequest | qicore-medicationrequest | Medication, route, authoredOn (AU proxy) |
| Observation | qicore-observation-lab | Culture result, susceptibility (AR) |
| DiagnosticReport | qicore-diagnosticreport-lab | Culture report, specimen (AR) |
| Specimen | us-core-specimen | Type, collection datetime (AR) |
| Coverage | qicore-coverage | Payer information |

### Key Value Sets / Codes

#### Antimicrobial Medications (RxNorm) - Sample
| Medication | RxNorm Code | Category |
|------------|-------------|----------|
| Meropenem | 1722939 | Carbapenem |
| Vancomycin | 1664986 | Glycopeptide |
| Ceftriaxone | 309090 | Cephalosporin 3rd gen |
| Piperacillin-Tazobactam | 1659149 | Beta-lactam/BLI |
| Ciprofloxacin | 309309 | Fluoroquinolone |
| Amikacin | 1665021 | Aminoglycoside |

#### Route of Administration (SNOMED)
| Route | SNOMED Code | Display |
|-------|-------------|---------|
| Intravenous | 47625008 | Intravenous route |
| Intramuscular | 78421000 | Intramuscular route |
| Oral | 26643006 | Oral route |
| Inhalation | 447694001 | Respiratory tract route |

#### Organisms (SNOMED)
| Organism | SNOMED Code | Display |
|----------|-------------|---------|
| Staphylococcus aureus | 3092008 | Staphylococcus aureus |
| Escherichia coli | 112283007 | Escherichia coli |
| Klebsiella pneumoniae | 56415008 | Klebsiella pneumoniae |
| Pseudomonas aeruginosa | 52499004 | Pseudomonas aeruginosa |
| Enterococcus faecalis | 78065002 | Enterococcus faecalis |
| Enterococcus faecium | 90272000 | Enterococcus faecium |
| Candida albicans | 53326005 | Candida albicans |
| Acinetobacter baumannii | 91288006 | Acinetobacter baumannii |

#### Susceptibility Results (SNOMED)
| Result | SNOMED Code | Display |
|--------|-------------|---------|
| Susceptible | 131196009 | Susceptible |
| Resistant | 30714006 | Resistant |
| Intermediate | 11896004 | Intermediate |

#### Specimen Types (SNOMED)
| Specimen | SNOMED Code | Display |
|----------|-------------|---------|
| Blood | 119297000 | Blood specimen |
| Urine | 122575003 | Urine specimen |
| CSF | 258450006 | Cerebrospinal fluid specimen |
| Sputum | 119334006 | Sputum specimen |

#### CDC Location Codes (HSLOC)
| Location | HSLOC Code | Display |
|----------|------------|---------|
| Medical Critical Care | 1027-2 | Medical Critical Care |
| Surgical Critical Care | 1030-6 | Surgical Critical Care |
| Medical Ward | 1060-3 | Medical Ward |
| Surgical Ward | 1072-8 | Surgical Ward |
| Emergency Department | 1108-0 | Emergency Department |
| Neonatal Critical Care (Level III) | 1040-5 | Neonatal Critical Care |

---

## Test Scenarios

### AU Option Test Cases
1. Basic inpatient with IV antimicrobial administration
2. Multiple antimicrobials on same day (each counted separately)
3. Same antimicrobial multiple doses same day (counts as 1 antimicrobial day)
4. Patient transfer between locations (antimicrobial day to both locations)
5. ED encounter with oral antimicrobial
6. Multi-day stay spanning two months
7. Medication order (proxy when administration not available)

### AR Option Test Cases
1. Hospital-onset MRSA bacteremia (blood culture day 4+)
2. Community-onset E. coli UTI (urine culture day 1-3)
3. Carbapenem-resistant Klebsiella pneumoniae (CRE)
4. Vancomycin-resistant Enterococcus (VRE)
5. Same-day duplicate cultures (deduplication test)
6. 14-day window test (invasive specimen deduplication)
7. MDR Pseudomonas aeruginosa
8. Negative culture (no event)

---

## Hospital Day Calculation

| Admission Date | Day 1 | Day 2 | Day 3 | Day 4 (HO eligible) |
|----------------|-------|-------|-------|---------------------|
| 2025-01-02 | Jan 2 | Jan 3 | Jan 4 | **Jan 5** |
| 2025-01-03 | Jan 3 | Jan 4 | Jan 5 | **Jan 6** |
