# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import pytest
from ckan.lib.helpers import url_for


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_package_search(app, group, package_factory):
    all_numbers = [
        dataset["name"].rsplit("_", 1)[-1]
        for dataset in package_factory.create_batch(51, groups=[{"name": group["name"]}])
    ]
    resp = app.get(url_for("dataset.search", q=f"groups:{group['name']}"))
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=2)["href"]
    assert f'/dataset/?q=groups%3A{group["name"]}&page=2' == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .dataset-heading a")
    ]
    assert all_numbers[:-21:-1] == numbers

    resp = app.get(
        url_for("dataset.search", q=f"groups:{group['name']}", page=2)
    )
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=1)["href"]
    assert f'/dataset/?q=groups%3A{group["name"]}&page=1' == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .dataset-heading a")
    ]
    assert all_numbers[-21:-41:-1] == numbers


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_group_datasets_read(app, group, package_factory):
    all_numbers = [
        dataset["name"].rsplit("_", 1)[-1]
        for dataset in package_factory.create_batch(51, groups=[{"name": group["name"]}])
    ]
    resp = app.get(
        url_for(controller="group", action="read", id=group["name"])
    )
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=2)["href"]

    assert f'/group/{group["name"]}?page=2' == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .dataset-heading a")
    ]
    assert all_numbers[:-21:-1] == numbers

    resp = app.get(
        url_for(controller="group", action="read", id=group["name"], page=2)
    )
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=1)["href"]

    assert f'/group/{group["name"]}?page=1' == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .dataset-heading a")
    ]
    assert all_numbers[-21:-41:-1] == numbers


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_group_index(app, group_factory):
    all_numbers = [
        group["name"].rsplit("_", 1)[-1]
        for group in group_factory.create_batch(22)
    ]

    resp = app.get(url_for("group.index"))
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=2)["href"]
    assert "/group/?q=&sort=&page=2" == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .media-view")
    ]

    assert all_numbers[:20] == numbers

    resp = app.get(url_for("group.index", page=2))
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=1)["href"]
    assert "/group/?q=&sort=&page=1" == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .media-view")
    ]
    assert all_numbers[20:] == numbers


@pytest.mark.usefixtures("clean_db", "clean_index")
def test_users_index(app, user_factory):
    all_numbers = [
        user["name"].rsplit("_", 1)[-1]
        for user in user_factory.create_batch(21)
    ]
    resp = app.get(url_for("user.index"))
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=2)["href"]
    assert "/user/?q=&order_by=name&page=2" == href
    # this page will list default user, created after db reset,
    # that is skipped by our scraper. So, actually there 20 items,
    # but only 19 of them have been caught by regExp
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .user-list a")
    ][1:]

    assert all_numbers[:19] == numbers

    resp = app.get(url_for("user.index", page=2))
    page = BeautifulSoup(resp.data)
    href = page.select_one(".pagination").find("a", text=1)["href"]
    assert "/user/?q=&order_by=name&page=1" == href
    numbers = [
        link["href"].rsplit("_", 1)[-1]
        for link in page.select(".primary .user-list a")
    ]

    assert all_numbers[19:] == numbers
