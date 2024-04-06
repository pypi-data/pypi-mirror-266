"""
Creates a test case class for use with the unittest library that is built into Python.
"""

from heaserver.service.testcase.microservicetestcase import get_test_case_cls_default
from heaserver.service.testcase import expectedvalues
from heaserver.volume import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import Action

db_store = {
    service.MONGODB_VOLUME_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Default File System',
        'invites': [],
        'shares': [],
        'modified': None,
        'name': 'heaobject.volume.MongoDBFileSystem^DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'source_detail': None,
        'type': 'heaobject.volume.Volume',
        'file_system_type': 'heaobject.volume.MongoDBFileSystem',
        'file_system_name': 'DEFAULT_FILE_SYSTEM',
        'folder_id': None,
        'mime_type': 'application/x.volume',
        'credential_id': None,
        'account': None
    },
    {
        'id': '0123456789ab0123456789ab',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'AWS File System',
        'invites': [],
        'shares': [],
        'modified': None,
        'name': 'heaobject.volume.AWSFileSystem^DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'source_detail': None,
        'type': 'heaobject.volume.Volume',
        'file_system_type': 'heaobject.volume.AWSFileSystem',
        'file_system_name': 'DEFAULT_FILE_SYSTEM',
        'folder_id': None,
        'mime_type': 'application/x.volume',
        'credential_id': None,
        'account': None
    }],
    service.MONGODB_FILE_SYSTEM_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': 'Access to Amazon Web Services (AWS)',
        'display_name': 'Amazon Web Services',
        'invites': [],
        'modified': None,
        'name': 'DEFAULT_FILE_SYSTEM',
        'owner': NONE_USER,
        'source': None,
        'source_detail': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'shares': []
    },
    {
        'id': '0123456789ab0123456789ab',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Local MongoDB instance',
        'invites': [],
        'modified': None,
        'name': 'local_mongodb_file_system',
        'owner': NONE_USER,
        'source': None,
        'source_detail': None,
        'type': 'heaobject.volume.MongoDBFileSystem',
        'database_name': 'hea',
        'connection_string': 'mongodb://heauser:heauser@localhost:27017/hea',
        'shares': []
    }]
}


def get_test_case_cls(*args, **kwargs):
    """Get a test case class specifically for this microservice."""
    class MyTestCase(get_test_case_cls_default(*args, **kwargs)):
        def __init__(self, *args_, **kwargs_):
            super().__init__(*args_, **kwargs_)
            if self._body_post:
                modified_data = {**db_store[self._coll][0], 'display_name': 'My File System'}
                if 'id' in modified_data:
                    del modified_data['id']
                self._body_post = expectedvalues._create_template(modified_data)

    return MyTestCase


VolumeTestCase = get_test_case_cls(coll=service.MONGODB_VOLUME_COLLECTION,
                                   wstl_package=service.__package__,
                                   href='http://localhost:8080/volumes',
                                   fixtures=db_store,
                                   get_actions=[Action(name='heaserver-volumes-volume-get-properties',
                                                       rel=['hea-properties']),
                                                Action(name='heaserver-volumes-volume-get-open-choices',
                                                       url='http://localhost:8080/volumes/{id}/opener',
                                                       rel=['hea-opener-choices']),
                                                Action(name='heaserver-volumes-volume-duplicate',
                                                       url='http://localhost:8080/volumes/{id}/duplicator',
                                                       rel=['hea-duplicator'])
                                                ],
                                   get_all_actions=[Action(name='heaserver-volumes-volume-get-properties',
                                                           rel=['hea-properties']),
                                                    Action(name='heaserver-volumes-volume-get-open-choices',
                                                           url='http://localhost:8080/volumes/{id}/opener',
                                                           rel=['hea-opener-choices']),
                                                    Action(name='heaserver-volumes-volume-duplicate',
                                                           url='http://localhost:8080/volumes/{id}/duplicator',
                                                           rel=['hea-duplicator'])],
                                   expected_opener=expectedvalues.Link(
                                       url=f'http://localhost:8080/volumes/{db_store[service.MONGODB_VOLUME_COLLECTION][0]["id"]}/content',
                                       rel=['hea-opener', 'hea-default', 'application/x.folder']),
                                   duplicate_action_name='heaserver-volumes-volume-duplicate-form',
                                   put_content_status=405)

FileSystemTestCase = get_test_case_cls(coll=service.MONGODB_FILE_SYSTEM_COLLECTION,
                                       wstl_package=service.__package__,
                                       href='http://localhost:8080/filesystems',
                                       fixtures=db_store,
                                       get_actions=[Action(name='heaserver-volumes-file-system-get-properties',
                                                           rel=['hea-properties']),
                                                    Action(name='heaserver-volumes-file-system-duplicate',
                                                           url='http://localhost:8080/filesystems/{id}/duplicator',
                                                           rel=['hea-duplicator'])
                                                    ],
                                       get_all_actions=[
                                           Action(name='heaserver-volumes-file-system-get-properties',
                                                  rel=['hea-properties']),
                                           Action(name='heaserver-volumes-file-system-duplicate',
                                                  url='http://localhost:8080/filesystems/{id}/duplicator',
                                                  rel=['hea-duplicator'])],
                                       duplicate_action_name='heaserver-volumes-file-system-duplicate-form',
                                       put_content_status=404)
