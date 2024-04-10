"""
The HEA Server Buckets Microservice provides ...
"""
import logging

from heaobject.data import AWSS3FileObject
from heaserver.service import response, client, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import awsservicelib, aws
from heaserver.service.wstl import builder_factory, action
from heaobject.folder import AWSS3BucketItem, Folder, AWSS3Folder
from heaobject.project import AWSS3Project
from heaobject.volume import AWSFileSystem
from heaobject.bucket import AWSBucket
from heaobject.error import DeserializeException
from heaobject.root import Tag, ShareImpl, Permission
from heaobject.activity import Status
from heaobject.user import NONE_USER, AWS_USER, ALL_USERS
from heaserver.service.appproperty import HEA_CACHE
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.heaobjectsupport import new_heaobject_from_type, type_to_resource_url
from heaserver.service.sources import AWS_S3
from heaserver.service.messagebroker import publish_desktop_object, publisher_cleanup_context_factory
from heaserver.service.activity import DesktopObjectActionLifecycle
from botocore.exceptions import ClientError as BotoClientError
import asyncio
from typing import Generator, Any
from yarl import URL
from mypy_boto3_s3.client import S3Client
from functools import partial
from aiohttp.client_exceptions import ClientError, ClientResponseError
from datetime import datetime
from mypy_boto3_s3.type_defs import TagTypeDef

MONGODB_BUCKET_COLLECTION = 'buckets'


@routes.get('/volumes/{volume_id}/buckets/{id}')
@action('heaserver-buckets-bucket-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='volumes/{volume_id}/buckets/{id}/opener')
@action(name='heaserver-buckets-bucket-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-buckets-bucket-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='volumes/{volume_id}/buckets/{id}/creator')
@action(name='heaserver-buckets-bucket-get-trash', rel='hea-trash hea-context-menu', path='volumes/{volume_id}/awss3trash')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='volumes/{volume_id}/buckets/{id}')
@action(name='heaserver-buckets-bucket-get-volume', rel='hea-volume', path='volumes/{volume_id}')
@action(name='heaserver-buckets-bucket-get-awsaccount', rel='hea-account', path='volumes/{volume_id}/awsaccounts/me')
@action(name='heaserver-buckets-bucket-get-uploader', rel='hea-uploader', path='volumes/{volume_id}/buckets/{id}/uploader')
async def get_bucket(request: web.Request) -> web.Response:
    """
    Gets the bucket with the specified id.
    :param request: the HTTP request.
    :return: the requested bucket or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """

    return await _get_bucket(request=request)


@routes.get('/volumes/{volume_id}/buckets/byname/{bucket_name}')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='volumes/{volume_id}/buckets/{id}')
@action(name='heaserver-buckets-bucket-get-volume', rel='hea-volume', path='volumes/{volume_id}')
@action(name='heaserver-buckets-bucket-get-awsaccount', rel='hea-account', path='volumes/{volume_id}/awsaccounts/me')
async def get_bucket_by_name(request: web.Request) -> web.Response:
    """
    Gets the bucket with the specified name.
    :param request: the HTTP request.
    :return: the requested bucket or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: bucket_name
          in: path
          required: true
          description: The name of the bucket to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: Name of the bucket
              value: hci-foundation
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_bucket(request=request)


@routes.get('/volumes/{volume_id}/buckets/{id}/opener')
@action('heaserver-buckets-bucket-open-content', rel=f'hea-opener hea-context-aws hea-default {Folder.get_mime_type()}',
        path='volumes/{volume_id}/buckets/{id}/awss3folders/root/items/')
async def get_bucket_opener(request: web.Request) -> web.Response:
    """
    Gets bucket opener choices.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Bucket opener choices
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _bucket_opener(request)


@routes.get('/volumes/{volume_id}/buckets/{id}/creator')
@action('heaserver-buckets-bucket-create-folder', rel='hea-creator hea-default application/x.folder',
        path='volumes/{volume_id}/buckets/{id}/newfolder')
@action('heaserver-buckets-bucket-create-project', rel='hea-creator hea-default application/x.project',
        path='volumes/{volume_id}/buckets/{id}/newproject')
async def get_bucket_creator(request: web.Request) -> web.Response:
    """
    Gets bucket creator choices.

    :param request: the HTTP Request.
    :return: A Response object with a status of Multiple Choices or Not Found.
    ---
    summary: Bucket creator choices
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '300':
        $ref: '#/components/responses/300'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _bucket_opener(request)

@routes.get('/volumes/{volume_id}/buckets/{id}/uploader')
@routes.get('/volumes/{volume_id}/buckets/{id}/uploader/')
@action('heaserver-buckets-bucket-get-upload-form')
async def get_folder_uploader_form(request: web.Request) -> web.Response:
    """
    Gets blank form for uploading to Bucket

    :param request: the HTTP request. Required.
    :return: a blank form for uploading a Bucket item or Not Found if the requested item does not
    exist.
    """
    return await _get_bucket(request)


@routes.get('/volumes/{volume_id}/buckets/{id}/newfolder')
@routes.get('/volumes/{volume_id}/buckets/{id}/newfolder/')
@action('heaserver-buckets-bucket-new-folder-form')
async def get_new_folder_form(request: web.Request) -> web.Response:
    """
    Gets form for creating a new folder within this bucket.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_bucket(request)

@routes.get('/volumes/{volume_id}/buckets/{id}/newproject')
@routes.get('/volumes/{volume_id}/buckets/{id}/newproject/')
@action('heaserver-buckets-bucket-new-project-form')
async def get_new_project_form(request: web.Request) -> web.Response:
    """
    Gets form for creating a new project within this bucket.

    :param request: the HTTP request. Required.
    :return: the current project, with a template for creating a child project or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _get_bucket(request)


@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newfolder')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newfolder/')
async def post_new_folder(request: web.Request) -> web.Response:
    """
    Gets form for creating a new folder within this bucket.

    :param request: the HTTP request. Required.
    :return: the current folder, with a template for creating a child folder or Not Found if the requested item does not
    exist.
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    requestBody:
        description: A new folder.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Folder example
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3Folder"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "display_name": "Joe",
                    "type": "heaobject.folder.AWSS3Folder"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    folder_url = await type_to_resource_url(request, AWSS3Folder, file_system_type_or_type_name=AWSFileSystem)
    if folder_url is None:
        raise ValueError('No AWSS3Folder service registered')
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    resource_base = str(URL(folder_url) / volume_id / 'buckets' / bucket_id / 'awss3folders' / 'root' / 'newfolder')
    folder = await new_heaobject_from_type(request, type_=AWSS3Folder)
    try:
        id_ = await client.post(request.app, resource_base, data=folder, headers=headers)
        return await response.post(request, id_, resource_base)
    except ClientResponseError as e:
        return response.status_generic_error(status=e.status, body=e.message)
    except ClientError as e:
        return response.status_generic(status=500, body=str(e))

@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newproject')
@routes.post('/volumes/{volume_id}/buckets/{bucket_id}/newproject/')
async def post_new_project(request: web.Request) -> web.Response:
    """
    Gets form for creating a new project within this bucket.

    :param request: the HTTP request. Required.
    :return: the current project, with a template for creating a child project or Not Found if the requested item does not
    exist.
    ---
    summary: A project.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    requestBody:
        description: A new project.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Project example
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "type",
                        "value": "heaobject.project.AWSS3Project"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "display_name": "Joe",
                    "type": "heaobject.project.AWSS3Project"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['bucket_id']
    project_url = await type_to_resource_url(request, AWSS3Project, file_system_type_or_type_name=AWSFileSystem)
    if project_url is None:
        raise ValueError('No AWSS3Project service registered')
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None
    resource_base = str(URL(project_url) / volume_id / 'buckets' / bucket_id / 'awss3projects')
    project = await new_heaobject_from_type(request, type_=AWSS3Project)
    try:
        id_ = await client.post(request.app, resource_base, data=project, headers=headers)
        return await response.post(request, id_, resource_base)
    except ClientResponseError as e:
        return response.status_generic_error(status=e.status, body=e.message)
    except ClientError as e:
        return response.status_generic(status=500, body=str(e))


@routes.post('/volumes/{volume_id}/buckets/{id}/uploader')
@routes.post('/volumes/{volume_id}/buckets/{id}/uploader/')
async def post_bucket_uploader(request: web.Request) -> web.Response:
    """
    :param request:
    :return:
    ---
    summary: A folder.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - name: bucket_id
          in: path
          required: true
          description: The id of the bucket.
          schema:
            type: string
          examples:
            example:
              summary: A bucket id
              value: my-bucket
    requestBody:
        description: Upload file to bucket.
        required: true
        content:
            application/vnd.collection+json:
              schema:
                type: object
              examples:
                example:
                  summary: Folder example
                  value: {
                    "template": {
                      "data": [
                      {
                        "name": "display_name",
                        "value": "Bob"
                      },
                      {
                        "name": "type",
                        "value": "heaobject.folder.AWSS3ItemInFolder"
                      }]
                    }
                  }
            application/json:
              schema:
                type: object
              examples:
                example:
                  summary: Item example
                  value: {
                    "display_name": "Joe",
                    "type": "heaobject.folder.AWSS3ItemInFolder",
                    "folder_id": "root"
                  }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    volume_id = request.match_info['volume_id']
    bucket_id = request.match_info['id']

    folder_url = await type_to_resource_url(request, AWSS3Folder, file_system_type_or_type_name=AWSFileSystem)
    if folder_url is None:
        raise ValueError('No AWSS3Folder service registered')
    headers = {SUB: request.headers[SUB]} if SUB in request.headers else None

    resource_base = str(URL(folder_url) / volume_id / 'buckets' / bucket_id / 'awss3folders' / 'root' / 'uploader')
    logging.info(f"This is the url to reach the folder service from the bucket\n{resource_base}")
    # posting to root of bucket with file template
    file = await new_heaobject_from_type(request, type_=AWSS3FileObject)
    try:
        location_url = await client.post(request.app, resource_base, data=file, headers=headers)
        content_rb = location_url.removeprefix(request.app[appproperty.HEA_COMPONENT] + "/")\
            .removesuffix("/content") if location_url else ""
        content_id = "content" if content_rb else None
        return await response.post(request=request, result=content_id, resource_base=content_rb)
    except ClientResponseError as e:
        return response.status_generic(status=e.status, body=str(e))
    except ClientError as e:
        return response.status_generic(status=500, body=str(e))



@routes.get('/volumes/{volume_id}/buckets')
@routes.get('/volumes/{volume_id}/buckets/')
@action('heaserver-buckets-bucket-get-open-choices', rel='hea-opener-choices hea-context-menu',
        path='volumes/{volume_id}/buckets/{id}/opener')
@action(name='heaserver-buckets-bucket-get-properties', rel='hea-properties hea-context-menu')
@action(name='heaserver-buckets-bucket-get-create-choices', rel='hea-creator-choices hea-context-menu',
        path='volumes/{volume_id}/buckets/{id}/creator')
@action(name='heaserver-buckets-bucket-get-trash', rel='hea-trash hea-context-menu', path='volumes/{volume_id}/awss3trash')
@action(name='heaserver-buckets-bucket-get-self', rel='self', path='volumes/{volume_id}/buckets/{id}')
@action(name='heaserver-buckets-bucket-get-uploader', rel='hea-uploader', path='volumes/{volume_id}/buckets/{id}/uploader')
async def get_all_buckets(request: web.Request) -> web.Response:
    """
    Gets all buckets.
    :param request: the HTTP request.
    :return: all buckets.
    ---
    summary: get all buckets for a hea-volume associate with account.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    sub = request.headers.get(SUB, NONE_USER)
    volume_id = request.match_info.get("volume_id", None)
    if not volume_id:
        return web.HTTPBadRequest(body="volume_id is required")
    loop = asyncio.get_running_loop()
    cache_key = (sub, volume_id, None, 'actual')
    bucket_dict_list = request.app[HEA_CACHE].get(cache_key)
    if not bucket_dict_list:
        async with DesktopObjectActionLifecycle(request=request,
                                                    code='hea-get',
                                                    description=f'Getting all buckets',
                                                    activity_cb=publish_desktop_object) as activity:
            async with aws.S3ClientContext(request=request, volume_id=volume_id) as s3_client:
                try:
                    resp = await loop.run_in_executor(None, s3_client.list_buckets)
                    async_bucket_list = []
                    for bucket in resp['Buckets']:
                        bucket_ = __get_bucket(volume_id=volume_id, bucket_name=bucket["Name"],
                                            s3_client=s3_client, cache=request.app[HEA_CACHE],
                                            creation_date=bucket['CreationDate'], sub=request.headers.get(SUB, NONE_USER))
                        if bucket_ is not None:
                            async_bucket_list.append(bucket_)

                    buck_list = await asyncio.gather(*async_bucket_list)
                    activity.new_object_uri = f'volumes/{volume_id}/buckets/'
                    activity.new_object_type_name = AWSBucket.get_type_name()
                    activity.new_volume_id = volume_id
                except BotoClientError as e:
                    activity.status = Status.FAILED
                    return awsservicelib.handle_client_error(e)
                else:
                    bucket_dict_list = [buck.to_dict() for buck in buck_list if buck is not None]
                    request.app[HEA_CACHE][cache_key] = bucket_dict_list
                    for buck in bucket_dict_list:
                        request.app[HEA_CACHE][(sub, volume_id, buck['id'], 'head')] = buck['id']
                        request.app[HEA_CACHE][(sub, volume_id, buck['id'], 'actual')] = buck
    return await response.get_all(request, bucket_dict_list, permissions=[buck.get_permissions(sub) for buck in buck_list])


@routes.get('/volumes/{volume_id}/bucketitems')
@routes.get('/volumes/{volume_id}/bucketitems/')
@action(name='heaserver-buckets-item-get-actual', rel='hea-actual', path='{+actual_object_uri}')
@action(name='heaserver-buckets-item-get-volume', rel='hea-volume', path='volumes/{volume_id}')
async def get_all_bucketitems(request: web.Request) -> web.Response:
    """
    Gets all buckets.
    :param request: the HTTP request.
    :return: all buckets.
    ---
    summary: get all bucket items for a hea-volume associate with account.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    volume_id = request.match_info.get("volume_id", None)
    sub = request.headers.get(SUB, NONE_USER)

    async with DesktopObjectActionLifecycle(request=request,
                                                code='hea-get',
                                                description=f'Getting all buckets',
                                                activity_cb=publish_desktop_object) as activity:
        cache_key = (sub, volume_id, None, 'items')
        result = request.app[HEA_CACHE].get(cache_key)
        if not result:
            async with aws.S3ClientContext(request=request, volume_id=volume_id) as s3_client:
                try:
                    resp = await asyncio.get_running_loop().run_in_executor(None, s3_client.list_buckets)

                    def bucket_items() -> Generator[AWSS3BucketItem, None, None]:
                        bucket_url = URL('volumes') / volume_id / 'buckets'
                        bucket_type = AWSBucket.get_type_name()

                        for bucket in resp['Buckets']:
                            bucket_item = AWSS3BucketItem()
                            bucket_name = bucket['Name']
                            bucket_item.bucket_id = bucket_name
                            creation_date = bucket['CreationDate']
                            bucket_item.modified = creation_date
                            bucket_item.created = creation_date
                            bucket_item.actual_object_type_name = bucket_type
                            bucket_item.actual_object_id = bucket_name
                            bucket_item.actual_object_uri = str(bucket_url / bucket_name)
                            bucket_item.source = AWS_S3
                            bucket_item.source_detail = AWS_S3
                            yield bucket_item
                    result = [buck.to_dict() for buck in bucket_items()]
                    activity.new_object_uri = f'volumes/{volume_id}/bucketitems/'
                    activity.new_object_type_name = AWSS3BucketItem.get_type_name()
                    activity.new_volume_id = volume_id
                    request.app[HEA_CACHE][cache_key] = result
                    for buck in result:
                        request.app[HEA_CACHE][(sub, volume_id, buck['id'], 'head')] = buck['id']
                except BotoClientError as e:
                    activity.status = Status.FAILED
                    return awsservicelib.handle_client_error(e)
        return await response.get_all(request, result)


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/{id}')
async def get_bucket_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'DELETE', 'HEAD', 'OPTIONS', 'PUT'])


@routes.route('OPTIONS', '/volumes/{volume_id}/buckets')
@routes.route('OPTIONS', '/volumes/{volume_id}/buckets/')
async def get_buckets_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'HEAD', 'POST', 'OPTIONS'])


@routes.route('OPTIONS', '/volumes/{volume_id}/bucketitems')
@routes.route('OPTIONS', '/volumes/{volume_id}/bucketitems/')
async def get_bucketitems_options(request: web.Request) -> web.Response:
    """
    ---
    summary: Allowed HTTP methods.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the volume to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            text/plain:
                schema:
                    type: string
                    example: "200: OK"
      '403':
        $ref: '#/components/responses/403'
      '404':
        $ref: '#/components/responses/404'
    """
    return await response.get_options(request, ['GET', 'HEAD', 'OPTIONS'])


@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok(None)


@routes.post('/volumes/{volume_id}/buckets')
@routes.post('/volumes/{volume_id}/buckets/')
async def post_bucket(request: web.Request) -> web.Response:
    """
    Posts the provided bucket.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    ---
    summary: Bucket Creation
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    requestBody:
      description: Attributes of new Bucket.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
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
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "invited",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
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
                    "name": "encrypted",
                    "value": true
                  },
                  {
                    "name": "versioned",
                    "value": false
                  },
                  {
                    "name": "locked",
                    "value": false
                  },
                  {
                    "name": "tags",
                    "value": []
                  },
                  {
                    "name": "region",
                    "value": us-west-2
                  },
                  {
                    "name": "permission_policy",
                    "value": null
                  },
                  {
                    "name": "type",
                    "value": "heaobject.bucket.AWSBucket"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": "This is a description",
                "display_name": "hci-test-bucket",
                "invited": [],
                "modified": null,
                "name": "hci-test-bucket",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.bucket.AWSBucket",
                "version": null,
                encrypted: true,
                versioned: false,
                locked: false,
                tags: [],
                region: "us-west-2",
                permission_policy: null
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await _post_bucket(request=request)


@routes.put('/volumes/{volume_id}/buckets/{id}')
async def put_bucket(request: web.Request) -> web.Response:
    """
    Updates the provided bucket. Only the tags may be updated.

    :param request: the HTTP request.
    :return: a Response object with a status of No Content, or Not Found if no
    bucket exists with that name, or Bad Request if there is a problem with the
    request.
    ---
    summary: Bucket update.
    tags:
        - heaserver-buckets
    parameters:
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
        - $ref: '#/components/parameters/id'
    requestBody:
      description: Attributes of the bucket.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "template": {
                  "data": [
                  {
                    "name": "id",
                    "value": "hci-test-bucket"
                  },
                  {
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
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "invited",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "hci-test-bucket"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
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
                    "name": "encrypted",
                    "value": true
                  },
                  {
                    "name": "versioned",
                    "value": false
                  },
                  {
                    "name": "locked",
                    "value": false
                  },
                  {
                    "name": "tags",
                    "value": []
                  },
                  {
                    "name": "region",
                    "value": us-west-2
                  },
                  {
                    "name": "permission_policy",
                    "value": null
                  },
                  {
                    "name": "type",
                    "value": "heaobject.bucket.AWSBucket"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Bucket example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": "This is a description",
                "display_name": "hci-test-bucket",
                "invited": [],
                "modified": null,
                "name": "hci-test-bucket",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.bucket.AWSBucket",
                "version": null,
                encrypted: true,
                versioned: false,
                locked: false,
                tags: [],
                region: "us-west-2",
                permission_policy: null
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
    volume_id = request.match_info['volume_id']
    bucket_name = request.match_info['id']

    async with aws.S3ClientContext(request, volume_id) as s3_client:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_name))
        except BotoClientError as e:
            return awsservicelib.handle_client_error(e);

        try:
            b = await new_heaobject_from_type(request=request, type_=AWSBucket)
            if not b:
                return web.HTTPBadRequest(body=f"Put body is not a {AWSBucket.get_type_name()}")
            if not b.name:
                return web.HTTPBadRequest(body="Bucket name is required in the body")
            if b.name != bucket_name:
                return web.HTTPBadRequest(body='Bucket name in URL does not match bucket in body')
        except DeserializeException as e:
            return web.HTTPBadRequest(body=str(e))

        async with DesktopObjectActionLifecycle(request=request,
                                                    code='hea-update',
                                                    description=f'Updating {bucket_name}',
                                                    activity_cb=publish_desktop_object) as activity:
            activity.old_object_id = bucket_name
            activity.old_object_uri = f'volumes/{volume_id}/buckets/{bucket_name}'
            activity.old_object_type_name = AWSBucket.get_type_name()
            activity.old_volume_id = volume_id
            #We only support changing the bucket tags.
            try:
                await _put_bucket_tags(s3_client, request, volume_id, bucket_name, b.tags)
            except BotoClientError as e:
                activity.status = Status.FAILED
                return awsservicelib.handle_client_error(e)
            activity.new_object_id = bucket_name
            activity.new_object_uri = f'volumes/{volume_id}/buckets/{bucket_name}'
            activity.new_object_type_name = AWSBucket.get_type_name()
            activity.new_volume_id = volume_id
            request.app[HEA_CACHE].pop((sub, volume_id, None, 'items'), None)
            request.app[HEA_CACHE].pop((sub, volume_id, None, 'actual'), None)
            request.app[HEA_CACHE].pop((sub, volume_id, bucket_name, 'head'), None)
            request.app[HEA_CACHE].pop((sub, volume_id, bucket_name, 'actual'), None)
            return await response.put(True)




@routes.delete('/volumes/{volume_id}/buckets/{id}')
async def delete_bucket(request: web.Request) -> web.Response:
    """
    Deletes the bucket with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: A specific bucket.
    tags:
        - heaserver-buckets
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the bucket to delete.
          schema:
            type: string
        - name: volume_id
          in: path
          required: true
          description: The id of the user's AWS volume.
          schema:
            type: string
          examples:
            example:
              summary: A volume id
              value: 666f6f2d6261722d71757578
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    sub = request.headers.get(SUB, NONE_USER)
    volume_id = request.match_info.get("volume_id", None)
    bucket_id = request.match_info.get("id", None)
    if not volume_id:
        return web.HTTPBadRequest(body="volume_id is required")
    if not bucket_id:
        return web.HTTPBadRequest(body="bucket_id is required")
    loop = asyncio.get_running_loop()
    async with DesktopObjectActionLifecycle(request=request,
                                                code='hea-delete',
                                                description=f'Deleting {bucket_id}',
                                                activity_cb=publish_desktop_object) as activity:
        activity.old_object_id = bucket_id
        activity.old_object_uri = f'volumes/{volume_id}/buckets/{bucket_id}'
        activity.old_object_type_name = AWSBucket.get_type_name()
        activity.old_volume_id = volume_id
        async with aws.S3ClientContext(request=request, volume_id=volume_id) as s3_client:
            try:
                await _delete_bucket_objects(s3_client, bucket_id)
                await loop.run_in_executor(None, partial(s3_client.delete_bucket, Bucket=bucket_id))
                request.app[HEA_CACHE].pop((sub, volume_id, bucket_id, 'head'), None)
                request.app[HEA_CACHE].pop((sub, volume_id, None, 'items'), None)
                request.app[HEA_CACHE].pop((sub, volume_id, None, 'actual'), None)
                request.app[HEA_CACHE].pop((sub, volume_id, bucket_id, 'actual'), None)
                return web.HTTPNoContent()
            except BotoClientError as e:
                activity.status = Status.FAILED
                return awsservicelib.handle_client_error(e)


def main() -> None:
    config = init_cmd_line(description='a service for managing buckets and their data within the cloud',
                           default_port=8080)
    start(package_name='heaserver-buckets', db=aws.S3Manager,
          wstl_builder_factory=builder_factory(__package__),
          cleanup_ctx=[publisher_cleanup_context_factory(config)],
          config=config)


async def _delete_bucket_objects(s3_client: S3Client, bucket_name: str,
                                 delete_versions: bool = False) -> None:
    """
    Deletes all objects inside a bucket. Assumes the bucket exists.

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account.
    :param bucket_name: Bucket to delete
    :param delete_versions: Boolean indicating if the versioning should be deleted as well, defaults to False
    """
    loop = asyncio.get_running_loop()
    if delete_versions:
        bucket_versioning = await loop.run_in_executor(None, partial(s3_client.get_bucket_versioning, Bucket=bucket_name))
        if bucket_versioning['Status'] == 'Enabled':
            object_response_paginator = await loop.run_in_executor(None, s3_client.get_paginator, 'list_object_versions')

            delete_marker_list = []
            version_list = []

            for object_response_itr in await loop.run_in_executor(None, partial(object_response_paginator.paginate, Bucket=bucket_name)):
                if 'DeleteMarkers' in object_response_itr:
                    for delete_marker in object_response_itr['DeleteMarkers']:
                        delete_marker_list.append({'Key': delete_marker['Key'], 'VersionId': delete_marker['VersionId']})

                if 'Versions' in object_response_itr:
                    for version in object_response_itr['Versions']:
                        version_list.append({'Key': version['Key'], 'VersionId': version['VersionId']})

            for i in range(0, len(delete_marker_list), 1000):
                await loop.run_in_executor(None, partial(s3_client.delete_objects,
                    Bucket=bucket_name,
                    Delete={
                        'Objects': delete_marker_list[i:i+1000],
                        'Quiet': True
                    }
                ))

            for i in range(0, len(version_list), 1000):
                await loop.run_in_executor(None, partial(s3_client.delete_objects,
                    Bucket=bucket_name,
                    Delete={
                        'Objects': version_list[i:i+1000],
                        'Quiet': True
                    }
                ))
        else:
            object_response_paginator = await loop.run_in_executor(None, s3_client.get_paginator, 'list_objects_v2')
            object_list = []
            for object_response_itr in await loop.run_in_executor(None, partial(object_response_paginator.paginate, Bucket=bucket_name)):
                for object in object_response_itr.get('Contents', []):
                    object_list.append({'Key': object['Key']})
            for i in range(0, len(object_list), 1000):
                delete_ = {
                    'Objects': object_list[i:i+1000],
                    'Quiet': True
                }
                await loop.run_in_executor(None, partial(s3_client.delete_objects, Bucket=bucket_name, Delete=delete_))
    else:
        object_response_paginator = await loop.run_in_executor(None, s3_client.get_paginator, 'list_objects_v2')
        object_list = []
        for object_response_itr in await loop.run_in_executor(None, partial(object_response_paginator.paginate, Bucket=bucket_name)):
            for object in object_response_itr.get('Contents', []):
                object_list.append({'Key': object['Key']})
        for i in range(0, len(object_list), 1000):
            delete_ = {
                'Objects': object_list[i:i+1000],
                'Quiet': True
            }
            await loop.run_in_executor(None, partial(s3_client.delete_objects, Bucket=bucket_name, Delete=delete_))


async def _get_bucket(request: web.Request) -> web.Response:
    """
    List a single bucket's attributes

    :param request: the aiohttp Request (required).
    :return:  return the single bucket object requested or HTTP Error Response
    """
    sub = request.headers.get(SUB, NONE_USER)
    try:
        volume_id = request.match_info['volume_id']
        bucket_name = request.match_info.get('id')
        if bucket_name is None:
            bucket_name = request.match_info['bucket_name']
    except KeyError as e:
        raise ValueError(str(e))

    async with DesktopObjectActionLifecycle(request=request,
                                                code='hea-get',
                                                description=f'Getting {bucket_name}',
                                                activity_cb=publish_desktop_object) as activity:
        cache_key = (sub, volume_id, bucket_name, 'actual')
        bucket_dict = request.app[HEA_CACHE].get(cache_key)
        if bucket_dict:
            return await response.get(request=request, data=bucket_dict)
        else:
            async with aws.S3ClientContext(request=request, volume_id=volume_id) as s3_client:
                try:
                    bucket_result = await __get_bucket(volume_id=volume_id, s3_client=s3_client, cache=request.app[HEA_CACHE],
                                                    bucket_name=bucket_name, bucket_id=bucket_name, sub=request.headers.get(SUB, NONE_USER))
                    if type(bucket_result) is AWSBucket:
                        activity.new_object_id = bucket_name
                        activity.new_object_uri = f'volumes/{volume_id}/buckets/{bucket_name}'
                        activity.new_object_type_name = AWSBucket.get_type_name()
                        activity.new_volume_id = volume_id
                        bucket_dict = bucket_result.to_dict()
                        request.app[HEA_CACHE][(sub, volume_id, bucket_dict['id'], 'actual')] = bucket_dict
                        return await response.get(request=request, data=bucket_dict, permissions=bucket_result.get_permissions(sub))
                    activity.status = Status.FAILED
                    return await response.get(request, data=None)
                except BotoClientError as e:
                    activity.status = Status.FAILED
                    return awsservicelib.handle_client_error(e)


async def __get_bucket(volume_id: str, s3_client: S3Client, cache,
                     bucket_name: str | None = None, bucket_id: str | None = None,
                     creation_date: datetime | None = None,
                     sub: str | None = None) -> AWSBucket | None:
    """
    :param volume_id: the volume id
    :param s3_client:  the boto3 client
    :param bucket_name: str the bucket name (optional)
    :param bucket_id: str the bucket id (optional)
    :param creation_date: str the bucket creation date (optional)
    :return: Returns either the AWSBucket or None for Not Found or Forbidden, else raises ClientError
    """
    logger = logging.getLogger(__name__)
    loop = asyncio.get_running_loop()
    if not volume_id or (not bucket_id and not bucket_name):
        raise ValueError("volume_id is required and either bucket_name or bucket_id")

    b = AWSBucket()
    b.name = bucket_id if bucket_id else bucket_name
    b.id = bucket_id if bucket_id else bucket_name
    if bucket_id is not None:
        b.display_name = bucket_id
    elif bucket_name is not None:
        b.display_name = bucket_name
    async_bucket_methods = []
    b.bucket_id = b.name
    b.source = AWS_S3
    b.source_detail = AWS_S3
    b.arn = f'arn:aws:s3::{b.id}'
    b.owner = AWS_USER
    share = ShareImpl()
    share.user = ALL_USERS
    share.permissions = [Permission.EDITOR]
    b.shares = [share]

    if creation_date:
        b.created = creation_date
    elif cached_value := cache.get((sub, volume_id, None, 'items')):
        b.created = next((bucket_['created'] for bucket_ in cached_value if bucket_['name'] == b.name), None)
    else:
        async def _get_creation_date(b: AWSBucket):
            logger.debug('Getting creation date of bucket %s', b.name)
            try:
                creation_date = next((bucket_['CreationDate'] for bucket_ in (await loop.run_in_executor(None, s3_client.list_buckets))['Buckets'] if bucket_['Name'] == b.name), None)
                b.created = creation_date
            except BotoClientError as ce:
                logger.exception('Error getting the creation date of bucket %s')
                raise ce

        async_bucket_methods.append(_get_creation_date(b))

    async def _get_version_status(b: AWSBucket):
        logger.debug('Getting version status of bucket %s', b.name)
        try:
            bucket_versioning = await loop.run_in_executor(None,
                                                            partial(s3_client.get_bucket_versioning, Bucket=b.name))
            logger.debug('bucket_versioning=%s', bucket_versioning)
            if 'Status' in bucket_versioning:
                b.versioned = bucket_versioning['Status'] == 'Enabled'
                logger.debug('Got version status of bucket %s successfully', b.name)
            else:
                logger.debug('No version status information for bucket %s', b.name)
        except BotoClientError as ce:
            logger.exception('Error getting the version status of bucket %s')
            raise ce

    async_bucket_methods.append(_get_version_status(b))

    async def _get_region(b: AWSBucket):
        logger.debug('Getting region of bucket %s', b.name)
        try:
            loc = await loop.run_in_executor(None, partial(s3_client.get_bucket_location, Bucket=b.name))
            b.region = loc['LocationConstraint'] or 'us-east-1'
        except BotoClientError as ce:
            logging.exception('Error getting the region of bucket %s', b.name)
            raise ce
        logger.debug('Got region of bucket %s successfully', b.name)

    async_bucket_methods.append(_get_region(b))

    # todo how to find partition dynamically. The format is arn:PARTITION:s3:::NAME-OF-YOUR-BUCKET
    # b.arn = "arn:"+"aws:"+":s3:::"

    async def _get_tags(b: AWSBucket):
        logger.debug('Getting tags of bucket %s', b.name)
        try:
            tagging = await loop.run_in_executor(None, partial(s3_client.get_bucket_tagging, Bucket=b.name))
            b.tags = _from_aws_tags(aws_tags=tagging['TagSet'])
        except BotoClientError as ce:
            if ce.response['Error']['Code'] != 'NoSuchTagSet':
                logging.exception('Error getting the tags of bucket %s', b.name)
                raise ce
        logger.debug('Got tags of bucket %s successfully', b.name)

    async_bucket_methods.append(_get_tags(b))

    async def _get_encryption_status(b: AWSBucket):
        logger.debug('Getting encryption status of bucket %s', b.name)
        try:
            encrypt = await loop.run_in_executor(None, partial(s3_client.get_bucket_encryption, Bucket=b.name))
            rules: list = encrypt['ServerSideEncryptionConfiguration']['Rules']
            b.encrypted = len(rules) > 0
        except BotoClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                b.encrypted = False
            else:
                logger.exception('Error getting the encryption status of bucket %s', b.name)
                raise e
        logger.debug('Got encryption status of bucket %s successfully', b.name)

    async_bucket_methods.append(_get_encryption_status(b))

    async def _get_bucket_policy(b: AWSBucket):
        logger.debug('Getting bucket policy of bucket %s', b.name)
        try:
            bucket_policy = await loop.run_in_executor(None, partial(s3_client.get_bucket_policy, Bucket=b.name))
            b.permission_policy = bucket_policy['Policy']
        except BotoClientError as e:
            if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                logging.exception('Error getting the bucket policy of bucket %s', b.name)
                raise e
        logger.debug('Got bucket policy of bucket %s successfully', b.name)

    async_bucket_methods.append(_get_bucket_policy(b))

    async def _get_bucket_lock_status(b: AWSBucket):
        logger.debug('Getting bucket lock status of bucket %s', b.name)
        try:
            lock_config = await loop.run_in_executor(None, partial(s3_client.get_object_lock_configuration,
                                                                    Bucket=b.name))
            b.locked = lock_config['ObjectLockConfiguration']['ObjectLockEnabled'] == 'Enabled'
        except BotoClientError as e:
            if e.response['Error']['Code'] != 'ObjectLockConfigurationNotFoundError':
                logger.exception('Error getting the lock status of bucket %s', b.name)
                raise e
            b.locked = False
        logger.debug('Got bucket lock status of bucket %s successfully', b.name)

    async_bucket_methods.append(_get_bucket_lock_status(b))

    # todo need to lazy load this these metrics
    total_size = None
    obj_count = None
    mod_date = None
    # FIXME need to calculate this metric data in a separate call. Too slow
    # s3bucket = s3_resource.Bucket(b.name)
    # for obj in s3bucket.objects.all():
    #     total_size += obj.size
    #     obj_count += 1
    #     mod_date = obj.last_modified if mod_date is None or obj.last_modified > mod_date else mod_date
    b.size = total_size
    b.object_count = obj_count
    b.modified = mod_date
    await asyncio.gather(*async_bucket_methods)
    return b


def _from_aws_tags(aws_tags: list[TagTypeDef]) -> list[Tag]:
    """
    :param aws_tags: Tags obtained from boto3 Tags api
    :return: List of HEA Tags
    """
    hea_tags = []
    for t in aws_tags:
        tag = Tag()
        tag.key = t['Key']
        tag.value = t['Value']
        hea_tags.append(tag)
    return hea_tags


async def _bucket_opener(request: web.Request) -> web.Response:
    """
    Returns links for opening the bucket. The volume id must be in the volume_id entry of the request's
    match_info dictionary. The bucket id must be in the id entry of the request's match_info dictionary.

    :param request: the HTTP request (required).
    :return: the HTTP response with a 200 status code if the bucket exists and a Collection+JSON document in the body
    containing an heaobject.bucket.AWSBucket object and links, 403 if access was denied, 404 if the bucket
    was not found, or 500 if an internal error occurred.
    """
    try:
        volume_id = request.match_info['volume_id']
        bucket_id = request.match_info['id']
    except KeyError as e:
        return response.status_bad_request(str(e))
    sub = request.headers.get(SUB, NONE_USER)
    loop = asyncio.get_running_loop()

    async with DesktopObjectActionLifecycle(request=request,
                                            code='hea-get',
                                            description=f'Accessing bucket {bucket_id}',
                                            activity_cb=publish_desktop_object) as activity:
        head_cache_key = (sub, volume_id, bucket_id, 'head')
        actual_cache_key = (sub, volume_id, bucket_id, 'actual')
        if head_cache_key not in request.app[HEA_CACHE] and actual_cache_key not in request.app[HEA_CACHE]:
            async with aws.S3ClientContext(request, volume_id) as s3_client:
                try:
                    await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=bucket_id))
                    activity.new_object_id = bucket_id
                    activity.new_object_type_name = AWSBucket.get_type_name()
                    activity.new_object_uri = f'volumes/{volume_id}/buckets/{bucket_id}'
                    activity.new_volume_id = volume_id
                    request.app[HEA_CACHE][head_cache_key] = bucket_id
                except BotoClientError as e:
                    raise awsservicelib.handle_client_error(e)
        return await response.get_multiple_choices(request)


async def _post_bucket(request: web.Request):
    """
    Create an S3 bucket in a specified region. Will fail if the bucket with the given name already exists.
    If a region is not specified, the bucket is created in the S3 default region (us-east-1).

    The request must have either a volume id, which is the id string of the volume representing the user's AWS account,
    or an id, which is the account id.

    :param request: the aiohttp Request (required). A volume_id must be specified in its match info. The AWSBucket
    in the body of the request must have a name.
    """
    logger = logging.getLogger(__name__)
    sub = request.headers.get(SUB, NONE_USER)
    bucket_already_exists_msg = "A bucket named {} already exists"

    volume_id = request.match_info.get('volume_id', None)
    if not volume_id:
        volume_id = await awsservicelib.get_volume_id_for_account_id(request)
        if not volume_id:
            return web.HTTPBadRequest(body="either id or volume_id is required")
    try:
        b = await new_heaobject_from_type(request=request, type_=AWSBucket)
        if not b:
            return web.HTTPBadRequest(body="Post body is not an HEAObject AWSBUCKET")
        if not b.name:
            return web.HTTPBadRequest(body="Bucket name is required")
    except DeserializeException as e:
        return web.HTTPBadRequest(body=str(e))

    loop = asyncio.get_running_loop()
    async with aws.S3ClientContext(request, volume_id) as s3_client:
        try:
            await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=b.name))  # check if bucket exists, if not throws an exception
            return web.HTTPConflict(body=bucket_already_exists_msg.format(b.display_name))
        except BotoClientError as e:
            loop = asyncio.get_running_loop()
            try:
                # todo this is a privileged actions need to check if authorized
                error_code = e.response['Error']['Code']

                if error_code == '404':  # bucket doesn't exist
                    create_bucket_params: dict[str, Any] = {'Bucket': b.name}
                    put_bucket_policy_params = {
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                    if b.region and b.region != 'us-east-1':
                        create_bucket_params['CreateBucketConfiguration'] = {'LocationConstraint': b.region}
                    if b.locked:
                        create_bucket_params['ObjectLockEnabledForBucket'] = True

                    await loop.run_in_executor(None, partial(s3_client.create_bucket, **create_bucket_params))
                    # make private bucket
                    await loop.run_in_executor(None, partial(s3_client.put_public_access_block, Bucket=b.name,
                                                            PublicAccessBlockConfiguration=put_bucket_policy_params))

                    await _put_bucket_encryption(b, loop, s3_client)
                    # todo this is a privileged action need to check if authorized ( may only be performed by bucket owner)

                    await _put_bucket_versioning(bucket_name=b.name, s3_client=s3_client, is_versioned=b.versioned)

                    await _put_bucket_tags(s3_client, request=request, volume_id=volume_id,
                                        bucket_name=b.name, new_tags=b.tags)
                elif error_code == '403':  # already exists but the user doesn't have access to it
                    logger.exception(bucket_already_exists_msg, b.display_name)
                    return web.HTTPBadRequest(body=bucket_already_exists_msg.format(b.display_name))
                else:
                    logger.exception(str(e))
                    return response.status_bad_request(str(e))
            except BotoClientError as e2:
                logger.exception(e2.message)
                try:
                    await loop.run_in_executor(None, partial(s3_client.head_bucket, Bucket=b.name))
                    del_bucket_result = await loop.run_in_executor(None, partial(s3_client.delete_bucket, Bucket=b.name))
                    logging.info(f"deleted failed bucket {b.name} details: \n{del_bucket_result}")
                except BotoClientError:  # bucket doesn't exist so no clean up needed
                    pass
                return web.HTTPBadRequest(body=e2.response['Error'].get('Message'))
            request.app[HEA_CACHE].pop((sub, volume_id, None, 'items'), None)
            request.app[HEA_CACHE].pop((sub, volume_id, None, 'actual'), None)
            return await response.post(request, b.name, f'volumes/{volume_id}/buckets')


async def _put_bucket_encryption(b, loop, s3_client):
    if b.encrypted:
        SSECNF = 'ServerSideEncryptionConfigurationNotFoundError'
        try:
            await loop.run_in_executor(None, partial(s3_client.get_bucket_encryption, Bucket=b.name))
        except BotoClientError as e:
            if e.response['Error']['Code'] == SSECNF:
                config = \
                    {'Rules': [{'ApplyServerSideEncryptionByDefault':
                                    {'SSEAlgorithm': 'AES256'}, 'BucketKeyEnabled': False}]}
                await loop.run_in_executor(None, partial(s3_client.put_bucket_encryption, Bucket=b.name,
                                                         ServerSideEncryptionConfiguration=config))
            else:
                logging.error(e.response['Error']['Code'])
                raise e


async def _put_bucket_versioning(bucket_name: str, is_versioned: bool | None, s3_client: S3Client):
    """
    Use To change turn on or off bucket versioning settings. Note that if the Object Lock
    is turned on for the bucket you can't change these settings.

    :param bucket_name: The bucket name
    :param is_versioned: For toggling on or off the versioning
    :param s3_client: Pass the active client if exists (optional)
    :raises BotoClientError: if an error occurred setting version information.
    """
    logger = logging.getLogger(__name__)
    loop = asyncio.get_running_loop()
    vconfig = {
        'MFADelete': 'Disabled',
        'Status': 'Enabled' if is_versioned else 'Suspended',
    }
    vresp = await loop.run_in_executor(None, partial(s3_client.put_bucket_versioning, Bucket=bucket_name,
                                                     VersioningConfiguration=vconfig))
    logger.debug(vresp)


async def _put_bucket_tags(s3_client: S3Client, request: web.Request, volume_id: str, bucket_name: str,
                           new_tags: list[Tag] | None):
    """
    Creates or adds to a tag list for bucket

    :param request: the aiohttp Request (required).
    :param volume_id: the id string of the volume representing the user's AWS account (required).
    :param bucket_name: The bucket (required).
    :param new_tags: new tags to be added tag list on specified bucket. Pass in the empty list or None to clear out
    the bucket's tags.
    :raises BotoClientError: if an error occurs interacting with S3.
    """
    if request is None:
        raise ValueError('request is required')
    if volume_id is None:
        raise ValueError('volume_id is required')
    if bucket_name is None:
        raise ValueError('bucket_name is required')

    loop = asyncio.get_running_loop()
    def delete_and_put():
        s3_client.delete_bucket_tagging(Bucket=bucket_name)
        s3_client.put_bucket_tagging(Bucket=bucket_name, Tagging={'TagSet': _to_aws_tags(new_tags or [])})
    await loop.run_in_executor(None, delete_and_put)


def _to_aws_tags(hea_tags: list[Tag]) -> list[dict[str, str]]:
    """
    :param hea_tags: HEA tags to converted to aws tags compatible with boto3 api
    :return: aws tags
    """
    aws_tag_dicts = []
    for hea_tag in hea_tags:
        aws_tag_dict = {}
        aws_tag_dict['Key'] = hea_tag.key
        aws_tag_dict['Value'] = hea_tag.value
        aws_tag_dicts.append(aws_tag_dict)
    return aws_tag_dicts
