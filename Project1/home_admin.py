import customtkinter
from tkinter import messagebox, Checkbutton, IntVar
import pyodbc
from datetime import datetime, timedelta
from customtkinter import CTkLabel
import tkinter as tk
from tkinter import ttk
from tkinter import StringVar, Scrollbar


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")
home_window_admin=None

def logout():
    home_window_admin.destroy()
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

#function for tab_1
################################################################################################
def fetch_user_data(cursor, user_id):
    query = 'SELECT * FROM ACCOUNTS WHERE UserID=?'
    cursor.execute(query, user_id)
    return cursor.fetchone()

def display_user_info(frame, user_data):
    frame.pack()

    font_size = 20 

    name_label = customtkinter.CTkLabel(frame, text="Tên: " + str(user_data[1]), font=('Time New Roman', font_size))
    name_label.pack(pady=20)

    email_label = customtkinter.CTkLabel(frame, text="Email: " + str(user_data[4]), font=('Time New Roman', font_size))
    email_label.pack(pady=20)

#function for tab_2
##############################################################################################
def display_users_list(frame, userid):
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM ACCOUNTS ORDER BY UserID'
    cursor.execute(query)
    users_data = cursor.fetchall()
    if users_data:
        canvas_width = 610 
        canvas_height = 500

        canvas = customtkinter.CTkCanvas(frame, width=canvas_width, height=canvas_height)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = customtkinter.CTkFrame(canvas, bg_color='transparent')
        inner_frame.pack(fill='both', expand=True)

        users_list = []

        for i, user in enumerate(users_data):
            user_id = user[0]
            user_frame = customtkinter.CTkFrame(inner_frame, fg_color='transparent')

            if(user[6] == True):
                text = f'AdminID: {user[0]} - Tên: {user[1]} - Email: {user[4]}'

                Information = customtkinter.CTkButton(user_frame, text=text, anchor='w', width=600, fg_color='teal', font=('Time New Roman', 15))
                if(user_id == userid):
                    Information.configure(fg_color = 'blue')
                Information.pack(padx=5, pady = 5,expand=True, fill='x')
                users_list.append(user_frame)

            else:
                text = f'UserID: {user[0]} - Tên: {user[1]} - Email: {user[4]} - Số dư: {user[9]}'
                Information = customtkinter.CTkButton(user_frame, text=text, anchor='w', width=600, font=('Time New Roman', 15), command=lambda id=user_id: display_user_detail(id))
                if(user[7]==True):
                    if((user[8] > datetime.now())):
                        Information.configure(fg_color = 'red')
                Information.pack(padx=5, pady = 5,expand=True, fill='x')
                users_list.append(user_frame)


        inner_frame.update_idletasks()
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        def on_canvas_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_canvas_configure)

        return users_list
    else:
        return None

def display_user_detail(user_id):
    detail_window = customtkinter.CTk()
    detail_window.geometry("600x400")
    detail_window.title('Thông tin chi tiết')
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM ACCOUNTS WHERE UserID = ?'
    cursor.execute(query, user_id)
    user_data = cursor.fetchone()
    
    IDLabel = customtkinter.CTkLabel(detail_window, text='User ID: ' + str(user_data[0]), font=('Time New Roman', 15))
    IDLabel.place(x=100, y=50)

    NameLabel = customtkinter.CTkLabel(detail_window, text = 'Tên: ' + user_data[1], font=('Time New Roman', 15))
    NameLabel.place(x=100, y=80)

    if(user_data[2] == None):
        BirthdayLabel = customtkinter.CTkLabel(detail_window, text='Ngày sinh: Chưa nhập', font=('Time New Roman', 15))
        BirthdayLabel.place(x=100, y=110)
    else:
        BirthdayLabel = customtkinter.CTkLabel(detail_window, text=f'Ngày sinh: {user_data[2].day}/{user_data[2].month}/{user_data[2].year}', font=('Time New Roman', 15))
        BirthdayLabel.place(x=100, y=110)

    gender = 'Chưa nhập'
    if(user_data[3] == 'M'):
        gender = 'Nam'
    elif(user_data[3] == 'F'):
        gender = 'Nữ'
    elif(user_data[3] == 'O'):
        gender = 'Khác'
    GenderLabel = customtkinter.CTkLabel(detail_window, text='Giới tính: ' + gender, font=('Time New Roman', 15))
    GenderLabel.place(x=100, y=140)
    
    EmailLabel = customtkinter.CTkLabel(detail_window, text = 'Email: ' + user_data[4], font=('Time New Roman', 15))
    EmailLabel.place(x=100, y=170)

    locked = 'Không'
    if(user_data[7] == 1):
        if((user_data[8] > datetime.now())):
            locked = f'Tới ngày {user_data[8].day}/{user_data[8].month}/{user_data[8].year}'
    LockedLabel = customtkinter.CTkLabel(detail_window, text = 'Khóa: ' + locked, font=('Time New Roman', 15))
    LockedLabel.place(x=100, y=200)

    BalanceLabel = customtkinter.CTkLabel(detail_window, text = 'Số dư: ' + str(user_data[9]), font=('Time New Roman', 15))
    BalanceLabel.place(x=100, y=230) 

    query = 'SELECT Ngay FROM TRANSACTIONS WHERE UserID = ? ORDER BY Ngay DESC'
    cursor.execute(query, user_id)
    result = cursor.fetchone()
    recent = 'Chưa có giao dịch'
    if result:
        recentday = result[0]
        recent = f'{recentday.day}/{recentday.month}/{recentday.year}'
    RecentLabel = customtkinter.CTkLabel(detail_window, text = 'Ngày giao dịch gần nhất: ' + recent, font=('Time New Roman', 15))
    RecentLabel.place(x=100, y=260)

    CloseButton = customtkinter.CTkButton(detail_window, width=50, text = "Đóng", command =  lambda: detail_window.destroy())
    CloseButton.place(x=100, y=290)

    NotifyButton = customtkinter.CTkButton(detail_window, width=50, text = "Thông báo", command =  lambda: notify_user(user_id))
    NotifyButton.place(x=160, y=290)

    if(user_data[7]):
        if (user_data[8] > datetime.now()):
            UnlockButton = customtkinter.CTkButton(detail_window, width=50, text = "Mở khóa", command =  lambda: unlock_user(user_id, detail_window))
            UnlockButton.place(x=245, y=290)
        else:
            LockButton = customtkinter.CTkButton(detail_window, width=50, text = "Khóa", command =  lambda: lock_user(user_id, detail_window))
            LockButton.place(x=245, y=290) 
    else:
        LockButton = customtkinter.CTkButton(detail_window, width=50, text = "Khóa", command =  lambda: lock_user(user_id, detail_window))
        LockButton.place(x=245, y=290) 
    detail_window.mainloop()

def notify_user(user_id):
    notify_window = customtkinter.CTk()
    notify_window.geometry("350x350")
    notify_window.title('Xác nhận thông báo')
    Label = customtkinter.CTkLabel(notify_window, text = 'Nhập thông báo', font=('Time New Roman', 20))
    Label.pack(padx=10, pady = 5)
    Entry = customtkinter.CTkTextbox(notify_window, width=300, height=200, wrap='word')
    Entry.pack(padx=10, pady = 5)
    Button = customtkinter.CTkButton(notify_window, text = 'Xác nhận', command = lambda: confirm_notify(user_id, Entry.get("1.0", "end-1c"), notify_window))
    Button.pack(padx=10, pady=10)
    notify_window.mainloop()

def confirm_notify(user_id, text, notify_window):
    connection, cursor = connect_to_database()

    if connection and cursor:
        try:
            if(text == None):
                messagebox.showerror('Error', 'Không được để trống nội dung')
                return
            update_query = 'INSERT INTO NOTIFICATIONS(UserID, Thongbao, Ngaygui) VALUES(?,?,?)'
            try:
                cursor.execute(update_query, user_id, text, datetime.now())
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Gửi thông báo thành công')
                notify_window.destroy()
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Gửi thông báo thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Gửi thông báo thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')

def unlock_user(user_id, detail_window):
    result = messagebox.askokcancel("Xác nhận", "Bạn có muốn mở khóa tài khoản này không?")
    if result:
        connection, cursor = connect_to_database()
        if connection and cursor:
            try:
                update_query = 'UPDATE ACCOUNTS SET Khoa = NULL, Thoigiankhoa=NULL WHERE UserID = ?'
                try:
                    cursor.execute(update_query, user_id)
                    connection.commit()
                    print("Update Successful")
                    messagebox.showinfo('Success', 'Mở khóa thành công!')
                    detail_window.destroy()
                except Exception as e:
                    print(f'Error during update: {e}')
                    messagebox.showerror('Error', f'Mở khóa thất bại: {e}')
            except Exception as e:
                messagebox.showerror('Error', f'Mở khóa thất bại: {e}')

            connection.close()
        else:
            messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')
    else:
        return 

def lock_user(user_id, detail_window):
    lock_window = customtkinter.CTk()
    lock_window.geometry("350x150")
    lock_window.title('Xác nhận khóa')
    DateLabel = customtkinter.CTkLabel(lock_window, text='Ngày hết khóa: ', font=('Time New Roman', 15))
    DateLabel.place(x=50, y=50)

    day_entry = customtkinter.CTkEntry(lock_window, width=30)
    day_entry.place(x=150, y=50)

    separator_label_1 = customtkinter.CTkLabel(lock_window, text="/")
    separator_label_1.place(x=180, y=50)

    month_entry = customtkinter.CTkEntry(lock_window, width=30)
    month_entry.place(x=190, y=50)

    separator_label_2 = customtkinter.CTkLabel(lock_window, text="/")
    separator_label_2.place(x=220, y=50)

    year_entry = customtkinter.CTkEntry(lock_window, width=45)
    year_entry.place(x=230, y=50)

    Button = customtkinter.CTkButton(lock_window, text = 'Xác nhận', command = lambda: confirm_lock(user_id, day_entry.get(), month_entry.get(), year_entry.get(), detail_window, lock_window))
    Button.pack(padx=10, pady=10, side = 'bottom')
    lock_window.mainloop()

def confirm_lock(user_id, day, month, year, detail_window, lock_window):
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
            if (date < datetime.now()):
                messagebox.showerror('Error', 'Ngày khóa không thể là ngày đã qua')
                return
        else:
            messagebox.showerror('Error', 'Vui lòng nhập đầy đủ ngày, tháng và năm')
            return
    except ValueError:
        messagebox.showerror('Error', 'Ngày hết khóa không hợp lệ.')
        return
    
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            update_query = 'UPDATE ACCOUNTS SET Khoa = ?, Thoigiankhoa = ?  WHERE UserID=?'
            try:
                cursor.execute(update_query, True, date, user_id)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Khóa thành công!')
                lock_window.destroy()
                detail_window.destroy()
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Khóa thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Khóa thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.') 

#function for tab_3
################################################################################################
def display_categories_list(frame, userid):
    connection, cursor = connect_to_database()
    query = 'SELECT * FROM CATEGORIES ORDER BY CategoryID'
    cursor.execute(query)
    categories_data = cursor.fetchall()
    if categories_data:
        canvas_width = 610 
        canvas_height = 500

        canvas = customtkinter.CTkCanvas(frame, width=canvas_width, height=canvas_height)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = Scrollbar(frame, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = customtkinter.CTkFrame(canvas, bg_color='transparent')
        inner_frame.pack(fill='both', expand=True)

        categories_list = []

        for i, category in enumerate(categories_data):
            category_id = category[0]
            category_frame = customtkinter.CTkFrame(inner_frame, fg_color='transparent')
            query = 'SELECT COUNT(*) FROM TRANSACTIONS WHERE CategoryID = ?'
            cursor.execute(query, category[0])
            Sogiaodich = cursor.fetchone()[0]
            text = f'ID: {category[0]} - Loại: {category[2]} - Tên: {category[1]} - Số giao dịch: {Sogiaodich}'

            Information = customtkinter.CTkButton(category_frame, text=text, anchor='w', width=600, font=('Time New Roman', 15))
            if (category[0] > 410000 and category[0] < 420000):
                Information.configure(fg_color = 'red')
            elif (category[0] > 420000 and category[0] < 430000):
                Information.configure(fg_color = 'orange')
            elif (category[0] > 430000 and category[0] < 440000):
                Information.configure(fg_color = 'blue')
            if (Sogiaodich == 0):
                Information.configure(fg_color = 'grey', command=lambda id=category_id: delete_category(id))
            Information.pack(padx=5, pady = 5,expand=True, fill='x')
            categories_list.append(category_frame)


        inner_frame.update_idletasks()
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        def on_canvas_configure(event):
            canvas.config(scrollregion=canvas.bbox('all'))

        canvas.bind('<Configure>', on_canvas_configure)

        return categories_list
    else:
        return None

def add_category():
    add_category_window = customtkinter.CTk()
    add_category_window.geometry("350x150")
    add_category_window.title('Thêm hạng mục')

    TypeLabel = customtkinter.CTkLabel(add_category_window, text='Loại giao dịch: ', font=('Time New Roman', 15))
    TypeLabel.place(x=50, y=20)
    type_options = ['Thu', 'Chi', 'Vay', 'Nợ']
    TypeDropdown = customtkinter.CTkComboBox(add_category_window, width=60, values=type_options, state="readonly")
    TypeDropdown.place(x=150, y=20)

    NameLabel = customtkinter.CTkLabel(add_category_window, text='Tên hạng mục: ', font=('Time New Roman', 15))
    NameLabel.place(x=50, y=50)
    Name_entry = customtkinter.CTkEntry(add_category_window, width=150)
    Name_entry.place(x=150, y=50)

    Button = customtkinter.CTkButton(add_category_window, text = 'Xác nhận', command = lambda: confirm_add_category(TypeDropdown.get(), Name_entry.get(), add_category_window))
    Button.pack(padx=10, pady=10, side = 'bottom')
    add_category_window.mainloop()

def confirm_add_category(type, name, window):
    if(type == None or name==None):
        messagebox.showerror('Error', 'Vui lòng nhập đủ thông tin.')
        return
    
    connection, cursor = connect_to_database()
    if connection and cursor:
        try:
            query = 'SELECT CategoryID FROM CATEGORIES WHERE Loai = ?'
            cursor.execute(query, type)
            results=cursor.fetchall()
            if (type == 'Thu'):
                category_id = 400001
            elif (type == 'Chi'):
                category_id = 410001
            elif (type == 'Nợ'):
                category_id = 420001
            elif (type == 'Vay'):
                category_id = 430001
            existing_category_ids = [result[0] for result in results]
            while category_id in existing_category_ids:
                category_id+=1

            update_query = 'INSERT INTO CATEGORIES(CategoryID, Tenhangmuc, Loai) Values (?, ?, ?)'
            print(category_id, name, type)
            try:
                cursor.execute(update_query, category_id, name, type)
                connection.commit()
                print("Update Successful")
                messagebox.showinfo('Success', 'Thêm hạng mục thành công!')
                window.destroy()
            except Exception as e:
                print(f'Error during update: {e}')
                messagebox.showerror('Error', f'Thêm hạng mục thất bại: {e}')
        except Exception as e:
            messagebox.showerror('Error', f'Thêm hạng mục thất bại: {e}')

        connection.close()
    else:
        messagebox.showerror('Error', 'Kết nối cơ sở dữ liệu thất bại.')   

def delete_category(category_id):
    result = messagebox.askokcancel("Xác nhận", "Bạn có muốn xóa hạng mục này không?")
    if result:
        connection, cursor = connect_to_database()
        if connection and cursor:
            try:
                update_query = 'DELETE FROM CATEGORIES WHERE CategoryID=?'
                print("Values:", category_id)
                try:
                    cursor.execute(update_query, category_id)
                    connection.commit()
                    print("Update Successful")
                    messagebox.showinfo('Success', 'Xóa thành công!')
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
#################################################################################################
def home_page_admin(user_id):
    global home_window_admin
    home_window_admin = customtkinter.CTk()
    home_window_admin.geometry("800x600")
    home_window_admin.title('Home Page for Admin')

    connection, cursor = connect_to_database()

    if connection and cursor:
        tabview = customtkinter.CTkTabview(home_window_admin)
        tabview.pack(fill=customtkinter.BOTH, expand=True, padx=20, pady=20)
        tabview.add("Thông tin cá nhân")
        tabview.add("Quản lý người dùng hệ thống")
        tabview.add("Hạng mục chi tiêu")

        tabview.set("Quản lý người dùng hệ thống")
        user_data = fetch_user_data(cursor, user_id)

        #tab-1
        if user_data:
            frame = customtkinter.CTkFrame(tabview.tab("Thông tin cá nhân"))
            display_user_info(frame, user_data)
        else:
            print("User data not found") 
        logout_button = customtkinter.CTkButton(tabview.tab("Thông tin cá nhân"), text='Đăng xuất', command=logout)
        logout_button.pack(padx=20, pady=20)

        #tab_2
        frame2 = customtkinter.CTkFrame(tabview.tab("Quản lý người dùng hệ thống"))
        frame2.pack()
        user_frames = display_users_list(frame2, user_id)
        if user_frames:
            for user_frame in user_frames:
                user_frame.pack()
        else:
            customtkinter.CTkLabel(frame2, text="Không có end-user nào trong hệ thống.", font=('Time New Roman', 30)).pack()
        RefreshButton = customtkinter.CTkButton(tabview.tab("Quản lý người dùng hệ thống"), width=100, text='Refresh', command=lambda: (home_window_admin.destroy(), home_page_admin(user_id), tabview.set("Quản lý người dùng hệ thống")))
        RefreshButton.pack(side='bottom',pady=10)

        query = 'SELECT COUNT(*) FROM ACCOUNTS WHERE Admin=0'
        cursor.execute(query)
        user_number = cursor.fetchone()[0]
        
        query = 'SELECT COUNT(*) FROM ACCOUNTS WHERE Admin=1'
        cursor.execute(query)
        admin_number = cursor.fetchone()[0]
        NumberLabel = customtkinter.CTkLabel(tabview.tab("Quản lý người dùng hệ thống"), text=f'Admin: {str(admin_number)}          Người dùng: {str(user_number)}', font = ('Time New Roman', 15)) 
        NumberLabel.pack(side='bottom',pady=10)

        #tab_3
        frame3 = customtkinter.CTkFrame(tabview.tab("Hạng mục chi tiêu"))
        frame3.pack()
        categories_frames = display_categories_list(frame3, user_id)
        if categories_frames:
            for category_frame in categories_frames:
                category_frame.pack()
        else:
            customtkinter.CTkLabel(frame3, text="Không có hạng mục chi tiêu nào trong hệ thống.", font=('Time New Roman', 30)).pack()
        
        RefreshButton = customtkinter.CTkButton(tabview.tab("Hạng mục chi tiêu"), width=120, text='Refresh', command=lambda: (home_window_admin.destroy(), home_page_admin(user_id), tabview.set("Hạng mục chi tiêu")))
        RefreshButton.pack(side='bottom',pady=2)

        AddButton = customtkinter.CTkButton(tabview.tab("Hạng mục chi tiêu"), width=120, text='Thêm hạng mục', command=add_category)
        AddButton.pack(side='bottom',pady=2)

        query = 'SELECT COUNT(*) FROM CATEGORIES WHERE Loai = ?'
        cursor.execute(query, 'Thu')
        earn_number = cursor.fetchone()[0]
        
        query = 'SELECT COUNT(*) FROM CATEGORIES WHERE Loai = ?'
        cursor.execute(query, 'Chi')
        spend_number = cursor.fetchone()[0]

        query = 'SELECT COUNT(*) FROM CATEGORIES WHERE Loai = ?'
        cursor.execute(query, 'Vay')
        borrow_number = cursor.fetchone()[0]

        query = 'SELECT COUNT(*) FROM CATEGORIES WHERE Loai = ?'
        cursor.execute(query, 'Nợ')
        owe_number = cursor.fetchone()[0]

        CountLabel = customtkinter.CTkLabel(tabview.tab("Hạng mục chi tiêu"), text=f'Thu: {str(earn_number)}   Chi: {str(spend_number)}    Vay: {str(borrow_number)}   Nợ: {str(owe_number)}', font = ('Time New Roman', 15)) 
        CountLabel.pack(side='bottom',pady=10)
        home_window_admin.mainloop()

if __name__ == "__main__":
    home_page_admin(100001)