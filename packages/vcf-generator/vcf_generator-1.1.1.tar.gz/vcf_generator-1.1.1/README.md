[![build status](https://github.com/talk2bryan/vcf-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/talk2bryan/vcf-generator/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/talk2bryan/vcf-generator/graph/badge.svg?token=IHS7IJ3RPN)](https://codecov.io/gh/talk2bryan/vcf-generator)
[![PyPI version](https://badge.fury.io/py/vcf-generator.svg)](https://badge.fury.io/py/vcf-generator)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vcf-generator)](https://pypi.org/project/vcf-generator/)
[![PyPI - License](https://img.shields.io/pypi/l/vcf-generator)](https://pypi.org/project/vcf-generator/)
[![PyPI - Format](https://img.shields.io/pypi/format/vcf-generator)](https://pypi.org/project/vcf-generator/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/vcf-generator)](https://pypi.org/project/vcf-generator/)

# vcf-generator

A simple VCF generator. Generate VCF files with random data.

## Installation
Using pip:
```bash
pip install vcf-generator
```
## Quick Start
```bash
$ vcf-generator vcards --output-file test.vcf --num_contacts 1000
$ vcf-generator contacts_str --output-file test.txt --num_contacts 1000
```

## Command Line Interface
```bash
$ vcf-generator --help
Usage: vcf-generator [OPTIONS] COMMAND [ARGS]...
Options:
  --help  Show this message and exit.
Commands:
    contacts_str  Generate contacts as string
    vcards        Generate contacts in VCF format (4.0)
```

See help for each command:

```bash
$ vcf-generator COMMAND --help
Usage: vcf-generator COMMAND [OPTIONS]
  Generate contacts in VCF format (4.0)
Options:
    -o, --output-file TEXT  Output file  [optional]
    -n, --num_contacts INTEGER  Number of contacts to generate  [optional]
    --help              Show this message and exit.
```


## Examples
### Generate VCF data with 1 contact
```bash
$ vcf-generator vcards
```

The above command will generate 1 contact as a VCF string and print the content to the console:

```bash
BEGIN:VCARD
VERSION:4.0
N:None;Laura;Valerie;;Miss
FN:Laura Valerie
TITLE:Miss
TEL;TYPE#HOME,voice;VALUE#uri:tel:+859-422-5863580
TEL;TYPE#MOBILE,voice;VALUE#uri:tel:+528-463-7642962
TEL;TYPE#MOBILE,voice;VALUE#uri:tel:+51-666-1415776
ADR;TYPE#WORK;PREF#1;LABEL#13962 Casey Spring Suite 931
Xavierfurt, VT 65391
Suriname:;;13962 Casey Spring Suite 931;Xavierfurt;VT;65391;Suriname
ADR;TYPE#OTHER;PREF#2;LABEL#33446 Deanna Prairie Apt. 140
Mcguireport, NJ 64518
Tokelau:;;33446 Deanna Prairie Apt. 140;Mcguireport;NJ;64518;Tokelau
BDAY:1959-08-06
EMAIL:caleb93@example.org
EMAIL:christopherblankenship@example.org
EMAIL:michaelwhite@example.org
END:VCARD
```

### Generate 1 contact as string
```bash
$ vcf-generator contacts_str
```

The above command will generate 1 contact information and print the content to the console:

```bash
Name: Charles Rebekah - Ind.
DOB: 1953-11-18
Phone Numbers: HOME: +738 (250) 705-2590. OTHER: +432 (509) 404-8152. MOBILE: +601 (647) 746-1060
Emails: OTHER: daniel03@example.org
Addresses: OTHER: 557 Ruiz Avenue, 7934 Westmouth, KY 56508 Guyana
```
