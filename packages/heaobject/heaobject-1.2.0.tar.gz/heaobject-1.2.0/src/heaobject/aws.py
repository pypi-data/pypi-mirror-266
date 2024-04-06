"""
Utility classes and functions for working with AWS.
"""
import abc
from heaobject import root
from typing import Optional
import re


class S3StorageClass(root.EnumWithAttrs):
    """
    The S3 storage classes. The list of storage classes is documented at
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2, and
    each storage class is explained in detail at
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html.
    """
    def __init__(self, display_name: str):
        self.__display_name = display_name

    @property
    def display_name(self) -> str:
        return self.__display_name

    STANDARD = 'Standard'
    DEEP_ARCHIVE = 'Glacier Deep Archive'
    GLACIER = 'Glacier Flexible Retrieval'
    GLACIER_IR = 'Glacier Instant Retrieval'
    REDUCED_REDUNDANCY = 'Reduced Redundancy'
    ONEZONE_IA = 'One Zone-IA'
    STANDARD_IA = 'Standard-IA'
    INTELLIGENT_TIERING = 'Intelligent Tiering'
    OUTPOSTS = 'Outposts'



def s3_uri(bucket: str | None, key: str | None = None) -> str | None:
    """
    Creates and returns a S3 URI from the given bucket and key.

    :param bucket: a bucket name (optional).
    :param key: a key (optional).
    :return: None if the bucket is None, else a S3 URI string.
    """
    if not bucket:
        return None
    return f"s3://{bucket}/{key if key is not None else ''}"


S3_URI_PATTERN = re.compile(r's3://(?P<bucket>[^/]+?)/(?P<key>.+)')
S3_URI_BUCKET_PATTERN = re.compile(r's3://(?P<bucket>[^/]+?)/')


class S3StorageClassMixin:
    """
    Mixin for adding a storage class property to a desktop object.
    """

    @property
    def storage_class(self) -> S3StorageClass:
        """The AWS S3 storage class of this file."""
        try:
            return self.__storage_class
        except AttributeError:
            self.__storage_class = None
            return self.__storage_class

    @storage_class.setter
    def storage_class(self, storage_class: S3StorageClass):
        if storage_class is None:
            self.__storage_class = None
        elif isinstance(storage_class, S3StorageClass):
            self.__storage_class = storage_class
        else:
            try:
                self.__storage_class = S3StorageClass[str(storage_class)]
            except KeyError:
                raise ValueError(f'Invalid storage class {storage_class}')

    def set_storage_class_from_str(self, storage_class: Optional[str]):
        """
        Sets the storage class property to the storage class corresponding to the provided string.
        """
        if storage_class is None:
            self.__storage_class = None
        else:
            try:
                self.__storage_class = S3StorageClass[str(storage_class)]
            except KeyError:
                raise ValueError(f'Invalid storage class {storage_class}')


class S3Version(root.Version, S3StorageClassMixin):
    """
    Version information for S3 objects.
    """
    pass


class S3Object(root.DesktopObject, abc.ABC):
    """
    Marker interface for S3 object classes, such as
    heaobject.folder.AWSS3Folder and heaobject.data.AWSS3FileObject.
    """

    @property
    @abc.abstractmethod
    def key(self) -> Optional[str]:
        """
        The object's key.
        """
        pass

    @key.setter
    @abc.abstractmethod
    def key(self, key: Optional[str]):
        pass

    @property
    @abc.abstractmethod
    def s3_uri(self) -> Optional[str]:
        """
        The object's S3 URI, computed from the bucket id and the id field.
        """
        pass

    @property
    @abc.abstractmethod
    def bucket_id(self) -> Optional[str]:
        """
        The object's bucket name.
        """
        pass

    @bucket_id.setter
    @abc.abstractmethod
    def bucket_id(self, bucket_id: Optional[str]):
        pass
