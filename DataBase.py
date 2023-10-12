import sqlite3

def get_tables_names(bd_file):
    con = sqlite3.connect(bd_file)
    cur = con.cursor()
    tables_sql = '''SELECT name FROM sqlite_master 
    WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' 
    UNION ALL SELECT name FROM sqlite_temp_master WHERE type IN ('table','view') ORDER BY 1;'''
    cur.execute(tables_sql)

    data = cur.fetchall()
    tables = [ data[i][0] for i in range(len(data))]
    cur.close()
    con.close()

    return tables

def get_column_names(bd_file, table_name):
    def my_factory(c, r):
        d = {}
        for i,name in enumerate(c.description):
            d[name[0]] = r[i]
            d[i] = r[i]
        return d
    
    con = sqlite3.connect(bd_file)
    con.row_factory = my_factory
    cur = con.cursor()
    cur.execute(f'SELECT * FROM {table_name}')

    columns = list(cur.fetchone().keys())[::2]
    cur.close()
    con.close()

    return columns

def show_table(bd_file, table_name):
    con = sqlite3.connect(bd_file)
    cur = con.cursor()
    cur.execute(f'SELECT * FROM {table_name}')
    data = cur.fetchall()
    cur.close()
    con.close()

    print('\nДанные из таблицы', bd_file)
    for row in data:
        print(row, '\n')

    