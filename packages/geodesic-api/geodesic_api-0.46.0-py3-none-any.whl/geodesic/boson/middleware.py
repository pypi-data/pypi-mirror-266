from geodesic.bases import _APIObject
from geodesic.descriptors import _ListDescr, _StringDescr, _DictDescr
from geodesic.boson.asset_bands import AssetBands
from typing import List, Union, Any

# Middleware types
SEARCH_FILTER_CQL2 = "cql2"
SEARCH_FILTER_SPATIAL = "spatial"
SEARCH_FILTER_DATETIME = "datetime"
SEARCH_TRANSFORM_RENAME_FIELDS = "rename-fields"
SEARCH_TRANSFORM_COMBINE_FIELDS = "combine-fields"
PIXELS_TRANSFORM_COLORMAP = "colormap"
PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS = "default_asset_bands"


class _Middleware(_APIObject):
    _limit_setitem = ("type", "properties")
    type = _StringDescr(
        doc="type of middleware to apply to a provider",
        one_of=[
            SEARCH_FILTER_DATETIME,
            SEARCH_FILTER_CQL2,
            SEARCH_FILTER_SPATIAL,
            SEARCH_TRANSFORM_RENAME_FIELDS,
            SEARCH_TRANSFORM_COMBINE_FIELDS,
            PIXELS_TRANSFORM_COLORMAP,
            PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
        ],
    )
    properties = _DictDescr(doc="properties (if any) to configure the middleware")


class SearchFilter(_Middleware):
    @staticmethod
    def cql2_filter() -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_CQL2)

    @staticmethod
    def spatial() -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_SPATIAL)

    @staticmethod
    def datetime(field: str) -> "SearchFilter":
        return SearchFilter(type=SEARCH_FILTER_DATETIME, properties={"datetime_field": field})


class SearchTransform(_Middleware):
    @staticmethod
    def rename_fields(case=None, field_map={}) -> "SearchTransform":
        """rename fields in the `properties` of a search response

        Args:
            case (str, optional): case to apply to the field names. Defaults to None. One of ["upper", "lower"]
            field_map (dict, optional): mapping of old field names to new field names. Defaults to {}.
        """
        properties = {"field_map": field_map}
        if case is not None and case in ["upper", "lower"]:
            properties["case"] = case
        elif case is not None:
            raise ValueError(f"case must be one of ['upper', 'lower'], got {case}")

        return SearchTransform(type=SEARCH_TRANSFORM_RENAME_FIELDS, properties=properties)

    @staticmethod
    def combine_fields(
        new_field: str, fields: List[str], separator: str = "", sprintf: str = ""
    ) -> "SearchTransform":
        """combine fields in the `properties` of a search response

        Args:
            new_field (str): name of the new field to create
            fields (List[str]): fields to combine
            separator (str, optional): separator to use when combining fields. Defaults to " ".
            sprintf (str, optional): sprintf format to use when combining fields. This uses golang
            format strings to format the fields into one combined string field. For instance,
            "%d.2 %s" would print "2.00 dollars" if the field values were 2 and "dollars".
            For more information about the formatting see https://pkg.go.dev/fmt.
            All fields must have values for the sprintf to be executed. Defaults to "".
        """
        return SearchTransform(
            type="combine-fields",
            properties={
                "new_field": new_field,
                "fields": fields,
                "separator": separator,
                "sprintf": sprintf,
            },
        )


class PixelsTransform(_Middleware):
    @staticmethod
    def colormap(
        *,
        asset: str,
        band: Union[int, str],
        colormap_name: str = "magma",
        lookup_table: List[List[int]] = None,
        min: float = None,
        max: float = None,
        rescale: bool = False,
        no_data_value: float = None,
        asset_name: str = "colormap",
    ) -> "PixelsTransform":
        """apply a colormap to the pixels data from an existing asset in the dataset

        Args:
            asset: asset to apply the colormap to
            band: band to apply the colormap to
            colormap_name: name of the colormap to apply. Defaults to "magma".
            lookup_table: lookup table to apply. Defaults to None. This can be used to provide a custom colormap
                via a lookup table. In this case, this should be a list of lists where each sublist is a color,
                including the alpha channel. For instance, [[0, 0, 0, 255], [255, 255, 255, 255]] would create a
                colormap that goes from black to white in two steps, splitting values below 0,5 to black and above
                to white.
            min: minimum value of the colormap. Valid only if rescale is True. Defaults to None.
            max: maximum value of the colormap. Valid only if rescale is True. Defaults to None.
            rescale: whether to rescale the colormap to the min and max values. If min/max are None, statistics
                of the dataset (if available) will be used, otherwise the values of the current response will be used.
                Defaults to False.
            no_data_value: value to use for pixels with no data. These values will be transparent. Defaults to None.
            asset_name: name of the asset to create. Defaults to "colormap".
        """
        properties = {
            "asset": asset,
            "band": band,
            "colormap_name": colormap_name,
            "rescale": rescale,
        }
        if lookup_table is not None:
            properties.pop("colormap_name")
            properties["lookup_table"] = lookup_table
        if min is not None:
            properties["min"] = min
        if max is not None:
            properties["max"] = max
        if no_data_value is not None:
            properties["no_data_value"] = no_data_value

        return PixelsTransform(type=PIXELS_TRANSFORM_COLORMAP, properties=properties)

    @staticmethod
    def default_asset_bands(default_asset_bands: List[AssetBands]) -> "PixelsTransform":
        """sets the default value of asset_bands in a pixels request on a Dataset.

        This is useful for when you are creating a static dataset and want to set the default bands that will be
        used in the pixels request or for when you have a dataset that has multiple bands and you want
        to set the default bands that will be used in the pixels request.
        """
        return PixelsTransform(
            type=PIXELS_TRANSFORM_DEFAULT_ASSET_BANDS,
            properties={"asset_bands": default_asset_bands},
        )

    @staticmethod
    def rasterize(
        attribute_name: str = None,
        value: Any = None,
        use_z: bool = False,
        initialize_value: Any = None,
        invert: bool = False,
        all_touched: bool = False,
        add: bool = False,
        collections: List[str] = [],
        asset_name: str = "rasterized",
        band_name: str = "rasterized",
        feature_limit: int = 25000,
    ) -> "PixelsTransform":
        """creates a rasterized image from a feature collection as a new raster asset

        Rasterize middleware is useful for performing simple aggregations on a feature collection. This can be
        useful for things like creating a population density raster from a feature collection of population
        counts or creating a binary raster from a feature collection of labels in a segmentation task.

        Args:
            attribute_name: attribute name to rasterize. Defaults to None.
            value: value to rasterize. Defaults to None.
            use_z: whether to use the z value of the feature. Defaults to False.
            initialize_value: value to initialize the raster with. Defaults to None.
            invert: invert which pixels are rasterize. Defaults to False.
            all_touched: whether to rasterize all pixels touched by the feature. Defaults to False.
            add: whether to add the raster to the asset. Defaults to False.
            collections: collections to rasterize. Defaults to [] (all collections).
            asset_name: name of the asset to create. Defaults to "rasterized".
            band_name: name of the band to create. Defaults to "rasterized".
            feature_limit: maximum number of features to rasterize. Defaults to 25000.

        Examples:
            >>> # Rasterize the population attribute by summing the values in the attribute for each pixel
            >>> transform = PixelsTransform.rasterize(
            ... attribute_name="population",
            ... add=True,
            ... asset_name="population_raster",
            ... band_name="population"
            ... )

            >>> # Rasterize by object by setting the value to 1 wherever there is an object
            >>> transform = PixelsTransform.rasterize(
            ... value=1
            ... )

            >>> # Rasterize by object by setting the value to 1 wherever there is NOT an object
            >>> transform = PixelsTransform.rasterize(
            ... value=1,
            ... invert=True
            ... )

        """

        if (value is None and attribute_name is None) and (not use_z):
            raise ValueError(
                "Must provide either a value or an attribute_name or use_z must be True."
            )

        return PixelsTransform(
            type="rasterize",
            properties={
                "value": value,
                "initialize_value": initialize_value,
                "attribute_name": attribute_name,
                "invert": invert,
                "all_touched": all_touched,
                "use_z": use_z,
                "add": add,
                "collections": collections,
                "asset_name": asset_name,
                "band_name": band_name,
                "feature_limit": feature_limit,
            },
        )


class MiddlewareConfig(_APIObject):
    """Configures the Middleware for a Dataset

    Middleware can be applied to a dataset to perform actions on the data before it is returned to the user, but
    without influencing the underlying data. This can be useful for things like filtering, transforming, or
    enhancing the data in some way. Middleware can be applied to the search and pixels handlers of a dataset.

    Middleware is broken into a few different pieces:

    - Search Filters: These are filters that are applied to the search results of a dataset. They can be used to
        filter the results of a search based on some criteria. These should ONLY be applied to providers that
        don't offer filtering themselves. When in doubt DON'T apply filters. Most providers have them implemented
        and this is generally not needed. If you've implemented a remote provider with a relatively small number
        of features, this can be useful since implementing filtering on the provider side can be difficult.
    - Search Transforms: These are transforms that are applied to the search results of a dataset. They can be used
        to rename fields, combine fields, or otherwise modify the results of a search. These can be applied either
        before or after search filters. In the former case, set `search_transforms_before` and in the latter case,
        set `search_transforms_after`.
    - Pixels Transforms: These are transforms that are applied to the pixels handler of a dataset. They can be used
        to apply colormaps, rescale pixel values, or otherwise modify the pixels data. Many of them can create new
        assets in the dataset while some may modifiy existing assets.
    """

    search_filters = _ListDescr(
        item_type=(SearchFilter, dict),
        coerce_items=True,
        doc="Which filter actions to perform applied to the result of a dataset.",
    )
    search_transforms_before = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied BEFORE any filtering takes place",
    )
    search_transforms_after = _ListDescr(
        item_type=(SearchTransform, dict),
        coerce_items=True,
        doc="transforms to be applied to each feature/item in a search response. "
        "This is applied AFTER any filtering takes place",
    )
    pixels_transforms = _ListDescr(
        item_type=(PixelsTransform, dict),
        coerce_items=True,
        doc="transforms the request/response of a pixels handler. Useful for "
        "things like applying colormaps or more complex transformations on the pixels data.",
    )
