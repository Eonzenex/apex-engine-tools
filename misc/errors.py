"""
Apex Engine tool errors
"""


# imports
from typing import Union, List


# class
class ApexEngineError(Exception):
    def __init__(self, message: str = "An Apex Engine tool error has occurred"):
        self.prefix: str = ">"
        self.message = message
        super().__init__(self.message)


# XML errors
class UnsupportedXMLTag(ApexEngineError):
    def __init__(self, unsupported_tag: str, supported_tags: Union[str, List], file_path: str,
                 message: str = f"Unsupported XML root tag"):
        self.unsupported_tag: str = unsupported_tag
        self.supported_tags: Union[str, List] = supported_tags
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        if isinstance(self.supported_tags, list):
            supported_tags: str = ", ".join(self.supported_tags)
        else:
            supported_tags: str = self.supported_tags
        return f"{self.prefix} {self.message} - '{self.unsupported_tag}' vs '{supported_tags}' ('{self.file_path}')"


class MissingInvalidXMLVersion(ApexEngineError):
    def __init__(self, xml_version: str, supported_versions: Union[str, List], file_path: str,
                 message: str = f"Unsupported XML root tag"):
        self.xml_version: str = xml_version
        self.supported_versions: Union[str, List] = supported_versions
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        if isinstance(self.supported_versions, list):
            supported_versions: str = ", ".join(self.supported_versions)
        else:
            supported_versions: str = self.supported_versions
        return f"{self.prefix} {self.message} - '{self.xml_version}' vs '{supported_versions}' ('{self.file_path}')"


class UnsupportedXMLVersion(ApexEngineError):
    def __init__(self, unsupported_version: str, supported_versions: Union[str, List], file_path: str,
                 message: str = f"Missing or invalid XML version"):
        self.unsupported_version: str = unsupported_version
        self.supported_versions: Union[str, List] = supported_versions
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        if isinstance(self.supported_versions, list):
            supported_versions: str = ", ".join(self.supported_versions)
        else:
            supported_versions: str = self.supported_versions
        return f"{self.prefix} {self.message} - '{self.unsupported_version}' vs '{supported_versions}' ('{self.file_path}')"


class MalformedXMLDoc(ApexEngineError):
    def __init__(self, filename: str, file_path: str, message: str = "Malformed XML document"):
        self.filename: str = filename
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.prefix} {self.message} - '{self.filename}' ('{self.file_path}')"


# IO errors
class FileDoesNotExist(ApexEngineError):
    def __init__(self, file_path: str, message: str = "Path does not exist"):
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.prefix} {self.message} - '{self.file_path}'"


class ExtensionTooShort(ApexEngineError):
    def __init__(self, ext: str, file_path: str, message: str = "File extension too short"):
        self.ext: str = ext
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.prefix} {self.message} - '{self.ext}' ('{self.file_path}')"


class IncorrectFileSize(ApexEngineError):
    def __init__(self, wrong_size: int, correct_size: int, file_path: str, message: str = f"Incorrect file size"):
        self.wrong_size: int = wrong_size
        self.correct_size: int = correct_size
        self.file_path: str = file_path
        self.message: str = message
        super().__init__(self.message)
    
    def __str__(self):
        return f"{self.prefix} {self.message} - '{self.wrong_size}' vs '{self.correct_size}' ('{self.file_path}')"
















