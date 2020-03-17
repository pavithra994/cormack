#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView
from django.views.static import serve as static_serve
from api import views
from api import viewsets
#from api.admin import event_admin_site
from api.admin import event_admin_site
from api.router import urlpatterns as api_routes
from ocom_xero.router import urlpatterns as xero_routes
from ocom import urls as auth_urls
from query.router import urlpatterns as query_routes
# from reports.views import ReportsStaticProxyView, ReportsProxyView

admin.autodiscover()
static_folder = '/images/' if settings.DEBUG else '/static/images/'

urlpatterns = [
                  url(r'^$', RedirectView.as_view(url='/index/'), name='home'),
                  url(r'^api/', include(api_routes)),
                  url(r'^query/', include(query_routes)),
                  url(r'^xero/', include(xero_routes)),
                  url(r'^', include(auth_urls)),
                  url(r'^index/$', views.home, name='home'),
                #   url(r'^admin/auth/user/(.*)/delete/',  RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-192x192.png'),
                                        #    permanent=False)),
                #   url(r'^adm/auth/user/(.*)/delete/',  RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-192x192.png'),
                                        #    permanent=False)),
                #   url(r'^adm/auth/user/',  viewsets.UserViewSet),

                  url(r'^adm/', include(admin.site.urls)),

                  # url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
                  url(r'^ocom_admin/', include(event_admin_site.urls)), # Admin Auth stuff

                  url(r'^dockerStatus/', views.docker_status),
                  url(r'^(images/)?favicon.ico$',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'favicon.ico'), permanent=False),
                      name="favicon"),
                  url(r'^(images/)?android-icon-36x36.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-36x36.png'),
                                           permanent=False)),
                  url(r'^(images/)?android-icon-48x48.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-48x48.png'),
                                           permanent=False)),
                  url(r'^(images/)?android-icon-72x72.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-72x72.png'),
                                           permanent=False)),
                  url(r'^(images/)?android-icon-96x96.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-96x96.png'),
                                           permanent=False)),
                  url(r'^(images/)?android-icon-144x144.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-144x144.png'),
                                           permanent=False)),
                  url(r'^(images/)?android-icon-192x192.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'android-icon-192x192.png'),
                                           permanent=False)),
                  url(r'^(images/)?browserconfig.xml',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'browserconfig.xml'),
                                           permanent=False)),
                  url(r'^(images/)?manifest.json',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'manifest.json'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-57x57.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-57x57.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-60x60.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-60x60.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-72x72.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-72x72.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-76x76.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-76x76.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-114x114.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-114x114.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-120x120.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-120x120.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-144x144.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-144x144.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-152x152.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-152x152.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-180x180.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-180x180.png'),
                                           permanent=False)),
                  url(r'^(images/)?apple-icon-precomposed.png',
                      RedirectView.as_view(url=staticfiles_storage.url(static_folder + 'apple-icon-precomposed.png'),
                                           permanent=False)),
                  # Change Password URLs
                  url(r'^rest-auth/', include('rest_auth.urls')),
                  url(r'^fetch-emails/', views.fetch_new_mails),
                  url(r'^send-email/', views.SendEmailAPI.as_view()),
                  url(r'^file/(?P<file_id>.*)$', views.redirect_original, name='redirectoriginal'),
                  url(r'^notification/(?P<url_id>.*)$', views.redirect_notification, name='redirectnotification'),
                  # url(r'^reports/(?P<path>.*)$', ReportsProxyView.as_view()),
                  # url(r'^report_static/(?P<path>.*)$', ReportsStaticProxyView.as_view()),

                  # URL for new UIs
                  url(r"^ui/$", static_serve, kwargs={ "path": "index.html", "document_root": settings.BASE_DIR + "/ui" }),
                  url(r"^ui/(?P<path>.+(js|map))$", static_serve, kwargs={ "document_root": settings.BASE_DIR + "/ui" }),
                  url(r"^ui/.+(?:(?!js|map))$", static_serve, kwargs={ "path": "index.html", "document_root": settings.BASE_DIR + "/ui" })
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
