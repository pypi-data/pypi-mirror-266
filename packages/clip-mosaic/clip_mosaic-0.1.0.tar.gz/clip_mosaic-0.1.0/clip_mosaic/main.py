import os, glob

import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.merge import merge
from shapely.geometry import Polygon, box

from typing import Literal
import warnings

class ClipMosaic:
    def __init__(self,
                 tifs: str or list,
                 is_directory: bool = True,
                 raster_suffix: str = '.tif',
                 crs: int = None,
                 save_when_clip: bool = True) -> None:
        """

        :param tifs:
        :param is_directory:
        :param raster_suffix:
        """
        self.province_name = None
        self.save_when_clip = save_when_clip
        if is_directory:
            self.tif_files = glob.glob(f'{tifs}/*{raster_suffix}')
        else:
            self.tif_files = tifs

        bounds = []
        for file in self.tif_files:
            with rasterio.open(file) as src:
                bounds.append(src.bounds)
                del src
        # shapely.geometry.box: convert bbox to polygon
        bounds = [box(*b) for b in bounds]

        if not crs is None:
            crs = crs
        else:
            with rasterio.open(self.tif_files[0]).src:
                crs = src.crs
                del src

        self.tiff_boxs = gpd.GeoDataFrame(self.tif_files, columns=['filename'], geometry=gpd.GeoSeries(bounds), crs=crs)
        # self.tiff_boxs.sindex
        return


    def __clip_to_bound(self,
                        in_range: Polygon,
                        mode: str,
                        out_path: str = None,
                        **kwargs) -> int or tuple:
        intersected_tifs = self.tiff_boxs.loc[self.tiff_boxs.intersects(in_range)].filename.values.tolist()
        masked_datasets = []

        for tif_path in intersected_tifs:
            with rasterio.open(tif_path) as src:
                out_image, out_transform = mask(src, [in_range], crop=True)
                # 创建一个新的内存中的数据集
                out_meta = src.meta
                out_meta.update({
                    "driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform
                    })
                masked_ds = rasterio.io.MemoryFile().open(**out_meta)
                masked_ds.write(out_image)
                masked_datasets.append(masked_ds)

        if len(masked_datasets) == 0:
            warnings.warn(f'No tif files intersected with {in_range}')
            return 0
        else:
            # if self.province_name == 'heilongjiang':
            #     merged_array, merged_transform = merge(masked_datasets,
            #                                            res = (masked_datasets[-1].meta['transform'][0], -masked_datasets[
            #                                                -1].meta['transform'][4]))
            #     out_meta = masked_datasets[-1].meta.copy()
            # else:
            merged_array, merged_transform = merge(masked_datasets)
            out_meta = masked_datasets[0].meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": merged_array.shape[1],
                "width": merged_array.shape[2],
                "transform": merged_transform,
                "count": merged_array.shape[0],
                "crs":4326
                })
            out_meta.update(kwargs)
            if not self.save_when_clip:
                return merged_array, out_meta
            with rasterio.open(out_path, 'w', compress = 'LZW', **out_meta) as dest:
                dest.write(merged_array)
            return 1


    def clip_by_shp(self,
                    shp: str,
                    out_path: str = None,
                    mosaic_mode: Literal['max', 'min', 'first', 'last'] = 'max',
                    **kwargs) -> int:
        assert os.path.exists(shp), "Shapefile does not exist"
        if out_path is None and self.save_when_clip == True:
            raise RuntimeError()
        try:
            shp_gdf = gpd.read_file(shp)
            # for testing
            # shp_gdf = shp_gdf.to_crs(self.tiff_boxs.crs)
            geom = shp_gdf.unary_union
            result = self.__clip_to_bound(geom, out_path, mosaic_mode, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(str(e))


    def clip_by_bbox(self,
                     bbox: tuple or list,
                     out_path: str = None,
                     mosaic_mode: Literal['max', 'min', 'first', 'last'] = 'max',
                     **kwargs) -> int:
        assert len(bbox) == 4, "Bounding box must have 4 values"
        if out_path is None and self.save_when_clip == True:
            raise RuntimeError()
        try:
            in_range = box(*bbox)
            result = self.__clip_to_bound(in_range, out_path, mosaic_mode, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(str(e))

    def clip_by_geom(self,
                     geom: Polygon,
                     out_path: str = None,
                     mosaic_mode: Literal['max', 'min', 'first', 'last'] = 'max',
                     **kwargs) -> int:
        if out_path is None and self.save_when_clip == True:
            raise RuntimeError()
        try:
            result = self.__clip_to_bound(geom, out_path, mosaic_mode, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(str(e))