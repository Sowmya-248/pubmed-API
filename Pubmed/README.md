# PubMed Paper Fetcher

## Overview
This CLI tool fetches research papers from PubMed and filters for those with at least one author affiliated with a pharmaceutical or biotech company.

## Features
- Fetches PubMed papers based on a search query.
- Identifies non-academic authors using keywords and email domains.
- Extracts details like title, publication date, and corresponding author email.
- Saves results as a CSV file.

## Installation
This project uses [Poetry](https://python-poetry.org/) for dependency management.

### 1. Install Poetry (if not already installed)
bash
pip install poetry


### 2. Clone the Repository
bash
git clone <your-repo-url>
cd pubmed-paper-fetcher


### 3. Install Dependencies
bash
poetry install


## Usage
### Run the CLI Tool in venv
bash
python3 -m venv venv
source venv/bin/activate
poetry run get-papers-list "cancer therapy"


### Save Results to a File
bash
poetry run get-papers-list "COVID-19 vaccine" -f results.csv


### Enable Debug Mode
bash
poetry run get-papers-list "gene editing" -d


## Project Structure

Empty/  # Root directory
├── pubmed_fetcher.py   # Core module
├── get_papers_list.py  # CLI script
├── pyproject.toml      # Poetry config
├── README.md           # Documentation



## Dependencies
- Python 3.8+
- requests
- pandas
- beautifulsoup4

## License
This project is licensed under the MIT License
