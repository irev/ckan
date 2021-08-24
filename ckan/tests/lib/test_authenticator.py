# encoding: utf-8

import pytest
from ckan.lib.authenticator import UsernamePasswordAuthenticator


class TestUsernamePasswordAuthenticator(object):
    @pytest.mark.usefixtures("clean_db")
    def test_succeeds_if_login_and_password_are_correct(self, user_factory):
        password = "somepass"
        user = user_factory(password=password)
        identity = {"login": user["name"], "password": password}
        assert (
            UsernamePasswordAuthenticator().authenticate({}, identity)
            == user["name"]
        )

    @pytest.mark.usefixtures("clean_db")
    def test_fails_if_user_is_deleted(self, user_factory):
        password = "somepass"
        user = user_factory(password=password, state="deleted")
        identity = {"login": user["name"], "password": password}
        assert (
            UsernamePasswordAuthenticator().authenticate({}, identity) is None
        )

    @pytest.mark.usefixtures("clean_db")
    def test_fails_if_user_is_pending(self, user_factory):
        password = "somepass"
        user = user_factory(password=password, state="pending")
        identity = {"login": user["name"], "password": password}
        assert (
            UsernamePasswordAuthenticator().authenticate({}, identity) is None
        )

    @pytest.mark.usefixtures("clean_db")
    def test_fails_if_password_is_wrong(self, user):
        identity = {"login": user["name"], "password": "wrong-password"}
        assert (
            UsernamePasswordAuthenticator().authenticate({}, identity) is None
        )

    @pytest.mark.parametrize(
        "identity",
        [
            {},
            {"login": "some-user"},
            {"password": "some-password"},
        ],
    )
    def test_fails_if_received_no_login_or_pass(self, identity):
        assert (
            UsernamePasswordAuthenticator().authenticate({}, identity) is None
        )
