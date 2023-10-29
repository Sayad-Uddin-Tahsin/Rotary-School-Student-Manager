import customtkinter as ctk
import threading
import time
import requests.exceptions
import google.auth.exceptions
import urllib3.exceptions
import re
from PIL import Image
import _tkinter
import os
from tkinter import messagebox
import json
import darkdetect
import gspread
from google.oauth2.service_account import Credentials
import sys
import urllib.parse
import webbrowser
import pyasn1.error

path = os.path.dirname(os.path.realpath(__file__))

with open(f"{path}/data.json", "r") as f:
    data = json.load(f)
    appearence_mode = data["appearence_mode"]
    color_theme = data["color_theme"]

ctk.set_appearance_mode(appearence_mode)
ctk.set_default_color_theme(color_theme)

database = None
assetsPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Assets")


def edit_data(key, value):
    with open(f"{path}/data.json", 'r') as f:
        data = json.load(f)
    data[key] = value
    with open(f"{path}/data.json", 'w') as f:
        json.dump(data, f, indent=4)


class Database():
    def __init__(self) -> None:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials = Credentials.from_service_account_file(
            f'{path}/creds.json',
            scopes=scopes
        )

        gc = gspread.authorize(credentials)

        self.sheet = gc.open("Rotary School Student Data").sheet1

    def get_all(self) -> list:
        return self.sheet.get()
    
    def get_classes(self) -> str:
        try:
            f = self.sheet.find("$Class$")
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        value = self.sheet.cell(f.row, f.col + 1).value
        value = value.replace("\"", "") 
        if value != '':
            value = value.split(", ")
        else:
            value = []
        return value

    def get_all_sections(self, class_str: str) -> list:
        try:
            data = self.sheet.col_values(2)
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        data = data[data.index("Class-Roll") + 1:]
        data = [i for i in data if i]

        sections = []
        for d in data:
            if str(d).split("-")[0] == class_str:
                if str(d).split("-")[1] not in sections:
                    sections.append(str(d).split("-")[1])
        sections.sort()
        return sections
    
    def get_student_amount_by_class(self) -> dict:
        try:
            data = self.sheet.col_values(2)
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        data = data[data.index("Class-Roll") + 1:]
        data = [i for i in data if i]
        
        student_dict = {}
        
        for d in data:
            _class = str(d).split("-")[0]
            if _class in student_dict:
                student_dict[_class] += 1
            else:
                student_dict[_class] = 1
                
        return student_dict

    def get_student_amount_by_section(self, class_str: str) -> dict:
        try:
            data = self.sheet.col_values(2)
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        data = data[data.index("Class-Roll") + 1:]
        data = [i for i in data if i]
        
        filtered_data = []
        for d in data:
            if str(d).split("-")[0] == class_str:
                filtered_data.append(d)
        student_dict = {}
            
        for d in filtered_data:
            _section = str(d).split("-")[1]
            if _section in student_dict:
                student_dict[_section] += 1
            else:
                student_dict[_section] = 1
        return student_dict

    def get_all_students_amount(self) -> int:
        try:
            data = self.sheet.col_values(2)
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        data = data[data.index("Class-Roll") + 1:]
        data = [i for i in data if i]

        return len(data)

    def add_class(self, class_str: str) -> None:
        try:
            f = self.sheet.find("$Class$")
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        value = self.sheet.cell(f.row, f.col + 1).value
        value = value.replace("\"", "")
        if value != '':
            value = value.split(", ")
        else:
            value = []
        value.append(class_str)
        value = [int(val) for val in value]
        value.sort()
        value = [str(val) for val in value]
        value = ", ".join(value)
        self.sheet.update_cell(f.row, f.col + 1, f"\"{value}\"")
    
    def get_all_student_data_by_class_and_section(self, class_str: str) -> dict:
        _class = class_str.split("-")[0]
        _section = class_str.split("-")[1]
        try:
            all_data = self.get_all()
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        all_data = all_data[2:]
        all_data = [i for i in all_data if i]
        all_class_students = []
        for data in all_data:
            if str(data[1]).split("-")[0] == _class and str(data[1]).split("-")[1] == _section:
                all_class_students.append(data)
        all_student_data = {}
        for student in all_class_students:
            student_data = {}
            student_data['studentID'] = student[0]
            student_data['name'] = student[2]
            all_student_data[str(student[1]).split("-")[2]] = student_data
        return all_student_data
    
    def get_student_data(self, position: str) -> dict:
        try:
            f = self.sheet.find(position)
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        data = self.sheet.row_values(f.row)
        student_data = {}
        student_data['studentID'] = data[0]
        student_data['class'] = str(data[1]).split("-")[0]
        student_data['roll'] = str(data[1]).split("-")[1]
        student_data['name'] = data[2]
        student_data['dob'] = data[3]
        student_data['fathersName'] = data[4]
        student_data['fathersPhone'] = str(data[5]).replace("\"", '')
        student_data['mothersName'] = data[6]
        student_data['mothersPhone'] = str(data[7]).replace("\"", '')
        student_data['presentAddress'] = data[8]
        student_data['permanentAddress'] = data[9]

        return data, student_data

    def delete_class(self, class_str: str) -> None:
        try:
            f = self.sheet.find("$Class$")
        except requests.exceptions.ConnectionError:
            if messagebox.showerror("Connection Lost!", "Connection was lost! Please check your Internet Connection and try again!"):
                exit(0)
        value = self.sheet.cell(f.row, f.col + 1).value
        value = value.replace("\"", "")
        if value != None:
            value = value.split(", ")
        value.remove(class_str)
        value = [int(val) for val in value]
        value.sort()
        value = [str(val) for val in value]
        value = ", ".join(value)
        self.sheet.update_cell(f.row, f.col + 1, f"\"{value}\"")
        all_values = self.sheet.col_values(2)
        all_values = all_values[all_values.index("Class-Roll") + 1:]
        all_values = [i for i in all_values if i]
        for value in all_values:
            if str(value).split("-")[0] == class_str:
                _find = self.sheet.find(value)
                self.sheet.delete_rows(_find.row)

    def delete_section(self, section_with_class: str) -> None:
        class_str, section_str = section_with_class.split("-")[0], section_with_class.split("-")[1].lower()
        all_values = self.sheet.col_values(2)
        all_values = all_values[all_values.index("Class-Roll") + 1:]
        all_values = [i for i in all_values if i]
        for value in all_values:
            if str(value).split("-")[0] == class_str and str(value).split("-")[1] == section_str:
                _find = self.sheet.find(value)
                self.sheet.delete_rows(_find.row) 

    def delete_student(self, class_position: str) -> None:
        _find = self.sheet.find(class_position)
        self.sheet.delete_rows(_find.row)
    
    def get_pin(self) -> str:
        _find = self.sheet.find("$Pin$")
        return (self.sheet.cell(_find.row, _find.col + 1).value).replace("\"", '')
    
    def get_rolls(self, class_str: str, section_str: str) -> list:
        all_values = self.sheet.col_values(2)
        all_values = all_values[all_values.index("Class-Roll") + 1:]
        all_values = [i for i in all_values if i]
        roles = []
        for data in all_values:
            _class, _section, _roll = str(data).split("-")
            if _class.lower() == class_str.lower() and _section.lower() == section_str.lower():
                roles.append(int(_roll))
        roles.sort()
        return roles

    def get_all_student_ids(self) -> list:
        all_ids = self.sheet.col_values(1)
        all_ids = all_ids[all_ids.index("Student ID") + 1:]
        all_ids = [int(i) for i in all_ids if i]
        all_ids.sort()
        return all_ids

    def get_classes_have_data(self) -> list:
        all_values = self.sheet.col_values(2)
        all_values = all_values[all_values.index("Class-Roll") + 1:]
        all_values = [i for i in all_values if i]
        classes = []
        for data in all_values:
            _class, _, _ = str(data).split("-")
            if int(_class) not in classes:
                classes.append(int(_class))
        classes.sort()
        return classes
    
    def add_student(self, student_id: str, class_section_roll: str, name: str, DoB: str, fathersname: str, fatherscontact: str, mothersname: str, motherscontact: str, presentaddress: str, permanentaddress: str) -> None:
        data = [student_id, class_section_roll, name, DoB, fathersname, fatherscontact, mothersname, motherscontact, presentaddress, permanentaddress]
        gclass, gsection, groll = str(class_section_roll).split("-")
        classes_have_data = self.get_classes_have_data()
        if classes_have_data:
            if int(gclass) in classes_have_data:
                sections = self.get_all_sections(gclass)
                if str(gsection).lower() in sections:
                    rolls = self.get_rolls(gclass, str(gsection).lower())
                    last_roll = 0
                    for roll in rolls:
                        if roll < int(groll):
                            last_roll = roll
                    if last_roll == 0:
                        _rolls = rolls.copy()
                        _rolls.append(int(groll))
                        _rolls.sort()
                        next_roll = _rolls[_rolls.index(int(groll)) + 1]                        
                        _find = self.sheet.find(f"{gclass}-{gsection}-{next_roll}")
                        self.sheet.insert_row(data, _find.row)
                    else:
                        _find = self.sheet.find(f"{gclass}-{gsection}-{last_roll}")
                        self.sheet.insert_row(data, _find.row + 1)
                else:
                    sections.append(gsection)
                    sections.sort()
                    last_section = ""
                    if sections.index(gsection) != 0:
                        last_section = sections[sections.index(gsection) - 1]
                        last_roll = self.get_rolls(gclass, last_section)[-1]
                        _find = self.sheet.find(f"{gclass}-{last_section}-{last_roll}")
                        self.sheet.insert_row(data, _find.row + 1)
                    else:
                        next_section = sections[sections.index(gsection)+1]
                        first_roll = self.get_rolls(gclass, next_section)[0]
                        print(gclass, next_section, first_roll)
                        _find = self.sheet.find(f"{gclass}-{next_section}-{first_roll}")
                        self.sheet.insert_row(data, _find.row)
            else:
                classes_have_data.append(int(gclass))
                classes_have_data.sort()
                if classes_have_data.index(int(gclass)) != 0:
                    last_class = classes_have_data[classes_have_data.index(int(gclass)) - 1]
                    last_section = self.get_all_sections(str(last_class))[-1]
                    last_roll = self.get_rolls(str(last_class), str(last_section))[-1]
                    _find = self.sheet.find(f"{last_class}-{last_section}-{last_roll}")
                    self.sheet.insert_row(data, _find.row + 1)
                else:
                    next_class = classes_have_data[classes_have_data.index(int(gclass)) + 1]
                    first_section = self.get_all_sections(str(next_class))[0]
                    first_roll = self.get_rolls(str(next_class), first_section)[0]
                    _find = self.sheet.find(f"{next_class}-{first_section}-{first_roll}")
                    self.sheet.insert_row(data, _find.row)
        else:
            self.sheet.append_row(data)
    
    def update_student(self, data) -> None:
        class_section_roll = data[1]
        _find = self.sheet.find(class_section_roll)
        self.sheet.delete_rows(_find.row)
        self.sheet.insert_row(data, _find.row)
    
    def change_pin(self, new_pin) -> None:
        pE = ""
        for c in new_pin:
            pE += chr(ord(c) + 5)
        _find = self.sheet.find("$Pin$")
        self.sheet.update_cell(_find.row, _find.col + 1, pE)


def splash():
    global istypewrite

    istypewrite = True

    def typewrite(obj: ctk.CTkLabel):
        global istypewrite

        while istypewrite:
            currentText = obj.cget("text")
            if "Getting things ready" in currentText:
                if "..." in currentText:
                    obj.configure(text=currentText.replace("...", ""))
                else:
                    obj.configure(text=f"{currentText}.")
            time.sleep(1)

    win = ctk.CTk()
    win.wm_overrideredirect(True)
    win.wm_iconbitmap(f"{assetsPath}/Icon.ico")
    win.title("Rotary School Student Manager")
    positionRight = int(win.winfo_screenwidth()/2 - 650/2)
    positionDown = int(win.winfo_screenheight()/2 - 400/2)
    win.geometry(f"650x400+{positionRight}+{positionDown-50}")

    pinFrame = ctk.CTkFrame(win, height=100, width=400, border_width=0, fg_color="transparent")
    pinFrame.pack(anchor="center", side="bottom", pady=40)
    pinFrame.pack_propagate(False)
    loadingLabel = ctk.CTkLabel(pinFrame, text="Getting things ready", font=("Segoe UI", 15, "bold", "italic"))
    loadingLabel.pack(anchor="center", side="bottom", pady=0)
    mainLabel = ctk.CTkLabel(win, text="Rotary School Student Manager", font=("Segoe UI", 25, "bold"), justify="left")
    mainLabel.pack(anchor="center", side="bottom")
    logo = ctk.CTkLabel(win, text="", image=ctk.CTkImage(Image.open(os.path.join(assetsPath, "Logo Dark.png")), Image.open(os.path.join(assetsPath, "Logo Light.png")), (150, 150)))
    logo.place(x=245, y=30)

    threading.Thread(target=typewrite, args=(loadingLabel, ), daemon=True).start()
    win.after(1500, lambda: dbloadWin(win))
    win.after(150, win.focus_force)
    win.mainloop()


def ReportErrorSequence(win: ctk.CTk, url: str):
    if messagebox.askyesno("Unexpected Error Raised!", "Rotary School Student Manager Software just hit an unexected error!\nWould you like to report it to the Developer, so that it can be solved as quickly as possible?"):
        webbrowser.open(url)

def dbloadWin(window):
    window.destroy()

    global istypewrite

    istypewrite = True

    def move_to_main():
        global istypewrite

        istypewrite = False
        win.overrideredirect(False)
        win.after(0, lambda: main(win))
    
    def typewrite(obj: ctk.CTkLabel):
        global istypewrite

        while istypewrite:
            currentText = obj.cget("text")
            if "Loading Database" in currentText:
                if "..." in currentText:
                    obj.configure(text=currentText.replace("...", ""))
                else:
                    obj.configure(text=f"{currentText}.")
            elif "Retrying in" in currentText:
                sec = int(re.search(r'\d+', currentText).group())
                if sec != 1:
                    obj.configure(text=currentText.replace(str(sec), str(sec - 1)))
                else:
                    obj.configure(text="Retrying to load Database...")
                    load_database()
            time.sleep(1)

    
    def move_to_pin():
        win.attributes("-topmost", 1)
        win.focus_force()
        global istypewrite

        def validate_entry(text, obj):
            if text == "" or text.isdigit():
                if len(text) > 1:
                    return False
                else:
                    currentIndex = pin_entries.index(obj)
                    if text != "":
                        if currentIndex == len(pin_entries) - 1:
                            threading.Thread(target=is_pin_match(str(text)), daemon=True).start()
                            win.focus_force()
                            return True
                        else:
                            pin_entries[currentIndex + 1].configure(state="normal")
                            pin_entries[currentIndex + 1].focus_force()
                    else:
                        if currentIndex != 0:
                            pin_entries[currentIndex].configure(state="disabled")
                            pin_entries[currentIndex - 1].focus_force()
                    return True
            else:
                return False
            
        def gen_pin_entries(bcolor: tuple = ("#979DA2", "#565B5E")):
            pin_entries.clear()
            last_x_pos = 0
            for i in range(1, 6):
                e = ctk.CTkEntry(pinFrame, width=30, height=35, font=("Consolas", 18), border_width=2, justify="center", border_color=bcolor)
                if i != 1:
                    e.configure(state="disabled")
                if i == 1:
                    e.focus_force()
                e.configure(validate="key", validatecommand=(win.register(lambda text, obj=e: validate_entry(text, obj)), "%P"))
                last_x_pos = i * 25
                e.place(x=last_x_pos + i * 45, y=25)
                pin_entries.append(e)
        
            
        def is_pin_match(last_int: str):
            pO = database.get_pin()
            pE = [e.get() for e in pinFrame.winfo_children()]
            pE.insert(-1, last_int)
            pE = ''.join([e for e in pE if e])
            pEE = ""
            for c in pE:
                pEE += chr(ord(c) + 5)
            if pO == pEE:
                for e in pinFrame.winfo_children():
                    e.configure(border_color=("#90ee90", "#154734"))
                move_to_main()
            else:
                for e in pinFrame.winfo_children():
                    e.destroy()
                win.bell()
                threading.Thread(target=gen_pin_entries, args=(("#FF0000", "#8B0000"), ), daemon=True).start()
        
        istypewrite = False
        win.resizable(0, 0)
        win.overrideredirect(False)
        loadingLabel.configure(text="")
        loadingLabel.destroy()
        pin_entries = []
        threading.Thread(target=gen_pin_entries, daemon=True).start()

    def load_database():
        global database, istypewrite
        
        done = False
        try:
            database = Database()
            done = True
        except (google.auth.exceptions.TransportError, requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) as e:
            loadingLabel.configure(text=f"Loading Failed, No Internet Connection! Retrying in 5")
        except google.auth.exceptions.RefreshError:
            loadingLabel.configure(text=f"Loading Failed, Computer time is incorrect! Retrying in 5")
        except (gspread.exceptions.WorksheetNotFound, gspread.exceptions.SpreadsheetNotFound):
            loadingLabel.configure(text=f"Database not found!")
            istypewrite = False
        except gspread.exceptions.GSpreadException as e:
            istypewrite = False
            win.bell()
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            url = f"mailto:tahsin.ict@outlook.com?subject=Unexpected Error on Rotary School Student Manager&body=\nError Information:\n```\nType: {e_type}\nFile: {e_filename}\nLine: {e_line_number}\nMessage: {e_message}\n```\n\nRedirected from Rotary School Student Manager Software"
            ReportErrorSequence(win, url)
        except pyasn1.error.PyAsn1Error:
            loadingLabel.configure(text=f"Database Credentials Error!")
            if messagebox.askyesno("Credentials Error", "Credentials error usually raised when the  Database credentials are not correct! Please contact with the Developer!\nDo you want to send him Mail?"):
                webbrowser.open("mailto:tahsin.ict@outlook.com?subject=Credendials Error on Rotary School Student Manager&body=%0A%0ARedirected from Rotary School Student Manager Software")
            istypewrite = False
        except Exception as e:
            istypewrite = False
            win.bell()
            e_type, e_object, e_traceback = sys.exc_info()
            e_filename = os.path.split(
                e_traceback.tb_frame.f_code.co_filename
            )[1]
            e_message = str(e)
            e_line_number = e_traceback.tb_lineno
            url = f"mailto:tahsin.ict@outlook.com?subject=Unexpected Error on Rotary School Student Manager&body=\nError Information:\n```\nType: {e_type}\nFile: {e_filename}\nLine: {e_line_number}\nMessage: {e_message}\n```\n\nRedirected from Rotary School Student Manager Software"
            ReportErrorSequence(win, url)
        if done:
            move_to_pin()


    win = ctk.CTk()
    win.wm_iconbitmap(f"{assetsPath}/Icon.ico")
    win.title("Rotary School Student Manager")
    positionRight = int(win.winfo_screenwidth()/2 - 650/2)
    positionDown = int(win.winfo_screenheight()/2 - 400/2)
    win.geometry(f"650x400+{positionRight}+{positionDown-50}")

    aboutLabel = ctk.CTkLabel(win, text="Developer", font=("Consolas", 12))
    aboutLabel.pack(anchor="e", side="bottom", padx=10)        
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())
    pinFrame = ctk.CTkFrame(win, height=100, width=450, border_width=0, fg_color="transparent")
    pinFrame.pack(anchor="center", side="bottom", pady=25)
    pinFrame.pack_propagate(False)
    loadingLabel = ctk.CTkLabel(pinFrame, text="Loading Database", font=("Segoe UI", 15, "bold", "italic"))
    loadingLabel.pack(anchor="center", side="bottom", pady=0)
    mainLabel = ctk.CTkLabel(win, text="Rotary School Student Manager", font=("Segoe UI", 25, "bold"), justify="left")
    mainLabel.pack(anchor="center", side="bottom")
    logo = ctk.CTkLabel(win, text="", image=ctk.CTkImage(Image.open(os.path.join(assetsPath, "Logo Dark.png")), Image.open(os.path.join(assetsPath, "Logo Light.png")), (150, 150)))
    logo.place(x=245, y=30)

    threading.Thread(target=typewrite, args=(loadingLabel, ), daemon=True).start()
    threading.Thread(target=load_database, daemon=True).start()
    win.focus_force()
    win.mainloop()

def about():
    root = ctk.CTkToplevel()
    root.geometry(f"650x400")
    root.title("Rotary School Student Manager")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")

    aboutLabel = ctk.CTkLabel(root, text=f"About", font=("Segoe UI", 30, 'bold'))
    aboutLabel.place(x=10, y=10)
    descriptionLabel = ctk.CTkLabel(root, text="Rotary School Student Manager is a Software made for Rotary School Khulna for organizing the Student Information in a Digital Way!", font=("Segoe UI", 13), wraplength=600, justify="left")
    descriptionLabel.place(x=10, y=60)
    sourceLabel = ctk.CTkLabel(root, text=f"Software Source Code is available at: ", font=("Seoge UI", 12, "bold"))
    sourceLabel.place(x=10, y=100)
    sourceHyperLabel = ctk.CTkLabel(root, text="GitHub: Sayad-Uddin-Tahsin/Rotary-School-Student-Manager", font=("Seoge UI", 12, "underline"), text_color="#0078D7")
    sourceHyperLabel.place(x=225, y=100)
    sourceHyperLabel.bind("<Enter>", lambda e: sourceHyperLabel.configure(cursor="hand2"))
    sourceHyperLabel.bind("<Leave>", lambda e: sourceHyperLabel.configure(cursor=""))
    sourceHyperLabel.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Sayad-Uddin-Tahsin/Rotary-School-Student-Manager"))

    devFrame = ctk.CTkFrame(root, width=450, height=200, corner_radius=6, border_width=1, fg_color="transparent")
    devFrame.place(x=100, y=140)
    imageLabel = ctk.CTkLabel(devFrame, text="", image=ctk.CTkImage(Image.open(os.path.join(assetsPath, "Tahsin.png")), Image.open(os.path.join(assetsPath, "Tahsin.png")), (50, 50)))
    imageLabel.place(x=30, y=10)
    ctk.CTkLabel(devFrame, text="Mohammad Sayad Uddin Tahsin", font=("Arial Black", 18, "bold")).place(x=90, y=10)
    ctk.CTkLabel(devFrame, text="Developer of Rotary School Student Manager", font=("Segoe UI", 14, 'bold')).place(x=90, y=35)
    text = """
This is Sayad Uddin Tahsin, a student of class 8 (2023) of Rotary School, Khulna. I have a passion for software development and technology. This software is a product of my dedication and interest in creating solutions through code. \nI hope you find it useful and enjoy using it.
"""
    ctk.CTkLabel(devFrame, text=text, font=("Segoe UI", 13), wraplength=450, justify="left").place(x=10, y=60)
    ctk.CTkLabel(devFrame, text="For any query, please reach me at:", font=("Segoe UI", 13)).place(x=10, y=165)
    mailLabel = ctk.CTkLabel(devFrame, text="Email", font=("Segoe UI", 13, 'underline'), text_color="#0078D7")
    mailLabel.place(x=215, y=165)
    mailLabel.bind("<Enter>", lambda e: mailLabel.configure(cursor="hand2"))
    mailLabel.bind("<Leave>", lambda e: mailLabel.configure(cursor=""))
    mailLabel.bind("<Button-1>", lambda e: webbrowser.open("mailto:tahsin.ict@outlook.com?subject=Query about Rotary School Student Manager&body=\n\n\nRedirected from Rotary School Student Manager Software"))

    versionLabel = ctk.CTkLabel(root, text=f"Rotary School Student Manager v1.0 is running on your computer.", font=("Seoge UI", 15, "bold"))
    versionLabel.place(x=10, y=360)
    root.after(100, root.lift)
    root.mainloop()

def main(backWindow: ctk.CTk=None):
    global classes, newClassOpen, settingsOpen

    newClassOpen = None
    settingsOpen = None

    def settingsWin():
        global settingsOpen, pinok, cpinok

        def on_closing():
            global settingsOpen

            settingsOpen = None
            root.destroy()

        def initiate_appearence_mode(mode: str):
            if mode == "system":
                if darkdetect.theme() == "Dark":
                    ctk.set_appearance_mode("dark")
                else:
                    ctk.set_appearance_mode("light")
                edit_data("appearence_mode", "system")    
            if mode == "light":
                edit_data("appearence_mode", "light")
            if mode == "dark":
                edit_data("appearence_mode", "dark")
            ctk.set_appearance_mode(mode)

        def initiate_color_theme(color: str):
            if color == "blue":
                edit_data("color_theme", "blue")
            if color == "dark-blue":
                edit_data("color_theme", "dark-blue")
            if color == "green":
                edit_data("color_theme", "green")
            ctk.set_default_color_theme(color)
            ctk.CTkLabel(frameTA, text="* Restart may require for update", font=("Segoe UI", 11, "italic")).place(x=115, y=115)
        
        pinok = False
        cpinok = False
        def validate_pin(text):
            if text == "" or text.isdigit():
                if len(text) > 5:
                    return False
                return True
            else:
                return False
        
        def validate_pin_length(obj, text):
            global pinok

            if len(text) != 5:
                obj.configure(border_color=("#de0202", "#8B0000"))
                pinok = False
            else:
                obj.configure(border_color=("#979DA2", "#565B5E"))
                pinok = True
        
        def changePIN():
            if not pinok:
                if messagebox.showerror("PIN Length Error", "PIN must be 5 in length!"):
                    root.focus_force()
                return
            if not cpinok:
                if messagebox.showerror("Confirm PIN Mismatch", "PIN provided in \"New PIN\" & \"Confirm New PIN\" didn't match!"):
                    root.focus_force()
                return        
            pin = database.get_pin()
            current_pin = CpinEntry.get()
            pEE = ""
            for c in current_pin:
                pEE += chr(ord(c) + 5)
            if str(pin) == str(pEE):
                if str(current_pin) == str(NpinEntry.get()):
                    if messagebox.showerror("New PIN Error", "New PIN can't be as same as the current PIN!"):
                        root.focus_force()
                    return
                if messagebox.askyesnocancel("Are you sure?", "Are you sure you want to change the PIN? Once you've changed the PIN you WON'T be able to ACCESS this Software with the PREVIOUS PIN!"):
                    database.change_pin(NpinEntry.get())
                    CpinEntry.delete("0", "end")
                    NpinEntry.delete("0", "end")
                    CNpinEntry.delete("0", "end")
                    CpinEntry.configure(placeholder_text="Enter Current PIN")
                    NpinEntry.configure(placeholder_text="Enter 5 Digit New PIN")
                    CNpinEntry.configure(placeholder_text="New 5 Digit PIN Again")
                    if messagebox.showinfo("PIN Changed", "Software Access PIN is successfully changed!"):
                        root.focus_force()
                        time.sleep(0.5)
                        on_closing()
                else:
                    root.focus_force()
            else:
                if messagebox.showerror("Current PIN Mismatch", "Current PIN provided is not Correct! Please try again with the actual one!"):
                    root.focus_force()            

        def confirmPINmatch(npin, cnpin):
            global cpinok

            if str(cnpin) == str(npin):
                CNpinEntry.configure(border_color=("#979DA2", "#565B5E"))
                cpinok = True
            else:
                cpinok = False
                CNpinEntry.configure(border_color=("#de0202", "#8B0000"))
    
        root = ctk.CTk()
        positionRight = int(root.winfo_screenwidth()/2 - 590/2)
        positionDown = int(root.winfo_screenheight()/2 - 300/2)
        root.geometry(f"590x300+{positionRight}+{positionDown-50}")
        root.title(f"Settings")
        root.resizable(0, 0)
        root.wm_iconbitmap(f"{assetsPath}/Icon.ico")
        settingsOpen = root
        root.protocol("WM_DELETE_WINDOW", on_closing)

        aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
        aboutLabel.pack(anchor="se", side="bottom", padx=10)
        aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
        aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
        aboutLabel.bind("<Button-1>", lambda e: about())

        classTitle = ctk.CTkLabel(root, text=f"Settings", font=("Segoe UI", 30, 'bold'))
        classTitle.pack(padx=10, pady=10, anchor="nw", side="left")

        frameTA = ctk.CTkFrame(root, width=280, height=200, fg_color="transparent", border_width=2)
        frameTA.place(x=10, y=70)
        frameTA.pack_propagate(0)
        frameTALabel = ctk.CTkLabel(root, text="Appearance and Theme", font=("Segoe UI", 14, 'bold'), padx=4)
        frameTALabel.place(x=15, y=55)
        serverModeLabel = ctk.CTkLabel(frameTA, text="Appearance Mode", font=("Segoe UI", 13, "bold"))
        serverModeLabel.place(x=12, y=6)
        serverintVarMode = ctk.IntVar(value=["system", "light", "dark"].index(appearence_mode))
        serverRadiobuttonSystem = ctk.CTkRadioButton(master=frameTA, text="System", variable=serverintVarMode, value=0, command=lambda: initiate_appearence_mode("system"))
        serverRadiobuttonSystem.place(x=12, y=36)
        serverRadiobuttonLight = ctk.CTkRadioButton(master=frameTA, text="Light", variable=serverintVarMode, value=1, command=lambda: initiate_appearence_mode("light"))
        serverRadiobuttonLight.place(x=100, y=36)
        serverRadiobuttonDark = ctk.CTkRadioButton(master=frameTA, text="Dark", variable=serverintVarMode, value=2, command=lambda: initiate_appearence_mode("dark"))
        serverRadiobuttonDark.place(x=170, y=36)

        serverColorLabel = ctk.CTkLabel(frameTA, text="Color Theme", font=("Segoe UI", 13, "bold"))
        serverColorLabel.place(x=12, y=60)
        serverintVarColor = ctk.IntVar(value=["blue", "dark-blue", "green"].index(color_theme))
        serverRadiobuttonBlue = ctk.CTkRadioButton(master=frameTA, text="Blue", variable=serverintVarColor, value=0, command=lambda: initiate_color_theme("blue"))
        serverRadiobuttonBlue.place(x=12, y=90)
        serverRadiobuttonDarkBlue = ctk.CTkRadioButton(master=frameTA, text="Dark Blue", variable=serverintVarColor, value=1, command=lambda: initiate_color_theme("dark-blue"))
        serverRadiobuttonDarkBlue.place(x=75, y=90)
        serverRadiobuttonGreen = ctk.CTkRadioButton(master=frameTA, text="Green", variable=serverintVarColor, value=2, command=lambda: initiate_color_theme("green"))
        serverRadiobuttonGreen.place(x=170, y=90)

        framePIN = ctk.CTkFrame(root, width=280, height=200, fg_color="transparent", border_width=2)
        framePIN.place(x=300, y=70)
        framePIN.pack_propagate(0)
        framePINLabel = ctk.CTkLabel(root, text="Change PIN", font=("Segoe UI", 14, 'bold'), padx=4)
        framePINLabel.place(x=305, y=55)
    
        CPINLabel = ctk.CTkLabel(framePIN, text="Current PIN", font=("Segoe UI", 13, "bold"))
        CPINLabel.place(x=12, y=6)
        CpinEntry = ctk.CTkEntry(framePIN, placeholder_text="Enter Current PIN", font=("Consolas", 13), height=26, width=160)
        CpinEntry.configure(validate="key", validatecommand=(root.register(validate_pin), "%P"))
        CpinEntry.place(x=12, y=30)
        CpinEntry.bind("<KeyRelease>", lambda e: validate_pin_length(CpinEntry, CpinEntry.get()))
        
        NPINLabel = ctk.CTkLabel(framePIN, text="New PIN", font=("Segoe UI", 13, "bold"))
        NPINLabel.place(x=12, y=60)
        NpinEntry = ctk.CTkEntry(framePIN, placeholder_text="Enter 5 Digit New PIN", font=("Consolas", 13), height=26, width=160)
        NpinEntry.configure(validate="key", validatecommand=(root.register(validate_pin), "%P"))
        NpinEntry.place(x=12, y=84)
        NpinEntry.bind("<KeyRelease>", lambda e: validate_pin_length(NpinEntry, NpinEntry.get()))
            
        CNPINLabel = ctk.CTkLabel(framePIN, text="Confirm New PIN", font=("Segoe UI", 13, "bold"))
        CNPINLabel.place(x=12, y=114)
        CNpinEntry = ctk.CTkEntry(framePIN, placeholder_text="New 5 Digit PIN Again", font=("Consolas", 13), height=26, width=160)
        CNpinEntry.configure(validate="key", validatecommand=(root.register(validate_pin), "%P"))
        CNpinEntry.place(x=12, y=138)
        CNpinEntry.bind("<FocusIn>", lambda e: CNpinEntry.configure(border_color=("#de0202", "#8B0000")))
        CNpinEntry.bind("<KeyRelease>", lambda e: validate_pin_length(CNpinEntry, CNpinEntry.get()))
        CNpinEntry.bind("<KeyRelease>", lambda e: confirmPINmatch(NpinEntry.get(), CNpinEntry.get()))

        SavePINbtn = ctk.CTkButton(framePIN, width=100, height=25, text="Change PIN", font=("Seoge UI", 13), command=changePIN)
        SavePINbtn.pack(anchor="se", side="bottom", padx=12, pady=3)
        
        root.mainloop()

    def update_class_list(scrollableFrame: ctk.CTkScrollableFrame, classes: list):
        if not classes:
            ctk.CTkLabel(scrollableFrame, text="No class was assigned!", font=("Segoe UI", 13, "bold")).pack(anchor="center")
        else:
            totalStudentsDict = database.get_student_amount_by_class()
            for c in classes:
                try:
                    frame = ctk.CTkFrame(scrollableFrame, border_width=1, height=60)
                    ctk.CTkLabel(frame, text=f"Total Students: {totalStudentsDict[c] if c in totalStudentsDict else 0}", font=("Consolas", 12)).place(x=10, y=2)
                    classLabel = ctk.CTkLabel(frame, text=f"Class: {c}", font=("Segoe UI", 22, "bold"))
                    classLabel.place(x=10, y=25)
                    frame.pack(padx=10, pady=2, fill='x', side="top")

                    def enter(event):
                        event.widget.configure(cursor="hand2")

                    def leave(event):
                        event.widget.configure(cursor="")

                    def on_frame_click(class_str):
                        sectionWindow(root, class_str)

                    for widget in frame.winfo_children():
                        widget.bind("<Enter>", enter)
                        widget.bind("<Leave>", leave)
                        widget.bind("<Button-1>", lambda e, label=str(classLabel.cget("text")).split(": ")[1]: on_frame_click(label))

                    frame.bind("<Enter>", enter)
                    frame.bind("<Leave>", leave)
                    frame.bind("<Button-1>", lambda e, label=str(classLabel.cget("text")).split(": ")[1]: on_frame_click(label))

                except _tkinter.TclError:
                    pass
            threading.Thread(target=build_info_frame, args=(infoFrame, ), daemon=True).start()

    def add_class():
        global classes, newClassOpen
        def handle_save_click():
            global classes

            database.add_class(ClassIntEntry.get())
            ClassIntEntry.delete("0", "end")
            for widget in scrollableFrame.winfo_children():
                widget.destroy()
            classes = database.get_classes()
            threading.Thread(target=update_class_list, args=(scrollableFrame, classes, ), daemon=True).start()
            on_closing()


        def validate_entry(text):
            if len(text) > 2:
                return False
            if text.isdigit() or text == "":
                if text == "":
                    error.configure(text="")
                    error.place(x=280, y=40)
                    save_button.configure(state='normal')
                    save_button.place(y=43)
                    ClassIntEntry.configure(border_color=('#979DA2', '#565B5E'))
                    return True
                else:
                    if text != "" and str(text) in classes:
                        error.configure(text=f"* Class {int(text)} already exists! ",
                                    font=("Segoe UI", 12, 'italic'),
                                    text_color="red")
                        error.place(x=190, y=40)
                        ClassIntEntry.configure(border_color=("#FF0000", "#8B0000"))
                        save_button.configure(state='disabled')
                        save_button.place(y=65)
                        return True
                    else:
                        error.configure(text="")
                        error.place(x=280, y=40)
                        save_button.configure(state='normal')
                        save_button.place(y=43)
                        ClassIntEntry.configure(border_color=('#979DA2', '#565B5E'))
                        return True
            elif not text.isdigit():
                error.configure(text="* Class must be a number! Ex. 9 ", font=("Segoe UI", 12, 'italic'),
                            text_color="red")
                error.place(x=145, y=40)
                save_button.place(y=65)
                save_button.configure(state='disabled')
                ClassIntEntry.configure(border_color=("#FF0000", "#8B0000"))
                return False
            else:
                pass
        
        def on_closing():
            global newClassOpen
            newClassOpen = None
            addClassWin.destroy()
        
        addClassWin = ctk.CTk()
        positionRight = int(addClassWin.winfo_screenwidth()/2 - 400/2)
        positionDown = int(addClassWin.winfo_screenheight()/2 - 130/2)
        addClassWin.geometry(f"400x130+{positionRight}+{positionDown-50}")
        addClassWin.title("Rotary School Student Manager")
        addClassWin.resizable(0, 0)
        addClassWin.wm_iconbitmap(f"{assetsPath}/Icon.ico")
        addClassWin.protocol("WM_DELETE_WINDOW", on_closing)
        newClassOpen = addClassWin

        aboutLabel = ctk.CTkLabel(addClassWin, text="Rotary School Student Manager", font=("Consolas", 12))
        aboutLabel.pack(anchor="se", side="bottom", padx=10)

        ClassIntLabel = ctk.CTkLabel(addClassWin, text="Enter Class Integer:", font=("Seoge UI", 16, "bold"))
        ClassIntLabel.place(x=15, y=15)
        ClassIntEntry = ctk.CTkEntry(addClassWin, placeholder_text="8", font=("Seoge UI", 13), height=22)
        ClassIntEntry.configure(validate="key", validatecommand=(addClassWin.register(validate_entry), "%P"))
        ClassIntEntry.place(x=175, y=18)
        error = ctk.CTkLabel(addClassWin, text="", font=("Seoge UI", 8, "bold"), text_color=("#FF0000", "#8B0000"))
        error.place(x=15, y=15)
        save_button = ctk.CTkButton(addClassWin, text="Save", font=("Segoe UI", 13), width=50, height=25, command=handle_save_click)
        save_button.place(x=265, y=43)
        ClassIntEntry.bind("<Return>", lambda e: handle_save_click() if save_button.cget("state") == "normal" else None)

        addClassWin.mainloop()

    def build_info_frame(infoFrame: ctk.CTkFrame):
        if len(infoFrame.winfo_children()) != 0:
            for widget in infoFrame.winfo_children():
                widget.destroy()
        ctk.CTkLabel(infoFrame, text="Information", fg_color=('gray78', 'gray23'), font=("Segoe UI", 16, 'bold'), corner_radius=infoFrame.cget("corner_radius")).pack(padx=6, pady=6, fill="x")
        ctk.CTkLabel(infoFrame, text=f"Total Students: {database.get_all_students_amount()}", font=("Consolas", 13)).place(x=6, y=40)
        ctk.CTkLabel(infoFrame, text=f"Class Assigned: {len(classes)}", font=("Consolas", 13)).place(x=6, y=60)

    def on_closing():
        root.quit()
        for widget in root.winfo_children():
            widget.destroy()
        if newClassOpen is not None:
            newClassOpen.destroy()
        if settingsOpen is not None:
            settingsOpen.destroy()
        root.destroy()
    
    if backWindow is None:
        root = ctk.CTk()
    else:
        backWindow.destroy()
        root = ctk.CTk()
        for widget in root.winfo_children():
            widget.destroy()
    
    positionRight = int(root.winfo_screenwidth()/2 - 650/2)
    positionDown = int(root.winfo_screenheight()/2 - 400/2)
    root.geometry(f"650x400+{positionRight}+{positionDown-50}")
    root.title("Rotary School Student Manager")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")
    root.protocol("WM_DELETE_WINDOW", on_closing)


    aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
    aboutLabel.pack(anchor="e", side="bottom", padx=10)        
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())
    settingsLabel = ctk.CTkLabel(root, text="Settings", font=("Consolas", 12))
    settingsLabel.pack(anchor="e", side="bottom", padx=10)
    settingsLabel.bind("<Enter>", lambda e: settingsLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    settingsLabel.bind("<Leave>", lambda e: settingsLabel.configure(cursor="", font=("Consolas", 12)))
    settingsLabel.bind("<Button-1>", lambda e: settingsWin() if settingsOpen is None else [settingsOpen.focus_force(), settingsOpen.deiconify()])
    logoLabel = ctk.CTkLabel(root, text="", image=ctk.CTkImage(Image.open(os.path.join(assetsPath, "Logo Dark.png")), Image.open(os.path.join(assetsPath, "Logo Light.png")), (90, 90)))
    logoLabel.place(x=110)
    titleLabel1 = ctk.CTkLabel(root, text=" Rotary School, Khulna", font=("Arial Black", 30, "bold"))
    titleLabel1.pack(anchor="e", padx=80, pady=10)
    titleLabel2 = ctk.CTkLabel(root, text="Student Management", font=("Arial Black", 18, "bold"))
    titleLabel2.place(x=207, y=50)

    scrollableFrame = ctk.CTkScrollableFrame(root, width=350, height=200, label_text="Classes", label_font=("Segoe UI", 16, "bold"))
    scrollableFrame.place(x=10, y=130)
    
    classes = database.get_classes()
    addClassButton = ctk.CTkButton(root, text="Assign Class", corner_radius=6, font=("Segoe UI", 12), width=80)
    addClassButton.place(x=300, y=100)
    addClassButton.bind("<Button-1>", lambda e: add_class() if newClassOpen is None else [newClassOpen.focus_force(), newClassOpen.deiconify()])
    threading.Thread(target=update_class_list, args=(scrollableFrame, classes, ), daemon=True).start()

    infoFrame = ctk.CTkFrame(root, width=230, corner_radius=6)
    infoFrame.place(x=410, y=130)
    infoFrame.pack_propagate(0)
    threading.Thread(target=build_info_frame, args=(infoFrame, ), daemon=True).start()

    root.mainloop()

def assignStudentWindow(window: ctk.CTk, class_str: str, data: list = None):
    global studentIDok, rollok, dobok
    
    studentIDok = False
    rollok = False
    dobok = False
    def validate_name(text):
        if len(text) > 30:
            return False
        else:
            return True
    
    def validate_student_id(text):
        if text.isdigit() or text in ["", "Enter the Student ID"]:
            return True
        else:
            return False
        
    def fill_student_id():
        ids = database.get_all_student_ids()
        if ids:
            idEntry.insert(0, ids[-1] + 1)
    
    def check_if_student_id_exists(text):
        global studentIDok
        
        student_ids = database.get_all_student_ids()
        if int(text) in student_ids:
            idEntry.configure(border_color=("#FF0000", "#8B0000"))
            studentIDok = False
        else:
            idEntry.configure(border_color=("#979DA2", "#565B5E"))
            studentIDok = True
    
    def rollEntryValidator(text):
        global rollok

        rolls = database.get_rolls(class_str, str(sectionCombobox.get()).lower())
        if int(text) in rolls:
            rollEntry.configure(border_color=("#FF0000", "#8B0000"))
            rollok = False
        else:
            rollEntry.configure(border_color=("#979DA2", "#565B5E"))
            rollok = True

    def DOBValidator(text):
        if text.isdigit() or text == "" or "/" in text:
            return True
        else:
            return False
    
    def DOBElementValidator(text):
        global dobok
        if text.count("/") != 2:
            dobEntry.configure(border_color=("#FF0000", "#8B0000"))
            dobok = False
        else:
            dobEntry.configure(border_color=("#979DA2", "#565B5E"))
            dobok = True  
    
    def DOBFormatter(text):
        _day, _month, _year = text.split("/")
        year = int(_year)
        month = int(_month)
        if month > 12:
            month = 12
        if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            daysInMonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        else:
            daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        highest_date = daysInMonth[int(month) - 1]
        if int(_day) > highest_date:
            day = highest_date
        else:
            day = _day
        month = str(month).zfill(2)
        day = str(day).zfill(2)
        dobEntry.delete("0", "end")
        dobEntry.insert(0, f"{day}/{month}/{year}")
    
    def number_validator(text):
        if len(text) > 15:
            return False
        if text == "":
            return True
        if (text.isdigit() if not text.startswith("+") else text[1:].isdigit()):
            return True
        if text[0] == "+" and len(text) == 1:
            return True
        return False


    def address_validator(event):
        content = event.widget.get("0.0", "end")
        if len(content) > 140:
            event.widget.delete("0.0", "end")
            event.widget.insert("0.0", content[:80])
    
    def update_student(old_data: list):
        new_data = [
            idEntry.get(), 
            data[1], 
            nameEntry.get(), 
            dobEntry.get(), 
            fnamevalueEntry.get(), 
            fcontactvalueEntry.get(), 
            mnamevalueEntry.get(),
            mcontactvalueEntry.get(),
            presentAddressEntry.get("0.0", "end").strip(),
            permanentAddressEntry.get("0.0", "end").strip()
        ]
        if new_data != old_data:
            database.update_student(new_data)
        studentWindow(root, data[1])

    def fillAll():
        idEntry.unbind("<FocusOut>")
        idEntry.delete("0", "end")
        idEntry.insert(0, data[0])
        idEntry.bind("<FocusOut>", lambda e: check_if_student_id_exists(int(idEntry.get())) if idEntry.get() not in ["", "Enter the Student ID", str(data[0])] else None)
        dobEntry.insert(0, data[3])
        nameEntry.insert(0, data[2]) 
        classLabel = ctk.CTkLabel(root, text=f"Class: {class_str}", font=("Consolas", 14))
        classLabel.place(x=10, y=100)    
        sectionLabel.configure(text=f"Section: {data[1].split('-')[1].title()}")
        sectionCombobox.place_forget()
        rollLabel.configure(text=f"Roll: {data[1].split('-')[2]}")
        rollEntry.place_forget()
        fnamevalueEntry.insert(0, data[4])
        fcontactvalueEntry.insert(0, data[5])
        mnamevalueEntry.insert(0, data[6])
        mcontactvalueEntry.insert(0, data[7])
        presentAddressEntry.insert("0.0", data[8])
        permanentAddressEntry.insert("0.0", data[9])
        saveStudentButton.configure(text="Update", command=lambda: update_student(data))

    def save_student():
        if messagebox.askyesno("Hold on! ", f"Please give a cross check as you will not able to edit the Section, Roll later!\nDo you want to proceed?"):
            database.add_student(
                idEntry.get(), 
                f"{class_str}-{sectionCombobox.get().lower()}-{rollEntry.get()}", 
                nameEntry.get(), 
                dobEntry.get(), 
                fnamevalueEntry.get(), 
                fcontactvalueEntry.get(), 
                mnamevalueEntry.get(),
                mcontactvalueEntry.get(),
                presentAddressEntry.get("0.0", "end").strip(),
                permanentAddressEntry.get("0.0", "end").strip()
            )
            sectionWindow(root, class_str)

    def sectionComboboxCallback(choice, first: bool = False):
        rollEntry.configure(state="disabled")
        rolls = database.get_rolls(class_str, choice)
        rollEntry.configure(state="normal")
        rollEntry.delete("0", "end")
        if rolls:
            rollEntry.insert(0, rolls[-1] + 1)
        else:
            if first:
                sectionCombobox.set("A")
            rollEntry.insert(0, 1)
    
    def on_closing(isback: bool = False):
        if isback:
            if messagebox.askyesno("Hold On!", "By going back, any information entered here will be DELETED and IRRECOVERABLE!\nAre you sure you want to go back?"):
                studentWindow(root, data[1])
        else:
            if messagebox.askyesno("Hold On!", "By closing, any information entered here will be DELETED and IRRECOVERABLE!\nAre you sure you want to proceed?"):
                root.destroy()

    
    window.destroy()
    root = ctk.CTk()
    root.title(f"Adding Student on class {class_str}")
    positionRight = int(root.winfo_screenwidth()/2 - 650/2)
    positionDown = int(root.winfo_screenheight()/2 - 470/2)
    root.geometry(f"650x470+{positionRight}+{positionDown-50}")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(False))

    aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
    aboutLabel.pack(anchor="se", side="bottom", padx=10)
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())

    saveStudentButton = ctk.CTkButton(root, text="Save", font=("Segoe UI", 13), command=save_student)
    saveStudentButton.pack(anchor="se", pady=2, padx=10, side="right")
    idLabel = ctk.CTkLabel(root, text=f"Student ID:", font=("Consolas", 13, 'bold'))
    idLabel.place(x=10, y=22)
    idEntry = ctk.CTkEntry(root, border_width=1, placeholder_text="Enter the Student ID", font=("Consolas", 12, 'bold'), height=18, width=160, validate="key", validatecommand=(root.register(validate_student_id), "%P"))
    idEntry.place(x=100, y=27)
    idEntry.bind("<FocusOut>", lambda e: check_if_student_id_exists(int(idEntry.get())) if idEntry.get() not in ["", "Enter the Student ID"] else None)
    fill_student_id()
    dobLabel = ctk.CTkLabel(root, text=f"Date of Birth:", font=("Consolas", 13, 'bold'))
    dobLabel.place(x=10, y=45)
    dobEntry = ctk.CTkEntry(root, placeholder_text="DD/MM/YYYY", font=("Consolas", 12, 'bold'), height=18, border_width=1, width=120, validate="key", validatecommand=(root.register(DOBValidator), "%P"))
    dobEntry.place(x=120, y=50)
    dobEntry.bind("<KeyRelease>", lambda e: DOBElementValidator(dobEntry.get()) if dobEntry.get() != "DD/MM/YYYY" else None)
    dobEntry.bind("<FocusOut>", lambda e: DOBFormatter(dobEntry.get()))
    nameLabel = ctk.CTkLabel(root, text="Name:", font=("Segoe UI", 19, 'bold'))
    nameLabel.place(x=10, y=70)
    nameEntry = ctk.CTkEntry(root, placeholder_text="Student Name", font=("Seoge UI", 17, 'bold'), border_width=1, width=300, height=25, validate="key", validatecommand=(root.register(validate_name), "%P"))
    nameEntry.place(x=80, y=73)
    classLabel = ctk.CTkLabel(root, text=f"Class: {class_str}", font=("Consolas", 14))
    classLabel.place(x=10, y=100)
    sectionLabel = ctk.CTkLabel(root, text="Section:", font=("Consolas", 14))
    sectionLabel.place(x=202, y=100)
    sections = [i.title() for i in database.get_all_sections(class_str)]
    sectionCombobox = ctk.CTkComboBox(root, values=sections, width=70, height=20, command=sectionComboboxCallback)
    sectionCombobox.place(x=272, y=105)
    sectionCombobox.bind("<KeyRelease>", lambda e: sectionComboboxCallback(sectionCombobox.get()))
    sectionCombobox.bind("<FocusIn>", lambda e: rollEntry.configure(state="disabled"))
    rollLabel = ctk.CTkLabel(root, text="Roll:", font=("Consolas", 14))
    rollLabel.place(x=418, y=100)
    rollEntry = ctk.CTkEntry(root, width=60, height=18, border_width=1, state="disabled", font=("Consolas", 13))
    rollEntry.place(x=468, y=103)
    rollEntry.bind("<KeyRelease>", lambda e: rollEntryValidator(rollEntry.get()))
    sectionComboboxCallback(sections[0] if sections else [], True)


    # ---------------------------------
    fatherFrame = ctk.CTkFrame(root, width=305, border_width=1, fg_color="transparent", height=130)
    fatherFrame.place(x=10, y=140)
    fatherFrameName = ctk.CTkLabel(root, text=" Father's Information ", font=("Segoe UI", 15, "bold"))
    fatherFrameName.place(x=15, y=125)

    fnameLabel = ctk.CTkLabel(fatherFrame, text="Father's Name", font=("Segoe UI", 14, "bold"))
    fnameLabel.place(x=10, y=10)
    fnamevalueEntry = ctk.CTkEntry(fatherFrame, placeholder_text="Father's Name", font=("Segoe UI", 13), height=23, width=220)
    fnamevalueEntry.place(x=10, y=35)

    fcontactLabel = ctk.CTkLabel(fatherFrame, text="Father's Contact", font=("Segoe UI", 14, "bold"))
    fcontactLabel.place(x=10, y=60)
    fcontactvalueEntry = ctk.CTkEntry(fatherFrame, placeholder_text="Contact Number", font=("Segoe UI", 13), height=23)
    fcontactvalueEntry.place(x=10, y=85)
    fcontactvalueEntry.configure(validate="key", validatecommand=(root.register(number_validator), "%P"))

    # ---------------------------------
    motherFrame = ctk.CTkFrame(root, width=305, border_width=1, fg_color="transparent", height=130)
    motherFrame.place(x=335, y=140)
    motherFrameName = ctk.CTkLabel(root, text=" Mother's Information ", font=("Segoe UI", 15, "bold"))
    motherFrameName.place(x=340, y=125)

    mnameLabel = ctk.CTkLabel(motherFrame, text="Mother's Name", font=("Segoe UI", 14, "bold"))
    mnameLabel.place(x=10, y=10)
    mnamevalueEntry = ctk.CTkEntry(motherFrame, placeholder_text="Mother's Name", font=("Segoe UI", 13), height=23, width=220)
    mnamevalueEntry.place(x=10, y=35)

    mcontactLabel = ctk.CTkLabel(motherFrame, text="Mother's Contact", font=("Segoe UI", 14, "bold"))
    mcontactLabel.place(x=10, y=60)
    mcontactvalueEntry = ctk.CTkEntry(motherFrame, placeholder_text="Contact Number", font=("Segoe UI", 13), height=23)
    mcontactvalueEntry.place(x=10, y=85)
    mcontactvalueEntry.configure(validate="key", validatecommand=(root.register(number_validator), "%P"))

    # ---------------------------------
    presentAddressFrame = ctk.CTkFrame(root, width=302, height=100, border_width=1, fg_color="transparent")
    presentAddressFrame.place(x=10, y=300)
    presentAddressFrameName = ctk.CTkLabel(root, text=" Present Address ", font=("Segoe UI", 15, "bold"))
    presentAddressFrameName.place(x=15, y=285)
    presentAddressEntry = ctk.CTkTextbox(presentAddressFrame, font=("Segoe UI", 13), width=282, height=65, border_width=2, border_color=("#979DA2", "#565B5E"))
    presentAddressEntry.place(x=10, y=15)
    presentAddressEntry.bind("<KeyRelease>", address_validator)

    # ---------------------------------
    permanentAddressFrame = ctk.CTkFrame(root, width=305, height=100, border_width=1, fg_color="transparent")
    permanentAddressFrame.place(x=335, y=300)
    permanentAddressFrameName = ctk.CTkLabel(root, text=" Permanent Address ", font=("Segoe UI", 15, "bold"))
    permanentAddressFrameName.place(x=340, y=285)
    permanentAddressEntry = ctk.CTkTextbox(permanentAddressFrame, font=("Segoe UI", 13), width=282, height=65, border_width=2, border_color=("#979DA2", "#565B5E"))
    permanentAddressEntry.place(x=10, y=15)
    permanentAddressEntry.bind("<KeyRelease>", address_validator)

    backButton = ctk.CTkButton(root, text="🢀", font=("Segoe UI", 13, "bold"), width=28, height=25, command=lambda: on_closing(True))
    backButton.place(x=2, y=2)

    if data != None:
        threading.Thread(target=fillAll, daemon=True).start()

    root.mainloop()

def sectionWindow(window: ctk.CTk, class_str: str=None):
    def load_section_frames(scrollableFrame):
        all_sections = database.get_all_sections(class_str)
        if all_sections == []:
            ctk.CTkLabel(scrollableFrame, text="No section was assigned!", font=("Segoe UI", 13, "bold")).pack(anchor="center")
        else:
            totalStudentsDict = database.get_student_amount_by_section(class_str)
            for section in all_sections:
                try:
                    frame = ctk.CTkFrame(scrollableFrame, border_width=1, height=60)
                    ctk.CTkLabel(frame, text=f"Total Students: {totalStudentsDict[section] if section in totalStudentsDict else 0}", font=("Consolas", 12)).place(x=10, y=2)
                    classLabel = ctk.CTkLabel(frame, text=f"Section: {str(section).title()}", font=("Segoe UI", 22, "bold"))
                    classLabel.place(x=10, y=25)
                    frame.pack(padx=10, pady=2, fill='x', side="top")

                    def enter(event):
                        event.widget.configure(cursor="hand2")

                    def leave(event):
                        event.widget.configure(cursor="")

                    def on_frame_click(class_str, section_str):
                        sectionStudentWindow(root, class_str, section_str)

                    for widget in frame.winfo_children():
                        widget.bind("<Enter>", enter)
                        widget.bind("<Leave>", leave)
                        widget.bind("<Button-1>", lambda e, _class=class_str, _section = str(classLabel.cget("text")).split(": ")[1].lower(): on_frame_click(_class, _section))

                    frame.bind("<Enter>", enter)
                    frame.bind("<Leave>", leave)
                    frame.bind("<Button-1>", lambda e, _class=class_str, _section = str(classLabel.cget("text")).split(": ")[1].lower(): on_frame_click(_class, _section))

                except _tkinter.TclError:
                    pass
    
    def delete_class():
        if messagebox.askyesnocancel("Hold on! ", f"Are you sure you want to remove class {class_str} with all the assigned students and sections?"):
            database.delete_class(class_str)
            messagebox.showinfo("Execution Completed!", f"Class {class_str} has been removed successfully!")
            root.after(1000, lambda: main(root))

    window.destroy()
    root = ctk.CTk()
    positionRight = int(root.winfo_screenwidth()/2 - 650/2)
    positionDown = int(root.winfo_screenheight()/2 - 400/2)
    root.geometry(f"650x400+{positionRight}+{positionDown-50}")
    root.title(f"Viewing Class {class_str}")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")


    aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
    aboutLabel.pack(anchor="se", side="bottom", padx=10)
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())

    classTitle = ctk.CTkLabel(root, text=f"Class {class_str}", font=("Segoe UI", 30, 'bold'))
    classTitle.pack(padx=10, pady=22, anchor="nw", side="left")
    backButton = ctk.CTkButton(root, text="🢀", font=("Segoe UI", 13, "bold"), width=28, height=25, command=lambda: main(root))
    backButton.place(x=2, y=2)

    scrollableFrame = ctk.CTkScrollableFrame(root, height=250, width=610, label_text=f"Sections of Class {class_str.title()}", label_font=("Segoe UI", 16, "bold"))
    scrollableFrame.place(x=10, y=70)
    addStudentButton = ctk.CTkButton(root, text="Add Student", font=("Segoe UI", 13), command=lambda: assignStudentWindow(root, class_str))
    addStudentButton.pack(anchor="ne", pady=20, padx=10, side="right")
    deleteClassButton = ctk.CTkButton(root, text="Remove Class", font=("Segoe UI", 13), command=delete_class, fg_color=("#de0202", "#8B0000"), hover_color=("#8B0000", "#de0202"))
    deleteClassButton.pack(anchor="ne", pady=20, padx=10, side="right")
    threading.Thread(target=load_section_frames, args=(scrollableFrame, ), daemon=True).start()

    root.mainloop()


def sectionStudentWindow(window: ctk.CTk, class_str: str, section_str: str):
    global all_student_data

    all_student_data = None
    def load_student_frames(scrollableFrame):
        global all_student_data

        all_student_data = database.get_all_student_data_by_class_and_section(f"{class_str}-{section_str}")
        if all_student_data == {}:
            ctk.CTkLabel(scrollableFrame, text="No student was assigned!", font=("Segoe UI", 13, "bold")).pack(anchor="center")
        else:
            for roll in all_student_data:
                try:
                    student_data = all_student_data[roll]
                    frame = ctk.CTkFrame(scrollableFrame, border_width=1, height=60)
                    ctk.CTkLabel(frame, text=f"Student ID: {student_data['studentID']}", font=("Consolas", 12)).place(x=10, y=2)
                    ctk.CTkLabel(frame, text=student_data['name'].title(), font=("Segoe UI", 22, "bold")).place(x=10, y=25)
                    frame.pack_propagate(0)
                    rollLabel = ctk.CTkLabel(frame, text=f"Roll: {roll}", font=("Consolas", 12))
                    rollLabel.pack(anchor="ne", padx=10, pady=2)
                    frame.pack(padx=10, pady=2, fill='x', side="top")
                    
                    
                    def enter(event):
                        event.widget.configure(cursor="hand2")

                    def leave(event):
                        event.widget.configure(cursor="")

                    def on_frame_click(position_str):
                        studentWindow(root, position_str)

                    for widget in frame.winfo_children():
                        widget.bind("<Enter>", enter)
                        widget.bind("<Leave>", leave)
                        widget.bind("<Button-1>", lambda e, label=f'{class_str}-{section_str}-{str(rollLabel.cget("text")).split(": ")[1]}': on_frame_click(label))

                    frame.bind("<Enter>", enter)
                    frame.bind("<Leave>", leave)
                    frame.bind("<Button-1>", lambda e, label=f'{class_str}-{section_str}-{str(rollLabel.cget("text")).split(": ")[1]}': on_frame_click(label))
                except _tkinter.TclError:
                    pass
    
    def delete_section():
        if messagebox.askyesnocancel("Hold on! ", f"Are you sure you want to remove section {class_str}/{section_str.title()} with all the assigned students?"):
            database.delete_section(f"{class_str}-{section_str.lower()}")
            messagebox.showinfo("Execution Completed!", f"Section {class_str}/{section_str.title()} has been removed successfully!")
            root.after(1000, lambda: sectionWindow(root, class_str))
    
    def search():
        text = searchEntry.get()
        matched = []
        for d in all_student_data:
            if text.lower() in all_student_data[d]['name'].lower():
                matched.append(d)
        for widget in scrollableFrame.winfo_children():
            widget.destroy()
        if matched:
            for roll in matched:
                try:
                    student_data = all_student_data[roll]
                    frame = ctk.CTkFrame(scrollableFrame, border_width=1, height=60)
                    ctk.CTkLabel(frame, text=f"Student ID: {student_data['studentID']}", font=("Consolas", 12)).place(x=10, y=2)
                    ctk.CTkLabel(frame, text=student_data['name'].title(), font=("Segoe UI", 22, "bold")).place(x=10, y=25)
                    frame.pack_propagate(0)
                    rollLabel = ctk.CTkLabel(frame, text=f"Roll: {roll}", font=("Consolas", 12))
                    rollLabel.pack(anchor="ne", padx=10, pady=2)
                    frame.pack(padx=10, pady=2, fill='x', side="top")
                    
                    
                    def enter(event):
                        event.widget.configure(cursor="hand2")

                    def leave(event):
                        event.widget.configure(cursor="")

                    def on_frame_click(position_str):
                        studentWindow(root, position_str)

                    for widget in frame.winfo_children():
                        widget.bind("<Enter>", enter)
                        widget.bind("<Leave>", leave)
                        widget.bind("<Button-1>", lambda e, label=f'{class_str}-{section_str}-{str(rollLabel.cget("text")).split(": ")[1]}': on_frame_click(label))

                    frame.bind("<Enter>", enter)
                    frame.bind("<Leave>", leave)
                    frame.bind("<Button-1>", lambda e, label=f'{class_str}-{section_str}-{str(rollLabel.cget("text")).split(": ")[1]}': on_frame_click(label))
                except _tkinter.TclError:
                    pass
        else:
            ctk.CTkLabel(scrollableFrame, text="No match result found!", font=("Segoe UI", 13, "bold")).pack(anchor="center")

    window.destroy()
    root = ctk.CTk()
    positionRight = int(root.winfo_screenwidth()/2 - 650/2)
    positionDown = int(root.winfo_screenheight()/2 - 400/2)
    root.geometry(f"650x400+{positionRight}+{positionDown-50}")
    root.title(f"Viewing Class {class_str}/{section_str.title()}")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")


    aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
    aboutLabel.pack(anchor="se", side="bottom", padx=10)
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())

    classTitle = ctk.CTkLabel(root, text=f"Class {class_str}/{section_str.title()}", font=("Segoe UI", 30, 'bold'))
    classTitle.pack(padx=10, pady=22, anchor="nw", side="left")
    backButton = ctk.CTkButton(root, text="🢀", font=("Segoe UI", 13, "bold"), width=28, height=25, command=lambda: sectionWindow(root, class_str))
    backButton.place(x=2, y=2)

    scrollableFrame = ctk.CTkScrollableFrame(root, height=250, width=610, label_text=f"Students of Class {class_str}/{section_str.title()}", label_font=("Segoe UI", 16, "bold"))
    scrollableFrame.place(x=10, y=70)
    deleteSectionButton = ctk.CTkButton(root, text="Remove Section", font=("Segoe UI", 13), command=delete_section, fg_color=("#de0202", "#8B0000"), hover_color=("#8B0000", "#de0202"))
    deleteSectionButton.pack(anchor="ne", pady=5, padx=10, side="right")
    searchEntry = ctk.CTkEntry(root, placeholder_text="Type Name to be searched", width=175, height=26)
    searchEntry.place(x=400, y=40)
    searchButton = ctk.CTkButton(root, text="Search", font=("Segoe UI", 13), width=60, height=26, command=search)
    searchButton.place(x=580, y=40)
    searchEntry.bind('<Return>', lambda e: search())
    threading.Thread(target=load_student_frames, args=(scrollableFrame, ), daemon=True).start()

    root.mainloop()

def studentWindow(window: ctk.CTk, class_position: str):
    window.destroy()
    root = ctk.CTk()
    positionRight = int(root.winfo_screenwidth()/2 - 650/2)
    positionDown = int(root.winfo_screenheight()/2 - 460/2)
    root.geometry(f"650x460+{positionRight}+{positionDown-50}")
    root.resizable(0, 0)
    root.wm_iconbitmap(f"{assetsPath}/Icon.ico")

    dataList, data = database.get_student_data(class_position)
    root.title(data['name'])

    
    def delete_student():
        if messagebox.askyesnocancel("Hold on! ", f"Are you sure you want to remove {data['name'].title()} from class {class_position.split('-')[0]}/{class_position.split('-')[1].title()}?"):
            database.delete_student(class_position)
            messagebox.showinfo("Execution Completed!", f"{data['name'].title()} has been removed successfully!")
            root.after(1000, lambda: sectionStudentWindow(root, class_position.split('-')[0], class_position.split('-')[1]))
    
    aboutLabel = ctk.CTkLabel(root, text="Rotary School Student Manager", font=("Consolas", 12))
    aboutLabel.pack(anchor="se", side="bottom", padx=10)
    aboutLabel.bind("<Enter>", lambda e: aboutLabel.configure(cursor="hand2", font=("Consolas", 12, 'underline')))
    aboutLabel.bind("<Leave>", lambda e: aboutLabel.configure(cursor="", font=("Consolas", 12)))
    aboutLabel.bind("<Button-1>", lambda e: about())

    deleteStudentButton = ctk.CTkButton(root, text="Remove Student", font=("Segoe UI", 13), command=delete_student, fg_color=("#de0202", "#8B0000"), hover_color=("#8B0000", "#de0202"))
    deleteStudentButton.pack(anchor="ne", pady=2, padx=10, side="right")
    editStudentButton = ctk.CTkButton(root, text="Edit", font=("Segoe UI", 13), command=lambda: assignStudentWindow(root, class_position.split("-")[0], dataList))
    editStudentButton.pack(anchor="ne", pady=2, padx=10, side="right")
    dobLabel = ctk.CTkLabel(root, text=f"Student ID: {data['studentID']}", font=("Consolas", 13, 'bold'))
    dobLabel.place(x=10, y=22)
    dobLabel = ctk.CTkLabel(root, text=f"Date of Birth: {data['dob']}", font=("Consolas", 13, 'bold'))
    dobLabel.place(x=10, y=42)
    nameLabel = ctk.CTkLabel(root, text=data['name'].title(), font=("Segoe UI", 27, 'bold'))
    nameLabel.place(x=10, y=60)
    classInfoLabel = ctk.CTkLabel(root, text=f"Class: {class_position.split('-')[0]}                Section: {class_position.split('-')[1].title()}                 Roll: {class_position.split('-')[2].title()}", font=("Consolas", 14))
    classInfoLabel.place(x=10, y=100)

    # ---------------------------------
    fatherFrame = ctk.CTkFrame(root, width=305, border_width=1, fg_color="transparent", height=130)
    fatherFrame.place(x=10, y=140)
    fatherFrameName = ctk.CTkLabel(root, text=" Father's Information ", font=("Segoe UI", 15, "bold"))
    fatherFrameName.place(x=15, y=125)

    fnameLabel = ctk.CTkLabel(fatherFrame, text="Father's Name", font=("Segoe UI", 14, "bold"))
    fnameLabel.place(x=10, y=10)
    fnamevalueLabel = ctk.CTkLabel(fatherFrame, text=data['fathersName'].title(), font=("Segoe UI", 13))
    fnamevalueLabel.place(x=10, y=30)

    fcontactLabel = ctk.CTkLabel(fatherFrame, text="Father's Contact", font=("Segoe UI", 14, "bold"))
    fcontactLabel.place(x=10, y=55)
    fcontactvalueLabel = ctk.CTkLabel(fatherFrame, text=data['fathersPhone'], font=("Segoe UI", 13))
    fcontactvalueLabel.place(x=10, y=75)

    # ---------------------------------
    motherFrame = ctk.CTkFrame(root, width=305, border_width=1, fg_color="transparent", height=130)
    motherFrame.place(x=335, y=140)
    motherFrameName = ctk.CTkLabel(root, text=" Mother's Information ", font=("Segoe UI", 15, "bold"))
    motherFrameName.place(x=340, y=125)

    fnameLabel = ctk.CTkLabel(motherFrame, text="Mother's Name", font=("Segoe UI", 14, "bold"))
    fnameLabel.place(x=10, y=10)
    fnamevalueLabel = ctk.CTkLabel(motherFrame, text=data['mothersName'].title(), font=("Segoe UI", 13))
    fnamevalueLabel.place(x=10, y=30)

    fcontactLabel = ctk.CTkLabel(motherFrame, text="Mother's Contact", font=("Segoe UI", 14, "bold"))
    fcontactLabel.place(x=10, y=55)
    fcontactvalueLabel = ctk.CTkLabel(motherFrame, text=data['mothersPhone'], font=("Segoe UI", 13))
    fcontactvalueLabel.place(x=10, y=75)

    # ---------------------------------
    presentAddressFrame = ctk.CTkFrame(root, width=302, height=110, border_width=1, fg_color="transparent")
    presentAddressFrame.place(x=10, y=300)
    presentAddressFrameName = ctk.CTkLabel(root, text=" Present Address ", font=("Segoe UI", 15, "bold"))
    presentAddressFrameName.place(x=15, y=285)
    presentAddressLabel = ctk.CTkLabel(presentAddressFrame, text=data['presentAddress'], font=("Segoe UI", 13), justify="left", wraplength=290)
    presentAddressLabel.place(x=10, y=10)

    # ---------------------------------
    permanentAddressFrame = ctk.CTkFrame(root, width=305, height=110, border_width=1, fg_color="transparent")
    permanentAddressFrame.place(x=335, y=300)
    permanentAddressFrameName = ctk.CTkLabel(root, text=" Permanent Address ", font=("Segoe UI", 15, "bold"))
    permanentAddressFrameName.place(x=340, y=285)
    permanentAddressLabel = ctk.CTkLabel(permanentAddressFrame, text=data['permanentAddress'], font=("Segoe UI", 13), justify="left", wraplength=290)
    permanentAddressLabel.place(x=10, y=10)

    backButton = ctk.CTkButton(root, text="🢀", font=("Segoe UI", 13, "bold"), width=28, height=25, command=lambda: sectionStudentWindow(root, class_position.split("-")[0], class_position.split("-")[1]))
    backButton.place(x=2, y=2)

    root.mainloop()


if __name__ == "__main__":
    splash()
