import xlrd
from emonitor.modules.persons.persons import Person


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
        try:
            row = worksheet.row(0)
        except IndexError:
            return []

        for i in row:
            c_cell = row.index(i)

            if c_cell + 65 > 90:
                p = "A" + unichr((c_cell + 65) - 26)
            else:
                p = unichr((c_cell + 65))
            if worksheet.cell_value(0, c_cell) != '':
                ret.append((p, worksheet.cell_value(0, c_cell)))
        return ret

    def getValues(self, coldefinition):
        states = {'-1': 0, '0': 0, '1': 0}
        worksheet = self.book.sheet_by_name(self.book.sheet_names()[int(coldefinition['sheet'])])

        def getPosForCol(name):
            ret = -65
            while len(name) > 0:
                ret += ord(name[0])
                name = name[1:]
            return ret

        def evalValue(crow, ccol):
            try:
                return unicode(worksheet.cell_value(crow, ccol))
            except:
                return ""

        importpersons = []
        # state -1:new, 0:no changes, 1:need update
        for row in range(self.headerrow + 1, worksheet.nrows - 1):
            item = {'dbid': None, 'state': '0', 'department': coldefinition['department'], }
            for key in coldefinition:
                item[key] = evalValue(row, getPosForCol(coldefinition[key]))

            # check if key exists
            p = Person.getPersons(identifier=item['identifier'])
            if p:
                item['dbid'] = p.id
                if "%s%s%s%s" % (p.firstname, p.lastname, p.grade, p.position) != "%s%s%s%s" % (item['firstname'], item['lastname'], item['grade'], item['position']):
                    item['state'] = '1'  # updated
            else:
                item['state'] = '-1'  # mark as new

            states[str(item['state'])] += 1
            importpersons.append(item)

        return dict(persons=importpersons, states=states)
