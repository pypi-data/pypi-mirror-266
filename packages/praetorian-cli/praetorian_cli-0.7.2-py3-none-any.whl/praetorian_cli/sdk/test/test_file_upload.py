import os
from praetorian_cli.sdk.test import BaseTest
from praetorian_cli.sdk.test import utils


class TestFileUpload(BaseTest):

    def setup_class(self):
        self.chaos, self.username = BaseTest.setup_chaos(self)
        self.file = "resources/seed_file.txt"
        self.downloaded_file = "resources/seed_file_downloaded.txt"
        self.seed = "contoso.com"

        directory = os.path.dirname(self.file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.file, 'w') as file:
            file.write(self.seed)

    def test_upload_file(self):
        self.chaos.upload(self.file)

    def test_my_file(self):
        response = self.chaos.my(dict(key=f'#file#{self.file}'))
        files = response['files']

        assert len(files) == 1
        assert files[0]['username'] == self.username
        assert files[0]['name'] == self.file
        assert files[0]['key'] == f"#file#{self.file}"

    def test_download_file(self):
        self.chaos.download(self.file, self.downloaded_file)
        assert os.path.exists(self.file) is True
        utils.assert_files_equal(self.file, self.downloaded_file)

    def teardown_class(self):
        os.remove(self.file)
        os.remove(self.downloaded_file)
