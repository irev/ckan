# encoding: utf-8

import pytest

from ckan.lib.helpers import url_for


@pytest.mark.ckan_config('ckan.views.default_views', '')
@pytest.mark.ckan_config("ckan.plugins", "video_view")
@pytest.mark.usefixtures("clean_db", "with_plugins")
def test_view_shown_on_resource_page_with_video_url(app, package, resource_factory, resource_view_factory):

    resource = resource_factory(package_id=package['id'],
                                  format='mp4')

    resource_view = resource_view_factory(
        resource_id=resource['id'],
        view_type='video_view',
        video_url='https://example/video.mp4')

    url = url_for('{}_resource.read'.format(package['type']),
                  id=package['name'], resource_id=resource['id'])

    response = app.get(url)

    assert resource_view['video_url'] in response
