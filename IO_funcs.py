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

def user_select_from_list(choose_descr: dict, prompt='Выберите действие:', compact_form = False):
    '''Выбор пользователем варианта из предоставленных в списке
    choose_descr - словарь, с вариантами выбора в качестве ключей и их описаниями в качестве значений.
    prompt - приглашение к вводу перед перечислением вариантов выбора.
    compact_form - Если True то вывод происходит в компактном виде. Если False, то на каждый вариант используется целая строка и соответствующее ей описание'''
    while True:
        if prompt:
            print(prompt, end='')

        if compact_form:
            str_variants = ', '.join(sorted(choose_descr.keys()))
            ans = input(f'Варианты. {str_variants}: ')
            if ans not in choose_descr.keys():
                print(f'Варианта {ans} в списке действий нет.')
                continue

            return ans

        print()
        for choose in sorted(choose_descr.keys()):
            print(f'{choose} - {choose_descr[choose]}')
        
        ans = input()
        if ans not in choose_descr.keys():
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
    assert len(data[0]) == len(columns)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', os.get_terminal_size()[0])
    pd.set_option('display.max_columns', None)

    data_pd = pd.DataFrame(data, columns=columns)
    #Используем repr для отображения кавычек для текстовых элементов
    print(data_pd.apply(lambda row: [repr(x) for x in row]))

    pd.reset_option('display.max_rows')
    pd.reset_option('display.width')
    pd.reset_option('display.max_columns')

