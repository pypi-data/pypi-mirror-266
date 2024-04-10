from typing import Iterable

from fused._constants import DEFAULT_SHOW_TABLE_NAMES

from .api import Dataset
from .viz import VizConfig


def _show_naip_preset(
    dataset: Dataset,
    output_table_name: str,
    asset_column_name: str = "tiff_url",
    r_column_name: str = "r",
    g_column_name: str = "g",
    b_column_name: str = "b",
    circle_size: float = 10.0,
    other_tables: Iterable[str] = DEFAULT_SHOW_TABLE_NAMES,
) -> str:
    dataset_config = VizConfig()
    dataset_config.selected_columns = {"geometry": True}
    dataset_config.column_names.assets = asset_column_name
    dataset_config.layer_config.r_channel = r_column_name
    dataset_config.layer_config.g_channel = g_column_name
    dataset_config.layer_config.b_channel = b_column_name
    dataset_config.raster_band_indexes = [1, 2, 3]
    dataset_config.raster_source_type = "naip"
    dataset_config.layer_config.data_circles.radiusMinPixels = circle_size
    dataset_config.layer_config.data_circles.radiusMaxPixels = circle_size
    return dataset.show(
        dataset_config=dataset_config, tables=[*other_tables, output_table_name]
    )
