from __future__ import annotations

import base64
import json
import typing

from Crypto.Hash import SHA256, SHA512
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from .enums import AlgorithmType

if typing.TYPE_CHECKING:
	from collections.abc import Callable, Sequence
	from datetime import tzinfo

	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


HASHES = {
	"sha256": SHA256,
	"sha512": SHA512
}


def deprecated(new_method: str, version: str, remove: str | None = None) -> Callable[..., Any]:
	"""
		Decorator to mark a function as deprecated and display a warning on first use.

		:param new_method: Name of the function to replace the wrapped function
		:param version: Version of the module in which the wrapped function was considered
			deprecated
		:param remove: Version the wrapped function will get removed
	"""

	called = False

	def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
		@wraps(func)
		def inner(*args: Any, **kwargs: Any) -> Any:
			if not called:
				name = func.__qualname__ if hasattr(func, "__qualname__") else func.__name__

				if not remove:
					print(f"WARN: {name} was deprecated in {version}. Use {new_method} instead.")

				else:
					msg = f"WARN: {name} was deprecated in {version} and will be removed in "
					msg += f"{remove}. Use {new_method} instead."
					print(msg)

			return func(*args, **kwargs)
		return inner
	return wrapper


class Digest:
	"Represents a body digest"

	__slots__ = {"digest", "algorithm"}

	def __init__(self, digest: str, algorithm: str) -> None:
		"""
			Create a new digest object from an already existing digest

			:param digest: Base64 encoded hash
			:param algorithm: Algorithm used for hash in the format of ``{type}-{bytes}``
		"""

		self.digest = digest
		self.algorithm = algorithm


	def __repr__(self) -> str:
		return f"Digest({self.digest}, {self.algorithm})"


	def __str__(self) -> str:
		return self.compile()


	def __eq__(self, value: object) -> bool:
		if isinstance(value, Digest):
			return self.algorithm == value.algorithm and self.digest == value.digest

		if isinstance(value, (dict, str, bytes)):
			return self.validate(value)

		raise TypeError(f"Cannot compare '{type(value).__name__}' to 'Digest'")


	@classmethod
	def new(cls: type[Self],
			body: dict[str, Any] | str | bytes,
			size: int = 256) -> Self:
		"""
			Generate a new body digest

			:param body: Message body to hash
			:param size: SHA hash size
		"""

		if isinstance(body, dict):
			body = json.dumps(body).encode("utf-8")

		elif isinstance(body, str):
			body = body.encode("utf-8")

		if size >= 1024:
			size = int(size / 8)

		raw_hash = HASHES[f"sha{size}"].new(data=body)
		digest = base64.b64encode(raw_hash.digest()).decode("utf-8")

		return cls(digest, f"SHA-{size}")


	@classmethod
	def parse(cls: type[Self], digest: str | None) -> Self | None:
		"""
			Create a new digest from a digest header

			:param digest: Digest header
		"""

		if not digest:
			return None

		alg, digest = digest.split("=", 1)
		return cls(digest, alg)


	@classmethod
	@deprecated("Digest.parse", "0.1.9", "0.3.0")
	def new_from_digest(cls: type[Self], digest: str | None) -> Self | None:
		"""
			Create a new digest from a digest header

			:param digest: Digest header
		"""

		return cls.parse(digest)


	@property
	def hashalg(self) -> str:
		"Hash function used when creating the signature as a string"

		return self.algorithm.replace("-", "").lower()


	def compile(self) -> str:
		"Turn the digest object into a ``str`` for the Digest header"

		return "=".join([self.algorithm, self.digest])


	def validate(self, body: dict[str, Any] | str | bytes, hash_size: int = 256) -> bool:
		"""
			Check if the body digest matches the body

			:param body: Message body to verify
			:param hash_size: Size of the hashing algorithm
		"""

		return self == Digest.new(body, hash_size)


class HttpDate(datetime):
	"Datetime object with convenience methods for parsing and creating HTTP date strings"

	FORMAT: str = "%a, %d %b %Y %H:%M:%S GMT"
	"Format to pass to datetime when (de)serializing a raw HTTP date"


	def __new__(cls: type[Self],
				year: int,
				month: int,
				day: int,
				hour: int = 0,
				minute: int = 0,
				second: int = 0,
				microsecond: int = 0,
				tzinfo: tzinfo = timezone.utc) -> Self:

		return datetime.__new__(
			cls, year, month, day, hour, minute, second, microsecond, tzinfo
		)


	def __str__(self) -> str:
		return self.to_string()


	@classmethod
	def parse(cls: type[Self], date: datetime | str | int | float) -> Self:
		"""
			Parse a unix timestamp or HTTP date in string format

			:param date: Unix timestamp or string from an HTTP Date header
		"""

		if isinstance(date, cls):
			return date

		elif isinstance(date, datetime):
			return cls.fromisoformat(date.isoformat())

		elif isinstance(date, (int | float)):
			data = cls.fromtimestamp(float(date) if type(date) is int else date)

		else:
			data = cls.strptime(date, cls.FORMAT)

		return data.replace(tzinfo=timezone.utc)


	@classmethod
	@deprecated("HttpDate.parse", "0.2.3", "0.3.0")
	def new_from_datetime(cls: type[Self], date: datetime) -> Self:
		"""
			Create a new ``HttpDate`` object from a ``datetime`` object

			:param date: ``datetime`` object to convert
		"""
		return cls.fromisoformat(date.isoformat())


	@classmethod
	def new_utc(cls: type[Self]) -> Self:
		"Create a new ``HttpDate`` object from the current UTC time"
		return cls.now(timezone.utc)


	def timestamp(self) -> int:
		"Return the date as a unix timestamp without microseconds"
		return int(datetime.timestamp(self))


	def to_string(self) -> str:
		"Create an HTTP Date header string from the datetime object"
		return self.strftime(self.FORMAT)


class JsonBase(dict[str, Any]):
	"A ``dict`` with methods to convert to JSON and back"

	@classmethod
	@deprecated("JsonBase.parse", "0.1.5", "0.2.0")
	def new_from_json(cls: type[Self], data: str | bytes | dict | Self) -> Self:
		"""
			Parse a JSON object

			.. deprecated:: 0.1.5
				Use :meth:`JsonBase.parse` instead

			:param data: JSON object to parse
			:raises TypeError: When an invalid object type is provided
		"""
		return cls.parse(data)


	@classmethod
	def parse(cls: type[Self], data: str | bytes | dict | Self) -> Self:
		"""
			Parse a JSON object

			:param data: JSON object to parse
			:raises TypeError: When an invalid object type is provided
		"""
		if isinstance(data, (str, bytes)):
			data = json.loads(data)

		if isinstance(data, cls):
			return data

		if not isinstance(data, dict):
			raise TypeError(f"Cannot parse objects of type \"{type(data).__name__}\"")

		return cls(data)


	def to_json(self, indent: int | str | None = None, **kwargs: Any) -> str:
		"""
			Return the message as a JSON string

			:param indent: Number of spaces or the string to use for indention
			:param kwargs: Keyword arguments to pass to :func:`json.dumps`
		"""

		return json.dumps(self, indent = indent, default = self.handle_value_dump, **kwargs)


	def handle_value_dump(self, value: Any) -> Any:
		"""
			Gets called when a value is of the wrong type and needs to be converted for dumping to
			json. If the type is unknown, it will be forcibly converted to a ``str``.

			:param value: Value to be converted
		"""

		if not isinstance(value, (str, int, float, bool, dict, list, tuple, type(None))):
			print(f"Warning: Cannot properly convert value of type '{type(value).__name__}'")
			return str(value)

		return value


class MessageDate(HttpDate):
	"""
		Datetime object with convenience methods for parsing and creating ActivityPub message date
		strings
	"""

	FORMAT: str = "%Y-%m-%dT%H:%M:%SZ"
	"Format to pass to datetime when (de)serializing a raw message date"


class Signature:
	"""
		Represents a signature header with access to values as attributes

		.. note:: ``created`` and ``expires`` properties will be :class:`datetime.datetime` objects
			in 0.3.0
	"""

	__slots__ = {"keyid", "algorithm", "headers", "signature", "created", "expires"}

	def __init__(self,
				signature: str,
				keyid: str,
				algorithm: AlgorithmType | str,
				headers: Sequence[str] | str,
				created: int | None = None,
				expires: int | None = None) -> None:
		"""
			Create a new signature object. This should not be initiated directly.

			:param signature: Generated signature hash
			:param keyid: URL of the public key
			:param algorithm: Hashing and signing algorithms used to create the signature
			:param headers: Header keys used to create the signature
			:param created: Unix timestamp representing the signature creation date
			:param expires: Unix timestamp representing the date the signature expires
		"""

		self.signature: str = signature
		"Generated signature hash"

		self.keyid: str = keyid
		"URL of the public key"

		self.algorithm: AlgorithmType = algorithm # type: ignore
		"Hashing and signing algorithms used to create the signature"

		self.headers: Sequence[str] = headers
		"Header keys used to create the signature"

		self.created: int | None = created
		"Unix timestamp representing the signature creation date"

		self.expires: int | None = expires
		"Unix timestamp representing the date the signature expires"


	def __setattr__(self, key: str, value: Any) -> None:
		if key == "headers" and isinstance(value, str):
			value = value.split()

		elif key == "algorithm":
			value = AlgorithmType.parse(value)

		elif key in {"created", "expires"} and value is not None:
			value = int(value)

		object.__setattr__(self, key, value)


	def __repr__(self) -> str:
		data = {
			"keyid": repr(self.keyid),
			"algorithm": self.algorithm,
			"headers": self.headers,
			"created": self.created,
			"expires": self.expires
		}

		str_data = ", ".join(f"{key}={value}" for key, value in data.items())
		return f"Signature({str_data})"


	@classmethod
	def new_from_headers(cls: type[Self], headers: dict[str, str]) -> Self:
		"""
			Parse the signature from a header dict

			:param dict[str,str] headers: Header key/value pairs
			:raises KeyError: When the signature header(s) cannot be found
			:raises NotImplementedError: When a newer unsupported signature standard is provided
		"""

		headers = {key.lower(): value for key, value in headers.items()}

		if "signature-input" in headers:
			raise NotImplementedError("Newer signature spec not supported yet")

		signature = headers["signature"]
		data: dict[str, str] = {}

		for chunk in signature.strip().split(","):
			key, value = chunk.split("=", 1)
			data[key.lower()] = value.strip("\"")

		return cls(**data) # type: ignore


	@classmethod
	def parse(cls: type[Self], data: str) -> Self:
		"""
			Parse a Signature in string format

			:param str string: Signature string
		"""

		return cls.new_from_headers({"signature": data})


	@classmethod
	@deprecated("Signature.parse", "0.1.9", "0.3.0")
	def new_from_signature(cls: type[Self], string: str) -> Self:
		"""
			Parse a Signature header

			:param str string: Signature header string
		"""

		return cls.new_from_headers({"signature": string})


	@property
	def algs(self) -> tuple[str, str]:
		"Return the algorithms used for signing [0] and hashing [1]"
		return self.algorithm.value.split("-", 1) # type: ignore


	@property
	def hashalg(self) -> str:
		"Algorithm used for hashing"
		return self.algs[1]


	@property
	def signalg(self) -> str:
		"Algorithm used for signing"
		return self.algs[0]


	@property
	@deprecated("Signature.algorithm", "0.1.9", "0.3.0")
	def algorithm_type(self) -> AlgorithmType:
		"Type of algorithm used for this signature"

		return self.algorithm


	@property
	def created_date(self) -> HttpDate:
		if not self.created:
			raise AttributeError("Created timestamp not set")

		return HttpDate.parse(self.created)


	@created_date.setter
	def created_date(self, value: datetime) -> None:
		self.created = int(value.timestamp())


	@property
	def expires_date(self) -> HttpDate:
		if not self.expires:
			raise AttributeError("Expires timestamp not set")

		return HttpDate.parse(self.expires)


	@expires_date.setter
	def expires_date(self, value: datetime) -> None:
		self.expires = int(value.timestamp())


	def compile(self) -> str:
		"Generate a string for a Signature header"

		data = {
			"keyId": self.keyid,
			"algorithm": self.algorithm.value,
			"headers": " ".join(self.headers),
			"created": self.created,
			"expires": self.expires,
			"signature": self.signature
		}

		return ",".join([f"{k}=\"{v}\"" for k, v in data.items() if v is not None])
