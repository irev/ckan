# encoding: utf-8

import pytest

from ckan import model


@pytest.mark.usefixtures(u"clean_db", u"with_request_context")
class TestPackage(object):
    def test_create(self):
        # Demonstrate creating a package.
        #
        # In practice this is done by a combination of:
        # * ckan.logic.action.create:package_create
        # * ckan.lib.dictization.model_save.py:package_dict_save
        # etc

        pkg = model.Package(name=u"test-package")
        pkg.notes = u"Some notes"
        pkg.author = u"bob"
        pkg.license_id = u"odc-by"

        model.Session.add(pkg)
        model.Session.commit()
        model.Session.remove()

        pkg = model.Package.by_name(u"test-package")
        assert pkg.notes == u"Some notes"
        assert pkg.author == u"bob"
        assert pkg.license_id == u"odc-by"
        assert pkg.license.title == u"Open Data Commons Attribution License"

    def test_as_dict(self):
        pkg = model.Package.by_name(factories.Dataset(license_id="cc-by")["name"])
        out = pkg.as_dict()
        assert out["name"] == pkg.name
        assert out["license"] == pkg.license.title
        assert out["license_id"] == pkg.license.id
        assert out["tags"] == [tag.name for tag in pkg.get_tags()]
        assert out["metadata_modified"] == pkg.metadata_modified.isoformat()
        assert out["metadata_created"] == pkg.metadata_created.isoformat()
        assert out["notes"] == pkg.notes

    def test_update(self, package):
        pkg = model.Package.by_name(package[u"name"])

        pkg.author = u"bob"
        model.Session.commit()
        model.Session.remove()

        pkg = model.Package.by_name(package[u"name"])
        assert pkg.author == u"bob"

    def test_delete(self, group, package_factory):
        dataset = package_factory(
            groups=[{u"id": group[u"id"]}],
            tags=[{u"name": u"science"}],
            extras=[{u"key": u"subject", u"value": u"science"}],
        )
        pkg = model.Package.by_name(dataset[u"name"])

        pkg.delete()
        model.Session.commit()
        model.Session.remove()

        pkg = model.Package.by_name(dataset[u"name"])
        assert pkg.state == u"deleted"
        # it is removed from the group
        group = model.Group.get(group["id"])
        assert [p.name for p in group.packages()] == []
        # other related objects don't change
        package_extra = model.Session.query(model.PackageExtra).all()[0]
        assert package_extra.state == u"active"
        package_tag = model.Session.query(model.PackageTag).all()[0]
        assert package_tag.state == u"active"
        tag = model.Session.query(model.Tag).all()[0]
        assert [p.name for p in tag.packages] == [dataset[u"name"]]

    def test_purge(self, group, organization_factory, package_factory):
        organization = organization_factory()
        dataset = package_factory(
            resources=[
                {
                    u"url": u"http://example.com/image.png",
                    u"format": u"png",
                    u"name": u"Image 1",
                }
            ],
            tags=[{u"name": u"science"}],
            extras=[{u"key": u"subject", u"value": u"science"}],
            groups=[{u"id": group[u"id"]}],
            owner_org=organization[u"id"],
        )
        pkg = model.Package.by_name(dataset[u"name"])

        pkg.purge()
        model.Session.commit()
        model.Session.remove()

        assert not model.Session.query(model.Package).all()
        # the purge cascades to some objects
        assert not model.Session.query(model.PackageExtra).all()
        assert not model.Session.query(model.PackageTag).all()
        assert not model.Session.query(model.Resource).all()
        # org remains, just not attached to the package
        organization = model.Group.get(organization[u"id"])
        assert organization.packages() == []
        # tag object remains, just not attached to the package
        tag = model.Session.query(model.Tag).all()[0]
        assert tag.packages == []
        # group object remains, just not attached to the package
        group = model.Group.get(group[u"id"])
        assert group.packages() == []
