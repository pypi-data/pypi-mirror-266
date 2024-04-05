from __init__ import Search, Scroll, Resource
import os

# Register for an API key at https://data.tepapa.govt.nz/docs/register.html
# Save it to the environment variable "TE-PAPA-KEY"
api_key = os.environ.get("TE-PAPA-KEY")

# Set functional parameters
quiet = False
sleep = 0.1
timeout = 5
attempts = 3

def try_search():
	# Set the search request parameters
	# Can only use multiple terms on a single filter for a GET query with a specified endpoint
	query = "Myosotis"
	endpoint = "object"
	filters = [{"field": "type", "keyword": "Specimen"}, {"field": "collection", "keyword": ["Plants", "LandMammals"]}]
	fields = None
	size = 100
	start = 0

	# Create the query object
	request = Search(api_key=api_key,
		query=query,
		endpoint=endpoint,
		filters=filters,
		fields=fields,
		size=size,
		start=start,
		timeout=timeout,
		attempts=attempts,
		sleep=sleep,
		quiet=quiet)

	# Run the query
	request.send_query()

	# See what you got
	print("Search returned {} results".format(request.record_count))
	if request.record_count > 0:
		print("First result:")
		print(next(iter(request.records)))

def try_scroll():
	# Set the scroll request parameters
	# Endpoint specified, will only search the object endpoint
	# We'll only ask for records that have images using exists
	endpoint = "object"
	query = "wellington"
	filters = [{"field": "type", "keyword": "Object"}, {"field": "hasRepresentation.rights.allowsDownload", "keyword": "True"}]
	fields = "id,pid,hasRepresentation"
	exists = "hasRepresentation"
	size = 1000
	duration = 1
	max_records = 5000

	# Create the query object
	request = Scroll(api_key=api_key,
		endpoint=endpoint,
		query=query,
		filters=filters,
		fields=fields,
		exists=exists,
		size=size,
		timeout=timeout,
		attempts=attempts,
		sleep=sleep,
		quiet=quiet,
		duration=duration,
		max_records=max_records)

	# Run the query
	request.send_query()

	# See what you got
	print("Search returned {} results".format(request.record_count))
	if request.record_count > 0:
		print("First result:")
		print(next(iter(request.records)))

def try_resource():
	# Endpoint required
	endpoint = "agent"
	irn = 67415

	# Create the query object
	request = Resource(api_key=api_key,
		endpoint=endpoint,
		irn=irn,
		timeout=timeout,
		attempts=attempts,
		quiet=quiet,
		related=True)

	# Run the query
	request.send_query()
	request.save_record()

	# See what you got
	print("Received record for {e}/{i}".format(e=endpoint, i=irn))
	if request.response_text:
		print(request.response_text)

try_search()
#try_scroll()
#try_resource()