# encoding: utf-8

import pytest
import six
from bs4 import BeautifulSoup

import ckan.authz as authz
from ckan import model
from ckan.lib.helpers import url_for
from ckan.tests import helpers


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationNew(object):
    @pytest.fixture
    def user_env(self, user):
        return {"REMOTE_USER": six.ensure_str(user["name"])}

    def test_not_logged_in(self, app):
        app.get(url=url_for("group.new"), status=403)

    def test_name_required(self, app, user_env):
        response = app.post(
            url=url_for("organization.new"), extra_environ=user_env, data={"save": ""}
        )
        assert "Name: Missing value" in response

    def test_saved(self, app, user_env):
        response = app.post(
            url=url_for("organization.new"), extra_environ=user_env,
            data={"save": "", "name": "saved"}
        )
        group = helpers.call_action("organization_show", id="saved")
        assert group["title"] == u""
        assert group["type"] == "organization"
        assert group["state"] == "active"

    def test_all_fields_saved(self, app, user_env):
        response = app.post(
            url=url_for("organization.new"), extra_environ=user_env,
            data={
                "name": u"all-fields-saved",
                "title": "Science",
                "description": "Sciencey datasets",
                "image_url": "http://example.com/image.png",
                "save": ""
            }
        )
        group = helpers.call_action("organization_show", id="all-fields-saved")
        assert group["title"] == u"Science"
        assert group["description"] == "Sciencey datasets"


@pytest.mark.usefixtures("with_request_context")
class TestOrganizationList(object):
    @pytest.mark.usefixtures("clean_db")
    def test_error_message_shown_when_no_organization_list_permission(
            self, monkeypatch, app, user
    ):
        authz._AuthFunctions.get('organization_list')
        monkeypatch.setitem(
            authz._AuthFunctions._functions, 'organization_list',
            lambda *args: {'success': False})
        self.user = user
        self.user_env = {"REMOTE_USER": six.ensure_str(self.user["name"])}
        self.organization_list_url = url_for("organization.index")

        response = app.get(
            url=self.organization_list_url,
            extra_environ=self.user_env,
            status=403,
        )


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationRead(object):
    def test_group_read(self, app, organization):
        response = app.get(url=url_for("organization.read", id=organization["name"]))
        assert organization["title"] in response
        assert organization["description"] in response

    def test_read_redirect_when_given_id(self, app, organization):
        response = app.get(
            url_for("organization.read", id=organization["id"]), follow_redirects=False
        )
        # redirect replaces the ID with the name in the URL
        expected_url = url_for("organization.read", id=organization["name"], _external=True)
        assert response.headers['location'] == expected_url

    def test_no_redirect_loop_when_name_is_the_same_as_the_id(self, app, organization):
        app.get(
            url_for("organization.read", id=organization["id"]), status=200
        )  # ie no redirect


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationEdit(object):
    @pytest.fixture
    def initial_data(self, user, organization_factory):
        return {
            "user": user,
            "user_env": {"REMOTE_USER": six.ensure_str(user["name"])},
            "organization": organization_factory(user=user),
        }

    def test_group_doesnt_exist(self, app, initial_data):
        url = url_for("organization.edit", id="doesnt_exist")
        app.get(url=url, extra_environ=initial_data["user_env"], status=404)

    def test_saved(self, app, initial_data):
        response = app.post(
            url=url_for(
                "organization.edit", id=initial_data["organization"]["id"]
            ),
            extra_environ=initial_data["user_env"],
            data={"save": ""}
        )

        group = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert group["title"] == u"Test Organization"
        assert group["type"] == "organization"
        assert group["state"] == "active"

    def test_all_fields_saved(self, app, initial_data):
        response = app.post(
            url=url_for(
                "organization.edit", id=initial_data["organization"]["id"]
            ),
            extra_environ=initial_data["user_env"],
            data={
                "name": u"all-fields-edited",
                "title": "Science",
                "description": "Sciencey datasets",
                "image_url": "http://example.com/image.png",
                "save": ""
            }
        )
        group = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert group["title"] == u"Science"
        assert group["description"] == "Sciencey datasets"
        assert group["image_url"] == "http://example.com/image.png"


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationDelete(object):
    @pytest.fixture
    def initial_data(self, user, organization_factory):
        return {
            "user": user,
            "user_env": {"REMOTE_USER": six.ensure_str(user["name"])},
            "organization": organization_factory(user=user),
        }

    def test_owner_delete(self, app, initial_data):
        response = app.post(
            url=url_for(
                "organization.delete", id=initial_data["organization"]["id"]
            ),
            extra_environ=initial_data["user_env"],
            data={"delete": ""}
        )
        organization = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert organization["state"] == "deleted"

    def test_sysadmin_delete(self, app, initial_data, sysadmin):
        extra_environ = {"REMOTE_USER": six.ensure_str(sysadmin["name"])}
        response = app.post(
            url=url_for(
                "organization.delete", id=initial_data["organization"]["id"]
            ),
            status=200,
            extra_environ=extra_environ,
            data={"delete": ""}
        )
        organization = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert organization["state"] == "deleted"

    def test_non_authorized_user_trying_to_delete_fails(
            self, app, initial_data, user
    ):
        extra_environ = {"REMOTE_USER": six.ensure_str(user["name"])}
        app.post(
            url=url_for(
                "organization.delete", id=initial_data["organization"]["id"]
            ),
            status=403,
            extra_environ=extra_environ,
            data={"delete": ""}
        )

        organization = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert organization["state"] == "active"

    def test_anon_user_trying_to_delete_fails(self, app, initial_data):
        app.get(
            url=url_for(
                "organization.delete", id=initial_data["organization"]["id"]
            ),
            status=403,
        )

        organization = helpers.call_action(
            "organization_show", id=initial_data["organization"]["id"]
        )
        assert organization["state"] == "active"

    @pytest.mark.ckan_config("ckan.auth.create_unowned_dataset", False)
    def test_delete_organization_with_datasets(self, app, initial_data, package_factory):
        """ Test deletion of organization that has datasets"""
        text = "Organization cannot be deleted while it still has datasets"
        datasets = [
            package_factory(owner_org=initial_data["organization"]["id"])
            for i in range(0, 5)
        ]
        response = app.post(
            url=url_for(
                "organization.delete", id=initial_data["organization"]["id"]
            ),
            extra_environ=initial_data["user_env"],
            data={"delete": ""}
        )

        assert helpers.body_contains(response, text)

    def test_delete_organization_with_unknown_dataset_true(self, initial_data, user, package_factory):
        """ Test deletion of organization that has datasets and unknown
            datasets are set to true"""
        dataset = package_factory(
            owner_org=initial_data["organization"]["id"]
        )
        assert dataset["owner_org"] == initial_data["organization"]["id"]
        helpers.call_action(
            "organization_delete",
            id=initial_data["organization"]["id"],
            context={"user": user["name"]},
        )

        dataset = helpers.call_action("package_show", id=dataset["id"])
        assert dataset["owner_org"] is None


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationBulkProcess(object):
    def test_make_private(self, app, user, organization_factory, package_factory):
        self.user = user
        self.user_env = {"REMOTE_USER": six.ensure_str(self.user["name"])}
        self.organization = organization_factory(user=self.user)

        datasets = [
            package_factory(owner_org=self.organization["id"], private=False)
            for i in range(0, 5)
        ]
        form = {'dataset_' + d["id"]: "on" for d in datasets}
        form["bulk_action.private"] = "private"

        response = app.post(
            url=url_for(
                "organization.bulk_process", id=self.organization["id"]
            ),
            extra_environ=self.user_env,
            data=form
        )

        for dataset in datasets:
            d = helpers.call_action("package_show", id=dataset["id"])
            assert d["private"]

    def test_make_public(self, app, user, organization_factory, package_factory):
        self.user = user
        self.user_env = {"REMOTE_USER": six.ensure_str(self.user["name"])}
        self.organization = organization_factory(user=self.user)

        datasets = [
            package_factory(owner_org=self.organization["id"], private=True)
            for i in range(0, 5)
        ]
        form = {'dataset_' + d["id"]: "on" for d in datasets}
        form["bulk_action.public"] = "public"
        response = app.post(
            url=url_for(
                "organization.bulk_process", id=self.organization["id"]
            ),
            extra_environ=self.user_env,
            data=form
        )
        for dataset in datasets:
            d = helpers.call_action("package_show", id=dataset["id"])
            assert not (d["private"])

    def test_delete(self, app, user, organization_factory, package_factory):
        self.user = user
        self.user_env = {"REMOTE_USER": six.ensure_str(self.user["name"])}
        self.organization = organization_factory(user=self.user)
        datasets = [
            package_factory(owner_org=self.organization["id"], private=True)
            for i in range(0, 5)
        ]
        form = {'dataset_' + d["id"]: "on" for d in datasets}
        form["bulk_action.delete"] = "delete"

        response = app.post(
            url=url_for(
                "organization.bulk_process", id=self.organization["id"]
            ),
            extra_environ=self.user_env,

            data=form
        )

        for dataset in datasets:
            d = helpers.call_action("package_show", id=dataset["id"])
            assert d["state"] == "deleted"


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationSearch(object):
    """Test searching for organizations."""

    def test_organization_search(self, app, organization_factory):
        """Requesting organization search (index) returns list of
        organizations and search form."""

        organization_factory(name="org-one", title="AOrg One")
        organization_factory(name="org-two", title="AOrg Two")
        organization_factory(name="org-three", title="Org Three")

        index_response = app.get(url_for("organization.index"))
        index_response_html = BeautifulSoup(index_response.body)
        org_names = index_response_html.select(
            "ul.media-grid " "li.media-item " "h2.media-heading"
        )
        org_names = [n.string for n in org_names]

        assert len(org_names) == 3
        assert "AOrg One" in org_names
        assert "AOrg Two" in org_names
        assert "Org Three" in org_names

    def test_organization_search_results(self, app, organization_factory):
        """Searching via organization search form returns list of expected
        organizations."""
        organization_factory(name="org-one", title="AOrg One")
        organization_factory(name="org-two", title="AOrg Two")
        organization_factory(name="org-three", title="Org Three")

        search_response = app.get(
            url_for("organization.index"),
            query_string={"q": "AOrg"}
        )

        search_response_html = BeautifulSoup(search_response.body)
        org_names = search_response_html.select(
            "ul.media-grid " "li.media-item " "h2.media-heading"
        )
        org_names = [n.string for n in org_names]

        assert len(org_names) == 2
        assert "AOrg One" in org_names
        assert "AOrg Two" in org_names
        assert "Org Three" not in org_names

    def test_organization_search_no_results(self, app, organization_factory):
        """Searching with a term that doesn't apply returns no results."""
        organization_factory(name="org-one", title="AOrg One")
        organization_factory(name="org-two", title="AOrg Two")
        organization_factory(name="org-three", title="Org Three")

        search_response = app.get(
            url_for("organization.index"),
            query_string={"q": "No Results Here"}
        )

        search_response_html = BeautifulSoup(search_response.body)
        org_names = search_response_html.select(
            "ul.media-grid " "li.media-item " "h2.media-heading"
        )
        org_names = [n.string for n in org_names]

        assert len(org_names) == 0
        assert helpers.body_contains(
            search_response,
            'No organizations found for "No Results Here"'
        )


@pytest.mark.usefixtures("clean_db", "clean_index", "with_request_context")
class TestOrganizationInnerSearch(object):
    """Test searching within an organization."""

    def test_organization_search_within_org(self, app, package_factory, organization):
        """Organization read page request returns list of datasets owned by
        organization."""
        package_factory(
            name="ds-one", title="Dataset One", owner_org=organization["id"]
        )
        package_factory(
            name="ds-two", title="Dataset Two", owner_org=organization["id"]
        )
        package_factory(
            name="ds-three", title="Dataset Three", owner_org=organization["id"]
        )

        org_url = url_for("organization.read", id=organization["name"])
        org_response = app.get(org_url)
        org_response_html = BeautifulSoup(org_response.body)

        ds_titles = org_response_html.select(
            ".dataset-list " ".dataset-item " ".dataset-heading a"
        )
        ds_titles = [t.string for t in ds_titles]

        assert "3 datasets found" in org_response
        assert len(ds_titles) == 3
        assert "Dataset One" in ds_titles
        assert "Dataset Two" in ds_titles
        assert "Dataset Three" in ds_titles

    def test_organization_search_within_org_results(self, app, package_factory, organization):
        """Searching within an organization returns expected dataset
        results."""
        package_factory(
            name="ds-one", title="Dataset One", owner_org=organization["id"]
        )
        package_factory(
            name="ds-two", title="Dataset Two", owner_org=organization["id"]
        )
        package_factory(
            name="ds-three", title="Dataset Three", owner_org=organization["id"]
        )

        org_url = url_for("organization.read", id=organization["name"])
        search_response = app.get(
            org_url,
            query_string={"q": "One"}
        )
        assert "1 dataset found for &#34;One&#34;" in search_response

        search_response_html = BeautifulSoup(search_response.body)

        ds_titles = search_response_html.select(
            ".dataset-list " ".dataset-item " ".dataset-heading a"
        )
        ds_titles = [t.string for t in ds_titles]

        assert len(ds_titles) == 1
        assert "Dataset One" in ds_titles
        assert "Dataset Two" not in ds_titles
        assert "Dataset Three" not in ds_titles

    def test_organization_search_within_org_no_results(self, app, package_factory, organization):
        """Searching for non-returning phrase within an organization returns
        no results."""

        package_factory(
            name="ds-one", title="Dataset One", owner_org=organization["id"]
        )
        package_factory(
            name="ds-two", title="Dataset Two", owner_org=organization["id"]
        )
        package_factory(
            name="ds-three", title="Dataset Three", owner_org=organization["id"]
        )

        org_url = url_for("organization.read", id=organization["name"])
        search_response = app.get(
            org_url,
            query_string={"q": "Nout"}
        )

        assert helpers.body_contains(search_response, 'No datasets found for "Nout"')

        search_response_html = BeautifulSoup(search_response.body)

        ds_titles = search_response_html.select(
            ".dataset-list " ".dataset-item " ".dataset-heading a"
        )
        ds_titles = [t.string for t in ds_titles]

        assert len(ds_titles) == 0


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestOrganizationMembership(object):
    def test_editor_users_cannot_add_members(self, app, user, organization_factory):

        organization = organization_factory(
            users=[{"name": user["name"], "capacity": "editor"}]
        )

        env = {"REMOTE_USER": six.ensure_str(user["name"])}

        with app.flask_app.test_request_context():
            app.get(
                url_for("organization.member_new", id=organization["id"]),
                extra_environ=env,
                status=403,
            )

            app.post(
                url_for("organization.member_new", id=organization["id"]),
                data={
                    "id": "test",
                    "username": "test",
                    "save": "save",
                    "role": "test",
                },
                extra_environ=env,
                status=403,
            )

    def test_member_users_cannot_add_members(self, app, organization_factory, user):
        organization = organization_factory(
            users=[{"name": user["name"], "capacity": "member"}]
        )

        env = {"REMOTE_USER": six.ensure_str(user["name"])}

        with app.flask_app.test_request_context():
            app.get(
                url_for("organization.member_new", id=organization["id"]),
                extra_environ=env,
                status=403,
            )

            app.post(
                url_for("organization.member_new", id=organization["id"]),
                data={
                    "id": "test",
                    "username": "test",
                    "save": "save",
                    "role": "test",
                },
                extra_environ=env,
                status=403,
            )

    def test_anonymous_users_cannot_add_members(self, app, organization):

        with app.flask_app.test_request_context():
            app.get(
                url_for("organization.member_new", id=organization["id"]),
                status=403,
            )

            app.post(
                url_for("organization.member_new", id=organization["id"]),
                data={
                    "id": "test",
                    "username": "test",
                    "save": "save",
                    "role": "test",
                },
                status=403,
            )


@pytest.mark.usefixtures("clean_db", "with_request_context")
class TestActivity(object):
    def test_simple(self, app, organization_factory, user):
        """Checking the template shows the activity stream."""
        org = organization_factory(user=user)

        url = url_for("organization.activity", id=org["id"])
        response = app.get(url)
        assert "Mr. Test User" in response
        assert "created the organization" in response

    def test_create_organization(self, app, organization_factory, user):
        org = organization_factory(user=user)

        url = url_for("organization.activity", id=org["id"])
        response = app.get(url)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "created the organization" in response
        assert (
            '<a href="/organization/{}">Test Organization'.format(org["name"])
            in response
        )

    def _clear_activities(self):
        model.Session.query(model.ActivityDetail).delete()
        model.Session.query(model.Activity).delete()
        model.Session.flush()

    def test_change_organization(self, app, organization_factory, user):
        org = organization_factory(user=user)
        self._clear_activities()
        org["title"] = "Organization with changed title"
        helpers.call_action(
            "organization_update", context={"user": user["name"]}, **org
        )

        url = url_for("organization.activity", id=org["id"])
        response = app.get(url)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "updated the organization" in response
        assert (
            '<a href="/organization/{}">Organization with changed title'.format(
                org["name"]
            )
            in response
        )

    def test_delete_org_using_organization_delete(self, app, organization_factory, user):
        org = organization_factory(user=user)
        self._clear_activities()
        helpers.call_action(
            "organization_delete", context={"user": user["name"]}, **org
        )

        url = url_for("organization.activity", id=org["id"])
        env = {"REMOTE_USER": six.ensure_str(user["name"])}
        response = app.get(url, extra_environ=env, status=404)
        # organization_delete causes the Member to state=deleted and then the
        # user doesn't have permission to see their own deleted Organization.
        # Therefore you can't render the activity stream of that org. You'd
        # hope that organization_delete was the same as organization_update
        # state=deleted but they are not...

    def test_delete_org_by_updating_state(self, app, organization_factory):
        org = organization_factory(user=user)
        self._clear_activities()
        org["state"] = "deleted"
        helpers.call_action(
            "organization_update", context={"user": user["name"]}, **org
        )

        url = url_for("organization.activity", id=org["id"])
        env = {"REMOTE_USER": six.ensure_str(user["name"])}
        response = app.get(url, extra_environ=env)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "deleted the organization" in response
        assert (
            '<a href="/organization/{}">Test Organization'.format(org["name"])
            in response
        )

    def test_create_dataset(self, app, user, organization, package_factory):
        self._clear_activities()
        dataset = package_factory(owner_org=organization["id"], user=user)

        url = url_for("organization.activity", id=organization["id"])
        response = app.get(url)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "created the dataset" in response
        assert (
            '<a href="/dataset/{}">Test Dataset'.format(dataset["id"])
            in response
        )

    def test_change_dataset(self, app, package_factory, user, organization):
        dataset = package_factory(owner_org=organization["id"], user=user)
        self._clear_activities()
        dataset["title"] = "Dataset with changed title"
        helpers.call_action(
            "package_update", context={"user": user["name"]}, **dataset
        )

        url = url_for("organization.activity", id=organization["id"])
        response = app.get(url)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "updated the dataset" in response
        assert (
            '<a href="/dataset/{}">Dataset with changed title'.format(
                dataset["id"]
            )
            in response
        )

    def test_delete_dataset(self, app, package_factory, user, organization):
        dataset = package_factory(owner_org=organization["id"], user=user)
        self._clear_activities()
        helpers.call_action(
            "package_delete", context={"user": user["name"]}, **dataset
        )

        url = url_for("organization.activity", id=organization["id"])
        response = app.get(url)
        assert (
            '<a href="/user/{}">Mr. Test User'.format(user["name"]) in response
        )
        assert "deleted the dataset" in response
        assert (
            '<a href="/dataset/{}">Test Dataset'.format(dataset["id"])
            in response
        )
