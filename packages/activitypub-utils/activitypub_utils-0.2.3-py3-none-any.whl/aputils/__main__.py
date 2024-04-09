#!/usr/bin/env python3
import aputils
import argparse
import json
import socket

from functools import cached_property, lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


HOME = f"""<!DOCTYPE html>
<html>
	<head>
		<title>ActivityPub Utilities Signature Verifier</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<style>
			a {{
				color: #A8D;
			}}

			a:hover {{
				color: #A6D;
			}}

			body {{
				color: white;
				background: #222;
				font-family: sans-serif;
				margin: 0px;
			}}

			h1 {{
				text-align: center;
				color: #A6D;
			}}

			p:first-child {{
				margin-top: 0px;
			}}

			p:last-child {{
				margin-botton: 0px;
			}}

			pre {{
				border: 1px solid transparent;
				border-radius: 5px;
				background: #403344;
				padding: 5px;
				overflow-x: auto;
			}}

			.section {{
				border: 1px solid transparent;
				border-radius: 5px;
				padding: 5px;
				background: #333;
				margin: 10px;
			}}
		</style>
	</head>
	<body>
		<h1 class="section">ActivityPub Utilities Signature Verifier</h1>

		<div class="section">
			<p>
				This server allows you to test your HTTP signature implementation. Just send a request
				of any method to an endpoint that is not any of the following:
			</p>
			<ul>
				<li>GET /</li>
				<li>GET /actor</li>
				<li>GET /.well-known/webfinger</li>
			</ul>
		</div>

		<div class="section">
			<p>
				The server will respond with a JSON message that includes some info sent to the server
				as well as whether or not the signature is valid. Example:
			</p>
			<pre>
{{
	"status": 200,
	"message": "HTTP signature is valid :3",
	"method": "GET",
	"path": "/heck",
	"address": "192.168.2.5",
	"valid": true,
	"headers": {{
		"Host": "valtest.barkshark.xyz",
		"User-Agent": "http.rb/5.1.1 (Mastodon/4.3.0-alpha.3+glitch; +https://barkshark.xyz/; im gay)",
		"Accept": "application/activity+json",
		"Accept-Encoding": "identity",
		"Content-Type": "application/activity+json",
		"Date": "Wed, 03 Apr 2024 17:24:50 GMT",
		"Signature": "[didn't wanna include this because it's so damn long]"
	}}
}}</pre>
		</div>

		<p class="section">
			Powered by
			<a href="https://git.barkshark.xyz/barkshark/aputils">ActivityPub Utilities/{aputils.__version__}</a>
		</p>
	</body>
</html>
""" # noqa: E501

ACTOR_BIO = """<p>Signature validation actor</p>
<p>Have an HTTP signature implementation you want to test? Just send a request to me. See more info
at <a href="{url}/">{url}</a>"""


def get_actor() -> aputils.JsonBase:
	return aputils.JsonBase({
		"@context": [
			"https://www.w3.org/ns/activitystreams"
		],
		"type": "Application",
		"id": f"{URL}/actor",
		"preferredUsername": "valtest",
		"name": "Signature Verifier",
		"summary": ACTOR_BIO.format(url = URL),
		"manuallyApprovesFollowers": True,
		"inbox": f"{URL}/inbox",
		"url": f"{URL}/",
		"endpoints": {
			"sharedInbox": f"{URL}/inbox"
		},
		"publicKey": {
			"id": keyid,
			"owner": f"{URL}/actor",
			"publicKeyPem": signer.pubkey
		}
	})


def get_machine_addr() -> str:
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
		try:
			sock.connect(("10.254.254.255", 1))
			return sock.getsockname()[0]

		except Exception:
			return "127.0.0.1"


class ClientError(Exception):
	...


class Response(aputils.JsonBase):
	def __init__(self,
				status: int,
				message: str,
				method: str,
				path: str,
				address: str,
				valid: bool,
				headers: dict[str, Any]) -> None:

		aputils.JsonBase.__init__(self,
			status = status, # type: ignore
			message = message, # type: ignore
			method = method, # type: ignore
			path = path.split("?", 1)[0], # type: ignore
			address = address, # type: ignore
			valid = valid, # type: ignore
			headers = headers # type: ignore
		)


class RequestHandler(BaseHTTPRequestHandler):
	default_request_version = "HTTP/1.1"
	signature: aputils.Signature
	actor: aputils.Message
	signer: aputils.Signer


	@property
	def content_length(self) -> int:
		try:
			return int(self.headers.get("Content-Length", 0))

		except ValueError:
			raise ClientError(f"Actor is larger than {args.size_limit} bytes") from None


	@property
	def method(self) -> str:
		return self.command.upper()


	@property
	def remote(self) -> str:
		return self.headers.get("X-Real-Ip", self.headers.get("X-Forwarded-For", self.address_string()))


	@cached_property
	def parsed_headers(self) -> dict[str, str]:
		headers = {}

		for key, value in self.headers.items():
			key = key.title()

			if key.startswith(("X-Forwarded", "X-Real")):
				continue

			headers[key] = value

		return headers


	def body(self) -> bytes:
		return self.rfile.read(self.content_length or -1)


	def log_request(self, status: int, length: int = 0) -> None: # type: ignore
		path = self.path.split("?", 1)[0]
		agent = self.headers.get("User-Agent", "n/a")
		message = f"{self.remote} \"{self.method} {path}\" {status} {length} {agent}"

		if not args.skip_date_log:
			date = self.date_time_string()
			message = f"[{date}] " + message

		print(message, flush = True)


	def send(self,
			status: int,
			message: aputils.JsonBase | str,
			headers: dict[str, str] | None = None) -> None:

		if isinstance(message, str):
			data = message.encode("utf-8")

		else:
			data = message.to_json().encode("utf-8")

		if headers is None:
			headers = {"Content-Type": "application/json"}

		if "Content-Type" not in headers:
			headers["Content-Type"] = "application/json"

		self.log_request(status, len(data))

		self.send_response_only(status, None)
		self.send_header("Server", self.version_string())
		self.send_header("Date", self.date_time_string())

		for key, value in headers.items():
			self.send_header(key, value)

		self.end_headers()

		self.wfile.write(data)
		self.wfile.flush()


	def send_error(self, status: int, message: str) -> None: # type: ignore
		response = Response(
			status,
			message,
			self.method,
			self.path,
			self.remote,
			False,
			self.parsed_headers
		)

		self.send(status, response, {"Content-Type": "application/json"})


	def handle_webfinger(self) -> None:
		try:
			path, query = self.path.split("?")

		except ValueError:
			self.send_error(400, "Missing query (ex. resource=acct:valtest@valtest.barkshark.xyz)")
			return

		if query != f"resource=acct:valtest@{args.hostname}":
			self.send_error(404, "Invalid user")
			return

		self.send(200, aputils.JsonBase({
			"subject": f"acct:valtest@{args.hostname}",
			"aliases": [
				f"{URL}/actor"
			],
			"links": [
				{
					"rel": "self",
					"type": "application/activity+json",
					"href": f"{URL}/actor"
				}
			]
		}))


	@lru_cache(maxsize = 1024, typed = True)
	def fetch_actor(self, url: str) -> aputils.Message:
		try:
			url, _ = url.split("#", 1)

		except ValueError:
			pass

		request = signer.sign_request(Request(
			url,
			method = "GET", headers = {
				"User-Agent": f"ApUtils Signature Verifier ({URL})"
			}
		))

		try:
			with urlopen(request) as response:
				if (length := int(response.headers.get("Content-Length", 0))) <= 0:
					raise ClientError("Actor body length is 0")

				if length > args.size_limit:
					raise ClientError(f"Actor is larger than {args.size_limit} bytes")

				return aputils.Message.parse(response.read())

		except HTTPError as error:
			msg = f"Failed to fetch actor: Status={error.code} Message='{str(error.read())}'"
			raise ClientError(msg) from None

		except json.JSONDecodeError as error:
			raise ClientError(f"Failed to parse actor: {str(error)}") from None

		except ValueError:
			raise ClientError("Content-Length header is not an integer") from None


	def parse_request(self) -> bool:
		if not BaseHTTPRequestHandler.parse_request(self):
			return False

		path = self.path.split("?", 1)[0]

		if self.method == "GET":
			if path == "/":
				self.send(200, HOME, {"Content-Type": "text/html"})
				return False

			if path == "/actor":
				self.send(200, get_actor(), {"Content-Type": "application/activity+json"})
				return False

			if path == "/.well-known/webfinger":
				self.handle_webfinger()
				return False

		if self.content_length > args.size_limit:
			self.send_error(400, f"Incoming message is larger than {args.size_limit} bytes")
			return False

		if self.method == "GET" and self.content_length:
			self.send_error(400, "GET messages should not have a body")
			return False

		if self.method in {"POST", "PUT"} and self.content_length <= 0:
			self.send_error(400, f"{self.method} messages should have a body")
			return False

		try:
			self.signature = aputils.Signature.new_from_headers(self.parsed_headers)

		except KeyError:
			self.send_error(400, "Missing signature header")
			return False

		try:
			self.actor = self.fetch_actor(self.signature.keyid)

		except ClientError as error:
			self.send_error(400, str(error))
			return False

		self.signer = aputils.Signer.new_from_actor(self.actor)

		if self.command.upper() == "GET" and self.content_length:
			self.send_error(400, "'GET' messages should not have a body")
			return False

		try:
			self.signer.validate_signature(self.method, path, self.parsed_headers)

		except aputils.SignatureFailureError as error:
			self.send_error(401, str(error))
			return False

		response = Response(
			200,
			"HTTP signature is valid :3",
			self.method,
			self.path,
			self.remote,
			True,
			self.parsed_headers
		)

		self.send(200, response)

		return False


parser = argparse.ArgumentParser(
	prog = "aputils",
	description = "Starts a server for validating HTTP signatures"
)

parser.add_argument("--hostname", "-n",
	help = "Domain or address this server will be hosted on (defaults to --addr value)")

parser.add_argument("--addr", "-a", default = "0.0.0.0",
	help = "IP address to listen on")

parser.add_argument("--port", "-p", default = 8080, type = int,
	help = "TCP port to listen on")

parser.add_argument("--size-limit", "-s", default = 1024 * 1024, type = int,
	help = "Max size of incoming or outgoing messages in bytes")

parser.add_argument("--protocol", "-r", default = "http", choices = ["https", "http"],
	help = "Supported protocol to advertise via the actor at /actor")

parser.add_argument("--skip-date-log", "-d", action = "store_true", default = False,
	help = "Don't append the date to the start of the access log lines")

args = parser.parse_args()

if args.hostname is None:
	args.hostname = args.addr if args.addr != "0.0.0.0" else get_machine_addr()

URL = f"{args.protocol}://{args.hostname}"
keyid = URL + "/actor#main-key"

if not (key := Path("privkey.pem")).exists():
	print("Creating private key. Please wait...", flush = True)
	signer = aputils.Signer.new(keyid)
	signer.export(key)

else:
	signer = aputils.Signer(key, keyid)

print(
	f"Starting server on {args.protocol}://{args.hostname} ({args.addr}:{args.port})",
	flush = True
)

server = ThreadingHTTPServer((args.addr, args.port), RequestHandler)

try:
	server.serve_forever()

except KeyboardInterrupt:
	pass
