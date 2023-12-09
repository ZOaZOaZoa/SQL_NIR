import os
import DataBase as db
import IO_funcs as io
import E4_funcs as action_funcs

def main():
    #Выбор и открытие базы данных
    while True:
        bd_file = input('Введите название файла с базой данных: ')
        if os.path.isfile(bd_file):
            break

        print('Файл', bd_file, 'не найден')    

    DataBase = db.DataBase(bd_file)
    #Получение информации о таблицах
    if not DataBase.tables:
        print('В данном файле не найдено таблиц')
        exit()

    print('-'*100)
    print('Найденные таблицы в', bd_file, '\n')

    for table in DataBase.tables:
        print(f'Таблица {table}')
        print('Содержащиеся поля:', str(DataBase.get_column_names(table))[1:-1], '\n')

    #Выбор таблицы с которой будет проводиться работа. По умолчанию первая из DataBase.tables
    if len(DataBase.tables) > 1:
        DataBase.select_table()

    #Основная работа с базой данных
    actions = {
        '1': db.DataBase.show_table,
        '2': db.DataBase.save_table,
        '3': db.DataBase.get_filtered, 
        '4': db.DataBase.change_values,
        '5': db.DataBase.delete_values,
        '6': db.DataBase.insert_values,
        '7': db.DataBase.select_table,
        '8': action_funcs.task1,
        '9': action_funcs.task2,
        }
    
    close_program = False
    while not close_program:
        print(f'''Для работы выбрана таблица {DataBase.selected_table}. Выберите действие:''')
        actions_descr = {
            '1': 'Отображение содержимого таблицы на экране',
            '2': 'Сохранение содержимого таблицы в файл',
            '3': 'Отображение содержимого таблицы на экране с учетом фильтра',
            '4': 'Изменение значений в базе данных',
            '5': 'Удаление значений из базы данных',
            '6': 'Внесение новой строки в базу данных',
            '8': 'Информация о ВУЗах по их статусу',
            '9': 'Информация о преподавательских составах федеральных университетов',
            'q': 'Выйти из программы'
        }
        if len(DataBase.tables) > 1:
            actions_descr['7'] = 'Выбор другой таблицы'
        ans = io.user_select_from_list(actions_descr)

        if ans == 'q':
            break

        if ans in actions.keys():
            actions[ans](DataBase)
            continue
        
        print('Опции', ans, 'в списке нет. Введите цифру соответствующую действию или напишите q, чтобы выйти')

if __name__ == '__main__':
    main()