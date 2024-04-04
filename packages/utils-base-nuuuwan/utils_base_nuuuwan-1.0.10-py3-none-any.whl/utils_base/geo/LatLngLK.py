from utils_base.geo.LatLng import LatLng


class LatLngLK(LatLng):
    # Cities
    COLOMBO = LatLng(6.917273734591578, 79.86479237575594)
    KANDY = LatLng(7.293495849930314, 80.64101416983969)
    GALLE = LatLng(6.029591949643258, 80.2161060278968)
    JAFFNA = LatLng(9.665142806084814, 80.00933289927613)

    # Extreme Points
    NORTH = LatLng(9.835556, 80.212222)
    SOUTH = LatLng(5.923389, 80.589694)
    EAST = LatLng(7.022222, 81.879167)
    WEST = LatLng(9.383333, 79.516667)

    BBOX = LatLng.bbox([NORTH, SOUTH, EAST, WEST])

    @staticmethod
    def get_func_t_lk(
        width: float,
        height: float,
        padding: float,
    ):
        return LatLng.get_func_t(
            [
                LatLngLK.NORTH,
                LatLngLK.SOUTH,
                LatLngLK.EAST,
                LatLngLK.WEST,
            ],
            width,
            height,
            padding,
        )
