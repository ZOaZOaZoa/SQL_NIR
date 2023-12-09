#IO_funcs.py
import os
import pandas as pd
import DataBase as db

def user_select_table(DataBase):
    while True:
            print('Таблицы данной базе данных:', *DataBase.tables)
            selected_table = input('Введите таблицу, с которой будете работать: ')
            if selected_table in DataBase.tables:
                break

            print('В данной базе данных таблицы', selected_table, 'нет')
    return selected_table

def user_select_from_list(choose_from, prompt='Выберите действие:', compact_form = False):
    '''Выбор пользователем варианта из предоставленных в списке
    choose_from - словарь, с вариантами выбора в качестве ключей и их описаниями в качестве значений. При заданном compact_form=True choose_from это список вариантов
    prompt - приглашение к вводу перед перечислением вариантов выбора.
    compact_form - Если True то вывод происходит в компактном виде. Если False, то на каждый вариант используется целая строка и соответствующее ей описание'''
    while True:
        if prompt:
            print(prompt, end='')

        if compact_form:
            str_variants = ', '.join(choose_from)
            ans = input(f'Варианты. {str_variants}: ')
            if ans not in choose_from:
                print(f'Варианта {ans} в списке действий нет.')
                continue

            return ans

        print()
        for choose in sorted(choose_from.keys()):
            print(f'{choose} - {choose_from[choose]}')
        
        ans = input()
        if ans not in choose_from.keys():
            print(f'Варианта {ans} в списке действий нет.')
            continue
        
        return ans

def user_get_save_file_name():
    '''Запрос и получение названия файла для записи данных. Для отмены используется комбманция !q. Если пользователь вводит 
    существующий файл, то требуется дополнительное подтверждение для перезаписи файла. '''
    ans = ''
    while True:
        print('Введите название файла для сохранения. Для отмены введите !q')
        ans = input('Сохранить данные в файл: ')
        if ans == '!q':
            return None
        
        if os.path.isfile(ans):
            print('Такой файл существует. Уверены, что хотите его перезаписать?\ny - перезаписать, n - не перезаписывать')
            ans2 = input()
            if ans2.lower() != 'y':
                continue
        
        return ans

def print_table(data, columns):
    if len(data) == 0:
        print('В таблице нет данных')
        return
    assert len(data[0]) == len(columns)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    data_pd = pd.DataFrame(data, columns=columns)
    #Используем repr для отображения кавычек для текстовых элементов
    print(data_pd.apply(lambda row: [repr(x) for x in row]))

    pd.reset_option('display.max_rows')
    pd.reset_option('display.width')
    pd.reset_option('display.max_columns')

def user_constuct_simplest_filter(DataBase, table_name = None):
        '''Пользовательский ввод простейшего фильтра вида:
        <столбец> <сравнение> <значение/столбец>'''
        if table_name is None:
            table_name = DataBase.selected_table
        
        column_names = DataBase.get_column_names(table_name)

        selected_column = user_select_from_list(column_names, 'Введите столбец по которому будет проводиться фильтрация. ', compact_form=True)

        relation = user_select_from_list(['>', '>=', '=', '<=', '<'], 'Введите логический фильтр. ', compact_form=True)   

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

def user_construct_filter(DataBase, table_name = None):
    '''Пользовательский ввод фильтра вида:
    <простейший фильтр> <и/или> <простейший фильтр> <и/или> ...'''
    if table_name is None:
        table_name = DataBase.selected_table
    
    constructing = True
    filter = ''
    while constructing:
        filter += user_constuct_simplest_filter(DataBase, table_name)
        
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
                log_dict = ['or', 'and']
                logical = user_select_from_list(log_dict, prompt='Введите логический оператор. ', compact_form=True)
                
                filter += f' {logical} '
                filter += user_constuct_simplest_filter(DataBase, table_name)
    return filter