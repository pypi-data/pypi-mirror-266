import os.path

import mysql.connector as mysql
import re
import codecs
import sys
import traceback
import numpy as np
from mysqlquerys import connect


class DataBase:
    def __init__(self, credentials):
        self.db = mysql.connect(**credentials)
        # self.db.set_session(autocommit=True)
        self.cursor = self.db.cursor()

    @property
    def dataBaseVersion(self):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.cursor.execute('SELECT version()')
        db_version = self.cursor.fetchone()
        return db_version

    @property
    def allAvailableTablesInDatabase(self):
        """ get all tables in schema"""
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        cur = self.db.cursor()
        command = "SHOW TABLES"
        cur.execute(command)
        rows = cur.fetchall()
        tables = []
        for row in rows:
            tabName = row[0]
            tables.append(tabName)
        cur.close()

        return sorted(tables)

    def checkProcess(self):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        query = "SHOW PROCESSLIST"
        cur = self.db.cursor()
        cur.execute(query)
        records = cur.fetchall()
        return records

    def killProcess(self, processes):
        for process in processes:
            query = "KILL {}".format(process)
            self.cursor.execute(query)

    def createTableFromFile(self, file):
        '''
        :param file: QFileDialog.getOpenFileName
        :return:
        '''
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        try:
            error = None
            command = ''
            # print ('createTableFromFile', file)
            f = open(file)
            # f = codecs.open(file, "r", "utf-8")
            for line in f.read().splitlines():
                # print(line)
                command += line
                if ';' in line:
                    if re.search("^CREATE TABLE", command) or re.search("^ALTER TABLE", command) or re.search(
                            "^INSERT INTO", command):
                        match = re.findall(r"\`(.+?)\`", command)
                        # print (match)
                        tableName = match[0]
                        # print (self.schemaName)
                        newTableName = '{}'.format(tableName)
                        command = command.replace(tableName, newTableName)
                        # print (command)
                        if 'REFERENCES' in command:
                        # print ('========')
                            text = command.split('REFERENCES')[1]
                            # print ('text', text)
                            match = re.findall(r"\`(.+?)\`", text)
                            referenceTable = match[0]
                            newRefName = "{} {}".format(self.schemaName, referenceTable)
                            refTab = '`{}`'.format(referenceTable)
                            newRef = '`{}`'.format(newRefName)
                            command = command.replace(refTab, newRef)
                            # print('text', command)
                        # sys.exit()
                    cur = self.db.cursor()
                    cur.execute(command)
                    command = ''
            f.close()
        except mysql.Error as err:
            print('ERROR mysql.Error: ', err.msg)
            error = (err.msg, command)
            cur.close()
        except Exception:
            print('ERR: ', traceback.format_exc())
            error = traceback.format_exc()
            cur.close()

        return error

    def createTableList(self, fileList):
        '''
        :param fileList: QFileDialog.getOpenFileNames
        :return: Error if exists, else None
        '''
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        errList = []
        while fileList:
            for i, file in enumerate(fileList):
                error = self.createTableFromFile(file)
                if error:
                    if error[0] == 'Cannot add foreign key constraint' \
                            or re.search("^relation.*does not exist$", error[0]):
                        errList.append(error[1])
                        fileList.pop(i)
                        continue
                    elif 'already exists' in error[0]:
                        fileList.pop(i)
                    else:
                        print('ERR createTablesFromFiles: ', error)
                        fileList.pop(i)
                else:
                    fileList.pop(i)

        probList = []
        for com in errList:
            try:
                print('Retrying... {}'.format(com))
                cur = self.db.cursor()
                cur.execute(com)
                cur.close()
            except Exception:
                print('ERR: ', traceback.format_exc())
                error = (traceback.format_exc(), com)
                probList.append(error)

        if probList:
            print('remaining errs:')
            for i in errList:
                print(i)
        else:
            print('Successfully')

    def drop_table(self, tableName):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        query = "DROP TABLE IF EXISTS {} CASCADE;".format(tableName)
        cur = self.db.cursor()
        cur.execute(query)
        cur.close()

    def drop_table_list(self, tableList):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        results = []
        while tableList:
            for i, tab in enumerate(tablelist):
                if self.connectionType == 'mysql':
                    exists = self.checkIfTableExists(tab)
                    if not exists:
                        print('table {} does not exist in database {}'.format(tab, self.dataBaseName))
                        tableList.pop(i)
                        continue
                    query = "SELECT table_name FROM information_schema.KEY COLUMN USAGE " \
                            "WHERE table_schema = %s AND referenced table_name = %s"
                    cur = self.db.cursor()
                    cur.execute(query, (self.dataBaseName, tab))
                    children = []
                    for cursor in cur.fetchall():
                        if cursor[0]:
                            children.append(cursor)
                    if not children:
                        res = self.drop_table(tab)
                        results.append(res)
                        tableList.pop(i)
                    else:
                        # if children make sure all of them are included in list
                        for child in children:
                            if child[0] not in tablelist:
                                print('if child not in tablelist:', tab, child, children)
                                err = self.drop_table(tab)
                                results.append(err)
                                tableList.pop(i)
                                break
                    cur.close()
                elif self.connectionType == 'postgresql':
                    res = self.drop_table(tab)
                    results.append(res)
                    tableList.pop(i)
        return results

    def rename_table(self, tableName, newName):
        # #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        query = ('RENAME TABLE {} TO {}'.format(tableName, newName))
        cur = self.db.cursor()
        try:
            cur.execute(query)
            cur.close
        except mysql.connector.Error as err:
            print(err.msg)

    def deleteAllDataInTable(self, tableList):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        cur = self.db.cursor()
        for tab in tableList:
            query = ('DELETE FROM {}'.format(tab))
            cur.execute(query)
            self.db.commit()
        cur.close()


class Table(DataBase):
    def __init__(self, credentials, tableName):
        super().__init__(credentials)
        self.tableName = tableName

    @property
    def noOfRows(self):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        query = 'SELECT COUNT(*) FROM {}'.format(self.tableName)
        cursor = self.db.cursor()
        cursor.execute(query)
        noOfRows = cursor.fetchone()[0]
        # rowNo = cursor.rowcount
        cursor.close()
        return noOfRows

    def lastRowId(self):
        query = ('SELECT id FROM {} ORDER BY id DESC LIMIT 1'.format(self.tableName))
        cur = self.db.cursor()
        cur.execute(query)
        lastId = cur.fetchonel()
        if lastId is None:
            return 0
        return lastId[0]

    @property
    def columnsNames(self):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        cursor = self.db.cursor()
        query = 'DESC {}'.format(self.tableName)
        cursor.execute(query)
        res = cursor.fetchall()
        cols = []
        for col in res:
            cols.append(col[0])
        cursor.close()
        return cols

    @property
    def columnsDetProperties(self):
        query = 'DESC {}'.format(self.tableName)
        colNames = ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']
        cursor = self.db.cursor()
        cursor.execute(query)
        res = cursor.fetchall()
        cols = {}
        for col in res:
            colName, colType, null, key, default, extra = col
            if isinstance(colType, bytes):
                colType = str(colType.decode("utf-8"))
            cols[colName] = [colType, null, key, default, extra]
        cursor.close()
        return cols

    @property
    def columnsProperties(self):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        cursor = self.db.cursor()
        query = ("SELECT table_name, column_name, data_type FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '{}'").format(self.tableName)
        cursor.execute(query)
        res = cursor.fetchall()
        cols = {}
        for col in res:
            table_name, col_name, data_type = col
            cols[col_name] = data_type
        cursor.close()
        return cols

    def deleteRow(self, condition):
        colName, value = condition
        query = 'DELETE FROM {} WHERE {} = {} '.format(self.tableName, colName, value)
        print(query)
        cursor = self.db.cursor()
        cursor.execute(query, value)
        self.db.commit()
        cursor.close()

    def delete_multiple_rows(self, condition):
        colName, value = condition
        query = 'DELETE FROM {} WHERE {} = {} '.format(self.tableName, colName, value)
        print(query)
        cursor = self.db.cursor()
        cursor.execute(query, value)
        self.db.commit()
        cursor.close()

    def delete_multiple_rows_multiple_conditions(self, condition):
        colName, value = condition
        query = 'DELETE FROM {} WHERE {} = {} '.format(self.tableName, colName, value)
        print(query)
        cursor = self.db.cursor()
        cursor.execute(query, value)
        self.db.commit()
        cursor.close()

    def convertToBinaryData(self, filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def addNewRow(self, columns, values):
        # print(len(columns), len(values))
        strCols = (('{}, ' * len(columns)).format(*columns))
        strCols = '({})'.format(strCols[:-2])
        strVals = ('%s,'*len(columns))
        strVals = '({})'.format(strVals[:-1])

        query = "INSERT INTO {} {} VALUES {}".format(self.tableName, strCols, strVals)
        #######
        print(query)
        for i in range(len(columns)):
            print(columns[i], values[i])
        #######
        if isinstance(values, int):
            values = (values, )
        elif isinstance(values, str):
            values = (values,)
        elif isinstance(values, tuple):
            new_vals = []
            for v in values:
                if os.path.isfile(v):
                    v = self.convertToBinaryData(v)
                new_vals.append(v)
            values = tuple(new_vals)

        cursor = self.db.cursor()
        cursor.execute(query, values)
        self.db.commit()
        cursor.close()

        return cursor.lastrowid

    def insertColumns(self, column_name, column_definition, afterCol):
        if afterCol == 'FIRST':
            query = 'ALTER TABLE {} ADD COLUMN {} {} FIRST'.format(self.tableName, column_name, column_definition)
        else:
            query = 'ALTER TABLE {} ADD COLUMN {} {} AFTER {}'.format(self.tableName, column_name, column_definition, afterCol)

        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        cursor.close()

    def returnAllRecordsFromTable(self):
        cur = self.db.cursor()
        query = ('SELECT * FROM {}'.format(self.tableName))
        cur.execute(query)
        records = cur.fetchall()
        return records

    def returnLastRecords(self, column, noOfRows2Return):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        cur = self.db.cursor()
        query = ('SELECT * FROM {} ORDER BY {} DESC LIMIT %s'.format(self.tableName, column))
        cur.execute(query, (noOfRows2Return,))
        rows = cur.fetchall()
        cur.close()
        return rows

    def filterRows(self, matches, order_by=None):
        filterText = ''
        for match in matches:
            search_col, search_key = match
            if isinstance(search_key, tuple):
                min, max = search_key
                new = "{} > '{}' AND {} < '{}' AND ".format (search_col, min, search_col, max)
                filterText += new
            elif isinstance(search_key, list):
                new = "{} in {} AND ".format(search_col, tuple(search_key))
                filterText += new
            elif search_key == 'None' or search_key is None:
                new = "{} IS NULL AND ".format(search_col, search_key)
                filterText += new
            else:
                new = "{} = '{}' AND ".format(search_col, search_key)
                filterText += new
        query = "SELECT * FROM {} WHERE ".format(self.tableName) + filterText[:-4]
        if order_by:
            col, order = order_by
            txt = 'ORDER BY {} {}'.format(col, order)
            query += txt
        cur = self.db.cursor()
        cur.execute(query)
        records = cur.fetchall()
        cur.close()
        return records

    def returnRowsWhere(self, matches):
        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT * FROM {} WHERE {} = '{}'".format(self.tableName, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT * FROM {} WHERE {} IN '{}'".format(self.tableName, searchCol, searchKey)
            if searchKey is None:
                query = "SELECT * FROM {} WHERE {} IS NULL".format(self.tableName, searchCol)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                if searchKey is None:
                    new = '{} IS NULL AND '.format(searchCol)
                else:
                    new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT * FROM {} WHERE ".format(self.tableName) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.db.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values

    def returnRowsLike(self, column, keyWord):
        query = "SELECT * FROM {} WHERE {} LIKE '%{}%'".format(self.tableName,
                                                               column, keyWord)
        cur = self.db.cursor()
        cur.execute(query)
        records = cur.fetchall()
        return records

    def returnRowsYoungerThan(self, column, timeP):
        query = "SELECT * FROM {} WHERE {} > %s ORDER BY {} DESC".format(self.tableName, column, column)
        cur = self.db.cursor()
        cur.execute(query, (timeP, ))
        records = cur.fetchall()
        return records

    def returnRowsInInterval(self, startColumn, startTime, endColumn, endTime):
        # query = "SELECT * FROM {} WHERE {} > %s ORDER BY {} DESC".format(self.tableName, startColumn, startColumn)
        query = "SELECT * FROM {} WHERE {} > %s OR {} < %s".format(self.tableName, startColumn, endColumn)
        # print(query)
        cur = self.db.cursor()
        cur.execute(query, (startTime, endTime))
        records = cur.fetchall()
        return records

    def returnRowsOfYear(self, startColumn, startTime, endColumn, endTime):
        # query = "SELECT * FROM {} WHERE {} > %s ORDER BY {} DESC".format(self.tableName, startColumn, startColumn)
        query = "SELECT * FROM {} WHERE {} > %s AND {} < %s".format(self.tableName, startColumn, endColumn)
        # print(query)
        cur = self.db.cursor()
        cur.execute(query, (startTime, endTime))
        records = cur.fetchall()
        return records

    def returnRowsOutsideInterval(self, startColumn, startTime, endColumn, endTime):
        # query = "SELECT * FROM {} WHERE {} > %s ORDER BY {} DESC".format(self.tableName, startColumn, startColumn)
        query = "SELECT * FROM {} WHERE {} < %s AND {} > %s".format(self.tableName, startColumn, endColumn)
        # print(query)
        cur = self.db.cursor()
        cur.execute(query, (startTime, endTime))
        records = cur.fetchall()
        return records

    def get_column_type(self, column):
        colProps = self.columnsProperties[column]
        colType = colProps[0]
        return colType

    def modify2AutoIncrement(self, column, colType):
        query = 'ALTER TABLE {} MODIFY {} {} AUTO_INCREMENT;'.format(self.tableName, column, colType)
        print(query)
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        cursor.close()

    def modifyType(self, column, colType):
        query = 'ALTER TABLE {} MODIFY {} {};'.format(self.tableName, column, colType)
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        cursor.close()

    def changeCellContent(self, column2Modify, val2Moify, refColumn, refValue):
        query = "UPDATE {} SET {} = %s WHERE {} = %s".format(self.tableName, column2Modify, refColumn)
        # print(query)
        cursor = self.db.cursor()
        vals = (val2Moify, refValue)
        # print(vals)
        cursor.execute(query, vals)
        self.db.commit()
        cursor.close()

    def dropColumn(self, column2Del):
        query = "ALTER TABLE {} DROP COLUMN %s;".format(self.tableName)
        query = "ALTER TABLE {} DROP COLUMN {};".format(self.tableName, column2Del)
        print(query)
        cursor = self.db.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        self.db.commit()
        cursor.close()

    def executeQuery(self, query):
        print(sys._getframe().f_code.co_name)
        # print(file)
        cursor = self.db.cursor()
        if isinstance(query, str):
            commands = query.split(';')
        for command in commands:
            print('executing command: ', command)
            cursor.execute(command)

    def importCSV(self, inpFile):
        with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
            linereader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for i, row in enumerate(linereader):
                if i == 0:
                    tableHead = row
                    continue
                if '' in row or 'None' in row:
                    new_strings = []
                    for string in row:
                        if string == '' or string == 'None':
                            new_strings.append(None)
                        else:
                            new_strings.append(string)
                    row = new_strings
                self.add_row(tableHead, row)

    def importSparkasseCSV(self, inpFile):
        with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
            linereader = csv.reader(csvfile, delimiter=';', quotechar='"')
            indxBuchungstag = self.columnsNames.index('Buchungstag')
            indxValutDatum = self.columnsNames.index('Valutadatum')
            indxBetrag = self.columnsNames.index('Betrag')
            for i, row in enumerate(linereader):
                # print(row)
                row.insert(0, i)
                if i == 0:
                    tableHead = row
                    continue
                if '' in row or 'None' in row:
                    new_strings = []
                    for string in row:
                        if string == '' or string == 'None':
                            new_strings.append(None)
                        else:
                            new_strings.append(string)
                    row = new_strings
                buchungstag = row[indxBuchungstag]
                valutDatum = row[indxValutDatum]
                betrag = row[indxBetrag]
                betrag = float(betrag.replace(',', '.'))
                buchungstag = self.convertDatumFormat4SQL(buchungstag)
                valutDatum = self.convertDatumFormat4SQL(valutDatum)

                row[indxBuchungstag] = buchungstag
                row[indxValutDatum] = valutDatum
                row[indxBetrag] = betrag
                self.add_row(self.columnsNames, row)

    def convertDatumFormat4SQL(self, datum):
        # print(sys._getframe().f_code.co_name)
        # newDate = datetime.strptime(datum, '%d.%m.%y')
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%y'):
            try:
                newDate = datetime.strptime(datum, fmt)
                return newDate.date()
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def convertTimeFormat4SQL(self, time):
        # print(sys._getframe().f_code.co_name)
        # newDate = datetime.strptime(datum, '%d.%m.%y')
        for fmt in ('%H:%M', '%H:%M:%S'):
            try:
                newDate = datetime.strptime(time, fmt)
                return newDate.time()
            except ValueError:
                pass
        raise ValueError('no valid date format found')

    def returnColumn(self, col):
        query = 'SELECT {} FROM {}'.format(col, self.tableName)
        cursor = self.db.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i[0])
        return values

    def returnColumns(self, cols):
        strTableHead = ''
        for col in cols:
            strTableHead += '{}, '.format(col)
        strTableHead = strTableHead[:-2]

        query = 'SELECT {} FROM {}'.format(strTableHead, self.tableName)
        cursor = self.db.cursor()
        # vals = (column2Del, )
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values

    def returnCellsWhere(self, col, matches):
        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT {} FROM {} WHERE {} = '{}'".format(col, self.tableName, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT {} FROM {} WHERE {} IN {}".format(col, self.tableName, searchCol, searchKey)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT {} FROM {} WHERE ".format(col, self.tableName) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.db.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        # print(records)
        cursor.close()
        values = []
        colType = self.get_column_type(col)
        for i in records:
            if colType == 'json':
                values.append(json.loads(i[0]))
            else:
                values.append(i[0])
        return values

    def returnCellsWhereDiffrent(self, col, matches):
        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT {} FROM {} WHERE {} != '{}'".format(col, self.tableName, searchCol, searchKey)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                new = '{} != "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT {} FROM {} WHERE ".format(col, self.tableName) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.db.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        # print(records)
        cursor.close()
        values = []
        colType = self.get_column_type(col)
        for i in records:
            if colType == 'json':
                values.append(json.loads(i[0]))
            else:
                values.append(i[0])
        return values

    def returnColsWhere(self, cols, matches):
        relCols = ''
        for col in cols:
            relCols += '{}, '.format(col)
        relCols = relCols[:-2]

        if isinstance(matches, tuple):
            searchCol, searchKey = matches
            if isinstance(searchKey, str) or isinstance(searchKey, int):
                query = "SELECT {} FROM {} WHERE {} = '{}'".format(relCols, self.tableName, searchCol, searchKey)
            if isinstance(searchKey, tuple):
                query = "SELECT {} FROM {} WHERE {} IN '{}'".format(relCols, self.tableName, searchCol, searchKey)
            if searchKey is None:
                query = "SELECT {} FROM {} WHERE {} IS NULL".format(relCols, self.tableName, searchCol)
        elif isinstance(matches, list):
            text = ''
            for i in matches:
                searchCol, searchKey = i
                if searchKey is None:
                    new = '{} IS NULL AND '.format(searchCol)
                else:
                    new = '{} = "{}" AND '.format(searchCol, searchKey)
                text += new
            query = "SELECT {} FROM {} WHERE ".format(relCols, self.tableName) + text[:-4]
        else:
            raise TypeError('{} must be tuple or list of tuples'.format(matches))

        cursor = self.db.cursor()
        # print('query', query)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        values = []
        for i in records:
            values.append(i)
        return values

    def write_file(self, data, filename):
        # Convert binary data to proper format and write it on Hard Disk
        with open(filename, 'wb') as file:
            file.write(data)


if __name__ == '__main__':

    # iniFile = r"D:\Python\MySQL\database.ini"
    iniFile = r"D:\Python\MySQL\web_db.ini"
    iniFile = r"D:\Python\MySQL\mysqlquerys\src\mysqlquerys\local.ini"

    conf = connect.Config(iniFile)
    testrrrr = Table(conf.credentials, 'testrrrr')
