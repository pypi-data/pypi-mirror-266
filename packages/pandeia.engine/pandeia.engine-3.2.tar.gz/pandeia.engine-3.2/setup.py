#!/usr/bin/env python

# setuptools is required
from setuptools import setup

import subprocess

with open('README.md') as fp:
    description = fp.read()

# Versioning
try:
    DEVBUILD = subprocess.check_output(["git", "describe", "--tags"])
    with open('pandeia/engine/helpers/DEVBUILD', 'wb') as out:
        out.write(DEVBUILD)
except (subprocess.CalledProcessError, FileNotFoundError) as err:
    print(err)

setup(
    # The package
    name="pandeia.engine",
    version="3.2",
    packages=["pandeia",
              "pandeia.engine",
              "pandeia.engine.defaults",
              "pandeia.engine.helpers",
              "pandeia.engine.helpers.bit",
              "pandeia.engine.helpers.bit.config",
              "pandeia.engine.helpers.bit.etc_web_data",
              "pandeia.engine.helpers.bit.pyetc_form_defaults",
              "pandeia.engine.helpers.bit.instruments",
              "pandeia.engine.helpers.bit.instruments.hst",
              "pandeia.engine.helpers.bit.instruments.hst.acs",
              "pandeia.engine.helpers.bit.instruments.hst.acs.web",
              "pandeia.engine.helpers.bit.instruments.hst.cos",
              "pandeia.engine.helpers.bit.instruments.hst.cos.web",
              "pandeia.engine.helpers.bit.instruments.hst.stis",
              "pandeia.engine.helpers.bit.instruments.hst.stis.web",
              "pandeia.engine.helpers.bit.instruments.hst.wfc3ir",
              "pandeia.engine.helpers.bit.instruments.hst.wfc3ir.web",
              "pandeia.engine.helpers.bit.instruments.hst.wfc3uvis",
              "pandeia.engine.helpers.bit.instruments.hst.wfc3uvis.web",
              "pandeia.engine.helpers.peng",
              "pandeia.engine.helpers.schema",
              "pandeia.engine.helpers.background",
              "pandeia.engine.helpers.background.hst",
              "pandeia.engine.helpers.background.jwst"],

    # For PyPI
    description='Pandeia 3D Exposure Time Calculator compute engine',
    long_description=description,
    author='Adric Riedel, Isaac Spitzer, Dharini Chittiraibalan, Oi In Tam, Chris Sontag, Ivo Busko, Craig Jones, Tim Pickering, Klaus Pontoppidan',
    #author_email='https://stsci.service-now.com/jwst',
    url='https://jwst.etc.stsci.edu',
    classifiers=["Intended Audience :: Science/Research",
                 "License :: OSI Approved :: BSD License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "Programming Language :: Python :: 3.11",
                 "Topic :: Scientific/Engineering :: Astronomy",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    # Other notes
    package_data={
        "pandeia.engine.defaults": ["*.json"],
        "pandeia.engine.helpers": ["DEVBUILD"],
        "pandeia.engine.helpers.bit.instruments.hst.stis":     ["*.dat"],
        "pandeia.engine.helpers.bit.instruments.hst.cos":      ["*.dat"],
        "pandeia.engine.helpers.bit.instruments.hst.acs":      ["*.dat"],
        "pandeia.engine.helpers.bit.instruments.hst.wfc3uvis": ["*.dat"],
        "pandeia.engine.helpers.bit.instruments.hst.wfc3ir":   ["*.dat"],
        },
    include_package_data=True,
    install_requires=[
        "numpy>=1.17",
        "scipy>1.6",
        "astropy>=4",
        "photutils",
        "synphot",
        "stsynphot",
        "setuptools"
    ],
    zip_safe=False
)
