from fastapi import Depends
from octomy.batch.db import Database
from octomy.batch.types import *
from octomy.utils import human_delta
from pathlib import Path
import datetime
import octomy.utils
import octomy.utils.Watchdog
import glob
import importlib
import importlib.util
import json
import logging
import os
import pprint
import pydantic.version
import random
import re
import string
import sys
import time
import traceback
from .types import *

logger = logging.getLogger(__name__)


CLEANUP_INTERVAL_MS = 0.999


def log_item(item):
	# logger.info(pprint.pformat(item))
	logger.info(item_to_str(item))



def item_to_str(item):
	prefix = "#=- "
	ret = "\n"
	if not item:
		ret = f"""
{prefix}
{prefix}Job:    NONE
{prefix}
"""
		return ret
	ret += f"{prefix}\n"
	type = item.get("type", "unknown-type")
	id = item.get("id", "XXXXXXX")
	ret += f"{prefix}BATCH JOB {type}: {id}\n"
	try:
		now = datetime.now()
		created_ago = human_delta(now - item.get("created_at"), None)
		updated_ago = human_delta(now - item.get("updated_at"), None)
		ret += f"{prefix}Created: {created_ago}, Updated: {updated_ago} ####\n"
	except:
		pass
	try:
		source = item.get("source")
		if source:
			ret += f"{prefix}Source: {source}\n"
		status = item.get("status")
		if status:
			ret += f"{prefix}Status: {status}\n"
	except:
		pass
	data_raw = item.get("data")
	if data_raw:
		ret += f"{prefix}Data:\n\n"
		try:
			data = json.loads(data_raw)
			data_str = json.dumps(data, indent=3, sort_keys=True, default=str)
			ret += data_str + "\n\n"
		except json.JSONDecodeError as e:
			ret += f"{prefix}JSON PARSE ERROR\n"
	result_raw = item.get("result")
	if result_raw:
		ret += f"{prefix}Result:\n\n"
		try:
			result = json.loads(result_raw)
			result_str = json.dumps(result, indent=3, sort_keys=True, default=str)
			ret += result_str + "\n\n"
		except json.JSONDecodeError as e:
			ret += result_raw + "\n\n"
	ret += f"{prefix}\n"
	return ret


def random_token(length=10):
	alphabet = string.ascii_letters + string.digits
	return "".join(random.choice(alphabet) for i in range(length))



class Processor:
	def __init__(self, config, dbc, do_debug=False):
		self.do_debug = do_debug
		self.worker_id = None
		self.config = config
		self.dbc = dbc
		self.db = octomy.batch.db.Database(config, dbc)
		self.do_log = self.config.get("batch-log-logging", True)
		self.last_cleanup_time = datetime.datetime.now()
		self.task_filter = re.compile("^([0-9a-z\-_]+(\/[0-9a-z\-_]+)*)$")
		self.last_status_time = None
		self.callables = {}
		self.callables_params = {}
		self.entry_name = "batch_filter_entrypoint"
		self.param_name = "batch_filter_parameters"

	async def get_id(self):
		if not self.worker_id:
			self.worker_id = random_token(10)
			logger.info(f"Batch Processor {self.worker_id} instanciated")
		return self.worker_id

	def __del__(self):
		if self.worker_id:
			logger.info(f"Batch Processor {self.worker_id} deleted")
			self.worker_id = None


	async def create_tables(self):
		await self.dbc.query_none("overwatch.batch.create_batch_status_enum", prepare=False)
		await self.dbc.query_none("overwatch.batch.create_batch_items", prepare=False)
		await self.dbc.query_none("overwatch.batch.create_gcra_throttle", prepare=False)

	async def verify(self):
		modules = self.list_modules()
		ok = []
		failed = []
		for (name, error) in modules:
			if error:
				failed.append((name, error))
			else:
				ok.append(name)
		if ok:
			logger.info("Available modules:")
			for name in ok:
				logger.info(f" + '{name}'")
		if failed:
			message = ""
			logger.info("Failed modules:")
			for (name, error) in failed:
				logger.error(f" + '{name}': {error}")
				message += f"{name}: {error}\n"
			return False, message
		logger.info(f"Extended logging={self.do_log}")
		return True, ""

	async def load_module_by_filepath(self, module_name, module_filepath):
		module = None
		failure = None
		spec = None
		try:
			spec = importlib.util.spec_from_file_location(module_name, module_filepath)
			spec.submodule_search_locations = list(__import__(__name__).__path__)
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
		except Exception as e:
			failure = f"Import of module '{module_name}'from file '{module_filepath}' had errors ({e}). (Spec was {pprint.pformat(spec)})"
			module = None
		return module, failure

	async def load_module_by_package(self, module_name, package_path=None):
		module = None
		failure = None
		try:
			module = importlib.import_module(module_name, package_path)
		except Exception as e:
			failure = f"Import of module '{module_name}'from package '{package_path}' had errors ({e})"
			module = None
		return module, failure

	async def get_item_types(self):
		module_root_raw = self.config.get("batch-filter-root", "/tmp/inexistant")
		module_root_object = Path(module_root_raw).resolve(strict=False)
		module_root = module_root_object.as_posix()
		if not module_root:
			logger.warning("Module root was not set")
		if not os.path.exists(module_root):
			logger.warning(f"Module root '{module_root}' did not exist")
		logger.info(f"Looking for types in '{module_root}':")
		ret = {}
		for path_object in module_root_object.rglob("*.py"):
			path_object = path_object.resolve(strict=False)
			path = path_object.as_posix()
			if path_object.name.startswith("__"):
				logger.warning(f"Skipping invalid path {path}")
				continue
			if not path.startswith(module_root):
				logger.warning(f"Skipping invalid path {path}")
				continue
			path_difference = path[len(module_root) + 1 :]
			name = Path(path_difference).with_suffix("").as_posix()
			ret[name] = path
			logger.info(f"  Found {name} (from {path})")
		return ret

	async def list_modules(self):
		module_root_raw = self.config.get("batch-filter-root", "/tmp/inexistant")
		module_root_object = Path(module_root_raw).resolve(strict=False)
		module_root = module_root_object.as_posix()

		ret = []
		failure = None
		if not module_root:
			ret.append(("module_root", f"Module root was not set"))
		elif not os.path.exists(module_root):
			ret.append(("module_root", f"Module root '{module_root}' did not exist"))
		else:
			files_objects = module_root_object.rglob("*.py")
			for file_object in files_objects:
				module_filepath = file_object.as_posix()
				if not module_filepath:
					logger.warn(f"Not posix path: {file_object}")
					continue
				if file_object.name.startswith("__"):
					logger.warn(f"Skipping internal: {file_object}")
					continue
				if octomy.utils.file_contains_str(module_filepath, self.entry_name):
					try:
						module, failure = self.load_module_by_filepath(module_filepath, module_filepath)
						if module:
							if hasattr(module, self.entry_name):
								entry_method = getattr(module, self.entry_name)
								if not callable(entry_method):
									entry_method = None
									failure = f"Entrypoint was not callable in filter module {module_filepath}"
							else:
								failure = f"Filter module {module_filepath} did not have method {self.entry_name}"
						else:
							failure = f"Filter module {module_filepath} could not be loaded because: {failure}"
					except Exception as e:
						failure = f"Import of module '{module_filepath}' had errors and was skipped ({e})"
				else:
					failure = f"No entrypoint found in filter module {module_filepath}"
				# logger.warn(f"Appending stat: {module_filepath}:{failure}")
				ret.append((module_filepath, failure))
		return ret

	async def get_callable_for_type_raw(self, t):
		match = self.task_filter.match(t)
		module_name = None
		entry_method = None
		param_dict = None
		failure = None
		# Is this a match?
		if match:
			# Exctract the data we want
			module_name = match.group(1)
			module_filename = module_name + ".py"
			module_filepath = os.path.join(self.config.get("batch-filter-root", "/dev/null"), module_filename)
			module = None
			if os.path.exists(module_filepath):
				if octomy.utils.file_contains_str(module_filepath, self.entry_name):
					try:
						module, failure = self.load_module_by_filepath(module_name, module_filepath)
						if module:
							if hasattr(module, self.entry_name):
								entry_method = getattr(module, self.entry_name)
								if not callable(entry_method):
									entry_method = None
									failure = f"Entrypoint was not callable in filter module {module_filepath}"
								if hasattr(module, self.param_name):
									param_dict = getattr(module, self.param_name)
							else:
								failure = f"Filter module {module_filepath} did not have method {self.entry_name}"
						else:
							failure = f"Filter module {module_filepath} could not be loaded because: {failure}"
					except Exception as e:
						failure = f"Import of module '{module_name}' had errors and was skipped ({e})"
				else:
					failure = f"No entrypoint found in filter module {module_filepath}"
			else:
				failure = f"Could not find filter module {module_filepath}"
		else:
			failure = f"No match for type {t}"
		return entry_method, param_dict, failure

	async def get_callable_for_type(self, t):
		if t in self.callables:
			return self.callables.get(t), self.callables_params.get(t), None
		else:
			cb, params, failure = self.get_callable_for_type_raw(t)
			if cb:
				self.callables[t] = cb
			if params:
				self.callables_params[t] = params
			return cb, params, failure

	async def _watchdog_hang_detected(self):
		logger.error("Watchdog triggered exception, restarting batch")
		sys.exit(99)

	async def _execute_safely(self, entrypoint, params, item):
		# logger.info("SAFE EXECUTION STARTED!")
		failure = None
		result = None
		watchdog = None
		try:
			# We cap runtime at TTL from which ever is set first; item ttl, param ttl or environment fallback value
			timeout = self.config.get("batch-default-ttl", 0)
			timeout = params.get("ttl_seconds", timeout) if params else timeout
			timeout = item.get("ttl_seconds", timeout) if item else timeout
			if timeout and timeout > 0:
				logger.info(f"Using watchdog with ttl={timeout}sec")
				watchdog = octomy.utils.Watchdog.Watchdog(timeout, self._watchdog_hang_detected)
			else:
				logger.info(f"No watchdog enabled")
			# logger.info("££££ Entry")
			unpackable = entrypoint(item, self.config)
			try:
				result, failure = unpackable
			except TypeError as te:
				failure = f"Filter did not return exactly one value and one error"
				logger.warning(failure)
				return None, failure
			# logger.info("££££ Exit")
		except octomy.utils.Watchdog.Watchdog:
			logger.warning("Watchdog triggered exception")
			failure = f"Execution timed out after {timeout} seconds"
		except Exception as e:
			logger.warning("")
			logger.warning("")
			logger.warning(f"###############################################")
			logger.warning(f"#    Batch item: {item} on worker {self.worker_id}")
			logger.warning(f"# Failed with: {e} ({type(e).__name__}, {e.args})")
			failure = f"{e}  ({type(e).__name__}, {e.args})"
			logger.warning(f"#          At:")
			traceback.print_exc()
			logger.warning(f"#######################################")
			logger.warning("")
			logger.warning("")
		if None is not watchdog:
			watchdog.stop()
		# logger.info("SAFE EXECUTION FINISHED!")

		watchdog = None
		return result, failure

	async def execute_one_batch_item(self):
		"""
		Take ownership of one batch item and make sure it is properly executed and updated with status underway
		"""
		worker_id = self.get_id()
		updated_status = {"from_status": JobStatusEnum.PENDING, "to_status": JobStatusEnum.IN_PROGRESS, "in_progress_status": JobStatusEnum.IN_PROGRESS, "worker_id": worker_id}
		item, err = await self.dbc.key_query(query_key = "overwatch.batch.book_batch_item", params=updated_status, mode = "one", item_type = dict)
		if item:
			if self.do_log:
				logger.info("Processing item:")
				log_item(item)
			id = item.get("id", None)
			t = item.get("type", None)
			updated_at = item.get("updated_at", None)
			if id and t and updated_at:
				entrypoint, params, failure = self.get_callable_for_type(t)
				if entrypoint and failure:
					entrypoint = None
					failure = f"{failure} AND ENTRYPOINT WAS SET!"
				result = None
				if entrypoint:
					result, failure = self._execute_safely(entrypoint, params, item)
				if failure:
					logger.warning("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ BATCH FILTER FAILED WITH ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
					logger.warning(failure)
					logger.warning("")
				(id2, updated_at2), err2 = await self.db.bump_batch_item(id=id, status=JobStatusEnum.FAILED if failure else JobStatusEnum.DONE, error=failure, updated_at=updated_at, result=result) or (None, None)
				if self.do_log:
					logger.info(f"id2={id2}, updated_at2={updated_at2}, id={id}, updated_at={updated_at}, {err2}")
				return True
			else:
				logger.warning(f"Missing data for item id={id}, type={t}, updated_at={updated_at}")
				logger.error(f"err={err}")
		# else:
		# logger.info(f"No pending items found")
		return False

	async def execute_one_throttled_batch_item(self):
		"""
		Take ownership of one batch item and make sure it is properly executed and updated with status underway
		NOTE: Throttled version
		"""
		worker_id = self.get_id()
		updated_status = {"from_status": JobStatusEnum.PENDING, "to_status": JobStatusEnum.IN_PROGRESS, "in_progress_status": JobStatusEnum.IN_PROGRESS, "worker_id": worker_id}
		item, err = await self.dbc.key_query(query_key = "overwatch.batch.book_throttled_batch_item", params=updated_status, mode = "one", item_type = dict)
		if item:
			if self.do_log:
				logger.info("Processing throttled item:")
				log_item(item)
			id = item.get("id", None)
			t = item.get("type", None)
			updated_at = item.get("updated_at", None)
			if id and t and updated_at:
				if item.get("wait_millis", 0) > 0:
					logger.warning("Item not booked")
					logger.warning(pprint.pformat(item))
					failure = "Not booked"
				else:
					entrypoint, params, failure = self.get_callable_for_type(t)
					if entrypoint and failure:
						entrypoint = None
						failure = f"{failure} AND ENTRYPOINT WAS SET!"
					result = None
					if entrypoint:
						result, failure = self._execute_safely(entrypoint, params, item)
					if failure:
						logger.warning("¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤ BATCH FILTER FAILED WITH ¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
						logger.warning(failure)
						logger.warning("")
				id2, updated_at2 = await self.db.bump_batch_item(id=id, status=JobStatusEnum.FAILED if failure else JobStatusEnum.DONE, error=failure, updated_at=updated_at, result=result) or (None, None)
				if self.do_log:
					logger.info(f"id2={id2}, updated_at2={updated_at2}, id={id}, updated_at={updated_at}")
				return True
			else:
				logger.warning(f"Missing data for item id={id}, type={t}, updated_at={updated_at}")
				logger.error(f"err={err}")
		# else:
		# logger.info(f"No pending items found")
		return False

	# Make sure data is a string ready for insertion into db
	async def _prepare_data(self, data):
		if data == None:
			return None
		data_type = type(data)
		if data_type is dict:
			data = json.dumps(data, indent=3, sort_keys=True, default=str)
		elif data_type is not str:
			data = str(data)
		return data

	async def insert_batch_item(self, type="test", data=None, ttl_seconds=None, result=None, priority=50, source=None, throttle_key=None, throttle_limit=1, throttle_period=1):
		"""
		Insert a new batch item into the database, ready for execution
		"""
		data = self._prepare_data(data)
		# fmt: off
		return await self.db.insert_batch_item(
			{
				"priority": priority,
				"ttl_seconds": ttl_seconds, 
				"data": data,
				"result": result,
				"type": type,
				"status": JobStatusEnum.PENDING,
				"throttle_key": throttle_key,
				"throttle_limit": throttle_limit,
				"throttle_period": throttle_period,
				"source": source
			}
		)
		# fmt: on

	async def _update_hang_status(self):
		updated_status= {"from_status": JobStatusEnum.IN_PROGRESS, "to_status": JobStatusEnum.HUNG, "in_progress_status": JobStatusEnum.IN_PROGRESS}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.update_hang_status", params=updated_status, mode = "one", item_type = dict)
		if db_err:
			logger.warning(f"Could not update hang status: {db_err}")
		return db_items

		return await self.db.update_batch_hang_status()

	async def retry_hung_jobs(self):
		updated_status = {"from_status": JobStatusEnum.IN_PROGRESS, "to_status": JobStatusEnum.PENDING, "in_progress_status": JobStatusEnum.IN_PROGRESS}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.bump_batch_items", params=updated_status, mode = "one", item_type = dict)
		if db_err:
			logger.warning(f"Could retry hung jobs: {db_err}")
		return db_items
		return await self.db.bump_batch_items(JobStatusEnum.HUNG, JobStatusEnum.PENDING)


	async def delete_jobs_with_status(self, status):
		query = {"status": status}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_batch_items_by_status", params = query, mode = "none", do_debug = self.do_debug)
		if db_err:
			logger.warning(f"Could not delete '{query.get('status')}' jobs: {db_err}")
		return db_items


	async def delete_all_jobs(self):
		query = {}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_all", params = query, mode = "none", do_debug = self.do_debug)
		if db_err:
			logger.warning(f"Could not delete all {db_err}")
		return db_items


	async def bump_job_by_id(self, id, status):
		return await self.db.bump_batch_item_status(id, status)


	async def retry_job_by_id(self, id):
		return await self.db.bump_batch_item_status(id, JobStatusEnum.PENDING)


	async def delete_job_by_id(self, id):
		query = {"id": id}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_by_id", params = query, mode = "none", do_debug = self.do_debug)
		if db_err:
			logger.warning(f"Could not delete JOB BY ID '{query.get('ID')}': {db_err}")
		return db_items


	async def get_job_counts(self):
		#raw, err = await self.db.get_job_counts()
		raw, err = await self.dbc.key_query(query_key="overwatch.batch.get_job_counts", params={}, mode = "many", item_type = List[JobCount])
		if raw:
			out = {}
			totals = {}
			for row in raw:
				t = row.type
				s = row.status
				c = row.count
				totals[s] = totals.get(s, 0) + c
				out[t] = out.get(t, {})
				out[t][s] = c
			out["total"] = totals
			return out, None
		else:
			logger.error(f"err={err}")
			return None, err

	async def get_job_times(self):
		raw = await self.db.get_job_times()
		return raw

	async def get_worker_stats(self):
		raw, err = await self.db.get_worker_stats()
		return raw, err

	async def get_status(self):
		status, status_err = await self.dbc.key_query(query_key="overwatch.batch.get_status_counts", params={}, mode = "many", item_type = List[StatusCount])
		counts, counts_err = await self.get_job_counts()
		times, times_err = await self.dbc.key_query(query_key="overwatch.batch.get_job_times", params={"statuses": ["done"]}, mode = "many", item_type = List[JobTimes])
		workers, workers_err = await self.get_worker_stats()
		# fmt: off
		status = {
			  "status": status
			, "counts": counts
			, "times": times
			, "workers": workers
			, "errors": {
				  "status": status_err
				, "counts": counts_err
				, "times": times_err
				, "workers": workers_err
			}
		}
		# fmt: on
		if any([status_err, counts_err, times_err, workers_err]):
			return None, f"status_err={status_err}, counts_err={counts_err}, times_err={times_err}, workers_err={workers_err}"
		return status, None

	async def process(self):
		# Perform some cleanup on occation
		now = datetime.datetime.now()
		if now - self.last_cleanup_time > datetime.timedelta(seconds=CLEANUP_INTERVAL_MS):
			self.last_cleanup_time = now
			self._update_hang_status()
		# Try to process one item
		if not self.execute_one_throttled_batch_item():
			# Lets not get stuck in a loop!
			time.sleep(1)
