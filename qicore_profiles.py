#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QICore Profile Definitions

This module defines URLs for QICore FHIR profiles used in measure test cases.
Based on QICore 6.0.0 Implementation Guide.
"""

# =============================================================================
# QICORE 6.0.0 PROFILE URLs
# =============================================================================

QICORE_BASE = "http://hl7.org/fhir/us/qicore/StructureDefinition"

QICORE_PROFILES = {
    # Patient
    "Patient": f"{QICORE_BASE}/qicore-patient",

    # Encounter
    "Encounter": f"{QICORE_BASE}/qicore-encounter",

    # Condition Profiles
    "Condition": f"{QICORE_BASE}/qicore-condition-problems-health-concerns",
    "ConditionProblemsHealthConcerns": f"{QICORE_BASE}/qicore-condition-problems-health-concerns",
    "ConditionEncounterDiagnosis": f"{QICORE_BASE}/qicore-condition-encounter-diagnosis",

    # Coverage
    "Coverage": f"{QICORE_BASE}/qicore-coverage",

    # Location
    "Location": f"{QICORE_BASE}/qicore-location",

    # Observation Profiles
    "Observation": f"{QICORE_BASE}/qicore-observation",
    "ObservationLab": f"{QICORE_BASE}/qicore-observation-lab",
    "LaboratoryResultObservation": f"{QICORE_BASE}/qicore-observation-lab",
    "ObservationClinicalResult": f"{QICORE_BASE}/qicore-observation-clinical-result",
    "SimpleObservation": f"{QICORE_BASE}/qicore-simple-observation",
    "ObservationScreeningAssessment": f"{QICORE_BASE}/qicore-observation-screening-assessment",

    # Medication Profiles
    "Medication": f"{QICORE_BASE}/qicore-medication",
    "MedicationRequest": f"{QICORE_BASE}/qicore-medicationrequest",
    "MedicationNotRequested": f"{QICORE_BASE}/qicore-medicationnotrequested",
    "MedicationAdministration": f"{QICORE_BASE}/qicore-medicationadministration",
    "MedicationAdministrationNotDone": f"{QICORE_BASE}/qicore-medicationadministrationnotdone",
    "MedicationDispense": f"{QICORE_BASE}/qicore-medicationdispense",
    "MedicationDispenseDeclined": f"{QICORE_BASE}/qicore-medicationdispensedeclined",
    "MedicationStatement": f"{QICORE_BASE}/qicore-medicationstatement",

    # Procedure Profiles
    "Procedure": f"{QICORE_BASE}/qicore-procedure",
    "ProcedureNotDone": f"{QICORE_BASE}/qicore-procedurenotdone",

    # Diagnostic Report Profiles
    "DiagnosticReport": f"{QICORE_BASE}/qicore-diagnosticreport",
    "DiagnosticReportLab": f"{QICORE_BASE}/qicore-diagnosticreport-lab",
    "DiagnosticReportNote": f"{QICORE_BASE}/qicore-diagnosticreport-note",

    # Service Request Profiles
    "ServiceRequest": f"{QICORE_BASE}/qicore-servicerequest",
    "ServiceNotRequested": f"{QICORE_BASE}/qicore-servicenotrequested",

    # Device Profiles
    "Device": f"{QICORE_BASE}/qicore-device",
    "DeviceNotRequested": f"{QICORE_BASE}/qicore-devicenotrequested",
    "DeviceRequest": f"{QICORE_BASE}/qicore-devicerequest",
    "DeviceUseStatement": f"{QICORE_BASE}/qicore-deviceusestatement",

    # Practitioner/Organization
    "Practitioner": f"{QICORE_BASE}/qicore-practitioner",
    "PractitionerRole": f"{QICORE_BASE}/qicore-practitionerrole",
    "Organization": f"{QICORE_BASE}/qicore-organization",

    # Care Plan/Goal
    "CarePlan": f"{QICORE_BASE}/qicore-careplan",
    "Goal": f"{QICORE_BASE}/qicore-goal",
    "NutritionOrder": f"{QICORE_BASE}/qicore-nutritionorder",

    # Immunization
    "Immunization": f"{QICORE_BASE}/qicore-immunization",
    "ImmunizationNotDone": f"{QICORE_BASE}/qicore-immunizationnotdone",
    "ImmunizationEvaluation": f"{QICORE_BASE}/qicore-immunizationevaluation",
    "ImmunizationRecommendation": f"{QICORE_BASE}/qicore-immunizationrecommendation",

    # Allergy/Adverse Event
    "AllergyIntolerance": f"{QICORE_BASE}/qicore-allergyintolerance",
    "AdverseEvent": f"{QICORE_BASE}/qicore-adverseevent",

    # Communication
    "Communication": f"{QICORE_BASE}/qicore-communication",
    "CommunicationNotDone": f"{QICORE_BASE}/qicore-communicationnotdone",
    "CommunicationRequest": f"{QICORE_BASE}/qicore-communicationrequest",

    # Task
    "Task": f"{QICORE_BASE}/qicore-task",
    "TaskRejected": f"{QICORE_BASE}/qicore-taskrejected",

    # Specimen
    "Specimen": f"{QICORE_BASE}/qicore-specimen",

    # Claim
    "Claim": f"{QICORE_BASE}/qicore-claim",
    "ClaimResponse": f"{QICORE_BASE}/qicore-claimresponse",

    # Substance
    "Substance": f"{QICORE_BASE}/qicore-substance",

    # Body Structure
    "BodyStructure": f"{QICORE_BASE}/qicore-bodystructure",

    # Family Member History
    "FamilyMemberHistory": f"{QICORE_BASE}/qicore-familymemberhistory",

    # Related Person
    "RelatedPerson": f"{QICORE_BASE}/qicore-relatedperson",
}

# =============================================================================
# US CORE PROFILE URLs (for resources not in QICore)
# =============================================================================

USCORE_BASE = "http://hl7.org/fhir/us/core/StructureDefinition"

USCORE_PROFILES = {
    "Specimen": f"{USCORE_BASE}/us-core-specimen",
    "Provenance": f"{USCORE_BASE}/us-core-provenance",
    "DocumentReference": f"{USCORE_BASE}/us-core-documentreference",
    # Vital Signs Profiles
    "VitalSigns": f"{USCORE_BASE}/us-core-vital-signs",
    "BloodPressure": f"{USCORE_BASE}/us-core-blood-pressure",
}

# =============================================================================
# CQFM (CQF Measures) PROFILE URLs
# =============================================================================

CQFM_BASE = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition"

CQFM_PROFILES = {
    "MeasureReport": f"{CQFM_BASE}/test-case-cqfm",
    "TestCaseMeasureReport": f"{CQFM_BASE}/test-case-cqfm",
}

# =============================================================================
# EXTENSION URLs
# =============================================================================

FHIR_EXTENSIONS = {
    # US Core Extensions
    "us-core-race": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
    "us-core-ethnicity": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
    "us-core-birthsex": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
    "us-core-genderIdentity": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-genderIdentity",

    # QICore Extensions
    "qicore-doNotPerformReason": f"{QICORE_BASE}/qicore-doNotPerformReason",
    "qicore-recorded": f"{QICORE_BASE}/qicore-recorded",
    "qicore-notDone": f"{QICORE_BASE}/qicore-notDone",
    "qicore-notDoneReason": f"{QICORE_BASE}/qicore-notDoneReason",

    # FHIR Core Extensions
    "observation-bodyPosition": "http://hl7.org/fhir/StructureDefinition/observation-bodyPosition",
    "procedure-approachBodyStructure": "http://hl7.org/fhir/StructureDefinition/procedure-approachBodyStructure",
    "diagnosticReport-locationPerformed": "http://hl7.org/fhir/StructureDefinition/diagnosticReport-locationPerformed",
    "location-boundary-geojson": "http://hl7.org/fhir/StructureDefinition/location-boundary-geojson",
    "device-note": "http://hl7.org/fhir/StructureDefinition/device-note",

    # CQF Measures Extensions
    "cqf-inputParameters": "http://hl7.org/fhir/StructureDefinition/cqf-inputParameters",
    "cqfm-testCaseDescription": "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-testCaseDescription",
    "cqfm-isTestCase": "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-isTestCase",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_profile_url(resource_type: str) -> str:
    """Get the QICore profile URL for a resource type"""
    return QICORE_PROFILES.get(resource_type)

def get_uscore_profile_url(resource_type: str) -> str:
    """Get the US Core profile URL for a resource type"""
    return USCORE_PROFILES.get(resource_type)

def get_cqfm_profile_url(resource_type: str) -> str:
    """Get the CQFM profile URL for a resource type"""
    return CQFM_PROFILES.get(resource_type)

def get_extension_url(extension_name: str) -> str:
    """Get the URL for an extension by name"""
    return FHIR_EXTENSIONS.get(extension_name)

def get_meta_with_profile(resource_type: str) -> dict:
    """Create a meta element with the appropriate profile for a resource type"""
    profile_url = get_profile_url(resource_type)
    if profile_url:
        return {"profile": [profile_url]}
    return {}
