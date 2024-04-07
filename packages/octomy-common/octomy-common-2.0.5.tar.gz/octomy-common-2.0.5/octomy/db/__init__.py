#!/bin/env python3
from functools import lru_cache
from pydantic import TypeAdapter, ValidationError
from typing import Type, get_args, get_origin
import aiofiles
import asyncio
import logging
import os
import pathlib
import pprint
import psycopg
import psycopg_pool
import re
import urllib.parse

logger = logging.getLogger(__name__)


class c:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	CYAN = '\033[96m'
	GREEN = '\033[92m'
	RED = '\u001b[31m'
	ORANGE = '\u001b[38;5;202m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def stripes(cols=79, rows=3, on=3, off=3, on_char="#", off_char=" ", offset=0, sheer=1):
	out=""
	alphabet = on_char * on + off_char * off
	alphabet_len=len(alphabet)
	for row in range(0, rows):
		index = offset
		out += c.ORANGE
		for col in range(0, cols):
			alphabet_index = index % alphabet_len
			out += alphabet[alphabet_index]
			index += 1
		offset+=sheer
		out += c.ENDC +"\n"
	return out



def schema_to_compact(schema: dict) -> str:
	# Extract the title or name of the model
	model_name = schema.get('title', 'UnknownModel')
	
	# Initialize an empty list to hold field descriptions
	field_descriptions = []
	
	# Iterate over the properties in the schema to build field descriptions
	for field_name, details in schema.get('properties', {}).items():
		field_type = details.get('type', 'UnknownType')
		
		# For more complex types (e.g., arrays, nested models), you might need additional handling here
		if field_type == 'array':
			items = details.get('items')
			if isinstance(items, dict):
				item_type = items.get('type', 'UnknownType')
				field_type = f"List[{item_type}]"
		
		# Append the field description to the list
		field_descriptions.append(f"{field_name}:{field_type}")
	
	# Join all field descriptions into a single string
	fields_str = ', '.join(field_descriptions)
	
	# Return the compact representation of the model
	return f"{model_name}{{ {fields_str} }}"


def describe_type(input_type: Type) -> str:
	# Handle Pydantic models by checking for the .schema() method
	if hasattr(input_type, 'schema') and callable(getattr(input_type, 'schema')):
		schema = schema_to_compact(input_type.schema())
		return f"Pydantic {schema}"
	
	# Check for generic types (e.g., List[SomeType])
	origin_type = get_origin(input_type)
	if origin_type is not None:
		type_args = get_args(input_type)
		type_args_descriptions = [describe_type(t) for t in type_args]
		descs='\n, '.join(type_args_descriptions)
		return f"Generic type: {origin_type.__name__} of [{descs}]"
	# Fallback for standard or simple types
	return f"Type: {input_type}"


class Database:
	def __init__(self, db_uri, sql_dir):
		self.db_uri = db_uri
		self.query_dirs = set()
		self.queries = dict()
		self.prepared = dict()
		self.pool = None
		if sql_dir:
			self.query_dirs.add(sql_dir)

	async def preload_queries(self, path):
		"""Recursively load and register queries from .sql files in given path."""
		self.query_dirs.add(pathlib.Path(path))
		for dir in self.query_dirs:
			for sql_file in dir.rglob('*.sql'):
				# some/path/file.sql --> some.path.file
				query_key = sql_file.relative_to(dir).with_suffix('').as_posix().replace('/', '.')
				with open(sql_file, 'r', encoding='utf-8') as file:
					self.queries[query_key] = file.read()

	def reset_queries(self):
		"""Reset the internal cache of queries, forcing queries to be reloaded upon next invocation"""
		self.queries=dict()
		self.prepared=dict()

	async def load_query(self, query_key):
		"""Load and return a single query by first looking it up in the internal cache and falling back on looking for it on disk"""
		# Cache hit
		if query_key in self.queries:
			return self.queries[query_key]
		# Cache miss, load from disk
		try:
			# Make sure we know where to look
			if len(self.query_dirs) <= 0:
				raise Exception(f"No query dir(s) specified")
			# Convert the query_key to a file path
			for dir in self.query_dirs:
				file_path = dir / pathlib.Path(query_key.replace('.', '/') + '.sql')
				logger.info(f"file_path {file_path}")
					
				# Read the SQL query from file
				async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
					sql_query = await file.read()
				# with open(file_path, 'r', encoding='utf-8') as file:
				#	sql_query = file.read()
				self.queries[query_key] = sql_query
				return sql_query
		except FileNotFoundError:
			logger.info(f"SQL file {os.path.abspath(file_path)}")
			logger.error(f"SQL file not found for key {query_key} at path {file_path}")
		except Exception as e:
			logger.error(f"{type(e).__name__}: Error loading SQL file for key {query_key}: {e}")
		return None

	def _get_pool(self):
		self.pool = self.pool or psycopg_pool.AsyncConnectionPool(self.db_uri) # , min_size=min_conn, max_size=max_conn
		return self.pool


	def _adapt(self, raw, item_type, do_debug=False):
		if not item_type:
			return raw
		if do_debug:
			logger.info(f"Adapting {pprint.pformat(raw)} to {pprint.pformat(item_type)}")
		try:
			return TypeAdapter(item_type).validate_python(raw)
		except Exception as e:
			logger.warning(f"Adaption error details")
			logger.warning(f"                       raw: {pprint.pformat(raw)}")
			logger.warning(f"                 type(raw): {type(raw)}")
			logger.warning(f"                 item_type: {item_type}")
			logger.warning(f"  describe_type(item_type): {describe_type(item_type)}")
			raise


	async def direct_query(self, query, query_name=None, params=dict(), mode="none", item_type=None, prepare=True, do_debug=True):
		cursor = None
		try:
			if not query:
				raise Exception("No query")
			# Make sure we actually have a pool
			pool = self._get_pool()
			if not pool:
				raise Exception("No pool")
			# TODO: Look into implementing pipeline mode
			# See: https://www.psycopg.org/psycopg3/docs/advanced/pipeline.html
			# Acquire a connection from the pool
			async with pool.connection() as connection:
				async with connection.transaction() as transaction:
					async with connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
						# See https://www.psycopg.org/psycopg3/docs/advanced/prepare.html
						if do_debug:
							logger.info(f"Preparing query '{query_name}'")
							logger.info("\n\n" + query+"\n\n")
							logger.info(f"With data")
							logger.info("\n\n" + pprint.pformat(params)+"\n\n")
						await cursor.execute(query = query, params = params, prepare = prepare)
						if mode == "many":
							res = self._adapt(await cursor.fetchall(), item_type, do_debug)
							if do_debug:
								logger.info(f"Returning many data: '{pprint.pformat(res)}'")
							return res, None
						elif mode == "one":
							res = self._adapt(await cursor.fetchone(), item_type, do_debug)
							if do_debug:
								logger.info(f"Returning one data: '{pprint.pformat(res)}'")
							return res, None
						elif mode == "exists":
							res = await cursor.fetchone()
							if item_type:
								logger.warning(f"item_type speficied '{item_type}' for query with mode exists")
							if do_debug:
								logger.info(f"Returning exist data: '{pprint.pformat(res)}'")
							return res is not None, None
						elif mode == "none":
							if item_type:
								logger.warning(f"item_type speficied '{item_type}' for query with mode none")
							if do_debug:
								logger.info(f"Returning for none")
							return None, None
						else:
							raise Exception(f"Unknown mode {mode}. Should be one of [many, one, exists, none]")
		except Exception as e:
			logger.error("\n\n"+stripes())
			logger.error("")
			logger.error("")
			logger.error(f"###############################################")
			logger.error(f"+       Error: ({type(e).__name__})")
			logger.error(f"#    Querying: '{query_name}'\n\n{query}\n")
			if cursor and query and "cursor" in query:
				logger.error(f"#    Injected: '{cursor.query.decode()}'")
			logger.error(f"#         On")
			logger.error(f"#         + db_uri =   '{self.db_uri}'")
			logger.error(f"#         For")
			logger.error(f"#         + mode =   '{mode}'")
			logger.error(f"#         + params = '{pprint.pformat(params)}'")
			logger.error(f"# Failed with:")
			if isinstance(e,psycopg.Error):
				logger.error(f"# + e.type:     '{type(e).__name__}'")
				logger.error(f"# + e.sqlstate: '{e.sqlstate}'")
				if getattr(e, "pgconn", None):
					logger.error(f"# + e.pgconn:   '{e.pgconn}'")
				if getattr(e, "pgresult", None):
					logger.error(f"# + e.pgresult: '{e.pgresult}'")
				if e.diag:
					logger.error(f"# + e.diag: '{e.diag}'")
					error_attrs = [
						"column_name", "constraint_name", "context", "datatype_name",
						"internal_position", "internal_query", "message_detail", "message_hint",
						"message_primary", "schema_name", "severity", "source_file",
						"source_function", "source_line", "sqlstate", "statement_position",
						"table_name", "severity_nonlocalized"
					]
					for attr in error_attrs:
						value = getattr(e.diag, attr, None)  # Use getattr to safely handle missing attributes
						if value is not None:  # Only log if the attribute is present and not None
							logger.error(f"#   + {attr}: {value}")
			elif isinstance(e, ValidationError):
				logger.error(f"Validation error: with item_type '{item_type}'")
			else:
				# Unexpected errors
				logger.error(f"Unexpected error: {type(e).__name__}")
			logger.error(f"#  Stacktrace: \n\n{e}\n")
			logger.error("\n\n"+stripes())
			return None, str(e)


	async def key_query(self, query_key, params=dict(), mode="none", item_type=None, prepare=True, do_debug=False):
		query = await self.load_query(query_key)
		if query:
			if do_debug:
				logger.info(f"key_query params='{pprint.pformat(params)}' prepare={prepare}")
			return await self.direct_query(query = query, query_name=query_key, params = params, mode = mode, item_type=item_type, prepare=prepare, do_debug=do_debug)
		return None, "No query"

	async def query_many(self, query_key, params=dict(), item_type=None, prepare=True, do_debug=False):
		if do_debug:
			logger.info(f"query_many params='{pprint.pformat(params)}' prepare={prepare}")
		return await self.key_query(query_key = query_key, params = params, mode = "many", item_type=item_type, prepare=prepare, do_debug=do_debug)

	async def query_one(self, query_key, params=dict(), item_type=None, prepare=True, do_debug=False):
		if do_debug:
			logger.info(f"query_one params='{pprint.pformat(params)}' prepare={prepare}", prepare=True, do_debug=False)
		return await self.key_query(query_key = query_key, params = params, mode = "one", item_type=item_type, prepare=prepare, do_debug=do_debug)

	async def query_none(self, query_key, params=dict(), prepare=True, do_debug=False):
		if do_debug:
			logger.info(f"query_none params='{pprint.pformat(params)}' prepare={prepare}", prepare=True, do_debug=False)
		return await self.key_query(query_key = query_key, params = params, mode = "none", prepare=prepare, do_debug=do_debug)

	async def query_exists(self, query_key, params=dict(), prepare=True, do_debug=False):
		if do_debug:
			logger.info(f"query_exists params='{pprint.pformat(params)}' prepare={prepare}")
		return await self.key_query(query_key = query_key, params = params, mode = "exists", prepare=prepare, do_debug=do_debug)


	async def execute_old(self, query_key, **params):
		"""Execute a registered query by its key."""
		if query_key not in self.queries:
			raise ValueError(f"Query '{query_key}' not found.")
		
		async with self.pool.connection() as connection:
			async with connection.cursor() as cur:
				await cur.execute(self.queries[query_key], params)
				# Assuming a fetch is needed, adjust as necessary
				return await cur.fetchall()


def _q(s):
	if not s:
		return ""
	return urllib.parse.quote(s)

def db_uri_from_conf(config:dict) ->str :
	return f"postgresql://{_q(config.get('db-username'))}:{_q(config.get('db-password'))}@{config.get('db-hostname')}:{config.get('db-port')}/{_q(config.get('db-database'))}"

#@lru_cache
def get_database(config:dict) -> Database:
	uri = db_uri_from_conf(config)
	logger.info(f"Trying to connect to database with '{uri}'")
	db = Database(db_uri=uri, sql_dir=config.get("db-sql-dir"))
	return db

