import re
from math import cos, sqrt, tan, sin, atan, trunc, radians, degrees


def getFloat(value):
    try:
        return float(value)
    except ValueError:
        value = str(value).replace('B', '8').replace('O', '0').replace(',', '.')
        _errcount = 0
        for i in value:
            if not re.match(r'[0-9\.]]', i):
                _errcount += 1
        if _errcount == 0:
            return float(value)
        return None


class Location:
    """
    Location class for position calculation and conversion, can handle GK and Wgs84 notation - default Wgs84
    """
    earthRadius = 6378137.0  # Earth radius in m
    aBessel = 6377397.155
    eeBessel = 0.0066743722296294277832
    ScaleFactor = 0.00000982
    RotXRad = -7.16069806998785E-06
    RotYRad = 3.56822869296619E-07
    RotZRad = 7.06858347057704E-06
    ShiftXMeters = 591.28
    ShiftYMeters = 81.35
    ShiftZMeters = 396.39

    def __init__(self, x, y, geotype='wgs84'):  # wgs84 (default), gk
        self.x = getFloat(x)
        self.y = getFloat(y)
        self.geotype = geotype.lower()
        
    def __repr__(self):
        return u"<location: {}, {} ({})>".format(self.x, self.y, self.geotype)

    def getLatLng(self, use_wgs84=None):
        if self.geotype == 'gk':  # gauss kruger
            (x, y) = self._gk_transformation()
            return Location.seven_parameter_helmert_transf(x, y, use_wgs84)
        else:
            return self.x, self.y

    def getDistance(self, lat, lng):
        """
        get distance in meters
        """
        (lat1, lng1) = self.getLatLng()
        x = ((radians(lng - lng1)) * cos(0.5 * (radians(lat + lat1))))**2
        return Location.earthRadius * sqrt(x + (radians(lat - lat1))**2)

    def _gk_transformation(self):  # transformation for gauss kruger
        # Check for invalid Parameters
        if not ((self.x > 1000000) and (self.y > 1000000)) and self.geotype != 'gk':
            raise ValueError("No valid Gauss-Kruger-Code.")

        # Variables to prepare the geovalues
        bii = (self.y / 10000855.7646)**2
        bf = (325632.08677 * (self.y / 10000855.7646) * (((((0.00000562025 * bii + 0.00022976983) * bii - 0.00113566119) * bii + 0.00424914906) * bii - 0.00831729565) * bii + 1)) / degrees(3600)
        g2 = 0.0067192188 * cos(bf)**2
        fa = (self.x - trunc(self.x / 1000000) * 1000000 - 500000) / (6398786.849 / sqrt(1 + g2))

        geo_dez_right = degrees(bf - fa**2 * tan(bf) * (1 + g2) / 2 + fa**4 * tan(bf) * (5 + 3 * tan(bf)**2 + 6 * g2 - 6 * g2 * tan(bf)**2) / 24)
        geo_dez_height = degrees(fa - fa**3 * (1 + 2 * tan(bf)**2 + g2) / 6 + fa**5 * (1 + 28 * tan(bf)**2 + 24 * tan(bf)**4) / 120) / cos(bf) + trunc(self.x / 1000000) * 3
        return geo_dez_right, geo_dez_height

    @staticmethod
    def seven_parameter_helmert_transf(x, y, use_wgs84=False):
        # calculate coordinates with helmert transformation
        latitudeit = 99999999

        if use_wgs84:
            ee = 0.0066943799
        else:
            ee = 0.00669438002290
        n = Location.aBessel / sqrt(1 - (Location.eeBessel * sin(radians(x))**2))

        cartesian_x_meters = n * cos(radians(x)) * cos(radians(y))
        cartesian_y_meters = n * cos(radians(x)) * sin(radians(y))
        cartesian_z_meters = n * (1 - Location.eeBessel) * sin(radians(x))

        cart_output_x_meters = (1 + Location.ScaleFactor) * cartesian_x_meters + Location.RotZRad * cartesian_y_meters - Location.RotYRad * cartesian_z_meters + Location.ShiftXMeters
        cart_output_y_meters = -1 * Location.RotZRad * cartesian_x_meters + (1 + Location.ScaleFactor) * cartesian_y_meters + Location.RotXRad * cartesian_z_meters + Location.ShiftYMeters
        cart_output_z_meters = Location.RotYRad * cartesian_x_meters - Location.RotXRad * cartesian_y_meters + (1 + Location.ScaleFactor) * cartesian_z_meters + Location.ShiftZMeters

        geo_dez_height = atan(cart_output_y_meters / cart_output_x_meters)
        latitude = atan(cart_output_z_meters / sqrt((cart_output_x_meters * cart_output_x_meters) + (cart_output_y_meters * cart_output_y_meters)))

        while abs(latitude - latitudeit) >= 0.000000000000001:
            latitudeit = latitude
            n = Location.earthRadius / sqrt(1 - ee * sin(latitude)**2)
            latitude = atan((cart_output_z_meters + ee * n * sin(latitudeit)) / sqrt(cart_output_x_meters**2 + cart_output_y_meters * cart_output_y_meters))
        return degrees(latitude), degrees(geo_dez_height)


if __name__ == "__main__":
    
    # test values
    # location1 (48.124570, 11.582328)
    lkx1 = 4469012.74
    lky1 = 5331920.84

    # location2 (48.1103206, 11.7233732)
    lkx2 = 4479507.160
    lky2 = "53302B9,O32"  # test value with error

    l1 = Location(lkx1, lky1, geotype='gk')
    l2 = Location(lkx2, lky2, geotype='gk')

    l3 = Location(48.1103206, 11.7233732)  # test coordinates (imprecision)
    print "l1: {}\nl2: {}\nl3: {}".format(l1, l2, l3)
    print "\nl2->l3 {:8.2f} m (precision)".format(l2.getDistance(*l3.getLatLng()))
    print "l2->l1 {:8.2f} m".format(l2.getDistance(*l1.getLatLng()))
