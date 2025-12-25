#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MADiE Exporter

Creates MADiE-compatible test case output structure including:
- Folder structure with UUID-named directories
- .madie metadata file
- README.txt mapping file
- ZIP archive for import
"""

import os
import json
import uuid
import shutil
import zipfile
from typing import Dict, List, Any, Optional

from .bundle_generator import FHIRBundleGenerator


class MADiEExporter:
    """
    Creates MADiE-compatible test case export structure.

    Usage:
        exporter = MADiEExporter("ACHMeasureMing", "0.0.000")
        exporter.add_test_case(gen, "QualEncPass", "EncInpatient", "Tests inpatient encounter", {"initialPopulation": 1})
        exporter.export()
    """

    def __init__(self,
                 measure_name: str,
                 version: str,
                 measure_url: str = None,
                 measurement_period_start: str = "2022-01-01",
                 measurement_period_end: str = "2022-01-31"):
        """
        Initialize the MADiE exporter.

        Args:
            measure_name: Name of the measure (e.g., "ACHMeasureMing")
            version: Version string (e.g., "0.0.000")
            measure_url: URL of the measure (auto-generated if not provided)
            measurement_period_start: Start of measurement period (YYYY-MM-DD)
            measurement_period_end: End of measurement period (YYYY-MM-DD)
        """
        self.measure_name = measure_name
        self.version = version
        self.measure_url = measure_url or f"https://madie.cms.gov/Measure/{measure_name}"
        self.measurement_period_start = measurement_period_start
        self.measurement_period_end = measurement_period_end

        self.test_cases = []

    def _generate_test_case_id(self) -> str:
        """Generate a MongoDB-style ObjectId (24 hex characters)"""
        return uuid.uuid4().hex[:24]

    def add_test_case(self,
                      generator_func,
                      series: str,
                      title: str,
                      description: str,
                      expected_populations: Dict[str, int] = None):
        """
        Add a test case to be exported.

        Args:
            generator_func: Function that returns a FHIRBundleGenerator
            series: Test series name (e.g., "QualEncPass")
            title: Test title (e.g., "EncInpatient")
            description: Description of what this test case tests
            expected_populations: Dict of population names to expected counts
                                  e.g., {"initialPopulation": 1}
        """
        if expected_populations is None:
            # Infer from series name
            if "Fail" in series:
                expected_populations = {"initialPopulation": 0}
            else:
                expected_populations = {"initialPopulation": 1}

        self.test_cases.append({
            "generator_func": generator_func,
            "series": series,
            "title": title,
            "description": description,
            "expected_populations": expected_populations
        })

    def add_test_case_from_generator(self,
                                      generator: FHIRBundleGenerator,
                                      series: str,
                                      title: str,
                                      description: str,
                                      expected_populations: Dict[str, int] = None):
        """
        Add a test case using an existing generator instance.

        Args:
            generator: FHIRBundleGenerator instance with resources already added
            series: Test series name
            title: Test title
            description: Description
            expected_populations: Expected population counts
        """
        # Wrap the generator in a function
        def gen_func():
            return generator

        self.add_test_case(gen_func, series, title, description, expected_populations)

    def export(self, output_dir: str = None, create_zip: bool = True) -> str:
        """
        Export all test cases to MADiE-compatible format.

        Args:
            output_dir: Output directory path (auto-generated if not provided)
            create_zip: Whether to create a ZIP file

        Returns:
            Path to the output directory (or ZIP file if create_zip=True)
        """
        if output_dir is None:
            output_dir = f"{self.measure_name}-v{self.version}-FHIR-TestCases"

        zip_file = f"{output_dir}.zip"

        # Clean up old output
        if os.path.exists(output_dir):
            print(f"Removing old directory: {output_dir}")
            shutil.rmtree(output_dir)
        if os.path.exists(zip_file):
            print(f"Removing old zip: {zip_file}")
            os.remove(zip_file)

        os.makedirs(output_dir, exist_ok=True)

        print("=" * 70)
        print(f"{self.measure_name} Test Case Export")
        print("=" * 70)
        print(f"Measure: {self.measure_name} v{self.version}")
        print(f"Measurement Period: {self.measurement_period_start} to {self.measurement_period_end}")
        print(f"Test Cases: {len(self.test_cases)}")
        print()

        madie_metadata = []

        # Generate each test case
        for i, tc in enumerate(self.test_cases, 1):
            series = tc["series"]
            title = tc["title"]
            description = tc["description"]
            expected_populations = tc["expected_populations"]
            generator_func = tc["generator_func"]

            print(f"[{i:2d}] Generating: {series}-{title}")

            # Create UUID for test case directory - this will also be the patient ID
            patient_id = str(uuid.uuid4())
            test_case_id = self._generate_test_case_id()

            # Create test case directory
            test_case_dir = os.path.join(output_dir, patient_id)
            os.makedirs(test_case_dir, exist_ok=True)

            # Create generator with the patient_id matching the folder UUID
            gen = FHIRBundleGenerator(f"{series}_{title}", patient_id=patient_id)

            # Call the generator function to get a configured generator
            source_gen = generator_func()

            # Copy the bundle structure
            gen.bundle = source_gen.bundle

            # Update patient ID in all resources
            self._update_patient_references(gen, patient_id, series, title)

            # Add MeasureReport with expected population values
            gen.patient_id = patient_id
            gen.add_measure_report(
                description=description,
                measure_url=self.measure_url,
                measurement_period_start=self.measurement_period_start,
                measurement_period_end=self.measurement_period_end,
                expected_populations=expected_populations
            )

            # Filename format: MeasureName-Version-SeriesTitle.json
            filename = f"{self.measure_name}-v{self.version}-{series}{title}.json"
            filepath = os.path.join(test_case_dir, filename)

            # Save test case
            gen.save(filepath)

            # Add to .madie metadata
            madie_metadata.append({
                "testCaseId": test_case_id,
                "patientId": patient_id,
                "title": f"{series}{title}",
                "series": "",  # Empty string matches MADiE export format
                "description": description
            })

        # Generate README.txt
        readme_path = os.path.join(output_dir, "README.txt")
        self._create_readme(readme_path, madie_metadata)
        print(f"\n  Created README: {readme_path}")

        # Generate .madie metadata file
        madie_path = os.path.join(output_dir, ".madie")
        with open(madie_path, 'w', newline='\n') as f:
            json.dump(madie_metadata, f)
        print(f"  Created .madie: {madie_path}")

        # Print summary
        self._print_summary(madie_metadata)

        # Create zip file
        if create_zip:
            self._create_zip(output_dir, zip_file)
            print(f"\n  Zip created: {zip_file}")
            return zip_file

        return output_dir

    def _update_patient_references(self,
                                    gen: FHIRBundleGenerator,
                                    patient_id: str,
                                    series: str,
                                    title: str):
        """Update all patient references in the bundle to use the new patient ID"""
        for entry in gen.bundle["entry"]:
            resource = entry["resource"]

            # Update Patient resource
            if resource["resourceType"] == "Patient":
                resource["id"] = patient_id
                entry["fullUrl"] = f"https://madie.cms.gov/Patient/{patient_id}"
                entry["request"]["url"] = f"Patient/{patient_id}"

                # Update identifier value
                if "identifier" in resource:
                    for identifier in resource["identifier"]:
                        identifier["value"] = patient_id

                # Update name to use series/title format
                if "name" in resource:
                    resource["name"] = [{"family": series, "given": [title]}]

            # Update references to patient
            elif "subject" in resource:
                resource["subject"]["reference"] = f"Patient/{patient_id}"

            if "beneficiary" in resource:
                resource["beneficiary"]["reference"] = f"Patient/{patient_id}"

            if "patient" in resource and isinstance(resource["patient"], dict):
                resource["patient"]["reference"] = f"Patient/{patient_id}"

    def _create_readme(self, filepath: str, metadata: List[Dict]):
        """Create README.txt with UUID to name mapping"""
        with open(filepath, 'w', newline='\n') as f:
            f.write("The purpose of this file is to allow users to view the mapping of test case names to their test case UUIDs.\n")
            f.write("In order to find a specific test case file in the export, first locate the test case name in this document\n")
            f.write("and then use the associated UUID to find the name of the folder in the export.\n\n")
            for i, tc in enumerate(metadata, 1):
                f.write(f"Case # {i} - {tc['patientId']} = {tc['series']}-{tc['title']}\n")

    def _print_summary(self, metadata: List[Dict]):
        """Print summary of generated test cases"""
        print("\n" + "=" * 70)
        print("Test Case Generation Summary")
        print("=" * 70)
        print(f"Total test cases generated: {len(metadata)}")

        # Group by series (extracted from title prefix)
        series_groups = {}
        for tc in metadata:
            # Extract series from title (assuming format like "QualEncPassEncInpatient")
            title = tc['title']
            # Try to find common series prefixes
            for prefix in ['QualEncTypePass', 'QualEncClassPass', 'QualEncStatusPass',
                          'QualEncPeriodPass', 'QualEncFail', 'EncLocPass', 'EncLocFail',
                          'BothPathsPass', 'SDEPass', 'NegationPass']:
                if title.startswith(prefix):
                    series = prefix
                    break
            else:
                # Use first word as series
                series = title.split('_')[0] if '_' in title else title

            if series not in series_groups:
                series_groups[series] = []
            series_groups[series].append(tc['title'])

        print("\nTest Cases by Category:")
        for series, titles in sorted(series_groups.items()):
            print(f"\n  {series}: {len(titles)} test cases")

    def _create_zip(self, source_dir: str, zip_path: str):
        """Create ZIP file with files at root level (not inside parent folder)"""
        print(f"\nCreating zip file: {zip_path}")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Get path relative to source_dir (not including source_dir itself)
                    rel_path = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, rel_path)
                    print(f"  Added: {rel_path}")

        print(f"\nNext steps:")
        print("1. Import the zip file into MADiE")
        print("2. Run measure execution")
        print("3. Verify each test case passes/fails as expected")


class TestCaseRegistry:
    """
    Registry for organizing test cases by category.

    Usage:
        registry = TestCaseRegistry()
        registry.add("QualEncTypePass", "EncInpatient", "Tests inpatient encounter", gen_func, {"initialPopulation": 1})
        exporter = MADiEExporter("MeasureName", "1.0.0")
        registry.register_all(exporter)
    """

    def __init__(self):
        self.test_cases = []

    def add(self,
            series: str,
            title: str,
            description: str,
            generator_func,
            expected_populations: Dict[str, int] = None):
        """
        Add a test case to the registry.

        Args:
            series: Test series name
            title: Test title
            description: Description
            generator_func: Function that returns FHIRBundleGenerator
            expected_populations: Expected population counts
        """
        self.test_cases.append({
            "series": series,
            "title": title,
            "description": description,
            "generator_func": generator_func,
            "expected_populations": expected_populations
        })

    def register_all(self, exporter: MADiEExporter):
        """
        Register all test cases with a MADiEExporter.

        Args:
            exporter: MADiEExporter instance
        """
        for tc in self.test_cases:
            exporter.add_test_case(
                generator_func=tc["generator_func"],
                series=tc["series"],
                title=tc["title"],
                description=tc["description"],
                expected_populations=tc["expected_populations"]
            )

    def __len__(self):
        return len(self.test_cases)

    def __iter__(self):
        return iter(self.test_cases)
