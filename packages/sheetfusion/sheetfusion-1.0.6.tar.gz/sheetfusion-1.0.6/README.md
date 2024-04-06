[python]: https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white
[version]: https://img.shields.io/badge/Version-1.0.5-blue

![python][python]
![version][version]

<p align="center">
  <img src="https://raw.githubusercontent.com/SMZ70/SheetFusion/master/assets/logo.png" alt="SheetFusion Logo" width="200">
</p>

<h1 align="center">SheetFusion</h1>

<p align="center">
  <b>Simple, user-friendly tool for merging cover sheets with document files.</b>
</p>


---
<p align="left" style="font-size: 1.5em; font-weight: bold;">Description</p>
SheetFusion is a simple, user-friendly tool designed to merge cover sheets with document files, primarily for academic and professional use. It automates the creation of personalized PDFs by combining individual cover pages with a standard document, such as exams or reports. This straightforward software offers a practical solution for those needing to distribute customized documents efficiently. It is written in Python and uses the [PyPDF3](https://github.com/sfneal/PyPDF3) library. It was created to merge cover sheets with exams. That is why the arguments are named as they are. However, it can be used to merge any PDF file with any other PDF file.

---


- [1. System Requirements](#1-system-requirements)
- [2. Installation](#2-installation)
  - [2.1. Using pip (recommended)](#21-using-pip-recommended)
  - [2.2. From source](#22-from-source)
- [3. Usage](#3-usage)
  - [3.1. Arguments](#31-arguments)
  - [3.2. Examples](#32-examples)
- [4. Change Log](#4-change-log)
- [5. License](#5-license)
- [6. Contact](#6-contact)

## 1. System Requirements

``SheetFusion`` runs on any system with ``Python`` installed:

- **Python:** Python 3.x is required. Verify your Python installation by running `python --version` or `python3 --version` in your command line.

- **Operating System:** Compatible with Windows, macOS, Linux, and any OS supporting Python.

## 2. Installation

### 2.1. Using pip (recommended)

```bash
python3 -m pip install sheetfusion
```

### 2.2. From source

You could use the following commands to clone and install SheetFusion. Make sure to replace X.X.X with the built version.

```bash
git clone https://github.com/SMZ70/SheetFusion.git
cd SheetFusion
python3 -m build
python3 -m pip install dist/sheetfusion-X.X.X.tar.gz
```

## 3. Usage

### 3.1. Arguments

`SheetFusion` is a command-line tool designed for merging cover sheets with exams. To use it, follow the command syntax below (see [Examples](#44-examples) for quick start).

```bash
python3 -m sheetfusion [--help] --cover-sheets --exam [--output-dir] [--overwrite]
```

or:

```bash
sheetfusion [--help] --cover-sheets --exam [--output-dir] [--overwrite]
```
#### 4.1. Help Options

- `--help`, `-h`  
  Show this help message and exit.

#### 4.2. Required Arguments

- `--cover-sheets`, `-c`  
  Specify the PDF file containing the cover sheets.
- `--exam`, `-e`  
  Specify the PDF file containing the exam.

#### 4.3. Optional Arguments

- `--output-dir`, `-o`  
  Define the directory to output the merged PDFs to.
- `--overwrite`  
  Enable overwriting of existing files.

### 3.2. Examples

The following examples demonstrate how to use `SheetFusion`:

#### Basic Usage

```bash
python3 -m sheetfusion -c cover_sheets.pdf -e exam.pdf
```

#### Specifying an Output Directory

```bash
python3 -m sheetfusion -c cover_sheets.pdf -e exam.pdf -o output_dir
```

#### Overwriting Existing Files

If the output directory already contains files with the same name as the merged PDFs, `SheetFusion` will not overwrite them by default. To enable overwriting, use the `--overwrite` flag.

```bash
python3 -m sheetfusion -c cover_sheets.pdf -e exam.pdf -o output_dir --overwrite
```

## 4. Change Log

See the [CHANGELOG](CHANGELOG.md) for more information.

## 5. License

`SheetFusion` is open-source software licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file in this repository.

## 6. Contact

Thank you for your interest in SheetFusion! For bug reports, feature requests, or general inquiries related to the project, please use [GitHub Issues](https://github.com/SMZ70/SheetFusion/issues). This is the fastest way to get your questions answered. It also allows other users to benefit from the discussion.
