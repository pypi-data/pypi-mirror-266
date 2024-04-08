from enum import Enum
import pydantic
from typing import List, Optional, Annotated, Any, Dict
import datetime
import json

class JobStatusEnum(str, Enum):
	PENDING = "pending"
	IN_PROGRESS = "in-progress"
	HUNG = "hung"
	DONE = "done"
	FAILED = "failed"

class JobStump(pydantic.BaseModel):
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
	type: Annotated[str, pydantic.StringConstraints(max_length=255)] | None = None
	status: JobStatusEnum | None = None
	throttle_key: Annotated[str, pydantic.StringConstraints(max_length=63)] | None = None
	throttle_limit:int | None = None
	throttle_period:int | None = None
	source:str | None = None
	error:str | None = None
	runtime:datetime.timedelta | None = None 
	runtime_ts:float | None = None 


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


class JobBooking(pydantic.BaseModel):
	id: int
	priority:int
	data:str | None = None
	result:str | None = None
	type: Annotated[str, pydantic.StringConstraints(max_length=255)] | None = None
	status: JobStatusEnum | None = None
	source:str | None = None
	ttl_seconds:int | None = None
	created_at:datetime.datetime
	updated_at:datetime.datetime
	def __str__(self):
		prefix = "#=- "
		ret = ""
		ret += f"{prefix}\n"
		type = self.type or "unknown-type"
		id = self.id or "XXXXXXX"
		ret += f"{prefix}BATCH JOB {type}: {id}\n"
		try:
			now = datetime.now()
			created_ago = human_delta(now - self.created_at, None)
			updated_ago = human_delta(now - self.updated_at, None)
			ret += f"{prefix}Created: {created_ago}, Updated: {updated_ago} ####\n"
		except:
			pass
		try:
			source = self.source
			if source:
				ret += f"{prefix}Source: {source}\n"
			status = self.status
			if status:
				ret += f"{prefix}Status: {status}\n"
		except:
			pass
		data_raw = self.data
		if data_raw:
			ret += f"{prefix}Data:\n\n"
			try:
				data = json.loads(data_raw)
				data_str = json.dumps(data, indent=3, sort_keys=True, default=str)
				ret += data_str + "\n\n"
			except json.JSONDecodeError as e:
				ret += f"{prefix}JSON PARSE ERROR\n"
		result_raw = self.result
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

class BumpedBatchItem(pydantic.BaseModel):
	id:str=None
	priority:str=None
	data:str=None
	result:str=None
	type:str=None
	status:str=None
	source:str=None
	created_at:str=None
	updated_at:str=None

class TypeCount(pydantic.BaseModel):
	count: int
	type: str

class StatusCount(pydantic.BaseModel):
	count: int
	status: JobStatusEnum | None = None

class JobCount(pydantic.BaseModel):
	count: int
	type: str | None = None
	status: JobStatusEnum | None = None

class ItemQuery(pydantic.BaseModel):
	id: List[int] | None = None
	error: List[str] | None = None
	limit: List[int] | None = None
	priority: List[int] | None = None
	source: List[str] | None = None
	status: List[JobStatusEnum] | None = None
	throttle_key: List[str] | None = None
	ttl_seconds: List[int] | None = None
	type: List[str] | None = None



class JobTimes(pydantic.BaseModel):
	avg: int | None
	count:int | None
	max:int | None
	max_ttl:int | None
	med:int | None
	min:int | None
	min_ttl:int | None
	type: str | None


class WorkerStats(pydantic.BaseModel):
	worker_id: str | None
	job_count:float | None
	ms_per_job:float | None
	jobs_per_hour:float | None
	first_active:datetime | None
	current_job_started:datetime | None
	last_job_finished:datetime | None
	run_time:int | None
	work_time:int | None
	idle_time:int | None
	is_activbe:bool | None


class Action(pydantic.BaseModel):
	action:str
	data:str | None = None
