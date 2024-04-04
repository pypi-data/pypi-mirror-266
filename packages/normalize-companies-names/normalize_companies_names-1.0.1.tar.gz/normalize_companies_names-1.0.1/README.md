# Library to add a normalized companies names column in Excel file


### About the problem:
Once we find misspelling and not normalized companies names in an Excel file that contains the at least the column named **organization** we will struggle against the possibility of save and process data without integrity. This library aims to process the Excel file and add a new column named **canonical_name**.

### Technologies used in this library
- [Click API](https://click.palletsprojects.com/en/8.1.x/)
- [Pandas](https://pandas.pydata.org/docs/)
- [The Fuzz](https://pypi.org/project/thefuzz/)
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)
- [Poetry](https://python-poetry.org/docs/)

### How to use the library
This library has two ways of use: The first one is installing locally through and the second is installing from PyPI repository. Let's see how to use it by the both ways below.

>**Observations**: This document assumes that you're familiar to Poetry, python virtual environment and has it already installed in your machine.

#### First Way - Installing locally using Poetry:
1 - Run the command to access the bash using the virtualenv created by poetry
```bash
poetry shell
```

2 - Run the command below to Poetry installs the library locally
```bash
poetry install
```

#### Second Way - Installing using pip:
- Run the command below to see install via pip
```bash
pip install normalize-companies-names
```

### Executing the library
1 - Run the command below to see the information about the library
```bash
normalize --help
```
>**Result:**
>Usage: normalize [OPTIONS]
>
>Options:
>
>  -c, --canonicals TEXT       Canonicals companies names separated by comma.
                              (e.g 'MICROSOFT TECHNOLOGY LICENSING,MICRON
                              TECHNOLOGY,DELTA TECHNOLOGY,ELTA TECHNOLOGY')
                              [required]
>
>  -i, --input_filepath TEXT   Path to the Excel file that need to be
                              processed.  [required]
>
>  -o, --output_filepath TEXT  Path to save the processed Excel file.
                              [required]
>
>  --help                      Show this message and exit.



2 - Run the command below to process a file and receive the processed one
```bash
normalize -c MICROSOFT,MICRON,ELTA,DELTA -i ./data/patent-records.xlsx -o ./data/
```