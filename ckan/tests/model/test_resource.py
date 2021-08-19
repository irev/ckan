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

    def test_package_deletion_does_not_delete_resources(self, package, resource_factory):
        resource_factory(package_id=package["id"])
        resource_factory(package_id=package["id"])

        assert model.Resource.active().count() == 2

        pkg = model.Package.get(package["id"])
        pkg.delete()
        model.repo.commit_and_remove()

        assert model.Resource.active().count() == 2

    def test_package_purge_deletes_resources(self, package, resource_factory):
        res1 = resource_factory(package_id=package["id"])
        res2 = resource_factory(package_id=package["id"])

        pkg = model.Package.get(package["id"])
        pkg.purge()
        model.repo.commit_and_remove()

        assert model.Resource.active().count() == 0
