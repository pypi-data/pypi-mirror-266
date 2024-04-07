from pydantic import BaseModel, StringConstraints
from typing import List, Optional, Annotated, Any, Dict
import pydantic.version
import pytz
from .types import JobCount, StatusCount, TypeCount, Job, JobTimes, WorkerStats
import logging
import pprint


logger = logging.getLogger(__name__)

class Database:



	def __init__(self, config, dbc):
		self.config = config
		self.dbc = dbc


	# Look at faster batch imports with
	# from psycopg2.extras import execute_values
	# execute_values(cur,
	# "INSERT INTO test (id, v1, v2) VALUES %s",
	# [(1, 2, 3), (4, 5, 6), (7, 8, 9)])
	# FROM https://stackoverflow.com/questions/8134602/psycopg2-insert-multiple-rows-with-one-query


	# Insert a new batch item into log
	#async def insert_batch_item(self, batch_item):
	#	return await self.dbc.key_query(query_key = "overwatch.batch.insert_batch_item", params=batch_item, mode = "one", item_type = dict)


	# Update status of all "in progress" jobs that already spent more than ttl time to "hung"
	#async def update_batch_hang_status(self):
	#	updated_status= {"from_status": (self.IN_PROGRESS,), "to_status": (self.HUNG,), "in_progress_status": (self.IN_PROGRESS,)}
	#	return await self.dbc.key_query(query_key = "overwatch.batch.update_hang_status", params=updated_status, mode = "one", item_type = dict)

	# Update status of all jobs with from_status to to_status
	#async def bump_batch_items(self, from_status=IN_PROGRESS, to_status=PENDING):
	#	updated_status = {"from_status": (from_status,), "to_status": (to_status,), "in_progress_status": (self.IN_PROGRESS,)}
	#	return await self.dbc.key_query(query_key = "overwatch.batch.bump_batch_items", params=updated_status, mode = "one", item_type = dict)

	# Update status of a batch item in the batch log, making sure to fail if the id and updated_at don't match, providing a guarantee of atomic operation
	# Returns updated_at, so caller can check if it was updated or not (compare it to argument)
	async def bump_batch_item(self, id, status, error, updated_at, result=None):
		updated_status = {"id": (id,), "status": (status,), "error": (error,), "result": (result,), "updated_at": (updated_at,), "in_progress_status": (self.IN_PROGRESS,)}
		return await self.dbc.key_query(query_key = "overwatch.batch.bump_batch_item", params=updated_status, mode = "one", item_type = dict)

	# Simplified version of bump_batch_item where status is updated, no questions asked
	async def bump_batch_item_status(self, id, status):
		updated_status = {"id": (id,), "status": (status,), "in_progress_status": (self.IN_PROGRESS,)}
		return await self.dbc.key_query(query_key = "overwatch.batch.bump_batch_item_status", params=updated_status, mode = "one", item_type = dict)

	# Update a batch item in the batch log, making sure to fail if the id and updated_at don't match, providing a guarantee of atomic operation
	#async def book_batch_item(self, from_status=PENDING, to_status=IN_PROGRESS, worker_id=None):
	#	updated_status = {"from_status": (from_status,), "to_status": (to_status,), "in_progress_status": (self.IN_PROGRESS,), "worker_id": (worker_id,)}
	#	return await self.dbc.key_query(query_key = "overwatch.batch.book_batch_item", params=updated_status, mode = "one", item_type = dict)

	# Update a batch item in the batch log, making sure to fail if the id and updated_at don't match, providing a guarantee of atomic operation
	# NOTE: This is the throttled version
	#async def book_throttled_batch_item(self, from_status=PENDING, to_status=IN_PROGRESS, worker_id=None):
	#	updated_status = {"from_status": (from_status,), "to_status": (to_status,), "in_progress_status": (self.IN_PROGRESS,), "worker_id": (worker_id,)}
	#	return await self.dbc.key_query(query_key = "overwatch.batch.book_throttled_batch_item", params=updated_status, mode = "one", item_type = dict)

	# Delete single item by id
	#async def delete_by_id(self, id):
	#	query = {"id": (id,)}
	#	db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_by_id", params = query, mode = "none", do_debug=True)
	#	return {}

	# Delete batch items with given status and update_at longer than given time
	#async def delete_batch_items_with_status(self, status):
	#	query = {"status": (status,)}
	#	db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_batch_items_by_status", params = query, mode = "none", do_debug=True)
	#	return {}

	# Clear out the batch items table
	#async def delete_all(self):
	#	query = {}
	#	db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.delete_all", params = query, mode = "none", do_debug=True)
	#	return {}

	# Get distinct batch types with counts
	async def get_type_counts(self) -> List[TypeCount]:
		query = {}
		return await self.dbc.key_query(query_key="overwatch.batch.get_type_counts", params=query, mode = "many", item_type = List[TypeCount])

	# Get distinct batch status with counts
	#async def get_status_counts(self) -> List[StatusCount]:
	#	query = {}
	#	return await self.dbc.key_query(query_key="overwatch.batch.get_status_counts", params=query, mode = "many", item_type = List[StatusCount])

	# Get distinct batch status+type with counts
	#async def get_job_counts(self) -> List[JobCount]:
	#	query = {}
	#	return await self.dbc.key_query(query_key="overwatch.batch.get_job_counts", params=query, mode = "many", item_type = List[JobCount])

	# Get statistics for each worker (inferred)
	async def get_worker_stats(self, limit=10) -> List[WorkerStats]:
		query = {"limit": limit}
		return await self.dbc.key_query(query_key="overwatch.batch.get_worker_stats", params=query, mode = "many", item_type = List[WorkerStats])

	# Get progression stats with totals for the given statuses
	#async def get_job_times(self, statuses=["done"]) -> List[JobTimes]:
	#	query = {"statuses": statuses}
	#	return await self.dbc.key_query(query_key="overwatch.batch.get_job_times", params=query, mode = "many", item_type = List[JobTimes])

	# Get batch items from batch log sorted by last active
	#async def get_jobs(self, id=None, priority=None, ttl_seconds=None, type="tits", status=None, throttle_key=None, source=None, error=None, limit=1):
	#	query = {"id": id, "priority": priority, "ttl_seconds": ttl_seconds, "type": type, "status": status, "throttle_key": throttle_key, "error": error, "source": source, "limit": limit}
	#	logger.info(f"DB PARAMS: {pprint.pformat(query)}")
	#	return await self.dbc.key_query(query_key="overwatch.batch.get_jobs", params=query, mode = "many", item_type = List[Job])


	#    , min( extract('epoch' from updated_at - created_at)) as low
	# , max( extract('epoch' from updated_at - created_at)) as high
	# , percentile_cont(0.5) within group (order by extract('epoch' from "test_median".updated_at - "test_median".created_at)::float ) as median

	# Return database's idea of current time
	async def get_now(self):
		query = {}
		db_items, db_err = await self.dbc.key_query(query_key = "overwatch.batch.get_now", params=query, mode = "one", item_type = dict)
		db_items = db_items.replace(tzinfo=pytz.UTC)
		return db_items
