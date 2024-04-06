"""
The HEA Server Organization provides ...
"""
import asyncio

from aiohttp import hdrs
from heaobject.error import DeserializeException
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaserver.service.appproperty import HEA_DB
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.heaobjectsupport import type_to_resource_url, new_heaobject_from_type
from heaserver.service import response, client
from heaobject.organization import Organization
from heaobject.account import AWSAccount
from heaobject.volume import AWSFileSystem, Volume
from heaobject.person import Person
from heaobject.user import NONE_USER
from collections.abc import AsyncGenerator
from yarl import URL
from asyncio import gather
from itertools import chain
from functools import partial
import logging

_logger = logging.getLogger(__name__)

MONGODB_ORGANIZATION_COLLECTION = 'organizations'


@routes.get('/organizationsping')
async def ping(request: web.Request) -> web.Response:
    """
    Checks if this service is running.

    :param request: the HTTP request.
    :return: the HTTP response.
    """
    return await mongoservicelib.ping(request)


@routes.get('/organizations/{id}')
@action('heaserver-organizations-organization-get-properties', rel='hea-properties')
@action('heaserver-organizations-organization-get-open-choices', rel='hea-opener-choices', path='organizations/{id}/opener')
@action('heaserver-organizations-organization-duplicate', rel='hea-duplicator', path='organizations/{id}/duplicator')
@action('heaserver-organizations-organization-get-self', rel='self', path='organizations/{id}')
@action('heaserver-organizations-organization-get-memberseditor', rel='hearesource-organizations-memberseditor', path='organizations/{id}/memberseditor')
async def get_organization(request: web.Request) -> web.Response:
    """
    Gets the organization with the specified id.
    :param request: the HTTP request.
    :return: the requested organization or Not Found.
    ---
    summary: A specific organization.
    tags:
        - heaserver-organizations-get-organization
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_ORGANIZATION_COLLECTION)

@routes.get('/organizations/{id}/memberseditor')
@action('heaserver-organizations-organization-edit-membership', rel='hea-properties')
@action('heaserver-organizations-organization-get-members', rel='application/x.person', path='organizations/{id}/members/')
async def get_organization_memberseditor(request: web.Request) -> web.Response:
    """
    Gets the organization with the specified id.
    :param request: the HTTP request.
    :return: the requested organization or Not Found.
    ---
    summary: A specific organization.
    tags:
        - heaserver-organizations-get-organization
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_ORGANIZATION_COLLECTION)

@routes.put('/organizations/{id}/memberseditor')
async def put_organization_memberseditor(request: web.Request) -> web.Response:
    """
    Updates the organization with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
     ---
    summary: Organization updates
    tags:
        - heaserver-organizations-put-organization
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated organization object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Max"
                  },
                  {
                    "name": "invites",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "aws_account_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "principal_investigator_id",
                    "value": "1",
                  },
                  {
                    "name": "admin_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "manager_ids",
                    "value": ["4321", "8765"]
                  },
                  {
                    "name": "member_ids",
                    "value": ["1", "2"]
                  },
                  {
                  "name": "id",
                  "value": "666f6f2d6261722d71757578"
                  },
                  {
                  "name": "type",
                  "value": "heaobject.organization.Organization"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Max",
                "invites": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.organization.Organization",
                "version": null,
                "aws_account_ids": ["1234", "5678"],
                "principal_investigator_id": "1",
                "admin_ids": ["1234", "5678"],
                "manager_ids": ["4321", "8765"],
                "member_ids": ["1", "2"]
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_ORGANIZATION_COLLECTION, Organization)

@routes.get('/organizations/byname/{name}')
@action('heaserver-organizations-organization-get-self', rel='self', path='organizations/{id}')
async def get_organization_by_name(request: web.Request) -> web.Response:
    """
    Gets the organization with the specified id.
    :param request: the HTTP request.
    :return: the requested organization or Not Found.
    ---
    summary: A specific organization, by name.
    tags:
        - heaserver-organizations-get-organization-by-name
    parameters:
      - name: name
        in: path
        required: true
        description: The name of the organization.
        schema:
          type: string
        examples:
          example:
            summary: An organization name
            value: Bob

    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations')
@routes.get('/organizations/')
@action('heaserver-organizations-organization-get-properties', rel='hea-properties')
@action('heaserver-organizations-organization-get-open-choices', rel='hea-opener-choices', path='organizations/{id}/opener')
@action('heaserver-organizations-organization-duplicate', rel='hea-duplicator', path='organizations/{id}/duplicator')
@action('heaserver-organizations-organization-get-self', rel='self', path='organizations/{id}')
@action('heaserver-organizations-organization-get-memberseditor', rel='hearesource-organizations-memberseditor', path='organizations/{id}/memberseditor')
async def get_all_organizations(request: web.Request) -> web.Response:
    """
    Gets all organizations.
    :param request: the HTTP request.
    :return: all organizations.
    ---
    summary: All organizations.
    tags:
        - heaserver-organizations-get-all-organizations
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    logger = logging.getLogger(__name__)
    logger.debug('Getting all organizations...')
    sort = request.query.get('sort', None)
    if sort is None:
        sort_int = None
    else:
        if sort != 'asc' and sort != 'desc':
            return response.status_bad_request(f'sort may be asc or desc but was {sort}')
        sort_int = 1 if sort == 'asc' else -1
    get_all = partial(mongoservicelib.get_all, request, MONGODB_ORGANIZATION_COLLECTION)
    if sort_int is not None:
        get_all = partial(get_all, sort={'display_name': sort_int})
    return await get_all()


@routes.get('/organizations/{id}/duplicator')
@action(name='heaserver-organizations-organization-duplicate-form', path='organizations/{id}')
async def get_organization_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested organization.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested organization was not found.
    """
    return await mongoservicelib.get(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.post('/organizations/duplicator')
async def post_organization_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided organization for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.post('/organizations')
@routes.post('/organizations/')
async def post_organization(request: web.Request) -> web.Response:
    """
    Posts the provided organization.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Organization creation
    tags:
        - heaserver-organizations-post-organization
    requestBody:
      description: A new organization object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Joe"
                  },
                  {
                    "name": "invites",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "joe"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "aws_account_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "principal_investigator_id",
                    "value": "1",
                  },
                  {
                    "name": "admin_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "manager_ids",
                    "value": ["4321", "8765"]
                  },
                  {
                    "name": "member_ids",
                    "value": ["1", "2"]
                  },
                  {
                  "name": "type",
                  "value": "heaobject.organization.Organization"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Joe",
                "invited": [],
                "modified": null,
                "name": "joe",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.organization.Organization",
                "version": null,
                "aws_account_ids": ["1234", "5678"],
                "principal_investigator_id": "1",
                "admin_ids": ["4321", "8765"],
                "manager_ids": ["4321", "8765"],
                "member_ids": ["1", "2"]
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.put('/organizations/{id}')
async def put_organization(request: web.Request) -> web.Response:
    """
    Updates the organization with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
     ---
    summary: Organization updates
    tags:
        - heaserver-organizations-put-organization
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated organization object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Max"
                  },
                  {
                    "name": "invites",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "aws_account_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "principal_investigator_id",
                    "value": "1",
                  },
                  {
                    "name": "admin_ids",
                    "value": ["1234", "5678"]
                  },
                  {
                    "name": "manager_ids",
                    "value": ["4321", "8765"]
                  },
                  {
                    "name": "member_ids",
                    "value": ["1", "2"]
                  },
                  {
                  "name": "id",
                  "value": "666f6f2d6261722d71757578"
                  },
                  {
                  "name": "type",
                  "value": "heaobject.organization.Organization"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Organization example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Max",
                "invites": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.organization.Organization",
                "version": null,
                "aws_account_ids": ["1234", "5678"],
                "principal_investigator_id": "1",
                "admin_ids": ["1234", "5678"],
                "manager_ids": ["4321", "8765"],
                "member_ids": ["1", "2"]
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    sub = request.headers.get(SUB, NONE_USER)
    old = await mongoservicelib.get_dict(request, MONGODB_ORGANIZATION_COLLECTION)
    if old is not None:
        old_org = Organization()
        old_org.from_dict(old)
        try:
            new_org = await new_heaobject_from_type(request, Organization)
        except DeserializeException as e:
            return response.status_bad_request(str(e))
        if old_org.admin_ids != new_org.admin_ids and \
            sub != old_org.owner and \
            sub != old_org.principal_investigator_id and \
            sub not in old_org.admin_ids:
            return response.status_bad_request('You have insufficient permissions to change the administrator list')
        if old_org.manager_ids != new_org.manager_ids and \
            sub != old_org.owner and \
            sub != old_org.principal_investigator_id and \
            sub not in old_org.manager_ids and \
            sub not in old_org.admin_ids:
            return response.status_bad_request('You have insufficient permissions to change the manager list')

    return await mongoservicelib.put(request, MONGODB_ORGANIZATION_COLLECTION, Organization)


@routes.delete('/organizations/{id}')
async def delete_organization(request: web.Request) -> web.Response:
    """
    Deletes the organization with the specified id.
    :param request: the HTTP request.
    :return: A Response object with a status of No Content or Not Found.
    ---
    summary: Organization deletion
    tags:
        - heaserver-organizations-delete-organization
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_ORGANIZATION_COLLECTION)


@routes.get('/organizations/{id}/opener')
@action('heaserver-organizations-organization-open-awsaccounts', rel=f'hea-opener hea-context-aws hea-default {AWSAccount.get_mime_type()}', path='organizations/{id}/awsaccounts')
async def get_organization_opener(request: web.Request) -> web.Response:
    """

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Organization opener choices
    tags:
        - heaserver-organizations-organization-get-open-choices
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.opener(request, MONGODB_ORGANIZATION_COLLECTION)

@routes.get('/organizations/{id}/volumes')
@routes.get('/organizations/{id}/volumes/')
async def get_organization_volumes(request: web.Request) -> web.Response:
    result = [v.to_dict() async for v in _get_organization_volumes(request)]
    return await response.get_all(request, result)


@routes.get('/organizations/{id}/awsaccounts')
@routes.get('/organizations/{id}/awsaccounts/')
@action('heaserver-organizations-awsaccount-get-open-choices', rel='hea-opener-choices', path='awsaccounts/{id}/opener')
@action('heaserver-organizations-awsaccount-get-self', rel='self', path='awsaccounts/{id}')
async def get_organization_aws_accounts(request: web.Request) -> web.Response:
    """

    :param request: the HTTP Request.
    :return: a Response object with a status code of 200.
    ---
    summary: An organization's AWS accounts.
    tags:
        - heaserver-organizations-organization-get-aws-accounts
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    sub = request.headers.get(SUB, NONE_USER)
    org_dict = await request.app[HEA_DB].get(request, MONGODB_ORGANIZATION_COLLECTION, var_parts='id', sub=sub)
    if org_dict is None:
        return response.status_not_found()
    org = Organization()
    org.from_dict(org_dict)
    headers = {SUB: sub or '',
               hdrs.AUTHORIZATION: request.headers.get(hdrs.AUTHORIZATION, '')} if SUB in request.headers else None

    aws_account_url = await type_to_resource_url(request, AWSAccount, file_system_type_or_type_name=AWSFileSystem)
    if aws_account_url is None:
        raise ValueError('No AWSAccount service registered')
    aws_account_ids = org.aws_account_ids
    query = [('account_id', account_id) for account_id in aws_account_ids]
    if aws_account_ids:
        result = [a.to_dict() async for a in client.get_all(request.app, URL(aws_account_url).with_path('awsaccounts').with_query(query), AWSAccount, headers=headers)]
    else:
        result = []
    return await response.get_all(request, result)


@routes.get('/organizations/{id}/members')
@routes.get('/organizations/{id}/members/')
@action('heaserver-organizations-member-get-self', rel='self', path='people/{id}')
async def get_organization_members(request: web.Request) -> web.Response:
    """
    Gets the S3 buckets in the provided account.

    :param request: the HTTP Request.
    :return: a Response object with status code 200 and a body containing either an empty list or a list of buckets.
    ---
    summary: the buckets in an AWS account.
    tags:
        - heaserver-get-members
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
        '200':
            $ref: '#/components/responses/200'
    """
    sub = request.headers.get(SUB)
    headers = {SUB: sub or '',
               hdrs.AUTHORIZATION: request.headers.get(hdrs.AUTHORIZATION, '')} if SUB in request.headers else None

    org_dict = await request.app[HEA_DB].get(request, MONGODB_ORGANIZATION_COLLECTION, var_parts='id', sub=sub)
    if org_dict is None:
        return response.status_not_found()
    org = Organization()
    org.from_dict(org_dict)
    org_members = {k: None for k in chain([org.principal_investigator_id] if org.principal_investigator_id is not None else [],
                                          org.admin_ids if org.admin_ids else [],
                                          org.manager_ids if org.manager_ids else [],
                                          org.member_ids if org.member_ids else [])}

    url = URL(await type_to_resource_url(request=request, type_or_type_name=Person))

    def get_one_member_dict(m):
        _logger.debug("People names %s returning", m.display_name if m is not None else None)
        return m.to_dict()

    people_dictionaries = [get_one_member_dict(p_obj) for p_obj in await gather(
        *[client.get(app=request.app, url=url / m_id, type_or_obj=Person, headers=headers) for m_id in org_members])
                           if p_obj is not None]

    return await response.get_all(request, people_dictionaries)


def main() -> None:
    config = init_cmd_line(description='a service for managing organization information for research laboratories and other research groups',
                           default_port=8087)
    start(package_name='heaserver-organizations', db=mongo.MongoManager, wstl_builder_factory=builder_factory(__package__), config=config)

async def _get_organization_volumes(request: web.Request) -> AsyncGenerator[Volume, None]:
    sub = request.headers.get(SUB)
    org_dict = await request.app[HEA_DB].get(request, MONGODB_ORGANIZATION_COLLECTION, var_parts='id', sub=sub)
    if org_dict is None:
        raise response.status_not_found()
    org = Organization()
    org.from_dict(org_dict)
    headers = {SUB: sub or '',
               hdrs.AUTHORIZATION: request.headers.get(hdrs.AUTHORIZATION, '')} if SUB in request.headers else None


    volume_url = await type_to_resource_url(request, Volume)
    if volume_url is None:
        raise ValueError('No Volume service registered')
    get_volumes_url = URL(volume_url) / 'byfilesystemtype' / AWSFileSystem.get_type_name()

    aws_account_url = await type_to_resource_url(request, AWSAccount, file_system_type_or_type_name=AWSFileSystem)
    if aws_account_url is None:
        raise ValueError('No AWSAccount service registered')

    async def get_one(volume_id):
        return await client.get(request.app, URL(aws_account_url) / volume_id / 'awsaccounts' / 'me', AWSAccount, headers=headers)
    async for v in client.get_all(request.app, get_volumes_url, Volume, headers=headers):
        if await get_one(v.id) is not None:
            yield v
