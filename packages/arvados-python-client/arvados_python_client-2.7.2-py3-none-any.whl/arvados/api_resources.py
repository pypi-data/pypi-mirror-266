"""Arvados API client reference documentation

This module provides reference documentation for the interface of the
Arvados API client, including method signatures and type information for
returned objects. However, the functions in `arvados.api` will return
different classes at runtime that are generated dynamically from the Arvados
API discovery document. The classes in this module do not have any
implementation, and you should not instantiate them in your code.

If you're just starting out, `ArvadosAPIClient` documents the methods
available from the client object. From there, you can follow the trail into
resource methods, request objects, and finally the data dictionaries returned
by the API server.
"""

import googleapiclient.discovery
import googleapiclient.http
import httplib2
import sys
from typing import Any, Dict, Generic, List, Optional, TypeVar
if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

# ST represents an API response type
ST = TypeVar('ST', bound=TypedDict)

class ApiClient(TypedDict, total=False):
    """ApiClient

    This is the dictionary object that represents a single ApiClient in Arvados
    and is returned by most `ApiClients` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    url_prefix: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trusted: 'bool'


class ApiClientAuthorization(TypedDict, total=False):
    """ApiClientAuthorization

    This is the dictionary object that represents a single ApiClientAuthorization in Arvados
    and is returned by most `ApiClientAuthorizations` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    api_token: 'str'
    api_client_id: 'int'
    user_id: 'int'
    created_by_ip_address: 'str'
    last_used_by_ip_address: 'str'
    last_used_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    expires_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    default_owner_uuid: 'str'
    scopes: 'List'


class ApiClientAuthorizationList(TypedDict, total=False):
    """ApiClientAuthorization list

    This is the dictionary object returned when you call `ApiClientAuthorizations.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ApiClientAuthorization` objects.
    """
    kind: 'str' = 'arvados#apiClientAuthorizationList'
    """Object type. Always arvados#apiClientAuthorizationList."""
    etag: 'str'
    """List version."""
    items: 'List[ApiClientAuthorization]'
    """The list of ApiClientAuthorizations."""
    next_link: 'str'
    """A link to the next page of ApiClientAuthorizations."""
    next_page_token: 'str'
    """The page token for the next page of ApiClientAuthorizations."""
    selfLink: 'str'
    """A link back to this list."""


class ApiClientList(TypedDict, total=False):
    """ApiClient list

    This is the dictionary object returned when you call `ApiClients.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ApiClient` objects.
    """
    kind: 'str' = 'arvados#apiClientList'
    """Object type. Always arvados#apiClientList."""
    etag: 'str'
    """List version."""
    items: 'List[ApiClient]'
    """The list of ApiClients."""
    next_link: 'str'
    """A link to the next page of ApiClients."""
    next_page_token: 'str'
    """The page token for the next page of ApiClients."""
    selfLink: 'str'
    """A link back to this list."""


class AuthorizedKey(TypedDict, total=False):
    """AuthorizedKey

    This is the dictionary object that represents a single AuthorizedKey in Arvados
    and is returned by most `AuthorizedKeys` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    key_type: 'str'
    authorized_user_uuid: 'str'
    public_key: 'str'
    expires_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class AuthorizedKeyList(TypedDict, total=False):
    """AuthorizedKey list

    This is the dictionary object returned when you call `AuthorizedKeys.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `AuthorizedKey` objects.
    """
    kind: 'str' = 'arvados#authorizedKeyList'
    """Object type. Always arvados#authorizedKeyList."""
    etag: 'str'
    """List version."""
    items: 'List[AuthorizedKey]'
    """The list of AuthorizedKeys."""
    next_link: 'str'
    """A link to the next page of AuthorizedKeys."""
    next_page_token: 'str'
    """The page token for the next page of AuthorizedKeys."""
    selfLink: 'str'
    """A link back to this list."""


class Collection(TypedDict, total=False):
    """Collection

    This is the dictionary object that represents a single Collection in Arvados
    and is returned by most `Collections` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    portable_data_hash: 'str'
    replication_desired: 'int'
    replication_confirmed_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    replication_confirmed: 'int'
    manifest_text: 'str'
    name: 'str'
    description: 'str'
    properties: 'Dict[str, Any]'
    delete_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    trash_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    storage_classes_desired: 'List'
    storage_classes_confirmed: 'List'
    storage_classes_confirmed_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    current_version_uuid: 'str'
    version: 'int'
    preserve_version: 'bool'
    file_count: 'int'
    file_size_total: 'int'


class CollectionList(TypedDict, total=False):
    """Collection list

    This is the dictionary object returned when you call `Collections.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Collection` objects.
    """
    kind: 'str' = 'arvados#collectionList'
    """Object type. Always arvados#collectionList."""
    etag: 'str'
    """List version."""
    items: 'List[Collection]'
    """The list of Collections."""
    next_link: 'str'
    """A link to the next page of Collections."""
    next_page_token: 'str'
    """The page token for the next page of Collections."""
    selfLink: 'str'
    """A link back to this list."""


class Container(TypedDict, total=False):
    """Container

    This is the dictionary object that represents a single Container in Arvados
    and is returned by most `Containers` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    state: 'str'
    started_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    finished_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    log: 'str'
    environment: 'Dict[str, Any]'
    cwd: 'str'
    command: 'List'
    output_path: 'str'
    mounts: 'Dict[str, Any]'
    runtime_constraints: 'Dict[str, Any]'
    output: 'str'
    container_image: 'str'
    progress: 'float'
    priority: 'int'
    exit_code: 'int'
    auth_uuid: 'str'
    locked_by_uuid: 'str'
    scheduling_parameters: 'Dict[str, Any]'
    runtime_status: 'Dict[str, Any]'
    runtime_user_uuid: 'str'
    runtime_auth_scopes: 'List'
    lock_count: 'int'
    gateway_address: 'str'
    interactive_session_started: 'bool'
    output_storage_classes: 'List'
    output_properties: 'Dict[str, Any]'
    cost: 'float'
    subrequests_cost: 'float'


class ContainerList(TypedDict, total=False):
    """Container list

    This is the dictionary object returned when you call `Containers.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Container` objects.
    """
    kind: 'str' = 'arvados#containerList'
    """Object type. Always arvados#containerList."""
    etag: 'str'
    """List version."""
    items: 'List[Container]'
    """The list of Containers."""
    next_link: 'str'
    """A link to the next page of Containers."""
    next_page_token: 'str'
    """The page token for the next page of Containers."""
    selfLink: 'str'
    """A link back to this list."""


class ContainerRequest(TypedDict, total=False):
    """ContainerRequest

    This is the dictionary object that represents a single ContainerRequest in Arvados
    and is returned by most `ContainerRequests` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    name: 'str'
    description: 'str'
    properties: 'Dict[str, Any]'
    state: 'str'
    requesting_container_uuid: 'str'
    container_uuid: 'str'
    container_count_max: 'int'
    mounts: 'Dict[str, Any]'
    runtime_constraints: 'Dict[str, Any]'
    container_image: 'str'
    environment: 'Dict[str, Any]'
    cwd: 'str'
    command: 'List'
    output_path: 'str'
    priority: 'int'
    expires_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    filters: 'str'
    container_count: 'int'
    use_existing: 'bool'
    scheduling_parameters: 'Dict[str, Any]'
    output_uuid: 'str'
    log_uuid: 'str'
    output_name: 'str'
    output_ttl: 'int'
    output_storage_classes: 'List'
    output_properties: 'Dict[str, Any]'
    cumulative_cost: 'float'


class ContainerRequestList(TypedDict, total=False):
    """ContainerRequest list

    This is the dictionary object returned when you call `ContainerRequests.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `ContainerRequest` objects.
    """
    kind: 'str' = 'arvados#containerRequestList'
    """Object type. Always arvados#containerRequestList."""
    etag: 'str'
    """List version."""
    items: 'List[ContainerRequest]'
    """The list of ContainerRequests."""
    next_link: 'str'
    """A link to the next page of ContainerRequests."""
    next_page_token: 'str'
    """The page token for the next page of ContainerRequests."""
    selfLink: 'str'
    """A link back to this list."""


class Group(TypedDict, total=False):
    """Group

    This is the dictionary object that represents a single Group in Arvados
    and is returned by most `Groups` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    description: 'str'
    group_class: 'str'
    trash_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    delete_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    properties: 'Dict[str, Any]'
    frozen_by_uuid: 'str'


class GroupList(TypedDict, total=False):
    """Group list

    This is the dictionary object returned when you call `Groups.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Group` objects.
    """
    kind: 'str' = 'arvados#groupList'
    """Object type. Always arvados#groupList."""
    etag: 'str'
    """List version."""
    items: 'List[Group]'
    """The list of Groups."""
    next_link: 'str'
    """A link to the next page of Groups."""
    next_page_token: 'str'
    """The page token for the next page of Groups."""
    selfLink: 'str'
    """A link back to this list."""


class Human(TypedDict, total=False):
    """Human

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single Human in Arvados
    and is returned by most `Humans` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    properties: 'Dict[str, Any]'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class HumanList(TypedDict, total=False):
    """Human list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `Humans.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Human` objects.
    """
    kind: 'str' = 'arvados#humanList'
    """Object type. Always arvados#humanList."""
    etag: 'str'
    """List version."""
    items: 'List[Human]'
    """The list of Humans."""
    next_link: 'str'
    """A link to the next page of Humans."""
    next_page_token: 'str'
    """The page token for the next page of Humans."""
    selfLink: 'str'
    """A link back to this list."""


class Job(TypedDict, total=False):
    """Job

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single Job in Arvados
    and is returned by most `Jobs` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    submit_id: 'str'
    script: 'str'
    script_version: 'str'
    script_parameters: 'Dict[str, Any]'
    cancelled_by_client_uuid: 'str'
    cancelled_by_user_uuid: 'str'
    cancelled_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    started_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    finished_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    running: 'bool'
    success: 'bool'
    output: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_locked_by_uuid: 'str'
    log: 'str'
    tasks_summary: 'Dict[str, Any]'
    runtime_constraints: 'Dict[str, Any]'
    nondeterministic: 'bool'
    repository: 'str'
    supplied_script_version: 'str'
    docker_image_locator: 'str'
    priority: 'int'
    description: 'str'
    state: 'str'
    arvados_sdk_version: 'str'
    components: 'Dict[str, Any]'


class JobList(TypedDict, total=False):
    """Job list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `Jobs.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Job` objects.
    """
    kind: 'str' = 'arvados#jobList'
    """Object type. Always arvados#jobList."""
    etag: 'str'
    """List version."""
    items: 'List[Job]'
    """The list of Jobs."""
    next_link: 'str'
    """A link to the next page of Jobs."""
    next_page_token: 'str'
    """The page token for the next page of Jobs."""
    selfLink: 'str'
    """A link back to this list."""


class JobTask(TypedDict, total=False):
    """JobTask

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single JobTask in Arvados
    and is returned by most `JobTasks` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    job_uuid: 'str'
    sequence: 'int'
    parameters: 'Dict[str, Any]'
    output: 'str'
    progress: 'float'
    success: 'bool'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_by_job_task_uuid: 'str'
    qsequence: 'int'
    started_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    finished_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class JobTaskList(TypedDict, total=False):
    """JobTask list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `JobTasks.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `JobTask` objects.
    """
    kind: 'str' = 'arvados#jobTaskList'
    """Object type. Always arvados#jobTaskList."""
    etag: 'str'
    """List version."""
    items: 'List[JobTask]'
    """The list of JobTasks."""
    next_link: 'str'
    """A link to the next page of JobTasks."""
    next_page_token: 'str'
    """The page token for the next page of JobTasks."""
    selfLink: 'str'
    """A link back to this list."""


class KeepDisk(TypedDict, total=False):
    """KeepDisk

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single KeepDisk in Arvados
    and is returned by most `KeepDisks` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    node_uuid: 'str'
    filesystem_uuid: 'str'
    bytes_total: 'int'
    bytes_free: 'int'
    is_readable: 'bool'
    is_writable: 'bool'
    last_read_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    last_write_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    last_ping_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    keep_service_uuid: 'str'


class KeepDiskList(TypedDict, total=False):
    """KeepDisk list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `KeepDisks.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `KeepDisk` objects.
    """
    kind: 'str' = 'arvados#keepDiskList'
    """Object type. Always arvados#keepDiskList."""
    etag: 'str'
    """List version."""
    items: 'List[KeepDisk]'
    """The list of KeepDisks."""
    next_link: 'str'
    """A link to the next page of KeepDisks."""
    next_page_token: 'str'
    """The page token for the next page of KeepDisks."""
    selfLink: 'str'
    """A link back to this list."""


class KeepService(TypedDict, total=False):
    """KeepService

    This is the dictionary object that represents a single KeepService in Arvados
    and is returned by most `KeepServices` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    service_host: 'str'
    service_port: 'int'
    service_ssl_flag: 'bool'
    service_type: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    read_only: 'bool'


class KeepServiceList(TypedDict, total=False):
    """KeepService list

    This is the dictionary object returned when you call `KeepServices.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `KeepService` objects.
    """
    kind: 'str' = 'arvados#keepServiceList'
    """Object type. Always arvados#keepServiceList."""
    etag: 'str'
    """List version."""
    items: 'List[KeepService]'
    """The list of KeepServices."""
    next_link: 'str'
    """A link to the next page of KeepServices."""
    next_page_token: 'str'
    """The page token for the next page of KeepServices."""
    selfLink: 'str'
    """A link back to this list."""


class Link(TypedDict, total=False):
    """Link

    This is the dictionary object that represents a single Link in Arvados
    and is returned by most `Links` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    tail_uuid: 'str'
    link_class: 'str'
    name: 'str'
    head_uuid: 'str'
    properties: 'Dict[str, Any]'


class LinkList(TypedDict, total=False):
    """Link list

    This is the dictionary object returned when you call `Links.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Link` objects.
    """
    kind: 'str' = 'arvados#linkList'
    """Object type. Always arvados#linkList."""
    etag: 'str'
    """List version."""
    items: 'List[Link]'
    """The list of Links."""
    next_link: 'str'
    """A link to the next page of Links."""
    next_page_token: 'str'
    """The page token for the next page of Links."""
    selfLink: 'str'
    """A link back to this list."""


class Log(TypedDict, total=False):
    """Log

    This is the dictionary object that represents a single Log in Arvados
    and is returned by most `Logs` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    id: 'int'
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    object_uuid: 'str'
    event_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    event_type: 'str'
    summary: 'str'
    properties: 'Dict[str, Any]'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    object_owner_uuid: 'str'


class LogList(TypedDict, total=False):
    """Log list

    This is the dictionary object returned when you call `Logs.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Log` objects.
    """
    kind: 'str' = 'arvados#logList'
    """Object type. Always arvados#logList."""
    etag: 'str'
    """List version."""
    items: 'List[Log]'
    """The list of Logs."""
    next_link: 'str'
    """A link to the next page of Logs."""
    next_page_token: 'str'
    """The page token for the next page of Logs."""
    selfLink: 'str'
    """A link back to this list."""


class Node(TypedDict, total=False):
    """Node

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single Node in Arvados
    and is returned by most `Nodes` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    slot_number: 'int'
    hostname: 'str'
    domain: 'str'
    ip_address: 'str'
    last_ping_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    properties: 'Dict[str, Any]'
    job_uuid: 'str'


class NodeList(TypedDict, total=False):
    """Node list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `Nodes.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Node` objects.
    """
    kind: 'str' = 'arvados#nodeList'
    """Object type. Always arvados#nodeList."""
    etag: 'str'
    """List version."""
    items: 'List[Node]'
    """The list of Nodes."""
    next_link: 'str'
    """A link to the next page of Nodes."""
    next_page_token: 'str'
    """The page token for the next page of Nodes."""
    selfLink: 'str'
    """A link back to this list."""


class PipelineInstance(TypedDict, total=False):
    """PipelineInstance

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single PipelineInstance in Arvados
    and is returned by most `PipelineInstances` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    pipeline_template_uuid: 'str'
    name: 'str'
    components: 'Dict[str, Any]'
    properties: 'Dict[str, Any]'
    state: 'str'
    components_summary: 'Dict[str, Any]'
    started_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    finished_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    description: 'str'


class PipelineInstanceList(TypedDict, total=False):
    """PipelineInstance list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `PipelineInstances.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `PipelineInstance` objects.
    """
    kind: 'str' = 'arvados#pipelineInstanceList'
    """Object type. Always arvados#pipelineInstanceList."""
    etag: 'str'
    """List version."""
    items: 'List[PipelineInstance]'
    """The list of PipelineInstances."""
    next_link: 'str'
    """A link to the next page of PipelineInstances."""
    next_page_token: 'str'
    """The page token for the next page of PipelineInstances."""
    selfLink: 'str'
    """A link back to this list."""


class PipelineTemplate(TypedDict, total=False):
    """PipelineTemplate

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object that represents a single PipelineTemplate in Arvados
    and is returned by most `PipelineTemplates` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    components: 'Dict[str, Any]'
    description: 'str'


class PipelineTemplateList(TypedDict, total=False):
    """PipelineTemplate list

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.


    This is the dictionary object returned when you call `PipelineTemplates.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `PipelineTemplate` objects.
    """
    kind: 'str' = 'arvados#pipelineTemplateList'
    """Object type. Always arvados#pipelineTemplateList."""
    etag: 'str'
    """List version."""
    items: 'List[PipelineTemplate]'
    """The list of PipelineTemplates."""
    next_link: 'str'
    """A link to the next page of PipelineTemplates."""
    next_page_token: 'str'
    """The page token for the next page of PipelineTemplates."""
    selfLink: 'str'
    """A link back to this list."""


class Repository(TypedDict, total=False):
    """Repository

    This is the dictionary object that represents a single Repository in Arvados
    and is returned by most `Repositorys` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class RepositoryList(TypedDict, total=False):
    """Repository list

    This is the dictionary object returned when you call `Repositorys.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Repository` objects.
    """
    kind: 'str' = 'arvados#repositoryList'
    """Object type. Always arvados#repositoryList."""
    etag: 'str'
    """List version."""
    items: 'List[Repository]'
    """The list of Repositories."""
    next_link: 'str'
    """A link to the next page of Repositories."""
    next_page_token: 'str'
    """The page token for the next page of Repositories."""
    selfLink: 'str'
    """A link back to this list."""


class Specimen(TypedDict, total=False):
    """Specimen

    This is the dictionary object that represents a single Specimen in Arvados
    and is returned by most `Specimens` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    material: 'str'
    properties: 'Dict[str, Any]'


class SpecimenList(TypedDict, total=False):
    """Specimen list

    This is the dictionary object returned when you call `Specimens.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Specimen` objects.
    """
    kind: 'str' = 'arvados#specimenList'
    """Object type. Always arvados#specimenList."""
    etag: 'str'
    """List version."""
    items: 'List[Specimen]'
    """The list of Specimens."""
    next_link: 'str'
    """A link to the next page of Specimens."""
    next_page_token: 'str'
    """The page token for the next page of Specimens."""
    selfLink: 'str'
    """A link back to this list."""


class Trait(TypedDict, total=False):
    """Trait

    This is the dictionary object that represents a single Trait in Arvados
    and is returned by most `Traits` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    name: 'str'
    properties: 'Dict[str, Any]'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class TraitList(TypedDict, total=False):
    """Trait list

    This is the dictionary object returned when you call `Traits.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Trait` objects.
    """
    kind: 'str' = 'arvados#traitList'
    """Object type. Always arvados#traitList."""
    etag: 'str'
    """List version."""
    items: 'List[Trait]'
    """The list of Traits."""
    next_link: 'str'
    """A link to the next page of Traits."""
    next_page_token: 'str'
    """The page token for the next page of Traits."""
    selfLink: 'str'
    """A link back to this list."""


class User(TypedDict, total=False):
    """User

    This is the dictionary object that represents a single User in Arvados
    and is returned by most `Users` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    email: 'str'
    first_name: 'str'
    last_name: 'str'
    identity_url: 'str'
    is_admin: 'bool'
    prefs: 'Dict[str, Any]'
    is_active: 'bool'
    username: 'str'


class UserAgreement(TypedDict, total=False):
    """UserAgreement

    This is the dictionary object that represents a single UserAgreement in Arvados
    and is returned by most `UserAgreements` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    portable_data_hash: 'str'
    replication_desired: 'int'
    replication_confirmed_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    replication_confirmed: 'int'
    manifest_text: 'str'
    name: 'str'
    description: 'str'
    properties: 'Dict[str, Any]'
    delete_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    trash_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    is_trashed: 'bool'
    storage_classes_desired: 'List'
    storage_classes_confirmed: 'List'
    storage_classes_confirmed_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    current_version_uuid: 'str'
    version: 'int'
    preserve_version: 'bool'
    file_count: 'int'
    file_size_total: 'int'


class UserAgreementList(TypedDict, total=False):
    """UserAgreement list

    This is the dictionary object returned when you call `UserAgreements.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `UserAgreement` objects.
    """
    kind: 'str' = 'arvados#userAgreementList'
    """Object type. Always arvados#userAgreementList."""
    etag: 'str'
    """List version."""
    items: 'List[UserAgreement]'
    """The list of UserAgreements."""
    next_link: 'str'
    """A link to the next page of UserAgreements."""
    next_page_token: 'str'
    """The page token for the next page of UserAgreements."""
    selfLink: 'str'
    """A link back to this list."""


class UserList(TypedDict, total=False):
    """User list

    This is the dictionary object returned when you call `Users.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `User` objects.
    """
    kind: 'str' = 'arvados#userList'
    """Object type. Always arvados#userList."""
    etag: 'str'
    """List version."""
    items: 'List[User]'
    """The list of Users."""
    next_link: 'str'
    """A link to the next page of Users."""
    next_page_token: 'str'
    """The page token for the next page of Users."""
    selfLink: 'str'
    """A link back to this list."""


class VirtualMachine(TypedDict, total=False):
    """VirtualMachine

    This is the dictionary object that represents a single VirtualMachine in Arvados
    and is returned by most `VirtualMachines` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    hostname: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""


class VirtualMachineList(TypedDict, total=False):
    """VirtualMachine list

    This is the dictionary object returned when you call `VirtualMachines.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `VirtualMachine` objects.
    """
    kind: 'str' = 'arvados#virtualMachineList'
    """Object type. Always arvados#virtualMachineList."""
    etag: 'str'
    """List version."""
    items: 'List[VirtualMachine]'
    """The list of VirtualMachines."""
    next_link: 'str'
    """A link to the next page of VirtualMachines."""
    next_page_token: 'str'
    """The page token for the next page of VirtualMachines."""
    selfLink: 'str'
    """A link back to this list."""


class Workflow(TypedDict, total=False):
    """Workflow

    This is the dictionary object that represents a single Workflow in Arvados
    and is returned by most `Workflows` methods.
    The keys of the dictionary are documented below, along with their types.
    Not every key may appear in every dictionary returned by an API call.
    When a method doesn't return all the data, you can use its `select` parameter
    to list the specific keys you need. Refer to the API documentation for details.
    """
    uuid: 'str'
    etag: 'str'
    """Object version."""
    owner_uuid: 'str'
    created_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_at: 'str'
    """String in ISO 8601 datetime format. Pass it to `ciso8601.parse_datetime` to build a `datetime.datetime`."""
    modified_by_client_uuid: 'str'
    modified_by_user_uuid: 'str'
    name: 'str'
    description: 'str'
    definition: 'str'


class WorkflowList(TypedDict, total=False):
    """Workflow list

    This is the dictionary object returned when you call `Workflows.list`.
    If you just want to iterate all objects that match your search criteria,
    consider using `arvados.util.keyset_list_all`.
    If you work with this raw object, the keys of the dictionary are documented
    below, along with their types. The `items` key maps to a list of matching
    `Workflow` objects.
    """
    kind: 'str' = 'arvados#workflowList'
    """Object type. Always arvados#workflowList."""
    etag: 'str'
    """List version."""
    items: 'List[Workflow]'
    """The list of Workflows."""
    next_link: 'str'
    """A link to the next page of Workflows."""
    next_page_token: 'str'
    """The page token for the next page of Workflows."""
    selfLink: 'str'
    """A link back to this list."""


class ApiClientAuthorizations:
    """Methods to query and manipulate Arvados api client authorizations"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Create a new ApiClientAuthorization.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def create_system_auth(self, *, api_client_id: 'int', scopes: 'List') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """create_system_auth api_client_authorizations

        Optional parameters:

        * api_client_id: int

        * scopes: List
        """

    def current(self) -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """current api_client_authorizations"""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Delete an existing ApiClientAuthorization.

        Required parameters:

        * uuid: str --- The UUID of the ApiClientAuthorization in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Gets a ApiClientAuthorization's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the ApiClientAuthorization in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[ApiClientAuthorizationList]':
        """List ApiClientAuthorizations.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[ApiClientAuthorization]':
        """Update attributes of an existing ApiClientAuthorization.

        Required parameters:

        * uuid: str --- The UUID of the ApiClientAuthorization in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class ApiClients:
    """Methods to query and manipulate Arvados api clients"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[ApiClient]':
        """Create a new ApiClient.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ApiClient]':
        """Delete an existing ApiClient.

        Required parameters:

        * uuid: str --- The UUID of the ApiClient in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ApiClient]':
        """Gets a ApiClient's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the ApiClient in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[ApiClientList]':
        """List ApiClients.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[ApiClient]':
        """Update attributes of an existing ApiClient.

        Required parameters:

        * uuid: str --- The UUID of the ApiClient in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class AuthorizedKeys:
    """Methods to query and manipulate Arvados authorized keys"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Create a new AuthorizedKey.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Delete an existing AuthorizedKey.

        Required parameters:

        * uuid: str --- The UUID of the AuthorizedKey in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Gets a AuthorizedKey's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the AuthorizedKey in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[AuthorizedKeyList]':
        """List AuthorizedKeys.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[AuthorizedKey]':
        """Update attributes of an existing AuthorizedKey.

        Required parameters:

        * uuid: str --- The UUID of the AuthorizedKey in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Collections:
    """Methods to query and manipulate Arvados collections"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', replace_files: 'Dict[str, Any]', select: 'List') -> 'ArvadosAPIRequest[Collection]':
        """Create a new Collection.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * replace_files: Dict[str, Any] --- Files and directories to initialize/replace with content from other collections.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Delete an existing Collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """Gets a Collection's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Collection in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', include_old_versions: 'bool', include_trash: 'bool', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[CollectionList]':
        """List Collections.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * include_old_versions: bool --- Include past collection versions. Default False.

        * include_trash: bool --- Include collections whose is_trashed attribute is true. Default False.

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def provenance(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """provenance collections

        Required parameters:

        * uuid: str
        """

    def trash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """trash collections

        Required parameters:

        * uuid: str
        """

    def untrash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """untrash collections

        Required parameters:

        * uuid: str
        """

    def update(self, *, uuid: 'str', replace_files: 'Dict[str, Any]', select: 'List') -> 'ArvadosAPIRequest[Collection]':
        """Update attributes of an existing Collection.

        Required parameters:

        * uuid: str --- The UUID of the Collection in question.

        Optional parameters:

        * replace_files: Dict[str, Any] --- Files and directories to initialize/replace with content from other collections.

        * select: List --- Attributes of the updated object to return in the response.
        """

    def used_by(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Collection]':
        """used_by collections

        Required parameters:

        * uuid: str
        """


class Configs:
    """Methods to query and manipulate Arvados configs"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """Get public config"""


class ContainerRequests:
    """Methods to query and manipulate Arvados container requests"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Create a new ContainerRequest.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Delete an existing ContainerRequest.

        Required parameters:

        * uuid: str --- The UUID of the ContainerRequest in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Gets a ContainerRequest's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the ContainerRequest in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', include_trash: 'bool', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[ContainerRequestList]':
        """List ContainerRequests.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * include_trash: bool --- Include container requests whose owner project is trashed. Default False.

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[ContainerRequest]':
        """Update attributes of an existing ContainerRequest.

        Required parameters:

        * uuid: str --- The UUID of the ContainerRequest in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Containers:
    """Methods to query and manipulate Arvados containers"""

    def auth(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """auth containers

        Required parameters:

        * uuid: str
        """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Container]':
        """Create a new Container.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def current(self) -> 'ArvadosAPIRequest[Container]':
        """current containers"""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Delete an existing Container.

        Required parameters:

        * uuid: str --- The UUID of the Container in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """Gets a Container's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Container in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[ContainerList]':
        """List Containers.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def lock(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """lock containers

        Required parameters:

        * uuid: str
        """

    def secret_mounts(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """secret_mounts containers

        Required parameters:

        * uuid: str
        """

    def unlock(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """unlock containers

        Required parameters:

        * uuid: str
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Container]':
        """Update attributes of an existing Container.

        Required parameters:

        * uuid: str --- The UUID of the Container in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """

    def update_priority(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Container]':
        """update_priority containers

        Required parameters:

        * uuid: str
        """


class Groups:
    """Methods to query and manipulate Arvados groups"""

    def contents(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', include: 'str', include_old_versions: 'bool', include_trash: 'bool', limit: 'int', offset: 'int', order: 'List', recursive: 'bool', select: 'List', uuid: 'str', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[Group]':
        """contents groups

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * include: str --- Include objects referred to by listed field in "included" (only owner_uuid).

        * include_old_versions: bool --- Include past collection versions. Default False.

        * include_trash: bool --- Include items whose is_trashed attribute is true. Default False.

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * recursive: bool --- Include contents from child groups recursively. Default False.

        * select: List --- Attributes of each object to return in the response.

        * uuid: str --- Default ''.

        * where: Dict[str, Any]
        """

    def create(self, *, async_: 'bool', cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Group]':
        """Create a new Group.

        Optional parameters:

        * async: bool --- defer permissions update Default False.

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """Delete an existing Group.

        Required parameters:

        * uuid: str --- The UUID of the Group in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """Gets a Group's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Group in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', include_trash: 'bool', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[GroupList]':
        """List Groups.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * include_trash: bool --- Include items whose is_trashed attribute is true. Default False.

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def shared(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', include: 'str', include_trash: 'bool', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[Group]':
        """shared groups

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * include: str

        * include_trash: bool --- Include items whose is_trashed attribute is true. Default False.

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def trash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """trash groups

        Required parameters:

        * uuid: str
        """

    def untrash(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Group]':
        """untrash groups

        Required parameters:

        * uuid: str
        """

    def update(self, *, uuid: 'str', async_: 'bool', select: 'List') -> 'ArvadosAPIRequest[Group]':
        """Update attributes of an existing Group.

        Required parameters:

        * uuid: str --- The UUID of the Group in question.

        Optional parameters:

        * async: bool --- defer permissions update Default False.

        * select: List --- Attributes of the updated object to return in the response.
        """


class Humans:
    """Methods to query and manipulate Arvados humans

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Human]':
        """Create a new Human.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Human]':
        """Delete an existing Human.

        Required parameters:

        * uuid: str --- The UUID of the Human in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Human]':
        """Gets a Human's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Human in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[HumanList]':
        """List Humans.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Human]':
        """Update attributes of an existing Human.

        Required parameters:

        * uuid: str --- The UUID of the Human in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class JobTasks:
    """Methods to query and manipulate Arvados job tasks

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[JobTask]':
        """Create a new JobTask.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[JobTask]':
        """Delete an existing JobTask.

        Required parameters:

        * uuid: str --- The UUID of the JobTask in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[JobTask]':
        """Gets a JobTask's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the JobTask in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[JobTaskList]':
        """List JobTasks.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[JobTask]':
        """Update attributes of an existing JobTask.

        Required parameters:

        * uuid: str --- The UUID of the JobTask in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Jobs:
    """Methods to query and manipulate Arvados jobs

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def cancel(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Job]':
        """cancel jobs

        Required parameters:

        * uuid: str
        """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', exclude_script_versions: 'List', filters: 'List', find_or_create: 'bool', minimum_script_version: 'str', select: 'List') -> 'ArvadosAPIRequest[Job]':
        """Create a new Job.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * exclude_script_versions: List

        * filters: List

        * find_or_create: bool --- Default False.

        * minimum_script_version: str

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Job]':
        """Delete an existing Job.

        Required parameters:

        * uuid: str --- The UUID of the Job in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Job]':
        """Gets a Job's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Job in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[JobList]':
        """List Jobs.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def lock(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Job]':
        """lock jobs

        Required parameters:

        * uuid: str
        """

    def queue(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[Job]':
        """queue jobs

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def queue_size(self) -> 'ArvadosAPIRequest[Job]':
        """queue_size jobs"""

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Job]':
        """Update attributes of an existing Job.

        Required parameters:

        * uuid: str --- The UUID of the Job in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class KeepDisks:
    """Methods to query and manipulate Arvados keep disks

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[KeepDisk]':
        """Create a new KeepDisk.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[KeepDisk]':
        """Delete an existing KeepDisk.

        Required parameters:

        * uuid: str --- The UUID of the KeepDisk in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[KeepDisk]':
        """Gets a KeepDisk's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the KeepDisk in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[KeepDiskList]':
        """List KeepDisks.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def ping(self, *, ping_secret: 'str', service_port: 'str', service_ssl_flag: 'str', filesystem_uuid: 'str', node_uuid: 'str', service_host: 'str', uuid: 'str') -> 'ArvadosAPIRequest[KeepDisk]':
        """ping keep_disks

        Required parameters:

        * ping_secret: str

        * service_port: str

        * service_ssl_flag: str

        Optional parameters:

        * filesystem_uuid: str

        * node_uuid: str

        * service_host: str

        * uuid: str
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[KeepDisk]':
        """Update attributes of an existing KeepDisk.

        Required parameters:

        * uuid: str --- The UUID of the KeepDisk in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class KeepServices:
    """Methods to query and manipulate Arvados keep services"""

    def accessible(self) -> 'ArvadosAPIRequest[KeepService]':
        """accessible keep_services"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[KeepService]':
        """Create a new KeepService.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[KeepService]':
        """Delete an existing KeepService.

        Required parameters:

        * uuid: str --- The UUID of the KeepService in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[KeepService]':
        """Gets a KeepService's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the KeepService in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[KeepServiceList]':
        """List KeepServices.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[KeepService]':
        """Update attributes of an existing KeepService.

        Required parameters:

        * uuid: str --- The UUID of the KeepService in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Links:
    """Methods to query and manipulate Arvados links"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Link]':
        """Create a new Link.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Link]':
        """Delete an existing Link.

        Required parameters:

        * uuid: str --- The UUID of the Link in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Link]':
        """Gets a Link's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Link in question.
        """

    def get_permissions(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Link]':
        """get_permissions links

        Required parameters:

        * uuid: str
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[LinkList]':
        """List Links.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Link]':
        """Update attributes of an existing Link.

        Required parameters:

        * uuid: str --- The UUID of the Link in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Logs:
    """Methods to query and manipulate Arvados logs"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Log]':
        """Create a new Log.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Log]':
        """Delete an existing Log.

        Required parameters:

        * uuid: str --- The UUID of the Log in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Log]':
        """Gets a Log's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Log in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[LogList]':
        """List Logs.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Log]':
        """Update attributes of an existing Log.

        Required parameters:

        * uuid: str --- The UUID of the Log in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Nodes:
    """Methods to query and manipulate Arvados nodes

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def create(self, *, assign_slot: 'bool', cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Node]':
        """Create a new Node.

        Optional parameters:

        * assign_slot: bool --- assign slot and hostname

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Node]':
        """Delete an existing Node.

        Required parameters:

        * uuid: str --- The UUID of the Node in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Node]':
        """Gets a Node's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Node in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[NodeList]':
        """List Nodes.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def ping(self, *, ping_secret: 'str', uuid: 'str') -> 'ArvadosAPIRequest[Node]':
        """ping nodes

        Required parameters:

        * ping_secret: str

        * uuid: str
        """

    def update(self, *, uuid: 'str', assign_slot: 'bool', select: 'List') -> 'ArvadosAPIRequest[Node]':
        """Update attributes of an existing Node.

        Required parameters:

        * uuid: str --- The UUID of the Node in question.

        Optional parameters:

        * assign_slot: bool --- assign slot and hostname

        * select: List --- Attributes of the updated object to return in the response.
        """


class PipelineInstances:
    """Methods to query and manipulate Arvados pipeline instances

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def cancel(self, *, uuid: 'str') -> 'ArvadosAPIRequest[PipelineInstance]':
        """cancel pipeline_instances

        Required parameters:

        * uuid: str
        """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[PipelineInstance]':
        """Create a new PipelineInstance.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[PipelineInstance]':
        """Delete an existing PipelineInstance.

        Required parameters:

        * uuid: str --- The UUID of the PipelineInstance in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[PipelineInstance]':
        """Gets a PipelineInstance's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the PipelineInstance in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[PipelineInstanceList]':
        """List PipelineInstances.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[PipelineInstance]':
        """Update attributes of an existing PipelineInstance.

        Required parameters:

        * uuid: str --- The UUID of the PipelineInstance in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class PipelineTemplates:
    """Methods to query and manipulate Arvados pipeline templates

    .. WARNING:: Deprecated
       This resource is deprecated in the Arvados API.
    """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[PipelineTemplate]':
        """Create a new PipelineTemplate.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[PipelineTemplate]':
        """Delete an existing PipelineTemplate.

        Required parameters:

        * uuid: str --- The UUID of the PipelineTemplate in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[PipelineTemplate]':
        """Gets a PipelineTemplate's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the PipelineTemplate in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[PipelineTemplateList]':
        """List PipelineTemplates.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[PipelineTemplate]':
        """Update attributes of an existing PipelineTemplate.

        Required parameters:

        * uuid: str --- The UUID of the PipelineTemplate in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Repositories:
    """Methods to query and manipulate Arvados repositories"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Repository]':
        """Create a new Repository.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Repository]':
        """Delete an existing Repository.

        Required parameters:

        * uuid: str --- The UUID of the Repository in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Repository]':
        """Gets a Repository's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Repository in question.
        """

    def get_all_permissions(self) -> 'ArvadosAPIRequest[Repository]':
        """get_all_permissions repositories"""

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[RepositoryList]':
        """List Repositories.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Repository]':
        """Update attributes of an existing Repository.

        Required parameters:

        * uuid: str --- The UUID of the Repository in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Specimens:
    """Methods to query and manipulate Arvados specimens"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Specimen]':
        """Create a new Specimen.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Specimen]':
        """Delete an existing Specimen.

        Required parameters:

        * uuid: str --- The UUID of the Specimen in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Specimen]':
        """Gets a Specimen's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Specimen in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[SpecimenList]':
        """List Specimens.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Specimen]':
        """Update attributes of an existing Specimen.

        Required parameters:

        * uuid: str --- The UUID of the Specimen in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Sys:
    """Methods to query and manipulate Arvados sys"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """apply scheduled trash and delete operations"""


class Traits:
    """Methods to query and manipulate Arvados traits"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Trait]':
        """Create a new Trait.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Trait]':
        """Delete an existing Trait.

        Required parameters:

        * uuid: str --- The UUID of the Trait in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Trait]':
        """Gets a Trait's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Trait in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[TraitList]':
        """List Traits.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Trait]':
        """Update attributes of an existing Trait.

        Required parameters:

        * uuid: str --- The UUID of the Trait in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class UserAgreements:
    """Methods to query and manipulate Arvados user agreements"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[UserAgreement]':
        """Create a new UserAgreement.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[UserAgreement]':
        """Delete an existing UserAgreement.

        Required parameters:

        * uuid: str --- The UUID of the UserAgreement in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[UserAgreement]':
        """Gets a UserAgreement's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the UserAgreement in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[UserAgreementList]':
        """List UserAgreements.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def new(self) -> 'ArvadosAPIRequest[UserAgreement]':
        """new user_agreements"""

    def sign(self) -> 'ArvadosAPIRequest[UserAgreement]':
        """sign user_agreements"""

    def signatures(self) -> 'ArvadosAPIRequest[UserAgreement]':
        """signatures user_agreements"""

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[UserAgreement]':
        """Update attributes of an existing UserAgreement.

        Required parameters:

        * uuid: str --- The UUID of the UserAgreement in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Users:
    """Methods to query and manipulate Arvados users"""

    def activate(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """activate users

        Required parameters:

        * uuid: str
        """

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[User]':
        """Create a new User.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def current(self) -> 'ArvadosAPIRequest[User]':
        """current users"""

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """Delete an existing User.

        Required parameters:

        * uuid: str --- The UUID of the User in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """Gets a User's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the User in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[UserList]':
        """List Users.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def merge(self, *, new_owner_uuid: 'str', new_user_token: 'str', new_user_uuid: 'str', old_user_uuid: 'str', redirect_to_new_user: 'bool') -> 'ArvadosAPIRequest[User]':
        """merge users

        Required parameters:

        * new_owner_uuid: str

        Optional parameters:

        * new_user_token: str

        * new_user_uuid: str

        * old_user_uuid: str

        * redirect_to_new_user: bool --- Default False.
        """

    def setup(self, *, repo_name: 'str', send_notification_email: 'bool', user: 'Dict[str, Any]', uuid: 'str', vm_uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """setup users

        Optional parameters:

        * repo_name: str

        * send_notification_email: bool --- Default False.

        * user: Dict[str, Any]

        * uuid: str

        * vm_uuid: str
        """

    def system(self) -> 'ArvadosAPIRequest[User]':
        """system users"""

    def unsetup(self, *, uuid: 'str') -> 'ArvadosAPIRequest[User]':
        """unsetup users

        Required parameters:

        * uuid: str
        """

    def update(self, *, uuid: 'str', bypass_federation: 'bool', select: 'List') -> 'ArvadosAPIRequest[User]':
        """Update attributes of an existing User.

        Required parameters:

        * uuid: str --- The UUID of the User in question.

        Optional parameters:

        * bypass_federation: bool --- Default False.

        * select: List --- Attributes of the updated object to return in the response.
        """


class VirtualMachines:
    """Methods to query and manipulate Arvados virtual machines"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[VirtualMachine]':
        """Create a new VirtualMachine.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[VirtualMachine]':
        """Delete an existing VirtualMachine.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[VirtualMachine]':
        """Gets a VirtualMachine's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine in question.
        """

    def get_all_logins(self) -> 'ArvadosAPIRequest[VirtualMachine]':
        """get_all_logins virtual_machines"""

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[VirtualMachineList]':
        """List VirtualMachines.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def logins(self, *, uuid: 'str') -> 'ArvadosAPIRequest[VirtualMachine]':
        """logins virtual_machines

        Required parameters:

        * uuid: str
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[VirtualMachine]':
        """Update attributes of an existing VirtualMachine.

        Required parameters:

        * uuid: str --- The UUID of the VirtualMachine in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """


class Vocabularies:
    """Methods to query and manipulate Arvados vocabularies"""

    def get(self) -> 'ArvadosAPIRequest[Dict[str, Any]]':
        """Get vocabulary definition"""


class Workflows:
    """Methods to query and manipulate Arvados workflows"""

    def create(self, *, cluster_id: 'str', ensure_unique_name: 'bool', select: 'List') -> 'ArvadosAPIRequest[Workflow]':
        """Create a new Workflow.

        Optional parameters:

        * cluster_id: str --- Create object on a remote federated cluster instead of the current one.

        * ensure_unique_name: bool --- Adjust name to ensure uniqueness instead of returning an error on (owner_uuid, name) collision. Default False.

        * select: List --- Attributes of the new object to return in the response.
        """

    def delete(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Workflow]':
        """Delete an existing Workflow.

        Required parameters:

        * uuid: str --- The UUID of the Workflow in question.
        """

    def get(self, *, uuid: 'str') -> 'ArvadosAPIRequest[Workflow]':
        """Gets a Workflow's metadata by UUID.

        Required parameters:

        * uuid: str --- The UUID of the Workflow in question.
        """

    def list(self, *, bypass_federation: 'bool', cluster_id: 'str', count: 'str', distinct: 'bool', filters: 'List', limit: 'int', offset: 'int', order: 'List', select: 'List', where: 'Dict[str, Any]') -> 'ArvadosAPIRequest[WorkflowList]':
        """List Workflows.

        Optional parameters:

        * bypass_federation: bool --- bypass federation behavior, list items from local instance database only

        * cluster_id: str --- List objects on a remote federated cluster instead of the current one.

        * count: str --- Default 'exact'.

        * distinct: bool --- Default False.

        * filters: List

        * limit: int --- Default 100.

        * offset: int --- Default 0.

        * order: List

        * select: List --- Attributes of each object to return in the response.

        * where: Dict[str, Any]
        """

    def update(self, *, uuid: 'str', select: 'List') -> 'ArvadosAPIRequest[Workflow]':
        """Update attributes of an existing Workflow.

        Required parameters:

        * uuid: str --- The UUID of the Workflow in question.

        Optional parameters:

        * select: List --- Attributes of the updated object to return in the response.
        """



class ArvadosAPIRequest(googleapiclient.http.HttpRequest, Generic[ST]):
    """Generic API request object

    When you call an API method in the Arvados Python SDK, it returns a
    request object. You usually call `execute()` on this object to submit the
    request to your Arvados API server and retrieve the response. `execute()`
    will return the type of object annotated in the subscript of
    `ArvadosAPIRequest`.
    """

    def execute(self, http: Optional[httplib2.Http]=None, num_retries: int=0) -> ST:
        """Execute this request and return the response

        Arguments:

        * http: httplib2.Http | None --- The HTTP client object to use to
          execute the request. If not specified, uses the HTTP client object
          created with the API client object.

        * num_retries: int --- The maximum number of times to retry this
          request if the server returns a retryable failure. The API client
          object also has a maximum number of retries specified when it is
          instantiated (see `arvados.api.api_client`). This request is run
          with the larger of that number and this argument. Default 0.
        """


class ArvadosAPIClient(googleapiclient.discovery.Resource):

    def api_client_authorizations(self) -> 'ApiClientAuthorizations':
        """Return an instance of `ApiClientAuthorizations` to call methods via this client"""


    def api_clients(self) -> 'ApiClients':
        """Return an instance of `ApiClients` to call methods via this client"""


    def authorized_keys(self) -> 'AuthorizedKeys':
        """Return an instance of `AuthorizedKeys` to call methods via this client"""


    def collections(self) -> 'Collections':
        """Return an instance of `Collections` to call methods via this client"""


    def configs(self) -> 'Configs':
        """Return an instance of `Configs` to call methods via this client"""


    def container_requests(self) -> 'ContainerRequests':
        """Return an instance of `ContainerRequests` to call methods via this client"""


    def containers(self) -> 'Containers':
        """Return an instance of `Containers` to call methods via this client"""


    def groups(self) -> 'Groups':
        """Return an instance of `Groups` to call methods via this client"""


    def humans(self) -> 'Humans':
        """Return an instance of `Humans` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def job_tasks(self) -> 'JobTasks':
        """Return an instance of `JobTasks` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def jobs(self) -> 'Jobs':
        """Return an instance of `Jobs` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def keep_disks(self) -> 'KeepDisks':
        """Return an instance of `KeepDisks` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def keep_services(self) -> 'KeepServices':
        """Return an instance of `KeepServices` to call methods via this client"""


    def links(self) -> 'Links':
        """Return an instance of `Links` to call methods via this client"""


    def logs(self) -> 'Logs':
        """Return an instance of `Logs` to call methods via this client"""


    def nodes(self) -> 'Nodes':
        """Return an instance of `Nodes` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def pipeline_instances(self) -> 'PipelineInstances':
        """Return an instance of `PipelineInstances` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def pipeline_templates(self) -> 'PipelineTemplates':
        """Return an instance of `PipelineTemplates` to call methods via this client

        .. WARNING:: Deprecated
           This resource is deprecated in the Arvados API.
        """


    def repositories(self) -> 'Repositories':
        """Return an instance of `Repositories` to call methods via this client"""


    def specimens(self) -> 'Specimens':
        """Return an instance of `Specimens` to call methods via this client"""


    def sys(self) -> 'Sys':
        """Return an instance of `Sys` to call methods via this client"""


    def traits(self) -> 'Traits':
        """Return an instance of `Traits` to call methods via this client"""


    def user_agreements(self) -> 'UserAgreements':
        """Return an instance of `UserAgreements` to call methods via this client"""


    def users(self) -> 'Users':
        """Return an instance of `Users` to call methods via this client"""


    def virtual_machines(self) -> 'VirtualMachines':
        """Return an instance of `VirtualMachines` to call methods via this client"""


    def vocabularies(self) -> 'Vocabularies':
        """Return an instance of `Vocabularies` to call methods via this client"""


    def workflows(self) -> 'Workflows':
        """Return an instance of `Workflows` to call methods via this client"""

