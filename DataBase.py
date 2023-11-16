import sqlite3
import IO_funcs as io
import pandas as pd

class DataBase:
    bd_file = None
    tables = None
    selected_table = None
    data_buff = None

    def __init__(self, bd_file: str):
        self.bd_file = bd_file
        self.tables = self.get_tables_names()
        if self.tables:
            self.selected_table = self.tables[0]

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
    
    def get_column_names(self, table_name = None):
        '''Получение списка названий колонок таблицы table_name из БД bd_file'''
        if table_name is None:
            table_name = self.selected_table
        #if self.__columns_buff is None:
        def my_factory(c, r):
            d = {}
            for i,name in enumerate(c.description):
                d[name[0]] = r[i]
                d[i] = r[i]
            return d
        
        con = sqlite3.connect(self.bd_file)
        con.row_factory = my_factory
        cur = con.cursor()
        cur.execute(f'SELECT * FROM {table_name}')

        columns = list(cur.fetchone().keys())[::2]
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

    def constuct_simplest_filter(self, table_name = None):
        '''Пользовательский ввод простейшего фильтра вида:
        <столбец> <сравнение> <значение/столбец>'''
        if table_name is None:
            table_name = self.selected_table
        
        column_names = self.get_column_names(table_name)
        print('Столбцы в выбранной таблице.')
        print(*column_names, sep=', ')
        while True:
            selected_column = input('Введите столбец по которому будет проводиться фильтрация: ')
            if selected_column in column_names:
                break

            print(f'Столбца {selected_column} в таблице {table_name} нет')
        
        while True:
            relation = input('Введите логический фильтр. Варианты: >, >=, =, <=, <: ')
            if relation in ['>', '>=', '=', '<=', '<']:
                break

            print(f'Варианта {relation} среди логических фильтров нет.')
        
        while True:
            value = input('Введите значения для сравнения: ')
            if value.isnumeric():
                break

            if value in column_names:
                break

            if value[0] == value[-1] and (value[0] == '"' or value[0] == "'"):
                break 
            
            print(f'Значение для сравнения должно быть числом, названием одного из столбцов или обернуто в кавычки. Получено {value}')

        return selected_column + relation + value

    def construct_filter(self, table_name = None):
        if table_name is None:
            table_name = self.selected_table
        
        constructing = True
        filter = ''
        while constructing:
            filter += self.constuct_simplest_filter(table_name)
            
            while True:
                print(f'\nТекущий фильтр: {filter}')
                print('Выберите дейсвие:\n')
                print('1 - Добавление логического оператора (и/или)')
                print('2 - Завершить создание фильтра')
                ans = input()
                if ans not in ['1', '2']:
                    print(f'Варианта {ans} среди данных действий нет')
                    continue
                    
                if ans == '2':
                    constructing = False
                    break

                if ans == '1':
                    log_dict = {'or': 'или', 'and': 'и'}
                    logical = io.user_select_from_list(log_dict, prompt='Введите логический оператор. ', compact_form=True)
                    
                    filter += f' {logical} '
                    filter += self.constuct_simplest_filter(table_name)
        return filter

    def get_filtered(self, table_name= None):
        if table_name is None:
            table_name = self.selected_table
        
        filter = self.construct_filter()

        sql = f'SELECT * FROM {table_name} WHERE {filter}'
        con = sqlite3.connect(self.bd_file)
        cur = con.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        con.close()

        io.print_table(data, self.get_column_names(table_name))
