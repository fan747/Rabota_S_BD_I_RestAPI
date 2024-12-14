import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import requests
from bs4 import BeautifulSoup
from tkcalendar import Calendar

pdfmetrics.registerFont(TTFont('DejaVuSans', 'Arial.ttf'))

def register_user(username, password):
    response = requests.post('http://localhost:5000/users', json={'username': username, 'password': password})
    if response.status_code == 201:
        messagebox.showinfo("Регистрация", "Пользователь успешно зарегистрирован.")
    else:
        messagebox.showerror("Ошибка", response.json().get("error", "Ошибка регистрации."))

def authenticate_user(username, password):
    response = requests.post('http://localhost:5000/login', json={'username': username, 'password': password})
    return response.status_code == 200


def show_login_window():
    login_window = tk.Toplevel(db_tab)
    login_window.title("Авторизация")

    tk.Label(login_window, text="Логин").grid(row=0, column=0)
    entry_login = tk.Entry(login_window)
    entry_login.grid(row=0, column=1)

    tk.Label(login_window, text="Пароль").grid(row=1, column=0)
    entry_password = tk.Entry(login_window, show='*')
    entry_password.grid(row=1, column=1)

    def on_login():
        username = entry_login.get()
        password = entry_password.get()
        if authenticate_user(username, password):
            login_window.destroy()
            lbl_user.config(text=f"Пользователь: {username}")
            root.deiconify()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль.")

    btn_login = tk.Button(login_window, text="Авторизоваться", command=on_login)
    btn_login.grid(row=2, columnspan=2)

    btn_register = tk.Button(login_window, text="Зарегистрироваться",
                             command=lambda: register_user(entry_login.get(), entry_password.get()))
    btn_register.grid(row=3, columnspan=2)


root = tk.Tk()
root.title("Приложение")

tab_control = ttk.Notebook(root)

db_tab = ttk.Frame(tab_control)
tab_control.add(db_tab, text='Работа с БД')

organizer_tab = ttk.Frame(tab_control)
tab_control.add(organizer_tab, text='Органайзер')

tab_control.grid(row=0, column=0, columnspan=4, sticky='nsew')

organizer_notebook = ttk.Notebook(organizer_tab)

calculator_tab = ttk.Frame(organizer_notebook)
organizer_notebook.add(calculator_tab, text='Калькулятор')

calendar_tab = ttk.Frame(organizer_notebook)
organizer_notebook.add(calendar_tab, text='Календарь')

weather_forecast_tab = ttk.Frame(organizer_notebook)
organizer_notebook.add(weather_forecast_tab, text='Прогноз погоды')

organizer_notebook.pack(expand=True, fill='both')

def calculator():
    def button_click(value):
        current = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current + str(value))

    def calculate():
        try:
            result = eval(entry.get())
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except Exception as e:
            entry.delete(0, tk.END)
            entry.insert(0, "Ошибка")

    def clear():
        entry.delete(0, tk.END)

    entry = tk.Entry(calculator_tab, width=16, font=('Arial', 24), borderwidth=2, relief='solid')
    entry.grid(row=1, column=0, columnspan=4)

    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        'C', '0', '=', '+'
    ]

    row_val = 2
    col_val = 0

    for button in buttons:
        if button == 'C':
            btn = tk.Button(calculator_tab, text=button, width=5, height=2, command=clear)
        elif button == '=':
            btn = tk.Button(calculator_tab, text=button, width=5, height=2, command=calculate)
        else:
            btn = tk.Button(calculator_tab, text=button, width=5, height=2, command=lambda b=button: button_click(b))

        btn.grid(row=row_val, column=col_val)
        col_val += 1
        if col_val > 3:
            col_val = 0
            row_val += 1

    label = tk.Label(calculator_tab, text="Калькулятор", font=('Arial', 16))
    label.grid(row=0, column=0, columnspan=4)

calculator()

def calendar():
    label = tk.Label(calendar_tab, text="Календарь", font=('Arial', 16))
    label.pack(pady=10)

    def show_date():
        selected_date = cal.get_date()
        date_label.config(text=f"Выбранная дата: {selected_date}")

    cal = Calendar(calendar_tab, selectmode='day', year=2024, month=11, day=30)
    cal.pack(pady=20)

    btn_show_date = tk.Button(calendar_tab, text="Показать выбранную дату", command=show_date)
    btn_show_date.pack(pady=10)

    date_label = tk.Label(calendar_tab, text="")
    date_label.pack(pady=10)

calendar()

def weather_forecast():
    label = tk.Label(weather_forecast_tab, text="Прогноз погоды", font=('Arial', 16))
    label.pack(pady=20)

    def get_weather(day_after):
        url = "https://www.meteoservice.ru/weather/14days/chelyabinsk"
        headers = {'user-agent': 'Mozilla/5.0', 'Accept-Language': 'ru-RU'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all('div', class_='row small-collapse medium-uncollapse align-middle')

            temps = []
            for card in cards:
                temps.extend(card.find_all('span', class_='value colorize-server-side'))

            days = []
            for card in cards:
                days.extend(card.find_all('div', class_='text-nowrap grey show-for-large'))

            temp_values = [element.get_text() for element in temps][day_after * 2:day_after * 2 + 2]
            days_values = [element.get_text() for element in days][day_after:day_after + 1]
        return [temp_values, days_values]

    def create_weather_card(parent, weather):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(pady=10)

        month_day_label = tk.Label(frame, text=f"{weather[1][0]}", font=('Arial', 16))
        month_day_label.pack()

        morning_label = tk.Label(frame, text=f"Макс. {weather[0][0]}C", font=('Arial', 12))
        morning_label.pack()

        day_label = tk.Label(frame, text=f"Мин. {weather[0][1]}C", font=('Arial', 12))
        day_label.pack()


    create_weather_card(weather_forecast_tab, get_weather(0))
    create_weather_card(weather_forecast_tab, get_weather(1))
    create_weather_card(weather_forecast_tab, get_weather(2))

weather_forecast()

root.withdraw()

lbl_user = tk.Label(db_tab, text="Пользователь: ")
lbl_user.grid(row=0, column=0, columnspan=4)

show_login_window()


def update_table(table_name):
    response = requests.get(f'http://localhost:5000/table/{table_name}')

    if response.status_code == 200:
        for row in tree.get_children():
            tree.delete(row)
        rows = response.json()
        for row in rows:
            tree.insert("", tk.END, values=row)
    else:
        messagebox.showerror("Ошибка", "Не удалось получить данные из таблицы.")

def validate_ids(id_region, id_branch, id_show):
    response = requests.post('http://localhost:5000/validate_ids', json={
        'id_region': id_region,
        'id_branch': id_branch,
        'id_show': id_show
    })

    if response.status_code == 200:
        return True, response.json().get("message", "")
    else:
        return False, response.json().get("message", "Ошибка при валидации идентификаторов.")


def add_record():
    table_name = selected_table.get()
    fields = get_table_fields(table_name)

    fields.remove('id')

    add_window = tk.Toplevel(db_tab)
    add_window.title(f"Добавить запись в {table_name}")

    entries = {}

    for i, field in enumerate(fields):
        label = tk.Label(add_window, text=field)
        label.grid(row=i, column=0)
        entry = tk.Entry(add_window)
        entry.grid(row=i, column=1)
        entries[field] = entry

    def save_record():
        values = {field: entry.get() for field, entry in entries.items()}
        data = {'table_name': table_name, 'values': values}
        response = requests.post('http://localhost:5000/add_record', json=data)
        if response.status_code == 201:
            add_window.destroy()
            update_table(table_name)
            update_record_count()
        else:
            messagebox.showerror("Ошибка", response.json()['error'])

    btn_save = tk.Button(add_window, text="Добавить", command=save_record)
    btn_save.grid(row=len(fields), columnspan=2)


def edit_record():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Выбор записи", "Пожалуйста, выберите запись для изменения.")
        return

    table_name = selected_table.get()
    fields = get_table_fields(table_name)

    fields.remove('id')
    values = tree.item(selected_item, 'values')

    edit_window = tk.Toplevel(db_tab)
    edit_window.title(f"Изменить запись в {table_name}")

    entries = {}

    for i, field in enumerate(fields):
        label = tk.Label(edit_window, text=field)
        label.grid(row=i, column=0)
        entry = tk.Entry(edit_window)
        entry.grid(row=i, column=1)
        entry.insert(0, values[i + 1])
        entries[field] = entry

    def save_changes():
        values_to_update = {field: entry.get() for field, entry in entries.items()}
        data = {'table_name': table_name, 'id': values[0], 'values_to_update': values_to_update}
        response = requests.post('http://localhost:5000/update_record', json=data)
        if response.status_code == 200:
            edit_window.destroy()
            update_table(table_name)
            update_record_count()
        else:
            messagebox.showerror("Ошибка", response.json()['error'])

    btn_save = tk.Button(edit_window, text="Сохранить", command=save_changes)
    btn_save.grid(row=len(fields), columnspan=2)


def delete_record():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Выбор записи", "Пожалуйста, выберите запись для удаления.")
        return

    if messagebox.askyesno("Подтверждение удаления", "Вы уверены, что хотите удалить эту запись?"):
        record_id = tree.item(selected_item, 'values')[0]
        delete_record_from_db(selected_table.get(), record_id)
        update_table(selected_table.get())
        update_record_count()


def delete_record_from_db(table_name, record_id):
    data = {'table_name': table_name, 'record_id': record_id}
    response = requests.post('http://localhost:5000/delete_record', json=data)


def get_table_fields(table_name):
    url = 'http://127.0.0.1:5000/get_table_fields'
    params = {'table_name': table_name}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['fields']
    else:
        print(f"Error: {response.json().get('error')}")
        return None


def search_record():
    search_id = entry_search.get()
    if not search_id.isdigit():
        messagebox.showerror("Ошибка", "ID должен быть целым числом.")
        return

    url = 'http://127.0.0.1:5000/search_record'
    params = {'table_name': selected_table.get(), 'search_id': search_id}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        record = data['record']

        view_window = tk.Toplevel(db_tab)
        view_window.title("Просмотр записи")

        for field, value in record.items():
            label = tk.Label(view_window, text=f"{field}: {value}")
            label.pack(anchor='w')
    else:
        messagebox.showerror("Ошибка", response.json().get('error'))


lbl_search = tk.Label(db_tab, text="Поиск по ID")
lbl_search.grid(row=1, column=4)

entry_search = tk.Entry(db_tab)
entry_search.grid(row=1, column=5)

btn_search = tk.Button(db_tab, text="Поиск", command=search_record)
btn_search.grid(row=1, column=6)


lbl_user = tk.Label(db_tab, text="Пользователь: ")
lbl_user.grid(row=0, column=0, columnspan=4)

tables = ['Region', 'Statistical_data', 'Show', 'Branch']
selected_table = tk.StringVar(value=tables[0])
table_dropdown = ttk.Combobox(db_tab, textvariable=selected_table, values=tables)
table_dropdown.grid(row=1, column=0)

btn_add = tk.Button(db_tab, text="Добавить", command=add_record)
btn_add.grid(row=1, column=1)

btn_edit = tk.Button(db_tab, text="Изменить", command=edit_record)
btn_edit.grid(row=1, column=2)

btn_delete = tk.Button(db_tab, text="Удалить", command=delete_record)
btn_delete.grid(row=1, column=3)

tree = ttk.Treeview(db_tab, show='headings')
tree.grid(row=2, column=0, columnspan=4)

def instruction():
    messagebox.showinfo("Инструкция", "Для входа в систему необходимо иметь учетную запись, для ее создание необходимо нажать на кнопку “Регистрация” при запуске приложения. После входа в систему, для работы необходимо выбрать необходимую таблицу в выпадающем списке слева сверху, после выбора таблицы в нее можно добавлять новые записи, изменять записи и удалять их. Для добавления новой записи нажмите кнопку “Добавить”, после чего откроется окно, в которое необходимо ввести необходимые данные и нажать кнопку “Добавить”. Для изменения записи, выберите необходимую запись для изменения и нажмите кнопку “Изменить”, после чего откроется окно, в которое необходимо ввести необходимые данные и нажать кнопку “ Изменить”. Для удаления записи, выберите необходимую запись для удаления и нажмите кнопку “Удалить” Для поиска по ID существует поисковик справа сверху, в который необходимо ввести ID нажать на кнопку поиск, после чего откроется окно с найденной записью и ее значениями. Снизу есть элемент со статистическими данными, в нем можно выбрать колонку, ввести значение и получить количество записей с введенным значением, так же там есть общее количество записей. Также можно создавать документы на печать, для этого нужно нажать на кнопку “ Создание документа для печати ”, после того как вы нажали на кнопку откроется окно в котором нужно будет ввести необходимые id записей из таблицы Statistical_data в формате число или число-число, после нажатия на кнопку Создать документ, будет создан документ содержащий в себе все данные из выбранных записей из таблицы Statistical_data, в том числе и данные из связанных таблиц. Документ будет находиться в директории программы.")

btn_about_program = tk.Button(db_tab, text="Инструкция", command=instruction)
btn_about_program.grid(row=6, column=2)

def about_author():
    messagebox.showinfo("Об авторе", "Данная программа и база данных разработана и предоставлена курсантом 365 группы Батуриным О.И. и является собственностью ЧРТ")

btn_about_program = tk.Button(db_tab, text="Об авторе", command=about_author)
btn_about_program.grid(row=6, column=1)

def about_programm():
    messagebox.showinfo("О программе", "Данная программа представляет собой графическое приложение для работы с базой данных, содержащей экономическую информацию. Она разработана с использованием библиотеки Tkinter для создания пользовательского интерфейса и SQLite для хранения данных. \nВерсия программы: 1.0 \nДата создания продукта: 30.11.2024 \nСвязь с разработчиком: oleg.baturin.2006@mail.ru")

btn_about_program = tk.Button(db_tab, text="О программе", command=about_programm)
btn_about_program.grid(row=6, column=0)

def get_record_count(table_name):
    count = 0
    response = requests.get(f'http://localhost:5000/record_count/{table_name}')

    if response.status_code == 200:
        count = response.json()
    else:
        messagebox.showerror("Ошибка", "Не удалось получить данные из таблицы.")

    return count

def update_record_count():
    count = get_record_count(selected_table.get())
    lbl_record_count.config(text=f"Общее количество записей: {count}")

lbl_record_count = tk.Label(db_tab, text="Общее количество записей: 0")
lbl_record_count.grid(row=4, column=0, columnspan=4)


def get_record_count_by_value(table_name, column_name, value):
    url = 'http://localhost:5000/get_record_count_by_value'
    data = {'table_name': table_name, 'column_name': column_name, 'value': value}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json()['count']
    else:
        return None


def search_by_value():
    column_name = selected_column.get()
    value = entry_value.get()

    if not value:
        messagebox.showerror("Ошибка", "Введите значение для поиска.")
        return

    count = get_record_count_by_value(selected_table.get(), column_name, value)
    lbl_value_count.config(text=f"Количество записей с введенным значением: {count}")


lbl_column = tk.Label(db_tab, text="Выберите колонку:")
lbl_column.grid(row=3, column=0)

selected_column = tk.StringVar(value="")
column_dropdown = ttk.Combobox(db_tab, textvariable=selected_column)
column_dropdown.grid(row=3, column=1)

lbl_value = tk.Label(db_tab, text="Введите значение:")
lbl_value.grid(row=3, column=2)

entry_value = tk.Entry(db_tab)
entry_value.grid(row=3, column=3)

btn_search_value = tk.Button(db_tab, text="Поиск", command=search_by_value)
btn_search_value.grid(row=3, column=4)

lbl_value_count = tk.Label(db_tab, text="Количество записей с введенным значением: 0")
lbl_value_count.grid(row=3, column=5)

def print_data():
    print_window = tk.Toplevel(db_tab)
    print_window.title("Печать данных")

    tk.Label(print_window, text="Введите номера записей:").grid(row=0, column=0)
    entry_records = tk.Entry(print_window)
    entry_records.grid(row=0, column=1)

    def create_document():
        record_input = entry_records.get()
        record_ids = parse_record_input(record_input)
        if not record_ids:
            messagebox.showerror("Ошибка", "Введите корректные номера записей.")
            return

        create_pdf_document(record_ids)
        messagebox.showinfo("Успех", "Документ успешно создан!")

    btn_create = tk.Button(print_window, text="Создать документ", command=create_document)
    btn_create.grid(row=1, columnspan=2)

def parse_record_input(input_string):
    ids = []
    ranges = input_string.split(',')
    for range_str in ranges:
        if '-' in range_str:
            start, end = range_str.split('-')
            if start.isdigit() and end.isdigit():
                ids.extend(range(int(start), int(end) + 1))
        elif range_str.isdigit():
            ids.append(int(range_str))
    return ids

def create_pdf_document(record_ids):
    url = 'http://localhost:5000/get_records_by_id'
    data = {'record_ids': record_ids, 'table_name': 'Statistical_data'}
    response = requests.get(url, params=data)

    if response.status_code != 200:
        print("Error: Unable to fetch records.")
        return

    try:
        records = response.json()
    except ValueError as e:
        print(f"JSON Decode Error: {e}")
        return

    id_regions = set(record[3] for record in records)
    id_branches = set(record[4] for record in records)
    id_shows = set(record[5] for record in records)

    pdf_filename = 'Statistical_data_report.pdf'
    document = SimpleDocTemplate(pdf_filename, pagesize=letter)

    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'DejaVuSans'
    styles['Heading2'].fontName = 'DejaVuSans'

    elements.append(Paragraph('Записи Statistical_data', styles['Title']))

    # Добавляем таблицу для Statistical_data
    data = [get_table_fields('Statistical_data')] + records
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    if id_regions:
        url = 'http://localhost:5000/get_records_by_id'
        data = {'record_ids': id_regions, 'table_name': 'Region'}
        response = requests.get(url, params=data)
        region_records = response.json()

        elements.append(Paragraph('Region', styles['Heading2']))
        region_data = [get_table_fields('Region')] + region_records
        region_table = Table(region_data)
        region_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(region_table)

    if id_branches:
        url = 'http://localhost:5000/get_records_by_id'
        data = {'record_ids': id_branches, 'table_name': 'Branch'}
        response = requests.get(url, params=data)
        branch_records = response.json()

        elements.append(Paragraph('Branches', styles['Heading2']))
        branch_data = [get_table_fields('Branch')] + branch_records
        branch_table = Table(branch_data)
        branch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(branch_table)

    if id_shows:
        url = 'http://localhost:5000/get_records_by_id'
        data = {'record_ids': id_shows, 'table_name': 'Show'}
        response = requests.get(url, params=data)
        show_records = response.json()

        elements.append(Paragraph('Show', styles['Heading2']))
        show_data = [get_table_fields('Show')] + show_records
        show_table = Table(show_data)
        show_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(show_table)

    document.build(elements)

btn_print = tk.Button(db_tab, text="Создание документа для печати", command=print_data)
btn_print.grid(row=5, column=5)


def on_table_change(event):
    tree.delete(*tree.get_children())
    tree['columns'] = get_table_fields(selected_table.get())
    for column in tree['columns']:
        tree.column(column, anchor='w')
        tree.heading(column, text=column, anchor='w')

    column_dropdown['values'] = get_table_fields(selected_table.get())
    update_table(selected_table.get())
    update_record_count()

column_dropdown['values'] = get_table_fields(selected_table.get())

update_record_count()


table_dropdown.bind("<<ComboboxSelected>>", on_table_change)

update_table(selected_table.get())

db_tab.mainloop()