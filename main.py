import sqlite3
import os
import cv2
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import END, Button, Entry, Label, PhotoImage, messagebox, filedialog
import face_recognition as fr
import shutil
from datetime import datetime, date

# defaults
DefalutLoginId = "Admin"
DefaultLoginPwd = "Password"


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        window = tk.Frame(self)
        window.pack()
        window.grid_rowconfigure(0, minsize=450)
        window.grid_columnconfigure(0, minsize=800)

        self.frames = {}
        for F in (Login, Menu, AddAPerson, RemoveAPerson, ShowDB, ShowAttendance):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(Menu)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.title("Automatic Attendance")


class Login(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # bgimg:
        bgimgpath = "UI 2/Login Screen.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        def done():
            if self.id.get() == "" or self.pwd.get() == "":
                self.id.delete(0, 'end')
                self.pwd.delete(0, 'end')
                messagebox.showwarning(title="Error",
                                       message="Fields cannot be empty",
                                       parent=self)

            elif self.id.get() == DefalutLoginId and self.pwd.get() == DefaultLoginPwd:
                controller.show_frame(Menu)

            else:
                self.id.delete(0, 'end')
                self.pwd.delete(0, 'end')
                messagebox.showwarning(title="Error",
                                       message="One or more credentials wrong!",
                                       parent=self)

        # Login id:
        self.id = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=35)
        self.id.place(x=104, y=158)
        self.id.bind('<Return>', lambda func1: self.pwd.focus())  # to press enter to continue

        # password:
        self.pwd = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=35, show="$")
        self.pwd.place(x=106, y=262)
        # self.pwd.bind('<Return>', done) # binding enter key to the doneBtn

        donebutton = tk.Button(self, command=done, text="LOGIN", fg="black", border=0, font=("", 26, "bold"), padx=70)
        donebutton.place(x=270, y=322)


class Menu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        bgimgpath = "UI 2/new menu.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        # buttons
        addbutton = tk.Button(self, text="Add a person", fg="black", border=0, font=("", 29, "bold"), padx=25,
                              command=lambda: controller.show_frame(AddAPerson)).place(x=112, y=158)

        rembutton = tk.Button(self, text="Remove a person", fg="black", border=0, font=("", 29, "bold"), padx=0,
                              command=lambda: controller.show_frame(RemoveAPerson)).place(x=413, y=156)

        showdatabase = tk.Button(self, text="Show Database", fg="black", border=0, font=("", 29, "bold"), padx=11,
                               command=lambda: controller.show_frame(ShowDB)).place(x=107, y=240)

        showattendance = tk.Button(self, text="Show Attendance", fg="black", border=0, font=("", 29, "bold"), padx=0,
                                 command=lambda: controller.show_frame(ShowAttendance)).place(x=413, y=242)

        startbutton = tk.Button(self, text="Start Attendance", fg="black", border=0, font=("", 29, "bold"), padx=152,
                                command=lambda: self.startAttendance()).place(x=107, y=328)

    def startAttendance(self):
        import camera
        if key == ord('q'):
            return


class AddAPerson(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        bgimgpath = "UI 2/new Add a person.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        self.value = False
        # entry
        self.name = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=26)
        self.name.place(x=240, y=113)
        self.name.bind('<Return>', lambda func1: self.empid.focus())

        self.empid = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=8)
        self.empid.place(x=240, y=169)
        self.empid.bind('<Return>', lambda func2: self.job.focus())

        self.job = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=12)
        self.job.place(x=463, y=169)
        self.job.bind('<Return>', lambda func: self.address.focus())


        self.address = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=26)
        self.address.place(x=240, y=223)
        self.address.bind('<Return>', lambda func3: self.mobile.focus())

        self.mobile = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=26)
        self.mobile.place(x=240, y=280)
        self.chkimg = tk.Label(self, text="", font=("", 26))


        # self.mobile.bind('<Return>', lambda: self.capture)

        # functions:

        # buttons
        addimg = tk.Button(self, text="Add image", fg="black", border=0, font=("", 29, "bold"), padx=32,
                           command=self.capture).place(x=124, y=357)

        addtodb = tk.Button(self, text="Add To DB", fg="black", border=0, font=("", 29, "bold"), padx=34,
                            command=self.addtodatabase).place(x=420, y=357)

        backbtn = tk.Button(self, text="◀ Back", fg="black", border=0, font=("", 16), padx=10,
                            command=lambda: controller.show_frame(Menu)).place(x=75, y=30)

        clearbutton = tk.Button(self, text="X-Clear", fg="black", border=0, font=("", 16), padx=10,
                                command=self.clear).place(x=575, y=33)

        self.makedb()

    def capture(self):
        # captured = False
        answer = messagebox.askokcancel(title="chose file",
                                        message="Browse Image? \n Hit cancel to start Camera !",
                                        parent=self)
        if answer:
            # captured = True
            filename = filedialog.askopenfilename()
            filename= str(filename)
            self.value = True
            shutil.copy(filename, "image.jpg")

        else:
            # captured = True
            vid = cv2.VideoCapture(0)
            while True:
                success, frame = vid.read()
                cv2.imshow("hit 's' to save image", frame)
                key = cv2.waitKey(1)
                if key == ord('s'):
                    self.value = True
                    cv2.imwrite('image.jpg', frame)
                    cv2.destroyWindow("hit 's' to save image")
                    break
            vid.release()

        if self.value:
            self.chkimg.config(text="✓")
            self.chkimg.place(x=126, y=359)
            self.chkimg.tkraise()
        return

    def clear(self):
        self.name.delete(0, 'end')
        self.empid.delete(0, 'end')
        self.address.delete(0, 'end')
        self.mobile.delete(0, 'end')
        self.job.delete(0, 'end')
        self.chkimg.config(text='')

    def makedb(self):
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (name TEXT, 
                                                            empId TEXT PRIMARY KEY,
                                                            job TEXT,
                                                            address TEXT, 
                                                            mob INT,
                                                            image BLOB)""")
        conn.commit()
        c.close()
        conn.close()

    def addtodatabase(self):
        if self.name.get() == '' or self.empid.get() == '' or self.mobile.get() == '' or self.address.get() == '' or self.job.get() == '' or self.value == False:
            messagebox.showwarning(title="Fields Empty",
                                   message="One or more fields empty",
                                   parent=self)
            return

        add_name = self.name.get()
        add_empid = self.empid.get()
        add_address = self.address.get()
        add_mob = self.mobile.get()
        add_job = self.job.get()
        with open('image.jpg', 'rb') as f:
            add_img = f.read()


        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        try:
            c.execute(f"""INSERT INTO users (name, empid, job, address, mob, image)
                        VALUES (?, ?, ?, ?, ?, ?)""", (add_name, add_empid, add_job, add_address, add_mob, add_img))

        except sqlite3.IntegrityError:
            messagebox.showerror(title="Already Present",
                                 message="This empid is already present in the DB",
                                 parent=self)
        finally:
            conn.commit()
            c.close()
            conn.close()
            messagebox.showinfo(title="Added Successfully",
                                message="The data was added to the database successfully",
                                parent=self)
            self.clear()


class RemoveAPerson(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        bgimgpath = "UI 2/Remove a person.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        # entry
        self.name = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=26)
        self.name.place(x=243, y=190)
        self.name.bind('<Return>', lambda func1: self.empid.focus())

        self.empid = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=26)
        self.empid.place(x=243, y=250)

        # functions:
        def sure():
            if self.name.get() == "" or self.empid.get() == "":
                self.name.delete(0, 'end')
                self.empid.delete(0, 'end')
                messagebox.showwarning(title="Error",
                                       message="Fields cannot be empty",
                                       parent=self)
                return

            answer = messagebox.askyesno(title="Confirmation",
                                         message=f"Are you sure you want to delete \nEmp id : {self.empid.get()} \nEmp name : {self.name.get()} ?",
                                         parent=self)
            if answer:
                remove()

        def remove():
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()

            c.execute(
                f"DELETE FROM users WHERE name='{self.name.get()}'AND empId='{self.empid.get()}'")

            conn.commit()
            c.close()
            conn.close()
            messagebox.showinfo(title="Removed Successfully",
                                message="The record was removed from the database successfully",
                                parent=self)
            self.name.delete(0, 'end')
            self.empid.delete(0, 'end')
            self.name.focus()

        # buttons
        backbtn = tk.Button(self, text="◀ Back", fg="black", border=0, font=("", 16), padx=2,
                            command=lambda: controller.show_frame(Menu)).place(x=75, y=30)
        rembutton = tk.Button(self, text="Remove", fg="black", border=0, font=("", 26), padx=60,
                              command=sure).place(x=260, y=345)
        self.name.focus()
        # add a popup window to either show an error or to show something like do you wish to continue to delete


class ShowDB(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        bgimgpath = "UI 2/Show database.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        # entry
        scroll_v = tk.Scrollbar(self, orient=tk.VERTICAL)
        scroll_v.pack(side=tk.RIGHT, fill="y")

        scroll_h = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        scroll_h.pack(side=tk.BOTTOM, fill="x")

        self.db = tk.Text(self, font=("Ivory", 26), bg="grey", fg="orange", width=34, height=9, pady=6, padx=2,
                                        wrap= tk.NONE, yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
        scroll_h.config(command=self.db.xview)
        scroll_v.config(command=self.db.yview)
        self.db.place(x=116, y=99)

        self.refresh()
        self.db.config(state='disabled')
        # buttons
        backbtn = tk.Button(self, text="◀ Back", fg="black", border=0, font=("", 16), padx=2,
                            command=lambda: controller.show_frame(Menu)).place(x=75, y=30)

        refbutton = tk.Button(self, text="⟲-Refresh", fg="black", border=0, font=("", 16), padx=10,
                              command=self.refresh).place(x=575, y=36)

    def refresh(self):
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        # try:
        text = c.execute('SELECT * FROM users')
        space = " || "
        self.db.config(state='normal')
        self.db.delete('1.0', 'end')
        for x in text:
            self.db.insert(tk.END, x[0] + space + x[1] + space + x[2] + space + str(x[3]) + space + str(x[4]) + '\n')

        self.db.config(state='disabled')
        conn.commit()
        c.close()
        conn.close()

        # except:
        #     messagebox.showerror(title="Error", message="No Person is added to the table", parent=self)
        #     c.close()
        #     conn.close()
        return


class ShowAttendance(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        bgimgpath = "UI 2/Show attendance.png"
        load = Image.open(bgimgpath)
        photo = ImageTk.PhotoImage(load)
        label = tk.Label(self, image=photo)
        label.image = photo
        label.place(x=0, y=0, relheight=1, relwidth=1)

        scroll_v = tk.Scrollbar(self, orient=tk.VERTICAL)
        scroll_v.pack(side=tk.RIGHT, fill="y")

        scroll_h = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        scroll_h.pack(side=tk.BOTTOM, fill="x")

        self.db = tk.Text(self, font=("Ivory", 26), bg="grey", fg="orange", width=34, height=9, pady=6, padx=2,
                          wrap=tk.NONE, yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
        scroll_h.config(command=self.db.xview)
        scroll_v.config(command=self.db.yview)
        self.db.place(x=113, y=105)


        self.db.config(state='disabled')

        searchDate = date.today()
        searchDate = str(searchDate)

        self.date_entry = tk.Entry(self, font=("Ivory", 26), bg="grey", fg="orange", width=11)


        self.date_entry.place(x=280, y=56)

        backbtn = tk.Button(self, text="◀ Back", fg="black", border=0, font=("", 16), padx=10,
                            command=lambda: controller.show_frame(Menu)).place(x=75, y=30)

        searchbutton = tk.Button(self, text='Search', fg="black", border=0, font=("", 26, "bold"), padx=9,
                              command = lambda: self.getdata()).place(x=483, y=56)

    def getdata(self):
        # self.date_entry.insert(0, searchDate)
        searchDate = self.date_entry.get()
        searchDate = str(searchDate)
        # print(searchDate)
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        try:
            text = c.execute(f'SELECT * FROM "{searchDate}"')
        except sqlite3.OperationalError:
            messagebox.showerror(title="No such table",
                                message="No such table exists!",
                                parent=self)
            self.db.config(state='normal')
            self.db.delete('1.0', 'end')
            self.db.config(state='disabled')

            return
        space = " || "
        self.db.config(state='normal')
        self.db.delete('1.0', 'end')
        for x in text:
            self.db.insert(tk.END,
                           x[0] + space + x[1] + space + x[3] + '\n')

        self.db.config(state='disabled')
        conn.commit()
        c.close()
        conn.close()

        # except:
        #     messagebox.showerror(title="Error", message="No Person is added to the table", parent=self)
        #     c.close()
        #     conn.close()
        return



app = Application()
app.mainloop()
