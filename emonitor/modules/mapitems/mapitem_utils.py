import math


def deg2num(lat_deg, lon_deg, zoom):
    """Calculate tile coordinates and pixel position

    :param lat_deg: float value for latitude
    :param lon_deg: float value for longitude
    :param zoom: integer value of zoom level
    :return: list with x-tile, y-tile, x-pixel, y-pixel
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    x = (lon_deg + 180.0) / 360.0 * n
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    y = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
    return [xtile, ytile, int(x % 1 * 256), int(y % 1 * 256)]
