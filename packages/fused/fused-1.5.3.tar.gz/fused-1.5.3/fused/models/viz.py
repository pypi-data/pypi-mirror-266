from typing import Any, Dict, List, Optional, Sequence

from pydantic import BaseModel, Field

from fused._constants import DEFAULT_SHOW_TABLE_NAMES

from .internal.dataset import DatasetInputV2
from .request import DebugMultiDatasetRequestDataset, MultiDebugSingleDatasetV2Request
from .urls import DatasetUrl


class LayerConfig(BaseModel):
    pass

    class Config:
        extra = "allow"


class CircleConfig(LayerConfig):
    radius_offset: Optional[float] = Field(None, alias="radiusOffset")
    radius_weight: Optional[float] = Field(None, alias="radiusWeight")
    radius_units: str = Field("meters", alias="radiusUnits")
    radius_min_pixels: int = Field(3, alias="radiusMinPixels")
    radius_max_pixels: int = Field(3, alias="radiusMaxPixels")


class VizLayerConfig(BaseModel):
    root_bboxes: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="rootBboxes"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/geojson-layer"""
    root_bbox_ids: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="rootBboxIds"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/text-layer"""
    root_points: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="rootPoints"
    )
    """Unused"""
    root_heatmap: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="rootHeatmap"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer"""
    selection_geojson: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="selectionGeojson"
    )
    """Properties as defined on https://nebula.gl/docs/api-reference/layers/editable-geojson-layer"""
    data_circles: CircleConfig = Field(
        default_factory=lambda: CircleConfig(), alias="dataCircles"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/scatterplot-layer"""

    root_bboxes_selected: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="rootBboxesSelected"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/geojson-layer"""
    data_bboxes: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="dataBboxes"
    )
    """Unused"""
    data_heatmap: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="dataHeatmap"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/aggregation-layers/heatmap-layer"""
    data_solid: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="dataSolid"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/solid-polygon-layer"""
    data_path: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="dataPath"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/path-layer"""
    data_text: LayerConfig = Field(
        default_factory=lambda: LayerConfig(), alias="dataText"
    )
    """Properties as defined on https://deck.gl/docs/api-reference/layers/text-layer"""

    r_channel: Optional[str] = Field(None, alias="rChannel")
    g_channel: Optional[str] = Field(None, alias="gChannel")
    b_channel: Optional[str] = Field(None, alias="bChannel")
    ndvi_channel: Optional[str] = Field(None, alias="ndviChannel")


class StandardColumnNameConfig(BaseModel):
    centroid_x: Optional[str] = Field("fused_centroid_x", alias="centroidX")
    centroid_y: Optional[str] = Field("fused_centroid_y", alias="centroidY")
    area: Optional[str] = "fused_area"
    assets: Optional[str] = None
    label: Optional[str] = None


class VizConfig(BaseModel):
    """Configuration for a dataset in the viz (debug) widget"""

    name: Optional[str] = None
    """Name to show for this dataset"""
    layer_config: VizLayerConfig = Field(
        default_factory=lambda: VizLayerConfig(), alias="layerConfig"
    )

    show_circles: bool = Field(True, alias="showCircles")
    show_heatmap: bool = Field(False, alias="showHeatmap")
    """Show materialized data as a heatmap instead of points (circles)"""
    show_bboxes: bool = Field(False, alias="showBboxes")
    """Show the bounding boxes of chunks"""
    show_bbox_ids: bool = Field(False, alias="showBboxIds")
    """Show the IDs of chunk bounding boxes (when show_bboxes is also True)"""
    show_data: bool = Field(True, alias="showData")
    """Show this dataset"""
    show_tooltip: bool = Field(True, alias="showTooltip")
    """Allow selection of points in this dataset (e.g. for use with raster debugging)"""

    selected_columns: Dict[str, bool] = Field(
        default_factory=lambda: {}, alias="selectedColumns"
    )
    """Columns that will be materialized by default"""
    column_names: StandardColumnNameConfig = Field(
        default_factory=lambda: StandardColumnNameConfig(), alias="columnNames"
    )
    """Column names for specific uses, such as geographic location or point size scaling"""
    raster_band_indexes: Optional[List[int]] = Field(None, alias="rasterBandIndexes")
    raster_source_type: Optional[str] = Field(None, alias="rasterSourceType")

    # geometryTableName and attributeTableNames are set when setting up the visualization, not here


class VizAppConfig(BaseModel):
    """Configuration for the viz (debug) widget"""

    map_background_style: Optional[str] = Field(None, alias="mapBackgroundStyle")
    map_style: Optional[str] = Field(None, alias="mapStyle")
    blend_mode: Optional[str] = Field(None, alias="blendMode")

    is_rough_mode: Optional[bool] = Field(None, alias="isRoughMode")
    allow_selection: Optional[bool] = Field(None, alias="allowSelection")
    materialize_on_select: Optional[bool] = Field(None, alias="materializeOnSelect")
    auto_materialization_settings: Optional[bool] = Field(
        None, alias="autoMaterializationSettings"
    )
    enable_toolbar_details: Optional[bool] = Field(None, alias="enableToolbarDetails")
    show_toolbar_details: Optional[bool] = Field(None, alias="showToolbarDetails")
    show_toolbar_stats: Optional[bool] = Field(None, alias="showToolbarStats")

    materialization_settings: Optional[Dict[str, Any]] = Field(
        None, alias="materializationSettings"
    )

    raster_source_visible: Optional[bool] = Field(None, alias="rasterSourceVisible")
    raster_source_opacity: Optional[float] = Field(None, alias="rasterSourceOpacity")
    raster_source_distance: Optional[float] = Field(None, alias="rasterSourceDistance")


class DatasetViz(BaseModel):
    """Configuration for visualizing a specific dataset"""

    path: DatasetUrl
    tables: Sequence[str] = DEFAULT_SHOW_TABLE_NAMES
    dataset_config: Optional[VizConfig] = None

    def _to_request(self) -> DebugMultiDatasetRequestDataset:
        dataset_config = self.dataset_config

        if dataset_config is None:
            dataset_config = VizConfig()

        if isinstance(dataset_config, VizConfig):
            dataset_config = dataset_config.dict(by_alias=True, exclude_none=True)

        return DebugMultiDatasetRequestDataset(
            path=self.path,
            tables=self.tables,
            dataset_config=dataset_config,
        )


class DatasetVizV2(BaseModel):
    """Configuration for visualizing a specific dataset"""

    dataset: DatasetInputV2
    dataset_config: Optional[VizConfig] = None

    def _to_request(self) -> MultiDebugSingleDatasetV2Request:
        dataset_config = self.dataset_config

        if dataset_config is None:
            dataset_config = VizConfig()

        if isinstance(dataset_config, VizConfig):
            dataset_config = dataset_config.dict(by_alias=True, exclude_none=True)

        return MultiDebugSingleDatasetV2Request(
            urls=[table.url for table in self.dataset.tables],
            operation=self.dataset.operation,
            dataset_config=dataset_config,
        )
