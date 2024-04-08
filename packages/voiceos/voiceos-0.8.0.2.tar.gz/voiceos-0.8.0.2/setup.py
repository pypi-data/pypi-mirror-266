from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


NAME = "voiceos"
VERSION = "0.8.0.2"
PYTHON_REQUIRES = ">=3.7"
REQUIRES = [
    "urllib3 >= 1.25.3, < 2.1.0",
    "python-dateutil",
    "pydantic >= 2",
    "typing-extensions >= 4.7.1",
]

setup(
    name=NAME,
    version=VERSION,
    description="VoiceOS Python SDK",
    author="WakoAI Inc",
    author_email="hello@wako.ai",
    url="https://github.com/WakoAi/voiceos-python",
    keywords=["VoiceOS", "VoiceOS Python ClientSDK", "VoiceOS Python"],
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description=long_description,
    package_data={"voiceos": ["py.typed"]},
)
