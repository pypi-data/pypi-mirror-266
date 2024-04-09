from __future__ import annotations

import typing

from urllib.request import Request as UrllibRequest

if typing.TYPE_CHECKING:
	from collections.abc import Callable
	from typing import Any
	from .enums import AlgorithmType

	try:
		from .signer import Signer

	except ImportError:
		class Signer(typing.Protocol): # type: ignore
			def sign_headers(self,
							method: str,
							url: str,
							data: dict[str, Any] | bytes | str | None = None,
							headers: dict[str, str] | None = None,
							algorithm: AlgorithmType = AlgorithmType.HS2019,
							sign_all: bool = False) -> dict[str, Any]: ...

			def validate_signature(self,
									method: str,
									path: str,
									headers: dict[str, Any],
									body: bytes | str | None = None) -> bool: ...

	SignerFunc = Callable[[Signer, Any, AlgorithmType], Any]
	ValidatorFunc = Callable[[Signer, Any], bool]


try:
	from requests import Request as RequestsRequest
	from requests import PreparedRequest as RequestsPreparedRequest

except ImportError:
	RequestsRequest = None # type: ignore
	RequestsPreparedRequest = None # type: ignore


try:
	from aiohttp.web import BaseRequest as AiohttpRequest

except ImportError:
	AiohttpRequest = None # type: ignore

try:
	from flask import Request as FlaskRequest

except ImportError:
	FlaskRequest = None # type: ignore

try:
	from sanic.request import Request as SanicRequest

except ImportError:
	SanicRequest = None # type: ignore


SIGNERS: dict[type[Any], SignerFunc] = {}
VALIDATORS: dict[type[Any], ValidatorFunc] = {}


def register_signer(request_type: type[Any]) -> Callable:
	"""
		Register a function to handle signing of a request type.

		:param request_type: Class of the request
	"""

	def wrapper(func: SignerFunc) -> SignerFunc:
		SIGNERS[request_type] = func
		return func

	return wrapper


def register_validator(request_type: type[Any]) -> Callable:
	"""
		Register a function to handle verification of a request type.

		:param request_type: Class of the request
	"""

	def wrapper(func: ValidatorFunc) -> ValidatorFunc:
		VALIDATORS[request_type] = func
		return func

	return wrapper


### Signers

@register_signer(UrllibRequest)
def sign_urllib(
			signer: Signer,
			request: UrllibRequest,
			algorithm: AlgorithmType) -> UrllibRequest:

	request_headers = dict(request.header_items())
	headers = signer.sign_headers(
		request.get_method().upper(),
		request.full_url, request.data,
		request_headers,
		algorithm = algorithm
	)

	request.headers = {key.title(): value for key, value in headers.items()}
	return request


if RequestsRequest is not None:
	@register_signer(RequestsRequest)
	def sign_requests(
				signer: Signer,
				request: RequestsRequest,
				algorithm: AlgorithmType) -> RequestsPreparedRequest:

		return sign_requests_prepared(signer, request.prepare(), algorithm)


if RequestsPreparedRequest is not None:
	@register_signer(RequestsPreparedRequest)
	def sign_requests_prepared(
				signer: Signer,
				request: RequestsPreparedRequest,
				algorithm: AlgorithmType) -> RequestsPreparedRequest:

		headers = signer.sign_headers(
			request.method,
			request.url,
			request.body,
			request.headers,
			algorithm = algorithm
		)

		request.headers = headers
		return request


### Validators

if AiohttpRequest is not None:
	@register_validator(AiohttpRequest)
	async def validate_aiohttp(signer: Signer, request: AiohttpRequest) -> bool:
		return signer.validate_signature(
			request.method,
			request.path,
			{key: value for key, value in request.headers.items()},
			await request.read()
		)


if FlaskRequest is not None:
	@register_validator(FlaskRequest)
	def validate_flask(signer: Signer, request: FlaskRequest) -> bool:
		return signer.validate_signature(
			request.method,
			request.path,
			{key: value for key, value in request.headers.items()},
			request.get_data()
		)


if SanicRequest is not None:
	@register_validator(SanicRequest)
	def validate_sanic(signer: Signer, request: SanicRequest) -> bool:
		return signer.validate_signature(
			request.method,
			request.path,
			{key: value for key, value in request.headers.items()},
			request.body
		)
