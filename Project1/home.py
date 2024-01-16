import customtkinter
from tkinter import messagebox, Checkbutton, IntVar
import pyodbc
from datetime import datetime, timedelta
from customtkinter import CTkLabel
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")
home_window=None
update_window=None

def logout():
    home_window.destroy()
    import signin

def connect_to_database():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=DESKTOP-IU28R6R\\SQLEXPRESS;"
        "DATABASE=Project1;"
        "Trusted_Connection=yes;")

    try:
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        return connection, cursor
    except Exception as e:
        messagebox.showerror('Error', f'Kết nối cơ sở dữ liệu thất bại: {e}')
        print(f'Error: {e}')
        return None, None

def fetch_user_data(cursor, user_id):
    query = 'SELECT * FROM ACCOUNTS WHERE UserID=?'
    cursor.execute(query, user_id)
    return cursor.fetchone()

#Function for tab_1
########################################################################################################### 
def update(user_id):
    connection, cursor = connect_to_database()

    if connection and cursor:
        global update_window
        update_window = customtkinter.CTk()
        update_window.geometry("400x200")
        update_window.title('Thay đổi thông tin')

        user_data = fetch_user_data(cursor, user_id)

        if user_data:
            user_name = user_data[1]

            name_label = customtkinter.CTkLabel(update_window, text="Họ tên:")
            name_label.place(x=20, y=20)

            nameEntry = customtkinter.CTkEntry(update_window, width=200)
            nameEntry.place(x=120, y=20)
            nameEntry.insert(0, user_name)

            birthday_label = customtkinter.CTkLabel(update_window, text="Ngày sinh:")
            birthday_label.place(x=20, y=60)

            day, month, year = (
                user_data[2].day if user_data[2] else "",
                user_data[2].month if user_data[2] else "",
                user_data[2].year if user_data[2] else "",
            )

            day_var = StringVar(value=str(day))
            month_var = StringVar(value=str(month))
            year_var = StringVar(value=str(year))

            day_entry = customtkinter.CTkEntry(update_window, width=30, textvariable=day_var)
            day_entry.place(x=120, y=60)
            day_entry.insert(0, day_var.get())

            separator_label_1 = customtkinter.CTkLabel(update_window, text="/")
            separator_label_1.place(x=150, y=60)

            month_entry = customtkinter.CTkEntry(update_window, width=30, textvariable=month_var)
            month_entry.place(x=160, y=60)
            month_entry.insert(0, month_var.get())

            separator_label_2 = customtkinter.CTkLabel(update_window, text="/")
            separator_label_2.place(x=190, y=60)

            year_entry = customtkinter.CTkEntry(update_window, width=45, textvariable=year_var)
            year_entry.place(x=200, y=60)
            year_entry.insert(0, year_var.get())

            gender_label = customtkinter.CTkLabel(update_window, text="Giới tính:")
            gender_label.place(x=20, y=100)
            
            gender_var = user_data[3] if user_data[3] is not None else None
            gender_options = [' ', 'F', 'M', 'O']

            gender_dropdown = customtkinter.CTkComboBox(update_window, width=60, values=gender_options, state="readonly")
            gender_dropdown.place(x=120, y=100)
            if gender_var:
                gender_dropdown.set(gender_var)
            else:
                gender_dropdown.set(' ')

            confirm_button = customtkinter.CTkButton(update_window, text='Xác nhận', command=lambda: update_user_data(user_id, nameEntry.get(), day_entry.get(), month_entry.get(), year_entry.get(), gender_dropdown.get()))
            confirm_button.place(x=20, y=140)

            update_window.mainloop()
        else:
            messagebox.showerror('Error', 'Không thể lấy dữ liệu người dùng.')

    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')

def update_user_data(user_id, name, day, month, year, gender):
    try:
        if (day and month and year) or (not day and not month and not year):
            day, month, year = int(day) if day else None, int(month) if month else None, int(year) if year else None

            if day and (day < 1 or day > 31 or (day > 29 and month == 2) or
                        (day > 30 and month in [4, 6, 9, 11]) or
                        (day > 31 and month in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày không hợp lệ.')
                return

            if month and (month < 1 or month > 12):
                messagebox.showerror('Error', 'Tháng không hợp lệ.')
                return

            if year and (year < 1900 or year > 2100):
                messagebox.showerror('Error', 'Năm không hợp lệ.')
                return

            birthdate = datetime(year, month, day) if day and month and year else None
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm hoặc để trống cả ba trường.')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày sinh không hợp lệ.')
        return

    if gender == ' ':
        gender = None 
    connection, cursor = connect_to_database()

    if connection and cursor:
        try:
            if len(name.strip()) == 0:
                messagebox.showerror('Error', 'Vui lòng nhập tên.')
                return
            
            update_query = 'UPDATE ACCOUNTS SET Ten=?, Ngaysinh=?, Gioitinh=? WHERE UserID=?'
            print("Values:", name, birthdate, gender, user_id)
            try:
                cursor.execute(update_query, name, birthdate, gender, user_id)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Cập nhật thông tin thành công!')
                update_window.destroy()
                home_window.destroy()
                home_page(user_id)
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')



def calculate_balance(user_id):
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=?'
            cursor.execute(query, user_id, 'Thu')
            result = cursor.fetchone()
            EarnAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=?'
            cursor.execute(query, user_id, 'Chi')
            result = cursor.fetchone()
            SpendAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=?'
            cursor.execute(query, user_id, 'Vay')
            result = cursor.fetchone()
            BorrowAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=?'
            cursor.execute(query, user_id, 'Nợ')
            result = cursor.fetchone()
            OweAmount = result[0] if result[0] else 0

            Amount = EarnAmount + BorrowAmount - OweAmount - SpendAmount    

            query = 'UPDATE ACCOUNTS SET Sodu = ? WHERE UserID=?'
            print(Amount, user_id)
            try:
                cursor.execute(query, Amount, user_id)
                connection.commit()
                print("Update Amount Successful")
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật số dư thất bại: {e}')

            return EarnAmount, SpendAmount, BorrowAmount, OweAmount
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật số dư thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.') 
    return None, None, None, None

def calculate_balance_period(user_id, startdate: datetime, enddate: datetime):
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=? AND Ngay BETWEEN ? AND ?'
            cursor.execute(query, user_id, 'Thu', startdate, enddate)
            result = cursor.fetchone()
            EarnAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=? AND Ngay BETWEEN ? AND ?'
            cursor.execute(query, user_id, 'Chi', startdate, enddate)
            result = cursor.fetchone()
            SpendAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=? AND Ngay BETWEEN ? AND ?'
            cursor.execute(query, user_id, 'Vay', startdate, enddate)
            result = cursor.fetchone()
            BorrowAmount = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS WHERE UserID=? AND Loai=? AND Ngay BETWEEN ? AND ?'
            cursor.execute(query, user_id, 'Nợ', startdate, enddate)
            result = cursor.fetchone()
            OweAmount = result[0] if result[0] else 0

            Amount = EarnAmount + BorrowAmount - OweAmount - SpendAmount    

            return Amount, EarnAmount, SpendAmount, BorrowAmount, OweAmount
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật số dư thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.') 
    return None, None, None, None, None

    
def display_user_info(frame, user_data):
    frame.pack()

    font_size = 20 

    name_label = customtkinter.CTkLabel(frame, text="Tên: " + str(user_data[1]), font=('Time New Roman', font_size))
    name_label.pack(pady=20)

    birthday_value = user_data[2].strftime("%d-%m-%Y") if user_data[2] is not None else "Chưa nhập"
    birthday_label = customtkinter.CTkLabel(frame, text="Ngày sinh: " + birthday_value, font=('Time New Roman', font_size))
    birthday_label.pack(pady=20)

    gender_value = {
        None: "Chưa nhập",
        'M': "Nam",
        'F': "Nữ",
        'O': "Khác"
    }.get(user_data[3], "Chưa nhập")
    gender_label = customtkinter.CTkLabel(frame, text="Giới tính: " + gender_value, font=('Time New Roman', font_size))
    gender_label.pack(pady=20)

    email_label = customtkinter.CTkLabel(frame, text="Email: " + str(user_data[4]), font=('Time New Roman', font_size))
    email_label.pack(pady=20)

    balance_label = customtkinter.CTkLabel(frame, text="Số dư: " + str(user_data[9]) + "đ", font=('Time New Roman', font_size))
    balance_label.pack(pady=20)
    print("User Data:", user_data)  #debug

def set_to_unlocked(user_id):
    connection, cursor = connect_to_database()

    if connection and cursor:
        try:
            update_query = 'UPDATE ACCOUNTS SET Khoa = NULL, Thoigiankhoa=NULL WHERE UserID = ?'
            try:
                cursor.execute(update_query, user_id)
                connection.commit()
                print("Update Successful")
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')

#Function for tab_2
########################################################################################################### 
def display_transaction_detail(transaction_id):
    detail_window = customtkinter.CTk()
    detail_window.geometry("500x350")
    detail_window.title('Chi tiết giao dịch')
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM TRANSACTIONS WHERE TransactionID = ?'
    cursor.execute(query, transaction_id)
    transaction_data = cursor.fetchone()

    CategoryLabel = customtkinter.CTkLabel(detail_window, text='Hạng mục: ', font=('Time New Roman', 15))
    CategoryLabel.place(x=100, y=50)
    query = 'SELECT Tenhangmuc FROM CATEGORIES'
    cursor.execute(query)
    temp = cursor.fetchall()
    Category_options = [] 
    for i, option in enumerate(temp): 
        Category_options.append(str(option[0])) 
    CategoryDropdown = customtkinter.CTkComboBox(detail_window, width=120, values=Category_options, state="readonly")
    CategoryDropdown.place(x=200, y=50)
    query = 'SELECT Tenhangmuc FROM CATEGORIES WHERE CategoryID = ?'
    cursor.execute(query, transaction_data[4])
    current = cursor.fetchone()[0]
    CategoryDropdown.set(current)
    
    TypeLabel = customtkinter.CTkLabel(detail_window, text='Loại giao dịch: ', font=('Time New Roman', 15))
    TypeLabel.place(x=100, y=80)
    type_options = ['Thu', 'Chi', 'Vay', 'Nợ']
    TypeDropdown = customtkinter.CTkComboBox(detail_window, width=60, values=type_options, state="readonly")
    TypeDropdown.place(x=200, y=80)
    TypeDropdown.set(transaction_data[3])

    DateLabel = customtkinter.CTkLabel(detail_window, text='Ngày: ', font=('Time New Roman', 15))
    DateLabel.place(x=100, y=110)
    day, month, year = (
                transaction_data[2].day if transaction_data[2] else "",
                transaction_data[2].month if transaction_data[2] else "",
                transaction_data[2].year if transaction_data[2] else "",
            )

    day_var = StringVar(value=str(day))
    month_var = StringVar(value=str(month))
    year_var = StringVar(value=str(year))

    day_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=day_var)
    day_entry.place(x=200, y=110)
    day_entry.insert(0, day_var.get())

    separator_label_1 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_1.place(x=230, y=110)

    month_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=month_var)
    month_entry.place(x=240, y=110)
    month_entry.insert(0, month_var.get())

    separator_label_2 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_2.place(x=270, y=110)

    year_entry = customtkinter.CTkEntry(detail_window, width=45, textvariable=year_var)
    year_entry.place(x=280, y=110)
    year_entry.insert(0, year_var.get())

    AmountLabel = customtkinter.CTkLabel(detail_window, text='Số tiền: ', font=('Time New Roman', 15))
    AmountLabel.place(x=100, y=140)
    Amount_entry = customtkinter.CTkEntry(detail_window, width=100)
    Amount_entry.place(x=200, y=140)
    Amount_entry.insert(0, str(transaction_data[1]))

    NoteLabel = customtkinter.CTkLabel(detail_window, text='Chú thích: ', font=('Time New Roman', 15))
    NoteLabel.place(x=100, y=170)
    Note_entry = customtkinter.CTkEntry(detail_window, width=200)
    Note_entry.place(x=200, y=170)
    if transaction_data[5]:
        Note_entry.insert(0, str(transaction_data[5]))

    NameLabel = customtkinter.CTkLabel(detail_window, text='Tên người vay/nợ: ', font=('Time New Roman', 15))
    NameLabel.place(x=100, y=200)
    Name_entry = customtkinter.CTkEntry(detail_window, width=80)
    Name_entry.place(x=225, y=200)
    if transaction_data[6]:
        Name_entry.insert(0, transaction_data[6])

    SetDateLabel = customtkinter.CTkLabel(detail_window, text='Ngày cố định: ', font=('Time New Roman', 15))
    SetDateLabel.place(x=100, y=230)
    SetDate_entry = customtkinter.CTkEntry(detail_window, width=80)
    SetDate_entry.place(x=200, y=230)
    if transaction_data[7]:
        SetDate_entry.set(str(transaction_data[7]))

    CloseButton = customtkinter.CTkButton(detail_window, width=50, text = "Đóng", command =  lambda: detail_window.destroy())
    CloseButton.place(x=100, y=260)

    UpdateButton = customtkinter.CTkButton(detail_window, width=50, text="Cập nhật", command=lambda: (
        print("Amount:", int(Amount_entry.get())),
        print("Day:", day_entry.get()),
        print("Month:", month_entry.get()),
        print("Year:", year_entry.get()),
        print("Type:", TypeDropdown.get()),
        print("Category:", CategoryDropdown.get()),
        print("Note:", Note_entry.get()),
        print("Name:", Name_entry.get()),
        print("SetDate:", int(SetDate_entry.get()) if SetDate_entry.get()  else None),
        update_transaction(
            transaction_id,
            int(Amount_entry.get()),
            day_entry.get(),
            month_entry.get(),
            year_entry.get(),
            TypeDropdown.get(),
            CategoryDropdown.get(),
            Note_entry.get(),
            Name_entry.get(),
            int(SetDate_entry.get()) if SetDate_entry.get() else None,
            transaction_data[8],
            detail_window
        )
    ))

    UpdateButton.place(x=160, y=260)
    '''DeleteButton = customtkinter.CTkButton(detail_window, width=50, text="Xóa", command=lambda: delete_transaction(transaction_id, detail_window, transaction_data[8]))
    DeleteButton.place(x=230, y=260)'''

    if transaction_data[3] == 'Chi':
        PlanButton = customtkinter.CTkButton(detail_window, width=100, text = "Các kế hoạch", command=lambda: display_plan_transaction(transaction_id, transaction_data[8]))
        PlanButton.place(x=100,y=290) 

    detail_window.mainloop()
    return detail_window

def display_plan_transaction(transaction_id, user_id):
    frame=customtkinter.CTk()
    frame.geometry("800x600")
    frame.title("Chi tiết các kế hoạch")
    customtkinter.CTkLabel(frame, text="Ấn vào kế hoạch để xóa liên kết", font=('Time New Roman', 16)).pack(side='bottom', pady=5)
    connection, cursor = connect_to_database()
    query = 'SELECT TransactionID, PLANS.PlanID, Ngaybatdau, Ngayketthuc, Tenkehoach, Ngansach, Tiencon FROM TRANSACTIONS_PLANS, PLANS WHERE PLANS.PlanID = TRANSACTIONS_PLANS.PlanID AND TransactionID = ?'
    cursor.execute(query, transaction_id)
    plans_data = cursor.fetchall()
    if plans_data:
        plans_list = []

        for i, plan in enumerate(plans_data):
            plan_id = plan[1]
            plan_frame = customtkinter.CTkFrame(frame, fg_color='transparent')

            text = f'{plan[2].day}/{plan[2].month}/{plan[2].year} - {plan[3].day}/{plan[3].month}/{plan[3].year} - {plan[4]} - {plan[6]}/{plan[5]}'

            Information = customtkinter.CTkButton(plan_frame, text=text, anchor='w', fg_color="red", width=600, font=('Time New Roman', 15), command=lambda id=plan_id: delete_plan_transaction(id, transaction_id, frame))
            Information.pack(padx=10, pady = 10,expand=True, fill='x')
            plans_list.append(plan_frame)

        for plan in plans_list:
            plan.pack()

    else:
        customtkinter.CTkLabel(frame, text="Không có liên kết với kế hoạch nào.", font=('Time New Roman', 30)).pack(padx=10, pady=10)
    
    AddButton = customtkinter.CTkButton(frame, width=100, text='Thêm liên kết', command=lambda: add_to_plan(transaction_id, user_id))
    AddButton.pack(side='bottom',pady=10)

    frame.mainloop()

def update_transaction(transaction_id, amount, day, month, year, type, category, note, name, setdate, userid, detail_window):
    try:
        if day and month and year:
            day, month, year = int(day) if day else None, int(month) if month else None, int(year) if year else None

            if day and (day < 1 or day > 31 or (day > 29 and month == 2) or
                        (day > 30 and month in [4, 6, 9, 11]) or
                        (day > 31 and month in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày không hợp lệ.')
                return

            if month and (month < 1 or month > 12):
                messagebox.showerror('Error', 'Tháng không hợp lệ.')
                return

            if year and (year < 1900 or year > 2100):
                messagebox.showerror('Error', 'Năm không hợp lệ.')
                return

            date = datetime(year, month, day) if day and month and year else None
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày giao dịch không hợp lệ.')
        return
    
    if(type == None or category==None):
        messagebox.showerror('Error', 'Vui lòng chọn hạng mục và loại chi tiêu.')
        return
    
    connection, cursor = connect_to_database()
    query = 'SELECT CategoryID, Loai FROM CATEGORIES WHERE Tenhangmuc = ?'
    cursor.execute(query, category)
    temp=cursor.fetchone()
    categoryID=temp[0]
    checktype =temp[1]
    if (checktype != type):
        messagebox.showerror('Error', 'Hạng mục và loại không tương thích')
        return

    if connection and cursor:
        try:
            if amount == None:
                messagebox.showerror('Error', 'Vui lòng nhập số tiền.')
                return
            
            if (type != 'Vay' and type != 'Nợ' and len(name) != 0):
                messagebox.showerror('Error', 'Loại giao dịch hiện tại không thể nhập người vay/nợ')
                return
            
            update_query = 'UPDATE TRANSACTIONS SET Sotien=?, Ngay=?, Loai=?, CategoryID=?, Chuthich=?, Tennguoivayno=?, Ngaycodinh=? WHERE TransactionID=?'
            print("Values:", amount, date, type, categoryID, note, name, setdate, transaction_id)
            try:
                cursor.execute(update_query, amount, date, type, categoryID, note, name, setdate, transaction_id)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Cập nhật thông tin thành công!')
                detail_window.destroy()
                home_window.destroy()
                home_page(userid) 
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')                                                                                                                

def delete_transaction(transaction_id, detail_window, userid):
    result = messagebox.askokcancel("Xác nhận", "Bạn có muốn xóa khoản vay/nợ này không?")
    if result:
        connection, cursor = connect_to_database()
        if connection and cursor:
            try:
                update_query2 = 'DELETE FROM TRANSACTIONS WHERE TransactionID=?'
                update_query1 = 'DELETE FROM TRANSACTIONS_PLANS WHERE TransactionID=?'
                print("Values:", transaction_id)
                try:
                    cursor.execute(update_query1, transaction_id)
                    connection.commit()
                    cursor.execute(update_query2, transaction_id)
                    connection.commit()
                    print("Update Successful")
                    messagebox.showinfo('Success', 'Xóa giao dịch thành công!')
                    detail_window.destroy()
                    home_window.destroy()
                    home_page(userid) 
                except Exception as e:
                    print(f'Error during update: {e}')
                    messagebox.showerror('Error', f'Xóa giao dịch thất bại: {e}')
            except Exception as e:
                messagebox.showerror('Error', f'Xóa giao dịch thất bại: {e}')

            connection.close()
        else:
            messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')       

def add_to_plan(transaction_id, user_id):
    frame = customtkinter.CTk()
    frame.geometry("800x600")
    frame.title("Danh sách các kế hoạch")
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM PLANS WHERE UserID = ? AND PlanID NOT IN (SELECT PlanID FROM TRANSACTIONS_PLANS WHERE TransactionID = ?) ORDER BY Ngaybatdau DESC'
    cursor.execute(query, user_id, transaction_id)
    plans_data = cursor.fetchall()
    if plans_data:
        plans_list = []

        for i, plan in enumerate(plans_data):
            plan_id = plan[0]
            plan_frame = customtkinter.CTkFrame(frame, fg_color='transparent')

            text = f'{plan[2].day}/{plan[2].month}/{plan[2].year} - {plan[3].day}/{plan[3].month}/{plan[3].year} - {plan[1]} - Số tiền còn: {plan[5]}/{plan[4]}'

            Information = customtkinter.CTkButton(plan_frame, text=text, anchor='w', width=600, font=('Time New Roman', 15), command=lambda id=plan_id: confirm_add_transactions_plans(id, transaction_id, frame))
            Information.pack(padx=10, pady = 10,expand=True, fill='x')
            plans_list.append(plan_frame)

        for plan in plans_list:
            plan.pack()

    else:
        customtkinter.CTkLabel(frame, text="Người dùng không còn kế hoạch nào.", font=('Time New Roman', 30)).pack(padx=10, pady=10)

    frame.mainloop()
    
def confirm_add_transactions_plans(plan_id, transaction_id, frame):
    result = messagebox.askokcancel("Xác nhận", "Bạn có muốn thêm liên kết với kế hoạch này không?")
    if result:
        connection, cursor = connect_to_database()
        if connection and cursor:
            query = 'SELECT Ngay FROM TRANSACTIONS WHERE TransactionID=?'
            cursor.execute(query, transaction_id)
            result = cursor.fetchone()
            transaction_date = result[0]

            query = 'SELECT Ngaybatdau, Ngayketthuc FROM PLANS WHERE PlanID=?'
            cursor.execute(query, plan_id)
            result = cursor.fetchone()
            plan_startdate, plan_enddate = result[0], result[1]
            if(transaction_date < plan_startdate) or (transaction_date > plan_enddate):
                messagebox.showerror("Error", "Ngày của giao dịch nằm ngoài thời gian kế hoạch")
                return
            
            query = 'SELECT Ngansach FROM PLANS WHERE PlanID=?'
            cursor.execute(query, plan_id)
            result = cursor.fetchone()
            budget = result[0]

            query = 'SELECT Tiencon FROM PLANS WHERE PlanID=?'
            cursor.execute(query, plan_id)
            result = cursor.fetchone()
            remain = result[0]

            query = 'SELECT Sotien FROM TRANSACTIONS WHERE TransactionID=?'
            cursor.execute(query, transaction_id)
            result = cursor.fetchone()
            amount = result[0]
            if(remain < amount):
                messagebox.showerror("Error", "Số tiền của giao dịch vượt quá số tiền còn lại của kế hoạch")
                return
            try:
                update_query = 'INSERT INTO TRANSACTIONS_PLANS(TransactionID, PlanID) VALUES (?, ?)'
                print("Values:", transaction_id, plan_id)
                try:
                    cursor.execute(update_query, transaction_id, plan_id)
                    connection.commit()
                    print("Update Successful")
                    calculate_remain(plan_id)
                    messagebox.showinfo('Success', 'Thêm thành công!')
                    frame.destroy()
                except Exception as e:
                    print(f'Error during update: {e}')
                    messagebox.showerror('Error', f'Thêm thất bại: {e}')
            except Exception as e:
                messagebox.showerror('Error', f'Thêm thất bại: {e}')
            if(remain - amount < 0.1*budget):
                messagebox.showinfo("Reminder", "Tiền trong kế hoạch sắp hết") 

            connection.close()
        else:
            messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')
    else:
        return    

def display_transactions_info(frame, user_id):
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM TRANSACTIONS WHERE UserID = ? ORDER BY Ngay DESC'
    cursor.execute(query, user_id)
    transactions_data = cursor.fetchall()
    if transactions_data:
        canvas_width = 610 
        canvas_height = 550

        canvas = customtkinter.CTkCanvas(frame, width=canvas_width, height=canvas_height)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = customtkinter.CTkFrame(canvas, bg_color='transparent')
        inner_frame.pack(fill='both', expand=True)

        transactions_list = []

        for i, transaction in enumerate(transactions_data):
            transaction_id = transaction[0]
            transaction_frame = customtkinter.CTkFrame(inner_frame, fg_color='transparent')

            query = 'SELECT Tenhangmuc FROM CATEGORIES WHERE CategoryID = ?'
            cursor.execute(query, transaction[4])
            Tenhangmuc = cursor.fetchone()[0]
            text = f'{transaction[2].day}/{transaction[2].month}/{transaction[2].year} - {Tenhangmuc} - Số tiền: {transaction[1]}đ'

            Information = customtkinter.CTkButton(transaction_frame, text=text, anchor='w', width=600, font=('Time New Roman', 15), command=lambda id=transaction_id: display_transaction_detail(id))
            if (transaction[4] > 410000 and transaction[4] < 420000):
                Information.configure(fg_color = 'red')
            elif (transaction[4] > 420000 and transaction[4] < 430000):
                Information.configure(fg_color = 'orange')
            elif (transaction[4] > 430000 and transaction[4] < 440000):
                Information.configure(fg_color = 'blue')
            Information.pack(padx=5, pady = 5,expand=True, fill='x')
            transactions_list.append(transaction_frame)


        inner_frame.update_idletasks()
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        def on_canvas_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_canvas_configure)

        return transactions_list
    else:
        return None

def add_transactions(user_id):
    add_window = customtkinter.CTk()
    add_window.geometry("500x350")
    add_window.title('Thêm giao dịch')
    connection, cursor = connect_to_database()

    CategoryLabel = customtkinter.CTkLabel(add_window, text='Hạng mục: ', font=('Time New Roman', 15))
    CategoryLabel.place(x=100, y=50)
    query = 'SELECT Tenhangmuc FROM CATEGORIES'
    cursor.execute(query)
    temp = cursor.fetchall()
    Category_options = [] 
    for i, option in enumerate(temp): 
        Category_options.append(str(option[0])) 
    CategoryDropdown = customtkinter.CTkComboBox(add_window, width=120, values=Category_options, state="readonly")
    CategoryDropdown.place(x=200, y=50)
    
    TypeLabel = customtkinter.CTkLabel(add_window, text='Loại giao dịch: ', font=('Time New Roman', 15))
    TypeLabel.place(x=100, y=80)
    type_options = ['Thu', 'Chi', 'Vay', 'Nợ']
    TypeDropdown = customtkinter.CTkComboBox(add_window, width=60, values=type_options, state="readonly")
    TypeDropdown.place(x=200, y=80)

    DateLabel = customtkinter.CTkLabel(add_window, text='Ngày: ', font=('Time New Roman', 15))
    DateLabel.place(x=100, y=110)

    day_entry = customtkinter.CTkEntry(add_window, width=30)
    day_entry.place(x=200, y=110)

    separator_label_1 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_1.place(x=230, y=110)

    month_entry = customtkinter.CTkEntry(add_window, width=30)
    month_entry.place(x=240, y=110)

    separator_label_2 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_2.place(x=270, y=110)

    year_entry = customtkinter.CTkEntry(add_window, width=45)
    year_entry.place(x=280, y=110)

    AmountLabel = customtkinter.CTkLabel(add_window, text='Số tiền: ', font=('Time New Roman', 15))
    AmountLabel.place(x=100, y=140)
    Amount_entry = customtkinter.CTkEntry(add_window, width=100)
    Amount_entry.place(x=200, y=140)

    NoteLabel = customtkinter.CTkLabel(add_window, text='Chú thích: ', font=('Time New Roman', 15))
    NoteLabel.place(x=100, y=170)
    Note_entry = customtkinter.CTkEntry(add_window, width=200)
    Note_entry.place(x=200, y=170)

    NameLabel = customtkinter.CTkLabel(add_window, text='Tên người vay/nợ: ', font=('Time New Roman', 15))
    NameLabel.place(x=100, y=200)
    Name_entry = customtkinter.CTkEntry(add_window, width=80)
    Name_entry.place(x=225, y=200)

    SetDateLabel = customtkinter.CTkLabel(add_window, text='Ngày cố định: ', font=('Time New Roman', 15))
    SetDateLabel.place(x=100, y=230)
    SetDate_entry = customtkinter.CTkEntry(add_window, width=80)
    SetDate_entry.place(x=200, y=230)

    query = 'SELECT TransactionID FROM TRANSACTIONS'
    cursor.execute(query)
    results=cursor.fetchall()
    transaction_id = 200001
    existing_transaction_ids = [result[0] for result in results]
    while transaction_id in existing_transaction_ids:
        transaction_id+=1

    ConfirmButton = customtkinter.CTkButton(add_window, width=50, text="Xác nhận", command=lambda: (
        print("Amount:", int(Amount_entry.get())),
        print("Day:", day_entry.get()),
        print("Month:", month_entry.get()),
        print("Year:", year_entry.get()),
        print("Type:", TypeDropdown.get()),
        print("Category:", CategoryDropdown.get()),
        print("Note:", Note_entry.get()),
        print("Name:", Name_entry.get()),
        print("SetDate:", int(SetDate_entry.get()) if SetDate_entry.get()  else None),
        add_transaction_todtb(
            transaction_id,
            int(Amount_entry.get()),
            day_entry.get(),
            month_entry.get(),
            year_entry.get(),
            TypeDropdown.get(),
            CategoryDropdown.get(),
            Note_entry.get(),
            Name_entry.get(),
            int(SetDate_entry.get()) if SetDate_entry.get() else None,
            user_id,
            add_window
        )
    ))

    ConfirmButton.place(x=100, y=260)
                                           
    add_window.mainloop()
    return add_window

def add_transaction_todtb(transaction_id, amount, day, month, year, type, category, note, name, setdate, userid, add_window):
    try:
        if day and month and year:
            day, month, year = int(day) if day else None, int(month) if month else None, int(year) if year else None

            if day and (day < 1 or day > 31 or (day > 29 and month == 2) or
                        (day > 30 and month in [4, 6, 9, 11]) or
                        (day > 31 and month in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày không hợp lệ.')
                return

            if month and (month < 1 or month > 12):
                messagebox.showerror('Error', 'Tháng không hợp lệ.')
                return

            if year and (year < 1900 or year > 2100):
                messagebox.showerror('Error', 'Năm không hợp lệ.')
                return

            date = datetime(year, month, day) if day and month and year else None
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày giao dịch không hợp lệ.')
        return
    
    if(type == None or category==None):
        messagebox.showerror('Error', 'Vui lòng chọn hạng mục và loại chi tiêu.')
        return
    
    connection, cursor = connect_to_database()
    query = 'SELECT CategoryID, Loai FROM CATEGORIES WHERE Tenhangmuc = ?'
    cursor.execute(query, category)
    temp=cursor.fetchone()
    categoryID=temp[0]
    checktype =temp[1]
    if (checktype != type):
        messagebox.showerror('Error', 'Hạng mục và loại không tương thích')
        return

    if connection and cursor:
        try:
            if amount == None:
                messagebox.showerror('Error', 'Vui lòng nhập số tiền.')
                return
            
            if (type != 'Vay' and type != 'Nợ' and len(name) != 0):
                messagebox.showerror('Error', 'Loại giao dịch hiện tại không thể nhập người vay/nợ')
                return
            
            update_query = 'INSERT INTO TRANSACTIONS(TransactionID, Sotien, Ngay, Loai, CategoryID, Chuthich, Tennguoivayno, Ngaycodinh, UserID) Values (?, ?, ?, ?, ?, ?, ?, ?, ?)'
            print(transaction_id, amount, date, type, categoryID, note, name, setdate, userid)
            try:
                cursor.execute(update_query, transaction_id, amount, date, type, categoryID, note, name, setdate, userid)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Thêm giao dịch thành công!')
                add_window.destroy()
                home_window.destroy()
                home_page(userid) 
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Thêm giao dịch thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Thêm giao dịch thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')   



def delete_plan_transaction(plan_id, transaction_id, detail_window):
    result = messagebox.askokcancel("Xác nhận", "Bạn có muốn xóa liên kết với kế hoạch này không?")
    if result:
        connection, cursor = connect_to_database()
        if connection and cursor:
            try:
                update_query = 'DELETE FROM TRANSACTIONS_PLANS WHERE TransactionID=? AND PlanID=?'
                print("Values:", transaction_id, plan_id)
                try:
                    cursor.execute(update_query, transaction_id, plan_id)
                    connection.commit()
                    calculate_remain(plan_id)
                    print("Update Successful")
                    messagebox.showinfo('Success', 'Xóa thành công!')
                    calculate_remain(plan_id)
                    detail_window.destroy()
                except Exception as e:
                    print(f'Error during update: {e}')
                    messagebox.showerror('Error', f'Xóa thất bại: {e}')
            except Exception as e:
                messagebox.showerror('Error', f'Xóa thất bại: {e}')

            connection.close()
        else:
            messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')
    else:
        return    


#Function for tab_3
########################################################################################################### 
def display_plans_info(frame, user_id):
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM PLANS WHERE UserID = ? ORDER BY Ngaybatdau DESC'
    cursor.execute(query, user_id)
    plans_data = cursor.fetchall()
    if plans_data:
        canvas_width = 700
        canvas_height = 500

        canvas = customtkinter.CTkCanvas(frame, width=canvas_width, height=canvas_height)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = customtkinter.CTkFrame(canvas, bg_color='transparent')
        inner_frame.pack(fill='both', expand=True)

        plans_list = []

        for i, plan in enumerate(plans_data):
            plan_id = plan[0]
            calculate_remain(plan_id)
            plan_frame = customtkinter.CTkFrame(inner_frame, fg_color='transparent')

            text = f'{plan[2].day}/{plan[2].month}/{plan[2].year} - {plan[3].day}/{plan[3].month}/{plan[3].year} - {plan[1]} - Số tiền còn: {plan[5]}/{plan[4]}đ'

            Information = customtkinter.CTkButton(plan_frame, text=text, anchor='w', width=600, font=('Time New Roman', 15), command=lambda id=plan_id: display_plan_detail(id))
            if(plan[5] <= 0.1*plan[4] and plan[5]>0): 
                Information.configure(fg_color = 'orange')
            elif(plan[5]==0):
                Information.configure(fg_color = 'red')
                
            Information.pack(padx=10, pady = 10,expand=True, fill='x')
            plans_list.append(plan_frame)


        inner_frame.update_idletasks()
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        def on_canvas_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_canvas_configure)

        return plans_list
    else:
        return None
    
def display_plan_detail(plan_id):
    detail_window = customtkinter.CTk()
    detail_window.geometry("500x350")
    detail_window.title('Chi tiết kế hoạch')
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM PLANS WHERE PlanID = ?'
    cursor.execute(query, plan_id)
    plan_data = cursor.fetchone()

    StartDateLabel = customtkinter.CTkLabel(detail_window, text='Ngày bắt đầu: ', font=('Time New Roman', 15))
    StartDateLabel.place(x=100, y=50)
    startday, startmonth, startyear = (
                plan_data[2].day if plan_data[2] else "",
                plan_data[2].month if plan_data[2] else "",
                plan_data[2].year if plan_data[2] else "",
            )

    startday_var = StringVar(value=str(startday))
    startmonth_var = StringVar(value=str(startmonth))
    startyear_var = StringVar(value=str(startyear))

    startday_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=startday_var)
    startday_entry.place(x=200, y=50)
    startday_entry.insert(0, startday_var.get())

    separator_label_11 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_11.place(x=230, y=50)

    startmonth_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=startmonth_var)
    startmonth_entry.place(x=240, y=50)
    startmonth_entry.insert(0, startmonth_var.get())

    separator_label_12 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_12.place(x=270, y=50)

    startyear_entry = customtkinter.CTkEntry(detail_window, width=45, textvariable=startyear_var)
    startyear_entry.place(x=280, y=50)
    startyear_entry.insert(0, startyear_var.get())

    EndDateLabel = customtkinter.CTkLabel(detail_window, text='Ngày kết thúc: ', font=('Time New Roman', 15))
    EndDateLabel.place(x=100, y=80)
    endday, endmonth, endyear = (
                plan_data[3].day if plan_data[3] else "",
                plan_data[3].month if plan_data[3] else "",
                plan_data[3].year if plan_data[3] else "",
    )

    endday_var = StringVar(value=str(endday))
    endmonth_var = StringVar(value=str(endmonth))
    endyear_var = StringVar(value=str(endyear))

    endday_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=endday_var)
    endday_entry.place(x=200, y=80)
    endday_entry.insert(0, endday_var.get())

    separator_label_21 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_21.place(x=230, y=80)

    endmonth_entry = customtkinter.CTkEntry(detail_window, width=30, textvariable=endmonth_var)
    endmonth_entry.place(x=240, y=80)
    endmonth_entry.insert(0, endmonth_var.get())

    separator_label_22 = customtkinter.CTkLabel(detail_window, text="/")
    separator_label_22.place(x=270, y=80)

    endyear_entry = customtkinter.CTkEntry(detail_window, width=45, textvariable=endyear_var)
    endyear_entry.place(x=280, y=80)
    endyear_entry.insert(0, endyear_var.get())

    NameLabel = customtkinter.CTkLabel(detail_window, text='Tên kế hoạch: ', font=('Time New Roman', 15))
    NameLabel.place(x=100, y=110)
    Name_entry = customtkinter.CTkEntry(detail_window, width=100)
    Name_entry.place(x=200, y=110)
    Name_entry.insert(0, plan_data[1])

    BudgetLabel = customtkinter.CTkLabel(detail_window, text='Ngân sách: ', font=('Time New Roman', 15))
    BudgetLabel.place(x=100, y=140)
    Budget_entry = customtkinter.CTkEntry(detail_window, width=100)
    Budget_entry.place(x=200, y=140)
    Budget_entry.insert(0, str(plan_data[4]))

    RemainLabel = customtkinter.CTkLabel(detail_window, text='Tiền còn lại: ', font=('Time New Roman', 15))
    RemainLabel.place(x=100, y=170)
    Amount_label = customtkinter.CTkLabel(detail_window, text=f'{plan_data[5]}đ', font=('Time New Roman', 15))
    Amount_label.place(x=200, y=170)

    CloseButton = customtkinter.CTkButton(detail_window, width=50, text = "Đóng", command =  lambda: detail_window.destroy())
    CloseButton.place(x=100, y=200)

    UpdateButton = customtkinter.CTkButton(detail_window, width=50, text="Cập nhật", command=lambda: (
        update_plan(
            plan_id,
            Name_entry.get(),
            startday_entry.get(),
            startmonth_entry.get(),
            startyear_entry.get(),
            endday_entry.get(),
            endmonth_entry.get(),
            endyear_entry.get(),
            int(Budget_entry.get()),
            plan_data[6],
            detail_window
        )
    ))

    UpdateButton.place(x=160, y=200)
    DeleteButton = customtkinter.CTkButton(detail_window, width=50, text="Xóa", command=lambda: delete_plan(plan_id, detail_window, plan_data[6]))
    DeleteButton.place(x=230, y=200)
    TransactionButton = customtkinter.CTkButton(detail_window, width=100, text = "Các khoản giao dịch", command=lambda: display_transaction_plan(plan_id, plan_data[6]))
    TransactionButton.place(x=100,y=230) 

    detail_window.mainloop()
    return detail_window

def update_plan(plan_id, name, startday, startmonth, startyear, endday, endmonth, endyear, budget, userid, detail_window):
    try:
        if startday and startmonth and startyear:
            startday, startmonth, startyear = int(startday) if startday else None, int(startmonth) if startmonth else None, int(startyear) if startyear else None

            if startday and (startday < 1 or startday > 31 or (startday > 29 and startmonth == 2) or
                        (startday > 30 and startmonth in [4, 6, 9, 11]) or
                        (startday > 31 and startmonth in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày bắt đầu không hợp lệ.')
                return

            if startmonth and (startmonth < 1 or startmonth > 12):
                messagebox.showerror('Error', 'Tháng bắt đầu không hợp lệ.')
                return

            if startyear and (startyear < 1900 or startyear > 2100):
                messagebox.showerror('Error', 'Năm bắt đầu không hợp lệ.')
                return

            startdate = datetime(startyear, startmonth, startday) 
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm bắt đầu')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày bắt đầu không hợp lệ.')
        return
    
    try:
        if endday and endmonth and endyear:
            endday, endmonth, endyear = int(endday) if endday else None, int(endmonth) if endmonth else None, int(endyear) if endyear else None

            if endday and (endday < 1 or endday > 31 or (endday > 29 and endmonth == 2) or
                        (endday > 30 and endmonth in [4, 6, 9, 11]) or
                        (endday > 31 and endmonth in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày kết thúc không hợp lệ.')
                return

            if endmonth and (endmonth < 1 or endmonth > 12):
                messagebox.showerror('Error', 'Tháng kết thúc không hợp lệ.')
                return

            if endyear and (endyear < 1900 or endyear > 2100):
                messagebox.showerror('Error', 'Năm kết thúc không hợp lệ.')
                return

            enddate = datetime(endyear, endmonth, endday) 
            if (enddate < startdate):
                messagebox.showerror('Error', 'Ngày kết thúc không được ở trước ngày bắt đầu.')
                return
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm kết thúc')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày kết thúc không hợp lệ.')
        return
    
    if(budget == None):
        messagebox.showerror('Error', 'Vui lòng nhập ngân sách.')
        return
    
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            if(len(name)==0):
                messagebox.showerror('Error', 'Vui lòng nhập tên.')
                return
            update_query = 'UPDATE PLANS SET Tenkehoach=?, Ngaybatdau=?, Ngayketthuc=?, Ngansach=? WHERE PlanID=?'
            print("Values:", name, startdate, enddate, budget, plan_id)
            try:
                cursor.execute(update_query, name, startdate, enddate, budget, plan_id)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Cập nhật thông tin thành công!')
                calculate_remain(plan_id)
                detail_window.destroy()
                home_window.destroy()
                home_page(userid) 
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật thông tin thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')

def add_plans(user_id):
    add_window = customtkinter.CTk()
    add_window.geometry("400x250")
    add_window.title('Thêm kế hoạch')
    connection, cursor = connect_to_database()

    StartDateLabel = customtkinter.CTkLabel(add_window, text='Ngày bắt đầu: ', font=('Time New Roman', 15))
    StartDateLabel.place(x=100, y=50)

    startday_entry = customtkinter.CTkEntry(add_window, width=30)
    startday_entry.place(x=200, y=50)

    separator_label_11 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_11.place(x=230, y=50)

    startmonth_entry = customtkinter.CTkEntry(add_window, width=30)
    startmonth_entry.place(x=240, y=50)

    separator_label_12 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_12.place(x=270, y=50)

    startyear_entry = customtkinter.CTkEntry(add_window, width=45)
    startyear_entry.place(x=280, y=50)

    EndDateLabel = customtkinter.CTkLabel(add_window, text='Ngày kết thúc: ', font=('Time New Roman', 15))
    EndDateLabel.place(x=100, y=80)

    endday_entry = customtkinter.CTkEntry(add_window, width=30)
    endday_entry.place(x=200, y=80)

    separator_label_21 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_21.place(x=230, y=80)

    endmonth_entry = customtkinter.CTkEntry(add_window, width=30)
    endmonth_entry.place(x=240, y=80)

    separator_label_22 = customtkinter.CTkLabel(add_window, text="/")
    separator_label_22.place(x=270, y=80)

    endyear_entry = customtkinter.CTkEntry(add_window, width=45)
    endyear_entry.place(x=280, y=80)

    NameLabel = customtkinter.CTkLabel(add_window, text='Tên kế hoạch: ', font=('Time New Roman', 15))
    NameLabel.place(x=100, y=110)
    Name_entry = customtkinter.CTkEntry(add_window, width=100)
    Name_entry.place(x=200, y=110)

    BudgetLabel = customtkinter.CTkLabel(add_window, text='Ngân sách: ', font=('Time New Roman', 15))
    BudgetLabel.place(x=100, y=140)
    Budget_entry = customtkinter.CTkEntry(add_window, width=100)
    Budget_entry.place(x=200, y=140)

    query = 'SELECT PlanID FROM PLANS'
    cursor.execute(query)
    results=cursor.fetchall()
    plan_id = 300001
    existing_plan_ids = [result[0] for result in results]
    while plan_id in existing_plan_ids:
        plan_id+=1

    ConfirmButton = customtkinter.CTkButton(add_window, width=50, text="Xác nhận", command=lambda: (
        add_plan_todtb(
            plan_id,
            Name_entry.get(),
            startday_entry.get(),
            startmonth_entry.get(),
            startyear_entry.get(),
            endday_entry.get(),
            endmonth_entry.get(),
            endyear_entry.get(),
            int(Budget_entry.get()),
            user_id,
            add_window
        )
    ))

    ConfirmButton.place(x=100, y=170)
                                           
    add_window.mainloop()
    return add_window

def add_plan_todtb(plan_id, name, startday, startmonth, startyear, endday, endmonth, endyear, budget, userid, add_window):
    try:
        if startday and startmonth and startyear:
            startday, startmonth, startyear = int(startday) if startday else None, int(startmonth) if startmonth else None, int(startyear) if startyear else None

            if startday and (startday < 1 or startday > 31 or (startday > 29 and startmonth == 2) or
                        (startday > 30 and startmonth in [4, 6, 9, 11]) or
                        (startday > 31 and startmonth in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày bắt đầu không hợp lệ.')
                return

            if startmonth and (startmonth < 1 or startmonth > 12):
                messagebox.showerror('Error', 'Tháng bắt đầu không hợp lệ.')
                return

            if startyear and (startyear < 1900 or startyear > 2100):
                messagebox.showerror('Error', 'Năm bắt đầu không hợp lệ.')
                return

            startdate = datetime(startyear, startmonth, startday) 
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm bắt đầu')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày bắt đầu không hợp lệ.')
        return
    
    try:
        if endday and endmonth and endyear:
            endday, endmonth, endyear = int(endday) if endday else None, int(endmonth) if endmonth else None, int(endyear) if endyear else None

            if endday and (endday < 1 or endday > 31 or (endday > 29 and endmonth == 2) or
                        (endday > 30 and endmonth in [4, 6, 9, 11]) or
                        (endday > 31 and endmonth in [1, 3, 5, 7, 8, 10, 12])):
                messagebox.showerror('Error', 'Ngày kết thúc không hợp lệ.')
                return

            if endmonth and (endmonth < 1 or endmonth > 12):
                messagebox.showerror('Error', 'Tháng kết thúc không hợp lệ.')
                return

            if endyear and (endyear < 1900 or endyear > 2100):
                messagebox.showerror('Error', 'Năm kết thúc không hợp lệ.')
                return

            enddate = datetime(endyear, endmonth, endday) 
            if (enddate < startdate):
                messagebox.showerror('Error', 'Ngày kết thúc không được ở trước ngày bắt đầu.')
                return
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm kết thúc')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày kết thúc không hợp lệ.')
        return
    
    if(budget == None):
        messagebox.showerror('Error', 'Vui lòng nhập ngân sách.')
        return
    
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            if(len(name)==0):
                messagebox.showerror('Error', 'Vui lòng nhập tên.')
                return
            update_query = 'INSERT INTO PLANS(PlanID, Tenkehoach, Ngaybatdau, Ngayketthuc, Ngansach, Tiencon, UserID) Values (?, ?, ?, ?, ?, ?, ?)'
            print(plan_id, name, startdate, enddate, budget, budget, userid)
            try:
                cursor.execute(update_query,plan_id, name, startdate, enddate, budget, budget, userid)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Thêm kế hoạch thành công!')
                add_window.destroy()
                home_window.destroy()
                home_page(userid) 
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Thêm kế hoạch thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Thêm kế hoạch thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')

def delete_plan(plan_id, detail_window, user_id):
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            update_query2 = 'DELETE FROM PLANS WHERE PlanID=?'
            update_query1 = 'DELETE FROM TRANSACTIONS_PLANS WHERE PlanID=?'
            print("Values:", plan_id)
            try:
                cursor.execute(update_query1, plan_id)
                connection.commit()
                cursor.execute(update_query2, plan_id)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Xóa kế hoạch thành công!')
                detail_window.destroy()
                home_window.destroy()
                home_page(user_id) 
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Xóa kế hoạch thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Xóa kế hoạch thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.') 

def display_transaction_plan(plan_id, user_id):
    frame=customtkinter.CTk()
    frame.geometry("800x600")
    frame.title("Chi tiết các khoản giao dịch")
    customtkinter.CTkLabel(frame, text="Ấn vào giao dịch để xóa liên kết", font=('Time New Roman', 16)).pack(side='bottom', pady=5)
    connection, cursor = connect_to_database()
    query = 'SELECT PlanID, TRANSACTIONS.TransactionID, Ngay, CategoryID, Sotien FROM TRANSACTIONS_PLANS, TRANSACTIONS WHERE TRANSACTIONS.TransactionID = TRANSACTIONS_PLANS.TransactionID AND PlanID = ?'
    cursor.execute(query, plan_id)
    transactions_data = cursor.fetchall()
    if transactions_data:
        transactions_list = []

        for i, transaction in enumerate(transactions_data):
            transaction_id = transaction[1]
            transaction_frame = customtkinter.CTkFrame(frame, fg_color='transparent')

            query = 'SELECT Tenhangmuc FROM CATEGORIES WHERE CategoryID=?'
            cursor.execute(query, transaction[3])
            CategoryName = cursor.fetchone()[0]
            text = f'{transaction[2].day}/{transaction[2].month}/{transaction[2].year} - {CategoryName} - {transaction[4]}'

            Information = customtkinter.CTkButton(transaction_frame, text=text, anchor='w', fg_color="red", width=600, font=('Time New Roman', 15), command=lambda id=transaction_id: delete_plan_transaction(plan_id, id, frame))
            Information.pack(padx=10, pady = 10,expand=True, fill='x')
            transactions_list.append(transaction_frame)

        for transaction in transactions_list:
            transaction.pack()

    else:
        customtkinter.CTkLabel(frame, text="Không có liên kết với giao dịch nào.", font=('Time New Roman', 30)).pack(padx=10, pady=10)
    
    frame.mainloop()

def calculate_remain(plan_id):
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            query = 'SELECT Ngansach FROM PLANS WHERE PlanID=?'
            cursor.execute(query,plan_id)
            result = cursor.fetchone()
            initial = result[0] if result[0] else 0

            query = 'SELECT SUM(Sotien) FROM TRANSACTIONS, TRANSACTIONS_PLANS WHERE TRANSACTIONS.TransactionID=TRANSACTIONS_PLANS.TransactionID AND PlanID=?'
            cursor.execute(query, plan_id)
            result = cursor.fetchone()
            Amount = result[0] if result[0] else 0   

            query = 'UPDATE PLANS SET Tiencon = ? WHERE PlanID=?'
            print(Amount, plan_id)
            try:
                cursor.execute(query, initial - Amount, plan_id)
                connection.commit()
                print("Update Remain Successful")
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Cập nhật tiền còn thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Cập nhật tiền còn thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.') 


#Function for tab_4
########################################################################################################### 
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def plot_pie_graph(frame, user_id, startdate, enddate):
    Amount, Earn, Spend, Borrow, Owe = calculate_balance_period(user_id, startdate - timedelta(days=1), enddate)
    labels = ['Thu', 'Chi', 'Vay', 'Nợ']
    sum_values = Earn + Spend + Borrow + Owe
    if(sum_values == 0):
        Label = CTkLabel(frame, text = 'Chưa có dữ liệu', font = ('Time New Roman', 15))
        Label.pack()
        return Label, Label, Label
    sizes = [float(Earn/sum_values), float(Spend/sum_values), float(Borrow/sum_values), float(Owe/sum_values)]

    fig, ax = plt.subplots(figsize=(5, 3))
    legends = ['','','','']
    for i in range (0,4):
        legends[i] = labels[i] + ': ' + str("{:.1f}".format(sizes[i]*100)) + '%'

    ax.axis('equal')  
    ax.set_title(f'Tỉ lệ các mục ({(startdate).day}/{(startdate).month}/{(startdate.year)} - {(enddate).day}/{(enddate).month}/{(enddate.year)})', pad=5)
    wedges, text_labels = ax.pie(sizes, labels=None, startangle=90)

    # Move labels and percentages below the pie chart
    plt.legend(wedges, legends, title="Tỉ lệ", loc="center left", bbox_to_anchor=(0.75, 0.5))
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(x=-60, rely=0)

    frame.update_idletasks()
    return canvas, canvas_widget, fig

def plot_bar_graph_week(frame, user_id):
    labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    today = datetime.now()
    days_to_monday = today.weekday()
    monday_date = today - timedelta(days=days_to_monday)
    sunday_date = monday_date + timedelta(days=6)
    values = [0,0,0,0,0,0,0]
    for i in range (0,7):
        values[i] = calculate_balance_period(user_id, monday_date + timedelta(days=i-1), monday_date + timedelta(days=i))[0]
        print (values[i])
    fig, ax = plt.subplots(figsize=(4.9,2.5))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    ax.axhline(0, color='black', linestyle='dashed', linewidth=1)
    ax.set_ylabel('Tổng thay đổi số dư', fontsize=8)
    ax.set_title(f'Thay đổi số dư tuần {(monday_date).day}/{(monday_date).month}/{(monday_date.year)} - {(sunday_date).day}/{(sunday_date).month}/{(sunday_date.year)}')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()
    total_sum = sum(values)
    total_average = total_sum / len(values)
    canvas_widget.place(relx=0, rely=0)

    return canvas, canvas_widget, fig, total_sum, total_average

def plot_bar_graph_reweek(frame, user_id):
    labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
    today = datetime.now()
    days_to_monday = today.weekday()
    monday_date = today - timedelta(days=days_to_monday)
    sunday_date = monday_date + timedelta(days=6)
    values = [0,0,0,0,0,0,0]
    for i in range (0,7):
        values[i] = calculate_balance_period(user_id, monday_date + timedelta(days=i-1), monday_date + timedelta(days=i))[0]
    fig, ax = plt.subplots(figsize=(4.9,2.5))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    ax.axhline(0, color='black', linestyle='dashed', linewidth=1)
    ax.set_ylabel('Tổng thay đổi số dư', fontsize=8)
    ax.set_title(f'Thay đổi số dư tuần {(monday_date).day}/{(monday_date).month}/{(monday_date.year)} - {(sunday_date).day}/{(sunday_date).month}/{(sunday_date.year)}')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()

    total_sum = sum(values)
    total_average = total_sum / len(values)
    canvas_widget.pack(fill='both', expand=1)

    return canvas, canvas_widget, fig, total_sum, total_average

def plot_bar_graph_month(frame, user_id):
    labels = []
    values = []
    today = datetime.now()
    month = today.month
    year = today.year
    if(month == 2) and (year % 4 ==0): 
        max_day = 29
    elif(month == 2) and (year % 4 !=0):
        max_day = 28
    elif(month == 4) or (month==6) or (month==9) or (month==11):
        max_day = 30
    else:
        max_day = 31
    for i in range (1,max_day+1):
        labels.append(str(i))
        values.append(0)
    days_to_first = today.day
    first_day = today - timedelta(days = days_to_first - 1)
    last_day = first_day + timedelta(days = max_day - 1)
    for i in range (0, max_day):
        values[i] = calculate_balance_period(user_id, first_day + timedelta(days=i-1), first_day + timedelta(days=i))[0]
    fig, ax = plt.subplots(figsize=(4.9,2.5))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    ax.axhline(0, color='black', linestyle='dashed', linewidth=1)
    ax.set_xlabel('Ngày')
    ax.set_ylabel('Tổng thay đổi số dư', fontsize=8)
    ax.set_title(f'Thay đổi số dư tháng {month}/{year}', pad=10)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()

    total_sum = sum(values)
    total_average = total_sum / len(values)
    canvas_widget.pack(fill='both', expand=1)

    return canvas, canvas_widget, fig, total_sum, total_average

def plot_bar_graph_year(frame, user_id):
    labels = []
    values = []
    today = datetime.now()
    month = today.month
    year = today.year
    for i in range (1,13):
        labels.append('T' + str(i))
        values.append(0)

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    first_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1) if (start_date + timedelta(days=x)).day == 1]
    first_dates.append(end_date + timedelta(days=1))
    for i in range (0, 12):
        values[i] = calculate_balance_period(user_id, first_dates[i] - timedelta(days=1), first_dates[i+1] - timedelta(days=1))[0]

    fig, ax = plt.subplots(figsize=(4.9,2.5))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    ax.axhline(0, color='black', linestyle='dashed', linewidth=1)
    ax.set_xlabel('Tháng')
    ax.set_ylabel('Tổng thay đổi số dư', fontsize=8)
    ax.set_title(f'Thay đổi số dư năm {year}',pad=10)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()

    total_sum = sum(values)
    total_average = total_sum / len(values)
    canvas_widget.pack(fill='both', expand=1)

    return canvas, canvas_widget, fig, total_sum, total_average

def plot_bar_graph_10_year(frame, user_id):
    labels = []
    values = []
    today = datetime.now()
    year = today.year
    for i in range (0,10):
        labels.append(str(year - 9 + i))
        values.append(0)
    
    first_dates=[]
    for i in range (0,10):
        first_dates.append(datetime(int(labels[i]), 1, 1))
    first_dates.append(datetime(year + 1, 1, 1))

    for i in range (0, 10):
        values[i] = calculate_balance_period(user_id, first_dates[i] - timedelta(days=1), first_dates[i+1] - timedelta(days=1))[0]

    fig, ax = plt.subplots(figsize=(4.9,2.5))
    bars = ax.bar(labels, values)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.0f}', ha='center', va='bottom' if height >= 0 else 'top')
    ax.axhline(0, color='black', linestyle='dashed', linewidth=1)
    ax.set_xlabel('Tháng')
    ax.set_ylabel('Tổng thay đổi số dư', fontsize=8)
    ax.set_title(f'Thay đổi số dư giai đoạn {year-9} - {year}',pad=10)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas_widget = canvas.get_tk_widget()

    total_sum = sum(values)
    total_average = total_sum / len(values)
    canvas_widget.pack(fill='both', expand=1)

    return canvas, canvas_widget, fig, total_sum, total_average

def display_reports_earning_spending(frame, user_id):
    Earn, Spend, Borrow, Owe = calculate_balance(user_id)
    customtkinter.CTkLabel(frame, text = 'Tình hình thu chi: ', font=('Time New Roman', 20, 'bold')).pack()
    if ((Earn == 0) and (Spend == 0) and (Borrow == 0) and (Owe == 0)):
        customtkinter.CTkLabel(frame, text = 'Chưa có dữ liệu', font=('Time New Roman',15)).pack(fill='both', expand=True)
    else:
        pie_chart = customtkinter.CTkFrame(frame, fg_color="transparent", width=500, height=240)
        pie_chart.pack(pady=5)
        pie_chart.pack_propagate(False)
        today = datetime.now()
        days_to_monday = today.weekday()
        monday_date = today - timedelta(days=days_to_monday)
        sunday_date = monday_date + timedelta(days=6)
        plot_pie_graph(pie_chart, user_id, monday_date, sunday_date)
        detail_button1 = customtkinter.CTkButton(pie_chart, text = 'Chi tiết', command=lambda: display_report_detail(user_id))
        detail_button1.pack(side='bottom', pady=5)

        bar_chart = customtkinter.CTkFrame(frame, fg_color="transparent", width=600, height=240)
        bar_chart.pack(pady=5)
        bar_chart.pack_propagate(False)
        plot_bar_graph_week(bar_chart, user_id)
    
def display_reports_borrowing_owing(frame, user_id):
    Earn, Spend, Borrow, Owe = calculate_balance(user_id)
    customtkinter.CTkLabel(frame, text = "Tổng vay người khác: " + str(Borrow) + 'đ', font=('Time New Roman', 15)).place(relx=0.05, rely=0.9)
    customtkinter.CTkLabel(frame, text = "Tổng người khác nợ: " + str(Owe) + 'đ', font=('Time New Roman', 15)).place(relx=0.05, rely=0.95)
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM TRANSACTIONS WHERE UserID = ? AND CategoryID > 420000 ORDER BY Ngay DESC'
    cursor.execute(query, user_id)
    transactions_data = cursor.fetchall()

    if transactions_data:
        transactions_list = []

        for i, transaction in enumerate(transactions_data):
            transaction_id = transaction[0]
            transaction_frame = customtkinter.CTkFrame(frame, fg_color='transparent')

            query = 'SELECT Tenhangmuc FROM CATEGORIES WHERE CategoryID = ?'
            cursor.execute(query, transaction[4])
            Tenhangmuc = cursor.fetchone()[0]
            text = f'{transaction[2].day}/{transaction[2].month}/{transaction[2].year} - {Tenhangmuc} - {transaction[6]}\nSố tiền: {transaction[1]}đ'

            Information = customtkinter.CTkButton(transaction_frame, text=text, anchor='nw', width=220, font=('Time New Roman', 15), command=lambda id=transaction_id: delete_transaction(id, frame, user_id))
            Information.pack(padx=5, pady=5, expand=True, fill='x')
            if (transaction[4] > 420000 and transaction[4] < 430000):
                Information.configure(fg_color = 'red')
            transactions_list.append(transaction_frame)


        return transactions_list
    else:
        return None

def display_report_detail(user_id):
    report_detail_window = customtkinter.CTk(fg_color='white')
    report_detail_window.geometry("800x600")
    report_detail_window.title("Báo cáo chi tiêu")
    
    button_frame = customtkinter.CTkFrame(report_detail_window, fg_color='transparent', height = 30)
    button_frame.pack(pady=10)
    view_button = customtkinter.CTkButton(button_frame, text='Xem', command = lambda: change_display(graph_frame1, graph_frame2, user_id, view_dropdown.get()))
    view_button.pack(side = 'left', padx=10)
    view_options = ['Trong tuần', 'Trong tháng', 'Trong năm', '10 năm gần nhất']
    view_dropdown = customtkinter.CTkComboBox(button_frame, width=120, values=view_options, state="readonly")
    view_dropdown.set('Trong tuần')
    view_dropdown.pack(side = 'left', padx=10)

    graph_frame1 = customtkinter.CTkFrame(report_detail_window, fg_color='white')
    graph_frame1.pack(pady=10, padx=10, expand=True, fill='both')

    graph_frame2 = customtkinter.CTkFrame(report_detail_window, fg_color='white')
    graph_frame2.pack(pady=50, padx=200, expand=True, fill='both')

    today = datetime.now()
    days_to_monday = today.weekday()
    monday_date = today - timedelta(days=days_to_monday)
    sunday_date = monday_date + timedelta(days=6)

    bar_canvas, bar_graph, bar_fig, total_sum, total_average = plot_bar_graph_week(graph_frame1, user_id)
    pie_canvas, pie_graph, pie_fig = plot_pie_graph(graph_frame2, user_id, monday_date, sunday_date)

    label = customtkinter.CTkLabel(graph_frame1, text=f'Tổng:  {str(total_sum)}đ \nTrung bình mỗi ngày: {str("{:.0f}".format(total_average))}đ', fg_color='white')
    
    bar_graph.pack(fill='both', expand=True)
    pie_graph.pack(fill='both', expand=True)
    label.pack(pady=5)

    report_detail_window.mainloop()

def change_display(frame1, frame2, user_id, view):
    clear_frame(frame1)
    clear_frame(frame2)
    if(view == 'Trong tuần'):
        today = datetime.now()
        days_to_monday = today.weekday()
        monday_date = today - timedelta(days=days_to_monday)
        sunday_date = monday_date + timedelta(days=6)
        pie_canvas, pie_graph, pie_fig = plot_pie_graph(frame2, user_id, monday_date, sunday_date)
        bar_canvas, bar_graph, bar_fig, total_sum, total_average = plot_bar_graph_reweek(frame1, user_id)
        pie_graph.pack(fill='both', expand=True)
        label = customtkinter.CTkLabel(frame1, text=f'Tổng:  {str(total_sum)}đ \nTrung bình mỗi ngày: {str("{:.0f}".format(total_average))}đ', fg_color='white')
        label.pack(pady=5)

    elif(view == 'Trong tháng'):
        today = datetime.now()
        month = today.month
        year = today.year
        if(month == 2) and (year % 4 ==0): 
            max_day = 29
        elif(month == 2) and (year % 4 !=0):
            max_day = 28
        elif(month == 4) or (month==6) or (month==9) or (month==11):
            max_day = 30
        else:
            max_day = 31
        days_to_first = today.day
        first_day = today - timedelta(days = days_to_first - 1)
        last_day = first_day + timedelta(days = max_day - 1)
        pie_canvas, pie_graph, pie_fig = plot_pie_graph(frame2, user_id, first_day, last_day)
        bar_canvas, bar_graph, bar_fig, total_sum, total_average = plot_bar_graph_month(frame1, user_id)
        pie_graph.pack(fill='both', expand=True)
        label = customtkinter.CTkLabel(frame1, text=f'Tổng:  {str(total_sum)}đ \nTrung bình mỗi ngày: {str("{:.0f}".format(total_average))}đ', fg_color='white')
        label.pack(pady=5)

    elif(view == 'Trong năm'):
        today = datetime.now()
        year = today.year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        pie_canvas, pie_graph, pie_fig = plot_pie_graph(frame2, user_id, start_date, end_date)
        bar_canvas, bar_graph, bar_fig, total_sum, total_average = plot_bar_graph_year(frame1, user_id)
        pie_graph.pack(fill='both', expand=True)
        label = customtkinter.CTkLabel(frame1, text=f'Tổng:  {str(total_sum)}đ \nTrung bình mỗi tháng: {str("{:.0f}".format(total_average))}đ', fg_color='white')
        label.pack(pady=5)

    elif(view == '10 năm gần nhất'):
        today = datetime.now()
        year = today.year
        start_date = datetime(year-9, 1, 1)
        end_date = datetime(year, 12, 31)
        pie_canvas, pie_graph, pie_fig = plot_pie_graph(frame2, user_id, start_date, end_date)
        bar_canvas, bar_graph, bar_fig, total_sum, total_average = plot_bar_graph_10_year(frame1, user_id)
        pie_graph.pack(fill='both', expand=True)
        label = customtkinter.CTkLabel(frame1, text=f'Tổng:  {str(total_sum)}đ \nTrung bình mỗi năm: {str("{:.0f}".format(total_average))}đ', fg_color='white')
        label.pack(pady=5)

#Function for tab5
########################################################################################################### 
def display_notifications(frame, user_id):
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM NOTIFICATIONS WHERE UserID = ? ORDER BY Ngaygui DESC'
    cursor.execute(query, user_id)
    notifications_data = cursor.fetchall()
    if notifications_data:
        canvas_width = 800
        canvas_height = 600

        canvas = customtkinter.CTkCanvas(frame, width=canvas_width, height=canvas_height)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = customtkinter.CTkFrame(canvas, bg_color='black', fg_color='transparent', width=800)
        inner_frame.pack(fill='both', expand=True)

        notifications_list = []

        for i, notification in enumerate(notifications_data):
            notification_frame = customtkinter.CTkFrame(inner_frame, fg_color='transparent', width=800)
            
            text = f'{notification[2].day}/{notification[2].month}/{notification[2].year}\n{notification[1]}'

            Information = customtkinter.CTkLabel(notification_frame, text=text, anchor='w', justify = 'left', width=800, font=('Time New Roman', 15), fg_color = 'light green')
            Information.pack(padx=5, pady = 5,expand=True, fill='x')
            notifications_list.append(notification_frame)


        inner_frame.update_idletasks()
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        def on_canvas_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_canvas_configure)

        return notifications_list
    else:
        return None

    
#Function for home
########################################################################################################### 
def home_page(user_id):
    global home_window
    home_window = customtkinter.CTk()
    home_window.geometry("800x600")
    home_window.title('Home Page')

    connection, cursor = connect_to_database()

    if connection and cursor:
        tabview = customtkinter.CTkTabview(home_window)
        tabview.pack(fill=customtkinter.BOTH, expand=True, padx=20, pady=20)
        set_to_unlocked(user_id)

        tabview.add("Thông tin cá nhân")
        tabview.add("Giao dịch")
        tabview.add("Kế hoạch chi tiêu")
        tabview.add("Báo cáo")
        tabview.add("Thông báo")

        tabview.set("Thông tin cá nhân")
        calculate_balance(user_id)
        user_data = fetch_user_data(cursor, user_id)

        #tab-1
        if user_data:
            frame = customtkinter.CTkFrame(tabview.tab("Thông tin cá nhân"))
            display_user_info(frame, user_data)
        else:
            print("User data not found") 
        
        update_button = customtkinter.CTkButton(tabview.tab("Thông tin cá nhân"), text='Thay đổi thông tin', command=lambda: update(user_id))
        update_button.pack(padx=20, pady=20)

        logout_button = customtkinter.CTkButton(tabview.tab("Thông tin cá nhân"), text='Đăng xuất', command=logout)
        logout_button.pack(padx=20, pady=20)

        #tab-2
        frame2 = customtkinter.CTkFrame(tabview.tab("Giao dịch"))
        frame2.pack()
        transaction_frames = display_transactions_info(frame2, user_id)
        if transaction_frames:
            for transaction_frame in transaction_frames:
                transaction_frame.pack()
        else:
            customtkinter.CTkLabel(frame2, text="Không có dữ liệu giao dịch.", font=('Time New Roman', 30)).pack()
        AddButton = customtkinter.CTkButton(tabview.tab("Giao dịch"), width=100, text='Thêm giao dịch', command=lambda: add_transactions(user_id))
        AddButton.pack(side='bottom',pady=10)

        #tab-3
        frame3 = customtkinter.CTkFrame(tabview.tab("Kế hoạch chi tiêu"))
        frame3.pack()
        plan_frames = display_plans_info(frame3, user_id)
        if plan_frames:
            for plan_frame in plan_frames:
                plan_frame.pack()
        else:
            customtkinter.CTkLabel(frame3, text="Không có kế hoạch.", font=('Time New Roman', 30)).pack()
        RefreshButton = AddPlanButton = customtkinter.CTkButton(tabview.tab("Kế hoạch chi tiêu"), width=100, text='Refresh', command=lambda: (home_window.destroy(), home_page(user_id), tabview.set("Kế hoạch chi tiêu")))
        RefreshButton.pack(side='bottom',pady=10)
        AddPlanButton = customtkinter.CTkButton(tabview.tab("Kế hoạch chi tiêu"), width=100, text='Thêm kế hoạch', command=lambda: add_plans(user_id))
        AddPlanButton.pack(side='bottom',pady=10)

        #tab-4
        frame4 = customtkinter.CTkFrame(tabview.tab("Báo cáo"), fg_color="white", width=360, height=500)
        frame4.place(relx=0, rely=0)
        frame4.pack_propagate(False)
        display_reports_earning_spending(frame4, user_id)

        frame5 = customtkinter.CTkFrame(tabview.tab("Báo cáo"), fg_color="white", width=360, height=500)
        frame5.place(relx=0.51,rely=0)
        frame5.pack_propagate(False)
        Section2Label=customtkinter.CTkLabel(frame5, text='Khoản vay nợ: ', font=('Time New Roman', 20, 'bold'))
        Section2Label.pack()

        display_reports_borrowing_owing(frame5, user_id)
        borrowing_owing_frames = display_reports_borrowing_owing(frame5, user_id)
        if borrowing_owing_frames:
            for borrowing_owing_frames in borrowing_owing_frames:
                borrowing_owing_frames.pack()
        else:
            customtkinter.CTkLabel(frame5, text="Không có dữ liệu khoản vay nợ.", font=('Time New Roman', 15)).pack()

        #tab-5
        frame6 = customtkinter.CTkFrame(tabview.tab("Thông báo"))
        frame6.pack()
        notification_frames = display_notifications(frame6, user_id)
        if notification_frames:
            for notification_frame in notification_frames:
                notification_frame.pack()
        else:
            customtkinter.CTkLabel(frame6, text="Không có thông báo.", font=('Time New Roman', 30)).pack()
        home_window.mainloop()


if __name__ == "__main__":
    home_page(110001)