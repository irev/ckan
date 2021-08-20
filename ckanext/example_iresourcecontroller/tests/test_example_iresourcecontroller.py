# encoding: utf-8

"""Tests for the ckanext.example_iauthfunctions extension.

"""
import pytest

import ckan.plugins
import ckan.tests.helpers as helpers


@pytest.mark.ckan_config("ckan.plugins", "example_iresourcecontroller")
@pytest.mark.usefixtures("clean_db", "with_plugins", "with_request_context")
class TestExampleIResourceController(object):
    """Tests for the plugin that uses IResourceController.

    """

    def test_resource_controller_plugin_create(self, sysadmin, package_factory):
        package = package_factory(user=sysadmin)

        plugin = ckan.plugins.get_plugin("example_iresourcecontroller")

        res = helpers.call_action(
            "resource_create",
            package_id=package["id"],
            name="test-resource",
            url="http://resource.create/",
            apikey=sysadmin["apikey"],
        )

        assert plugin.counter["before_create"] == 1, plugin.counter
        assert plugin.counter["after_create"] == 1, plugin.counter
        assert plugin.counter["before_update"] == 0, plugin.counter
        assert plugin.counter["after_update"] == 0, plugin.counter
        assert plugin.counter["before_delete"] == 0, plugin.counter
        assert plugin.counter["after_delete"] == 0, plugin.counter

    def test_resource_controller_plugin_update(self, sysadmin, resource_factory):
        resource = resource_factory(user=sysadmin)
        plugin = ckan.plugins.get_plugin("example_iresourcecontroller")

        res = helpers.call_action(
            "resource_update",
            id=resource["id"],
            url="http://resource.updated/",
            apikey=sysadmin["apikey"],
        )

        assert plugin.counter["before_create"] == 1, plugin.counter
        assert plugin.counter["after_create"] == 1, plugin.counter
        assert plugin.counter["before_update"] == 1, plugin.counter
        assert plugin.counter["after_update"] == 1, plugin.counter
        assert plugin.counter["before_delete"] == 0, plugin.counter
        assert plugin.counter["after_delete"] == 0, plugin.counter

    def test_resource_controller_plugin_delete(self, sysadmin, resource_factory):
        resource = resource_factory(user=sysadmin)

        plugin = ckan.plugins.get_plugin("example_iresourcecontroller")

        res = helpers.call_action(
            "resource_delete", id=resource["id"], apikey=sysadmin["apikey"]
        )

        assert plugin.counter["before_create"] == 1, plugin.counter
        assert plugin.counter["after_create"] == 1, plugin.counter
        assert plugin.counter["before_update"] == 0, plugin.counter
        assert plugin.counter["after_update"] == 0, plugin.counter
        assert plugin.counter["before_delete"] == 1, plugin.counter
        assert plugin.counter["after_delete"] == 1, plugin.counter

    def test_resource_controller_plugin_show(self, sysadmin, package_factory, resource_factory):
        """
        Before show gets called by the other methods but we test it
        separately here and make sure that it doesn't call the other
        methods.
        """
        package = package_factory(user=sysadmin)
        resource = resource_factory(user=sysadmin, package_id=package["id"])

        plugin = ckan.plugins.get_plugin("example_iresourcecontroller")

        res = helpers.call_action("package_show", name_or_id=package["id"])

        assert plugin.counter["before_create"] == 1, plugin.counter
        assert plugin.counter["after_create"] == 1, plugin.counter
        assert plugin.counter["before_update"] == 0, plugin.counter
        assert plugin.counter["after_update"] == 0, plugin.counter
        assert plugin.counter["before_delete"] == 0, plugin.counter
        assert plugin.counter["after_delete"] == 0, plugin.counter
        assert plugin.counter["before_show"] == 5, plugin.counter
