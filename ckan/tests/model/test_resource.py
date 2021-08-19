# encoding: utf-8

import pytest

import ckan.model as model

Resource = model.Resource


@pytest.mark.usefixtures("clean_db")
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

    def test_package_deletion_does_not_delete_resources(self):
        parent = factories.Dataset()
        factories.Resource(package_id=parent["id"])
        factories.Resource(package_id=parent["id"])

        assert model.Resource.active().count() == 2

        pkg = model.Package.get(parent["id"])
        pkg.delete()
        model.repo.commit_and_remove()

        assert model.Resource.active().count() == 2

    def test_package_purge_deletes_resources(self):
        parent = factories.Dataset()
        res1 = factories.Resource(package_id=parent["id"])
        res2 = factories.Resource(package_id=parent["id"])

        pkg = model.Package.get(parent["id"])
        pkg.purge()
        model.repo.commit_and_remove()

        assert model.Resource.active().count() == 0
