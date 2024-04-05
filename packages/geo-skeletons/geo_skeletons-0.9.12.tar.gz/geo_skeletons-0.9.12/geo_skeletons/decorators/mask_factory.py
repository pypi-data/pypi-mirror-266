import numpy as np
from copy import deepcopy

CARTESIAN_STRINGS = ["x", "y", "xy"]
SPHERICAL_STRINGS = ["lon", "lat", "lonlat"]

from typing import Union
import dask


def add_mask(
    name: str,
    default_value: int,
    coords: str = "grid",
    opposite_name: str = None,
):
    """coord_type = 'all', 'spatial', 'grid' or 'gridpoint'"""

    def mask_decorator(c):
        def get_mask(self, empty: bool = False, **kwargs) -> np.ndarray:
            """Returns bool array of the mask.

            Set empty=True to get an empty mask (even if it doesn't exist)

            **kwargs can be used for slicing data.
            """

            mask = self.get(f"{name}_mask", boolean_mask=True, empty=empty, **kwargs)

            return mask

        def get_not_mask(self, empty: bool = False, **kwargs):
            mask = get_mask(self, empty=empty, **kwargs)
            if mask is None:
                return None
            return np.logical_not(mask)

        def get_masked_points(
            self,
            type: str = "lonlat",
            native: bool = True,
            order_by: str = "lat",
            strict=False,
            **kwargs,
        ):
            mask = get_mask(self, **kwargs)
            if mask is None:
                mask = get_mask(self, empty=True, **kwargs)

            if type in CARTESIAN_STRINGS:
                return self.xy(
                    mask=mask, native=native, order_by=order_by, strict=strict, **kwargs
                )
            elif type in SPHERICAL_STRINGS:
                return self.lonlat(
                    mask=mask, native=native, order_by=order_by, strict=strict, **kwargs
                )

        def get_not_points(
            self,
            type: str = "lonlat",
            native: bool = True,
            order_by: str = "lat",
            strict=False,
            **kwargs,
        ):
            mask = get_not_mask(self, **kwargs)
            if mask is None:
                mask = get_not_mask(self, empty=True, **kwargs)

            if type in CARTESIAN_STRINGS:
                return self.xy(
                    mask=mask, native=native, order_by=order_by, strict=strict, **kwargs
                )
            elif type in SPHERICAL_STRINGS:
                return self.lonlat(
                    mask=mask, native=native, order_by=order_by, strict=strict, **kwargs
                )

        def set_mask(
            self,
            data: Union[np.ndarray, int, bool] = None,
            allow_reshape: bool = True,
            allow_transpose: bool = False,
            coords: list[str] = None,
            chunks: Union[tuple, str] = None,
            silent: bool = True,
        ) -> None:
            if isinstance(data, int) or isinstance(data, bool):
                data = np.full(self.size(f"{name}_mask"), data)
            if data is not None:
                data = data.astype(int)
            self.set(
                f"{name}_mask",
                data,
                allow_reshape=allow_reshape,
                allow_transpose=allow_transpose,
                coords=coords,
                chunks=chunks,
                silent=silent,
            )

        def set_opposite_mask(
            self,
            data: Union[np.ndarray, int, bool] = None,
            allow_reshape: bool = True,
            allow_transpose: bool = False,
            coords: list[str] = None,
            chunks: Union[tuple, str] = None,
            silent: bool = True,
        ) -> None:
            if data is not None:
                try:
                    data = dask.array.from_array(data)
                except ValueError:
                    pass
                data = dask.array.logical_not(data)
            self.set(
                f"{opposite_name}_mask",
                data,
                allow_reshape=allow_reshape,
                allow_transpose=allow_transpose,
                coords=coords,
                chunks=chunks,
                silent=silent,
            )

        if c._coord_manager.initial_state:
            c._coord_manager = deepcopy(c._coord_manager)
            c._coord_manager.initial_state = False
        c._coord_manager.add_mask(name, coords, default_value, opposite_name)
        exec(f"c.{name}_mask = get_mask")
        exec(f"c.{name}_points = get_masked_points")
        exec(f"c.set_{name}_mask = set_mask")
        if opposite_name is not None:
            exec(f"c.{opposite_name}_mask = get_not_mask")
            exec(f"c.{opposite_name}_points = get_not_points")
            exec(f"c.set_{opposite_name}_mask = set_opposite_mask")

        return c

    return mask_decorator
