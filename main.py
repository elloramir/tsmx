import argparse
from src.database import initialize_database
from src.processor import DataProcessor
from src.loader import DataLoader
from src.view import view_import_summary, view_contracts
from src.logger import logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["process", "view"])
    parser.add_argument("--file", default="data/sheet.xlsx")
    args = parser.parse_args()

    db_data = initialize_database()
    logger.info("Data base is connect and ready for pairing!")

    if args.mode == "view":
        view_contracts()
    else:
        processor = DataProcessor()
        
        df = processor.preprocess_data(args.file)
        logger.info("Data Frame from sheet file has been pre-processed")

        clients = processor.extract_clients(df)
        contracts = processor.extract_contracts(df, clients)
        logger.info("Data has been transformed")

        loader = DataLoader(db_data)
        loader.clean_previous_data()
        logger.info("On load process... (can take a while)")
        stats = loader.load_data(clients, contracts, processor.dropped_records)

        logger.info("Data loaded on database")
        logger.info("Visual summary:\n")
        view_import_summary(stats)
