"""
Desktop and member objects that compose the HEA registry.
"""

from . import root
import yarl
import copy
from typing import Optional, List, Mapping, Union, Sequence
from .volume import DEFAULT_FILE_SYSTEM
from heaobject.volume import MongoDBFileSystem
from heaobject.data import DataObject
import uritemplate
from uritemplate.orderedset import OrderedSet


class Resource(root.AbstractMemberObject):
    """
    Metadata describing a REST API resource served by a HEA microservice.
    Resource objects each have a corresponding Collection desktop object that
    provides a convenient way to retrieve objects managed by the resource, or
    you can use the resource's get_resource_url() method to get a URL for
    working with desktop objects served by the resource.

    The resource metadata allows identifying the REST resource that serves a
    particular type of desktop object. Other metadata include a display name
    for the type of object served by the resource, the users who can create new
    desktop objects with the resource, the default shares for desktop objects
    created using the resource, and the users who can access this resource's
    collection object.
    """

    def __init__(self, resource_type_name: Optional[str] = None,
                 base_path: Optional[str] = None,
                 file_system_name: str = DEFAULT_FILE_SYSTEM,
                 file_system_type: str = MongoDBFileSystem.get_type_name(),
                 resource_collection_type_display_name: str | None = None):
        """
        Constructor, with the option to set the resource's properties.

        :param resource_type_name: the type name of HEAObject that is served by
        this resource.
        :param base_path: the path to be appended to the base URL or external
        base URL of the component when constructing a resource URL. See
        Component.get_resource_url(). The base path must not begin with a /.
        """
        super().__init__()
        if resource_type_name is not None and not root.is_heaobject_type(resource_type_name):
            raise ValueError(f'resource_type_name {resource_type_name} not a type of HEAObject')
        self.__resource_type_name: Optional[str] = str(resource_type_name) if resource_type_name is not None else None
        self.__base_path: Optional[str] = str(base_path) if base_path is not None else None
        self.__file_system_name: str = str(file_system_name) if file_system_name is not None else DEFAULT_FILE_SYSTEM
        self.__file_system_type: str = str(file_system_type) if file_system_type is not None else MongoDBFileSystem.get_type_name()
        self.__resource_collection_type_display_name = str(resource_collection_type_display_name) if resource_collection_type_display_name is not None else None
        self.__creator_users: set[str] = set([])
        self.__collection_accessor_users: set[str] = set([])
        self.__default_shares: list[root.Share] = []

    @property
    def base_path(self) -> Optional[str]:
        """
        The path to be appended to the base URL or external base URL of the
        component when constructing a resource URL. See
        Component.get_resource_url(). The base path must not begin with a /
        unless the component's base URL is None.
        The base path may be a URI template. If so, it must support the
        following standard template keys:
            volume_id: the HEA Object's volume id
            id: the HEA object's unique id.
        """
        return self.__base_path

    @base_path.setter
    def base_path(self, base_path: Optional[str]) -> None:
        if base_path is not None:
            u = yarl.URL(base_path)
            if not u.is_absolute() and base_path.startswith('/'):
                raise ValueError (f'relative base_path {base_path} cannot start with /')
        self.__base_path = str(base_path) if base_path is not None else None

    @property
    def resource_type_name(self) -> Optional[str]:
        """
        The type name of HEAObject that is served by this resource.
        """
        return self.__resource_type_name

    @resource_type_name.setter
    def resource_type_name(self, type_name: str):
        if not root.is_heaobject_type(type_name):
            raise ValueError(f'type_name {type_name} not a type of HEAObject')
        self.__resource_type_name = str(type_name)

    @property
    def resource_collection_type_display_name(self) -> str:
        """A display name for collections of this resource type. Defaults to the value of the resource_type_name attribute."""
        return self.__resource_collection_type_display_name if self.__resource_collection_type_display_name is not None else self.resource_type_name

    @resource_collection_type_display_name.setter
    def resource_collection_type_display_name(self, resource_collection_type_display_name: str):
        self.__resource_collection_type_display_name = str(resource_collection_type_display_name) if resource_collection_type_display_name is not None else None

    @property
    def file_system_name(self) -> str:
        """
        Optional file system name to which this resource applies. A value of None is equivalent to the default file
        system (see the heaobject.volume module).
        """
        return self.__file_system_name

    @file_system_name.setter
    def file_system_name(self, file_system_name: str | None) -> None:
        self.__file_system_name = str(file_system_name) if file_system_name is not None else DEFAULT_FILE_SYSTEM

    @property
    def file_system_type(self) -> str:
        """
        Optional file system type to which this resource applies. A value of None is equivalent to the default file
        system (see the heaobject.volume module).
        """
        return self.__file_system_type

    @file_system_type.setter
    def file_system_type(self, file_system_type: str | None) -> None:
        self.__file_system_type = str(file_system_type) if file_system_type is not None else MongoDBFileSystem.get_type_name()

    @property
    def creator_users(self) -> list[str]:
        """
        Users who can create desktop objects managed by this resource. An empty list means no one can create new
        desktop objects managed by this resource. Getting the creator users will return a de-duplicated list.
        """
        return list(self.__creator_users)

    @creator_users.setter
    def creator_users(self, creator_users: list[str]):
        if creator_users is None:
            raise ValueError('creator_users cannot be None')
        if not all(isinstance(r, str) for r in creator_users):
            raise TypeError('creator_users must contain all user strings')
        self.__creator_users = set(creator_users)

    def add_creator_user(self, creator_user: str):
        """
        Adds the provided creator user to the creator users list.

        :param creator_user: the creator user.
        """
        self.__creator_users.add(str(creator_user))

    def remove_creator_user(self, creator_user: str):
        """
        Removes the provided creator user from the creator users list.

        :param creator_user: the creator user.
        :raises ValueError: if the user is not present.
        """
        self.__creator_users.remove(creator_user)

    def is_creator_user(self, sub: str) -> bool:
        """
        Returns whether the user is in the creator user list.

        :param sub: the user (required).
        :return: True or False.
        """
        return sub in self.__creator_users

    @property
    def collection_accessor_users(self) -> list[str]:
        """
        Users who can access desktop objects managed by this resource via a Collection. An empty list means no one can
        access these objects via a Collection. Getting the users will return a de-duplicated list.
        """
        return list(self.__collection_accessor_users)

    @collection_accessor_users.setter
    def collection_accessor_users(self, collection_accessor_users: list[str]):
        if collection_accessor_users is None:
            raise ValueError('collection_accessor_users cannot be None')
        if not all(isinstance(r, str) for r in collection_accessor_users):
            raise TypeError('collection_accessor_users must contain all user strings')
        self.__collection_accessor_users = set(collection_accessor_users)

    def add_collection_accessor_user(self, collection_accessor_user: str):
        """
        Adds the provided user to the collection accessor users list.

        :param collection_accessor_user: the user.
        """
        self.__collection_accessor_users.add(str(collection_accessor_user))

    def remove_collection_accessor_user(self, collection_accessor_user: str):
        """
        Removes the provided user from the collection accessor users list.

        :param collection_accessor_user: the user.
        :raises ValueError: if the user is not present.
        """
        self.__collection_accessor_users.remove(collection_accessor_user)

    def is_collection_accessor_user(self, sub: str) -> bool:
        """
        Returns whether the user is in the collection accessor user list.

        :param sub: the user (required).
        :return: True or False.
        """
        return sub in self.__collection_accessor_users

    @property
    def default_shares(self) -> list[root.Share]:
        """
        Default permissions for desktop objects managed by this resource.
        """
        return copy.deepcopy(self.__default_shares)

    @default_shares.setter
    def default_shares(self, shares: list[root.Share]):
        if shares is None:
            raise ValueError('shares cannot be None')
        if not all(isinstance(r, root.Share) for r in shares):
            raise TypeError('shares must contain all Share objects')
        self.__default_shares = list(copy.deepcopy(r) for r in shares)

    def add_default_share(self, share: root.Share) -> None:
        """
        Adds a Share to the default shares for desktop objects managed by this resource.

        :param value: a Share object.
        """
        if not isinstance(share, root.Share):
            raise TypeError('value must be a Share')
        self.__default_shares.append(copy.deepcopy(share))

    def remove_default_share(self, share: root.Share) -> None:
        """
        Removes a Share from the default shares for desktop objects managed by this resource.

        :param value: a Share object.
        :raises ValueError if the share is not present.
        """
        if not isinstance(share, root.Share):
            raise TypeError('value must be a Share')
        self.__default_shares.remove(share)


class Component(root.AbstractDesktopObject):
    """
    Metadata about a HEA microservice. The component's name must be its
    distribution package name. Components have one or more resources, which are
    REST API resources that provide access to desktop objects stored on a
    file system. Resources each host a collection of desktop objects of a
    distinct type.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__base_url: str | None = None
        self.__external_base_url: str | None = None
        self.__resources: list[Resource] = []

    @property
    def base_url(self) -> str | None:
        """
        The base URL of the service for HEA services to call each other. The
        property's setter accepts a string or a yarl URL. In the latter case, it
        converts the URL to a string. In resolving a resource URL with the
        get_resource_url() method, any path part of this property will be
        replaced by the resource's base path.
        """
        return self.__base_url

    @base_url.setter
    def base_url(self, value: str | None) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise TypeError('value must be a str')
            self.__base_url = str(value)
        else:
            self.__base_url = None

    @property
    def external_base_url(self) -> str | None:
        """
        The base URL of the service for HEA services to call each other. The
        property's setter accepts a string or a yarl URL. In the latter case, it
        converts the URL to a string. In resolving a resource URL with the
        get_external_resource_url() method, any path part of this property will
        be replaced by the resource's base path.
        """
        return self.__external_base_url

    @external_base_url.setter
    def external_base_url(self, value: str | None) -> None:
        if value is not None:
            if not isinstance(value, str):
                raise TypeError('value must be a str')
            self.__external_base_url = str(value)
        else:
            self.__external_base_url = None

    @property
    def resources(self) -> List[Resource]:
        """
        The information that is served by this component. The property's setter
        accepts any iterable and converts it to a list.
        """
        return copy.deepcopy(self.__resources)

    @resources.setter
    def resources(self, value: List[Resource]) -> None:
        if value is None:
            raise ValueError('value cannot be None')
        if not all(isinstance(r, Resource) for r in value):
            raise TypeError('value must contain all Resource objects')
        self.__resources = list(copy.deepcopy(r) for r in value)

    def add_resource(self, value: Resource) -> None:
        """
        Adds a REST resource to the list of resources that are served by this component.
        :param value: a Resource object.
        """
        if not isinstance(value, Resource):
            raise TypeError('value must be a Resource')
        self.__resources.append(copy.deepcopy(value))

    def remove_resource(self, value: Resource) -> None:
        """
        Removes a REST resource from the list of resources that are served by this component. Ignores None values.
        :param value: a Resource object.
        """
        if not isinstance(value, Resource):
            raise TypeError('value must be a Resource')
        self.__resources.remove(value)

    def get_resource(self, type_name: str, file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM) -> Resource | None:
        """
        Returns the resource with the given type.

        :param type_name: a HEA object type or type name.
        :param file_system_name: the unique name of a file system (or volume.DEFAULT_FILE_SYSTEM, or None, which
        is the same as specifying volume.DEFAULT_FILE_SYSTEM)
        :return: a Resource, or None if this service does not serve resources of the given type.
        :raises ValueError: if type_name is not a valid HEA object type.
        """
        if not root.is_heaobject_type(type_name):
            raise ValueError('type_name not a type of HEAObject')

        if file_system_name is None:
            file_system_name_ = DEFAULT_FILE_SYSTEM
        else:
            file_system_name_ = str(file_system_name)

        for resource in self.__resources:
            if type_name == resource.resource_type_name and file_system_name_ == resource.file_system_name:
                return resource
        return None

    def get_resource_url(self, type_name: str, file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM,
                         parameters: Optional[dict[str, Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]]] = None,
                         **kwargs: Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]) -> str | None:
        """
        Returns the base URL of resources of the given type. It constructs the
        URL by combining the base_url of the component with the base path
        provided in the Resource object corresponding to this type.

        :param type_name: a HEA object type or type name.
        :param file_system_name: the unique name of a file system (or volume.DEFAULT_FILE_SYSTEM, or None, which
        is the same as specifying volume.DEFAULT_FILE_SYSTEM)
        :param parameters: an optional dictionary of parameters for expanding the resource's base path.
        :param kwargs: alternative way of specifying parameters.
        :return: a URL string, or None if this service does not serve resources of the given type.
        :raises ValueError: if type_name is not a valid HEA object type.
        """
        return self.__get_resource_url(self.base_url, type_name,
                                       file_system_name, parameters, **kwargs)

    def get_external_resource_url(self, type_name: str, file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM,
                         parameters: Optional[dict[str, Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]]] = None,
                         **kwargs: Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]) -> str | None:
        """
        Returns the external base URL of resources of the given type. It
        constructs the URL by combining the external_base_url of the component
        with the base path provided in the Resource object corresponding to
        this type.

        :param type_name: a HEA object type or type name.
        :param file_system_name: the unique name of a file system (or
        DEFAULT_FILE_SYSTEM, or None, which is the same as specifying
        DEFAULT_FILE_SYSTEM)
        :param parameters: an optional dictionary of parameters for expanding
        the resource's base path.
        :param kwargs: alternative way of specifying parameters.
        :return: a URL string, or None if this service does not serve resources
        of the given type.
        :raises ValueError: if type_name is not a valid HEA object type.
        """
        return self.__get_resource_url(self.external_base_url, type_name,
                                       file_system_name, parameters, **kwargs)

    def __get_resource_url(self, base_url: str | None, type_name: str,
                           file_system_name: Optional[str] = DEFAULT_FILE_SYSTEM,
                         parameters: Optional[dict[str, Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]]] = None,
                         **kwargs: Union[Sequence[Union[int, float, complex, str]], Mapping[str, Union[int, float, complex, str]], tuple[str, Union[int, float, complex, str]], int, float, complex, str]):
        """
        Constructs a REST resource URL from the given base URL and a
        base path from one of the component's Resource objects. The base path
        may contain URI template-style parameters.

        :param base_url: the base URL (required). If None, just the base path
        is used to construct a relative URL.
        :param type_name: the type name of the resource to use (required).
        :param file_system_name: the file system name of the resource to use.
        If None or omitted, DEFAULT_FILE_SYSTEM is used.
        :param parameters: If the base path has any URI template-style
        parameters, they will be substituted with the values in this mapping.
        :param kwargs: additional parameters may be specified as keyword
        arguments.
        :return a URL string, or None if no resource matched the type_name and
        file_system_name arguments.
        """
        resource = self.get_resource(type_name, file_system_name)
        parameters_ = dict(parameters or [])
        parameters_.update(kwargs)
        if resource is None:
            return None
        else:
            vars_ = uritemplate.variables(resource.base_path) if resource.base_path is not None else OrderedSet()
            if vars_ > parameters_.keys():
                raise ValueError(f'Missing parameters: {", ".join(v for v in vars_ if v not in parameters_.keys())}')
            if base_url:
                return str(yarl.URL(base_url) / uritemplate.expand(resource.base_path, parameters_))
            else:
                return uritemplate.expand(resource.base_path, parameters_)

    @classmethod
    def get_type_display_name(cls) -> Optional[str]:
        return 'Registry Component'


class Property(root.AbstractDesktopObject):
    """
    System or user configuration as key-value pairs. Use the owner and shares
    attributes to control to which users a property applies.
    """
    def __init__(self):
        super().__init__()
        self.value = None


class Collection(DataObject):
    """
    A group of desktop objects of the same type.
    """
    def __init__(self) -> None:
        super().__init__()
        self.__url: str | None = None
        self.__collection_type_name: str | None = None
        self.__file_system_type: str = MongoDBFileSystem.get_type_name()
        self.__file_system_name: str = DEFAULT_FILE_SYSTEM

    @property
    def mime_type(self) -> str:
        return 'application/x.collection'

    @property
    def url(self) -> str | None:
        """The URL for retrieving the objects in the collection. If a relative
        URL, it may not be prefixed with a forward slash."""
        return self.__url

    @url.setter
    def url(self, url: str | None):
        if url is not None:
            u = yarl.URL(url)
            if not u.is_absolute() and url.startswith('/'):
                raise ValueError(f'relative url {url} cannot start with /')
        self.__url = str(url) if url is not None else None

    @property
    def collection_type_name(self) -> str | None:
        """The type name of the desktop objects in the collection."""
        return self.__collection_type_name

    @collection_type_name.setter
    def collection_type_name(self, collection_type_name: str | None):
        self.__collection_type_name = str(collection_type_name) if collection_type_name is not None else None

    @property
    def file_system_name(self) -> str:
        """
        Optional file system name to which this resource applies. A value of None is equivalent to the default file
        system (see the heaobject.volume module).
        """
        return self.__file_system_name

    @file_system_name.setter
    def file_system_name(self, file_system_name: str | None) -> None:
        self.__file_system_name = str(file_system_name) if file_system_name is not None else DEFAULT_FILE_SYSTEM

    @property
    def file_system_type(self) -> str:
        """
        Optional file system type to which this resource applies. A value of None is equivalent to the default file
        system (see the heaobject.volume module).
        """
        return self.__file_system_type

    @file_system_type.setter
    def file_system_type(self, file_system_type: str | None) -> None:
        self.__file_system_type = str(file_system_type) if file_system_type is not None else MongoDBFileSystem.get_type_name()

    def can_create(self, sub: str) -> bool:
        """
        Returns whether the user can create desktop objects in this collection.

        :param sub: the user (required).
        """
        return self.has_permissions(sub, root.DefaultPermissionGroup.CREATOR_PERMS)

    def can_access(self, sub: str) -> bool:
        """
        Returns whether the user can access objects in this collection. Objects in the collection may have their own
        permissions.

        :param sub: the user (required).
        """
        return self.has_permissions(sub, root.DefaultPermissionGroup.ACCESSOR_PERMS)
