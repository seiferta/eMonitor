import os, imp
import requests, yaml
from xml.dom import minidom
from emonitor.extensions import db
from flask import current_app


class MapItem(db.Model):
    """MapItems class"""
    __tablename__ = "mapitems"
    __table_args__ = {'extend_existing': True}

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
    def loadFromOSM(itemtype, city):
        SEARCHSTRING = 'area["name"="%s"];%s(area)%s;(._;>;);out;' % (city, itemtype['itemtype'], itemtype['filter'])  # search all objects

        r = requests.post(MapItem.URL, data={'data': SEARCHSTRING})
        xmldoc = minidom.parseString(r._content)
        items = []
        if itemtype['itemtype'] == 'node':
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

        elif itemtype['itemtype'] == 'way':
            nodes = {}
            for node in xmldoc.getElementsByTagName('node'):  # get nodes
                nodes[node.attributes['id'].value] = {}
                for attr in [a for a in node.attributes.keys() if a in itemtype['attributes']]:
                    nodes[node.attributes['id'].value][attr] = node.attributes[attr].value

            for way in xmldoc.getElementsByTagName('way'):  # build ways from nodes
                i = dict(id=way.attributes['id'].value, nodes=[])
                for p in [p for p in way.childNodes if p.nodeName == 'nd']:
                    i['nodes'].append(nodes[p.attributes['ref'].value])
                items.append(i)

        return items

    @staticmethod
    def getLayouters():  # get all layouters
        ret = []
        for f in [f for f in os.listdir('%s/emonitor/modules/mapitems/inc/' % current_app.config.get('PROJECT_ROOT')) if f.endswith('.py') and f.startswith('layout_')]:
            cls = imp.load_source('emonitor.modules.mapitems.inc', 'emonitor/modules/mapitems/inc/%s' % f)
            layouter = getattr(cls, cls.__all__[0])()
            if isinstance(layouter, ItemLayout):
                ret.append(layouter)
        return ret

    @staticmethod
    def _buildTiles(items, definition):  # build tiles with layouter
        for layouter in MapItem.getLayouters():
            if layouter.getName() == definition['parameters']['layout']:
                layouter.buildTiles(items, definition['attributes'])
                break


class ItemLayout:
    """ItemLayout prototype class"""
    __name__ = "defaultlayout"
    """name as identifier"""
    __version__ = '0.0'

    itemtype = ''
    filter = ''
    attributes = []

    def getName(self):
        """
        Get name of layout

        :return: :py:attr:`emonitor.modules.mapitems.mapitem.ItemLayout.__name__`
        """
        return self.__name__

    def buildTiles(self, items, attributes):
        """
        Build tiles from definition

        :param items: list of items to build
        :param attributes: attributes to build tiles
        """
        pass
