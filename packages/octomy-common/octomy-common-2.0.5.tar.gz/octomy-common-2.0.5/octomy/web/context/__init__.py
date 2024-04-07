from fastapi import Depends
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Any, Callable, Set, List, Optional, Annotated
import logging
import octomy.access
import octomy.config
import octomy.db
import octomy.batch
import pprint
import asyncio

logger = logging.getLogger(__name__)


DEFAULT_ADMIN_PATH="overwatch"

def url_for(name:str) -> str:
	url = f"http://CONTEXT_URL_FOR/{name}"
	logger.info(f"Generated url '{url}'")
	return  url



#required_scopes=["overwatch.access.profile.view"]
#required_scopes: List[str]

class Context(BaseSettings):
	config: octomy.config.OctomyConfig | None
	access: octomy.access.AccessContext | None
	db: octomy.db.Database | None
	bp: octomy.batch.Processor | None
#	current_user: Optional[octomy.access.User] = octomy.access.get_current_user()
#	url_for:Callable[[str], str] = url_for # SUBSTITUTE WITH NATIVE FASTAPI request.url_for() INSTEAD
	admin_path:str = DEFAULT_ADMIN_PATH
	required_scopes:List[str] = list()
	#@property
	#def url_for(self, key) -> str:
	#	return url_for(key)
#	data:Data = Data()
#	parts:Parts = Parts()
#	search_engine:SearchEngine = SearchEngine()
	webroot: str = "/app/webroot"
	password_cost_factor:int = 12


def default_decorator_function(undecorated_context:Context):
	return undecorated_context

_dec_fun = default_decorator_function

def set_context_decorator(dec_fun):
	_dec_fun = dec_fun



def scoped_context(s:list):
	return Annotated[Context, Depends(context_dependency(required_scopes=s))]



#@lru_cache
def get_context(required_scopes: Optional[List[str]] = None) -> Context:
	config:octomy.config.OctomyConfig = octomy.config.get_config()
	db:octomy.db.Database = octomy.db.get_database(config)
	bp:octomy.batch.Processor = octomy.batch.Processor(config, db)
	access:octomy.access.AccessContext = octomy.access.get_access_context(required_scopes)
	logger.info(f"AccessContext: {pprint.pformat(access)}")
	return Context(config=config, access=access, db=db, bp=bp, admin_path = config.get("app-admin-path", DEFAULT_ADMIN_PATH))


# Helper dependency
def context_dependency(required_scopes: Optional[List[str]] = None):
	async def dependency():
		return get_context(required_scopes=required_scopes)
	return dependency

