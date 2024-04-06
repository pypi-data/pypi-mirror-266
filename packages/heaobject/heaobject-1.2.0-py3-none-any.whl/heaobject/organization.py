import logging

from .account import AccountAssociation, AWSAccount
from .root import Permission
from .data import DataObject, SameMimeType
from typing import Optional
from copy import deepcopy

permission_id_dict = {
    'admin_ids': [Permission.COOWNER],
    'manager_ids': [Permission.VIEWER, Permission.EDITOR, Permission.SHARER, Permission.DELETER],
    'member_ids': [Permission.VIEWER, Permission.SHARER]
}


class Organization(DataObject, SameMimeType):
    """
    Represents a directory in the HEA desktop.
    """

    def __init__(self) -> None:
        super().__init__()
        # id is a super field
        self.__accounts: dict[AccountAssociation, None] = {}
        self.__principal_investigator_id: Optional[str] = None  # this would be a people id
        self.__admin_ids: list[str] = []  # list of user ids to be managers
        self.__manager_ids: list[str] = []  # list of user ids to be managers
        self.__member_ids: list[str] = []  # list of user ids to be members
        # super's name and display name would be used as org name(required)

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the Organization class.

        :return: application/x.organization
        """
        return 'application/x.organization'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for Organization objects, application/x.organization."""
        return type(self).get_mime_type()

    @property
    def accounts(self) -> list[AccountAssociation]:
        """The list of accounts owned by this organization."""
        return list(deepcopy(account) for account in self.__accounts)

    @accounts.setter
    def accounts(self, accounts: list[AccountAssociation]):
        if accounts is None:
            self.__accounts.clear()
        elif isinstance(accounts, AccountAssociation):
            self.__accounts.clear()
            self.__accounts[deepcopy(accounts)] = None
        else:
            if not all(isinstance(account, AccountAssociation) for account in accounts):
                raise TypeError('accounts can only contain AccountAssociation objects')
            self.__accounts.clear()
            for account in accounts:
                self.__accounts[deepcopy(account)] = None

    def add_account(self, account: AccountAssociation):
        if isinstance(account, AccountAssociation):
            self.__accounts[deepcopy(account)] = None
        else:
            raise TypeError('account must be an AccountAssociation')

    def remove_account(self, account: AccountAssociation):
        try:
            del self.__accounts[account]
        except KeyError:
            raise ValueError(f'Account {account} not found')

    @property
    def aws_account_ids(self) -> list[str]:
        """
        The list of aws account ids owned by this organization.
        """
        return [account.actual_object_id for account in self.__accounts
                if account.actual_object_type_name == AWSAccount.get_type_name()]

    @aws_account_ids.setter
    def aws_account_ids(self, value: list[str]) -> None:
        aws_account_type_name = AWSAccount.get_type_name()
        keys_to_remove = (account for account in self.__accounts if
                          account.actual_object_type_name != aws_account_type_name)
        for key in keys_to_remove:
            del self.__accounts[key]
        if value is None:
            pass
        elif isinstance(value, str):
            self.add_aws_account_id(value)
        else:
            for account_id in value:
                self.add_aws_account_id(account_id)

    def add_aws_account_id(self, value: str) -> None:
        """
        Adds a REST resource to the list of resources that are served by this component.
        :param value: a Resource object.
        """
        account = AccountAssociation()
        account.actual_object_id = value
        account.actual_object_type_name = AWSAccount.get_type_name()
        self.__accounts[deepcopy(account)] = None

    def remove_aws_account_id(self, value: str) -> None:
        """
        Removes a REST aws_account_id from the list of ids that are served by this organization. Ignores None values.
        :param value: str representing the aws account id.
        :raises ValueError: if the value is not among this organization's AWS account ids.
        """
        account_to_remove: AccountAssociation | None = None
        for account in self.__accounts:
            if account.actual_object_type_name == AWSAccount.get_type_name() and account.actual_object_id == value:
                account_to_remove = account
                break
        if account_to_remove is not None:
            del self.__accounts[account_to_remove]
        else:
            raise ValueError(f'AWS account id {value} not found')

    @property
    def principal_investigator_id(self) -> Optional[str]:
        """
        The principal investigator People ID.
        """
        return self.__principal_investigator_id

    @principal_investigator_id.setter
    def principal_investigator_id(self, principal_investigator_id: Optional[str]) -> None:
        self.__principal_investigator_id = str(principal_investigator_id) \
            if principal_investigator_id is not None else None

    @property
    def admin_ids(self) -> list[str]:
        """
        The organization manager ids.
        """
        return [i for i in self.__admin_ids] if self.__admin_ids else []

    @admin_ids.setter
    def admin_ids(self, admin_ids: list[str]) -> None:
        if admin_ids is None:
            self.__admin_ids = []
        elif not isinstance(admin_ids, str):
            self.__admin_ids = [str(i) for i in admin_ids]
        else:
            self.__admin_ids = [str(admin_ids)]

    def add_admin_id(self, value: str) -> None:
        self.__admin_ids.append(str(value))

    def remove_admin_id(self, value: str) -> None:
        """
        Removes a REST manager id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the manager id.
        """
        self.__admin_ids.remove(str(value))

    @property
    def manager_ids(self) -> list[str]:
        """
        The organization manager ids.
        """
        return [i for i in self.__manager_ids] if self.__manager_ids else []

    @manager_ids.setter
    def manager_ids(self, manager_ids: list[str]) -> None:
        if manager_ids is None:
            self.__manager_ids = []
        elif not isinstance(manager_ids, str):
            self.__manager_ids = [str(i) for i in manager_ids]
        else:
            self.__manager_ids = [str(manager_ids)]

    def add_manager_id(self, value: str) -> None:
        self.__manager_ids.append(str(value))

    def remove_manager_id(self, value: str) -> None:
        """
        Removes a REST manager id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the manager id.
        """
        self.__manager_ids.remove(str(value))

    @property
    def member_ids(self) -> list[str]:
        """
        The organization member ids.
        """
        return [i for i in self.__member_ids]

    @member_ids.setter
    def member_ids(self, member_ids: list[str]) -> None:
        if member_ids is None:
            self.__member_ids = []
        elif not isinstance(member_ids, str):
            self.__member_ids = [str(i) for i in member_ids]
        else:
            self.__member_ids = [str(member_ids)]

    def add_member_id(self, value: str) -> None:
        self.__member_ids.append(str(value))

    def remove_member_id(self, value: str) -> None:
        """
        Removes a REST member id from the list of member ids that are served by this organization. Ignores None values.
        :param value: a str representing the member id.
        """
        self.__member_ids.remove(str(value))

    def dynamic_permission(self, sub: str) -> list[Permission]:
        """
        Returns permissions if the sub is in the member_ids list, or an empty list if not.

        :param sub: the user id (required).
        :return: A list containing Permissions or the empty list.
        """
        try:
            perms: set[Permission] = set()
            if sub == self.principal_investigator_id:
                perms.add(Permission.COOWNER)
            else:
                for p_id in permission_id_dict:
                    if sub in getattr(self, p_id):
                        perms.update(permission_id_dict[p_id])
            return list(perms)
        except:
            logging.exception('Permissions are not correctly configured...returning empty permissions set')
            return []
