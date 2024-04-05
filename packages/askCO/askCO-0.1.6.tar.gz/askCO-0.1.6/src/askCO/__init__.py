from requests import get, post, exceptions
import json
import os
from sys import exit
import time


class Query():
	# Run a single query to the API to return either a page of results or a single resource
	# Provide the API key, a method (either GET or POST), and a complete URL and body (if POST)
	# Redirects cannot be allowed on a scroll POST request
	def __init__(self, api_key=None, method=None, url=None, data=None, allow_redirects=True, timeout=5, attempts=3, sleep=0.1, quiet=False):
		auth_key = "x-api-key"
		headers = {auth_key: api_key, "Content-Type": "application/json", "Accept": "application/json;profiles=tepapa.collections.api.v1"}

		self.response = None

		# TODO: Review error handling - when to keep trying, when to fall back
		for attempt in range(attempts):
			if self.response == None:
				try:
					if not quiet:
						print("Requesting {}".format(url))
					if method == "GET":
						self.response = get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
					elif method == "POST":
						self.response = post(url, data=data, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
				except exceptions.Timeout:
					if not quiet:
						print("{} timed out!".format(url))
					time.sleep(sleep)
				except exceptions.ConnectionError:
					if not quiet:
						print("Disconnected trying to get {}".format(url))
					time.sleep(sleep)
				except exceptions.HTTPError:
					if not quiet:
						print(response.status_code)
					time.sleep(sleep)

		if self.response == None:
			print("Query {m} {u} failed".format(m=method, u=url))


class Request():
	def __init__(self, **kwargs):
		# Functional request settings
		self.quiet = kwargs.get("quiet")
		self.sleep = kwargs.get("sleep")

		# Request header settings
		self.api_key = kwargs.get("api_key")
		self.method = None
		self.allow_redirects = None
		self.timeout = kwargs.get("timeout")
		self.attempts = kwargs.get("attempts")

		# Query elements
		self.endpoint = kwargs.get("endpoint")
		self.base_url = "https://data.tepapa.govt.nz/collection"
		self.request_url = None
		self.request_body = None

		# Response element
		self.status_code = None
		self.response = None
		self.response_text = None
		self.error_message = None
		self.record_count = 0
		self.records = []

		# Switches to True when a 200, 204, or 404 status is returned
		# Look at self.status_code to handle retrying in other cases
		self.complete = False

	def send_query(self):
		if not self.api_key:
			raise ValueError("No api key found.")
			exit("No api key found.")

		self.response = Query(
			api_key=self.api_key,
			method=self.method,
			url=self.request_url,
			data=self.request_body,
			timeout=self.timeout,
			attempts=self.attempts,
			allow_redirects=self.allow_redirects,
			sleep=self.sleep,
			quiet=self.quiet).response

		self.status_code = self.response.status_code

		if not self.quiet:
			print("Request status {}".format(self.status_code))

		self.check_status()

	def check_status(self):
		# Check self.status_code and decide what to do
		if self.status_code == 200:
			# Successful completion of search or resource request
			if not self.quiet:
				print("Request completed successfully")
			if self.query_type == "search":
				self.save_records()
			elif self.query_type == "resource":
				if self.related == True:
					self.save_records()
				else:
					self.save_record()
			self.complete = True
		elif self.status_code == 204:
			# Successful completion of scroll request
			if not self.quiet:
				print("Scroll complete: no more results")
			self.complete = True
		elif self.status_code == 303:
			# Successful completion of a scroll page
			self.save_records()
			if self.query_type == "scroll":
				if self.method == "POST":
					if not self.quiet:
						print("Scroll successfully started")
					self.run_scroll()
		elif self.status_code == 422:
			# Failure to complete a scroll before the duration expired
			if not self.quiet:
				print("Duration limit exceeded")
			# Add function to re-run/resume
		elif self.status_code == 429:
			# API rate limit reached - need to pause requests until rate limit resets
			if not self.quiet:
				print("API rate limit exceeded. Cool off")
		else:
			if self.response:
				response_text = json.loads(self.response.text)
				self.error_message = self.response_text.get("userMessage")
				if not self.quiet:
					print("Error: {}".format(self.error_message))

	def save_records(self):
		# Save the result count for the search or scroll, save records
		response_text = json.loads(self.response.text)
		if not self.record_count:
			self.record_count = response_text["_metadata"]["resultset"]["count"]
			if not self.quiet:
				print("Retrieving {} records".format(self.record_count))

		if response_text.get("results"):
			self.records.extend([result for result in response_text["results"]])


class Search(Request):
	def __init__(self, **kwargs):
		Request.__init__(self, **kwargs)
		# Build a search for a specified page of results
		self.query_type = "search"
		self.query = kwargs.get("query")
		self.fields = kwargs.get("fields")
		self.sort = kwargs.get("sort")
		self.start = kwargs.get("start")
		self.size = kwargs.get("size")
		# Note that filters with multiple values only work for GET queries at the moment
		self.filters = kwargs.get("filters")
		self.exists = kwargs.get("exists")

		self.build_query()

	def build_query(self):
		if not self.endpoint:
			self.request_url = "{}/search".format(self.base_url)
			self.method = "POST"
			self.request_body = {}

			if self.query:
				self.request_body.update(self._singleValueFormatter("query", self.query))
			if self.fields:
				self.request_body.update(self._multiValueFormatter("fields", self.fields))
			if self.sort:
				self.request_body.update(self._singleValueFormatter("sort", self.sort))
			if self.start:
				self.request_body.update(self._singleValueFormatter("from", self.start))
			if self.size:
				self.request_body.update(self._singleValueFormatter("size", self.size))
			if self.filters:
				self.request_body.update(self._singleValueFormatter("filters", self.filters))

			# CO API requires post data to be json-encoded, not form-encoded
			self.request_body = json.dumps(self.request_body)

			if not self.quiet:
				print("Request body: {}".format(self.request_body))

		else:
			self.request_url = "{b}/{e}?q=".format(b=self.base_url, e=self.endpoint)
			self.method = "GET"

			url_parts = []
			query_parts = []

			if self.query:
				query_parts.append(self.query)
			if self.filters:
				for f in self.filters:
					if isinstance(f["keyword"], list):
						filter_value = "(" + " OR ".join(f["keyword"]) + ")"
					else:
						filter_value = f["keyword"]
					query_parts.append("{k}:{v}".format(k=f["field"], v=filter_value))
			if self.exists:
				query_parts.append("_exists_:{}".format(self.exists))

			query_string = " AND ".join(query_parts)
			url_parts.append(query_string)
			
			if self.fields:
				url_parts.append("fields={}".format(self.fields))
			if self.start:
				url_parts.append("from={}".format(self.start))
			if self.size:
				url_parts.append("size={}".format(self.size))
			if self.sort:
				url_parts.append("sort={}".format(self.sort))

			self.request_url += "&".join(url_parts)

			if not self.quiet:
				print("Search url: {}".format(self.request_url))
		
	def _singleValueFormatter(self, param_name, value):
		return {param_name: value}

	def _multiValueFormatter(self, param_name, values):
		return {param_name: ",".join(values)}


class Scroll(Request):
	# Continually call all matching records until done
	def __init__(self, **kwargs):
		Request.__init__(self, **kwargs)
		self.query_type = "scroll"
		self.allow_redirects = False

		self.query = kwargs.get("query")
		self.fields = kwargs.get("fields")
		self.sort = kwargs.get("sort")
		self.size = kwargs.get("size")
		self.filters = kwargs.get("filters")
		self.duration = kwargs.get("duration")
		self.exists = kwargs.get("exists")

		self.record_limit = None

		if kwargs.get("max_records") != -1:
			self.record_limit = kwargs.get("max_records")

		self.build_query()

	def build_query(self):
		if not self.endpoint:
			slug = "search"
		else:
			slug = self.endpoint

		scroll_base_url = "{b}/{s}/_scroll/?q=".format(b=self.base_url, s=slug)

		query_parts = []

		if self.query:
			query_parts.append(self.query)
		if self.filters:
			for f in self.filters:
				query_parts.append("{k}:{v}".format(k=f["field"], v=f["keyword"]))
		if self.exists:
			query_parts.append("_exists_:{}".format(self.exists))

		url_parts = []
		url_parts.append(" AND ".join(query_parts))

		if self.fields:
			url_parts.append("fields={}".format(self.fields))
		if self.size:
			url_parts.append("size={}".format(self.size))
		if self.duration:
			url_parts.append("duration={}".format(self.duration))

		self.method = "POST"
		self.request_url = scroll_base_url + "&".join(url_parts)

	def run_scroll(self):
		while self.status_code == 303:
			if self.record_limit:
				if len(self.records) >= self.record_limit:
					if not self.quiet:
						print("Scroll hit record limit")
					break

			self.method = "GET"
			self.request_url = "{b}{l}".format(b=self.base_url, l=self.response.headers["Location"])
			self.send_query()
			time.sleep(self.sleep)


class Resource(Request):
	# Resource object to build a query and hold a returned resource
	def __init__(self, **kwargs):
		Request.__init__(self, **kwargs)
		self.query_type = "resource"
		self.method = "GET"
		self.irn = kwargs.get("irn")
		self.related = kwargs.get("related")
		self.size = None
		self.types = None

		self.build_query()

	def build_query(self):
		if not self.endpoint:
			self.endpoint = "object"
		self.request_url = "{b}/{e}/{i}".format(b=self.base_url, e=self.endpoint, i=self.irn)

		# Build a search for related
		if self.related == True:
			self.request_url += "/related"
			if self.size or self.types:
				self.request_url += "?"
			if self.size:
				self.request_url += "size={}".format(size)
			if self.size and self.types:
				self.request_url += "&"
			if self.types:
				self.request_url += "types={}".format(types)

	def save_record(self):
		self.response_text = json.loads(self.response.text)
