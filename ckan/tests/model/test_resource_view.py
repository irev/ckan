# encoding: utf-8

import pytest

import ckan.model as model

ResourceView = model.ResourceView


@pytest.mark.ckan_config("ckan.plugins", "image_view webpage_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
class TestResourceView(object):
    def test_resource_view_get(self, resource_view):
        obj = ResourceView.get(resource_view["id"])

        assert obj is not None

    def test_get_count_view_type(self, resource_view_factory):
        resource_view_factory(view_type="image_view")
        resource_view_factory(view_type="webpage_view")

        result = ResourceView.get_count_not_in_view_types(["image_view"])

        assert result == [("webpage_view", 1)]

    def test_delete_view_type(self, resource_view_factory):
        resource_view_factory(view_type="image_view")
        resource_view_factory(view_type="webpage_view")

        ResourceView.delete_not_in_view_types(["image_view"])

        result = ResourceView.get_count_not_in_view_types(["image_view"])
        assert result == []

    def test_delete_view_type_doesnt_commit(self, resource_view_factory):
        resource_view_factory(view_type="image_view")
        resource_view_factory(view_type="webpage_view")

        ResourceView.delete_not_in_view_types(["image_view"])
        model.Session.rollback()

        result = ResourceView.get_count_not_in_view_types(["image_view"])
        assert result == [("webpage_view", 1)]

    def test_purging_resource_removes_its_resource_views(self, resource_view):
        resource = model.Resource.get(resource_view["resource_id"])

        resource.purge()
        model.repo.commit_and_remove()

        assert ResourceView.get(resource_view["id"]) is None
