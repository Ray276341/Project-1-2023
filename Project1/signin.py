import customtkinter
from tkinter import messagebox, END
import pyodbc
from datetime import datetime
from home import home_page

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

def login():
    if emailEntry.get() == '' or passwordEntry.get() == '':
        messagebox.showerror('Error','Chưa nhập đủ các trường')
    else:
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-IU28R6R\\SQLEXPRESS;"
            "DATABASE=Project1;"
            "Trusted_Connection=yes;")
        try:
            connection = pyodbc.connect(conn_str)
            cursor = connection.cursor()
        except Exception as e:
            messagebox.showerror('Error', f'Kết nối cơ sở dữ liệu thất bại: {e}')
            print(f'Error: {e}')
            return
        
        query = 'select * from ACCOUNTS where Email=?'
        cursor.execute(query,(emailEntry.get()))
        row=cursor.fetchone()
        if row == None:
            messagebox.showerror('Error','Email chưa tồn tại trong hệ thống')
        else:
            password_index = None
            for i, desc in enumerate(cursor.description):
                if desc[0] == 'Matkhau':
                    password_index = i
                    break
            if row[password_index] != passwordEntry.get():
                messagebox.showerror('Error', 'Sai mật khẩu')
            else:
                locked_index = None
                for i, desc in enumerate(cursor.description):
                    if desc[0] == 'Khoa':
                        locked_index = i
                        break
                day_locked_index = None
                for i, desc in enumerate(cursor.description):
                    if desc[0] == 'Thoigiankhoa':
                        day_locked_index = i
                        break
                today = datetime.now()
                if (row[locked_index] == 1) and (row[day_locked_index] > today ):
                    messagebox.showinfo('Error', f'Tài khoản bị khóa tới ngày {row[day_locked_index].day}/{row[day_locked_index].month}/{row[day_locked_index].year}')
                else:
                    user_id = row[0]
                    admin_index = None
                    for i, desc in enumerate(cursor.description):
                        if desc[0] == 'Admin':
                            admin_index = i
                            break
                    if (row[admin_index] == 0):
                        messagebox.showinfo('Success', 'Đăng nhập thành công')
                        login_window.destroy()
                        home_page(user_id)
                    else: 
                        messagebox.showinfo('Success', 'Đăng nhập thành công với vai trò quản trị viên')
                        login_window.destroy()
                        import home_admin
                        home_admin.home_page_admin(user_id)
                


def signup_page():
    login_window.destroy()
    import signup

#GUI
login_window = customtkinter.CTk()
login_window.geometry("500x350")
login_window.resizable(0,0)
login_window.title('Quan ly chi tieu')

frame = customtkinter.CTkFrame(master=login_window)
frame.pack(padx=20,pady=60, fill="both", expand=True)

heading=customtkinter.CTkLabel(master=frame, text="USER LOGIN", font=("Roboto", 24,'bold'))
heading.pack(padx=10, pady=12)

emailEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Email")
emailEntry.pack(padx=10, pady=12)

passwordEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Password", show="*")
passwordEntry.pack(padx=10, pady=12)

loginbutton = customtkinter.CTkButton(master=frame, text="Login", command=login, cursor='hand2')
loginbutton.pack(padx=10,pady=12)

signuplabel=customtkinter.CTkLabel(master=frame, text="Don't have an account?", font=("Roboto",12))
signuplabel.place(x=147,y=200)

signupbutton=customtkinter.CTkButton(master=frame, width=18, text="Sign up", font=("Roboto", 12, 'underline'),bg_color='transparent',fg_color='transparent',text_color='black',cursor='hand2',command=signup_page)
signupbutton.place(x=270,y=200)

login_window.mainloop()
