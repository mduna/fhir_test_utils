#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FHIR Test Utilities Package

A reusable library for generating FHIR R4 test cases for CQL measures.
Designed for use with MADiE (Measure Authoring Development Integrated Environment).

Components:
- FHIRBundleGenerator: Creates FHIR transaction bundles with QICore resources
- VSACClient: Downloads valuesets from VSAC FHIR API
- MADiEExporter: Creates MADiE-compatible export structure
- Code Systems: Common code system URLs and codes
- QICore Profiles: QICore 6.0.0 profile URLs

Usage:
    from fhir_test_utils import (
        FHIRBundleGenerator,
        VSACClient,
        MADiEExporter,
        TestCaseRegistry,
        CODE_SYSTEMS,
        COMMON_CODES,
        QICORE_PROFILES
    )

    # Create a test case
    gen = FHIRBundleGenerator("TestCaseName")
    gen.add_patient()
    enc_id = gen.add_encounter(start="2022-01-05T08:00:00.000Z", end="2022-01-10T12:00:00.000Z")
    gen.add_condition(enc_id)

    # Export to MADiE format
    exporter = MADiEExporter("MeasureName", "1.0.0")
    exporter.add_test_case(lambda: gen, "Series", "Title", "Description")
    exporter.export()
"""

__version__ = "1.0.0"
__author__ = "AI-Generated"

# Bundle Generator
from .bundle_generator import FHIRBundleGenerator

# VSAC Client
from .vsac_client import (
    VSACClient,
    extract_valuesets_from_cql,
    extract_codesystems_from_cql,
    extract_direct_codes_from_cql,
    # Exceptions
    VSACError,
    VSACAuthenticationError,
    VSACNotFoundError,
    VSACRateLimitError,
    VSACConnectionError,
    VSACResponseError,
    VSACValidationError,
    CacheError,
)

# MADiE Exporter
from .madie_exporter import (
    MADiEExporter,
    TestCaseRegistry
)

# Code Systems
from .code_systems import (
    CODE_SYSTEMS,
    COMMON_CODES,
    get_code_system_url,
    get_common_code,
    create_coding,
    create_codeable_concept
)

# QICore Profiles
from .qicore_profiles import (
    QICORE_PROFILES,
    USCORE_PROFILES,
    CQFM_PROFILES,
    FHIR_EXTENSIONS,
    get_profile_url,
    get_uscore_profile_url,
    get_cqfm_profile_url,
    get_extension_url,
    get_meta_with_profile
)

__all__ = [
    # Classes
    "FHIRBundleGenerator",
    "VSACClient",
    "MADiEExporter",
    "TestCaseRegistry",

    # VSAC Exceptions
    "VSACError",
    "VSACAuthenticationError",
    "VSACNotFoundError",
    "VSACRateLimitError",
    "VSACConnectionError",
    "VSACResponseError",
    "VSACValidationError",
    "CacheError",

    # Code Systems
    "CODE_SYSTEMS",
    "COMMON_CODES",
    "get_code_system_url",
    "get_common_code",
    "create_coding",
    "create_codeable_concept",

    # Profiles
    "QICORE_PROFILES",
    "USCORE_PROFILES",
    "CQFM_PROFILES",
    "FHIR_EXTENSIONS",
    "get_profile_url",
    "get_uscore_profile_url",
    "get_cqfm_profile_url",
    "get_extension_url",
    "get_meta_with_profile",

    # CQL Parsing
    "extract_valuesets_from_cql",
    "extract_codesystems_from_cql",
    "extract_direct_codes_from_cql",
]
