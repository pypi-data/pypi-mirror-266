from __future__ import annotations

import json
import re
import typing

from datetime import datetime
from functools import cached_property
from mimetypes import guess_type
from urllib.parse import urlparse

from .enums import ObjectType
from .errors import InvalidKeyError
from .misc import HttpDate, MessageDate, JsonBase
from .signer import Signer

if typing.TYPE_CHECKING:
	from collections.abc import Callable
	from typing import Any

	try:
		from typing import Self

	except ImportError:
		from typing_extensions import Self


T = typing.TypeVar("T")
TYPES: dict[str, type | tuple[type, ...]] = {
	"str": str,
	"int": int,
	"float": float,
	"bool": bool,
	"date": datetime,
	"dict": dict,
	"object": (dict, str),
	"list": (list, set, tuple)
}

CONVERTERS: dict[type, tuple[Callable, Callable]] = {
	datetime: (MessageDate.parse, lambda v: v.strftime(MessageDate.FORMAT)),
	HttpDate: (HttpDate.parse, lambda v: v.to_string()),
	MessageDate: (MessageDate.parse, lambda v: v.to_string()),
	dict: (JsonBase.parse, lambda v: JsonBase(v).to_json()),
	JsonBase: (JsonBase.parse, lambda v: v.to_json()),
	list: (json.loads, json.dumps)
}


class Property(typing.Generic[T]):
	"Represents a key in a dict"


	def __init__(self, type_name: str = "str") -> None:
		"""
			Create a new dict property

			:param key: Name of the key to be handled by this ``Property``
			:param value_type: Name of the value type to be used for (de)serialization
		"""

		self.key: str = ""
		self.type_name: str = type_name


	def __set_name__(self, obj: Any, key: str) -> None:
		self.key = Property.name_to_camel_case(key)


	def __get__(self, obj: Message | None, objtype: Any | None = None) -> Any:
		if obj is None:
			return self

		try:
			return obj[self.key]

		except KeyError:
			objname = object.__class__.__name__
			raise AttributeError(f"'{objname}' has no attribute '{self.key}'") from None


	def __set__(self, obj: Message, value: Any) -> None:
		if type(value) is dict:
			value = Message(value)

		obj[self.key] = value


	def __delete__(self, obj: Message) -> None:
		del obj[self.key]


	@staticmethod
	def name_to_snake_case(key: str) -> str:
		new_key = "_".join(re.split(r"(?<=.)(?=[A-Z])", key))
		return new_key.lower()


	@staticmethod
	def name_to_camel_case(key: str) -> str:
		if "_" not in key:
			return key

		parts = key.split("_")

		if len(parts) > 1:
			return "".join([parts[0], *(part.title() for part in parts[1:])])

		return parts[0]


	@classmethod
	def add_type(self,
				name: str,
				cls: type,
				deserializer: Callable,
				serializer: Callable) -> None:
		"""
			Add or update a value type

			:param name: Name of the value type
			:param cls: Class of the deserialized value
			:param serializer: Method that will turn the value into a JSON-friendly type
			:param deserializer: Method that will convert the value to the specified class
		"""

		TYPES[name] = cls
		CONVERTERS[cls] = (deserializer, serializer)


class Message(JsonBase):
	":class:`dict` object that represents an ActivityPub Object"

	__slots__: tuple[str, ...] = tuple([])


	id: Property[str] = Property("str")
	"``id`` key"

	type: Property[str] = Property("str")
	"``type`` key"

	accuracy: Property[float] = Property("float")
	"``accuracy`` key"

	actor: Property[str] | Message = Property("object")
	"``actor`` key"

	altitude: Property[float] = Property("float")
	"``altitude`` key"

	any_of: Property[dict[str, Any]] = Property("dict")
	"``anyOf`` key"

	attachment: Property[list[Attachment]] = Property("list")
	"``attachment`` key"

	attributed_to: Property[str | Message] = Property("object")
	"``attributedTo`` key"

	audience: Property[str | Message] = Property("object")
	"``audience`` key"

	bcc: Property[list[str]] = Property("list")
	"``bcc`` key"

	bto: Property[list[str]] = Property("list")
	"``bto`` key"

	cc: Property[list[str]] = Property("list")
	"``cc`` key"

	closed: Property[MessageDate] = Property("date")
	"``closed`` key"

	content: Property[str] = Property("str")
	"``content`` key"

	content_map: Property[dict] = Property("dict")
	"``contentMap`` key"

	context: Property[str] = Property("str")
	"``context`` key"

	created: Property[MessageDate] = Property("date")
	"``created`` key"

	current: Property[str] | Message = Property("object")
	"``current`` key"

	deleted: Property[MessageDate] = Property("date")
	"``deleted`` key"

	describes: Property[str] | Message = Property("object")
	"``describes`` key"

	devices: Property[str] = Property("str")
	"``devices`` key"

	discoverable: Property[bool] = Property("bool")
	"``discoverable`` key"

	duration: Property[int] = Property("str")
	"``duration`` key"

	end_time: Property[MessageDate] = Property("date")
	"``endTime`` key"

	endpoints: Property[str | Message] = Property("object")
	"``endpoints`` key"

	featured: Property[str] = Property("str")
	"``featured`` key"

	featured_tags: Property[str] = Property("str")
	"``featuredTags`` key"

	first: Property[str] = Property("str")
	"``first`` key"

	followers: Property[str] = Property("str")
	"``followers`` key"

	following: Property[str] = Property("following")
	"``following`` key"

	former_type: Property[str] = Property("str")
	"``formerType`` key"

	generator: Property[str | Message] = Property("object")
	"``generator`` key"

	height: Property[int] = Property("int")
	"``height`` key"

	href: Property[str] = Property("str")
	"``href`` key"

	href_lang: Property[str] = Property("str")
	"``hreflang`` key"

	icon: Property[str | Message] = Property("object")
	"``icon`` key"

	image: Property[str | Message] = Property("object")
	"``image`` key"

	in_reply_to: Property[str | Message] = Property("object")
	"``inReplyTo`` key"

	inbox: Property[str] = Property("str")
	"``inbox`` key"

	instrument: Property[str | Message] = Property("object")
	"``instrument`` key"

	obj_items: Property[dict[str, Any]] = Property("str")
	"``items`` key"

	last: Property[str] = Property("str")
	"``last`` key"

	latitude: Property[float] = Property("float")
	"``latitude`` key"

	link: Property[str | Message] = Property("object")
	"``link`` key"

	location: Property[str | Message] = Property("object")
	"``location`` key"

	longitude: Property[float] = Property("float")
	"``longitude`` key"

	manually_approves_followers: Property[bool] = Property("bool")
	"``manuallyApprovesFollowers`` key"

	media_type: Property[str] = Property("str")
	"``mediaType`` key"

	name: Property[str] = Property("str")
	"``name`` key"

	next: Property[str] = Property("str")
	"``next`` key"

	object: Property[str | Message] = Property("object")
	"``object`` key"

	one_of: Property[dict[str, Any]] = Property("str")
	"``oneOf`` key"

	origin: Property[str | Message] = Property("object")
	"``origin`` key"

	outbox: Property[str] = Property("str")
	"``outbox`` key"

	owner: Property[str] = Property("str")
	"``owner`` key"

	part_of: Property[str] = Property("str")
	"``partOf`` key"

	preferred_username: Property[str] = Property("str")
	"``preferredUsername`` key"

	preview: Property[str | Message] = Property("object")
	"``preview`` key"

	previous: Property[str] = Property("str")
	"``previous`` key"

	public_key: Property[str | Message] = Property("object")
	"``publicKey`` key"

	public_key_pem: Property[str] = Property("str")
	"``publicKeyPem`` key"

	published: Property[MessageDate] = Property("date")
	"``published`` key"

	radius: Property[int] = Property("int")
	"``radius`` key"

	rel: Property[str] = Property("str")
	"``rel`` key"

	relationship: Property[str | Message] = Property("object")
	"``relationship`` key"

	replies: Property[str | Message] = Property("object")
	"``replies`` key"

	result: Property[str | Message] = Property("object")
	"``result`` key"

	start_index: Property[int] = Property("int")
	"``startIndex`` key"

	start_time: Property[MessageDate] = Property("date")
	"``startTime`` key"

	summary: Property[str] = Property("str")
	"``summary`` key"

	tag: Property[dict[str, Any]] = Property("object")
	"``tag`` key"

	target: Property[str | Message] = Property("object")
	"``target`` key"

	to: Property[list[str]] = Property("list")
	"``to`` key"

	total_items: Property[int] = Property("int")
	"``totalItems`` key"

	units: Property[str] = Property("str")
	"``units`` key"

	updated: Property[MessageDate] = Property("date")
	"``updated`` key"

	url: Property[str] = Property("str")
	"``url`` key"

	value: Property[str] = Property("str")
	"``value`` key"

	width: Property[int] = Property("int")
	"``width`` key"


	def __getitem__(self, key: str) -> Any:
		return dict.__getitem__(self, Property.name_to_camel_case(key))


	def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN001
		dict_key = Property.name_to_camel_case(key)
		key = Property.name_to_snake_case(key)

		if key == "attachment":
			value = [Attachment(item) for item in value] if value else []

		else:
			try:
				prop = getattr(Message, key)
				vtype = TYPES[prop.type_name]

				if isinstance(value, datetime) and not isinstance(value, MessageDate):
					value = MessageDate.parse(value)

				elif vtype == TYPES["object"] and isinstance(value, str):
					pass

				else:
					vtype = vtype[0] if isinstance(vtype, tuple) else vtype

					if not isinstance(value, vtype):
						value = CONVERTERS[vtype][0](value)

			except (KeyError, AttributeError):
				pass

		dict.__setitem__(self, dict_key, value)


	def __delitem__(self, key: str) -> None:
		dict.__delitem__(self, Property.name_to_camel_case(key))


	@classmethod
	def new(cls,
			obj_type: ObjectType | str,
			data: dict[str, Any],
			context: list[Any] | None = None) -> Self:
		"""
			Create a new ActivityPub object

			:param obj_type: Type of object to create
			:param data: Key/value pairs to include in the message
			:param context: List of JSON-LD context items
			:raises InvalidKeyError: When an invalid key has been specified
		"""

		if not context:
			context = []

		elif not isinstance(context, (list, tuple, set)):
			raise TypeError("Object context must be a list, tuple, or set")

		if "https://www.w3.org/ns/activitystreams" not in context:
			context.insert(0, "https://www.w3.org/ns/activitystreams")

		message = cls({"@context": context})
		message.type = ObjectType.parse(obj_type)

		for key, value in (data or {}).items():
			if key in {"@context", "type"}:
				raise InvalidKeyError(key)

			message[key] = value

		return message


	@classmethod
	def new_image(cls, url: str, mimetype: str | None = None) -> Self:
		"""
			Create a new ``Image`` object. If a mimetype is not provided, it will be guessed based
			on the filename in the url.

			:param url: Location of the image
			:param mimetype: Mimetype to use
			:raises ValueError: When a mimetype is not provided and cannot be determined
		"""

		if not mimetype:
			if not (mimetype := guess_type(urlparse(url).path)[0]):
				raise ValueError(f"Cannot determine mimetype of url: {url}")

		data = cls()
		data.type = ObjectType.IMAGE
		data.media_type = mimetype
		data.url = url
		return data


	# general properties
	@property
	def actor_id(self) -> str:
		"Get the url of the actor associated with the message"

		if "actor" not in self:
			raise AttributeError("Message does not have an 'actor' key")

		if isinstance(self["actor"], str):
			return self["actor"]

		try:
			return self["actor"]["id"]

		except KeyError:
			raise AttributeError("Message does not have an 'actor' key") from None


	@property
	def domain(self) -> str:
		"Get the domain of the object origin"
		return urlparse(self["id"]).hostname


	@property
	def object_id(self) -> str:
		"Get the ``id`` field of a linked object if it exists"

		if "object" not in self:
			raise AttributeError("Message does not have an 'object' key")

		if isinstance(self["object"], str):
			return self["object"]

		try:
			return self["object"]["id"]

		except KeyError:
			raise AttributeError("Message does not have an 'object' key") from None


	@property
	def object_domain(self) -> str:
		"Get the domain of the linked object if it exists"

		if (domain := urlparse(self.object_id).hostname) is None:
			raise ValueError("Could not get domain")

		return domain


	def add_field(self, key: str, value: str) -> None:
		"""
			Add a profile field

			:param key: Name of the field
			:param value: Value to associate with the name
		"""

		if "attachment" not in self:
			self.attachment = []

		self.attachment.append(Attachment.new_field(key, value))


	def add_image(self, key: str, url: str) -> None:
		"""
			Add an ``Image`` object at the specified key

			:param key: Key name to attach the ``Image`` object to
			:param url: Location of the image
		"""
		self[key] = type(self).new_image(url)


	def del_field(self, key: str) -> None:
		"""
			Delete a profile field

			:param key: Name of the field
		"""
		self.attachment.remove(self.get_field(key))


	def get_field(self, key: str) -> dict[str, str]:
		"""
			Get a field dict with the specified name

			:param key: Name of the field
		"""
		for field in self.get("attachment", []):
			if field["type"] == "PropertyValue" and field["name"] == key:
				return field

		raise KeyError(key)


	def get_fields(self) -> dict[str, str]:
		"Get all profile fields as key/value pairs"
		data = {}

		for field in self.get("attachment", []):
			if field["type"] == "PropertyValue":
				data[field["name"]] = field["value"]

		return data


	# Actor stuff
	@classmethod
	def new_actor(cls,
				actor_type: ObjectType,
				handle: str,
				actor: str,
				pubkey: str,
				inbox: str | None = None,
				outbox: str | None = None,
				shared_inbox: str | None = None,
				fields: dict[str, str] | None = None,
				avatar: str | None = None,
				header: str | None = None,
				**kwargs: Any) -> Self:
		"""
			Create a new actor object

			:param actor_type: Type of actor to create
			:param handle: Username of the actor
			:param actor: URL to where this object will be hosted
			:param pubkey: PEM of the public key associated with the actor
			:param inbox: URL to the actor's inbox
			:param outbox: URL to the actor's outbox,
			:param shared_inbox: URL to the inbox shared amongst all users of the instance
			:param fields: key/value string pairs to display on the actor's profile page
			:param avatar: URL to an image to be used as the actor's profile picture
			:param header: URL to an image to be used as the actor's header image
			:param kwargs: Extra object values to set
			:raises ValueError: When a non-actor type is provided
		"""

		if (actor_type := ObjectType.parse(actor_type)) not in ObjectType.Actor:
			raise ValueError(f"Invalid Actor type: {actor_type.value}")

		parsed_url = urlparse(actor)
		proto = parsed_url.scheme
		domain = parsed_url.netloc

		data = cls.new(
			actor_type,
			data = {
				"id": actor,
				"preferred_username": handle,
				"inbox": inbox or f"{actor}/inbox",
				"outbox": outbox or f"{actor}/outbox",
				"attachment": [],
				**kwargs,
				"endpoints": {
					"sharedInbox": shared_inbox or f"{proto}://{domain}/inbox"
				},
				"public_key": {
					"id": f"{actor}#main-key",
					"owner": actor,
					"publicKeyPem": pubkey
				}
			},
			context = [
				{
					"toot": "http://joinmastodon.org/ns#",
					"publicKeyBase64": "toot:publicKeyBase64",
				}
			]
		)

		if fields:
			data["@context"][1].update({
				"schema": "http://schema.org#",
				"PropertyValue": "schema:PropertyValue",
				"value": "schema:value"
			})

			for key, value in fields.items():
				data.add_field(key, value)

		else:
			del data.attachment

		if avatar:
			data.add_image("icon", avatar)

		if header:
			data.add_image("image", header)

		return data


	@property
	def username(self) -> str:
		"Get the actor's username (alias of :attr:`Message.preferred_username`)"
		return self["preferredUsername"]


	@property
	def keyid(self) -> str:
		"Get the ID of the actor's public key"
		return self["publicKey"]["id"]


	@property
	def pubkey(self) -> str:
		"Get the actor's PEM encoded public key"
		return self["publicKey"]["publicKeyPem"]


	@property
	def shared_inbox(self) -> str:
		"Get the instance's shared inbox"
		return self["endpoints"]["sharedInbox"]


	@cached_property
	def signer(self) -> Signer:
		"Create :class:`Signer` object for the actor"
		return Signer.new_from_actor(self)


	@property
	def handle(self) -> str:
		"Get the full username that includes the domain"
		return f"{self.username}@{self.domain}"


	def handle_value_dump(self, value: Any) -> Any:
		try:
			return CONVERTERS[type(value)][1](value)

		except KeyError:
			pass

		return JsonBase.handle_value_dump(self, value)


class Attachment(JsonBase):
	"Represents an object in the ``attachment`` list"

	@classmethod
	def new_field(cls: type[Attachment], key: str, value: str) -> Attachment:
		"""
			Create a new attachment meant for storing a key/value pair on an actor

			:param key: Name of the field
			:param value: Value to store with the field
		"""
		return cls({
			"type": "PropertyValue",
			"name": key,
			"value": value
		})
