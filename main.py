from datetime import datetime
from tkinter import *
import os
import shutil
import fitz  
from PIL import Image, ImageTk

input_dir = "C:\\Users\\sandr\\OneDrive\\Desktop\\SCAN"
target_dir = "C:\\Users\\sandr\\OneDrive\\Desktop\\DMS"

def list_pdf_files():
    files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    return sorted(files)


def open_selected_file(event):
    selected_file = listbox.get(listbox.curselection())
    if selected_file:
        preview_pdf(os.path.join(input_dir, selected_file))

def get_immediate_subdirectories(a_dir):
    return sorted([name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))])

def store_file(preview_file, destination):

    def select_dir(sub_dir):
        selected_dir.set(sub_dir)
        subdirectory_dialog.destroy()
        return sub_dir

    def stop_process():
        nonlocal exit_flag
        exit_flag = True
        subdirectory_dialog.destroy()

    exit_flag = False
    source_path = os.path.join(input_dir, preview_file)
    destination_dir = os.path.join(target_dir, destination)
    curr_depth = get_immediate_subdirectories(destination_dir)

    while curr_depth:

        subdirectory_dialog = Toplevel(root)
        subdirectory_dialog.protocol("WM_DELETE_WINDOW", stop_process)
        subdirectory_dialog.title("Select Subdirectory")
        x = root.winfo_x() + (root.winfo_width() // 2) - (subdirectory_dialog.winfo_reqwidth() // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (subdirectory_dialog.winfo_reqheight() // 2)

        subdirectory_dialog.geometry(f"+{x}+{y}")
        subdirectory_dialog.configure(bg="white")

        selected_dir = StringVar()

        for sub_dir in curr_depth:
            sub_button = Button(
                subdirectory_dialog,
                text=sub_dir,
                command=lambda sub=sub_dir: select_dir(sub),
                font=("Calibri", 12),
                bg="white",
                fg="black",
                bd=1,
                relief="solid",
                width=20
            )
            sub_button.pack(pady=5)

        subdirectory_dialog.wait_window()

        if exit_flag:
            output_box.insert(END, f"File {os.path.basename(preview_file)} was NOT moved: PROCESS INTERRUPTED\n")
            output_box.see(END)
            return

        selected_dir_value = selected_dir.get()

        destination_dir = os.path.join(destination_dir, selected_dir_value)
        curr_depth = get_immediate_subdirectories(destination_dir)

    destination_file = os.path.join(destination_dir, preview_file.replace(' ', '_'))
    copy_file(source_path, destination_file)


def preview_pdf(file):
    global current_previewed_file
    current_previewed_file = file
    preview_label.config(text="Loading...")
    root.update_idletasks()

    pdf_document = fitz.open(file)
    page = pdf_document.load_page(0) 
    pix = page.get_pixmap()

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.thumbnail((400, 600))
    photo = ImageTk.PhotoImage(img)

    preview_label.config(image=photo, text="")
    preview_label.image = photo

def delete_file(file):
    destination_dir = os.path.join(target_dir, "DELETE")
    os.makedirs(destination_dir, exist_ok=True)
    destination_file = os.path.join(destination_dir, os.path.basename(file))
    copy_file(os.path.join(input_dir, file), destination_file)

def copy_file(in_path, out_path):

    save_path = os.path.join(target_dir, "SAVE")
    os.makedirs(save_path, exist_ok=True)
    shutil.copy(in_path, save_path)

    destination_file = f"{out_path[:-4]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
    shutil.copy(in_path, destination_file)

    print(destination_file)
    output_box.insert(END, f"{os.path.basename(in_path)} --> {destination_file[len(target_dir)+1:]}\n")
    output_box.see(END)


def refresh_list():
    listbox.delete(0, END)
    for pdf_file in list_pdf_files():
        file_path = os.path.join(input_dir, pdf_file)
        creation_date = os.path.getctime(file_path)
        listbox.insert(END, f"{pdf_file}")  #{'📄'}

root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry('%sx%s' % (int(width / 1.2), int(height / 1.2)))
root.title("Hunkeler-DMS")
root.configure(bg="white")

title_label = Label(root, text="Hunkeler-DMS", font=("Calibri", 16), bg="white", fg="black")
title_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=10)

scan_frame = Frame(root, bg="white", bd=1, relief="solid", width=200)
scan_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
scan_label = Label(scan_frame, text="Scan Ordner", font=("Calibri", 12), bg="white")
scan_label.pack(side="top", padx=10, pady=(10, 5))
listbox = Listbox(scan_frame, bg="white", fg="black", font=("Calibri", 12), bd=0, selectbackground="lightgrey",
                  width=30, height=20)
listbox.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 10))
for pdf_file in list_pdf_files():
    file_path = os.path.join(input_dir, pdf_file)
    creation_date = os.path.getctime(file_path)
    listbox.insert(END, f"{pdf_file}")  #{'📄'}
listbox.bind("<<ListboxSelect>>", open_selected_file)

refresh_button = Button(scan_frame, text="Refresh", command=refresh_list, font=("Calibri", 12), bg="white", fg="black",
                        bd=1, relief="solid")
refresh_button.pack(side="bottom", padx=10, pady=(5, 10))

preview_frame = Frame(root, bg="white", bd=1, relief="solid", width=400)
preview_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=(0, 10))
preview_label = Label(preview_frame, bg="white", bd=0)
preview_label.pack(side="top", padx=10, pady=10)

process_frame = Frame(root, bg="white", bd=1, relief="solid", width=200)
process_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 10), pady=(0, 10))
process_label = Label(process_frame, text="Prozesse", font=("Calibri", 12), bg="white")
process_label.pack(side="top", padx=10, pady=(10, 5))
for destination in get_immediate_subdirectories(target_dir):
    button_color = "lightgrey" if get_immediate_subdirectories(os.path.join(target_dir, destination)) else "white"
    button = Button(process_frame, text=f"{destination}",
                    command=lambda dest=destination: store_file(os.path.basename(current_previewed_file), dest),
                    bg=button_color, fg="black", bd=1, relief="solid", font=("Calibri", 12), width=20)
    button.pack(fill="x", padx=10, pady=(0, 5))

delete_button = Button(root, text="DELETE", command=lambda: delete_file(current_previewed_file),
                       font=("Calibri", 12), bg="black", fg="white", bd=1, relief="solid", width=20)
delete_button.grid(row=1, column=2, sticky="se", padx=(5, 10), pady=(0, 10))

output_box = Text(root, wrap=WORD, bg="white", fg="black", font=("Calibri", 12), height=5)
output_box.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)

root.mainloop()
