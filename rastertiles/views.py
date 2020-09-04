from django.views.generic import DetailView
from django.http.response import HttpResponse, HttpResponseBadRequest
from sphericalmercator import WrongZoomException
from rastertiler import RasterTiler
from .models import RasterFile

class TileView(DetailView):
    model = RasterFile
    
    def dispatch(self, request, *args, **kwargs):
        return DetailView.dispatch(self, request, *args, **kwargs)
    
    def get(self, request, pk, z, x, y, *args, **kwargs):
        raster = self.get_object()
        z, x, y = int(z), int(x), int(y)
        try:
            tile = RasterTiler(raster.file.path, zoom_levels=raster.zoom_levels).get_tile(x, y, z)
        except WrongZoomException:
            return HttpResponseBadRequest('wrong zoom')
        return HttpResponse(tile.tostring('png'), content_type='image/png')

class RasterOverviewView(DetailView):
    model = RasterFile
    template_name = 'rastertiles/raster_view.html'
