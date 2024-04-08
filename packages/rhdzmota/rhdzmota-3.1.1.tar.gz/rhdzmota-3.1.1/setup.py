import os
import json
from typing import Dict, List
from setuptools import setup, find_namespace_packages


CODEBASE_PATH = os.environ.get(
    "CODEBASE_PATH",
    default=os.path.join("src", "main"),
)

DEPS_FILE = os.environ.get(
    "DEPS_FILE",
    default="",
)

with open("requirements.txt", "r") as file:
    requirements = [line for line in file.read().splitlines() if line and not line.startswith("#")]

with open(os.path.join(CODEBASE_PATH, "rhdzmota", "version"), "r") as file:
    version = file.read().strip()

with open("README.md") as file:
    readme = file.read()


def get_extras_requires(requirement_list: List[str]) -> Dict[str, List[str]]:
    extra_requires = {
        "baseline": set([]),
        "standalone": set([]),
        "all": set([]),
    }
    exclude = {}
    for line in requirement_list:
        line_with_tags = ":" in line
        line_comment = line.strip().startswith("#")
        if line_comment or not line_with_tags:
            print("Skipping requirement line: ", line)
            continue
        requirement, _, tags = line.partition(":")
        clean_requirement = requirement.strip()
        # Register clean requirement with "all" tag
        extra_requires["all"] = extra_requires["all"].union({clean_requirement})
        # Register clean requirement with corresponding tags
        for tag in tags.split(","):
            clean_tag = tag.strip()
            if not clean_tag.startswith("~"):
                extra_requires[clean_tag] = extra_requires.get(clean_tag, set([])).union({clean_requirement})
            else:
                reference_tag = clean_tag.replace("~", "").strip()
                exclude[reference_tag] = exclude.get(reference_tag, set([])).union({clean_requirement})
        if "standalone" in tags and "~" not in tags:
            extra_requires["baseline"] = extra_requires.get("baseline", set([])).union({clean_requirement})
    # Add the default requirements into all tags
    for tag in extra_requires.keys():
        if tag in ["standalone", "all", "baseline"]:
            continue
        extra_requires[tag] = extra_requires[tag].union(extra_requires["standalone"])
    return {
        tag: list(reqs - exclude.get(tag, set([])))
        for tag, reqs in extra_requires.items()
    }


dependencies = get_extras_requires(requirement_list=requirements)
if DEPS_FILE:
    with open(DEPS_FILE, "w") as file:
        file.write(json.dumps(dependencies, indent=4))

setup(
    name="rhdzmota",
    version=version,
    description="RHDZMOTA Package",
    long_description=readme,
    long_description_content_type='text/markdown',
    url="https://github.com/rhdzmota/package.rhdzmota.com",
    author="Rodrigo H. Mota",
    author_email="info@rhdzmota.com",
    packages=find_namespace_packages(where=CODEBASE_PATH),
    package_dir={
        "": CODEBASE_PATH
    },
    package_data={
        "": [
            os.path.join(CODEBASE_PATH, "rhdzmota", "iso3166", "datafiles", "*.json"),
            os.path.join(CODEBASE_PATH, "rhdzmota", "version"),
        ]
    },
    entry_points={
        "console_scripts": [
            "rhdzmota=rhdzmota.cli.main:main",
            "rhdzmota.ext=rhdzmota.cli.ext:ext",
        ]
    },
    install_requires=dependencies["baseline"],
    extras_require=dependencies,
    include_package_data=True,
    python_requires=">=3.8.10"
)
