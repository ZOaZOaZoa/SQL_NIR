import sqlite3
import IO_funcs as io
import pandas as pd

class DataBase:
    bd_file = None
    tables = None
    selected_table = None
    columns = None
    data_buff = None

    def __init__(self, bd_file: str):
        self.bd_file = bd_file
        self.tables = self.get_tables_names()
        if self.tables:
            self.selected_table = self.tables[0]
            columns = self.get_column_names(self.selected_table)

    def get_tables_names(self):
        '''Получение названий таблиц в БД bd_file'''
        con = sqlite3.connect(self.bd_file)
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
    
    def select_table(self, table_name = None):
        '''Изменить выбранную для работы таблицу'''
        if len(self.tables) == 1:
            return
        
        if table_name is None:
            self.selected_table = io.user_select_table(self)
            return
        
        assert table_name in self.tables
        self.selected_table = table_name
        self.columns = self.get_column_names(table_name)
    
    def get_column_names(self, table_name = None):
        '''Получение списка названий колонок таблицы table_name из БД bd_file'''

        if (table_name is None or table_name == self.selected_table) and self.columns is not None:
            #Возвращение столбцов выбранной таблицы
            return self.columns

        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(f'PRAGMA table_info({table_name})')

        columns = [i[1] for i in cur.fetchall()]
        cur.close()
        con.close()

        return columns

    def get_table_contents(self, table_name = None):
        '''Получение содержимого таблицы из БД'''
        if table_name is None:
            table_name = self.selected_table

        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(f'SELECT * FROM {table_name}')
        data = cur.fetchall()
        cur.close()
        con.close()

        return data

    def show_table(self, table_name = None):
        '''Напечатать таблицу'''
        if table_name is None:
            table_name = self.selected_table

        data = self.get_table_contents(table_name)

        print('\nДанные из таблицы', self.bd_file)
        io.print_table(data, self.get_column_names(table_name))

    def save_table(self, table_name = None):
        '''Сохранение таблицы из БД в файл'''
        if table_name is None:
            table_name = self.selected_table

        data = self.get_table_contents(table_name)
        columns = self.get_column_names(table_name)
        
        file_to_save = io.user_get_save_file_name()
        if file_to_save:
            data_pd = pd.DataFrame(data, columns=columns)
            data_pd.to_csv(file_to_save)

    def get_filtered(self, table_name= None, filter=None, prompt='Полученные данные', print_data=True):
        '''Получение данных из заданной таблицы с учётом фильтра передаваемого после ключевого слова WHERE в SQL запросе.
        table_name - имя таблицы из которой получить данные. Если None, то используется выбранная таблица, хранящаяся в self.selected_table
        filter - фильтр, который будет указан после WHERE в SQL запросе.
        prompt - Сообщение, которое будет выведено перед выводом полученных данных.
        print_data - нужно ли печатать таблицу полученных данных. Значение bool.
        '''
        if table_name is None:
            table_name = self.selected_table
        
        if filter is None:
            filter = io.user_construct_filter(self)

        sql = f'SELECT * FROM {table_name} WHERE {filter}'
        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()

        if prompt:
            print(prompt)
        if print_data:
            io.print_table(data, self.get_column_names(table_name))

        return data
    
    def change_values(self, table_name = None, filter = None):
        if table_name is None:
            table_name = self.selected_table

        if filter is None:
            filter = io.user_construct_filter(self)

        self.get_filtered(table_name, filter=filter, prompt='Данные по заданному фильтру.', print_data=True)
        print()

        columns = self.get_column_names(table_name)
        selected_column = io.user_select_from_list(columns, 'Введите столбец, значение в котором нужно изменить. ', compact_form=True)

        while True:
            value = input('Введите значение для записи: ')

            if value.isnumeric():
                break
        
            if value[0] == value[-1] and value[0] in ['"', "'"]:
                break

            print(f'Значение должно быть числом или обёрнуто в кавычки. Введено {value}')
        
        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(f'UPDATE {table_name} SET {selected_column}={value} WHERE {filter}')
        con.commit()
        cur.close()
        con.close()
    
    def delete_values(self, table_name = None, filter = None):
        if table_name is None:
            table_name = self.selected_table

        if filter is None:
            filter = io.user_construct_filter(self)
        
        data = self.get_filtered(table_name, filter=filter, prompt='Данные по заданному фильтру.', print_data=True)
        ans = input(f'Будет удалено {len(data)} строк. Продолжить? y/n: ')
        if ans != 'y':
            return
        print()

        if filter == '':
            ans = input(f'Удаление данных с заданным фильтром {filter} сотрёт всё содержимое таблицы. Всё равно удалить? y/n: ')
            if ans != 'y':
                return

        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(f'DELETE FROM {table_name} WHERE {filter}')
        con.commit()
        cur.close()
        con.close()

    def insert_values(self, table_name = None):
        if table_name is None:
            table_name = self.selected_table
        
        columns = self.get_column_names(table_name)

        while True:
            rows = input('Введите количество строк, которое вы хотите добавить: ')
            try:
                rows = int(rows)
                break
            except ValueError:
                print(f'Введите целое значение. Получено {rows}')
        
        print()
        rows_data = []
        for i in range(rows):
            print(f'{i+1} строка.')
            row = []
            for column in columns:
                value = input(f'{column} = ')
                row.append(value)
                
            rows_data.append(tuple(row))
            print()
        
        values_format = repr(tuple(['?',]*len(columns))).replace("'", '')
        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.executemany(f'INSERT INTO {table_name} {repr(tuple(columns))} VALUES {values_format}', rows_data)
        con.commit()
        cur.close()
        con.close()