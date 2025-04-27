import argparse
from src.database import initialize_database
from src.processor import DataProcessor
from src.loader import DataLoader
from src.view import view_import_summary, view_contracts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["process", "view"])
    parser.add_argument("--file", default="data/sheet.xlsx")
    args = parser.parse_args()

    db_data = initialize_database()

    if args.mode == "view":
        view_contracts()
    else:
        processor = DataProcessor()
        df = processor.preprocess_data(args.file)

        if not df:
            exit("Error: Failed to process data.")

        clients = processor.extract_clients(df)
        contracts = processor.extract_contracts(df, clients)

        loader = DataLoader(db_data)
        loader.clean_previous_data()
        stats = loader.load_data(clients, contracts, processor.dropped_records)

        view_import_summary(stats)
