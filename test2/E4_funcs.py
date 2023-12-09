import DataBase as db
import IO_funcs as io
import sqlite3
import pandas as pd

def task1(DataBase: db.DataBase):
    #Получение статусов
    con = sqlite3.connect(DataBase.bd_file)
    cur = con.cursor()
    cur.execute('SELECT DISTINCT status FROM vuzkart')
    status_list = [ row[0] for row in cur.fetchall() ]
    cur.close()
    con.close()

    #Выбор статуса
    status_dict = dict(zip(map(str, range(1, len(status_list) + 1)), status_list))
    selected_status = status_dict[io.user_select_from_list(status_dict, 'Выберите статус вуза, который вас интересует:')]
    
    #Получение данных
    con = sqlite3.connect(DataBase.bd_file)
    cur = con.cursor()
    cur.execute(f'SELECT z1 FROM vuzkart WHERE status="{selected_status}"')
    data = [ row[0] for row in cur.fetchall() ]
    cur.execute(f'SELECT z1 FROM vuzkart WHERE status="{selected_status}" AND TRIM(z15) = ""')
    data_pr_null = [ row[0] for row in cur.fetchall() ]
    cur.execute(f'SELECT z1 FROM vuzkart WHERE status="{selected_status}" AND TRIM(z9) = ""')
    data_tel_null = [ row[0] for row in cur.fetchall() ]
    cur.execute(f'SELECT z1 FROM vuzkart WHERE status="{selected_status}" AND TRIM(z9) = "" AND TRIM(z15) = ""')
    data_pr_tel_null = [ row[0] for row in cur.fetchall() ]
    cur.close()
    con.close()

    print(f'Статистика по вузам со статусом {selected_status}')
    print(f'Всего вузов: {len(data)}')
    print(f'Всего вузов без данных о ректоре: {len(data_pr_null)}')
    print(f'Всего вузов без данных о справочном телефоне: {len(data_tel_null)}')
    print(f'Всего вузов без данных о ректоре и справочном телефоне: {len(data_pr_tel_null)}')
    
    print(f'\nВузы без данных о ректоре и справочном телефоне:')
    if data_pr_tel_null:
        print(pd.Series(data_pr_tel_null), '\n')
    else:
        print('Таких вузов не найдено\n')
    
def task2(DataBase : db.DataBase):
    con = sqlite3.connect(DataBase.bd_file)
    cur = con.cursor()
    cur.execute('''select vuzstat.codvuz, z2, PPS, DN+KN, ROUND(CAST(DN+KN AS float)/CAST(PPS AS float)*100, 2)
from vuzstat join vuzkart on vuzstat.codvuz = vuzkart.codvuz 
where vuzkart.gr_ved = "ФУ "; ''')
    data = cur.fetchall()
    cur.close()
    con.close()
    data_pd = pd.DataFrame(data, columns=['Код вуза', 'Название ВУЗа', 'Кол-во преподавателей', 'Кол-во преподавателей с учёными степенями', 'Процент преподавателей с учёными степенями'])
    summary = data_pd.sum()
    summary.iloc[0] = None
    summary.iloc[1] = 'Итого'
    summary.iloc[4] = round((summary.iloc[3] / summary.iloc[2])*100, 2)
    data_pd.loc[len(data_pd)] = summary

    print(f'Информация о федеральных университетах. Всего {len(data)} записей:')
    io.print_table(data_pd, is_dataframe=True)
    print()