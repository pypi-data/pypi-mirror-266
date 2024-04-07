from enum import Enum
from pydantic import BaseModel, StringConstraints
from typing import List, Optional, Annotated, Any, Dict
import datetime

class JobStatusEnum(str, Enum):
	PENDING = "pending"
	IN_PROGRESS = "in-progress"
	HUNG = "hung"
	DONE = "done"
	FAILED = "failed"

class JobStump(BaseModel):
	'''
	, priority int not null default 50
	, ttl_seconds int
	, data text
	, result text
	, type varchar(255)
	, status varchar(255)
	, throttle_key varchar(63)
	, throttle_limit integer
	, throttle_period integer
	, source text
	, error text
	, worker_id varchar(63) default null
	'''
	priority:int
	ttl_seconds:int | None = None
	data:str | None = None
	result:str | None = None
	type: Annotated[str, StringConstraints(max_length=255)] | None = None
	status: JobStatusEnum | None = None
	throttle_key: Annotated[str, StringConstraints(max_length=63)] | None = None
	throttle_limit:int | None = None
	throttle_period:int | None = None
	source:str | None = None
	error:str | None = None
	runtime:datetime.timedelta | None = None 
	runtime_ts:int | None = None 


class Job(JobStump):
	'''
	  id serial primary key
	, last_started_at timestamptz
	, last_finished_at timestamptz
	, created_at timestamptz not null default now()
	, updated_at timestamptz not null default now()
	'''
	id: int
	last_started_at:datetime.datetime | None = None 
	last_finished_at:datetime.datetime | None = None 
	updated_at:datetime.datetime
	created_at:datetime.datetime


class TypeCount(BaseModel):
	count: int
	type: str

class StatusCount(BaseModel):
	count: int
	status: JobStatusEnum | None = None

class JobCount(BaseModel):
	count: int
	type: str | None = None
	status: JobStatusEnum | None = None

class ItemQuery(BaseModel):
	id: List[int] | None = None
	error: List[str] | None = None
	limit: List[int] | None = None
	priority: List[int] | None = None
	source: List[str] | None = None
	status: List[JobStatusEnum] | None = None
	throttle_key: List[str] | None = None
	ttl_seconds: List[int] | None = None
	type: List[str] | None = None



class JobTimes(BaseModel):
	avg: int | None
	count:int | None
	max:int | None
	max_ttl:int | None
	med:int | None
	min:int | None
	min_ttl:int | None
	type: str | None


class WorkerStats(BaseModel):
	worker_id: str | None
	job_count:int | None
	ms_per_job:int | None
	jobs_per_hour:int | None
	first_active:int | None
	current_job_started:int | None
	last_job_finished:int | None
	run_time:int | None
	work_time:int | None
	idle_time:int | None
	is_activbe:bool | None


class Action(BaseModel):
	action:str
	data:str | None = None
