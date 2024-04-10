"""
The HEAObject project implements classes representing all the data managed by HEA microservices that are maintained by
RISR. It also provides base classes for third parties to use in creating their own microservices.

Generally speaking, there is a one-to-one correspondence between module and microservice. Each module's docstring, and
the docstrings for the classes contained within, describe any special requirements for microservices that use those
classes. For HEA microservice authors, it is important to understand those requirements so that your microservices
function properly. For example, the heaobject.folder module describes requirements for microservices that implement
management of folders.

Class in this package have the following conventions for object attributes:
* Private attributes' names are prefixed with a double underscore.
* Protected attributes' names are prefixed with a single underscore. "Protected" is defined as accessible only to
the class in which it's defined and subclasses. Python does not enforce protected access, but uses of protected
attributes outside of subclasses may break even in patch releases.
"""
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
