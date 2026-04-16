import pandas as pd
from etl.logger import logger

def extract_csv(filepath):
	logger.info(f'Extracting CSV: {filepath}')
	df = pd.read_csv(filepath)
	logger.info(f'  → {len(df):,} rows loaded from {filepath}')
	return df

def extract_excel(filepath, sheet=0):
	logger.info(f'Extracting Excel: {filepath}')
	df = pd.read_excel(filepath, sheet_name=sheet)
	logger.info(f'  → {len(df):,} rows loaded from {filepath}')
	return df

def extract_json(filepath):
	logger.info(f'Extracting JSON: {filepath}')
	df = pd.read_json(filepath)
	logger.info(f'  → {len(df):,} rows loaded from {filepath}')
	return df