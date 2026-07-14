import tkinter as tk
from tkinter import filedialog, messagebox
import sys

PROGRAM_NAME = "LiteEdit"

current_file_path = ""
textbox = None
root = tk.Tk()


def update_title():
    prefix = "*" if textbox.edit_modified() else ""
    root.title(f"{prefix}{current_file_path or PROGRAM_NAME}")


def main():
    global textbox

    root.title(PROGRAM_NAME)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.6)

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    top_frame = tk.Frame(root, height=40)
    top_frame.pack(fill="x")

    tk.Button(top_frame, text="Open", command=open_file).pack(side="left", padx=10, pady=10)
    tk.Button(top_frame, text="Save", command=save_file).pack(side="left", padx=10, pady=10)
    tk.Button(top_frame, text="New", command=new_file).pack(side="left", padx=10, pady=10)

    textbox = tk.Text(root, wrap="word", undo=True, font=("Arial", 15))
    textbox.pack(fill="both", expand=True)
    textbox.focus_set()

    textbox.bind("<Control-s>", save_file) # save
    textbox.bind("<Control-a>", select_all_text) # select all text
    textbox.bind("<Control-o>", open_file) # open file
    textbox.bind("<Control-n>", new_file) # create new file
    textbox.bind("<Control-q>", on_closing) # close program
    textbox.bind("<Control-z>", undo) # undo
    textbox.bind("<Control-y>", redo) # redo

    textbox.bind("<<Modified>>", on_modified)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


def open_file(event=None):
    global current_file_path

    if textbox.edit_modified():
        if messagebox.askyesno("Confirmation", "Do you want to save before continuing?"):
            save_file()

    file_path = filedialog.askopenfilename(
        title="Open File",
        filetypes=[("All files", "*.*")]
    )

    if not file_path:
        return

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    textbox.delete("1.0", "end")
    textbox.insert("1.0", content)

    current_file_path = file_path
    textbox.edit_reset()
    textbox.edit_modified(False)
    update_title()


def save_file(event=None):
    global current_file_path

    if not textbox.edit_modified():
        return

    if not current_file_path:
        current_file_path = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=".txt",
            filetypes=[("All files", "*.*")]
        )

        if not current_file_path:
            return

    content = textbox.get("1.0", "end-1c")

    with open(current_file_path, "w", encoding="utf-8") as file:
        file.write(content)

    textbox.edit_modified(False)
    update_title()


def new_file(event=None):
    global current_file_path

    if textbox.edit_modified():
        if messagebox.askyesno("Confirmation", "Do you want to save before continuing?"):
            save_file()

    current_file_path = ""

    textbox.delete("1.0", "end")
    textbox.edit_reset()
    textbox.edit_modified(False)

    update_title()


def select_all_text(event=None):
    textbox.tag_add("sel", "1.0", "end-1c")
    return "break"

def undo(event=None):
    try:
        textbox.edit_undo()
    except tk.TclError:
        pass  # Nothing to undo
    return "break"

def redo(event=None):
    try:
        textbox.edit_redo()
    except tk.TclError:
        pass  # Nothing to redo
    return "break"


def on_closing(event=None):
    if textbox.edit_modified():
        if messagebox.askyesno("Confirmation", "Do you want to save before continuing?"):
            save_file()

    root.destroy()


def on_modified(event=None):
    update_title()


if __name__ == "__main__":
    main()