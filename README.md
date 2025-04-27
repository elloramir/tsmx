## Overview

This project was developed for a practical interview for the **Data Analyst** position at **TSMX**.

The goal is to import data from an Excel file into a PostgreSQL database, ensuring data integrity and handling inconsistencies.
s

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file with your database credentials**.

3. **(Optional)** Up the container:
   If you are using a local installation of PostgreSQL, just ignore that step

   ```bash
   docker compose up
   ```

4. **Initialize the database**
   ```bash
   python setup.py
   ```

## How It Works

- Create a PostgreSQL database and restore the schema from `data/dump.sql`.
- Process data from `data/dados_importacao.xlsx`.
- Ensure no duplicated clients based on CPF/CNPJ.
- Show a summary of imported and dropped records.


## Usage

- To process and import data:
  ```bash
  python main.py process --file data/sheet.xlsx
  ```

- To view existing contracts:
  ```bash
  python main.py view
  ```

