class InvalidKeyError(KeyError):
	"Raise when an invalid key is attempting to be added via the data parameter in Message.new"

	@property
	def key(self) -> str:
		"Name of the invalid key"

		return self.args[0]


	def __str__(self) -> str:
		return f"Invalid message key '{self.args[0]}'"


class SignatureFailureError(Exception):
	"Raise when a signature could not be verified for any reason"
