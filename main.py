from src.database import initialize_database
from src.processor import DataProcessor
from src.loader import DataLoader, print_import_summary

if __name__ == "__main__":
    processor = DataProcessor()
    df = processor.preprocess_data("data/sheet.xlsx")
    
    if df is not None:
        clients = processor.extract_clients(df)
        contracts = processor.extract_contracts(df, clients)
        
        db_data = initialize_database()
        loader = DataLoader(db_data)
        stats = loader.load_data(clients, contracts, processor.dropped_records)
        
        print_import_summary(stats)
    else:
        print("Error: Failed to process data")