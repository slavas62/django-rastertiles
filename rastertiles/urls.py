from django.conf.urls import patterns, url
from .views import TileView, RasterOverviewView

urlpatterns = patterns('',
    url(r'^rasters/(?P<pk>\d+)/tiles/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)/$', TileView.as_view(), name='raster_tile'),
    url(r'^rasters/(?P<pk>\d+)/view/$', RasterOverviewView.as_view(), name='raster_overview'),
)