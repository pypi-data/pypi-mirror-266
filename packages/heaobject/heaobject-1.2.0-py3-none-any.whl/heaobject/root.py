"""
A collection of classes and interfaces supporting the construction of data transfer objects for moving data between
HEA microservices as well as between a HEA microservice and a web browser or other client. The HEAObject is the root
interface for these data transfer objects, and AbstractHEAObject provides a root abstract implementation for them.
See HEAObject's docstring for details.
"""

import json
from datetime import date, time

from humanize import naturalsize

from .error import DeserializeException
from .util import parse_bool
from . import user
from enum import auto, Enum
from typing import Optional, List, Union, Any, Type, Callable, Dict, TypeVar, cast, Protocol
from collections.abc import Iterable, Iterator, Mapping, Sequence
import copy
import inspect
import abc
import logging
import importlib
from copy import deepcopy
from dateutil import parser as dateparser

from .user import ALL_USERS

PRIMITIVE_ATTRIBUTE_TYPES = (int, float, str, bool, Enum, type(None), date, time)

Primitive = Optional[Union[int, float, str, bool, Enum, date, time]]
MemberObjectDict = Dict[str, Union[Primitive, List[Primitive]]]
HEAObjectDictValueTypeVar = TypeVar('HEAObjectDictValueTypeVar', List[MemberObjectDict], MemberObjectDict,
                                    List[Primitive], Primitive)
HEAObjectDictValue = Optional[Union[List[MemberObjectDict], MemberObjectDict, List[Primitive], Primitive]]
DesktopObjectDict = Dict[str, HEAObjectDictValueTypeVar]
HEAObjectDict = Union[DesktopObjectDict, MemberObjectDict]

try:
    inspect.getmembers_static
    def _get_type_attributes(cls):
        return set(dir(cls))
    def _get_attributes(self, type_attrs):
        return set(m[0] for m in inspect.getmembers_static(self, lambda x: not inspect.isroutine(x)) \
                     if not m[0].startswith('_') and (inspect.isdatadescriptor(m[1]) or m[0] not in type_attrs))
except AttributeError:
    def _get_type_attributes(cls):
        return set(inspect.getmembers(cls, lambda x: not inspect.isroutine(x)))
    def _get_attributes(self, type_attrs):
        return set(m[0] for m in inspect.getmembers(self, lambda x: not inspect.isroutine(x)) \
                     if not m[0].startswith('_') and m not in type_attrs)


def json_dumps(o: Any) -> str:
    """
    Serialize any python object to a JSON document. Date and datetime properties are serialized as ISO timestamps, and
    enums are serialized to their names.

    :param o: the object to serialize.
    :return: a JSON document.
    """
    return json.dumps(o, default=json_encode)


def json_loads(o: str | bytes) -> Any:
    """
    Deserialize a HEAObject, a date, or a JSON-serializable object supported by default by json.dumps.

    :param o: the JSON string or bytes object.
    :return: a JSON document.
    """
    return json.loads(o)


class OrderedEnum(Enum):
    """An enum ordered by value."""

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

class EnumAutoName(Enum):
    """
    Subclass of Enum in which auto() returns the name as a string.
    """

    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self) -> str:
        return self.name

class EnumWithAttrs(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class Permission(EnumAutoName):
    """
    The standard permissions that apply to all HEA desktop objects.
    """
    CHECK_DYNAMIC = auto()  # No access to the object unless dynamic_permission() returns a non-None value.
    VIEWER = auto()  # Read-only access to the object and its content.
    EDITOR = auto()  # May update the object and its content.
    SHARER = auto()  # May share the object and its content.
    COOWNER = auto()  # May do anything with the object, like the owner of it.
    CREATOR = auto()  # May create an object; assigned to a container.
    DELETER = auto()  # May delete the object and its content.


class PermissionGroup(Protocol):
    """
    A duck typing protocol for permission groups, which are objects with a perms attribute that returns a list of
    Permission objects. Any object with such a perms attribute may be passed into DesktopObject.has_permissions().
    """
    @property
    def perms(self) -> list[Permission]:
        """The permissions in this group."""
        pass


class DefaultPermissionGroup(EnumWithAttrs):
    """
    Enum that maps heaobject's root.Permission enum values to typical operations, suitable for passing into a
    DesktopObject's has_permissions() method. To support desktop objects that implement the dynamic_permission()
    method, each group has a special permission, Permission.CHECK_DYNAMIC, which causes the dynamic_permission() method
    to be invoked by has_permissions() if the desktop object has a share for the user with the Permission.CHECK_DYNAMIC
    permission.

    The Permission enum values composing each group can be queried by each PermissionGroup enum value's perms
    attribute.

    In order to access an object, the user must have at least one of the permissions in the
    ACCESSOR_PERMS permission group (VIEWER, COOWNER, or EDITOR) for the object.

    In order to create an object, the user must have at least one of the permissions in the
    CREATOR_PERMS permission group (CREATOR, COOWNER) for the container in which the object will be created.

    In order to update an object, the user must have at least one of the permissions in the
    UPDATER_PERMS permission group (EDITOR, COOWNER) for the object.

    In order to delete an object, the user must have at least one of the permissions in the
    DELETER_PERMS permission group (DELETER, COOWNER) for the object.
    """

    def __init__(self, perms):
        self.__perms = perms

    @property
    def perms(self) -> list[Permission]:
        """
        The permissions that are part of the group.
        """
        return self.__perms[:-1]

    @property
    def _perms_internal(self) -> list[Permission]:
        """
        A representation of the group that is internal to HEA and NOT part of the public API.
        """
        return list(self.__perms)

    ACCESSOR_PERMS = [Permission.VIEWER, Permission.COOWNER, Permission.EDITOR, Permission.CHECK_DYNAMIC]
    UPDATER_PERMS = [Permission.EDITOR, Permission.COOWNER, Permission.CHECK_DYNAMIC]
    CREATOR_PERMS = [Permission.CREATOR, Permission.COOWNER]
    DELETER_PERMS = [Permission.DELETER, Permission.COOWNER, Permission.CHECK_DYNAMIC]

class HEAObject(abc.ABC):
    """
    Interface for all HEA objects. HEA objects are data transfer objects for moving data between HEA microservices as
    well as between a HEA microservice and a web browser or other client. HEA objects have no behavior except support
    for storage, retrieval, serialization, and deserialization. The AbstractHEAObject class provides default
    implementations for setting and getting attributes, as well as default implementations of behaviors.

    HEA objects have built-in facilities for extracting the object's data attributes into a dictionary or JSON string
    (the get_attributes(), to_dict() and to_json() methods). These methods are used by other parts of HEA to
    build REST API responses. These three methods support monkey-patched data attributes. However, from_dict() and
    from_json() will only set data attributes that already exist in the object.

    There are two sub-types of HEA objects: desktop objects (DesktopObject) and owned
    objects (MemberObject). The AbstractDesktopObject and AbstractMemberObject classes provide default implementations
    for setting and getting attributes, and default implementations of behaviors. There may be additional sub-types in
    the future.

    Desktop objects represent objects that appear on the HEA desktop. Desktop objects have permissions, timestamps for
    when the object was created and modified, versions, and more. One or more HEA microservices provide CRUD (create,
    read, update, and delete) operations on each desktop object type. Additional HEA microservices may implement actions
    that consume or produce specific desktop object types.

    Member objects cannot appear by themselves on the HEA desktop. Instead, they have a part-of relationship with a
    desktop object, and their lifecycle is managed by the desktop object. Example member objects represent permissions
    and data sharing. While owned objects provide for their own storage, retrieval, serialization, and deserialization,
    these behaviors are always invoked by the desktop object of which they are a part. HEA objects may contain only one
    level of nested members.

    HEA objects must conform to several conventions to ease their use and reuse across the HEA desktop.
    All subclasses of HEAObject must have a zero-argument constructor. Attribute values may be strings, numbers, booleans,
    enums, or a HEA object; or a list of strings, numbers, booleans, enums, or HEA objects. Attributes of type enum
    must be implemented as a property with a setter that accepts both strings and the enum values, and will convert the
    strings to enum values.

    In general, HEA objects implement composition relationships by making the container a desktop object and the "owned"
    object a member object. Other association relationships are implemented by storing the id of the associated object
    rather than nesting it. By convention, the id attributes are named hea_object_class_name_id, where hea_object_class_name
    is the name of the class converted from camel case to underscores.

    Copies and deep copies using the copy module will copy all non-callable instance members of any subclass of HEAObject.

    Properties of a HEAObject must never raise an error because another property is unset.

    Objects are expected to perform defensive copying when setting and getting attributes so that altering an
    attribute's value from outside of the object cannot affect the object's internal state.

    Objects are expected to allow setting primitive type sequence attributes to a single object of the allowed type, in
    which case the attribute is stored as a singleton sequence containing that object. Unfortunately, there is no way
    to specify type hints for properties in which the getter type may be different from the setter type. The from_dict()
    method relies on this behavior.

    In addition, HEA objects should include type annotations throughout.

    It is imperative that users gain access to desktop objects by calling an appropriate HEA microservice as themselves, which
    will filter any nested member objects that are returned according to their permissions.
    """

    def __new__(cls, *args, **kwargs):
        return make_abstract(HEAObject, cls)

    @abc.abstractmethod
    def to_dict(self) -> HEAObjectDict:
        """
        Returns a dict containing this object's data attributes as defined by the get_attributes() method.

        :return: a dict of attribute names to attribute values.
        """
        pass

    @abc.abstractmethod
    def to_json(self, dumps: Callable[[HEAObjectDict], str] = json_dumps) -> str:
        """
        Returns a JSON-formatted string containing this object's data attributes as defined by the get_attributes()
        method. Passes the json_encode function as the default parameter.

        :param dumps: any callable that accepts a HEAObject and returns a string.
        :return: a string.
        """
        pass

    @abc.abstractmethod
    def from_json(self, jsn: str, loads: Callable[[str | bytes | bytearray], HEAObjectDict] = json_loads) -> None:
        """
        Populates the object's data attributes as defined by the get_attributes() method with the property values in
        the provided JSON. The JSON must have a type property that matches this object's type. Properties that
        correspond to read-only data attributes or non-existent data attributes are ignored. This object's attributes
        are set in order of appearance in the JSON.

        :param jsn: a JSON string.
        :param loads: any callable that accepts str and returns dict with parsed JSON (json_loads() by default).
        :raises DeserializeException: if any of the JSON object's values are wrong, or the provided JSON
        document is not a valid JSON document.
        """
        pass

    @abc.abstractmethod
    def from_dict(self, d: HEAObjectDict) -> None:
        """
        Populates the object's writeable data attributes as defined by the get_attributes() method with the property
        values in the given dict. The dict must have a type key whose value matches this object's type. Dict entries
        that correspond to read-only data attributes or non-existent data attributes are ignored. This object's
        attributes are set in order of appearance in the dictionary.

        :param d: a mapping.
        :raises DeserializeException: if any of the mapping's values are wrong.
        """
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def type(self) -> str:
        """
        The string representation of this object's type.

        :return: a string.
        """
        pass

    @abc.abstractmethod
    def get_attributes(self) -> Iterator[str]:
        """
        Returns an iterator containing the object's data attributes, including monkey-patched attributes.

        :return: an iterator of attribute names.
        """
        pass

    @abc.abstractmethod
    def get_all_attributes(self) -> Iterator[str]:
        """
        Returns an iterator containing the object's data attributes, including monkey-patched attributes.

        :return: an iterator of attribute names.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_prompt(cls, field_name: Optional[str]) -> Optional[str]:
        pass

    @classmethod
    @abc.abstractmethod
    def is_displayed(cls, field_name: Optional[str]) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def get_type_name(cls) -> str:
        """
        Returns a string representation of a HEAObject type.

        :return: a type string.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_type_display_name(cls) -> Optional[str]:
        """
        Returns a display name for the HEAObject type, or None if there is no display name for this type.

        :return: the display name string
        """
        pass


class MemberObject(HEAObject, abc.ABC):
    """
    Interface for HEA objects that have a part-of relationship with a desktop objects and whose lifecycle is
    managed by the desktop object. Owned objects have the same permissions as the owning desktop object. As a result,
    they can be accessed by anyone who can access the desktop object, and they can be modified by anyone who can modify
    the desktop object.
    """
    pass


class PermissionAssignment(MemberObject, abc.ABC):
    """
    Interface for permission assignments for desktop objects. Desktop objects are owned by the user who created them.
    After creating an object, the object's owner can share the object with other users with the desired set of
    permissions. Optionally, users can invite another users to access the object with the desired set of permissions,
    and the user will receive access upon accepting the invite. Permission assignment objects are owned by a desktop
    object. As a result, they can be accessed by anyone who can access the desktop object, and they can be
    modified by anyone who can modify the desktop object.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def user(self) -> str:
        """
        The user whose permissions will be impacted.
        """
        pass

    @user.setter  # type: ignore
    @abc.abstractmethod
    def user(self, user: str) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def permissions(self) -> List[Permission]:
        """
        The list of assigned permissions.
        """
        pass

    @permissions.setter  # type: ignore
    @abc.abstractmethod
    def permissions(self, perms: List[Permission]):
        pass

    @abc.abstractmethod
    def add_permission(self, perm: Permission):
        """
        Adds a permission the share.

        :param perm: the Permission.
        """
        pass

    @abc.abstractmethod
    def remove_permission(self, perm: Permission):
        """
        Removes a permission from the share.

        :param perm: the Permission.
        :raises ValueError: if the perm value is not present.
        """
        pass


class Invite(PermissionAssignment, abc.ABC):
    """
    Interface for invites to access a desktop object. Invite objects are owned by a desktop object, and as a result they
    do not have permissions of their own.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def accepted(self) -> bool:
        """
        Whether the user has accepted the invite.
        """
        pass

    @accepted.setter  # type: ignore
    @abc.abstractmethod
    def accepted(self, accepted: bool) -> bool:
        pass


class Share(PermissionAssignment, abc.ABC):
    """
    Interface for representing the permissions of users to whom a desktop object has been shared. Share objects are
    owned by a desktop object, and as a result they do not have permissions of their own.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def invite(self) -> Invite | None:
        """
        The invite, if any.
        """
        pass

    @invite.setter  # type: ignore
    @abc.abstractmethod
    def invite(self, invite: Invite | None) -> None:
        pass


class DesktopObject(HEAObject, abc.ABC):
    """
    Interface for objects that can appear on the HEA desktop. Desktop objects have permissions, with those permissions
    represented by owned objects implementing the MemberObject interface. Other attributes may also employ owned
    objects. One or more HEA microservices provide CRUD (create, read, update, and delete) operations on each desktop
    object type. Additional HEA microservices may implement actions that use specific desktop object types.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.

    Desktop objects may employ three authorization mechanisms:

    1) User-based: if the user is the object's owner, then the user can do anything with the object.
    2) Shares-based: if the owner has shared the object with a user, then the user can use the object according to the
    values of the heaobject.root.Permission enum.
    3) Dynamic permissions: Implemented using the dynamic_permission function, it uses the object's field values to
    determine the user's permissions. It will only be invoked if the user has some level of shares-based permission. In
    the absence of the object actually having been shared with a user, a Share object can be added to the shares list
    with user system|all and the minimum permission level (CHECK_DYNAMIC). In the future, it may be possible to
    traverse relationships between objects via their *_id fields so that related objects' field values might be used to
    determine permissions.

    The level of permissions granted will be the greatest of the 3 approaches. Being an object's owner trumps
    everything. The shares-based and dynamic permissions-based approaches both return heaobject.root.Permission objects,
    and in the event of conflicting Permissions, the most permissive permissions will prevail.

    Desktop objects may have a class variable, associations, with type Dict[property, str]. For properties ending in
    _id or _ids that represent an association relationship with another desktop object type, it defines the type name
    of the desktop object being referred to. The associations variable is intended to have many purposes. In the future,
    implementations of the dynamic_permission() method might use these annotations to traverse an association
    relationship to another desktop object as part of permissions checking.
    """

    @property  # type: ignore
    @abc.abstractmethod
    def id(self) -> Optional[str]:
        """
        The object's resource unique identifier. It must be unique among all
        objects of the same type. The id is expected to be generated by the
        database in which the objects are stored, thus prior to storing the
        object the id is expected to be None. In a client-server application,
        the id is generated on the server side and provided back to the client.

        When an application needs to store updates of an object in a database,
        the application should first arrange to store the original version of
        the object and get its generated id back from the database for use in
        subsequent updates. However, in asynchronous operations this may not be
        possible, such as when an object and updates to it are sent over a
        message queue. In a message queue, the sender may generate updates to
        an object before the receiver finishes processing the original object
        version.

        In this case, the application must generate and maintain its own object
        id, and the object class should provide a different property for the
        application to store it. The database will still generate its id and
        store it in the id field, thus the object will have two unique ids, a
        database-generated id and an application-generated id. Typical methods
        for generating ids on the application side such as UUIDs are highly
        reliable but may be somewhat less reliable over the long term than
        database-generated ids. Thus, applications should use database-
        generated ids whenever feasible and treat application-generated ids as
        temporary. Applications should link the database- and application-
        generated ids. In a client-server application, this must happen server-
        side so that the server can appropriately store objects received from
        the client with only an application-generated id. However, the client
        could maintain its own linkage if necessary.

        In client-server applications with multiple server processes such as
        microservices, application-generated ids should be based upon unique
        identifiers of the source of the object, which depending on the
        architecture might include IP address or other form of host identifier,
        so that objects generated by separate server processes cannot clash.
        Consider security concerns if the generated ids may become visible to
        users.

        For some HEAObject classes, it may be natural for its unique id to be
        a string with characters that cannot be incorporated into a URL's path,
        such as /. The same is true for HEAObject's name attribute. For this
        situation, we recommend encoding the value using URL-safe base 64
        encoding as described in IETF RFC 4648 section 5, and adding a custom
        attribute to the class for storing the actual id/name value. The id,
        name, and custom attributes can be synchronized such that setting the
        custom attribute automatically generates an encoded value that can be
        accessed via the id and/or name attributes.
        """
        pass

    @id.setter  # type: ignore
    @abc.abstractmethod
    def id(self, id_: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def source(self) -> Optional[str]:
        """
        A string indicating the object's source system
        """
        pass

    @source.setter  # type: ignore
    @abc.abstractmethod
    def source(self, source: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def source_detail(self) -> Optional[str]:
        """
        Additional details about the object's source.
        """
        pass

    @source_detail.setter  # type: ignore
    @abc.abstractmethod
    def source_detail(self, source: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def name(self) -> Optional[str]:
        """
        This object's name. The name must be unique across all objects of the same type, sometimes in combination with
        the object's owner. For some HEAObject classes, it may be natural for its name to be a string with characters
        that cannot be incorporated into a URL's path, such as /. The same is true for HEAObject's id attribute. For
        this situation, we recommend encoding the value using URL-safe base 64 encoding as described in IETF RFC 4648
        section 5, and adding a custom attribute to the class for storing the actual id/name value. The id, name, and
        custom attributes can be synchronized such that setting the custom attribute automatically generates an encoded
        value that can be accessed via the id and/or name attributes, and setting the id or name attribute
        automatically generates a decoded value that is returned by the custom attribute.
        """
        pass

    @name.setter  # type: ignore
    @abc.abstractmethod
    def name(self, name: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def display_name(self) -> str:
        """
        The object's display name. The default value is the object's name. If the name is None, then a sensible
        default value is returned.
        """
        pass

    @display_name.setter  # type: ignore
    @abc.abstractmethod
    def display_name(self, display_name: str) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def description(self) -> Optional[str]:
        """
        The object's description.
        """
        pass

    @description.setter  # type: ignore
    @abc.abstractmethod
    def description(self, description: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def owner(self) -> str:
        """
        The username of the object's owner. Cannot be None. Defaults to heaobject.user.NONE_USER.
        """
        pass

    @owner.setter  # type: ignore
    @abc.abstractmethod
    def owner(self, owner: str) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def created(self) -> Optional[date]:
        """
        The date or datetime at which this object was initially stored, as a
        date object. Setting this property with an ISO 8601 string will also
        work -- the ISO string will be parsed automatically as a datetime
        object.
        """
        pass

    @created.setter  # type: ignore
    @abc.abstractmethod
    def created(self, value: Optional[date]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def modified(self) -> Optional[date]:
        """
        The date or datetime at which the latest update to this object was
        stored. Setting this property with an ISO 8601 string will also work --
        the ISO string will be parsed automatically as a datetime object.
        """
        pass

    @modified.setter  # type: ignore
    @abc.abstractmethod
    def modified(self, value: Optional[date]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def derived_by(self) -> Optional[str]:
        """
        The id of the mechanism by which this object was derived, if any.
        """
        pass

    @derived_by.setter  # type: ignore
    @abc.abstractmethod
    def derived_by(self, derived_by: Optional[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def derived_from(self) -> List[str]:
        """
        A list of the ids of the HEAObjects from which this object was derived. If None, will be set to the default
        value (the empty list).
        """
        pass

    @derived_from.setter  # type: ignore
    @abc.abstractmethod
    def derived_from(self, derived_from: List[str]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def invites(self) -> List[Invite]:
        """
        A list of Invite objects representing the users who have been invited to access this object. If None, will be
        set to the default value (the empty list).
        """
        pass

    @invites.setter  # type: ignore
    @abc.abstractmethod
    def invites(self, invites: List[Invite]) -> None:
        pass

    @property  # type: ignore
    @abc.abstractmethod
    def shares(self) -> List[Share]:
        """
        A list of Share objects representing the users with whom this object has been shared. If None, will be set to
        the default value (the empty list).
        """
        pass

    @shares.setter  # type: ignore
    @abc.abstractmethod
    def shares(self, shares: List[Share]) -> None:
        pass

    @abc.abstractmethod
    def dynamic_permission(self, sub: str) -> List[Permission]:
        """
        Uses the object's attributes to determine what level of permissions a user may have to this object.

        :param sub: the user id to check.
        :return: a list of Permission enum values, or an empty list to signify no permissions.
        """
        pass

    @abc.abstractmethod
    def get_permissions(self, sub: str) -> List[Permission]:
        """
        Gets the subject's permissions for this object. The result includes any permissions computed dynamically if
        the subject has the CHECK_DYNAMIC permission for the object, omitting CHECK_DYNAMIC in the returned permission
        list.

        :param sub: the user (required).
        :return: a list of Permission enum values, or an empty list to signify no permissions.
        """
        pass

    @abc.abstractmethod
    def has_permissions(self, sub: str, perms: Sequence[Permission] | PermissionGroup) -> bool:
        """
        Returns whether the given subject has any of the provided permissions for this object. If the subject is the
        owner of the object, then the user has all permissions. Otherwise, this method checks the object's shares and
        dynamic permissions.

        :param sub: the user (required).
        :param perms: the permissions to check (required), which may be passed as an iterable of Permission objects or
        an object adhering to the PermissionGroup protocol.
        :return: True or False.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_subclasses(cls) -> Iterator[Type['DesktopObject']]:
        """
        Returns an iterator of subclasses of this class that have previously been loaded into the python interpreter.
        :return: an iterator of DesktopObject types.
        """
        pass


def make_abstract(cls: Type[Any], cls_arg: Type[Any], *args, **kwargs):
    if cls_arg is cls:
        raise TypeError(f"Can't instantiate abstract class {cls.__name__}")
    return super(cls, cls_arg).__new__(cls_arg, *args, **kwargs)


class AbstractHEAObject(HEAObject, abc.ABC):
    """
    Abstract base class for all HEA objects. HEA objects are data transfer objects for moving data between HEA
    microservices as well as between a HEA microservice and a web browser or other client. HEA objects have no behavior
    except support for storage, retrieval, serialization, and deserialization. The AbstractHEAObject class provides
    default implementations for setting and getting attributes, as well as default implementations of behaviors.

    There are two sub-types of HEA objects: desktop objects (DesktopObject) and owned
    objects (MemberObject). The AbstractDesktopObject and AbstractMemberObject classes provide default implementations
    for setting and getting attributes, and default implementations of behaviors. There may be additional sub-types in
    the future.

    Desktop objects represent objects that appear on the HEA desktop. Desktop objects have permissions, timestamps for
    when the object was created and modified, versions, and more. One or more HEA microservices provide CRUD (create,
    read, update, and delete) operations on each desktop object type. Additional HEA microservices may implement actions
    that consume or produce specific desktop object types.

    Owned objects cannot appear by themselves on the HEA desktop. Instead, they have a part-of relationship with a
    desktop object, and their lifecycle is managed by the desktop object. Example owned objects represent permissions
    and data sharing. While owned objects provide for their own storage, retrieval, serialization, and deserialization,
    these behaviors are always invoked by the desktop object of which they are a part.

    HEA object implementations must conform to several conventions to ease their use and reuse across the HEA desktop.
    All subclasses of HEAObject must have a zero-argument constructor. All non-callable instance members must be
    included in the to_dict() and json_dumps() methods. Copies and deep copies using the copy module will copy all
    non-callable instance members of any subclass of HEAObject. Override __copy__ and __deepcopy__ to change that
    behavior. In addition, HEA objects should include type annotations for all properties and callables.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.
    """

    _type_attributes: set | None = None
    _attributes: set | None = None

    def __new__(cls, *args, **kwargs):
        return make_abstract(AbstractHEAObject, cls, *args, **kwargs)

    def __init__(self) -> None:
        super().__init__()
        self.__attributes = set()

    def to_dict(self) -> HEAObjectDict:
        def nested(obj):
            match obj:
                case HEAObject():
                    return obj.to_dict()
                case list():
                    return [nested(o) for o in obj]
                case Enum():
                    return obj.name
                case _:
                    return obj

        return {a: nested(getattr(self, a)) for a in self.get_attributes()}

    def to_json(self, dumps: Callable[[HEAObjectDict], str] = json_dumps) -> str:
        return dumps(self.to_dict())

    def from_json(self, jsn: str, loads: Callable[[str | bytes | bytearray], HEAObjectDict] = json_loads) -> None:
        try:
            self.from_dict(loads(jsn))
        except json.JSONDecodeError as e:
            raise DeserializeException from e

    def from_dict(self, d: HEAObjectDict) -> None:
        try:
            for k, v in d.items():
                if k in self.get_attributes():
                    if isinstance(v, list):
                        lst: List[Union[HEAObject, Primitive]] = []
                        for e in v:
                            if isinstance(e, dict):
                                if 'type' not in e:
                                    raise ValueError(
                                        'type property is required in nested dicts but is missing from {}'.format(e))
                                e_type = e['type']
                                obj = type_for_name(e_type)()
                                obj.from_dict(e)
                                lst.append(obj)
                            else:
                                lst.append(e)
                        self.__setattr_known_and_writeable(k, lst)
                    elif isinstance(v, dict):
                        if 'type' not in v:
                            raise ValueError(
                                'type property is required in nested dicts but is missing from {}'.format(v))
                        v_type = v['type']
                        obj = type_for_name(v_type)()
                        obj.from_dict(v)
                        self.__setattr_known_and_writeable(k, obj)
                    elif k != 'type':
                        self.__setattr_known_and_writeable(k, v)
                    else:
                        if v != self.type:
                            raise ValueError(
                                f"type property does not match object type: object type is {self.type} but the dict's type property has value {v}")
        except (ValueError, TypeError) as e:
            raise DeserializeException from e

    @property
    def type(self) -> str:
        return self.get_type_name()

    def get_attributes(self) -> Iterator[str]:
        type_ = type(self)
        if type_._attributes is None:
            type_._attributes = _get_attributes(self, type_.__get_type_attributes())
        self.__attributes.update(type_._attributes)
        return iter(self.__attributes)

    @classmethod
    def __get_type_attributes(cls):
        if cls._type_attributes is None:
            cls._type_attributes = _get_type_attributes(cls)
        return cls._type_attributes

    def get_all_attributes(self) -> Iterator[str]:
        return self.get_attributes()

    def __setattr__(self, attr, value):
        if not attr.startswith('_'):
            self.__attributes.add(attr)
        super().__setattr__(attr, value)

    @classmethod
    def get_prompt(cls, field_name: Optional[str]) -> Optional[str]:
        return field_name

    @classmethod
    def is_displayed(cls, field_name: Optional[str]) -> bool:
        return True if field_name != 'id' else False

    @classmethod
    def get_type_name(cls) -> str:
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def get_type_display_name(cls) -> Optional[str]:
        """
        Returns a display name for the HEAObject type, or None if there is no display name for this type. The default
        implementation returns None. A concrete type implementation should override this method to return a display
        name for the type.

        :return: the display name string
        """
        return cls.__name__

    def __setattr_known_and_writeable(self, name: str, value: Any) -> None:
        """
        Sets any of this object's attributes, ignoring attempts to set read-only attributes or to monkey patch the object with additional attributes.

        :param name: the name of the attribute.
        :param value: the attribute's value.
        """
        try:
            setattr(self, name, value)
        except AttributeError:
            logger = logging.getLogger(__name__)
            if hasattr(self, name):
                logger.debug(
                    'Tried setting attribute %s.%s=%s and got an error, most likely because the attribute is read-only. HEA will ignore this attribute.',
                    self, name, value)
            else:
                logger.debug('Attempted to set an unexpected attribute %s.%s=%s. HEA will ignore this attribute.',
                             self,
                             name, value)


    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        attrs = set(self.get_all_attributes()).union(other.get_all_attributes())
        return all(getattr(self, a, None) == getattr(other, a, None) for a in attrs)

    def __repr__(self) -> str:
        return 'heaobject.root.from_dict(' + repr(self.to_dict()) + ')'

    def __copy__(self):
        clz = type(self)
        result = clz()
        for a in self.get_attributes():
            try:
                setattr(result, a, getattr(self, a))
            except AttributeError:
                pass  # Skip read-only attributes
        return result

    def __deepcopy__(self, memo):
        result = type(self)()
        for a in self.get_attributes():
            try:
                setattr(result, a, copy.deepcopy(getattr(self, a), memo))
            except AttributeError:
                pass  # Skip read-only attributes
        return result


class AbstractMemberObject(AbstractHEAObject, MemberObject, abc.ABC):
    """
    Abstract base class for all classes that are owned by a desktop class. Owned classes have a part-of relationship
    with a desktop class, and their lifecycle is managed by the desktop class. The desktop class and this class have a
    composition relationship in UML. Owned objects have the same permissions as the owning desktop object. As a result,
    they can be accessed by anyone who can access the desktop object, and they can be modified by anyone who can modify
    the desktop object.
    """
    def __new__(cls, *args, **kwargs):
        return make_abstract(AbstractMemberObject, cls, *args, **kwargs)


class VersionedDesktopObject(DesktopObject, abc.ABC):
    """
    Interface for desktop objects that can be versioned.
    """
    @property  # type: ignore
    @abc.abstractmethod
    def version(self) -> Optional[str]:
        """
        The current version of this object. It will be added to the versions property, if it is not already there.
        A None version is only permitted if the versions property's value is the empty list.
        """
        pass

    @version.setter
    @abc.abstractmethod
    def version(self, version: str | None):
        pass


class AbstractPermissionAssignment(AbstractMemberObject, PermissionAssignment, abc.ABC):
    """
    Abstract base class for permissions-related classes. Desktop objects are owned by the user who created them.
    After creating an object, the object's owner can share the object with other users with the desired set of
    permissions. Optionally, users can invite another users to access the object with the desired set of permissions,
    and the user will receive access upon accepting the invite. Permission assignment objects are owned by a desktop
    object. As a result, they can be accessed by anyone who can access the desktop object, and they can be
    modified by anyone who can modify the desktop object.
    """

    def __new__(cls, *args, **kwargs):
        return make_abstract(AbstractPermissionAssignment, cls, *args, **kwargs)


    def __init__(self) -> None:
        super().__init__()
        self.__user = user.NONE_USER
        self.__permissions: List[Permission] = []

    @property
    def user(self) -> str:
        return self.__user

    @user.setter
    def user(self, user: str) -> None:
        self.__user = str(user)

    @property
    def permissions(self) -> List[Permission]:
        """
        List of granted permissions. Any strings in the list will be parsed into Permission objects. Cannot be None.
        Attempting to set this property to None will result in setting it to the empty list.
        """
        return list(self.__permissions)

    @permissions.setter
    def permissions(self, perms: List[Permission]):
        if perms is None:
            self.__permissions = []
        else:
            perms_ = [p if isinstance(p, Permission) else Permission[p] for p in perms]
            self.__permissions = perms_

    def add_permission(self, perm: Permission):
        if not isinstance(perm, Permission):
            raise TypeError('perm must be a Permission')
        self.__permissions.append(perm)

    def remove_permission(self, perm: Permission):
        self.__permissions.remove(perm)

class InviteImpl(AbstractPermissionAssignment, Invite):
    """
    Implementation of an invite.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__accepted = False

    @property
    def accepted(self) -> bool:
        return self.__accepted

    @accepted.setter
    def accepted(self, accepted: bool) -> None:
        if accepted is None:
            self.__accepted = False
        elif isinstance(accepted, bool):
            self.__accepted = accepted
        else:
            self.__accepted = parse_bool(accepted)  # type: ignore


class ShareImpl(AbstractPermissionAssignment, Share):
    """
    Implementation of a share.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__invite: Invite | None = None

    @property
    def invite(self) -> Invite | None:
        return self.__invite

    @invite.setter
    def invite(self, invite: Invite | None) -> None:
        if invite is not None and not isinstance(invite, Invite):
            raise TypeError('invite not an Invite')
        self.__invite = copy.deepcopy(invite)


class Tag(AbstractMemberObject):
    """
    Tags are essentially key value pairs
    """

    def __init__(self) -> None:
        super().__init__()
        self.__key: str | None = None
        self.__value: str | None = None

    @property
    def key(self) -> str | None:
        return self.__key

    @key.setter
    def key(self, key: str | None) -> None:
        self.__key = str(key) if key is not None else key

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = str(value) if value is not None else value


class AbstractDesktopObject(AbstractHEAObject, DesktopObject, abc.ABC):
    """
    Abstract base class representing HEA desktop objects. Desktop objects have permissions, with those permissions
    represented by owned objects implementing the MemberObject interface. Other attributes may also employ owned
    objects.

    Desktop objects implement no capability to check the current user when getting and setting owned objects, and
    different users may only have access to a subset of its owned objects. Similarly, owned objects have no knowledge of
    permissions at all. It is imperative that users gain access to desktop objects by calling an appropriate HEA
    microservice as themselves, which will filter the owned objects that are returned according to their permissions.
    """

    def __new__(cls, *args, **kwargs):
        return make_abstract(AbstractDesktopObject, cls, *args, **kwargs)

    def __init__(self) -> None:
        super().__init__()
        self.__id: Optional[str] = None
        self.__source: Optional[str] = None
        self.__source_detail: Optional[str] = None
        self.__name: Optional[str] = None
        self.__display_name: str = self.__default_display_name()
        self.__description: Optional[str] = None
        self.__owner = user.NONE_USER
        self.__created: Optional[date] = None  # The date when the object was created
        self.__modified: Optional[date] = None  # The date when the object was last modified
        self.__invites: List[Invite] = []
        self.__shares: List[Share] = []
        self.__derived_by: str | None = None
        self.__derived_from: list[str] = []

    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, id_: Optional[str]) -> None:
        self.__id = str(id_) if id_ is not None else None

    @property
    def source(self) -> Optional[str]:
        return self.__source

    @source.setter
    def source(self, source: Optional[str]) -> None:
        self.__source = str(source) if source is not None else None

    @property
    def source_detail(self) -> Optional[str]:
        return self.__source_detail

    @source_detail.setter
    def source_detail(self, source_detail: Optional[str]) -> None:
        self.__source_detail = str(source_detail) if source_detail is not None else None

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, name: Optional[str]) -> None:
        self.__name = str(name) if name is not None else None

    @property
    def display_name(self) -> str:
        return self.__display_name

    @display_name.setter
    def display_name(self, display_name: str) -> None:
        if display_name is not None:
            self.__display_name = str(display_name)
        elif self.name is not None:
            self.__display_name = self.name
        else:
            self.__display_name = self.__default_display_name()

    @property
    def description(self) -> Optional[str]:
        return self.__description

    @description.setter
    def description(self, description: Optional[str]) -> None:
        self.__description = str(description) if description is not None else None

    @property
    def owner(self) -> str:
        return self.__owner

    @owner.setter
    def owner(self, owner: str) -> None:
        self.__owner = str(owner) if owner is not None else user.NONE_USER

    @property
    def created(self) -> date | None:
        return self.__created

    @created.setter
    def created(self, value: date | None) -> None:
        if value is None or isinstance(value, date):
            self.__created = value
        else:
            self.__created = dateparser.isoparse(value) # TODO Use datetime.fromisoformat after we switch to python 3.11.

    @property
    def modified(self) -> Optional[date]:
        return self.__modified

    @modified.setter
    def modified(self, value: date | None) -> None:
        if value is None or isinstance(value, date):
            self.__modified = value
        else:
            self.__modified = dateparser.isoparse(value) # TODO Use datetime.fromisoformat after we switch to python 3.11.

    @property
    def derived_by(self) -> Optional[str]:
        return self.__derived_by

    @derived_by.setter
    def derived_by(self, derived_by: Optional[str]) -> None:
        self.__derived_by = str(derived_by) if derived_by is not None else None

    @property
    def derived_from(self) -> list[str]:
        return list(self.__derived_from)

    @derived_from.setter
    def derived_from(self, derived_from: list[str]) -> None:
        if derived_from is None:
            self.__derived_from = []
        else:
            self.__derived_from = [str(i) for i in derived_from]

    @property
    def invites(self) -> List[Invite]:
        """
        A list of Invite objects representing the users who have been invited to access this object. Cannot be None.
        """
        return copy.deepcopy(self.__invites)

    @invites.setter
    def invites(self, invites: List[Invite]) -> None:
        if invites is None:
            self.__invites = []
        elif isinstance(invites, Invite):
            self.__invites = [copy.deepcopy(invites)]
        else:
            if not all(isinstance(s, Invite) for s in invites):
                raise KeyError('invites can only contain Invite objects')
            self.__invites = list(copy.deepcopy(invites))

    @property
    def shares(self) -> List[Share]:
        """
        A list of Share objects representing the users with whom this object has been shared.
        """
        return copy.deepcopy(self.__shares)

    @shares.setter
    def shares(self, shares: List[Share]) -> None:
        if shares is None:
            self.__shares = []
        elif isinstance(shares, Share):
            self.__shares = [copy.deepcopy(shares)]
        else:
            if not all(isinstance(s, Share) for s in shares):
                raise KeyError("shares can only contain Share objects")
            self.__shares = copy.deepcopy(shares)

    def add_share(self, share: Share):
        if not isinstance(share, Share):
            raise TypeError('share must be a Share')
        self.__shares.append(share)

    def remove_share(self, share: Share):
        self.__shares.remove(share)

    def dynamic_permission(self, sub: str) -> List[Permission]:
        """
        Default implementation that returns an empty list, signifying no permissions.

        :param sub: the user id.
        :return: an empty list.
        """
        return []

    def get_permissions(self, sub: str) -> List[Permission]:
        if sub is None:
            raise ValueError('sub cannot be None')

        if self.owner == sub:
            return list(p for p in Permission)

        result = set(perm for share in self.__shares for perm in share.permissions
                     if share.user == sub or share.user == ALL_USERS)
        if Permission.CHECK_DYNAMIC in result:
            result.update(self.dynamic_permission(sub))
        return list(r for r in result if r is not Permission.CHECK_DYNAMIC)

    def has_permissions(self, sub: str, perms: Sequence[Permission] | PermissionGroup) -> bool:
        if sub is None:
            raise ValueError('sub cannot be None')
        if perms is None:
            raise ValueError('perms cannot be None')

        user_perms = set(p for s in self.__shares if s.user == sub or s.user == ALL_USERS for p in s.permissions)

        if hasattr(perms, 'perms'):
            perms_ = cast(PermissionGroup, perms).perms
        else:
            perms_ = perms

        return self.owner == sub or \
               any(perm is not Permission.CHECK_DYNAMIC and perm in user_perms for perm in perms_) or \
               ((Permission.CHECK_DYNAMIC in user_perms) and any(perm in perms_ for perm in self.dynamic_permission(sub)))

    @classmethod
    def get_subclasses(cls) -> Iterator[Type['AbstractDesktopObject']]:
        for subclass in cls.__subclasses__():
            yield from subclass.get_subclasses()
            yield subclass

    def __default_display_name(self):
        return 'Untitled ' + self.get_type_display_name()

    def __str__(self) -> str:
        """
        Returns the object's display name.
        :return: the display name.
        """
        return self.display_name


class Version(AbstractDesktopObject):
    """
    Represents version metadata for an object. Versioned desktop objects (that
    extend the VersionedDesktopObject class) have a version attribute
    representing the object's current version, and they may implement an API
    for getting version metadata represented by instances of this class. If
    such an API is provided, it must return a Version metadata object whose id
    equals the value of the desktop object's version attribute. The API may
    also return additional Version objects representing older versions of the
    object.

    Microservices may implement subclasses of Version if their versions have
    extra attributes or their attributes need custom validation logic.
    """
    def __init__(self) -> None:
        super().__init__()
        self.__current = False
        self.__version_of_id: str | None = None

    @property
    def current(self) -> bool:
        """Whether this is the current version of the desktop object. The default value is False."""
        return self.__current

    @current.setter
    def current(self, current: bool):
        if current is None:
            self.__current = False
        elif isinstance(current, bool):
            self.__current = current
        else:
            self.__current = parse_bool(current)

    @property
    def version_of_id(self) -> str | None:
        return self.__version_of_id

    @version_of_id.setter
    def version_of_id(self, version_of_id: str | None):
        self.__version_of_id = str(version_of_id) if version_of_id is not None else None


class AbstractVersionedDesktopObject(AbstractDesktopObject, VersionedDesktopObject, abc.ABC):
    """
    Base class for versioned desktop objects.
    """

    def __new__(cls, *args, **kwargs):
        return make_abstract(AbstractVersionedDesktopObject, cls, *args, **kwargs)

    def __init__(self) -> None:
        super().__init__()
        self.__version: str | None = None

    @property
    def version(self) -> str | None:
        return self.__version

    @version.setter
    def version(self, version: str | None):
        self.__version = str(version) if version is not None else None


class Alias(abc.ABC):
    """
    Placeholder mixin for implementing aliases similar to those in MacOS and Windows.
    """
    pass


class View(abc.ABC):
    """
    View mixin. Views are desktop objects that are automatically managed alternative representations of some other
    desktop object. Acting on a view also acts on the other desktop object, and vice-versa. A desktop object can have
    multiple views served by different endpoints, all of which synchronize with the corresponding desktop object.
    Create a view class by extending both heaobject.root.DesktopObject (or a subclass) and this class. In addition to
    the attributes provided by this mixin, microservices are expected to populate a view's attributes from those of the
    desktop object for all attributes that overlap. Furthermore, submitting a view object to a PUT, POST, or DELETE
    endpoint must also update the corresponding desktop object. A client must be able to work with views and their
    corresponding desktop objects interchangeably, and synchronization between the two must be immediate such that a
    workflow must be able to submit a change to a view and subsequently request the corresponding desktop object,
    and the changes in the view must reflect in the desktop object.

    Views are different from MacOS or Windows aliases. While aliases can be modified and deleted without affecting
    the object that they point to, and changes to an object may or may not affect its aliases, changes to HEA views
    always change the corresponding desktop object and vice-versa. HEA defines an heaobject.root.Alias mixin as a
    placeholder for supporting desktop objects in the future that have similar properties to MacOS and Windows aliases.
    """

    @property
    def actual_object_type_name(self) -> str | None:
        """The actual object's type name."""
        try:
            return self.__actual_object_type_name
        except AttributeError:
            self.__actual_object_type_name: str | None = None
            return self.__actual_object_type_name

    @actual_object_type_name.setter
    def actual_object_type_name(self, actual_object_type_name: str | None) -> None:
        self.__actual_object_type_name = str(actual_object_type_name) if actual_object_type_name is not None else None

    @property
    def actual_object_id(self) -> str | None:
        """The actual object's id."""
        try:
            return self.__actual_object_id
        except AttributeError:
            self.__actual_object_id: str | None = None
            return self.__actual_object_id

    @actual_object_id.setter
    def actual_object_id(self, actual_object_id: str | None) -> None:
        self.__actual_object_id = str(actual_object_id) if actual_object_id is not None else None

    @property
    def actual_object_uri(self) -> str | None:
        """The actual object's URL, as a relative URL without a leading slash to an API gateway for accessing the
        object."""
        try:
            return self.__actual_object_uri
        except AttributeError:
            self.__actual_object_uri: str | None = None
            return self.__actual_object_uri

    @actual_object_uri.setter
    def actual_object_uri(self, actual_object_uri: str | None) -> None:
        self.__actual_object_uri = str(actual_object_uri) if actual_object_uri is not None else None


class AbstractAssociation(AbstractMemberObject):
    """
    Abstract base class for creating associations between desktop objects. Unlike most other classes in heaobject, this
    class overrides __eq__ and __hash__ so that objects of the same type and that have the same values for its
    attributes are equal.
    """
    def __init__(self):
        super().__init__()
        self.__actual_object_type_name: str | None = None
        self.__actual_object_id: str | None = None
        self.__name: str | None = None

    @property
    @abc.abstractmethod
    def allowed_actual_object_type_names(self) -> list[str]:
        """
        The permitted types for this association as a list of type names.
        """
        pass

    @property
    def actual_object_type_name(self) -> str | None:
        """The name of the type of the associated object."""
        return self.__actual_object_type_name

    @actual_object_type_name.setter
    def actual_object_type_name(self, actual_object_type_name: str | None):
        if actual_object_type_name is not None and actual_object_type_name not in self.allowed_actual_object_type_names:
            raise ValueError(f'{actual_object_type_name} not an allowed type')
        self.__actual_object_type_name = str(actual_object_type_name) if actual_object_type_name is not None else None

    @property
    def actual_object_id(self) -> str | None:
        """The id string of the associated object."""
        return self.__actual_object_id

    @actual_object_id.setter
    def actual_object_id(self, actual_object_id: str | None):
        self.__actual_object_id = str(actual_object_id) if actual_object_id is not None else None

    @property
    def name(self) -> str | None:
        """A name for the association, like hasA."""
        return self.__name

    @name.setter
    def name(self, name: str | None):
        self.__name = str(name) if name is not None else None

    def __eq__(self, other):
        """
        Overrides the default equality implementation. Objects of the same type and that have the same values for the
        actual_object_type_name, actual_object_id, and name attributes are equal.
        """
        if self is not type(other):
            return False
        if self.actual_object_type_name != other.actual_object_type_name:
            return False
        if self.actual_object_id != other.actual_object_id:
            return False
        if self.name != other.name:
            return False
        return True

    def __hash__(self):
        """
        Overrides the default hash code implementation. It computes the hash code from the actual_object_type_name,
        actual_object_id, and name attributes.
        """
        val = 17
        val += 37 * hash(self.actual_object_type_name)
        val += 37 * hash(self.actual_object_id)
        val += 37 * hash(self.name)
        return val


class HasSize:
    """
    Size mixin for use in desktop objects with content.
    """
    @property
    def size(self) -> Optional[int]:
        """Size of the item in bytes"""
        try:
            return self.__size
        except AttributeError:
            return None

    @size.setter
    def size(self, size: Optional[int]) -> None:
        """The size of the desktop object's content in bytes."""
        self.__size = int(size) if size is not None else None

    @property
    def human_readable_size(self) -> str | None:
        """The size of the desktop object's content in human readable form."""
        return naturalsize(self.size) if self.size is not None else None



HEAObjectTypeVar = TypeVar('HEAObjectTypeVar', bound=HEAObject)
DesktopObjectTypeVar = TypeVar('DesktopObjectTypeVar', bound=DesktopObject)
MemberObjectTypeVar = TypeVar('MemberObjectTypeVar', bound=MemberObject)


def json_encode(o: Any) -> Union[str, HEAObjectDict]:
    """
    Function to pass into the json.dumps default parameter that customizes encoding for HEAObjects, dates, and enums.

    :param o: the object to encode.
    :return: the object after encoding.
    :raise TypeError: if the object is neither a HEAObject nor a date.
    """
    match o:
        case HEAObject():
            return o.to_dict()
        case date():
            return o.isoformat()
        case Enum():
            return str(o)
        case _:
            raise TypeError(f'values {o} must be HEAObject, date, or a value type supported by json.dumps by default')


def is_primitive(obj: Any) -> bool:
    """
    Returns whether the argument is an instance of a HEA primitive type (int, float, str, bool, Enum, or NoneType).
    :return: True or False.
    """
    return isinstance(obj, PRIMITIVE_ATTRIBUTE_TYPES)


def is_primitive_list(obj: Any) -> bool:
    """
    Returns whether the argument is a list of HEA primitive types. Will return True if passed an empty list.
    :return: True or False.
    """
    return isinstance(obj, list) and all(is_primitive(elt) for elt in obj)


def is_member_object(obj: Any) -> bool:
    """
    Returns whether the argument is a MemberObject.
    :return: True or False.
    """
    return isinstance(obj, MemberObject)


def is_member_object_list(obj: Any) -> bool:
    """
    Returns whether the argument is an iterable of MemberObjects. Will return False if passed an empty list.
    :return: True or False.
    """
    return isinstance(obj, list) and len(obj) > 0 and all(isinstance(elt, MemberObject) for elt in obj)


def is_desktop_object_dict(obj: Any) -> bool:
    """
    Returns whether the argument is a desktop object dict, defined as a dict with a type key, and the type name is
    that of a subclass of DesktopObject.

    :param obj: any object.
    :return: True or False.
    """
    return isinstance(obj, dict) and 'type' in obj and issubclass(type_for_name(obj['type']), DesktopObject)


def is_heaobject_dict(obj: Any) -> bool:
    """
    Returns whether the argument is an HEAObject dict, defined as a dict with a type key.

    :param obj: any object.
    :return: True or False.
    """
    return isinstance(obj, dict) and 'type' in obj


def is_heaobject_dict_list(obj: Any) -> bool:
    """
    Returns whether the argument is a list of HEAObject dicts. Will return False if passed an empty list.

    :param obj: any object.
    :return: True or False.
    """
    return isinstance(obj, list) and len(obj) > 0 and all(is_heaobject_dict(elt) for elt in obj)


def type_for_name(name: str) -> Type[HEAObject]:
    """
    Returns the HEAObject type for the given string.

    :param name: a type string.
    :return: a HEAObject type.
    :raises TypeError: if the supplied name is not an HEAObject type.
    """
    return _type_for_name(name, HEAObject)


def is_heaobject_type(name: str) -> bool:
    """
    Returns whether the supplied string is the name of an HEAObject type.

    :param name: a string.
    :return: True if the string is the name of an HEAObject type, or False if not.
    """
    try:
        type_for_name(name)
        return True
    except TypeError:
        return False


def desktop_object_type_for_name(name: str) -> Type[DesktopObject]:
    """
    Returns the HEA desktop object type for the given string.

    :param name: a type string.
    :return: a HEAObject type.
    :raises TypeError: if the supplied name is not a desktop object type.
    """
    return _type_for_name(name, DesktopObject)


def is_desktop_object_type(name: str) -> bool:
    """
    Returns whether the supplied string is the name of an HEA desktop object type.

    :param name: a string.
    :return: True if the string is the name of an HEA desktop object type, or False if not.
    """
    try:
        desktop_object_type_for_name(name)
        return True
    except TypeError:
        return False


def from_dict(d: HEAObjectDict) -> HEAObject:
    """
    Creates a HEA object from the given dict.

    :param d: a dict. It must have, at minimum, a type key with the type name of the HEA object to create. It must
    additionally have key-value pairs for any mandatory attributes of the HEA object.
    :return: a HEAObject.
    :raises ValueError: if the input DesktopObjectDict is missing a type key.
    :raises TypeError: if the input DesktopObjectDict's type value is not a string.
    :raises DeserializeException: if the input DesktopObjectDict could not otherwise be read.
    """
    type_name = d.get('type', None)
    if not type_name:
        raise ValueError('type key is required')
    if not isinstance(type_name, str):
        raise TypeError(f'type is {type(type_name)} but must be a str')
    obj = type_for_name(type_name)()
    obj.from_dict(d)
    return obj


def from_json(o: str | bytes) -> HEAObject:
    """
    Creates a HEA object from the given JSON document.

    :param o: the JSON document. It must have, at minimum, a type propertu with the type name of the HEA object to
    create. It must additionally have properties for any mandatory attributes of the HEA object.
    :return: a HEAObject.
    :raises ValueError: if the input DesktopObjectDict is missing a type key.
    :raises TypeError: if the input DesktopObjectDict's type value is not a string.
    :raises heaobject.error.DeserializeException: if the input DesktopObjectDict could not otherwise be read.
    :raises json.decoder.JSONDecodeError: if the input is not valid JSON.
    """
    return from_dict(json_loads(o))


def desktop_object_from_dict(d: DesktopObjectDict) -> DesktopObject:
    """
    Creates a desktop object from the given dict.

    :param d: a dict. It must have, at minimum, a type key with the type name of the desktop object to create. It must
    additionally have key-value pairs for any mandatory attributes of the desktop object.
    :return: a desktop object.
    :raises ValueError: if the input DesktopObjectDict is missing a type key.
    :raises TypeError: if the input DesktopObjectDict's type value is not a string.
    :raises heaobject.error.DeserializeException: if the input DesktopObjectDict could not otherwise be read.
    """
    type_name = d.get('type', None)
    if not type_name:
        raise ValueError('type key is required')
    if not isinstance(type_name, str):
        raise TypeError(f'type is {type(type_name).__name__} but must be a str')
    obj = desktop_object_type_for_name(type_name)()
    obj.from_dict(d)
    return obj


def desktop_object_from_json(o: str | bytes) -> DesktopObject:
    """
    Creates a desktop object from the given JSON document.

    :param o: the JSON document. It must have, at minimum, a type propertu with the type name of the desktop object to
    create. It must additionally have properties for any mandatory attributes of the desktop object.
    :return: a DesktopObject.
    :raises ValueError: if the input DesktopObjectDict is missing a type key.
    :raises TypeError: if the input DesktopObjectDict's type value is not a string.
    :raises heaobject.error.DeserializeException: if the input DesktopObjectDict could not otherwise be read.
    :raises json.decoder.JSONDecodeError: if the input is not valid JSON.
    """
    return desktop_object_from_dict(json_loads(o))


def copy_heaobject_dict_with(d: HEAObjectDict, changes: Mapping[str, HEAObjectDictValue] | None) -> HEAObjectDict:
    """
    Shallow copies the given dictionary and updates it with the given changes.

    :param d: The HEA object dictionary that will be changed (required).
    :param changes: The changes being made, expressed as a mapping.
    :return: A shallow copy of the given dictionary with the given changes.
    """
    copied_dict = dict(d)
    copied_dict.update(changes or {})
    return copied_dict


def copy_heaobject_dict_with_deletions(d: HEAObjectDict, deletions: Iterable[str] | None) -> HEAObjectDict:
    """
    Shallow copies the given dictionary and updates it with the given deletions.

    :param d: The HEA object dictionary that will be changed (required).
    :param deletions: The deletions being made, as an iterable.
    :return: A shallow copy of the given dictionary with the given changes.
    """
    copied_dict = dict(d)
    for deletion in (deletions or []):
        if deletion in d:
            del d[deletion]
    return copied_dict


def deepcopy_heaobject_dict_with(d: HEAObjectDict, changes: Mapping[str, HEAObjectDictValue] | None) -> HEAObjectDict:
    """
    Deep copies the given dictionary and updates it with the given changes.

    :param d: The HEA object dictionary that will be changed (required).
    :param changes: The changes being made, expressed as a mapping.
    :return: A deep copy of the given dictionary with the given changes.
    """
    copied_dict = dict(deepcopy(d))
    copied_dict.update(changes or {})
    return copied_dict


def deepcopy_heaobject_dict_with_deletions(d: HEAObjectDict, deletions: Iterable[str] | None) -> HEAObjectDict:
    """
    Deep copies the given dictionary and updates it with the given deletions.

    :param d: The HEA object dictionary that will be changed (required).
    :param deletions: The deletions being made, as an iterable.
    :return: A deep copy of the given dictionary with the given changes.
    """
    copied_dict = deepcopy(d)
    for deletion in (deletions or []):
        if deletion in d:
            del d[deletion]
    return copied_dict


def _type_for_name(name: str, type_: type):
    """
    Returns the object type for the given string.

    :param name: a type string.
    :return: a type.
    :raises TypeError: if the supplied name is not an object type.
    """
    try:
        mod_str, cls_str = name.rsplit('.', 1)
        try:
            result = getattr(importlib.import_module(mod_str), cls_str)
        except (NameError, AttributeError):
            raise TypeError(f'Type doesn\'t exist: {name}')
        if not issubclass(result, type_):
            raise TypeError(f'Name must be the name of a {type_} type, but was {name}')
        return result
    except ValueError:
        raise TypeError(f'{name} does not look like a module path')
