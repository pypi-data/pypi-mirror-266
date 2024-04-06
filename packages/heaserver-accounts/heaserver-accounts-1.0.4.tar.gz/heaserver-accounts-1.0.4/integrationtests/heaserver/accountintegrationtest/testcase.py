"""
Creates a test case class for use with the unittest library that is built into Python.
"""
from heaserver.service.testcase.collection import CollectionKey
from heaserver.service.testcase.dockermongo import MockDockerMongoManager, RealRegistryContainerConfig
from heaserver.service.testcase.awsdockermongo import MockS3WithMockDockerMongoManager
from heaserver.service.testcase.testenv import MicroserviceContainerConfig
from heaserver.service.testcase.mockaws import MockS3Manager
from heaserver.service.testcase import microservicetestcase, expectedvalues
from heaserver.account import service
from heaserver.service.sources import AWS
from heaobject.user import NONE_USER, AWS_USER
from heaobject.registry import Resource
from heaobject.volume import DEFAULT_FILE_SYSTEM


db_store = {
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
        'invited': [],
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
    CollectionKey(name='awsaccounts', db_manager_cls=MockS3Manager): [
        {
            "alternate_contact_name": None,
            "alternate_email_address": None,
            "alternate_phone_number": None,
            "created": None,
            "derived_by": None,
            "derived_from": [],
            "description": None,
            "display_name": "123456789012",
            "email_address": 'master@example.com',
            "full_name": None,
            "id": "123456789012",
            "invites": [],
            "mime_type": "application/x.awsaccount",
            "modified": None,
            "name": "master",
            "owner": AWS_USER,
            "phone_number": None,
            "shares": [],
            "source": AWS,
            "source_detail": AWS,
            "type": "heaobject.account.AWSAccount"
        }
    ]
}


HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0'
HEASERVER_KEYCHAIN_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-keychain:1.0.0'
volume_microservice = MicroserviceContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                                  resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                      base_path='volumes',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM),
                                                             Resource(resource_type_name='heaobject.volume.FileSystem',
                                                                      base_path='filesystems',
                                                                      file_system_name=DEFAULT_FILE_SYSTEM)],
                                                  db_manager_cls=MockDockerMongoManager)
keychain_microservice = MicroserviceContainerConfig(image=HEASERVER_KEYCHAIN_IMAGE, port=8080,
                                                    check_path='/credentials',
                                                    resources=[
                                                        Resource(resource_type_name='heaobject.keychain.Credentials',
                                                                 base_path='credentials',
                                                                 file_system_name=DEFAULT_FILE_SYSTEM)],
                                                    db_manager_cls=MockDockerMongoManager)


AWSAccountTestCase = \
    microservicetestcase.get_test_case_cls_default(
        href='http://localhost:8080/awsaccounts',
        wstl_package=service.__package__,
        coll='awsaccounts',
        fixtures=db_store,
        db_manager_cls=MockS3WithMockDockerMongoManager,
        get_all_actions=[
            expectedvalues.Action(
                name='heaserver-accounts-awsaccount-get-open-choices',
                url='http://localhost:8080/awsaccounts/{id}/opener',
                rel=['hea-context-menu', 'hea-opener-choices']),
            expectedvalues.Action(name='heaserver-accounts-awsaccount-get-self',
                url='http://localhost:8080/awsaccounts/{id}',
                rel=['self']),
            expectedvalues.Action(name='heaserver-accounts-awsaccount-get-properties',
                   rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-accounts-awsaccount-get-create-choices',
                url='http://localhost:8080/awsaccounts/{id}/creator',
                rel=['hea-creator-choices', 'hea-context-menu'])
        ],
        get_actions=[
            expectedvalues.Action(
                name='heaserver-accounts-awsaccount-get-open-choices',
                url='http://localhost:8080/awsaccounts/{id}/opener',
                rel=['hea-context-menu', 'hea-opener-choices']),
            expectedvalues.Action(name='heaserver-accounts-awsaccount-get-self',
                url='http://localhost:8080/awsaccounts/{id}',
                rel=['hea-account', 'self']),
            expectedvalues.Action(name='heaserver-accounts-awsaccount-get-properties',
                   rel=['hea-properties', 'hea-context-menu']),
            expectedvalues.Action(name='heaserver-accounts-awsaccount-get-trash',
                                  rel=['hea-trash', 'hea-context-menu'],
                                  url='http://localhost:8080/volumes/666f6f2d6261722d71757578/awss3trash',
                                  wstl_url='http://localhost:8080/volumes/{volume_id}/awss3trash'),
            expectedvalues.Action(
                name='heaserver-accounts-awsaccount-get-create-choices',
                url='http://localhost:8080/awsaccounts/{id}/creator',
                rel=['hea-creator-choices', 'hea-context-menu']),
            expectedvalues.Action(
                name='heaserver-accounts-awsaccount-get-volume',
                url='http://localhost:8080/volumes/666f6f2d6261722d71757578',
                wstl_url='http://localhost:8080/volumes/{volume_id}',
                rel=['hea-volume'])],
        put_content_status=404,
        duplicate_action_name=None,
        exclude=['body_put', 'body_post'],
        registry_docker_image=RealRegistryContainerConfig(HEASERVER_REGISTRY_IMAGE),
        other_docker_images=[volume_microservice, keychain_microservice]
    )

