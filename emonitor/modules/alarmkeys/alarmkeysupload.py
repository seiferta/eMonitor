import xlrd
import xlsxwriter
from flask import current_app
from emonitor.extensions import classes


class XLSFile:
    """
    XLSX-file object uploaded with alarmkeys, cars, material, ...
    """

    def __init__(self, filename):
        """
        Init object with given filename

        :param filename:
        """
        self.book = xlrd.open_workbook(filename, encoding_override="cp1252")
        self.headerrow = 0
        
    def getSheets(self):
        """
        Deliver sheet list of current xlsx file

        :return: list with names of sheets
        """
        return self.book.sheet_names()
        
    def getCols(self, sheet):
        """
        Read columns of given sheet

        :param sheet: sheet as integer
        :return: list of columns
        """
        ret = []
        worksheet = self.book.sheet_by_name(self.book.sheet_names()[int(sheet)])
        num_rows = worksheet.nrows - 1

        curr_row = -1
        while curr_row < num_rows:
            curr_row += 1
            row = worksheet.row(curr_row)
            
            for item in row:
                curr_cell = row.index(item)
                cell_value = worksheet.cell_value(curr_row, curr_cell)

                if cell_value in ["Stichwort", "category"]:
                    self.headerrow = curr_row
                    for i in row:
                        c_cell = row.index(i)

                        if c_cell + 65 > 90:
                            p = "A" + unichr((c_cell + 65) - 26)
                        else:
                            p = unichr((c_cell + 65))
                        if worksheet.cell_value(curr_row, c_cell) != '':
                            ret.append((p, worksheet.cell_value(curr_row, c_cell)))
                    break
        return ret

    def getValues(self, coldefinition):
        cars = {}
        notfound = {}
        states = {'-1': 0, '0': 0, '1': 0}
        for c in classes.get('car').getCars(deptid=coldefinition['dept']):
            cars[unicode(c.name)] = c

        keys = classes.get('alarmkey').getAlarmkeys()
        worksheet = self.book.sheet_by_name(self.book.sheet_names()[int(coldefinition['sheet'])])
        
        def getPosForCol(name):
            ret = -65
            while len(name) > 0:
                ret += ord(name[0])
                name = name[1:]
            return ret
            
        def evalValue(crow, ccol):
            try:
                return worksheet.cell_value(crow, ccol)
            except:
                return ""
        
        importkeys = []
        # state -1:new, 0:no changes, 1:need update
        for row in range(self.headerrow + 1, worksheet.nrows - 1):
            item = {'cars1': [], 'cars2': [], 'material': [], 'cars1_ids': [], 'cars2_ids': [], 'material_ids': [],
                    'dbid': None, 'state': '0', 'category': evalValue(row, getPosForCol(coldefinition['category'])),
                    'key': evalValue(row, getPosForCol(coldefinition['key'])),
                    'keyinternal': evalValue(row, getPosForCol(coldefinition['keyinternal'])),
                    'remark': evalValue(row, getPosForCol(coldefinition['remark']))}

            for field in ['cars1', 'cars2', 'material']:
                for c in coldefinition[field]:
                    cell_val = evalValue(row, getPosForCol(c))
                    if unicode(cell_val) in cars.keys():
                        item[field].append(cars[unicode(cell_val)])
                        item[field + '_ids'].append(str(cars[unicode(cell_val)].id))
                    elif cell_val.strip() != '':
                        if unicode(cell_val) not in notfound.keys():
                            n_c = classes.get('car')('<em style="color:#ff0000">%s</em>' % cell_val, '', '', 0, 'new', coldefinition['dept'])
                            notfound[unicode(cell_val)] = n_c
                        else:
                            n_c = notfound[unicode(cell_val)]
                        item[field].append(n_c)
                        item[field + '_ids'].append(-1)

            # check if key exists
            for k in keys:
                if unicode(k.category) == unicode(item['category']) and unicode(k.key) == unicode(item['key']):
                    item['dbid'] = k.id
                    if k.getCars1(coldefinition['dept']) != item['cars1'] or k.getCars2(coldefinition['dept']) != item['cars2'] or k.getMaterial(coldefinition['dept']) != item['material']:
                        item['cars1'] = k.getCars1(coldefinition['dept'])
                        item['cars2'] = k.getCars2(coldefinition['dept'])
                        item['material'] = k.getMaterial(coldefinition['dept'])
                        item['state'] = '1'  # mark to update

            if not item['dbid']: item['state'] = '-1'  # mark as new
            
            if item['category'] != '' and item['key'] != '':
                states[str(item['state'])] += 1
                importkeys.append(item)

        return dict(keys=importkeys, carsnotfound=notfound, states=states)
        
        
def buildDownloadFile(department, dtype=0):
    """
    Create XLSX file with definition of given department and store file in tmp directory with filename *aao.xlsx*

    :param department: department object
    :param dtype: 0|1: add default definition if no material definition found for keyword
    :return: filename of created file, on error ''
    """
    alarmkeys = classes.get('alarmkey').getAlarmkeys()
    
    header = ['dbid', 'category', 'key', 'key internal']
    _maxcars1 = 1
    _maxcars2 = 1
    _maxmaterial = 1

    counted_keys = classes.get('alarmkeycar').query.from_statement("select kid, dept, (LENGTH(cars1)-LENGTH(REPLACE(cars1, ';', '')))as cars1, (LENGTH(cars2)-LENGTH(REPLACE(cars2, ';', ''))) as cars2, (LENGTH(material)-LENGTH(REPLACE(material, ';', ''))) as material from alarmkeycars where dept='1';")
    
    for c_k in counted_keys:
        if _maxcars1 < c_k._cars1: _maxcars1 = c_k._cars1
        if _maxcars2 < c_k._cars2: _maxcars2 = c_k._cars2
        if _maxmaterial < c_k._material: _maxmaterial = c_k._material
        
    header += ['p_%s' % i for i in range(0, _maxcars1 + 1)]
    header += ['s_%s' % i for i in range(0, _maxcars2 + 1)]
    header += ['m_%s' % i for i in range(0, _maxmaterial + 1)]
    header += ['remark']
        
    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook('%s/aao.xlsx' % current_app.config.get('PATH_TMP'))
    worksheet = workbook.add_worksheet('aao')
    bold = workbook.add_format({'bold': 1})

    worksheet.write_row(0, 0, header, bold)

    _w = 0
    for alarmkey in alarmkeys:
        if dtype == '1' and not alarmkey.hasDefinition(department):
            continue
        _w += 1
        data = [alarmkey.id, alarmkey.category, alarmkey.key, alarmkey.key_internal]
        _c1 = alarmkey.getCars1(department)
        data += [c1.name for c1 in _c1]
        data += ['' for i in range(0, _maxcars1 - len(_c1) + 1)]
        _c2 = alarmkey.getCars2(department)
        data += [c2.name for c2 in _c2]
        data += ['' for i in range(0, _maxcars2 - len(_c2) + 1)]
        _c3 = alarmkey.getMaterial(department)
        data += [c3.name for c3 in _c3]
        data += ['' for i in range(0, _maxmaterial - len(_c3) + 1)]
        data += [alarmkey.remark]
        
        worksheet.write_row(list(alarmkeys).index(alarmkey) + 1, 0, data)

    workbook.close()
    
    if _w == 0:  # no data written
        return ''
    else:
        return 'aao.xlsx'
