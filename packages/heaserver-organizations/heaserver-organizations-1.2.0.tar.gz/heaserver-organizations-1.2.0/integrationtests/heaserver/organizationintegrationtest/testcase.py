"""
Creates a test case class for use with the unittest library that is built into Python.
"""

from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase.collection import CollectionKey
from heaserver.service.testcase.dockermongo import MockDockerMongoManager, RealRegistryContainerConfig
from heaserver.service.testcase.awsdockermongo import MockS3WithMockDockerMongoManager
from heaserver.service.testcase.docker import MicroserviceContainerConfig
from heaserver.service.testcase.mockaws import MockS3Manager

from heaserver.organization import service
from heaobject.user import NONE_USER
from heaobject.person import Person
from heaobject.registry import Resource
from heaobject.volume import Volume, FileSystem, DEFAULT_FILE_SYSTEM, AWSFileSystem
from heaobject.account import AWSAccount
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    CollectionKey(name=service.MONGODB_ORGANIZATION_COLLECTION, db_manager_cls=MockDockerMongoManager): [
        {
            "id": "666f6f2d6261722d71757578",
            "source": None,
            "source_detail": None,
            "name": "Bob",
            "display_name": "Bob",
            "description": "Description of Bob lab",
            "owner": NONE_USER,
            "created": None,
            "modified": None,
            "invites": [],
            "shares": [],
            "derived_by": None,
            "derived_from": [],
            "aws_account_ids": [],
            "admin_ids": [],
            "principal_investigator_id": "23423DAFSDF12adfasdf3",
            "manager_ids": ['666f6f2d6261722d71757578'],
            "member_ids": ['0123456789ab0123456789ab'],
            'type': 'heaobject.organization.Organization',
            'mime_type': 'application/x.organization',
            'accounts': []
        },
        {
            "id": "0123456789ab0123456789ab",
            "source": None,
            "source_detail": None,
            "name": "Reximus",
            "display_name": "Reximus",
            "description": "Description of Reximus",
            "owner": NONE_USER,
            "created": None,
            "modified": None,
            "invites": [],
            "shares": [],
            "derived_by": None,
            "derived_from": [],
            "aws_account_ids": [],
            "admin_ids": [],
            "principal_investigator_id": "11234867890b0123a56789ab",
            "manager_ids": ["11234867890b0123a56789ab"],
            "member_ids": [],
            'type': 'heaobject.organization.Organization',
            'mime_type': 'application/x.organization',
            'accounts': []
        }
    ],
    CollectionKey(name='filesystems', db_manager_cls=MockDockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'version': None
    }],
    CollectionKey(name='volumes', db_manager_cls=MockDockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'My Amazon Web Services',
        'invites': [],
        'modified': None,
        'name': 'amazon_web_services',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.volume.Volume',
        'version': None,
        'file_system_name': 'DEFAULT_FILE_SYSTEM',
        'file_system_type': 'heaobject.volume.AWSFileSystem',
        'credential_id': None  # Let boto3 try to find the user's credentials.
    }],
    CollectionKey(name='people', db_manager_cls=MockDockerMongoManager): [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invited': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.person.Person',
        'version': None
    }, {
        'id': '0123456789ab0123456789ab',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus Thomas',
        'invited': [],
        'modified': None,
        'title': 'Manager',
        'name': 'Reximus Thomas',
        'owner': NONE_USER,
        'shares': [],
        'source': None,
        'type': 'heaobject.person.Person',
        'version': None
    }],
    CollectionKey(name='awsaccounts', db_manager_cls=MockS3Manager): [
        {
            "alternate_contact_name": None,
            "alternate_email_address": None,
            "alternate_phone_number": None,
            "created": "2021-06-08T17:38:31+00:00",
            "derived_by": None,
            "derived_from": [],
            "description": None,
            "display_name": "311813441058",
            "email_address": 'no-reply@example.com',
            "full_name": None,
            "id": "311813441058",
            "invites": [],
            "mime_type": "application/x.awsaccount",
            "modified": None,
            "name": "311813441058",
            "owner": "system|none",
            "phone_number": None,
            "shares": [],
            "source": None,
            "type": "heaobject.account.AWSAccount",
            "version": None
        },
        {
            "alternate_contact_name": None,
            "alternate_email_address": None,
            "alternate_phone_number": None,
            "created": "2021-06-08T17:38:31+00:00",
            "derived_by": None,
            "derived_from": [],
            "description": None,
            "display_name": "311813441059",
            "email_address": 'no-reply@example.com',
            "full_name": None,
            "id": "311813441059",
            "invites": [],
            "mime_type": "application/x.awsaccount",
            "modified": None,
            "name": "311813441059",
            "owner": "system|none",
            "phone_number": None,
            "shares": [],
            "source": None,
            "type": "heaobject.account.AWSAccount",
            "version": None
        }
    ]
}

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0'
# HEASERVER_PEOPLE_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-people:1.0.0'
HEASERVER_VOLUME_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0'
HEASERVER_ACCOUNTS_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-accounts:1.0.0'

TestCase = get_test_case_cls_default(coll=service.MONGODB_ORGANIZATION_COLLECTION,
                                     href='http://localhost:8080/organizations',
                                     db_manager_cls=MockS3WithMockDockerMongoManager,
                                     wstl_package=service.__package__,
                                     fixtures=db_store,
                                     get_actions=[Action(name='heaserver-organizations-organization-get-properties',
                                                         rel=['hea-properties']),
                                                  Action(name='heaserver-organizations-organization-get-open-choices',
                                                         url='http://localhost:8080/organizations/{id}/opener',
                                                         rel=['hea-opener-choices']),
                                                  Action(name='heaserver-organizations-organization-duplicate',
                                                         url='http://localhost:8080/organizations/{id}/duplicator',
                                                         rel=['hea-duplicator']),
                                                  Action(name='heaserver-organizations-organization-get-self',
                                                         url='http://localhost:8080/organizations/{id}',
                                                         rel=['self']),
                                                  Action(name='heaserver-organizations-organization-get-memberseditor',
                                                         url='http://localhost:8080/organizations/{id}/memberseditor',
                                                         rel=['hearesource-organizations-memberseditor'])
                                                  ],
                                     get_all_actions=[Action(name='heaserver-organizations-organization-get-properties',
                                                             rel=['hea-properties']),
                                                      Action(
                                                          name='heaserver-organizations-organization-get-open-choices',
                                                          url='http://localhost:8080/organizations/{id}/opener',
                                                          rel=['hea-opener-choices']),
                                                      Action(name='heaserver-organizations-organization-duplicate',
                                                             url='http://localhost:8080/organizations/{id}/duplicator',
                                                             rel=['hea-duplicator']),
                                                      Action(name='heaserver-organizations-organization-get-self',
                                                             url='http://localhost:8080/organizations/{id}',
                                                             rel=['self']),
                                                      Action(name='heaserver-organizations-organization-get-memberseditor',
                                                         url='http://localhost:8080/organizations/{id}/memberseditor',
                                                         rel=['hearesource-organizations-memberseditor'])
                                                  ],
                                     duplicate_action_name='heaserver-organizations-organization-duplicate-form',
                                     registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
                                     other_docker_images=[
                                         # MicroserviceContainerConfig(image=HEASERVER_PEOPLE_IMAGE,
                                         #                             port=8080,
                                         #                             check_path='/ping',
                                         #                             db_manager_cls=DockerMongoManager,
                                         #                             resources=[
                                         #                                 Resource(
                                         #                                     resource_type_name=Person.get_type_name(),
                                         #                                     base_path='/people'
                                         #                                 )
                                         #                             ]),
                                         MicroserviceContainerConfig(image=HEASERVER_ACCOUNTS_IMAGE,
                                                                     port=8080,
                                                                     check_path='/ping',
                                                                     db_manager_cls=MockS3Manager,
                                                                     resources=[
                                                                         Resource(
                                                                             resource_type_name=AWSAccount.get_type_name(),
                                                                             base_path='awsaccounts',
                                                                             file_system_name=DEFAULT_FILE_SYSTEM,
                                                                             file_system_type=AWSFileSystem.get_type_name()
                                                                         )
                                                                     ]),
                                         MicroserviceContainerConfig(image=HEASERVER_VOLUME_IMAGE,
                                                                     port=8080,
                                                                     check_path='/volumes/',
                                                                     db_manager_cls=MockDockerMongoManager,
                                                                     resources=[
                                                                         Resource(
                                                                             resource_type_name=Volume.get_type_name(),
                                                                             base_path='volumes',
                                                                             file_system_name=DEFAULT_FILE_SYSTEM
                                                                         ),
                                                                         Resource(
                                                                             resource_type_name=FileSystem.get_type_name(),
                                                                             base_path='filesystems',
                                                                             file_system_name=DEFAULT_FILE_SYSTEM
                                                                         )
                                                                     ])
                                     ])
