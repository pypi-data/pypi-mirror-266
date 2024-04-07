from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import datetime
#import octomy.utils
#import octomy.utils.expiry_cache
import jinja2
import logging
import os
import pprint
import traceback


logger = logging.getLogger(__name__)

def gen_tags(parts):
	tags = ["-".join(parts[:-1])] + [part for part in parts]
	# logger.info(f"TAGS: {pprint.pformat(parts)} --> {tags}")
	return  tags




def url_for(index):
	return "http://TODO_MAKE_URLFOR/"+str(index)

class AutoRouter:

	def __init__(self, app, context):
		self.app = app
		self.context = context
		self.env = self.prepare_env()
		self.auto_routes = {}
		self.auto_route_all(self.context.webroot)
		#logger.info(f"ROUTES: {pprint.PrettyPrinter(indent=4, compact=False).pformat(self.auto_routes)}")


	def prepare_env(self):
		loader = jinja2.ChoiceLoader(
			[
				jinja2.FileSystemLoader(self.context.webroot)
	#			, jinja2.FileSystemLoader(os.path.join(project_folder, os.path.dirname(template_name)))
			]
		)
		env = jinja2.Environment(loader=loader)
		env.globals['datetime'] = datetime
		env.globals['context'] = self.context
#		env.globals['current_user'] = user
#		env.globals['current_user_can'] = current_user_can
#		env.globals['url_for'] = url_for
		#env.globals.update(get_expiry=octomy.utils.expiry_cache.get_expiry)
		#env.filters['myfilter'] = filter
		return env


	def subpages(self, path, max_level=2):
		out = {}
		#space = max_level * "   "
		parts = os.path.normpath(path).strip(os.path.sep).split(os.path.sep) 
		path = "/".join(parts)
		obj = self.auto_routes.get(path, dict())
		if max_level > 1:
			out[path] = obj
			if obj:
				subs = obj.get("children", list())
				for sub in subs:
					subsubs = self.subpages(sub, max_level - 1)
					for subsub in subsubs:
						if subsub not in out:
							subobj = self.auto_routes.get(subsub, dict())
							if subobj:
								out[subsub] = subobj
		return out


	def handler_raw(self, path):
		try:
			template_fn = f"{self.context.webroot}/{path}/index.html"
			template_string = ""
			parts = os.path.normpath(path).strip(os.path.sep).split(os.path.sep) 
			#dir = Path(os.path.relpath(os.path.dirname(template), self.context.webroot))
			subs = self.subpages(path, 4)
			#return f"subpages {pprint.pformat(subs)}", None
			logger.info(f"Reading template {template_fn}:")
			with open(template_fn, "r") as template_file:
				template_string = template_file.read()
				#logger.info(f"Content was: {template_string}")
			#return template_string, None
			template = self.env.from_string(template_string)
			if not template:
				return None, f"Error creating template for '{template_fn}'"
			#logger.info(f"template_fn:{template_fn}")
			html = template.render(title="TODO: Set title from context", subpages=subs)
			return html, None
		except Exception as e:
			logger.exception(f"Could not handle {path}")
			return None, f"Error rendering template '{template_fn}' with error\n{traceback.format_exc()}"


	def auto_route_all(self, base):
		for path in Path(base).rglob('index.html'):
			self.auto_route_path(path)
	

	def auto_route_path(self, template_fn):
		dir = Path(os.path.relpath(os.path.dirname(template_fn), self.context.webroot))
		self.auto_routes[str(dir)] = { "children":[], "path": str(dir), "title": os.path.basename(str(dir)).capitalize() }
		name = os.path.basename(dir)
		#logger.info(f"GOT ROUTE{pprint.pformat(dir.parts)} {name}")
		self.app.add_api_route(path=f"/{dir}", endpoint=self.handler, methods=["GET"], tags=gen_tags(dir.parts), name=name, response_class=HTMLResponse)
		acc = []
		for part in dir.parts:
			key = "/".join(acc)
			node = self.auto_routes.get(key, dict())
			children = node.get("children", list())
			childkey = f"{key}/{part}"
			if childkey not in children:
				children.append(childkey)
			node["children"] = children
			node["path"] = str(key)
			node["title"] = os.path.basename(str(key)).capitalize()
			self.auto_routes[key] = node
			#index_page(str(key))
			acc.append(part)
		return {"dir":dir, "name":name, }
	

	def handler(self, request:Request):
		path = request.scope['route'].path
		logger.info(f"GOT HANDLER{pprint.pformat(path)}, {pprint.pformat(request.path_params)} {request.url.path}")
		res, err =  self.handler_raw(path)
		if err:
			return HTTPException(status_code=500, detail=err)
		return HTMLResponse(content=res, status_code=200)
