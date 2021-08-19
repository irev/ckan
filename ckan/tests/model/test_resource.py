# encoding: utf-8

import pytest

import ckan.model as model

Resource = model.Resource


@pytest.mark.ckan_config("ckan.plugins", "image_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestResource(object):
    def test_edit_url(self, resource_factory):
        res_dict = resource_factory(url="http://first")
        res = Resource.get(res_dict["id"])
        res.url = "http://second"
        model.repo.commit_and_remove()
        res = Resource.get(res_dict["id"])
        assert res.url == "http://second"

    def test_edit_extra(self, resource_factory):
        res_dict = resource_factory(newfield="first")
        res = Resource.get(res_dict["id"])
        res.extras = {"newfield": "second"}
        model.repo.commit_and_remove()
        res = Resource.get(res_dict["id"])
        assert res.extras["newfield"] == "second"

    def test_resource_count(self, resource_factory):
        """Resource.count() should return a count of instances of Resource
        class"""
        assert Resource.count() == 0
        resource_factory()
        resource_factory()
        resource_factory()
        assert Resource.count() == 3
