import requests, yaml
from xml.dom import minidom
from emonitor.extensions import db


class MapItem(db.Model):
    __tablename__ = "mapitems"

    URL = 'http://overpass-api.de/api/interpreter'

    id = db.Column(db.Integer, primary_key=True)
    osmid = db.Column(db.BigInteger)
    itemtype = db.Column(db.String(32))
    _parameters = db.Column('parameter', db.Text)

    def __init__(self, itemtype, osmid, parameters):
        self.itemtype = itemtype
        self.osmid = osmid
        if type(parameters) == dict:
            self._parameters = yaml.safe_dump(parameters, encoding='utf-8')
        else:
            self._parameters = parameters

    @property
    def parameters(self):
        return yaml.load(self._parameters)

    @parameters.setter
    def parameters(self, val):
        if type(val) == dict:
            self._parameters = yaml.safe_dump(val, encoding='utf-8')
        else:
            self._parameters = val

    @staticmethod
    def getitemtypes():  # TODO deprecated
        return db.session.query(MapItem.itemtype).distinct().all()

    @staticmethod
    def getMapitems(itemtype='', osmid=0):
        if itemtype == '' and osmid == 0:
            return db.session.query(MapItem).all()
        elif osmid == 0:
            return db.session.query(MapItem).filter_by(itemtype='%s' % itemtype).all()
        elif itemtype == '':
            return db.session.query(MapItem).filter_by(osmid='%s' % osmid).first()

    @staticmethod
    def loadFromOSM(itemtype, area={}):
        SEARCHSTRING = 'node(%s,%s,%s,%s)[%s];(._;>;);out;' % (area['min_latdeg'], area['min_lngdeg'], area['max_latdeg'], area['max_lngdeg'], itemtype['filter'])  # search all objects

        r = requests.post(MapItem.URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r._content)
        items = []
        for node in xmldoc.getElementsByTagName('node'):
            data = {}

            for attr in [a for a in node.attributes.keys() if a in itemtype['attributes']]:
                data[attr] = node.attributes[attr].value

            for c in node.childNodes:
                if c.nodeType == minidom.Node.ELEMENT_NODE:
                    _t = ''
                    for attr in c.attributes.keys():
                        if attr == 'k' and c.attributes[attr].value in itemtype['attributes']:
                            _t = c.attributes[attr].value
                        elif attr == 'v' and _t != '':
                            data[_t] = c.attributes[attr].value
            items.append(data)

        return items

