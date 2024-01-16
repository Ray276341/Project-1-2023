import customtkinter
from tkinter import messagebox, END
import pyodbc

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

def clear():
    emailEntry.delete(0,END)
    nameEntry.delete(0,END)
    passwordEntry.delete(0,END)
    confirmpasswordEntry.delete(0,END)

def signup():
    if emailEntry.get() == '' or nameEntry.get() == '' or passwordEntry.get() == '' or confirmpasswordEntry.get() == '':
        messagebox.showerror('Lỗi','Chưa nhập đủ các trường')
    elif passwordEntry.get() != confirmpasswordEntry.get():
        messagebox.showerror('Lỗi','Không khớp mật khẩu')
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
        
        query = 'SELECT max(UserID) FROM ACCOUNTS'
        cursor.execute(query)
        row = cursor.fetchone()
        if row and row[0] is not None:
            biggestID = row[0]
            newUserID = biggestID + 1
        else:
            newUserID = 110001
        
        query = 'select * from ACCOUNTS where Email=?'
        cursor.execute(query,(emailEntry.get()))
        row=cursor.fetchone()
        if row != None:
            messagebox.showerror('Lỗi','Email đã tồn tại trong hệ thống')
        else:
            query='insert into ACCOUNTS(UserID,Email,Ten,Matkhau) values(?,?,?,?)'
            try:
                cursor.execute(query,(newUserID,emailEntry.get(),nameEntry.get(),passwordEntry.get()))
                connection.commit()
                messagebox.showinfo('Success','Đăng ký thành công')
            except Exception as e:
                messagebox.showerror('Error', f'Kết nối cơ sở dữ liệu thất bại: {e}')
                print(f'Error: {e}')
                return
            finally:
                connection.close()
                cursor.close()
                clear()
                login_page()

def login_page():
    signup_window.destroy()
    import signin



#GUI
signup_window = customtkinter.CTk()
signup_window.geometry("500x500")
signup_window.resizable(0,0)
signup_window.title('Quan ly chi tieu')

frame = customtkinter.CTkFrame(master=signup_window)
frame.pack(padx=20,pady=60, fill="both", expand=True)

heading=customtkinter.CTkLabel(master=frame, text="USER SIGN UP", font=("Roboto", 24,'bold'))
heading.pack(padx=10, pady=12)

emailEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Email")
emailEntry.pack(padx=10, pady=12)

nameEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Name")
nameEntry.pack(padx=10, pady=12)

passwordEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Password", show="*")
passwordEntry.pack(padx=10, pady=12)

confirmpasswordEntry = customtkinter.CTkEntry(master=frame, width=200, placeholder_text="Confirm Password", show="*")
confirmpasswordEntry.pack(padx=10, pady=12)

signupbutton = customtkinter.CTkButton(master=frame, text="Sign up", command=signup, cursor='hand2')
signupbutton.pack(padx=10,pady=12)

loginlabel=customtkinter.CTkLabel(master=frame, text="Already have an account?", font=("Roboto",12))
loginlabel.place(x=140,y=310)

loginbutton=customtkinter.CTkButton(master=frame, width=18, text="Login", font=("Roboto", 12, 'underline'),bg_color='transparent',fg_color='transparent',text_color='black',cursor='hand2', command=login_page)
loginbutton.place(x=277,y=310)

signup_window.mainloop()
