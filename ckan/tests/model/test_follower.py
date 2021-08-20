# encoding: utf-8

import pytest
import ckan.model as model


class FollowerClassesTests(object):
    def test_get(self):
        following = self.FOLLOWER_CLASS.get(
            self.follower["id"], self.followee["id"]
        )
        assert following.follower_id == self.follower["id"], following
        assert following.object_id == self.followee["id"], following

    def test_get_returns_none_if_couldnt_find_users(self):
        following = self.FOLLOWER_CLASS.get("some-id", "other-id")
        assert following is None, following

    def test_is_following(self):
        assert self.FOLLOWER_CLASS.is_following(
            self.follower["id"], self.followee["id"]
        )

    def test_is_following_returns_false_if_user_isnt_following(self):
        assert not self.FOLLOWER_CLASS.is_following(
            self.followee["id"], self.follower["id"]
        )

    def test_followee_count(self):
        count = self.FOLLOWER_CLASS.followee_count(self.follower["id"])
        assert count == 1, count

    def test_followee_list(self):
        followees = self.FOLLOWER_CLASS.followee_list(self.follower["id"])
        object_ids = [f.object_id for f in followees]
        assert object_ids == [self.followee["id"]], object_ids

    def test_follower_count(self):
        count = self.FOLLOWER_CLASS.follower_count(self.followee["id"])
        assert count == 1, count

    def test_follower_list(self):
        followers = self.FOLLOWER_CLASS.follower_list(self.followee["id"])
        follower_ids = [f.follower_id for f in followers]
        assert follower_ids == [self.follower["id"]], follower_ids


class TestUserFollowingUser(FollowerClassesTests):
    FOLLOWER_CLASS = model.UserFollowingUser

    @pytest.fixture(autouse=True)
    def _before(self, clean_db, user_factory):
        self.follower = user_factory(name="follower")
        self.followee = user_factory(name="followee")
        self.FOLLOWER_CLASS(self.follower["id"], self.followee["id"]).save()

        deleted_user = user_factory(name="deleted_user")
        self.FOLLOWER_CLASS(deleted_user["id"], self.followee["id"]).save()
        self.FOLLOWER_CLASS(self.follower["id"], deleted_user["id"]).save()
        user = model.User.get(deleted_user["id"])
        user.delete()
        user.save()


class TestUserFollowingDataset(FollowerClassesTests):
    FOLLOWER_CLASS = model.UserFollowingDataset

    @pytest.fixture(autouse=True)
    def _before(self, clean_db, user_factory, package_factory):
        self.follower = user_factory(name="follower")
        self.followee = package_factory(name="followee")
        self.FOLLOWER_CLASS(self.follower["id"], self.followee["id"]).save()

        deleted_user = user_factory(name="deleted_user")
        self.FOLLOWER_CLASS(deleted_user["id"], self.followee["id"]).save()
        user = model.User.get(deleted_user["id"])
        user.delete()
        user.save()
        deleted_dataset = package_factory(name="deleted_dataset")
        self.FOLLOWER_CLASS(self.follower["id"], deleted_dataset["id"]).save()
        dataset = model.Package.get(deleted_dataset["id"])
        dataset.delete()
        dataset.save()


class TestUserFollowingGroup(FollowerClassesTests):
    FOLLOWER_CLASS = model.UserFollowingGroup

    @pytest.fixture(autouse=True)
    def _before(self, clean_db, user_factory, group_factory):
        self.follower = user_factory(name="follower")
        self.followee = group_factory(name="followee")
        self.FOLLOWER_CLASS(self.follower["id"], self.followee["id"]).save()

        deleted_user = user_factory(name="deleted_user")
        self.FOLLOWER_CLASS(deleted_user["id"], self.followee["id"]).save()
        user = model.User.get(deleted_user["id"])
        user.delete()
        user.save()

        deleted_group = group_factory(name="deleted_group")
        self.FOLLOWER_CLASS(self.follower["id"], deleted_group["id"]).save()
        group = model.Group.get(deleted_group["id"])
        group.delete()
        group.save()

        model.repo.commit_and_remove()
