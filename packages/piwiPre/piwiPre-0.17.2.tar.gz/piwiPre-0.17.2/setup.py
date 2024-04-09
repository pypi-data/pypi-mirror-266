import setuptools
from piwiPre.pwpVersion import PwpVersion

# CAVEAT : This file is edited by pwpPatcher.py to set up the version name from the latest tag
with open("README.md", "r") as fh:
    long_description = fh.read()

# see https://setuptools.pypa.io/en/latest/references/keywords.html
setuptools.setup(
    name="piwiPre",
    version=PwpVersion.spec,
    author="Fabien BATTINI",                    # noqa
    author_email="fabien.battini@gmail.com",
    description="piwigo picture preparation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/fabien.battini/piwipre",
    license_files=["LICENCE"],
    keywords='piwigo images pictures',
    packages=setuptools.find_packages(),
    classifiers=[
        # see https://pypi.org/classifiers/
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",  # noqa
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Office Suites",
    ],
    entry_points={
        'console_scripts': [
            'piwiPre = PiwiPre.pwpConfig:pwp_main', # noqa
        ]
    },
    python_requires='>=3.6',
)