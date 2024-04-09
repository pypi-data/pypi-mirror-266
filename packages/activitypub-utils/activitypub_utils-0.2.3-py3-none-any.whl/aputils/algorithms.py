from __future__ import annotations

import base64
import json
import typing

from Crypto import Hash
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import PKCS1_v1_5
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from urllib.parse import urlparse

from .enums import AlgorithmType
from .errors import SignatureFailureError
from .misc import Digest, HttpDate, Signature

if typing.TYPE_CHECKING:
	from collections.abc import Sequence
	from typing import Any
	from .message import Message
	from .signer import Signer

	class DataHash(typing.Protocol):
		def update(self, data: bytes) -> None: ...
		def digest(self) -> bytes: ...
		def hexdigest(self) -> str: ...


ALGORITHMS: dict[str, type[Algorithm]] = {}


def get(algo: AlgorithmType | str) -> type[Algorithm]:
	"""
		Fetch an algorithm class

		:param algo: Name of the class or an AlgorithmType enum associated with the class
		:raises KeyError: When a class could not be fetched
	"""

	if isinstance(algo, AlgorithmType):
		for cls in ALGORITHMS.values():
			if cls.algo_type == algo:
				return cls

		raise KeyError(algo)

	return ALGORITHMS[algo.lower()]


def register(algo: type[Algorithm]) -> type[Algorithm]:
	"""
		Register a new algorithm

		:param algo: Class of the new algorithm
		:raises KeyError: When an algorithm by the same name exists
	"""

	if algo.__name__.lower() in ALGORITHMS:
		raise KeyError(algo.__name__)

	ALGORITHMS[algo.__name__.lower()] = algo
	return algo


class Algorithm(ABC):
	"Represents an algorithm for signing and verifying signatures"

	algo_type: AlgorithmType
	"Name of the algorithm type"


	def __init__(self, signer: Signer) -> None:
		self.signer: Signer = signer


	@staticmethod
	@abstractmethod
	def hash_data(data: bytes | str) -> DataHash:
		"""
			Hash some data and return a `Hash` object

			:param data: Data to hash
		"""
		...


	@abstractmethod
	def verify_data(self, data: DataHash, signature: bytes) -> bool:
		"""
			Verify a signed hash

			:param data: Hash to verify
			:param signature: HTTP signature of the signed data hash
		"""
		...


	@abstractmethod
	def sign_data(self, data: DataHash) -> bytes:
		"""
			Sign a data hash

			:param data: Hash to sign
		"""
		...


	@staticmethod
	@abstractmethod
	def process_headers_for_signing(
			method: str,
			host: str | None,
			path: str,
			headers: dict[str, str],
			body: Message | dict[str, Any] | bytes | str | None = None) -> dict[str, str]:
		"""
			Process the headers of a response just before signing them

			:param method: HTTP method of the response
			:param host: Hostname of the target server
			:param path: Path of the response
			:param headers: Headers to be sent with the response
			:param body: Optional body data to be sent with the response
		"""
		...


	@staticmethod
	@abstractmethod
	def process_headers_for_validation(
			method: str,
			path: str,
			headers: dict[str, str],
			signature: Signature) -> dict[str, str]:
		"""
			Process the headers of a request just before validating them

			:param method: HTTP method of the request
			:param path: Path of the request
			:param headers: Headers sent with the request
			:param signature: HTTP signature for the request
		"""
		...


	@staticmethod
	def build_signing_string(
			headers: dict[str, str],
			used_headers: Sequence[str] | None = None) -> tuple[bytes, Sequence[str]]:
		"""
			Create a signing string from HTTP headers

			:param headers: Key/value pair of HTTP headers
			:param used_headers: List of headers to be used in the signing string
		"""

		if used_headers is None:
			used_headers = tuple(headers)

		data: bytes = ("\n".join(f"{key}: {headers[key]}" for key in used_headers)).encode("ascii")
		return data, used_headers


	def sign_headers(self,
					method: str,
					url: str,
					headers: dict[str, str],
					used_headers: Sequence | None = None,
					body: Message | dict[str, Any] | bytes | str | None = None) -> dict[str, str]:
		"""
			Create an HTTP signature for a request

			:param method: HTTP method of the request
			:param url: Location of the request
			:param headers: Headers to be sent with the request
			:param used_headers: Name of header keys to include in the signature
			:param body: Optional body of the request
		"""

		uri = urlparse(url)

		headers = type(self).process_headers_for_signing(
			method, uri.hostname, uri.path, headers, body
		)

		used_headers = tuple([*headers.keys(), *(used_headers or [])])
		hash_bytes, used_headers = type(self).build_signing_string(headers, used_headers)
		data_hash = self.hash_data(hash_bytes)

		sig_data = base64.b64encode(self.sign_data(data_hash)).decode("utf-8")
		signature = Signature(
			sig_data,
			self.signer.keyid,
			type(self).algo_type,
			used_headers
		)

		if type(self).algo_type == AlgorithmType.HS2019:
			signature.created = int(headers["(created)"])
			signature.expires = int(headers["(expires)"])

		for key in {"(request-target)", "(created)", "(expires)", "host"}:
			try:
				del headers[key]

			except KeyError:
				pass

		headers["signature"] = signature.compile()
		return headers


	def verify_headers(self,
						method: str,
						path: str,
						headers: dict[str, str],
						signature: Signature,
						body: Message | dict[str, Any] | bytes | str | None = None) -> bool:
		"""
			Verify the headers of a request

			:param method: HTTP method of the request
			:param path: Path of the request
			:param headers: Headers of the request
			:param signature: HTTP signature include in the request
			:param body: Body data of the request
		"""

		headers = self.process_headers_for_validation(method, path, headers, signature)

		if (digest := Digest.parse(headers.get("digest"))) is not None:
			if body is None:
				raise SignatureFailureError("A digest was added with an empty body")

			if not digest.validate(body):
				raise SignatureFailureError("Body digest does not match")

		sig_hash, _ = type(self).build_signing_string(headers, signature.headers)

		return self.verify_data(
			type(self).hash_data(sig_hash),
			base64.b64decode(signature.signature)
		)


@register
class HS2019(Algorithm):
	"""
		Represents the
		`HS2019 <https://datatracker.ietf.org/doc/id/draft-richanna-http-message-signatures-00.html>`_
		signing standard

		.. note:: This does not fully comply with the standard since a lot of fediverse software
			also don't. Use `http-message-signatures <https://pypi.org/project/http-message-signatures>`_
			instead if you need full compliance.
	"""

	algo_type: AlgorithmType = AlgorithmType.HS2019


	@staticmethod
	def hash_data(data: bytes | str) -> DataHash:
		if isinstance(data, str):
			data = bytes(data, encoding = "utf-8")

		return Hash.SHA256.new(data = data)


	def verify_data(self, data: DataHash, signature: bytes) -> bool:
		if not isinstance(self.signer.key, RsaKey):
			raise TypeError("Signer key is not an RSA Key")

		return PKCS1_v1_5.new(self.signer.key).verify(data, signature)


	def sign_data(self, data: DataHash) -> bytes:
		if not isinstance(self.signer.key, RsaKey):
			raise TypeError("Signer key is not an RSA Key")

		return PKCS1_v1_5.new(self.signer.key).sign(data)


	@staticmethod
	def process_headers_for_signing(
			method: str,
			host: str | None,
			path: str,
			headers: dict[str, str],
			body: Message | dict[str, Any] | bytes | str | None = None) -> dict[str, str]:

		from .message import Message

		if body is not None:
			if isinstance(body, Message):
				body = body.to_json()

			elif isinstance(body, dict):
				body = json.dumps(body)

			if not isinstance(body, bytes):
				body = bytes(body, encoding = "utf-8")

		headers = {key.lower(): value for key, value in headers.items()}

		if host:
			headers["host"] = host

		raw_date: HttpDate | datetime | str = headers.get("date", HttpDate.new_utc())

		if isinstance(raw_date, str):
			date = HttpDate.parse(raw_date)

		elif isinstance(raw_date, datetime) and not isinstance(raw_date, HttpDate):
			date = HttpDate.new_from_datetime(raw_date)

		else:
			date = raw_date

		if date + timedelta(hours = 6) >= (new_date := HttpDate.new_utc()):
			date = new_date

		headers.update({
			"date": date.to_string(),
			"(request-target)": f"{method.lower()} {path}",
			"(created)": str(date.timestamp()),
			"(expires)": str((date + timedelta(hours=6)).timestamp())
		})

		if body is not None:
			headers.update({
				"digest": Digest.new(body).compile(),
				"content-length": str(len(body))
			})

		return headers


	@staticmethod
	def process_headers_for_validation(
			method: str,
			path: str,
			headers: dict[str, str],
			signature: Signature) -> dict[str, str]:

		headers = {key.lower(): value for key, value in headers.items()}
		headers["(request-target)"] = f"{method.lower()} {path}"

		if signature.created is not None:
			if signature.created_date > HttpDate.new_utc():
				raise SignatureFailureError("Signature creation date is in the future")

			headers["(created)"] = str(signature.created)

		if signature.expires is not None:
			if signature.expires_date < HttpDate.new_utc():
				raise SignatureFailureError("Signature has expired")

			headers["(expires)"] = str(signature.expires)

		return headers


@register
class RsaSha256(HS2019):
	"Represents an old signing standard that is a subset of HS2019"

	algo_type: AlgorithmType = AlgorithmType.RSASHA256


	@staticmethod
	def process_headers_for_signing(
			method: str,
			host: str | None,
			path: str,
			headers: dict[str, str],
			body: Message | dict[str, Any] | bytes | str | None = None) -> dict[str, str]:

		headers = HS2019.process_headers_for_signing(method, host, path, headers, body)

		del headers["(created)"]
		del headers["(expires)"]

		return headers


	@staticmethod
	def process_headers_for_validation(
			method: str,
			path: str,
			headers: dict[str, str],
			signature: Signature) -> dict[str, str]:

		headers = {key.lower(): value for key, value in headers.items()}
		headers["(request-target)"] = f"{method.lower()} {path}"

		return headers
