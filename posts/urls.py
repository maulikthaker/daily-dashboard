from django.conf.urls import url

from . import views


urlpatterns = [

    url(r'^$', views.walkscore),
    url(r'^walkscore/$', views.walkscore),
    url(r'^deals/$', views.deals),
    url(r'^es/$', views.es),
    url(r'^tagbuilder/$', views.tagbuilder)

]
