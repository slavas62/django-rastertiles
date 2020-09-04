import mapnik
from mapnik import Gdal, Layer, Style, Rule, RasterSymbolizer, RasterColorizer
from sphericalmercator import SphericalMercator
from django.contrib.gis.gdal import GDALRaster

class DefaultStyler(object):
    style_name = 'raster'
    
    def __init__(self, raster):
        self.raster = raster
        self.srs = self.raster.srs.proj.encode()
        
    def get_styles(self):
        s = Style()
        r = Rule()
        symbolizer = RasterSymbolizer()
        r.symbols.append(symbolizer)
        s.rules.append(r)
        return [(self.style_name, s)]

    def get_layers(self):
        lyr = Layer('Tiff Layer')
        lyr.datasource = Gdal(file=self.raster.name, nodata=0, shared=True)
        lyr.srs = self.srs
        lyr.styles.append(self.style_name)
        return [lyr]
    
class ByBandStyler(DefaultStyler):
    band_colors = ['#f00', '#0f0', '#00f']
    
    def __init__(self, raster):
        super(ByBandStyler, self).__init__(raster)
        self.band_nums = zip(*enumerate(self.raster.bands, 1))[0][:3]
    
    def get_band_style_name(self, band_num):
        return 'band_%s' % band_num

    def get_band_style(self, band_num):
        s = Style()
        r = Rule()
        symbolizer = RasterSymbolizer()
        
        band = self.raster.bands[band_num-1]
        colorizer = RasterColorizer()
        
        colorizer.default_mode = mapnik.COLORIZER_LINEAR
        
        colorizer.add_stop(band.min, mapnik.COLORIZER_LINEAR, mapnik.Color('#000'))
        colorizer.add_stop(band.max, mapnik.COLORIZER_DISCRETE, mapnik.Color(self.band_colors[band_num-1]))

        symbolizer.colorizer = colorizer
        
        s.comp_op = mapnik.CompositeOp.plus
        
        r.symbols.append(symbolizer)
        s.rules.append(r)
        return self.get_band_style_name(band_num), s

    def get_styles(self):
        styles = []
        for band_num in self.band_nums:
            styles.append(self.get_band_style(band_num))
        return styles

    def get_band_layer(self, band_num):
        lyr = Layer('Tiff Layer')
        lyr.datasource = Gdal(file=self.raster.name, band=band_num, nodata=0, shared=True)
        lyr.srs = self.srs
        lyr.styles.append(self.get_band_style_name(band_num))
        return lyr
    
    def get_layers(self):
        layers = []
        for band_num in self.band_nums:
            layers.append(self.get_band_layer(band_num))
        return layers

class ByBandStylerGrayScale(ByBandStyler):
    band_colors = ['#fff']

def styler_factory(raster):
    if raster.bands[0].datatype() != 1:
        if len(raster.bands) == 1:
            return ByBandStylerGrayScale(raster)
        return ByBandStyler(raster) 
    return DefaultStyler(raster)

class RasterTiler(object):
    
    PROJ = '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs'
    STYLE_NAME = 'style'
    
    def __init__(self, image_path, zoom_levels=18, tile_size=256):
        self.image_path = image_path
        self.zoom_levels = zoom_levels
        self.tile_size = tile_size
        self.raster = GDALRaster(self.image_path)
        self.styler = styler_factory(self.raster)
        self.map = self.get_map()

    def __del__(self):
        #hack for garbage collector. see https://code.djangoproject.com/ticket/25072
        del self.raster.bands
        
    def get_map(self):
        m = mapnik.Map(256,256)
        m.srs = self.PROJ
        for l in self.styler.get_layers():
            m.layers.append(l)
        for style_name, style in self.styler.get_styles():
            m.append_style(style_name, style)
        return m
    
    def get_tile(self, x, y, z):
        proj = mapnik.Projection(self.PROJ)
        merc = SphericalMercator(self.zoom_levels, self.tile_size)
        bbox = proj.forward(mapnik.Box2d(*merc.xyz_to_envelope(x, y, z)))
        self.map.zoom_to_box(bbox)
        
        image = mapnik.Image(self.map.width, self.map.height)
        mapnik.render(self.map, image)
        
        return image
