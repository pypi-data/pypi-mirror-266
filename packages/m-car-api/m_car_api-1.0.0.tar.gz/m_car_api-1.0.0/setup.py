import os
import sys
from typing import Dict, List

from setuptools import find_namespace_packages, setup

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 10)
EGG_NAME = "m_car_api"


def list_packages(source_directory: str = "src") -> List[str]:
    packages = list(find_namespace_packages(source_directory, exclude="venv"))
    return packages


def list_namespace_packages(source_directory: str = "src") -> List[str]:
    return []


def get_package_dir() -> Dict[str, str]:
    if not os.path.isdir("src"):
        return {}
    return {"": "src"}


__version__ = "1.0.0"
requirements = ["requests", "pydantic>=2", "mujson", "pyproj"]
test_requirements = [
    "black>=19.10b0",
    "coverage>=5.1,<7",
    "faker>=18,<19",
    "flake8>=5.0.4,<6",
    "mypy>=0.961",
    "pre-commit>=3,<4",
    "pytest-cases>=3.1.1,<4",
    "pytest-html",
    "pytest>=7,<8",
    "pytest-mock>=3.5.1,<4",
    "python-dotenv>=1,<2",
    "python-semantic-release>=8,<9",
    "twine>=3.1.1,<4",
]


setup(
    name=EGG_NAME,
    version=__version__,
    python_requires=">={}.{}".format(*REQUIRED_PYTHON),
    url="https://github.com/cbrand/mapi",
    author="Christoph Brand",
    author_email="christoph@brand.rest",
    description="",
    long_description="",
    license="MIT",
    packages=list_packages(),
    package_dir=get_package_dir(),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    extras_require={"test": test_requirements},
    project_urls={"GitHub": "https://github.com/cbrand/m_car_api"},
    namespace_packages=list_namespace_packages(),
)
