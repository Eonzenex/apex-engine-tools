"""
Apex Engine tool errors
"""


# class
class ApexError(Exception):
	def __init__(self, message: str = "An Apex Engine tool error has occurred"):
		self.message = message
		super().__init__(self.message)


class WrongFileType(ApexError):
	def __init__(self, magic: bytes, message: str = "The given file was not the correct file type"):
		self.magic = magic
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f"{self.message} ({self.magic})"
