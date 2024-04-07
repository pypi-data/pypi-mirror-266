import time


def assert_files_equal(file1_path, file2_path):
    with open(file1_path, 'r') as file1:
        content1 = file1.read()

    with open(file2_path, 'r') as file2:
        content2 = file2.read()

    assert content1 == content2, f"Contents of the files {file1_path} and {file2_path} file are not equal"

class Utils:
    def __init__(self, chaos):
        self.chaos = chaos

    def wait_for_key(self, key, timeout=60, interval=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            print(f"Trying to get response for my {key}")
            response = self.chaos.my(key)
            if response:
                return response
            time.sleep(interval)

    def add_seed(self, seed):
        return self.chaos.upsert_seed(seed, 0)

    def freeze_seed(self, seed):
        return self.chaos.upsert_seed(seed, 1)
