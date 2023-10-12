import os
import DataBase as db

def main():
    while True:
        bd_file = input('Введите название файла с базой данных: ')
        if os.path.isfile(bd_file):
            break

        print('Файл', bd_file, 'не найден')    

    tables = db.get_tables_names(bd_file)

    if not tables:
        print('В данном файле не найдено таблиц')
        exit()

    print('-'*100)
    print('Найденные таблицы в', bd_file, '\n')

    for table in tables:
        print(f'Таблица {table}')
        print('Таблица содержит следующие поля:', str(db.get_column_names(bd_file, table))[1:-1], '\n')

    selected_table = tables[0]
    if len(tables) > 1:
        while True:
            selected_table = input('Введите таблицу, с которой будете работать: ')
            if selected_table in tables:
                break

            print('В данной базе данных таблицы', selected_table, 'нет')
    print(f'Для работы выбрана таблица {selected_table}')

    


if __name__ == '__main__':
    main()