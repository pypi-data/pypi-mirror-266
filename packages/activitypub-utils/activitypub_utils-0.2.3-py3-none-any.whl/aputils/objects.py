from __future__ import annotations

import re
import typing

from .misc import JsonBase
from .enums import (
	NodeinfoProtocol,
	NodeinfoServiceInbound,
	NodeinfoServiceOutbound,
	NodeinfoVersion
)

if typing.TYPE_CHECKING:
	from typing import Any

	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


class NewWebFingerType(typing.TypedDict):
	subject: str
	aliases: list[str]
	links: list[dict[str, str]]


class NewNodeinfoType(typing.TypedDict):
	version: str
	software: dict[str, str]
	protocols: list[NodeinfoProtocol]
	services: dict[str, list[Any]]
	openRegistrations: bool
	usage: dict[str, int | dict[str, int]]
	metadata: dict[str, Any] | None


class HostMeta(str):
	"An object that represents the ``/.well-known/host-meta`` endpoint"

	def __new__(cls: type[Self], data: str) -> Self:
		return str.__new__(cls, data)


	@classmethod
	def new(cls: type[Self], domain: str) -> Self:
		"""
			Generate a new host-meta xml string

			:param domain: Domain to use for the template url
		"""
		return cls(f"""<?xml version="1.0" encoding="UTF-8">
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
	<Link rel="lrdd" template="https://{domain}/.well-known/webfinger?resource={{uri}}" />
</XRD>""")


class HostMetaJson(JsonBase):
	"An object that represents the ``/.well-known/host-meta.json`` endpoint"

	@classmethod
	def new(cls: type[Self], domain: str) -> Self:
		"""
			Generate a new host-meta dict

			:param domain: Domain to use for the template url
		"""
		return cls({
			"links": [
				{
					"rel": "lrdd",
					"template": f"https://{domain}/.well-known/webfinger?resource={{uri}}"
				}
			]
		})


class Nodeinfo(JsonBase):
	"An object that represents a nodeinfo endpoint"

	@classmethod
	def new(cls: type[Self],  # pylint: disable=too-many-locals,too-many-arguments
			name: str,
			version: str,
			protocols: list[NodeinfoProtocol | str] | str | None = None,
			insrv: list[NodeinfoServiceInbound | str] | None = None,
			outsrv: list[NodeinfoServiceOutbound | str] | None = None,
			metadata: dict[str, Any] | None = None,
			repo: str | None = None,
			homepage: str | None = None,
			open_regs: bool = True,
			users: int = 0,
			halfyear: int = 0,
			month: int = 0,
			posts: int = 0,
			comments: int = 0) -> Self:
		"""
			Create a new nodeinfo object. It will default to version 2.0 if ``repo`` and ``homeage``
			are not set.

			:param name: Software name to use. Can only include lowercase letters and "-", "_"
				characters.
			:param version: Version of the software.
			:param protocols: List of supported protocols
			:param insrv: Supported inbound services
			:param outsrv: Supported outbound services
			:param metadata: Extra server info
			:param repo: Url to the repository that hosts the server code
			:param homepage: Url to the homepage of the server software
			:param open_regs: Whether user registrations are open or not
			:param users: Total number of registered users
			:param halfyear: Number of active users in the past 6 months
			:param month: Number of active users in the past month
			:param posts: Total number of posts
			:param comments: Total number of comments
		"""

		if protocols is None:
			protocols = []

		if insrv is None:
			insrv = []

		if outsrv is None:
			outsrv = []

		else:
			outsrv = list(NodeinfoServiceOutbound.parse(v) for v in outsrv)

		if metadata is None:
			metadata = {}

		if not re.match("^[a-z0-9-]+$", name):
			raise ValueError("Invalid software name. Must match regex: ^[a-z0-9-]+$")

		if isinstance(protocols, str):
			protocols = [protocols]

		elif not isinstance(protocols, (list, set, tuple)):
			raise TypeError("Protocols must be a list, set, or tuple")

		data: NewNodeinfoType = {
			"version": "2.1" if repo or homepage else "2.0",
			"software": {
				"name": name,
				"version": version
			},
			"protocols": list(NodeinfoProtocol.parse(v) for v in protocols),
			"services": {
				"inbound": list(NodeinfoServiceInbound.parse(v) for v in insrv),
				"outbound": outsrv
			},
			"openRegistrations": open_regs,
			"usage": {
				"localPosts": posts,
				"localComments": comments,
				"users": {
					"total": users,
					"activeHalfyear": halfyear,
					"activeMonth": month,
				}
			},
			"metadata": metadata
		}

		if repo:
			data["software"]["repository"] = repo

		if homepage:
			data["software"]["homepage"] = homepage

		return cls(data)


	@property
	def sw_name(self) -> str:
		"Get the software name at ``Nodeinfo['software']['name']``"
		return self["software"]["name"]


	@property
	def sw_version(self) -> str:
		"Get the software version at ``Nodeinfo['software']['version']``"
		return self["software"]["version"]


class Webfinger(JsonBase):
	"An object that represents the ``/.well-known/webfinger`` endpoint"


	@classmethod
	def new(cls: type[Self],
			handle: str,
			domain: str,
			actor: str,
			profile: str | None = None,
			interaction: str | None = None) -> Self:
		"""
			Create a new webfinger object

			:param handle: Username of the account
			:param domain: Domain the account resides on
			:param actor: URL that points to the ActivityPub Actor of the account
			:param profile: URL that points to an HTML representation of the account
			:param interaction: URL used for remote interaction
		"""
		data: NewWebFingerType = {
			"subject": f"acct:{handle}@{domain}",
			"aliases": [actor],
			"links": [{
				"rel": "self",
				"type": "application/activity+json",
				"href": actor
			}]
		}

		if profile:
			data["aliases"].append(profile)
			data["links"].append({
				"rel": "http://webfinger.net/rel/profile-page",
				"type": "text/html",
				"href": profile
			})

		if interaction:
			data["links"].append({
				"rel": "http://ostatus.org/schema/1.0/subscribe",
				"template": interaction
			})

		return cls(data)


	@property
	def handle(self) -> str:
		"Username of the account"
		return self["subject"][5:].split("@", 1)[0]


	@property
	def domain(self) -> str:
		"Domain the account resides on"
		return self["subject"][5:].split("@", 1)[1]


	@property
	def profile(self) -> str:
		"URL to the HTML representation of the account"
		return self.get_link("profile")


	@property
	def actor(self) -> str:
		"URL that points to the ActivityPub Actor of the account"
		return self.get_link("actor")


	@property
	def interaction(self) -> str:
		"URL used for remote interaction"
		return self.get_link("interaction")


	def get_link(self, link_type: str) -> str:
		"""
			Get a URL for the account

			:param link_type: The type of URL to get [profile, actor, interaction]
		"""

		for link in self["links"]:
			if link_type == "profile" and link["rel"] == "http://webfinger.net/rel/profile-page":
				return link["href"]

			if link_type == "actor" and link["rel"] == "self":
				return link["href"]

			if link_type == "interaction" and link["rel"] == "http://ostatus.org/schema/1.0/subscribe":
				return link["template"]

		raise KeyError(link_type)


class WellKnownNodeinfo(JsonBase):
	"An object that represents the ``/.well-known/nodeinfo`` endpoint"

	@classmethod
	def new(cls: type[Self],
			v20: str | None = None,
			v21: str | None = None) -> Self:
		"""
			Create a new ``WellKnownNodeinfo`` object by specifying the url(s)

			:param v20: URL pointing to a nodeinfo v2.0 object
			:param v21: Url pointing to a nodeinfo v2.1 object
		"""

		if not (v20 or v21):
			raise ValueError("At least one nodeinfo version must be specified")

		data = []

		if v20:
			data.append({
				"rel": NodeinfoVersion.V20.value,
				"href": v20
			})

		if v21:
			data.append({
				"rel": NodeinfoVersion.V21.value,
				"href": v21
			})

		return cls({"links": data})


	@classmethod
	def new_template(cls: type[Self],
					domain: str,
					path: str = "/nodeinfo",
					v20: bool = True,
					v21: bool = True) -> Self:
		"""
			Create a new ``WellKnownNodeinfo`` object by specifying the domain, path, and which
			versions to include.

			:param domain: Domain to use for urls
			:param path: Base path for urls
			:param v20: If true, generate a Nodeinfo v2.0 url
			:param v21: If true, generate a Nodeinfo v2.1 url

			:raises ValueError: When both ``v20`` and ``v21`` are ``False``
		"""

		if not (v20 or v21):
			raise ValueError("At least one nodeinfo version must be specified")

		if path.endswith("/"):
			path = path[:-1]

		if not path.startswith("/"):
			path = "/" + path

		urls = {}

		if v20:
			urls["v20"] = f"https://{domain}{path}/2.0.json"

		if v21:
			urls["v21"] = f"https://{domain}{path}/2.1.json"

		return cls.new(**urls)


	@property
	def v20(self) -> str:
		"Try to get the v2.0 url. Shortcut for ``Nodeinfo.get_url('20')``"
		return self.get_url("20")


	@property
	def v21(self) -> str:
		"Try to get the v2.0 url. Shortcut for ``Nodeinfo.get_url('21')``"
		return self.get_url("21")


	def get_url(self, version: str = "20") -> str:
		"""
			Get a versioned nodeinfo url

			:param version: The nodeinfo version url to get

			:raises KeyError: If the url for the specified nodeinfo version cannot be found
		"""

		for item in self["links"]:
			if item["rel"] == NodeinfoVersion.parse("V" + version):
				return item["href"]

		raise KeyError(version)
