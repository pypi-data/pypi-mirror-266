from mysqld_integration_test import Mysqld
import pytest
import getpass


@pytest.mark.slow
@pytest.mark.integration_test
@pytest.mark.integration_mariadb_test
def test_mysqld_run_mariadb():
    mysqld = Mysqld(mysqld_binary='tests/data/binaries/mariadb/mysqld',
                    mysql_install_db_binary='tests/data/binaries/mariadb/mysql_install_db')
    instance = mysqld.run()
    assert instance.username == getpass.getuser()
