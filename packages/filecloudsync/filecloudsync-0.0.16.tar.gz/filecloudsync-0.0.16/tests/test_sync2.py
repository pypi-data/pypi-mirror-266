import unittest
from os.path import exists
from shutil import rmtree

from filecloudsync import s3
from filecloudsync.s3.exceptions import TagsNotMatchError


class MyTestCase(unittest.TestCase):
    def test_something(self):
        client = s3.connect(multipart_chunk_size_mb=15)
        try:
            s3.sync(client, 'ia-ocr.models', 'models/')
        finally:
            if exists('models'):
                rmtree('models')
            s3.remove_sync_status(client, 'ia-ocr.models', 'models/')
        client = s3.connect(multipart_chunk_size_mb=8)
        try:
            with self.assertRaises(TagsNotMatchError):
                s3.sync(client, 'ia-ocr.models', 'models/')
        finally:
            if exists('models'):
                rmtree('models')
            s3.remove_sync_status(client, 'ia-ocr.models', 'models/')


if __name__ == '__main__':
    unittest.main()
