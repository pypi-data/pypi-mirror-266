from importlib_metadata import metadata as _metadata


"""
Metadata of neurobeam installation.
"""


name = _metadata("neurobeam")["name"]
version = _metadata("neurobeam")["version"]
author = _metadata("neurobeam")["author"]
maintainer = _metadata("neurobeam")["maintainer"]
