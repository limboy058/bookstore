import uuid

import pytest
import sys
sys.path.append("D:\\code\\数据库系统\\AllStuRead-master\\Project_1\\bookstore")

from fe.access import auth
from fe import conf


class TestPassword:

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        # register a user
        self.user_id = "test_password_{}".format(str(uuid.uuid1()))
        self.old_password = "old_password_" + self.user_id
        self.new_password = "new_password_" + self.user_id
        self.terminal = "terminal_" + self.user_id

        assert self.auth.register(self.user_id, self.old_password) == 200
        yield

    def test_ok(self):
        code = self.auth.password(self.user_id, self.old_password,
                                  self.new_password)
        assert code == 200

        code, new_token = self.auth.login(self.user_id, self.old_password,
                                          self.terminal)
        assert code != 200

        code, new_token = self.auth.login(self.user_id, self.new_password,
                                          self.terminal)
        assert code == 200

        code = self.auth.logout(self.user_id, new_token)
        assert code == 200

    def test_error_password(self):
        code = self.auth.password(self.user_id, self.old_password + "_x",
                                  self.new_password)
        assert code != 200

        code, new_token = self.auth.login(self.user_id, self.new_password,
                                          self.terminal)
        assert code != 200

    def test_error_user_id(self):
        code = self.auth.password(self.user_id + "_x", self.old_password,
                                  self.new_password)
        assert code != 200

        code, new_token = self.auth.login(self.user_id, self.new_password,
                                          self.terminal)
        assert code != 200

# if __name__=="__main__":
#     test=TestPassword()
#     test.pre_run_initialization()
#    # test.test_cancel_paid_order_refund_ok()
#     test.test_ok()