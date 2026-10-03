"""Build runtime resources from canonical sources without maintaining duplicate copies."""

from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).parent


class ResourceBuild(build_py):
    def run(self):
        super().run()
        destination = Path(self.build_lib) / "vessell" / "_resources"
        self.mkpath(str(destination / "schemas"))
        self.copy_file(
            str(ROOT / "vesselframework_reference_v1.1_provenance_firewall.py"),
            str(destination / "reference.py"),
        )
        for schema in sorted((ROOT / "schemas").glob("*.json")):
            self.copy_file(str(schema), str(destination / "schemas" / schema.name))


setup(cmdclass={"build_py": ResourceBuild})
