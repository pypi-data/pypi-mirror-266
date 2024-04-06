import time
from datetime import date
from mysqlquerys import mysql_rm
import connect


def insert_file_to_db():
    #https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/
    ini_file = r"D:\Python\MySQL\test_db.ini"
    txt_file = r"D:\Documente\Munca\ALTEN\Arbeitszeugnis.pdf"
    with open(txt_file, 'rb') as file:
        binaryData = file.read()
    conf = connect.Config(ini_file)
    active_table = mysql_rm.Table(conf.credentials, 'testrrrr')
    query = "INSERT INTO testrrrr (aaa, ccc, biodata) VALUES (%s,%s,%s)"
    insert_blob_tuple = (111, 'aaa', binaryData)
    cursor = active_table.db.cursor()
    result = cursor.execute(query, insert_blob_tuple)
    active_table.db.commit()
    print("Image and file inserted successfully as a BLOB into python_employee table", result)
    cursor.close()


def get_blob():
    test_db = r"D:\Python\MySQL\test_db.ini"
    conf = connect.Config(test_db)
    active_table = mysql_rm.Table(conf.credentials, 'testrrrr')
    print(active_table.columnsProperties)

    cursor = active_table.db.cursor()
    # print(active_table.columnsNames)
    file_name = r'D:\Python\MySQL\test.pdf'
    id = 9
    sql_fetch_blob_query = "SELECT * from testrrrr where id = %s"
    cursor.execute(sql_fetch_blob_query, (id,))
    record = cursor.fetchall()
    for row in record:
        data = row[3]

        with open(file_name, 'wb') as file:
            file.write(data)


def filterRows_order_by():
    chelt_db = r"D:\Python\MySQL\cheltuieli_db.ini"
    conf = connect.Config(chelt_db)
    active_table = mysql_rm.Table(conf.credentials, 'alimentari')
    selectedStartDate = date(2021, 1, 1)
    selectedEndDate = date(2023, 12, 31)
    matches = [('data', (selectedStartDate, selectedEndDate)), ('type', 'benzina')]

    order_by = ('data', 'DESC')

    table = active_table.filterRows(matches, order_by)
    for i in table:
        print(i)



def main():
    script_start_time = time.time()
    selectedStartDate = date(2023, 11, 20)
    selectedEndDate = date(2023, 11, 30)

    chelt_db = r"D:\Python\MySQL\cheltuieli_db.ini"
    # ini_file = r"D:\Python\MySQL\cheltuieli_online\src\rappmysql\static\wdb.ini"
    # test_db = r"D:\Python\MySQL\test_db.ini"

    conf = connect.Config(chelt_db)
    active_table = mysql_rm.Table(conf.credentials, 'alimentari')
    print(active_table.columnsProperties)

    matches = [('type', 'benzina'), ('type', 'intretinere')]
    ids = active_table.returnCellsWhereDiffrent('id',matches)
    # money = active_table.returnCellsWhere('id', matches)
    print(ids)
    for i in ids:
        # match = [('id', i)]
        # val = active_table.returnCellsWhere('type', match)
        # print(val[0])
        active_table.changeCellContent('type', 'electric', 'id', i)

    scrip_end_time = time.time()
    duration = scrip_end_time - script_start_time
    duration = time.strftime("%H:%M:%S", time.gmtime(duration))
    print('run time: {}'.format(duration))

if __name__ == '__main__':
    main()
