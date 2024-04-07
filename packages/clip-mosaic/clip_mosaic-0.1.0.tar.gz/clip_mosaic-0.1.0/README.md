# Clip Mosaic

Clip & Mosaic multiple TIFF Images with shapefiles.

Python>=3.10

GDAL, rasterio and geopandas must be installed before using

It is recommended that all the tifs to be mosaiced have the same projection, resolution and other metadata. Otherwise, uncertain errors may occur or undesired results may be obtained.

Usage:
```python
# testdata is the folder containing the tif images
from clip_mosaic import ClipMosaic
clipper = ClipMosaic('testdata', True)
clipper.clip_by_shp('testdata/testrange.shp', 'test_clip.tif')
```

Please read the source code (which is clearly written and easily understood) for more usage. :D