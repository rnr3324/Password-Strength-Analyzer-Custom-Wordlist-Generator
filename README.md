# Password Strength Analyzer & Custom Wordlist Generator

A Python-based tool that analyzes password strength using `zxcvbn` and
generates custom password wordlists based on user inputs such as name,
birth year, pet name, favorite words, and numeric patterns. Includes CLI
and optional Tkinter GUI.

------------------------------------------------------------------------

## Features

### 🔐 Password Strength Analysis

-   Entropy calculation\
-   Crack-time estimation\
-   Feedback suggestions\
-   Strength score (0--4)

### 📝 Custom Wordlist Generator

-   Uses user-provided personal keywords\
-   Leetspeak mutations\
-   Capitalization variations\
-   Appends common patterns (123, 2024, !, @ etc.)\
-   Exports generated wordlist to `.txt`

### 🖥️ Interfaces

-   CLI support with `argparse`\
-   Optional Tkinter GUI

------------------------------------------------------------------------

## Installation

``` bash
pip install zxcvbn nltk
```

If zxcvbn fails, try:

``` bash
pip install zxcvbn-python
```

------------------------------------------------------------------------

## Usage

### CLI --- Analyze Password

``` bash
python password_tool.py --password "P@ssw0rd123"
```

### CLI --- Generate Wordlist

``` bash
python password_tool.py --name "raj" --pet "tommy" --dob "2006" --fav "guitar" --generate --output raj_list.txt
```

### Launch GUI

``` bash
python password_tool.py --gui
```

------------------------------------------------------------------------

## Project Structure

    project/
    │── password_tool.py
    │── README.md
    │── project_report.pdf
    │── custom_wordlist.txt (generated)

------------------------------------------------------------------------

## License

This project is for **educational and cybersecurity learning purposes
only**. Unauthorized password cracking is illegal.
