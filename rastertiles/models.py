import os
import tempfile
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
# from django.core.urlresolvers import reverse
from django.urls import reverse # fix
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal.error import GDALException
from django.utils.translation import gettext_lazy as _ # fix
from .statistics import band_statistics

STORAGE = getattr(settings, 'RASTERTILES_STORAGE', None)

'''
hack for preventing creating new migrations on change location of storage.
see https://code.djangoproject.com/ticket/24648
''' 
class FileField(models.FileField):
    def deconstruct(self):
        name, path, args, kwargs = super(FileField, self).deconstruct() 
        kwargs.pop('storage', None)
        return name, path, args, kwargs

class RasterFile(models.Model):
    file = FileField(upload_to='rasters', storage=STORAGE)
    zoom_levels = models.PositiveSmallIntegerField(default=18)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __unicode__(self):
        return u'RasterFile <%s>' % self.file

    def clean(self):
        file = self.file.file
        if hasattr(file, 'temporary_file_path'):
            filepath = file.temporary_file_path()
        else:
            tmp = tempfile.NamedTemporaryFile()
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp.flush()
            filepath = tmp.name
        try:
            GDALRaster(filepath)
        except GDALException:
            raise ValidationError({'file': _('Uploaded file is not valid raster image')})

    def save(self, *args, **kwargs):
        self.clean()
        super(RasterFile, self).save(*args, **kwargs)
        raster = GDALRaster(self.file.path)
        for band in raster.bands:
            band_statistics(band)
        del raster.bands #hack for garbage collector. see https://code.djangoproject.com/ticket/25072

    def get_tiles_uri_template(self):
        tile_uri = reverse('raster_tile', args=(self.pk, '0', '0', '0'))
        tiles_uri_template = tile_uri.replace('/0/0/0', '/{z}/{x}/{y}')
        return tiles_uri_template

    @property
    def filename(self):
        return os.path.basename(self.file.path)

    @property
    def extent_poly(self):
        gr = GDALRaster(self.file.path)
        poly = Polygon.from_bbox(gr.extent)
        poly.srid = gr.srs.srid
        return poly.transform(4326, clone=True)

    @property
    def extent(self):
        return self.extent_poly.extent


@receiver(post_delete, sender=RasterFile)
def remove_file_on_rasterfile_delete(sender, instance, **kwargs):
    if instance.file:
        aux_file = '%s.aux.xml' % instance.file.name
        instance.file.delete(save=False)
        instance.file.storage.delete(aux_file)
