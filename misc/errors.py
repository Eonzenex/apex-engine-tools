"""
Apex Engine tool errors
"""


# imports
from typing import Union, List


# class
class ApexError(Exception):
	def __init__(self, message: str = "An Apex Engine tool error has occurred"):
		self.message = message
		super().__init__(self.message)


class WrongFileType(ApexError):
	def __init__(self, four_cc: bytes, message: str = "The given file was not the correct file type"):
		self.four_cc = four_cc
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f"{self.message} ({self.four_cc})"


# XML errors
class UnsupportedXMLTag(ApexError):
	def __init__(self, unsupported_tag: str, supported_tags: Union[str, List], file_path: str,
	             message: str = f"Unsupported XML root tag"):
		self.unsupported_tag = unsupported_tag
		self.supported_tags = supported_tags
		self.file_path = file_path
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		supported_tags: str = self.supported_tags if isinstance(self.supported_tags, str) else ", ".join(self.supported_tags)
		return f"{self.message} - '{self.unsupported_tag}' vs '{supported_tags}' ('{self.file_path}')"


class MissingInvalidXMLVersion(ApexError):
	def __init__(self, xml_version: str, supported_versions: Union[str, List], file_path: str,
	             message: str = f"Unsupported XML root tag"):
		self.xml_version = xml_version
		self.supported_versions = supported_versions
		self.file_path = file_path
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		if isinstance(self.supported_versions, list):
			supported_versions: str = ", ".join(self.supported_versions)
		else:
			supported_versions: str = self.supported_versions
		return f"{self.message} - '{self.xml_version}' vs '{supported_versions}' ('{self.file_path}')"


class UnsupportedXMLVersion(ApexError):
	def __init__(self, unsupported_version: str, supported_versions: Union[str, List], file_path: str,
	             message: str = f"Missing or invalid XML version"):
		self.unsupported_version = unsupported_version
		self.supported_versions = supported_versions
		self.file_path = file_path
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		if isinstance(self.supported_versions, list):
			supported_versions: str = ", ".join(self.supported_versions)
		else:
			supported_versions: str = self.supported_versions
		return f"{self.message} - '{self.unsupported_version}' vs '{supported_versions}' ('{self.file_path}')"


# IO errors
class ExtensionTooShort(ApexError):
	def __init__(self, ext: str, file_path: str, message: str = "File extension too short"):
		self.ext = ext
		self.file_path = file_path
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f"{self.message} - '{self.ext}' ('{self.file_path}')"


class MalformedXMLDoc(ApexError):
	def __init__(self, filename: str, file_path: str, message: str = "Malformed XML document"):
		self.filename = filename
		self.file_path = file_path
		self.message = message
		super().__init__(self.message)
	
	def __str__(self):
		return f"{self.message} - '{self.filename}' ('{self.file_path}')"



















