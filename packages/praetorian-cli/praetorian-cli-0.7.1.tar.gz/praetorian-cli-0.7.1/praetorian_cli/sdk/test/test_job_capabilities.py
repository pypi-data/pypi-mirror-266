from praetorian_cli.sdk.test.utils import Utils

from praetorian_cli.sdk.test import BaseTest


class TestJob(BaseTest):

    def setup_class(self):
        self.chaos, self.username = BaseTest.setup_chaos(self)
        self.seed = "contoso.com"
        self.capabilities = ['vulnerability', 'whois', 'subfinder', 'cidr', 'portscan', 'code', 'secrets']
        self.utils = Utils(self.chaos)

    def test_my_jobs(self):
        response = self.utils.key(dict(key=f'#job#{self.seed}'), 300, 60)
        assert response.get('jobs'), "Received empty response for my jobs"

        for my_job in response.get('jobs', []):
            print(my_job)
            assert my_job['username'] == self.username, "Job did not have username"
            assert self.seed in my_job['key'], "Job key did not have required seed"
            assert my_job['key'].split('#')[
                       -2] in self.capabilities, "Job capability is not in defined capabilities"

    def test_my_assets(self):
        response = self.utils.wait_for_key(dict(key=f'#asset#{self.seed}'), 40, 5)
        assert response.get('assets'), "Received empty response for my assets"

        for my_asset in response.get('assets', []):
            assert my_asset['username'] == self.username, f"Job did not have username = {self.username}"
            assert self.seed in my_asset['key'], f"Asset key did not have required seed = {self.seed}"

    def test_my_services(self):
        response = self.utils.wait_for_key(dict(key=f'#service#{self.seed}'), 180, 10)
        assert response.get('services'), "Received empty response for my services"

        for my_service in response.get('services', []):
            assert my_service['username'] == self.username, f"Job did not have username = {self.username}"
            assert self.seed in my_service['key'], "Service key does not have seed"

    def test_my_risks(self):
        response = self.utils.wait_for_key(dict(key=f'#risk#{self.seed}'), 300, 30)
        assert response.get('risks'), "Received empty response for my risks"

        for my_risk in response.get('risks', []):
            assert my_risk['username'] == self.username, f"Job did not have username = {self.username}"
            assert self.seed in my_risk['key'], "Service key does not have seed"

    def test_delete_seed(self):
        response = self.utils.freeze_seed(self.seed)
        assert response['seed'] == self.seed
