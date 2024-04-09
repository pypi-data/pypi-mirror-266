from mysqld_integration_test import Mysqld
import pytest


@pytest.mark.skip
@pytest.mark.integration_test
@pytest.mark.integration_mysql_test
def test_mysqld_run_mysql():
    mysqld = Mysqld(mysqld_binary='tests/data/binaries/mysql/mysqld')
    instance = mysqld.run()
    assert instance.username == 'root'
