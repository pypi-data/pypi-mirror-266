from typing import Union
from _typeshed import Incomplete
from collections.abc import Generator
from ipalib import Method, Object, crud
from ipapython.dn import DN

unicode = str
DNA_MAGIC: int
global_output_params: Incomplete

def validate_add_attribute(ugettext, attr) -> None: ...
def validate_set_attribute(ugettext, attr) -> None: ...
def validate_del_attribute(ugettext, attr) -> None: ...
def validate_attribute(ugettext, name, attr) -> None: ...
def get_effective_rights(ldap, dn, attrs: Incomplete | None = ...): ...
def entry_from_entry(entry, newentry) -> None: ...
def entry_to_dict(entry, **options): ...
def pkey_to_unicode(key): ...
def pkey_to_value(key, options): ...
def wait_for_value(ldap, dn, attr, value): ...
def validate_externalhost(ugettext, hostname): ...

external_host_param: Incomplete
member_validator: Incomplete

def validate_host(ldap, dn, keys, options, hostname) -> None: ...
def add_external_pre_callback(membertype, ldap, dn, keys, options): ...

EXTERNAL_OBJ_PREFIX: str

def pre_callback_process_external_objects(
    member_attr, object_desc, ldap, dn, found, not_found, *keys, **options
): ...
def add_external_post_callback(
    ldap,
    dn,
    entry_attrs,
    failed,
    completed,
    memberattr,
    membertype,
    externalattr,
    normalize: bool = ...,
    reject_failures: bool = ...,
): ...
def remove_external_post_callback(
    ldap,
    dn,
    entry_attrs,
    failed,
    completed,
    memberattr,
    membertype,
    externalattr,
): ...
def host_is_master(ldap, fqdn) -> None: ...
def add_missing_object_class(
    ldap,
    objectclass,
    dn,
    entry_attrs: Incomplete | None = ...,
    update: bool = ...,
): ...

class LDAPObject(Object):
    backend_name: str
    parent_object: str
    container_dn: Union[str, DN]
    object_name: Incomplete
    object_name_plural: Incomplete
    object_class: Incomplete
    object_class_config: Incomplete
    possible_objectclasses: Incomplete
    limit_object_classes: Incomplete
    disallow_object_classes: Incomplete
    permission_filter_objectclasses: Incomplete
    search_attributes: Incomplete
    search_attributes_config: Incomplete
    default_attributes: Incomplete
    search_display_attributes: Incomplete
    hidden_attributes: Incomplete
    rdn_attribute: str
    uuid_attribute: str
    attribute_members: Incomplete
    allow_rename: bool
    password_attributes: Incomplete
    bindable: bool
    relationships: Incomplete
    label: Incomplete
    label_singular: Incomplete
    managed_permissions: Incomplete
    container_not_found_msg: Incomplete
    parent_not_found_msg: Incomplete
    object_not_found_msg: Incomplete
    already_exists_msg: Incomplete
    def get_dn(self, *keys, **kwargs): ...
    def get_dn_if_exists(self, *keys, **kwargs): ...
    def get_primary_key_from_dn(self, dn): ...
    def get_ancestor_primary_keys(
        self,
    ) -> Generator[Incomplete, None, None]: ...
    def has_objectclass(self, classes, objectclass): ...
    def convert_attribute_members(
        self, entry_attrs, *keys, **options
    ) -> None: ...
    def get_indirect_members(self, entry_attrs, attrs_list) -> None: ...
    def get_memberindirect(self, group_entry) -> None: ...
    def get_memberofindirect(self, entry) -> None: ...
    def get_password_attributes(self, ldap, dn, entry_attrs) -> None: ...
    def handle_not_found(self, *keys) -> None: ...
    def handle_duplicate_entry(self, *keys) -> None: ...
    json_friendly_attributes: Incomplete
    def __json__(self): ...

class BaseLDAPCommand(Method):
    setattr_option: Incomplete
    addattr_option: Incomplete
    delattr_option: Incomplete
    callback_types: Incomplete
    def get_summary_default(self, output): ...
    def process_attr_options(
        self, entry_attrs, dn, keys, options
    ) -> None: ...
    @classmethod
    def register_pre_callback(cls, callback, first: bool = ...) -> None: ...
    @classmethod
    def register_post_callback(cls, callback, first: bool = ...) -> None: ...
    @classmethod
    def register_exc_callback(cls, callback, first: bool = ...) -> None: ...
    def get_options(self) -> Generator[Incomplete, None, None]: ...

class LDAPCreate(BaseLDAPCommand, crud.Create):
    takes_options: Incomplete
    def get_args(self) -> Generator[Incomplete, None, None]: ...
    has_output_params: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(
        self, ldap, dn, entry_attrs, attrs_list, *keys, **options
    ): ...
    def post_callback(self, ldap, dn, entry_attrs, *keys, **options): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPQuery(BaseLDAPCommand, crud.PKQuery):
    def get_args(self) -> Generator[Incomplete, None, None]: ...

class LDAPMultiQuery(LDAPQuery):
    takes_options: Incomplete
    def get_args(self) -> Generator[Incomplete, None, None]: ...

class LDAPRetrieve(LDAPQuery):
    has_output: Incomplete
    has_output_params: Incomplete
    takes_options: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, attrs_list, *keys, **options): ...
    def post_callback(self, ldap, dn, entry_attrs, *keys, **options): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPUpdate(LDAPQuery, crud.Update):
    takes_options: Incomplete
    has_output_params: Incomplete
    def get_options(self) -> Generator[Incomplete, None, None]: ...
    def execute(self, *keys, **options): ...
    def pre_callback(
        self, ldap, dn, entry_attrs, attrs_list, *keys, **options
    ): ...
    def post_callback(self, ldap, dn, entry_attrs, *keys, **options): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPDelete(LDAPMultiQuery):
    has_output: Incomplete
    has_output_params: Incomplete
    subtree_delete: bool
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, *keys, **options): ...
    def post_callback(self, ldap, dn, *keys, **options): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPModMember(LDAPQuery):
    member_attributes: Incomplete
    member_param_doc: Incomplete
    member_param_label: Incomplete
    member_count_out: Incomplete
    def get_options(self) -> Generator[Incomplete, None, None]: ...
    def get_member_dns(self, **options): ...

class LDAPAddMember(LDAPModMember):
    member_param_doc: Incomplete
    member_count_out: Incomplete
    allow_same: bool
    has_output: Incomplete
    has_output_params: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, found, not_found, *keys, **options): ...
    def post_callback(
        self, ldap, completed, failed, dn, entry_attrs, *keys, **options
    ): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPRemoveMember(LDAPModMember):
    member_param_doc: Incomplete
    member_count_out: Incomplete
    has_output: Incomplete
    has_output_params: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, found, not_found, *keys, **options): ...
    def post_callback(
        self, ldap, completed, failed, dn, entry_attrs, *keys, **options
    ): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

def gen_pkey_only_option(cli_name): ...

class LDAPSearch(BaseLDAPCommand, crud.Search):
    member_attributes: Incomplete
    member_param_incl_doc: Incomplete
    member_param_excl_doc: Incomplete
    sort_result_entries: bool
    takes_options: Incomplete
    def get_args(self) -> Generator[Incomplete, None, None]: ...
    def get_member_options(
        self, attr
    ) -> Generator[Incomplete, None, None]: ...
    def get_options(self) -> Generator[Incomplete, None, None]: ...
    def get_attr_filter(self, ldap, **options): ...
    def get_term_filter(self, ldap, term): ...
    def get_member_filter(self, ldap, **options): ...
    has_output_params: Incomplete
    def execute(self, *args, **options): ...
    def pre_callback(
        self, ldap, filters, attrs_list, base_dn, scope, *args, **options
    ): ...
    def post_callback(self, ldap, entries, truncated, *args, **options): ...
    def exc_callback(
        self, args, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPModReverseMember(LDAPQuery):
    reverse_attributes: Incomplete
    reverse_param_doc: Incomplete
    reverse_count_out: Incomplete
    has_output_params: Incomplete
    def get_options(self) -> Generator[Incomplete, None, None]: ...

class LDAPAddReverseMember(LDAPModReverseMember):
    member_param_doc: Incomplete
    member_count_out: Incomplete
    show_command: Incomplete
    member_command: Incomplete
    reverse_attr: Incomplete
    member_attr: Incomplete
    has_output: Incomplete
    has_output_params: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, *keys, **options): ...
    def post_callback(
        self, ldap, completed, failed, dn, entry_attrs, *keys, **options
    ): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class LDAPRemoveReverseMember(LDAPModReverseMember):
    member_param_doc: Incomplete
    member_count_out: Incomplete
    show_command: Incomplete
    member_command: Incomplete
    reverse_attr: Incomplete
    member_attr: Incomplete
    has_output: Incomplete
    has_output_params: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(self, ldap, dn, *keys, **options): ...
    def post_callback(
        self, ldap, completed, failed, dn, entry_attrs, *keys, **options
    ): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class BaseLDAPModAttribute(LDAPQuery):
    attribute: Incomplete
    has_output: Incomplete
    def execute(self, *keys, **options): ...
    def pre_callback(
        self, ldap, dn, entry_attrs, attrs_list, *keys, **options
    ): ...
    def post_callback(self, ldap, dn, entry_attrs, *keys, **options): ...
    def exc_callback(
        self, keys, options, exc, call_func, *call_args, **call_kwargs
    ) -> None: ...

class BaseLDAPAddAttribute(BaseLDAPModAttribute):
    msg_summary: Incomplete

class BaseLDAPRemoveAttribute(BaseLDAPModAttribute):
    msg_summary: Incomplete

class LDAPModAttribute(BaseLDAPModAttribute):
    def get_args(self) -> Generator[Incomplete, None, None]: ...

class LDAPAddAttribute(LDAPModAttribute, BaseLDAPAddAttribute): ...
class LDAPRemoveAttribute(LDAPModAttribute, BaseLDAPRemoveAttribute): ...

class LDAPModAttributeViaOption(BaseLDAPModAttribute):
    def get_options(self) -> Generator[Incomplete, None, None]: ...

class LDAPAddAttributeViaOption(
    LDAPModAttributeViaOption, BaseLDAPAddAttribute
): ...
class LDAPRemoveAttributeViaOption(
    LDAPModAttributeViaOption, BaseLDAPRemoveAttribute
): ...
