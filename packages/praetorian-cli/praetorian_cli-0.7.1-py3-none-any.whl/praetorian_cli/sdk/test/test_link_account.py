import random

from praetorian_cli.sdk.test import BaseTest


class TestLinkAccount(BaseTest):

    def setup_class(self):
        self.chaos, self.username = BaseTest.setup_chaos(self)
        self.link_account_name = f"chaos_cli_test_{random.randint(0, 9999)}"

    def test_link_account(self):
        response = self.chaos.link_account(username=self.link_account_name, secret="")
        assert response['member'] == self.link_account_name
        my_accounts=self.chaos.my(dict(key=f'#account#{self.username}'))['accounts']
        assert any(account.get("member") == self.link_account_name for account in my_accounts)

    def test_unlink_account(self):
        response = self.chaos.unlink_account(username=self.link_account_name)
        assert response['member'] == self.link_account_name
        my_accounts=self.chaos.my(dict(key=f'#account#{self.username}'))['accounts']
        assert all(account.get("member") != self.link_account_name for account in my_accounts)
        
