from praetorian_cli.sdk.test import BaseTest


class TestNVD(BaseTest):

    def setup_class(self):
        self.chaos, self.username = BaseTest.setup_chaos(self)

    def test_my_threats(self):
        response = self.chaos.my(dict(key=f'#threat'))
        assert response is not None, "Received empty response for my Threats"
        assert len(response['threats']) > 1000, "Less than 1000 CVEs received"

        for my_threat in response.get('threats', []):
            assert 'KEV' in my_threat['key'], "Threat did not have required KEV"
            assert 'CVE' in my_threat['key'], "Threat did not have required CVE"