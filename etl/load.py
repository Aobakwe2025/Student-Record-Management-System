import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from etl.logger import logger

load_dotenv()

def get_connection():
	return psycopg2.connect(
		host=os.getenv('DB_HOST'),
		port=os.getenv('DB_PORT', 5432),
		dbname=os.getenv('DB_NAME'),
		user=os.getenv('DB_USER'),
		password=os.getenv('DB_PASSWORD')
	)

def load_table(df, table, columns, conflict_col):
	"""
	Batch insert a DataFrame into a PostgreSQL table.
	Uses ON CONFLICT DO NOTHING to safely skip duplicates.
	Rolls back the entire batch if any error occurs.
	"""
	logger.info(f'Loading {len(df):,} rows into [{table}]...')

	conn = get_connection()
	cursor = conn.cursor()

	rows = [tuple(row) for row in df[columns].itertuples(index=False)]
	col_str = ', '.join(columns)

	try:
		execute_values(
			cursor,
			f"""
			INSERT INTO {table} ({col_str})
			VALUES %s
			ON CONFLICT ({conflict_col}) DO NOTHING
			""",
			rows,
			page_size=100       # insert in batches of 100 rows
		)
		conn.commit()
		logger.info(f'  ✓ {cursor.rowcount} rows inserted into [{table}]')

	except Exception as e:
		conn.rollback()
		logger.error(f'  ✗ ROLLBACK on [{table}]: {e}')
		raise

	finally:
		cursor.close()
		conn.close()