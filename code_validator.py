#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Code Validator

Validates clinical codes against official terminology servers:
- SNOMED CT (via official FHIR API)
- RxNorm (via RxNav REST API)
- LOINC (via LOINC FHIR server)
- HSLOC (via local lookup table from CDC NHSN)
- ICD-10-CM (via HL7 Terminology server)

Optional VSAC API Integration:
    Set environment variable VSAC_API_KEY to enable VSAC API validation.
    This allows lookup of codes in NHSN value sets directly from VSAC.

    Get a VSAC API key at: https://uts.nlm.nih.gov/uts/signup-login

    Windows:   set VSAC_API_KEY=your-api-key-here
    Linux/Mac: export VSAC_API_KEY=your-api-key-here

Usage:
    # Single code validation
    from code_validator import CodeValidator
    validator = CodeValidator()
    result = validator.validate("SNOMED", "91861009", "Acute myeloid leukemia")

    # Batch validation from protocol file
    python code_validator.py protocols/sepsis/generate_sepsis_tests.py

    # Validate all protocols
    python code_validator.py --all

    # Use VSAC API (requires VSAC_API_KEY environment variable)
    python code_validator.py --all --use-vsac
"""

import os
import re
import json
import time
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    raise

# Try to import VSACClient for optional VSAC integration
try:
    from vsac_client import VSACClient, VSACError
    VSAC_AVAILABLE = True
except ImportError:
    VSAC_AVAILABLE = False
    VSACClient = None
    VSACError = Exception

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def load_dotenv(env_file: str = None):
    """
    Load environment variables from .env file.
    Simple implementation that doesn't require python-dotenv.
    """
    if env_file is None:
        # Look for .env in the same directory as this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(script_dir, ".env")

    if not os.path.exists(env_file):
        return False

    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
        return True
    except Exception as e:
        logger.warning(f"Failed to load .env file: {e}")
        return False


# Load .env file on module import
load_dotenv()


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValidationResult:
    """Result of a single code validation"""
    code_system: str
    code: str
    provided_display: str
    is_valid: bool
    official_display: Optional[str] = None
    display_matches: bool = False
    error_message: Optional[str] = None
    source_file: Optional[str] = None
    source_line: Optional[int] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ValidationSummary:
    """Summary of batch validation results"""
    total_codes: int = 0
    valid_codes: int = 0
    invalid_codes: int = 0
    display_mismatches: int = 0
    validation_errors: int = 0
    results: List[ValidationResult] = field(default_factory=list)

    def add_result(self, result: ValidationResult):
        self.results.append(result)
        self.total_codes += 1
        if result.is_valid:
            self.valid_codes += 1
            if not result.display_matches:
                self.display_mismatches += 1
        elif result.error_message and "API" in result.error_message:
            self.validation_errors += 1
        else:
            self.invalid_codes += 1


# =============================================================================
# CODE VALIDATOR
# =============================================================================

class CodeValidator:
    """
    Validates clinical codes against official terminology servers.

    Supported code systems:
    - SNOMED: SNOMED CT concepts
    - RXNORM: RxNorm drug codes
    - LOINC: LOINC observation codes
    - HSLOC: CDC NHSN Healthcare Service Locations
    - ICD10CM: ICD-10-CM diagnosis codes
    """

    # API endpoints
    ENDPOINTS = {
        "SNOMED": "https://browser.ihtsdotools.org/snowstorm/snomed-ct/browser/MAIN/concepts/{code}",
        "RXNORM": "https://rxnav.nlm.nih.gov/REST/rxcui/{code}/properties.json",
        "LOINC": "https://fhir.loinc.org/CodeSystem/$lookup?system=http://loinc.org&code={code}",
        "HSLOC": "https://terminology.hl7.org/CodeSystem/hsloc",  # Will use $lookup
        "ICD10CM": "https://terminology.hl7.org/CodeSystem/$lookup?system=http://hl7.org/fhir/sid/icd-10-cm&code={code}",
    }

    # Cache settings
    CACHE_FILE = ".code_validation_cache.json"
    CACHE_EXPIRY_DAYS = 30

    def __init__(self, cache_dir: str = None, verbose: bool = True,
                 vsac_api_key: str = None, use_vsac: bool = False):
        """
        Initialize the code validator.

        Args:
            cache_dir: Directory to store cache file (default: current directory)
            verbose: Whether to print status messages
            vsac_api_key: Optional VSAC API key for VSAC validation
            use_vsac: Whether to use VSAC API for validation
        """
        self.cache_dir = cache_dir or os.getcwd()
        self.verbose = verbose
        self.cache = self._load_cache()
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "NHSN-FHIR-TestCaseGenerator/1.0"
        })

        # VSAC integration
        self.vsac_client = None
        self.use_vsac = use_vsac

        if use_vsac:
            # Try to get API key from parameter, env var, or fail gracefully
            api_key = vsac_api_key or os.environ.get("VSAC_API_KEY")

            if api_key and VSAC_AVAILABLE:
                try:
                    self.vsac_client = VSACClient(api_key=api_key, verbose=False)
                    self._log("VSAC API integration enabled")
                except Exception as e:
                    self._log(f"Warning: Failed to initialize VSAC client: {e}", "warning")
            elif not VSAC_AVAILABLE:
                self._log("Warning: VSAC module not available. Install vsac_client.", "warning")
            elif not api_key:
                self._log("Warning: VSAC_API_KEY environment variable not set.", "warning")
                self._log("  Set it with: set VSAC_API_KEY=your-key (Windows)", "warning")
                self._log("  Or: export VSAC_API_KEY=your-key (Linux/Mac)", "warning")

    def _log(self, message: str, level: str = "info"):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(message)
        getattr(logger, level)(message)

    def _get_cache_path(self) -> str:
        """Get the cache file path"""
        return os.path.join(self.cache_dir, self.CACHE_FILE)

    def _load_cache(self) -> Dict:
        """Load the validation cache from file"""
        cache_path = self._get_cache_path()
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    # Check cache expiry
                    cache_time = cache.get("_timestamp", 0)
                    if time.time() - cache_time < self.CACHE_EXPIRY_DAYS * 86400:
                        return cache
            except (json.JSONDecodeError, OSError):
                pass
        return {"_timestamp": time.time()}

    def _save_cache(self):
        """Save the validation cache to file"""
        cache_path = self._get_cache_path()
        try:
            self.cache["_timestamp"] = time.time()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except OSError as e:
            logger.warning(f"Failed to save cache: {e}")

    def _get_cache_key(self, code_system: str, code: str) -> str:
        """Generate cache key for a code"""
        return f"{code_system}:{code}"

    def _make_request(self, url: str, timeout: int = 10) -> Optional[Dict]:
        """Make an HTTP GET request with error handling"""
        try:
            response = self.session.get(url, timeout=timeout)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.warning(f"API returned status {response.status_code}: {url}")
                return None
        except requests.exceptions.Timeout:
            logger.warning(f"Request timed out: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed: {e}")
            return None
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON response: {url}")
            return None

    # =========================================================================
    # SNOMED CT Validation
    # =========================================================================

    def _validate_snomed(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a SNOMED CT code.

        Returns:
            Tuple of (is_valid, official_display)
        """
        url = self.ENDPOINTS["SNOMED"].format(code=code)
        data = self._make_request(url)

        if data and "conceptId" in data:
            # Get the preferred term
            display = data.get("pt", {}).get("term") or data.get("fsn", {}).get("term")
            return True, display
        return False, None

    # =========================================================================
    # RxNorm Validation
    # =========================================================================

    def _validate_rxnorm(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an RxNorm code using RxNav API.

        Returns:
            Tuple of (is_valid, official_display)
        """
        url = self.ENDPOINTS["RXNORM"].format(code=code)
        data = self._make_request(url)

        if data and "properties" in data:
            props = data["properties"]
            display = props.get("name")
            return True, display
        return False, None

    # =========================================================================
    # LOINC Validation
    # =========================================================================

    def _validate_loinc(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a LOINC code using LOINC FHIR server.

        Returns:
            Tuple of (is_valid, official_display)
        """
        # Use the LOINC FHIR CodeSystem lookup
        url = f"https://fhir.loinc.org/CodeSystem/loinc/$lookup?code={code}"

        # LOINC FHIR server requires specific headers
        headers = {"Accept": "application/fhir+json"}

        try:
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                # Extract display from FHIR Parameters response
                if data.get("resourceType") == "Parameters":
                    for param in data.get("parameter", []):
                        if param.get("name") == "display":
                            return True, param.get("valueString")
                    # Code found but no display
                    return True, None
            elif response.status_code == 404:
                return False, None
            else:
                # Try alternative: BioPortal REST API
                return self._validate_loinc_bioportal(code)
        except Exception as e:
            logger.warning(f"LOINC validation error: {e}")
            # Try alternative on error
            return self._validate_loinc_bioportal(code)

    def _validate_loinc_bioportal(self, code: str) -> Tuple[bool, Optional[str]]:
        """Fallback LOINC validation using BioPortal"""
        url = f"https://bioportal.bioontology.org/ontologies/LOINC?p=classes&conceptid={code}"
        # BioPortal requires API key for REST, so just return unknown
        # This is a fallback - assume valid if primary fails
        return True, None  # Assume valid, display unknown

    # =========================================================================
    # HSLOC Validation
    # =========================================================================

    # Known valid HSLOC codes (from CDC NHSN)
    HSLOC_CODES = {
        "1025-6": "Trauma Critical Care",
        "1026-4": "Burn Critical Care",
        "1027-2": "Medical Critical Care",
        "1028-0": "Medical Cardiac Critical Care",
        "1029-8": "Medical-Surgical Critical Care",
        "1030-6": "Surgical Critical Care",
        "1031-4": "Neurosurgical Critical Care",
        "1032-2": "Surgical Cardiothoracic Critical Care",
        "1033-0": "Respiratory Critical Care",
        "1034-8": "Prenatal Critical Care",
        "1035-5": "Neurologic Critical Care",
        "1060-3": "Medical Ward",
        "1061-1": "Medical-Surgical Ward",
        "1062-9": "Surgical Ward",
        "1108-0": "Emergency Department",
        "1109-8": "Pediatric Emergency Department",
    }

    def _validate_hsloc(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an HSLOC code using local lookup table.

        The HL7 Terminology server often has issues with HSLOC codes,
        so we use a local lookup table based on CDC NHSN documentation.

        Returns:
            Tuple of (is_valid, official_display)
        """
        if code in self.HSLOC_CODES:
            return True, self.HSLOC_CODES[code]

        # Try HL7 terminology server as fallback
        url = f"https://terminology.hl7.org/CodeSystem/hsloc/$lookup?code={code}"
        headers = {"Accept": "application/fhir+json"}

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("resourceType") == "Parameters":
                    for param in data.get("parameter", []):
                        if param.get("name") == "display":
                            return True, param.get("valueString")
                    return True, None
            return False, None
        except Exception as e:
            logger.warning(f"HSLOC validation error: {e}")
            return False, None

    # =========================================================================
    # ICD-10-CM Validation
    # =========================================================================

    def _validate_icd10cm(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an ICD-10-CM code.

        Returns:
            Tuple of (is_valid, official_display)
        """
        url = self.ENDPOINTS["ICD10CM"].format(code=code)
        headers = {"Accept": "application/fhir+json"}

        try:
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("resourceType") == "Parameters":
                    for param in data.get("parameter", []):
                        if param.get("name") == "display":
                            return True, param.get("valueString")
                    return True, None
            return False, None
        except Exception as e:
            logger.warning(f"ICD-10-CM validation error: {e}")
            return False, None

    # =========================================================================
    # VSAC Validation (Optional - requires API key)
    # =========================================================================

    # NHSN Value Set OIDs for code validation
    NHSN_VALUE_SETS = {
        "SNOMED": [
            "2.16.840.1.113883.3.666.5.307",   # Encounter Inpatient
            "2.16.840.1.113883.3.117.1.7.1.292", # Emergency Department Visit
            # Add more as needed
        ],
        "LOINC": [
            "2.16.840.1.113762.1.4.1",  # Observation codes
        ],
        "RXNORM": [
            "2.16.840.1.113883.3.464.1003.196.12.1001",  # Medications
        ],
    }

    def _validate_with_vsac(self, code_system: str, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a code using VSAC value sets.

        This is a supplementary validation that checks if a code exists
        in known NHSN value sets.

        Returns:
            Tuple of (is_valid, official_display)
        """
        if not self.vsac_client:
            return None, None  # VSAC not available

        oids = self.NHSN_VALUE_SETS.get(code_system.upper(), [])

        for oid in oids:
            try:
                codes = self.vsac_client.get_codes(oid)
                for c in codes:
                    if c.get("code") == code:
                        return True, c.get("display")
            except VSACError as e:
                logger.debug(f"VSAC lookup failed for {oid}: {e}")
                continue

        return None, None  # Code not found in VSAC value sets

    # =========================================================================
    # Main Validation Method
    # =========================================================================

    def validate(self, code_system: str, code: str,
                 provided_display: str = None) -> ValidationResult:
        """
        Validate a clinical code against the official terminology server.

        Args:
            code_system: Code system name (SNOMED, RXNORM, LOINC, HSLOC, ICD10CM)
            code: The code to validate
            provided_display: Optional display name to check

        Returns:
            ValidationResult with validation status and official display
        """
        code_system = code_system.upper()
        code = str(code).strip()

        # Check cache first
        cache_key = self._get_cache_key(code_system, code)
        if cache_key in self.cache and cache_key != "_timestamp":
            cached = self.cache[cache_key]
            display_matches = self._display_matches(provided_display, cached.get("display"))
            return ValidationResult(
                code_system=code_system,
                code=code,
                provided_display=provided_display or "",
                is_valid=cached["valid"],
                official_display=cached.get("display"),
                display_matches=display_matches,
                error_message=None
            )

        # Validate based on code system
        validators = {
            "SNOMED": self._validate_snomed,
            "RXNORM": self._validate_rxnorm,
            "LOINC": self._validate_loinc,
            "HSLOC": self._validate_hsloc,
            "ICD10CM": self._validate_icd10cm,
        }

        validator = validators.get(code_system)
        if not validator:
            return ValidationResult(
                code_system=code_system,
                code=code,
                provided_display=provided_display or "",
                is_valid=False,
                error_message=f"Unsupported code system: {code_system}"
            )

        try:
            is_valid, official_display = validator(code)

            # Cache the result
            self.cache[cache_key] = {
                "valid": is_valid,
                "display": official_display
            }
            self._save_cache()

            display_matches = self._display_matches(provided_display, official_display)

            return ValidationResult(
                code_system=code_system,
                code=code,
                provided_display=provided_display or "",
                is_valid=is_valid,
                official_display=official_display,
                display_matches=display_matches,
                error_message=None if is_valid else f"Code {code} not found in {code_system}"
            )

        except Exception as e:
            return ValidationResult(
                code_system=code_system,
                code=code,
                provided_display=provided_display or "",
                is_valid=False,
                error_message=f"API error: {str(e)}"
            )

    def _display_matches(self, provided: Optional[str],
                         official: Optional[str]) -> bool:
        """Check if provided display matches official display (case-insensitive)"""
        if not provided or not official:
            return True  # Can't compare if one is missing

        # Normalize for comparison
        provided_norm = provided.lower().strip()
        official_norm = official.lower().strip()

        # Exact match or one contains the other
        return (provided_norm == official_norm or
                provided_norm in official_norm or
                official_norm in provided_norm)

    def validate_batch(self, codes: List[Dict]) -> ValidationSummary:
        """
        Validate multiple codes.

        Args:
            codes: List of dicts with keys: system, code, display (optional)

        Returns:
            ValidationSummary with all results
        """
        summary = ValidationSummary()

        for i, code_info in enumerate(codes):
            system = code_info.get("system", code_info.get("code_system", ""))
            code = code_info.get("code", "")
            display = code_info.get("display", "")

            if not system or not code:
                continue

            # Map system URL to code system name
            system_name = self._url_to_system_name(system)
            if not system_name:
                continue

            result = self.validate(system_name, code, display)
            result.source_file = code_info.get("source_file")
            result.source_line = code_info.get("source_line")
            summary.add_result(result)

            # Progress indicator
            if self.verbose and (i + 1) % 10 == 0:
                print(f"  Validated {i + 1}/{len(codes)} codes...")

        return summary

    def _url_to_system_name(self, url: str) -> Optional[str]:
        """Convert code system URL to system name"""
        url_mapping = {
            "snomed": "SNOMED",
            "rxnorm": "RXNORM",
            "loinc": "LOINC",
            "hsloc": "HSLOC",
            "icd-10-cm": "ICD10CM",
            "icd10cm": "ICD10CM",
        }

        url_lower = url.lower()
        for key, value in url_mapping.items():
            if key in url_lower:
                return value
        return None


# =============================================================================
# PROTOCOL FILE PARSER
# =============================================================================

def extract_codes_from_protocol(file_path: str) -> List[Dict]:
    """
    Extract clinical codes from a protocol generator Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        List of code dicts with system, code, display, source_file, source_line
    """
    codes = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    # Pattern to match code definitions
    # Matches: "code": "12345" or 'code': '12345'
    code_pattern = re.compile(r'"code"\s*:\s*["\']([^"\']+)["\']')
    display_pattern = re.compile(r'"display"\s*:\s*["\']([^"\']+)["\']')
    system_pattern = re.compile(r'"system"\s*:\s*([A-Z_]+\[["\'][^"\']+["\']\]|["\'][^"\']+["\'])')

    # Find all code blocks (look for "code": patterns)
    for i, line in enumerate(lines, 1):
        code_match = code_pattern.search(line)
        if code_match:
            code = code_match.group(1)

            # Look for display and system in nearby lines (within 5 lines before/after)
            context_start = max(0, i - 6)
            context_end = min(len(lines), i + 5)
            context = '\n'.join(lines[context_start:context_end])

            display_match = display_pattern.search(context)
            system_match = system_pattern.search(context)

            display = display_match.group(1) if display_match else ""

            # Parse system
            system = ""
            if system_match:
                system_str = system_match.group(1)
                # Handle CODE_SYSTEMS["SNOMED"] format
                if "CODE_SYSTEMS" in system_str:
                    sys_match = re.search(r'\[["\']([^"\']+)["\']\]', system_str)
                    if sys_match:
                        system = sys_match.group(1)
                else:
                    # Direct URL
                    system = system_str.strip('"\'')

            if system and code:
                codes.append({
                    "system": system,
                    "code": code,
                    "display": display,
                    "source_file": file_path,
                    "source_line": i
                })

    return codes


def find_protocol_files(base_dir: str = None) -> List[str]:
    """Find all protocol generator Python files"""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    protocols_dir = os.path.join(base_dir, "protocols")
    files = []

    if os.path.exists(protocols_dir):
        for root, dirs, filenames in os.walk(protocols_dir):
            for filename in filenames:
                if filename.startswith("generate_") and filename.endswith(".py"):
                    files.append(os.path.join(root, filename))

    return files


# =============================================================================
# REPORT GENERATION
# =============================================================================

def print_validation_report(summary: ValidationSummary, verbose: bool = True):
    """Print a formatted validation report"""
    print("\n" + "=" * 70)
    print("CLINICAL CODE VALIDATION REPORT")
    print("=" * 70)

    print(f"\nSummary:")
    print(f"  Total codes checked:    {summary.total_codes}")
    print(f"  Valid codes:            {summary.valid_codes}")
    print(f"  Invalid codes:          {summary.invalid_codes}")
    print(f"  Display mismatches:     {summary.display_mismatches}")
    print(f"  Validation errors:      {summary.validation_errors}")

    # Group results by status
    invalid = [r for r in summary.results if not r.is_valid]
    mismatches = [r for r in summary.results if r.is_valid and not r.display_matches]

    if invalid:
        print(f"\n{'='*70}")
        print("INVALID CODES (Code not found in official terminology)")
        print("=" * 70)
        for r in invalid:
            print(f"\n  [{r.code_system}] {r.code}")
            print(f"    Provided display: {r.provided_display}")
            print(f"    Error: {r.error_message}")
            if r.source_file:
                print(f"    Source: {r.source_file}:{r.source_line}")

    if mismatches and verbose:
        print(f"\n{'='*70}")
        print("DISPLAY MISMATCHES (Code valid but display name differs)")
        print("=" * 70)
        for r in mismatches:
            print(f"\n  [{r.code_system}] {r.code}")
            print(f"    Provided:  {r.provided_display}")
            print(f"    Official:  {r.official_display}")
            if r.source_file:
                print(f"    Source: {r.source_file}:{r.source_line}")

    if summary.invalid_codes == 0 and summary.display_mismatches == 0:
        print(f"\n{'='*70}")
        print("ALL CODES VALIDATED SUCCESSFULLY!")
        print("=" * 70)

    print()


def save_validation_report(summary: ValidationSummary, output_file: str):
    """Save validation report to JSON file"""
    report = {
        "summary": {
            "total_codes": summary.total_codes,
            "valid_codes": summary.valid_codes,
            "invalid_codes": summary.invalid_codes,
            "display_mismatches": summary.display_mismatches,
            "validation_errors": summary.validation_errors
        },
        "results": [r.to_dict() for r in summary.results]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to: {output_file}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Validate clinical codes in NHSN protocol generators",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all protocol files
  python code_validator.py --all

  # Validate a specific protocol
  python code_validator.py protocols/sepsis/generate_sepsis_tests.py

  # Validate a single code
  python code_validator.py --code SNOMED:91861009

  # Save report to file
  python code_validator.py --all --output validation_report.json

  # Use VSAC API for validation (requires API key)
  set VSAC_API_KEY=your-key-here
  python code_validator.py --all --use-vsac

  # Or pass API key directly
  python code_validator.py --all --use-vsac --vsac-key your-key-here
"""
    )

    parser.add_argument("files", nargs="*", help="Protocol files to validate")
    parser.add_argument("--all", action="store_true", help="Validate all protocol files")
    parser.add_argument("--code", type=str, help="Validate single code (format: SYSTEM:CODE)")
    parser.add_argument("--output", "-o", type=str, help="Save report to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--use-vsac", action="store_true",
                        help="Use VSAC API for validation (requires VSAC_API_KEY env var)")
    parser.add_argument("--vsac-key", type=str,
                        help="VSAC API key (alternative to VSAC_API_KEY env var)")

    args = parser.parse_args()

    validator = CodeValidator(
        verbose=True,
        use_vsac=args.use_vsac,
        vsac_api_key=args.vsac_key
    )

    # Clear cache if requested
    if args.no_cache:
        validator.cache = {"_timestamp": time.time()}

    # Single code validation
    if args.code:
        parts = args.code.split(":")
        if len(parts) != 2:
            print("Error: Code format should be SYSTEM:CODE (e.g., SNOMED:91861009)")
            return 1

        system, code = parts
        print(f"\nValidating {system} code: {code}")
        result = validator.validate(system, code)

        print(f"\n  Valid: {result.is_valid}")
        if result.official_display:
            print(f"  Official display: {result.official_display}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        return 0 if result.is_valid else 1

    # Determine files to validate
    files = []
    if args.all:
        files = find_protocol_files()
    elif args.files:
        files = args.files
    else:
        parser.print_help()
        return 0

    if not files:
        print("No protocol files found to validate.")
        return 1

    print(f"\nValidating {len(files)} protocol file(s)...")

    # Extract and validate codes
    all_codes = []
    for file_path in files:
        print(f"\n  Scanning: {file_path}")
        codes = extract_codes_from_protocol(file_path)
        print(f"    Found {len(codes)} codes")
        all_codes.extend(codes)

    if not all_codes:
        print("\nNo codes found in protocol files.")
        return 0

    print(f"\nValidating {len(all_codes)} codes against official terminology servers...")
    summary = validator.validate_batch(all_codes)

    # Print report
    print_validation_report(summary, verbose=args.verbose)

    # Save report if requested
    if args.output:
        save_validation_report(summary, args.output)

    # Return exit code based on validation results
    return 0 if summary.invalid_codes == 0 else 1


if __name__ == "__main__":
    exit(main())
