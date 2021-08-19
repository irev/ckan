# encoding: utf-8

import pytest

from ckan import model
from ckan.model.system_info import SystemInfo, set_system_info


@pytest.mark.usefixtures("clean_db")
class TestSystemInfo(object):
    def test_set_value(self):

        key = "config_option_1"
        value = "test_value"
        set_system_info(key, value)

        results = model.Session.query(SystemInfo).filter_by(key=key).all()

        assert len(results) == 1

        obj = results[0]

        assert obj.key == key
        assert obj.value == value

    def test_sets_new_value_for_same_key(self, system_info_factory):

        config = system_info_factory()
        config = system_info_factory()

        new_config = (
            model.Session.query(SystemInfo).filter_by(key=config.key).first()
        )

        assert config.id == new_config.id

        assert config.id == new_config.id

    def test_does_not_set_same_value_for_same_key(self, system_info):
        set_system_info(system_info.key, system_info.value)

        new_config = (
            model.Session.query(SystemInfo).filter_by(key=system_info.key).first()
        )

        assert system_info.id == new_config.id
