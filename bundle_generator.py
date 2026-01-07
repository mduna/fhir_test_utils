#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FHIR Bundle Generator

A reusable class for generating FHIR R4 transaction bundles for test cases.
Resources conform to QICore 6.0.0 profiles.
"""

import uuid
import json
from typing import Dict, List, Any, Optional

from .qicore_profiles import (
    QICORE_PROFILES, USCORE_PROFILES, CQFM_PROFILES, FHIR_EXTENSIONS,
    get_profile_url, get_extension_url
)
from .code_systems import CODE_SYSTEMS, COMMON_CODES, create_coding


class FHIRBundleGenerator:
    """
    Generates FHIR R4 transaction bundles for measure test cases.

    All resources are created with QICore 6.0.0 profiles.

    Usage:
        gen = FHIRBundleGenerator("TestCaseName")
        gen.add_patient()
        enc_id = gen.add_encounter(start="2022-01-05T08:00:00.000Z", end="2022-01-10T12:00:00.000Z")
        gen.add_condition(enc_id)
        gen.save("output/test_case.json")
    """

    MADIE_BASE_URL = "https://madie.cms.gov"

    def __init__(self, test_case_name: str, patient_id: str = None):
        """
        Initialize the bundle generator.

        Args:
            test_case_name: Name of the test case (used in patient name)
            patient_id: Optional patient ID (auto-generated if not provided)
        """
        self.test_case_name = test_case_name
        self.patient_id = patient_id or str(uuid.uuid4())
        self.bundle = {
            "resourceType": "Bundle",
            "id": str(uuid.uuid4()).replace("-", "")[:24],
            "type": "transaction",
            "entry": []
        }

    def _generate_id(self) -> str:
        """Generate a new UUID for a resource"""
        return str(uuid.uuid4())

    def _add_entry(self, resource: Dict, resource_id: str = None) -> str:
        """
        Add a resource entry to the bundle.

        Args:
            resource: The FHIR resource dictionary
            resource_id: Optional resource ID (extracted from resource if not provided)

        Returns:
            The resource ID
        """
        if resource_id is None:
            resource_id = resource.get("id", self._generate_id())

        resource_type = resource["resourceType"]

        entry = {
            "fullUrl": f"{self.MADIE_BASE_URL}/{resource_type}/{resource_id}",
            "resource": resource,
            "request": {
                "method": "PUT",
                "url": f"{resource_type}/{resource_id}"
            }
        }

        self.bundle["entry"].append(entry)
        return resource_id

    def _build_encounter_locations(self,
                                   location_id: str = None,
                                   locations: List[Dict] = None,
                                   encounter_id: str = None,
                                   default_start: str = None,
                                   default_end: str = None) -> List[Dict]:
        """
        Build the location array for an Encounter resource.

        Supports both simple single-location (via location_id) and complex
        multi-location scenarios with periods (via locations list).

        Args:
            location_id: Simple single location ID (backward compatible)
            locations: List of location dicts, each containing:
                       - location_id: Reference to Location resource (required)
                       - display: Display name (optional)
                       - period: Dict with 'start' and 'end' (optional)
                       - physicalType: Dict with 'code' and 'display' (optional)
                       - status: Location status (optional, defaults to 'active')
            encounter_id: The encounter ID for generating default location refs
            default_start: Default period start
            default_end: Default period end

        Returns:
            List of FHIR Encounter.location entries
        """
        # If locations list is provided, use it (multi-location scenario)
        if locations:
            encounter_locations = []
            for loc in locations:
                loc_entry = {
                    "location": {
                        "reference": f"Location/{loc['location_id']}"
                    },
                    "status": loc.get("status", "active")
                }

                # Add display if provided
                if loc.get("display"):
                    loc_entry["location"]["display"] = loc["display"]

                # Add period if provided
                if loc.get("period"):
                    loc_entry["period"] = loc["period"]

                # Add physicalType if provided
                if loc.get("physicalType"):
                    physical_type = loc["physicalType"]
                    loc_entry["physicalType"] = {
                        "coding": [{
                            "system": CODE_SYSTEMS["LocationPhysicalType"],
                            "code": physical_type.get("code", "ro"),
                            "display": physical_type.get("display", "Room")
                        }],
                        "text": physical_type.get("display", "Room")
                    }

                encounter_locations.append(loc_entry)

            return encounter_locations

        # Otherwise, use simple single-location (backward compatible)
        return [
            {
                "location": {
                    "reference": f"Location/{location_id if location_id else 'default-loc-' + encounter_id[:8]}"
                },
                "status": "active",
                "physicalType": {
                    "coding": [{
                        "system": CODE_SYSTEMS["LocationPhysicalType"],
                        "code": "ro",
                        "display": "Room"
                    }]
                },
                "period": {"start": default_start, "end": default_end}
            }
        ]

    # =========================================================================
    # PATIENT
    # =========================================================================

    def add_patient(self,
                    given_name: str = None,
                    family_name: str = None,
                    gender: str = "male",
                    birth_date: str = "1980-01-01",
                    race_code: str = "2028-9",
                    race_display: str = "Asian",
                    ethnicity_code: str = "2186-5",
                    ethnicity_display: str = "Not Hispanic or Latino",
                    deceased_datetime: str = None) -> str:
        """
        Add a Patient resource with US Core race/ethnicity extensions.

        Returns:
            The patient ID
        """
        if given_name is None:
            given_name = self.test_case_name
        if family_name is None:
            family_name = "TestPatient"

        # Add General Practitioner first (referenced by Patient)
        gp_id = "gp-001"
        gp_practitioner = {
            "resourceType": "Practitioner",
            "id": gp_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "GeneralPractitioner", "given": ["Dr"]}]
        }
        self._add_entry(gp_practitioner, gp_id)

        patient = {
            "resourceType": "Patient",
            "id": self.patient_id,
            "meta": {"profile": [QICORE_PROFILES["Patient"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["us-core-race"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": race_code,
                                "display": race_display,
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": race_display}
                    ]
                },
                {
                    "url": FHIR_EXTENSIONS["us-core-ethnicity"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": ethnicity_code,
                                "display": ethnicity_display,
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": ethnicity_display}
                    ]
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [{"system": CODE_SYSTEMS["IdentifierType"], "code": "MR"}]
                    },
                    "system": f"{self.MADIE_BASE_URL}/",
                    "value": self.patient_id
                }
            ],
            "active": True,
            "name": [{"use": "official", "family": family_name, "given": [given_name]}],
            "telecom": [
                {"system": "phone", "value": "555-123-4567", "use": "home"},
                {"system": "email", "value": "patient@example.com", "use": "home"}
            ],
            "gender": gender,
            "birthDate": birth_date,
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "line": ["123 Main Street"],
                    "city": "Boston",
                    "state": "MA",
                    "postalCode": "02101",
                    "country": "USA"
                }
            ],
            "maritalStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["MaritalStatus"],
                    "code": "M",
                    "display": "Married"
                }]
            },
            "multipleBirthInteger": 2,
            "contact": [
                {
                    "relationship": [{
                        "coding": [{
                            "system": CODE_SYSTEMS["ContactRelationship"],
                            "code": "N",
                            "display": "Next-of-Kin"
                        }]
                    }],
                    "name": {"family": "Contact", "given": ["Emergency"]},
                    "telecom": [{"system": "phone", "value": "555-987-6543", "use": "home"}]
                }
            ],
            "communication": [
                {
                    "language": {
                        "coding": [{
                            "system": CODE_SYSTEMS["Language"],
                            "code": "en",
                            "display": "English"
                        }]
                    },
                    "preferred": True
                }
            ],
            "photo": [
                {
                    "contentType": "image/png",
                    "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
                }
            ],
            "generalPractitioner": [{"reference": f"Practitioner/{gp_id}"}],
            "managingOrganization": {"reference": "Organization/managing-org-001"},
            "link": [{"other": {"reference": "Patient/related-patient-001"}, "type": "seealso"}]
        }

        # Only add deceasedDateTime if patient is actually deceased
        if deceased_datetime:
            patient["deceasedDateTime"] = deceased_datetime

        self._add_entry(patient, self.patient_id)
        return self.patient_id

    # =========================================================================
    # ENCOUNTER
    # =========================================================================

    def add_encounter(self,
                      start: str,
                      end: str,
                      status: str = "finished",
                      class_code: str = "AMB",
                      class_display: str = None,
                      type_coding: List[Dict] = None,
                      location_id: str = None,
                      locations: List[Dict] = None,
                      discharge_disposition: Dict = None) -> str:
        """
        Add an Encounter resource.

        Args:
            start: Period start datetime (ISO format)
            end: Period end datetime (ISO format)
            status: Encounter status (finished, in-progress, etc.)
            class_code: Encounter class code (IMP, EMER, AMB, etc.)
            class_display: Display text for class (auto-mapped if not provided)
            type_coding: List of type codings [{system, code, display}]
            location_id: Optional single location ID to reference (simple case)
            locations: Optional list of location dicts for multiple locations with periods.
                       Each dict can contain:
                       - location_id: Reference to Location resource (required)
                       - display: Display name for the location (optional)
                       - period: Dict with 'start' and 'end' datetimes (optional)
                       - physicalType: Dict with 'code' and 'display' (optional)
                       - status: Location status like 'active' (optional, defaults to 'active')
            discharge_disposition: Optional discharge disposition coding dict

        Returns:
            The encounter ID
        """
        encounter_id = self._generate_id()

        # Default type coding if none specified (required by QICore 6.0.0)
        if type_coding is None:
            type_coding = [{
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "281036007",
                "display": "Follow-up consultation (procedure)"
            }]

        # Map class codes to proper display values
        class_display_map = {
            "IMP": "inpatient encounter",
            "ACUTE": "inpatient acute",
            "NONAC": "inpatient non-acute",
            "SS": "short stay",
            "EMER": "emergency",
            "OBSENC": "observation encounter",
            "AMB": "ambulatory"
        }
        if class_display is None:
            class_display = class_display_map.get(class_code, "ambulatory")

        encounter = {
            "resourceType": "Encounter",
            "id": encounter_id,
            "meta": {"profile": [QICORE_PROFILES["Encounter"]]},
            "identifier": [
                {"system": f"{self.MADIE_BASE_URL}/encounter-id", "value": encounter_id}
            ],
            "status": status,
            "statusHistory": [
                {"status": "arrived", "period": {"start": start, "end": start}}
            ],
            "class": {
                "system": CODE_SYSTEMS["ActCode"],
                "code": class_code,
                "display": class_display
            },
            "classHistory": [
                {
                    "class": {
                        "system": CODE_SYSTEMS["ActCode"],
                        "code": class_code,
                        "display": class_display
                    },
                    "period": {"start": start, "end": end}
                }
            ],
            "type": [{"coding": type_coding}],
            "serviceType": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "394802001",
                    "display": "General medicine"
                }]
            },
            "priority": {
                "coding": [{
                    "system": CODE_SYSTEMS["ActPriority"],
                    "code": "R",
                    "display": "routine"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "period": {"start": start, "end": end},
            "length": {
                "value": 5,
                "unit": "days",
                "system": CODE_SYSTEMS["UCUM"],
                "code": "d"
            },
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{encounter_id[:8]}"}],
            "diagnosis": [
                {
                    "condition": {"reference": f"Condition/diag-{encounter_id[:8]}"},
                    "use": {
                        "coding": [{
                            "system": CODE_SYSTEMS["DiagnosisRole"],
                            "code": "AD",
                            "display": "Admission diagnosis"
                        }]
                    },
                    "rank": 1
                }
            ],
            "account": [{"reference": f"Account/acct-{encounter_id[:8]}"}],
            "hospitalization": {
                "dischargeDisposition": discharge_disposition if discharge_disposition else {
                    "coding": [{
                        "system": CODE_SYSTEMS["DischargeDisposition"],
                        "code": "home",
                        "display": "Home"
                    }]
                }
            },
            "partOf": {"reference": f"Encounter/parent-{encounter_id[:8]}"},
            "location": self._build_encounter_locations(
                location_id=location_id,
                locations=locations,
                encounter_id=encounter_id,
                default_start=start,
                default_end=end
            )
        }

        self._add_entry(encounter, encounter_id)
        return encounter_id

    # =========================================================================
    # LOCATION
    # =========================================================================

    def add_location(self, location_type: Dict = None) -> str:
        """
        Add a Location resource.

        Args:
            location_type: Type coding {system, code, display}

        Returns:
            The location ID
        """
        location_id = self._generate_id()

        if location_type is None:
            location_type = {
                "system": CODE_SYSTEMS["HSLOC"],
                "code": "1025-6",
                "display": "Trauma Critical Care"
            }

        location = {
            "resourceType": "Location",
            "id": location_id,
            "meta": {"profile": [QICORE_PROFILES["Location"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["location-boundary-geojson"],
                    "valueAttachment": {"contentType": "application/geo+json"}
                }
            ],
            "status": "active",
            "operationalStatus": {
                "system": CODE_SYSTEMS["LocationOperationalStatus"],
                "code": "O",
                "display": "Occupied"
            },
            "name": location_type.get("display", "Hospital Location"),
            "alias": ["Main Unit", "Primary Care Unit"],
            "description": "Hospital location for patient care",
            "mode": "instance",
            "type": [{"coding": [location_type]}],
            "telecom": [{"system": "phone", "value": "555-123-4567", "use": "work"}],
            "address": {
                "use": "work",
                "type": "physical",
                "line": ["123 Hospital Drive"],
                "city": "Boston",
                "state": "MA",
                "postalCode": "02101",
                "country": "USA"
            },
            "physicalType": {
                "coding": [{
                    "system": CODE_SYSTEMS["LocationPhysicalType"],
                    "code": "ro",
                    "display": "Room"
                }]
            },
            "position": {"longitude": -71.0589, "latitude": 42.3601},
            "managingOrganization": {"reference": "Organization/hospital-org-123"},
            "partOf": {"reference": "Location/parent-location-001"},
            "hoursOfOperation": [
                {"daysOfWeek": ["mon", "tue", "wed", "thu", "fri"], "allDay": True}
            ],
            "availabilityExceptions": "Closed on holidays",
            "endpoint": [{"reference": "Endpoint/location-endpoint-001"}]
        }

        self._add_entry(location, location_id)
        return location_id

    # =========================================================================
    # CONDITION
    # =========================================================================

    def add_condition(self,
                      encounter_id: str,
                      code: Dict = None,
                      clinical_status: str = "active",
                      verification_status: str = "confirmed",
                      onset_datetime: str = "2022-01-05T10:00:00.000Z") -> str:
        """
        Add a Condition resource using ConditionProblemsHealthConcerns profile.

        Args:
            encounter_id: Reference to the encounter
            code: Condition code {system, code, display}
            clinical_status: Clinical status (active, resolved, etc.)
            verification_status: Verification status (confirmed, etc.)
            onset_datetime: Onset datetime

        Returns:
            The condition ID
        """
        condition_id = self._generate_id()

        if code is None:
            code = {
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "44054006",
                "display": "Diabetes mellitus type 2 (disorder)"
            }

        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": {"profile": [QICORE_PROFILES["ConditionProblemsHealthConcerns"]]},
            "clinicalStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["ConditionClinicalStatus"],
                    "code": clinical_status
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["ConditionVerificationStatus"],
                    "code": verification_status
                }]
            },
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ConditionCategory"],
                        "code": "problem-list-item",
                        "display": "Problem List Item"
                    }]
                }
            ],
            "severity": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "24484000",
                    "display": "Severe"
                }]
            },
            "code": {"coding": [code]},
            "bodySite": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "38266002",
                        "display": "Entire body as a whole"
                    }]
                }
            ],
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "onsetDateTime": onset_datetime,
            "stage": [
                {
                    "summary": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "786005",
                            "display": "Clinical stage I"
                        }]
                    }
                }
            ],
            "evidence": [
                {
                    "code": [
                        {
                            "coding": [{
                                "system": CODE_SYSTEMS["SNOMED"],
                                "code": "169876006",
                                "display": "Blood test evidence"
                            }]
                        }
                    ]
                }
            ],
            "note": [{"text": "Patient condition documented during encounter"}]
        }

        self._add_entry(condition, condition_id)
        return condition_id

    # =========================================================================
    # COVERAGE
    # =========================================================================

    def add_coverage(self, start: str, end: str) -> str:
        """
        Add a Coverage resource.

        Args:
            start: Coverage period start
            end: Coverage period end

        Returns:
            The coverage ID
        """
        coverage_id = self._generate_id()

        coverage = {
            "resourceType": "Coverage",
            "id": coverage_id,
            "meta": {"profile": [QICORE_PROFILES["Coverage"]]},
            "status": "active",
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["ActCode"],
                    "code": "HIP",
                    "display": "health insurance plan policy"
                }]
            },
            "policyHolder": {"reference": f"Patient/{self.patient_id}"},
            "subscriber": {"reference": f"Patient/{self.patient_id}"},
            "subscriberId": "MBR-12345",
            "beneficiary": {"reference": f"Patient/{self.patient_id}"},
            "dependent": "01",
            "relationship": {
                "coding": [{
                    "system": CODE_SYSTEMS["SubscriberRelationship"],
                    "code": "self",
                    "display": "Self"
                }]
            },
            "period": {"start": start, "end": end},
            "payor": [{"reference": "Organization/payor-org-123"}],
            "class": [
                {
                    "type": {
                        "coding": [{
                            "system": CODE_SYSTEMS["CoverageClass"],
                            "code": "plan",
                            "display": "Plan"
                        }]
                    },
                    "value": "PLAN-001",
                    "name": "Premium Health Plan"
                }
            ],
            "order": 1,
            "network": "Preferred Provider Network",
            "subrogation": True,
            "contract": [{"reference": "Contract/contract-123"}]
        }

        self._add_entry(coverage, coverage_id)
        return coverage_id

    # =========================================================================
    # OBSERVATION
    # =========================================================================

    def add_observation(self,
                        encounter_id: str,
                        category: str = "laboratory",
                        code: Dict = None,
                        value: float = 100,
                        unit: str = "mg/dL",
                        effective_datetime: str = None) -> str:
        """
        Add an Observation resource.

        Args:
            encounter_id: Reference to the encounter
            category: Observation category (laboratory, vital-signs, etc.)
            code: Observation code {system, code, display}
            value: Numeric value
            unit: Unit of measure
            effective_datetime: Effective datetime

        Returns:
            The observation ID
        """
        observation_id = self._generate_id()
        specimen_id = self._generate_id()

        if code is None:
            if category == "laboratory":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "2339-0",
                    "display": "Glucose [Mass/volume] in Blood"
                }
            else:
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "8867-4",
                    "display": "Heart rate"
                }

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        # Select appropriate profile based on category
        if category == "laboratory":
            profile = QICORE_PROFILES["ObservationLab"]
        elif category == "vital-signs":
            profile = QICORE_PROFILES["ObservationClinicalResult"]
        else:
            profile = QICORE_PROFILES["SimpleObservation"]

        # Add Specimen resource for the observation
        specimen = {
            "resourceType": "Specimen",
            "id": specimen_id,
            "meta": {"profile": [USCORE_PROFILES["Specimen"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "119297000",
                    "display": "Blood specimen"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "receivedTime": effective_datetime,
            "collection": {"collectedDateTime": effective_datetime}
        }
        self._add_entry(specimen, specimen_id)

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [profile]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["observation-bodyPosition"],
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "33586001",
                            "display": "Sitting position"
                        }]
                    }
                }
            ],
            "partOf": [{"reference": f"Procedure/proc-{observation_id[:8]}"}],
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": category,
                        "display": category.replace("-", " ").title()
                    }]
                }
            ],
            "code": {"coding": [code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": effective_datetime,
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": CODE_SYSTEMS["UCUM"],
                "code": unit
            },
            "interpretation": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationInterpretation"],
                        "code": "N",
                        "display": "Normal"
                    }]
                }
            ],
            "bodySite": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "368209003",
                    "display": "Right upper arm structure"
                }]
            },
            "method": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "129300006",
                    "display": "Measurement - action"
                }]
            },
            "specimen": {"reference": f"Specimen/{specimen_id}"},
            "referenceRange": [
                {
                    "low": {"value": 70, "unit": unit, "system": CODE_SYSTEMS["UCUM"], "code": unit},
                    "high": {"value": 140, "unit": unit, "system": CODE_SYSTEMS["UCUM"], "code": unit},
                    "type": {
                        "coding": [{
                            "system": CODE_SYSTEMS["ReferenceRangeMeaning"],
                            "code": "normal",
                            "display": "Normal Range"
                        }]
                    }
                }
            ],
            "hasMember": [{"reference": f"Observation/member-{observation_id[:8]}"}],
            "derivedFrom": [{"reference": f"Observation/derived-{observation_id[:8]}"}],
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LOINC"],
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mmHg",
                        "system": CODE_SYSTEMS["UCUM"],
                        "code": "mm[Hg]"
                    }
                }
            ]
        }

        self._add_entry(observation, observation_id)
        return observation_id

    def add_observation_data_absent(self,
                                     encounter_id: str,
                                     category: str = "laboratory",
                                     code: Dict = None,
                                     effective_datetime: str = None) -> str:
        """
        Add an Observation resource with dataAbsentReason (no value).

        Args:
            encounter_id: Reference to the encounter
            category: Observation category
            code: Observation code
            effective_datetime: Effective datetime

        Returns:
            The observation ID
        """
        observation_id = self._generate_id()

        if code is None:
            if category == "laboratory":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "2339-0",
                    "display": "Glucose [Mass/volume] in Blood"
                }
            else:
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "8867-4",
                    "display": "Heart rate"
                }

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        if category == "laboratory":
            profile = QICORE_PROFILES["ObservationLab"]
        elif category == "vital-signs":
            profile = QICORE_PROFILES["ObservationClinicalResult"]
        else:
            profile = QICORE_PROFILES["SimpleObservation"]

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [profile]},
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": category,
                        "display": category.replace("-", " ").title()
                    }]
                }
            ],
            "code": {"coding": [code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "dataAbsentReason": {
                "coding": [{
                    "system": CODE_SYSTEMS["DataAbsentReason"],
                    "code": "not-performed",
                    "display": "Not Performed"
                }]
            }
        }

        self._add_entry(observation, observation_id)
        return observation_id

    def add_blood_pressure(self,
                           encounter_id: str,
                           systolic: float,
                           diastolic: float,
                           effective_datetime: str) -> str:
        """
        Add a Blood Pressure Observation using US Core Vital Signs Profile.

        Uses the panel code (85354-9) with systolic and diastolic as components.
        QI-Core references US Core Vital Signs Profile for vital signs observations.

        Args:
            encounter_id: Reference to the encounter
            systolic: Systolic blood pressure value (mmHg)
            diastolic: Diastolic blood pressure value (mmHg)
            effective_datetime: Effective datetime

        Returns:
            The observation ID
        """
        observation_id = self._generate_id()

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [USCORE_PROFILES["VitalSigns"]]},
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }],
                    "text": "Vital Signs"
                }
            ],
            "code": {
                "coding": [{
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "85354-9",
                    "display": "Blood pressure panel with all children optional"
                }],
                "text": "Blood pressure systolic and diastolic"
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LOINC"],
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }],
                        "text": "Systolic blood pressure"
                    },
                    "valueQuantity": {
                        "value": systolic,
                        "unit": "mmHg",
                        "system": CODE_SYSTEMS["UCUM"],
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LOINC"],
                            "code": "8462-4",
                            "display": "Diastolic blood pressure"
                        }],
                        "text": "Diastolic blood pressure"
                    },
                    "valueQuantity": {
                        "value": diastolic,
                        "unit": "mmHg",
                        "system": CODE_SYSTEMS["UCUM"],
                        "code": "mm[Hg]"
                    }
                }
            ]
        }

        self._add_entry(observation, observation_id)
        return observation_id

    def add_blood_culture(self,
                          encounter_id: str,
                          organism_code: str,
                          organism_display: str,
                          collected_datetime: str,
                          specimen_id: str = None) -> tuple:
        """
        Add a blood culture observation with organism result.

        This creates:
        1. A Specimen resource (blood specimen)
        2. An Observation resource with organism identification

        Args:
            encounter_id: Reference to the encounter
            organism_code: SNOMED code for the organism identified
            organism_display: Display name for the organism
            collected_datetime: Specimen collection datetime (ISO format)
            specimen_id: Optional specimen ID (auto-generated if not provided)

        Returns:
            Tuple of (observation_id, specimen_id)
        """
        observation_id = self._generate_id()
        if specimen_id is None:
            specimen_id = self._generate_id()

        # Add Specimen resource for blood specimen
        specimen = {
            "resourceType": "Specimen",
            "id": specimen_id,
            "meta": {"profile": [USCORE_PROFILES["Specimen"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "119297000",
                    "display": "Blood specimen"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "receivedTime": collected_datetime,
            "collection": {
                "collectedDateTime": collected_datetime
            }
        }
        self._add_entry(specimen, specimen_id)

        # Add Blood Culture Observation with organism result
        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [QICORE_PROFILES["ObservationLab"]]},
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": "laboratory",
                        "display": "Laboratory"
                    }]
                }
            ],
            "code": {
                "coding": [{
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "600-7",
                    "display": "Bacteria identified in Blood by Culture"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": collected_datetime,
            "issued": collected_datetime,
            "valueCodeableConcept": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": organism_code,
                    "display": organism_display
                }]
            },
            "specimen": {"reference": f"Specimen/{specimen_id}"},
            "interpretation": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationInterpretation"],
                        "code": "POS",
                        "display": "Positive"
                    }]
                }
            ]
        }

        self._add_entry(observation, observation_id)
        return observation_id, specimen_id

    # =========================================================================
    # MEDICATION ADMINISTRATION
    # =========================================================================

    def add_medication_administration(self,
                                       encounter_id: str,
                                       effective_start: str,
                                       effective_end: str,
                                       medication_code: Dict = None) -> str:
        """
        Add a MedicationAdministration resource.

        Args:
            encounter_id: Reference to the encounter
            effective_start: Effective period start
            effective_end: Effective period end
            medication_code: Medication code {system, code, display}

        Returns:
            The medication administration ID
        """
        med_admin_id = self._generate_id()
        practitioner_id = self._generate_id()
        device_id = self._generate_id()

        if medication_code is None:
            medication_code = {
                "system": CODE_SYSTEMS["RXNORM"],
                "code": "860975",
                "display": "insulin human, isophane 70 UNT/ML / insulin human, regular 30 UNT/ML Injectable Suspension"
            }

        # Add Practitioner for performer
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Nurse", "given": ["Admin"]}]
        }
        self._add_entry(practitioner, practitioner_id)

        # Add Device for administration
        device = {
            "resourceType": "Device",
            "id": device_id,
            "meta": {"profile": [QICORE_PROFILES["Device"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "468063009",
                    "display": "Infusion pump"
                }]
            },
            "patient": {"reference": f"Patient/{self.patient_id}"}
        }
        self._add_entry(device, device_id)

        medication_admin = {
            "resourceType": "MedicationAdministration",
            "id": med_admin_id,
            "meta": {"profile": [QICORE_PROFILES["MedicationAdministration"]]},
            "instantiates": ["http://example.org/fhir/PlanDefinition/insulin-protocol"],
            "partOf": [{"reference": f"Procedure/proc-{med_admin_id[:8]}"}],
            "status": "completed",
            "statusReason": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "373066001",
                        "display": "Yes"
                    }]
                }
            ],
            "category": {
                "coding": [{
                    "system": CODE_SYSTEMS["MedicationAdminCategory"],
                    "code": "inpatient",
                    "display": "Inpatient"
                }]
            },
            "medicationCodeableConcept": {"coding": [medication_code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "context": {"reference": f"Encounter/{encounter_id}"},
            "supportingInformation": [{"reference": f"Observation/obs-{med_admin_id[:8]}"}],
            "effectivePeriod": {"start": effective_start, "end": effective_end},
            "performer": [
                {
                    "actor": {"reference": f"Practitioner/{practitioner_id}"},
                    "function": {
                        "coding": [{
                            "system": CODE_SYSTEMS["MedicationAdminPerformFunction"],
                            "code": "performer",
                            "display": "Performer"
                        }]
                    }
                }
            ],
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{med_admin_id[:8]}"}],
            "request": {"reference": f"MedicationRequest/req-{med_admin_id[:8]}"},
            "device": [{"reference": f"Device/{device_id}"}],
            "note": [
                {
                    "authorString": "Nurse Admin",
                    "time": effective_start,
                    "text": "Patient tolerated medication well"
                }
            ],
            "dosage": {
                "text": "10 units subcutaneously",
                "site": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "368209003",
                        "display": "Right upper arm structure"
                    }]
                },
                "route": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "34206005",
                        "display": "Subcutaneous route"
                    }]
                },
                "method": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "422145002",
                        "display": "Inject"
                    }]
                },
                "dose": {
                    "value": 10,
                    "unit": "U",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "U"
                },
                "rateQuantity": {
                    "value": 1,
                    "unit": "mL/hour",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "mL/h"
                }
            }
        }

        self._add_entry(medication_admin, med_admin_id)
        return med_admin_id

    # =========================================================================
    # MEDICATION REQUEST
    # =========================================================================

    def add_medication_request(self,
                                encounter_id: str,
                                authored_on: str,
                                medication_code: Dict = None) -> str:
        """
        Add a MedicationRequest resource.

        Args:
            encounter_id: Reference to the encounter
            authored_on: Authored on datetime
            medication_code: Medication code {system, code, display}

        Returns:
            The medication request ID
        """
        med_request_id = self._generate_id()
        practitioner_id = self._generate_id()
        recorder_id = self._generate_id()

        if medication_code is None:
            medication_code = {
                "system": CODE_SYSTEMS["RXNORM"],
                "code": "860975",
                "display": "insulin human, isophane 70 UNT/ML / insulin human, regular 30 UNT/ML Injectable Suspension"
            }

        # Add Practitioner resource (requester)
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Smith", "given": ["John"]}]
        }
        self._add_entry(practitioner, practitioner_id)

        # Add Practitioner resource (recorder)
        recorder = {
            "resourceType": "Practitioner",
            "id": recorder_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Recorder", "given": ["Jane"]}]
        }
        self._add_entry(recorder, recorder_id)

        medication_request = {
            "resourceType": "MedicationRequest",
            "id": med_request_id,
            "meta": {"profile": [QICORE_PROFILES["MedicationRequest"]]},
            "status": "active",
            "statusReason": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "373066001",
                    "display": "Yes"
                }]
            },
            "intent": "order",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["MedicationRequestCategory"],
                        "code": "inpatient",
                        "display": "Inpatient"
                    }]
                }
            ],
            "priority": "routine",
            "reportedReference": {"reference": f"Practitioner/{practitioner_id}"},
            "medicationCodeableConcept": {"coding": [medication_code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "authoredOn": authored_on,
            "requester": {"reference": f"Practitioner/{practitioner_id}"},
            "recorder": {"reference": f"Practitioner/{recorder_id}"},
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{med_request_id[:8]}"}],
            "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/insulin-protocol"],
            "instantiatesUri": ["http://example.org/protocols/insulin"],
            "courseOfTherapyType": {
                "coding": [{
                    "system": CODE_SYSTEMS["MedicationRequestCourseOfTherapy"],
                    "code": "continuous",
                    "display": "Continuous long term therapy"
                }]
            },
            "dosageInstruction": [
                {
                    "sequence": 1,
                    "text": "10 units subcutaneously before breakfast",
                    "timing": {
                        "repeat": {
                            "frequency": 1,
                            "period": 1,
                            "periodUnit": "d",
                            "when": ["ACM"]
                        }
                    },
                    "route": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "34206005",
                            "display": "Subcutaneous route"
                        }]
                    },
                    "doseAndRate": [
                        {
                            "type": {
                                "coding": [{
                                    "system": CODE_SYSTEMS["DoseRateType"],
                                    "code": "ordered",
                                    "display": "Ordered"
                                }]
                            },
                            "doseQuantity": {
                                "value": 10,
                                "unit": "U",
                                "system": CODE_SYSTEMS["UCUM"],
                                "code": "U"
                            }
                        }
                    ]
                }
            ]
        }

        self._add_entry(medication_request, med_request_id)
        return med_request_id

    def add_medication_not_requested(self,
                                      encounter_id: str,
                                      authored_on: str,
                                      medication_code: Dict = None) -> str:
        """
        Add a MedicationNotRequested resource (doNotPerform=true).

        Args:
            encounter_id: Reference to the encounter
            authored_on: Authored on datetime
            medication_code: Medication code {system, code, display}

        Returns:
            The medication request ID
        """
        med_request_id = self._generate_id()
        practitioner_id = self._generate_id()
        recorder_id = self._generate_id()

        if medication_code is None:
            medication_code = {
                "system": CODE_SYSTEMS["RXNORM"],
                "code": "860975",
                "display": "insulin human, isophane 70 UNT/ML / insulin human, regular 30 UNT/ML Injectable Suspension"
            }

        # Add Practitioner resources
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Smith", "given": ["John"]}]
        }
        self._add_entry(practitioner, practitioner_id)

        recorder = {
            "resourceType": "Practitioner",
            "id": recorder_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Recorder", "given": ["NotReq"]}]
        }
        self._add_entry(recorder, recorder_id)

        medication_not_requested = {
            "resourceType": "MedicationRequest",
            "id": med_request_id,
            "meta": {"profile": [QICORE_PROFILES["MedicationNotRequested"]]},
            "status": "completed",
            "statusReason": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "183932001",
                    "display": "Procedure contraindicated (situation)"
                }]
            },
            "intent": "order",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["MedicationRequestCategory"],
                        "code": "inpatient",
                        "display": "Inpatient"
                    }]
                }
            ],
            "priority": "routine",
            "doNotPerform": True,
            "reportedReference": {"reference": f"Practitioner/{practitioner_id}"},
            "medicationCodeableConcept": {"coding": [medication_code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "authoredOn": authored_on,
            "requester": {"reference": f"Practitioner/{practitioner_id}"},
            "recorder": {"reference": f"Practitioner/{recorder_id}"},
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "183932001",
                        "display": "Procedure contraindicated (situation)"
                    }],
                    "text": "Medication not requested due to contraindication"
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-notreq-{med_request_id[:8]}"}],
            "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/negation-protocol"],
            "instantiatesUri": ["http://example.org/protocols/negation"],
            "courseOfTherapyType": {
                "coding": [{
                    "system": CODE_SYSTEMS["MedicationRequestCourseOfTherapy"],
                    "code": "acute",
                    "display": "Short course (acute) therapy"
                }]
            },
            "dosageInstruction": [
                {
                    "sequence": 1,
                    "text": "Medication not to be given - contraindicated",
                    "timing": {"repeat": {"frequency": 1, "period": 1, "periodUnit": "d"}}
                }
            ]
        }

        self._add_entry(medication_not_requested, med_request_id)
        return med_request_id

    # =========================================================================
    # PROCEDURE
    # =========================================================================

    def add_procedure(self,
                      encounter_id: str,
                      performed_start: str,
                      performed_end: str,
                      procedure_code: Dict = None) -> str:
        """
        Add a Procedure resource.

        Args:
            encounter_id: Reference to the encounter
            performed_start: Performed period start
            performed_end: Performed period end
            procedure_code: Procedure code {system, code, display}

        Returns:
            The procedure ID
        """
        procedure_id = self._generate_id()
        location_id = self._generate_id()

        if procedure_code is None:
            procedure_code = {
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "80146002",
                "display": "Appendectomy (procedure)"
            }

        # Add Location for procedure
        location = {
            "resourceType": "Location",
            "id": location_id,
            "meta": {"profile": [QICORE_PROFILES["Location"]]},
            "status": "active",
            "name": "Operating Room 1",
            "type": [{"coding": [{"system": CODE_SYSTEMS["RoleCode"], "code": "OR", "display": "Operating Room"}]}]
        }
        self._add_entry(location, location_id)

        procedure = {
            "resourceType": "Procedure",
            "id": procedure_id,
            "meta": {"profile": [QICORE_PROFILES["Procedure"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["procedure-approachBodyStructure"],
                    "valueReference": {"display": "Laparoscopic approach"}
                }
            ],
            "basedOn": [{"reference": f"ServiceRequest/sr-{procedure_id[:8]}"}],
            "partOf": [{"reference": f"Procedure/parent-{procedure_id[:8]}"}],
            "status": "completed",
            "category": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "387713003",
                    "display": "Surgical procedure"
                }]
            },
            "code": {"coding": [procedure_code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "performedPeriod": {"start": performed_start, "end": performed_end},
            "location": {"reference": f"Location/{location_id}"},
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "74400008",
                        "display": "Appendicitis"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{procedure_id[:8]}"}],
            "bodySite": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "66754008",
                        "display": "Appendix structure"
                    }]
                }
            ]
        }

        self._add_entry(procedure, procedure_id)
        return procedure_id

    # =========================================================================
    # DIAGNOSTIC REPORT
    # =========================================================================

    def add_diagnostic_report(self,
                               encounter_id: str,
                               effective_datetime: str = None,
                               report_code: Dict = None) -> str:
        """
        Add a DiagnosticReport Lab resource.

        Args:
            encounter_id: Reference to the encounter
            effective_datetime: Effective datetime
            report_code: Report code {system, code, display}

        Returns:
            The diagnostic report ID
        """
        report_id = self._generate_id()

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        if report_code is None:
            report_code = {
                "system": CODE_SYSTEMS["LOINC"],
                "code": "58410-2",
                "display": "CBC panel - Blood by Automated count"
            }

        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "meta": {"profile": [QICORE_PROFILES["DiagnosticReportLab"]]},
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["DiagnosticServiceSection"],
                        "code": "LAB",
                        "display": "Laboratory"
                    }]
                }
            ],
            "code": {"coding": [report_code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": effective_datetime
        }

        self._add_entry(diagnostic_report, report_id)
        return report_id

    def add_diagnostic_report_note(self,
                                    encounter_id: str,
                                    category: str = "RAD",
                                    effective_datetime: str = None) -> str:
        """
        Add a DiagnosticReport Note resource.

        Args:
            encounter_id: Reference to the encounter
            category: Category (RAD, PATH, CARD)
            effective_datetime: Effective datetime

        Returns:
            The diagnostic report ID
        """
        report_id = self._generate_id()

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        category_coding = []
        if category == "RAD":
            category_coding = [{"system": CODE_SYSTEMS["LOINC"], "code": "LP29684-5", "display": "Radiology"}]
        elif category == "PATH":
            category_coding = [{"system": CODE_SYSTEMS["LOINC"], "code": "LP7839-6", "display": "Pathology"}]
        elif category == "CARD":
            category_coding = [{"system": CODE_SYSTEMS["LOINC"], "code": "LP29708-2", "display": "Cardiology"}]

        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "meta": {"profile": [QICORE_PROFILES["DiagnosticReportNote"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["diagnosticReport-locationPerformed"],
                    "valueReference": {"display": "Radiology Department"}
                }
            ],
            "basedOn": [{"reference": f"ServiceRequest/sr-{report_id[:8]}"}],
            "status": "final",
            "category": [{"coding": category_coding}],
            "code": {
                "coding": [{"system": CODE_SYSTEMS["LOINC"], "code": "18748-4", "display": "Diagnostic imaging study"}]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": effective_datetime,
            "specimen": [{"reference": f"Specimen/spec-{report_id[:8]}"}],
            "result": [{"reference": f"Observation/obs-{report_id[:8]}"}],
            "conclusion": "No acute abnormality identified.",
            "conclusionCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "17621005",
                        "display": "Normal"
                    }]
                }
            ]
        }

        self._add_entry(diagnostic_report, report_id)
        return report_id

    def add_diagnostic_report_others(self,
                                      encounter_id: str,
                                      effective_datetime: str = None) -> str:
        """
        Add a DiagnosticReport Others resource (non-RAD/PATH/CARD category).

        Args:
            encounter_id: Reference to the encounter
            effective_datetime: Effective datetime

        Returns:
            The diagnostic report ID
        """
        report_id = self._generate_id()

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        diagnostic_report = {
            "resourceType": "DiagnosticReport",
            "id": report_id,
            "meta": {"profile": [QICORE_PROFILES["DiagnosticReportNote"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["diagnosticReport-locationPerformed"],
                    "valueReference": {"display": "General Medicine Department"}
                }
            ],
            "basedOn": [{"reference": f"ServiceRequest/sr-{report_id[:8]}"}],
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["DiagnosticServiceSection"],
                        "code": "OTH",
                        "display": "Other"
                    }]
                }
            ],
            "code": {
                "coding": [{"system": CODE_SYSTEMS["LOINC"], "code": "11488-4", "display": "Consult note"}]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": effective_datetime,
            "specimen": [{"reference": f"Specimen/spec-{report_id[:8]}"}],
            "result": [{"reference": f"Observation/obs-{report_id[:8]}"}],
            "conclusion": "General consultation completed.",
            "conclusionCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "17621005",
                        "display": "Normal"
                    }]
                }
            ]
        }

        self._add_entry(diagnostic_report, report_id)
        return report_id

    # =========================================================================
    # SERVICE REQUEST
    # =========================================================================

    def add_service_request(self,
                             encounter_id: str,
                             authored_on: str,
                             service_code: Dict = None) -> str:
        """
        Add a ServiceRequest resource.

        Args:
            encounter_id: Reference to the encounter
            authored_on: Authored on datetime
            service_code: Service code {system, code, display}

        Returns:
            The service request ID
        """
        service_request_id = self._generate_id()
        requester_id = self._generate_id()
        performer_id = self._generate_id()

        if service_code is None:
            service_code = {
                "system": CODE_SYSTEMS["LOINC"],
                "code": "24323-8",
                "display": "Comprehensive metabolic 2000 panel - Serum or Plasma"
            }

        # Add requester Practitioner
        requester = {
            "resourceType": "Practitioner",
            "id": requester_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Requester", "given": ["Dr"]}]
        }
        self._add_entry(requester, requester_id)

        # Add performer Practitioner
        performer = {
            "resourceType": "Practitioner",
            "id": performer_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Performer", "given": ["Lab"]}]
        }
        self._add_entry(performer, performer_id)

        service_request = {
            "resourceType": "ServiceRequest",
            "id": service_request_id,
            "meta": {"profile": [QICORE_PROFILES["ServiceRequest"]]},
            "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/lab-protocol"],
            "instantiatesUri": ["http://example.org/protocols/lab"],
            "basedOn": [{"reference": f"CarePlan/cp-{service_request_id[:8]}"}],
            "replaces": [{"reference": f"ServiceRequest/sr-old-{service_request_id[:8]}"}],
            "requisition": {
                "system": "http://example.org/requisition",
                "value": f"REQ-{service_request_id[:8]}"
            },
            "status": "active",
            "intent": "order",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "108252007",
                        "display": "Laboratory procedure"
                    }]
                }
            ],
            "priority": "routine",
            "code": {"coding": [service_code]},
            "orderDetail": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "373066001",
                        "display": "Yes"
                    }]
                }
            ],
            "quantityQuantity": {
                "value": 1,
                "unit": "test",
                "system": CODE_SYSTEMS["UCUM"],
                "code": "{test}"
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "occurrenceDateTime": authored_on,
            "asNeededBoolean": True,
            "authoredOn": authored_on,
            "requester": {"reference": f"Practitioner/{requester_id}"},
            "performerType": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "61246008",
                    "display": "Laboratory medicine specialist"
                }]
            },
            "performer": [{"reference": f"Practitioner/{performer_id}"}],
            "locationCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["RoleCode"],
                        "code": "HOSP",
                        "display": "Hospital"
                    }]
                }
            ],
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{service_request_id[:8]}"}],
            "insurance": [{"reference": f"Coverage/cov-{service_request_id[:8]}"}],
            "bodySite": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "368209003",
                        "display": "Right upper arm structure"
                    }]
                }
            ],
            "note": [
                {
                    "authorString": "Dr Requester",
                    "time": authored_on,
                    "text": "Please perform fasting lab test"
                }
            ],
            "patientInstruction": "Fast for 8 hours before the test"
        }

        self._add_entry(service_request, service_request_id)
        return service_request_id

    def add_service_not_requested(self,
                                   encounter_id: str,
                                   authored_on: str,
                                   service_code: Dict = None) -> str:
        """
        Add a ServiceNotRequested resource (doNotPerform=true).

        Args:
            encounter_id: Reference to the encounter
            authored_on: Authored on datetime
            service_code: Service code {system, code, display}

        Returns:
            The service request ID
        """
        service_request_id = self._generate_id()
        requester_id = self._generate_id()
        performer_id = self._generate_id()

        if service_code is None:
            service_code = {
                "system": CODE_SYSTEMS["LOINC"],
                "code": "24323-8",
                "display": "Comprehensive metabolic 2000 panel - Serum or Plasma"
            }

        # Add Practitioners
        requester = {
            "resourceType": "Practitioner",
            "id": requester_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Requester", "given": ["Dr"]}]
        }
        self._add_entry(requester, requester_id)

        performer = {
            "resourceType": "Practitioner",
            "id": performer_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Performer", "given": ["NotReq"]}]
        }
        self._add_entry(performer, performer_id)

        service_not_requested = {
            "resourceType": "ServiceRequest",
            "id": service_request_id,
            "meta": {"profile": [QICORE_PROFILES["ServiceNotRequested"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["qicore-doNotPerformReason"],
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "105480006",
                            "display": "Procedure declined by patient (situation)"
                        }],
                        "text": "Patient declined procedure after discussion of risks"
                    }
                }
            ],
            "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/negation-protocol"],
            "instantiatesUri": ["http://example.org/protocols/negation"],
            "basedOn": [{"reference": f"CarePlan/cp-notreq-{service_request_id[:8]}"}],
            "replaces": [{"reference": f"ServiceRequest/sr-old-notreq-{service_request_id[:8]}"}],
            "requisition": {
                "system": "http://example.org/requisition",
                "value": f"REQ-NOTREQ-{service_request_id[:8]}"
            },
            "status": "completed",
            "intent": "order",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "108252007",
                        "display": "Laboratory procedure"
                    }]
                }
            ],
            "priority": "routine",
            "doNotPerform": True,
            "code": {"coding": [service_code]},
            "orderDetail": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "373067005",
                        "display": "No"
                    }]
                }
            ],
            "quantityQuantity": {
                "value": 0,
                "unit": "test",
                "system": CODE_SYSTEMS["UCUM"],
                "code": "{test}"
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "occurrenceDateTime": authored_on,
            "asNeededBoolean": True,
            "authoredOn": authored_on,
            "requester": {"reference": f"Practitioner/{requester_id}"},
            "performerType": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "61246008",
                    "display": "Laboratory medicine specialist"
                }]
            },
            "performer": [{"reference": f"Practitioner/{performer_id}"}],
            "locationCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["RoleCode"],
                        "code": "HOSP",
                        "display": "Hospital"
                    }]
                }
            ],
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "105480006",
                        "display": "Procedure declined by patient (situation)"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-notreq-{service_request_id[:8]}"}],
            "insurance": [{"reference": f"Coverage/cov-notreq-{service_request_id[:8]}"}],
            "bodySite": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "368209003",
                        "display": "Right upper arm structure"
                    }]
                }
            ],
            "note": [
                {
                    "authorString": "Dr Requester",
                    "time": authored_on,
                    "text": "Service not requested - patient declined"
                }
            ],
            "patientInstruction": "Patient declined this procedure"
        }

        self._add_entry(service_not_requested, service_request_id)
        return service_request_id

    # =========================================================================
    # DEVICE
    # =========================================================================

    def add_device(self, device_type: Dict = None) -> str:
        """
        Add a Device resource.

        Args:
            device_type: Device type coding {system, code, display}

        Returns:
            The device ID
        """
        device_id = self._generate_id()

        if device_type is None:
            device_type = {
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "706172005",
                "display": "Ventilator"
            }

        device = {
            "resourceType": "Device",
            "id": device_id,
            "meta": {"profile": [QICORE_PROFILES["Device"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["device-note"],
                    "valueAnnotation": {"text": "Device in good working condition"}
                }
            ],
            "status": "active",
            "expirationDate": "2025-12-31",
            "lotNumber": "LOT-2022-001",
            "serialNumber": "SN-12345678",
            "modelNumber": "MODEL-V2000",
            "partNumber": "PART-001",
            "type": {"coding": [device_type]},
            "patient": {"reference": f"Patient/{self.patient_id}"},
            "parent": {"reference": "Device/parent-device-001"}
        }

        self._add_entry(device, device_id)
        return device_id

    # =========================================================================
    # MEDICATION
    # =========================================================================

    def add_medication(self, medication_code: Dict = None) -> str:
        """
        Add a Medication resource.

        Args:
            medication_code: Medication code {system, code, display}

        Returns:
            The medication ID
        """
        medication_id = self._generate_id()

        if medication_code is None:
            medication_code = {
                "system": CODE_SYSTEMS["RXNORM"],
                "code": "860975",
                "display": "insulin human, isophane 70 UNT/ML / insulin human, regular 30 UNT/ML Injectable Suspension"
            }

        medication = {
            "resourceType": "Medication",
            "id": medication_id,
            "meta": {"profile": [QICORE_PROFILES["Medication"]]},
            "code": {"coding": [medication_code]},
            "status": "active",
            "manufacturer": {"reference": "Organization/pharma-org-123"},
            "form": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "385055001",
                    "display": "Tablet"
                }]
            },
            "amount": {
                "numerator": {
                    "value": 500,
                    "unit": "mg",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "mg"
                },
                "denominator": {
                    "value": 1,
                    "unit": "{tbl}",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "{tbl}"
                }
            },
            "ingredient": [
                {
                    "itemCodeableConcept": {
                        "coding": [{
                            "system": CODE_SYSTEMS["RXNORM"],
                            "code": "6809",
                            "display": "Metformin"
                        }]
                    },
                    "isActive": True,
                    "strength": {
                        "numerator": {
                            "value": 500,
                            "unit": "mg",
                            "system": CODE_SYSTEMS["UCUM"],
                            "code": "mg"
                        },
                        "denominator": {
                            "value": 1,
                            "unit": "{tbl}",
                            "system": CODE_SYSTEMS["UCUM"],
                            "code": "{tbl}"
                        }
                    }
                }
            ],
            "batch": {
                "lotNumber": "MED-LOT-2022-001",
                "expirationDate": "2025-12-31"
            }
        }

        self._add_entry(medication, medication_id)
        return medication_id

    # =========================================================================
    # MEDICATION WITH REFERENCE
    # =========================================================================

    def add_medication_request_with_reference(self,
                                               encounter_id: str,
                                               authored_on: str,
                                               medication_id: str) -> str:
        """
        Add a MedicationRequest with reference to Medication resource.

        Args:
            encounter_id: Reference to the encounter
            authored_on: Authored on datetime
            medication_id: Reference to Medication resource

        Returns:
            The medication request ID
        """
        med_request_id = self._generate_id()
        practitioner_id = self._generate_id()
        recorder_id = self._generate_id()

        # Add Practitioners
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Smith", "given": ["John"]}]
        }
        self._add_entry(practitioner, practitioner_id)

        recorder = {
            "resourceType": "Practitioner",
            "id": recorder_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Recorder", "given": ["Jane"]}]
        }
        self._add_entry(recorder, recorder_id)

        medication_request = {
            "resourceType": "MedicationRequest",
            "id": med_request_id,
            "meta": {"profile": [QICORE_PROFILES["MedicationRequest"]]},
            "status": "active",
            "statusReason": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "373066001",
                    "display": "Yes"
                }]
            },
            "intent": "order",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["MedicationRequestCategory"],
                        "code": "inpatient",
                        "display": "Inpatient"
                    }]
                }
            ],
            "priority": "routine",
            "reportedReference": {"reference": f"Practitioner/{practitioner_id}"},
            "medicationReference": {"reference": f"Medication/{medication_id}"},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "authoredOn": authored_on,
            "requester": {"reference": f"Practitioner/{practitioner_id}"},
            "recorder": {"reference": f"Practitioner/{recorder_id}"},
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{med_request_id[:8]}"}],
            "instantiatesCanonical": ["http://example.org/fhir/PlanDefinition/insulin-protocol"],
            "instantiatesUri": ["http://example.org/protocols/insulin"],
            "courseOfTherapyType": {
                "coding": [{
                    "system": CODE_SYSTEMS["MedicationRequestCourseOfTherapy"],
                    "code": "continuous",
                    "display": "Continuous long term therapy"
                }]
            },
            "dosageInstruction": [
                {
                    "sequence": 1,
                    "text": "10 units subcutaneously before breakfast",
                    "timing": {"repeat": {"frequency": 1, "period": 1, "periodUnit": "d", "when": ["ACM"]}},
                    "route": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "34206005",
                            "display": "Subcutaneous route"
                        }]
                    },
                    "doseAndRate": [
                        {
                            "type": {
                                "coding": [{
                                    "system": CODE_SYSTEMS["DoseRateType"],
                                    "code": "ordered",
                                    "display": "Ordered"
                                }]
                            },
                            "doseQuantity": {
                                "value": 10,
                                "unit": "U",
                                "system": CODE_SYSTEMS["UCUM"],
                                "code": "U"
                            }
                        }
                    ]
                }
            ]
        }

        self._add_entry(medication_request, med_request_id)
        return med_request_id

    def add_medication_administration_with_reference(self,
                                                      encounter_id: str,
                                                      effective_start: str,
                                                      effective_end: str,
                                                      medication_id: str) -> str:
        """
        Add a MedicationAdministration with reference to Medication resource.

        Args:
            encounter_id: Reference to the encounter
            effective_start: Effective period start
            effective_end: Effective period end
            medication_id: Reference to Medication resource

        Returns:
            The medication administration ID
        """
        med_admin_id = self._generate_id()
        practitioner_id = self._generate_id()
        device_id = self._generate_id()

        # Add Practitioner
        practitioner = {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "Nurse", "given": ["Admin"]}]
        }
        self._add_entry(practitioner, practitioner_id)

        # Add Device
        device = {
            "resourceType": "Device",
            "id": device_id,
            "meta": {"profile": [QICORE_PROFILES["Device"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "468063009",
                    "display": "Infusion pump"
                }]
            },
            "patient": {"reference": f"Patient/{self.patient_id}"}
        }
        self._add_entry(device, device_id)

        medication_admin = {
            "resourceType": "MedicationAdministration",
            "id": med_admin_id,
            "meta": {"profile": [QICORE_PROFILES["MedicationAdministration"]]},
            "instantiates": ["http://example.org/fhir/PlanDefinition/insulin-protocol"],
            "partOf": [{"reference": f"Procedure/proc-{med_admin_id[:8]}"}],
            "status": "completed",
            "statusReason": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "373066001",
                        "display": "Yes"
                    }]
                }
            ],
            "category": {
                "coding": [{
                    "system": CODE_SYSTEMS["MedicationAdminCategory"],
                    "code": "inpatient",
                    "display": "Inpatient"
                }]
            },
            "medicationReference": {"reference": f"Medication/{medication_id}"},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "context": {"reference": f"Encounter/{encounter_id}"},
            "supportingInformation": [{"reference": f"Observation/obs-{med_admin_id[:8]}"}],
            "effectivePeriod": {"start": effective_start, "end": effective_end},
            "performer": [
                {
                    "actor": {"reference": f"Practitioner/{practitioner_id}"},
                    "function": {
                        "coding": [{
                            "system": CODE_SYSTEMS["MedicationAdminPerformFunction"],
                            "code": "performer",
                            "display": "Performer"
                        }]
                    }
                }
            ],
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "reasonReference": [{"reference": f"Condition/cond-{med_admin_id[:8]}"}],
            "request": {"reference": f"MedicationRequest/req-{med_admin_id[:8]}"},
            "device": [{"reference": f"Device/{device_id}"}],
            "note": [
                {
                    "authorString": "Nurse Admin",
                    "time": effective_start,
                    "text": "Patient tolerated medication well"
                }
            ],
            "dosage": {
                "text": "10 units subcutaneously",
                "site": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "368209003",
                        "display": "Right upper arm structure"
                    }]
                },
                "route": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "34206005",
                        "display": "Subcutaneous route"
                    }]
                },
                "method": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "422145002",
                        "display": "Inject"
                    }]
                },
                "dose": {
                    "value": 10,
                    "unit": "U",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "U"
                },
                "rateQuantity": {
                    "value": 1,
                    "unit": "mL/hour",
                    "system": CODE_SYSTEMS["UCUM"],
                    "code": "mL/h"
                }
            }
        }

        self._add_entry(medication_admin, med_admin_id)
        return med_admin_id

    # =========================================================================
    # MEASURE REPORT
    # =========================================================================

    def add_measure_report(self,
                            description: str,
                            measure_url: str,
                            measurement_period_start: str,
                            measurement_period_end: str,
                            expected_populations: Dict = None) -> str:
        """
        Add a MeasureReport resource for test case validation.

        Args:
            description: Test case description
            measure_url: URL of the measure being tested
            measurement_period_start: Start of measurement period (YYYY-MM-DD)
            measurement_period_end: End of measurement period (YYYY-MM-DD)
            expected_populations: Dict of population codes to expected counts
                                  e.g., {"initialPopulation": 1, "denominator": 1}

        Returns:
            The measure report ID
        """
        measure_report_id = self._generate_id()
        parameters_id = f"{self._generate_id()}-parameters"

        if expected_populations is None:
            expected_populations = {"initialPopulation": 1}

        # Collect all resource references for evaluatedResource
        evaluated_resources = []
        for entry in self.bundle["entry"]:
            resource = entry["resource"]
            resource_type = resource["resourceType"]
            resource_id = resource["id"]
            evaluated_resources.append({"reference": f"{resource_type}/{resource_id}"})

        # Build population list
        populations = []
        population_code_map = {
            "initialPopulation": ("initial-population", "Initial Population"),
            "denominator": ("denominator", "Denominator"),
            "numerator": ("numerator", "Numerator"),
            "denominatorExclusion": ("denominator-exclusion", "Denominator Exclusion"),
            "denominatorException": ("denominator-exception", "Denominator Exception"),
            "numeratorExclusion": ("numerator-exclusion", "Numerator Exclusion"),
            "measurePopulation": ("measure-population", "Measure Population"),
            "measurePopulationExclusion": ("measure-population-exclusion", "Measure Population Exclusion"),
        }

        for pop_key, count in expected_populations.items():
            if pop_key in population_code_map:
                code, display = population_code_map[pop_key]
                populations.append({
                    "id": f"{pop_key}_1",
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["MeasurePopulation"],
                            "code": code,
                            "display": display
                        }]
                    },
                    "count": count
                })

        measure_report = {
            "resourceType": "MeasureReport",
            "id": measure_report_id,
            "meta": {"profile": [CQFM_PROFILES["MeasureReport"]]},
            "contained": [
                {
                    "resourceType": "Parameters",
                    "id": parameters_id,
                    "parameter": [{"name": "subject", "valueString": self.patient_id}]
                }
            ],
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["cqf-inputParameters"],
                    "valueReference": {"reference": f"#{parameters_id}"}
                },
                {
                    "url": FHIR_EXTENSIONS["cqfm-testCaseDescription"],
                    "valueMarkdown": description
                }
            ],
            "modifierExtension": [
                {
                    "url": FHIR_EXTENSIONS["cqfm-isTestCase"],
                    "valueBoolean": True
                }
            ],
            "status": "complete",
            "type": "individual",
            "measure": measure_url,
            "period": {"start": measurement_period_start, "end": measurement_period_end},
            "group": [
                {
                    "id": "Group_1",
                    "population": populations,
                    "measureScore": {"value": 0.0}
                }
            ],
            "evaluatedResource": evaluated_resources
        }

        self._add_entry(measure_report, measure_report_id)
        return measure_report_id

    # =========================================================================
    # BUNDLE OUTPUT
    # =========================================================================

    # =========================================================================
    # ENCOUNTER WITH CHIEF COMPLAINT
    # =========================================================================

    def add_encounter_with_cc(self,
                               start: str,
                               end: str,
                               status: str = "finished",
                               class_code: str = "IMP",
                               class_display: str = None,
                               type_coding: List[Dict] = None,
                               location_id: str = None) -> str:
        """
        Add an Encounter resource with Chief Complaint diagnosis use.

        Args:
            start: Period start datetime (ISO format)
            end: Period end datetime (ISO format)
            status: Encounter status
            class_code: Encounter class code
            class_display: Display text for class
            type_coding: List of type codings
            location_id: Optional location ID

        Returns:
            The encounter ID
        """
        encounter_id = self._generate_id()

        if type_coding is None:
            type_coding = [{
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "32485007",
                "display": "Hospital admission (procedure)"
            }]

        class_display_map = {
            "IMP": "inpatient encounter",
            "ACUTE": "inpatient acute",
            "NONAC": "inpatient non-acute",
            "SS": "short stay",
            "EMER": "emergency",
            "AMB": "ambulatory"
        }
        if class_display is None:
            class_display = class_display_map.get(class_code, "ambulatory")

        # Create a Condition resource for the Chief Complaint diagnosis
        condition_id = self._generate_id()
        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": {"profile": [QICORE_PROFILES["Condition"]]},
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active"
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed"
                }]
            },
            "category": [
                {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }]
                },
                {
                    "coding": [{
                        "system": "http://hl7.org/fhir/us/core/CodeSystem/condition-category",
                        "code": "health-concern",
                        "display": "Health Concern"
                    }]
                }
            ],
            "code": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "44054006",
                    "display": "Diabetes mellitus type 2"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "onsetDateTime": start
        }
        self._add_entry(condition, condition_id)

        encounter = {
            "resourceType": "Encounter",
            "id": encounter_id,
            "meta": {"profile": [QICORE_PROFILES["Encounter"]]},
            "identifier": [
                {"system": f"{self.MADIE_BASE_URL}/encounter-id", "value": encounter_id}
            ],
            "status": status,
            "statusHistory": [
                {"status": "arrived", "period": {"start": start, "end": start}}
            ],
            "class": {
                "system": CODE_SYSTEMS["ActCode"],
                "code": class_code,
                "display": class_display
            },
            "classHistory": [
                {
                    "class": {
                        "system": CODE_SYSTEMS["ActCode"],
                        "code": class_code,
                        "display": class_display
                    },
                    "period": {"start": start, "end": end}
                }
            ],
            "type": [{"coding": type_coding}],
            "serviceType": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "394802001",
                    "display": "General medicine"
                }]
            },
            "priority": {
                "coding": [{
                    "system": CODE_SYSTEMS["ActPriority"],
                    "code": "R",
                    "display": "routine"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "period": {"start": start, "end": end},
            "length": {
                "value": 5,
                "unit": "days",
                "system": CODE_SYSTEMS["UCUM"],
                "code": "d"
            },
            "reasonCode": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "44054006",
                        "display": "Diabetes mellitus type 2"
                    }]
                }
            ],
            "diagnosis": [
                {
                    "condition": {"reference": f"Condition/{condition_id}"},
                    "use": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/diagnosis-role",
                            "code": "CC",
                            "display": "Chief Complaint"
                        }]
                    },
                    "rank": 1
                }
            ],
            "hospitalization": {
                "dischargeDisposition": {
                    "coding": [{
                        "system": CODE_SYSTEMS["DischargeDisposition"],
                        "code": "home",
                        "display": "Home"
                    }]
                }
            }
        }

        # Add location if provided
        if location_id:
            encounter["location"] = [
                {
                    "location": {"reference": f"Location/{location_id}"},
                    "status": "active",
                    "physicalType": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LocationPhysicalType"],
                            "code": "ro",
                            "display": "Room"
                        }]
                    },
                    "period": {"start": start, "end": end}
                }
            ]

        self._add_entry(encounter, encounter_id)
        return encounter_id

    # =========================================================================
    # OBSERVATION WITH ALL FIELDS (FOR COVERAGE)
    # =========================================================================

    def add_observation_full(self,
                              encounter_id: str,
                              category: str = "laboratory",
                              code: Dict = None,
                              value: float = 100,
                              unit: str = "mg/dL",
                              effective_datetime: str = None) -> str:
        """
        Add an Observation resource with ALL fields for full coverage.
        Includes: text, basedOn, focus, performer, dataAbsentReason, note, device

        Args:
            encounter_id: Reference to the encounter
            category: Observation category
            code: Observation code
            value: Numeric value
            unit: Unit of measure
            effective_datetime: Effective datetime

        Returns:
            The observation ID
        """
        observation_id = self._generate_id()
        specimen_id = self._generate_id()
        device_id = self._generate_id()
        performer_id = self._generate_id()
        service_request_id = self._generate_id()

        if code is None:
            code = {
                "system": CODE_SYSTEMS["LOINC"],
                "code": "2339-0",
                "display": "Glucose [Mass/volume] in Blood"
            }

        if effective_datetime is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        if category == "laboratory":
            profile = QICORE_PROFILES["ObservationLab"]
        else:
            profile = QICORE_PROFILES["SimpleObservation"]

        # Add Specimen
        specimen = {
            "resourceType": "Specimen",
            "id": specimen_id,
            "meta": {"profile": [USCORE_PROFILES["Specimen"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "119297000",
                    "display": "Blood specimen"
                }]
            },
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "receivedTime": effective_datetime,
            "collection": {"collectedDateTime": effective_datetime}
        }
        self._add_entry(specimen, specimen_id)

        # Add Device for the observation
        device = {
            "resourceType": "Device",
            "id": device_id,
            "meta": {"profile": [QICORE_PROFILES["Device"]]},
            "type": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "706177008",
                    "display": "Glucometer"
                }]
            },
            "patient": {"reference": f"Patient/{self.patient_id}"}
        }
        self._add_entry(device, device_id)

        # Add Practitioner as performer
        performer = {
            "resourceType": "Practitioner",
            "id": performer_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "LabTech", "given": ["Sally"]}]
        }
        self._add_entry(performer, performer_id)

        # Add ServiceRequest for basedOn
        service_request = {
            "resourceType": "ServiceRequest",
            "id": service_request_id,
            "meta": {"profile": [QICORE_PROFILES["ServiceRequest"]]},
            "status": "completed",
            "intent": "order",
            "code": {"coding": [code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "authoredOn": effective_datetime
        }
        self._add_entry(service_request, service_request_id)

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [profile]},
            "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\">Blood Glucose Test Result</div>"
            },
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["observation-bodyPosition"],
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "33586001",
                            "display": "Sitting position"
                        }]
                    }
                }
            ],
            "basedOn": [{"reference": f"ServiceRequest/{service_request_id}"}],
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": category,
                        "display": category.replace("-", " ").title()
                    }]
                }
            ],
            "code": {"coding": [code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "effectiveDateTime": effective_datetime,
            "issued": effective_datetime,
            "performer": [{"reference": f"Practitioner/{performer_id}"}],
            "valueQuantity": {
                "value": value,
                "unit": unit,
                "system": CODE_SYSTEMS["UCUM"],
                "code": unit
            },
            "interpretation": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationInterpretation"],
                        "code": "N",
                        "display": "Normal"
                    }]
                }
            ],
            "note": [
                {
                    "authorString": "Lab Technician",
                    "time": effective_datetime,
                    "text": "Patient was fasting for 8 hours before test"
                }
            ],
            "bodySite": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "368209003",
                    "display": "Right upper arm structure"
                }]
            },
            "method": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "129300006",
                    "display": "Measurement - action"
                }]
            },
            "specimen": {"reference": f"Specimen/{specimen_id}"},
            "device": {"reference": f"Device/{device_id}"},
            "referenceRange": [
                {
                    "low": {"value": 70, "unit": unit, "system": CODE_SYSTEMS["UCUM"], "code": unit},
                    "high": {"value": 140, "unit": unit, "system": CODE_SYSTEMS["UCUM"], "code": unit},
                    "type": {
                        "coding": [{
                            "system": CODE_SYSTEMS["ReferenceRangeMeaning"],
                            "code": "normal",
                            "display": "Normal Range"
                        }]
                    }
                }
            ],
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LOINC"],
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mmHg",
                        "system": CODE_SYSTEMS["UCUM"],
                        "code": "mm[Hg]"
                    }
                }
            ]
        }

        self._add_entry(observation, observation_id)
        return observation_id

    # =========================================================================
    # PATIENT WITH DETAILED ETHNICITY
    # =========================================================================

    def add_patient_with_detailed_ethnicity(self,
                                             given_name: str = None,
                                             family_name: str = None,
                                             gender: str = "male",
                                             birth_date: str = "1980-01-01") -> str:
        """
        Add a Patient resource with detailed ethnicity extension.

        Returns:
            The patient ID
        """
        if given_name is None:
            given_name = self.test_case_name
        if family_name is None:
            family_name = "TestPatient"

        # Add General Practitioner
        gp_id = "gp-001"
        gp_practitioner = {
            "resourceType": "Practitioner",
            "id": gp_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "GeneralPractitioner", "given": ["Dr"]}]
        }
        self._add_entry(gp_practitioner, gp_id)

        patient = {
            "resourceType": "Patient",
            "id": self.patient_id,
            "meta": {"profile": [QICORE_PROFILES["Patient"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["us-core-race"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": "2028-9",
                                "display": "Asian",
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": "Asian"}
                    ]
                },
                {
                    "url": FHIR_EXTENSIONS["us-core-ethnicity"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": "2135-2",
                                "display": "Hispanic or Latino",
                                "userSelected": True
                            }
                        },
                        {
                            "url": "detailed",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": "2148-5",
                                "display": "Mexican",
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": "Hispanic or Latino - Mexican"}
                    ]
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [{"system": CODE_SYSTEMS["IdentifierType"], "code": "MR"}]
                    },
                    "system": f"{self.MADIE_BASE_URL}/",
                    "value": self.patient_id
                }
            ],
            "active": True,
            "name": [{"use": "official", "family": family_name, "given": [given_name]}],
            "telecom": [
                {"system": "phone", "value": "555-123-4567", "use": "home"},
                {"system": "email", "value": "patient@example.com", "use": "home"}
            ],
            "gender": gender,
            "birthDate": birth_date,
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "line": ["123 Main Street"],
                    "city": "Boston",
                    "state": "MA",
                    "postalCode": "02101",
                    "country": "USA"
                }
            ],
            "maritalStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["MaritalStatus"],
                    "code": "M",
                    "display": "Married"
                }]
            },
            "communication": [
                {
                    "language": {
                        "coding": [{
                            "system": CODE_SYSTEMS["Language"],
                            "code": "en",
                            "display": "English"
                        }]
                    },
                    "preferred": True
                }
            ],
            "generalPractitioner": [{"reference": f"Practitioner/{gp_id}"}]
        }

        self._add_entry(patient, self.patient_id)
        return self.patient_id

    # =========================================================================
    # COVERAGE WITH PAYER TYPE
    # =========================================================================

    def add_coverage_payer_type(self, start: str, end: str) -> str:
        """
        Add a Coverage resource with Payer Type valueset code.

        Args:
            start: Coverage period start
            end: Coverage period end

        Returns:
            The coverage ID
        """
        coverage_id = self._generate_id()

        coverage = {
            "resourceType": "Coverage",
            "id": coverage_id,
            "meta": {"profile": [QICORE_PROFILES["Coverage"]]},
            "status": "active",
            "type": {
                "coding": [{
                    "system": "https://nahdo.org/sopt",
                    "code": "1",
                    "display": "MEDICARE"
                }]
            },
            "policyHolder": {"reference": f"Patient/{self.patient_id}"},
            "subscriber": {"reference": f"Patient/{self.patient_id}"},
            "subscriberId": "MBR-12345",
            "beneficiary": {"reference": f"Patient/{self.patient_id}"},
            "dependent": "01",
            "relationship": {
                "coding": [{
                    "system": CODE_SYSTEMS["SubscriberRelationship"],
                    "code": "self",
                    "display": "Self"
                }]
            },
            "period": {"start": start, "end": end},
            "payor": [{"reference": "Organization/payor-org-123"}],
            "class": [
                {
                    "type": {
                        "coding": [{
                            "system": CODE_SYSTEMS["CoverageClass"],
                            "code": "plan",
                            "display": "Plan"
                        }]
                    },
                    "value": "PLAN-001",
                    "name": "Medicare Plan A"
                }
            ],
            "order": 1,
            "network": "Medicare Network",
            "subrogation": False,
            "contract": [{"reference": "Contract/contract-123"}]
        }

        self._add_entry(coverage, coverage_id)
        return coverage_id

    # =========================================================================
    # PATIENT WITH SEX EXTENSION
    # =========================================================================

    def add_patient_with_sex(self,
                              given_name: str = None,
                              family_name: str = None,
                              gender: str = "male",
                              birth_date: str = "1980-01-01") -> str:
        """
        Add a Patient resource with sex extension (SNOMED code).

        Returns:
            The patient ID
        """
        if given_name is None:
            given_name = self.test_case_name
        if family_name is None:
            family_name = "TestPatient"

        # Add General Practitioner
        gp_id = "gp-001"
        gp_practitioner = {
            "resourceType": "Practitioner",
            "id": gp_id,
            "meta": {"profile": [QICORE_PROFILES["Practitioner"]]},
            "identifier": [{"system": CODE_SYSTEMS["NPI"], "value": "1234567893"}],
            "name": [{"family": "GeneralPractitioner", "given": ["Dr"]}]
        }
        self._add_entry(gp_practitioner, gp_id)

        # Sex extension uses codes from ValueSet 2.16.840.1.113762.1.4.1240.3
        # Valid codes: male, female, unknown (lowercase string codes)
        sex_code = "male" if gender == "male" else "female"

        patient = {
            "resourceType": "Patient",
            "id": self.patient_id,
            "meta": {"profile": [QICORE_PROFILES["Patient"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["us-core-race"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": "2028-9",
                                "display": "Asian",
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": "Asian"}
                    ]
                },
                {
                    "url": FHIR_EXTENSIONS["us-core-ethnicity"],
                    "extension": [
                        {
                            "url": "ombCategory",
                            "valueCoding": {
                                "system": CODE_SYSTEMS["RaceEthnicity"],
                                "code": "2186-5",
                                "display": "Not Hispanic or Latino",
                                "userSelected": True
                            }
                        },
                        {"url": "text", "valueString": "Not Hispanic or Latino"}
                    ]
                },
                {
                    "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex",
                    "valueCode": sex_code
                }
            ],
            "identifier": [
                {
                    "type": {
                        "coding": [{"system": CODE_SYSTEMS["IdentifierType"], "code": "MR"}]
                    },
                    "system": f"{self.MADIE_BASE_URL}/",
                    "value": self.patient_id
                }
            ],
            "active": True,
            "name": [{"use": "official", "family": family_name, "given": [given_name]}],
            "telecom": [
                {"system": "phone", "value": "555-123-4567", "use": "home"},
                {"system": "email", "value": "patient@example.com", "use": "home"}
            ],
            "gender": gender,
            "birthDate": birth_date,
            "address": [
                {
                    "use": "home",
                    "type": "physical",
                    "line": ["123 Main Street"],
                    "city": "Boston",
                    "state": "MA",
                    "postalCode": "02101",
                    "country": "USA"
                }
            ],
            "maritalStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["MaritalStatus"],
                    "code": "M",
                    "display": "Married"
                }]
            },
            "communication": [
                {
                    "language": {
                        "coding": [{
                            "system": CODE_SYSTEMS["Language"],
                            "code": "en",
                            "display": "English"
                        }]
                    },
                    "preferred": True
                }
            ],
            "generalPractitioner": [{"reference": f"Practitioner/{gp_id}"}]
        }

        self._add_entry(patient, self.patient_id)
        return self.patient_id

    # =========================================================================
    # CONDITION ENCOUNTER DIAGNOSIS (for SDE Condition Diagnosis)
    # =========================================================================

    def add_condition_encounter_diagnosis(self,
                                           encounter_id: str,
                                           code: Dict = None,
                                           clinical_status: str = "active",
                                           verification_status: str = "confirmed",
                                           onset_datetime: str = "2022-01-05T10:00:00.000Z",
                                           abatement_datetime: str = None) -> str:
        """
        Add a Condition resource using ConditionEncounterDiagnosis profile.
        This profile is for encounter diagnoses (not problem list items).

        Args:
            encounter_id: Reference to the encounter
            code: Condition code {system, code, display}
            clinical_status: Clinical status (active, resolved, etc.)
            verification_status: Verification status (confirmed, etc.)
            onset_datetime: Onset datetime (used for prevalenceInterval)
            abatement_datetime: Optional abatement datetime

        Returns:
            The condition ID
        """
        condition_id = self._generate_id()

        if code is None:
            code = {
                "system": CODE_SYSTEMS["SNOMED"],
                "code": "44054006",
                "display": "Diabetes mellitus type 2 (disorder)"
            }

        condition = {
            "resourceType": "Condition",
            "id": condition_id,
            "meta": {"profile": [QICORE_PROFILES["ConditionEncounterDiagnosis"]]},
            "clinicalStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["ConditionClinicalStatus"],
                    "code": clinical_status
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": CODE_SYSTEMS["ConditionVerificationStatus"],
                    "code": verification_status
                }]
            },
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ConditionCategory"],
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }]
                }
            ],
            "severity": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "24484000",
                    "display": "Severe"
                }]
            },
            "code": {"coding": [code]},
            "bodySite": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "38266002",
                        "display": "Entire body as a whole"
                    }]
                }
            ],
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "onsetDateTime": onset_datetime,
            "stage": [
                {
                    "summary": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "786005",
                            "display": "Clinical stage I"
                        }]
                    }
                }
            ],
            "evidence": [
                {
                    "code": [
                        {
                            "coding": [{
                                "system": CODE_SYSTEMS["SNOMED"],
                                "code": "169876006",
                                "display": "Blood test evidence"
                            }]
                        }
                    ]
                }
            ],
            "note": [{"text": "Encounter diagnosis documented during admission"}]
        }

        # Add abatementDateTime if provided
        if abatement_datetime:
            condition["abatementDateTime"] = abatement_datetime

        self._add_entry(condition, condition_id)
        return condition_id

    # =========================================================================
    # SIMPLE OBSERVATION (for SDE Observation Simple)
    # =========================================================================

    def add_simple_observation(self,
                                encounter_id: str,
                                category: str = "social-history",
                                code: Dict = None,
                                value: float = None,
                                value_string: str = None,
                                value_codeable_concept: Dict = None,
                                unit: str = None,
                                effective_datetime: str = None,
                                effective_period_start: str = None,
                                effective_period_end: str = None,
                                data_absent_reason: str = None,
                                include_specimen: bool = True) -> str:
        """
        Add a SimpleObservation resource for categories like social-history, survey, imaging, procedure.

        Args:
            encounter_id: Reference to the encounter
            category: Observation category (social-history, survey, imaging, procedure)
            code: Observation code {system, code, display}
            value: Optional numeric value
            value_string: Optional string value
            value_codeable_concept: Optional codeable concept value {system, code, display}
            unit: Unit of measure (if numeric value)
            effective_datetime: Effective datetime
            effective_period_start: Start of effective period (alternative to datetime)
            effective_period_end: End of effective period
            data_absent_reason: If set, use dataAbsentReason instead of value (e.g., "unknown", "not-asked", "masked")
            include_specimen: Whether to include a specimen reference (default True)

        Returns:
            The observation ID
        """
        observation_id = self._generate_id()
        specimen_id = self._generate_id()

        # Default codes based on category
        if code is None:
            if category == "social-history":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "72166-2",
                    "display": "Tobacco smoking status"
                }
            elif category == "survey":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "44249-1",
                    "display": "PHQ-9 quick depression assessment panel"
                }
            elif category == "imaging":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "30746-2",
                    "display": "CT Chest"
                }
            elif category == "procedure":
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "29463-7",
                    "display": "Body weight"
                }
            else:
                code = {
                    "system": CODE_SYSTEMS["LOINC"],
                    "code": "8302-2",
                    "display": "Body height"
                }

        if effective_datetime is None and effective_period_start is None:
            effective_datetime = "2022-01-06T10:00:00.000Z"

        # Category display names
        category_displays = {
            "social-history": "Social History",
            "survey": "Survey",
            "imaging": "Imaging",
            "procedure": "Procedure"
        }

        # Add Specimen resource if requested
        if include_specimen:
            specimen = {
                "resourceType": "Specimen",
                "id": specimen_id,
                "meta": {"profile": [USCORE_PROFILES["Specimen"]]},
                "type": {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "119297000",
                        "display": "Blood specimen"
                    }]
                },
                "subject": {"reference": f"Patient/{self.patient_id}"},
                "receivedTime": effective_datetime or effective_period_start,
                "collection": {"collectedDateTime": effective_datetime or effective_period_start}
            }
            self._add_entry(specimen, specimen_id)

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "meta": {"profile": [QICORE_PROFILES["SimpleObservation"]]},
            "extension": [
                {
                    "url": FHIR_EXTENSIONS["observation-bodyPosition"],
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": CODE_SYSTEMS["SNOMED"],
                            "code": "33586001",
                            "display": "Sitting position"
                        }]
                    }
                }
            ],
            "partOf": [{"reference": f"Procedure/proc-{observation_id[:8]}"}],
            "status": "final",
            "category": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationCategory"],
                        "code": category,
                        "display": category_displays.get(category, category.replace("-", " ").title())
                    }]
                }
            ],
            "code": {"coding": [code]},
            "subject": {"reference": f"Patient/{self.patient_id}"},
            "encounter": {"reference": f"Encounter/{encounter_id}"},
            "issued": effective_datetime or effective_period_start,
            "interpretation": [
                {
                    "coding": [{
                        "system": CODE_SYSTEMS["ObservationInterpretation"],
                        "code": "N",
                        "display": "Normal"
                    }]
                }
            ],
            "bodySite": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "368209003",
                    "display": "Right upper arm structure"
                }]
            },
            "method": {
                "coding": [{
                    "system": CODE_SYSTEMS["SNOMED"],
                    "code": "129300006",
                    "display": "Measurement - action"
                }]
            },
            "referenceRange": [
                {
                    "text": "Normal range"
                }
            ],
            "hasMember": [{"reference": f"Observation/member-{observation_id[:8]}"}],
            "derivedFrom": [{"reference": f"Observation/derived-{observation_id[:8]}"}],
            "component": [
                {
                    "code": {
                        "coding": [{
                            "system": CODE_SYSTEMS["LOINC"],
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }]
                    },
                    "valueQuantity": {
                        "value": 120,
                        "unit": "mmHg",
                        "system": CODE_SYSTEMS["UCUM"],
                        "code": "mm[Hg]"
                    }
                }
            ]
        }

        # Add specimen reference if included
        if include_specimen:
            observation["specimen"] = {"reference": f"Specimen/{specimen_id}"}

        # Set effective[x] - either datetime or period
        if effective_period_start:
            observation["effectivePeriod"] = {
                "start": effective_period_start
            }
            if effective_period_end:
                observation["effectivePeriod"]["end"] = effective_period_end
        else:
            observation["effectiveDateTime"] = effective_datetime

        # Set value[x] or dataAbsentReason based on what's provided
        if data_absent_reason is not None:
            # Use dataAbsentReason instead of a value
            observation["dataAbsentReason"] = {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                    "code": data_absent_reason,
                    "display": data_absent_reason.replace("-", " ").title()
                }]
            }
        elif value is not None:
            observation["valueQuantity"] = {
                "value": value,
                "unit": unit or "1",
                "system": CODE_SYSTEMS["UCUM"],
                "code": unit or "1"
            }
        elif value_string is not None:
            observation["valueString"] = value_string
        elif value_codeable_concept is not None:
            observation["valueCodeableConcept"] = {
                "coding": [value_codeable_concept]
            }
        else:
            # Default to a codeable concept value for social-history
            if category == "social-history":
                observation["valueCodeableConcept"] = {
                    "coding": [{
                        "system": CODE_SYSTEMS["SNOMED"],
                        "code": "8517006",
                        "display": "Ex-smoker"
                    }]
                }
            else:
                observation["valueString"] = "Test result"

        self._add_entry(observation, observation_id)
        return observation_id

    # =========================================================================
    # BUNDLE OUTPUT
    # =========================================================================

    def get_bundle(self) -> Dict:
        """Return the FHIR Bundle dictionary"""
        return self.bundle

    def save(self, output_path: str):
        """
        Save the bundle to a JSON file.

        Args:
            output_path: Path to output file
        """
        # Use Unix line endings (LF) to match MADiE expected format
        with open(output_path, 'w', newline='\n') as f:
            json.dump(self.bundle, f, indent=2)
        print(f"  Saved: {output_path}")
