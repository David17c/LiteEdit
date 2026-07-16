import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, font
from pathlib import Path

PROGRAM_NAME = "LiteEdit"

current_file_path = ""
root = tk.Tk()
textbox = None
textbox_font = font.Font(family="TkDefaultFont", size=13)

startup_file = ""

if len(sys.argv) > 1:
    startup_file = sys.argv[1]


# Update the title of the window based on save status
def update_title():
    prefix = "*" if textbox.edit_modified() else ""
    root.title(f"{prefix}{current_file_path or PROGRAM_NAME}")


# Program starts here
def main():
    global startup_file
    global textbox

    root.title(PROGRAM_NAME)

    script_dir = Path(__file__).parent
    icon_path = script_dir / "image" / "icon.png"

    icon = tk.PhotoImage(file=icon_path)
    root.iconphoto(True, icon)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.6)

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    menubar = tk.Menu(root, tearoff=0)
    root.config(menu=menubar)

    file_menu = tk.Menu(menubar, tearoff=0)

    file_menu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Open", command=open_file, accelerator="Ctrl+O")
    file_menu.add_separator()
    file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
    file_menu.add_command(
        label="Save as", command=save_file, accelerator="Ctrl+Shift+S  "
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=on_closing, accelerator="Ctrl+Q")

    menubar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(menubar, tearoff=0)

    edit_menu.add_command(label="Undo", command=undo, accelerator="Ctrl+Z  ")
    edit_menu.add_command(label="Redo", command=redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Cut",
        command=lambda: textbox.event_generate("<<Cut>>"),
        accelerator="Ctrl+X",
    )
    edit_menu.add_command(
        label="Copy",
        command=lambda: textbox.event_generate("<<Copy>>"),
        accelerator="Ctrl+C",
    )
    edit_menu.add_command(
        label="Paste",
        command=lambda: textbox.event_generate("<<Paste>>"),
        accelerator="Ctrl+V",
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Select All", command=select_all_text, accelerator="Ctrl+A"
    )
    edit_menu.add_command(
        label="Select Current Line", command=select_current_line, accelerator="Ctrl+L"
    )

    menubar.add_cascade(label="Edit", menu=edit_menu)

    view_menu = tk.Menu(menubar, tearoff=0)

    view_menu.add_command(
        label="Zoom in", command=lambda: zoom("in"), accelerator="Ctrl+Up"
    )
    view_menu.add_command(
        label="Zoom out", command=lambda: zoom("out"), accelerator="Ctrl+Down  "
    )
    view_menu.add_command(
        label="font", command=change_font, accelerator="Ctrl+Shift+T  "
    )

    menubar.add_cascade(label="View", menu=view_menu)
    textbox = tk.Text(root, wrap="none", undo=True, font=textbox_font)

    textbox.pack(fill="both", expand=True)
    textbox.focus_set()

    if startup_file and os.path.isfile(startup_file):
        root.after(0, open_file)

    textbox.bind("<Control-s>", save_file)
    textbox.bind("<Control-Shift-S>", save_as_file)
    textbox.bind("<Control-a>", select_all_text)
    textbox.bind("<Control-l>", select_current_line)
    textbox.bind("<Control-o>", open_file)
    textbox.bind("<Control-n>", new_file)
    textbox.bind("<Control-q>", on_closing)
    textbox.bind("<Control-z>", undo)
    textbox.bind("<Control-y>", redo)
    textbox.bind("<Control-equal>", lambda event: zoom("in"))
    textbox.bind("<Control-Up>", lambda event: zoom("in"))
    textbox.bind("<Control-Down>", lambda event: zoom("out"))
    textbox.bind("<Control-Shift-T>", change_font)

    textbox.bind("<<Modified>>", on_modified)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()


# Open a new file
def open_file(event=None):
    global current_file_path
    global startup_file

    if textbox.edit_modified():
        result = messagebox.askyesnocancel(
            "Confirmation", "Do you want to save before continuing?"
        )

        if result is True:
            save_file()

        elif result is None:
            return

    if startup_file != "":
        file_path = startup_file
        startup_file = ""
    else:
        file_path = filedialog.askopenfilename(
            title="Open File", filetypes=[("All files", "*.*")]
        )

    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        messagebox.showerror("ERROR", "File is not a valid UTF-8 text file.")
        return
    except OSError as err:
        messagebox.showerror("ERROR", f"Unable to open file. {err}")
        return

    textbox.delete("1.0", "end")
    textbox.insert("1.0", content)

    current_file_path = file_path
    textbox.edit_reset()
    textbox.edit_modified(False)
    update_title()


# Save the current file
def save_file(event=None):
    global current_file_path

    if not textbox.edit_modified():
        return

    if not current_file_path:
        current_file_path = filedialog.asksaveasfilename(
            title="Save File", defaultextension=".txt", filetypes=[("All files", "*.*")]
        )

        if not current_file_path:
            return

    content = textbox.get("1.0", "end-1c")

    with open(current_file_path, "w", encoding="utf-8") as file:
        file.write(content)

    textbox.edit_modified(False)
    update_title()


# Saves the current file as a new file
def save_as_file(event=None):
    global current_file_path

    new_file_path = filedialog.asksaveasfilename(
        title="Save As", defaultextension=".txt", filetypes=[("All files", "*.*")]
    )

    if not new_file_path:
        return

    content = textbox.get("1.0", "end-1c")

    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(content)

    current_file_path = new_file_path
    textbox.edit_modified(False)
    update_title()


# Creates a new empty document
def new_file(event=None):
    global current_file_path

    if textbox.edit_modified():
        result = messagebox.askyesnocancel(
            "Confirmation", "Do you want to save before continuing?"
        )

        if result is True:
            save_file()

        elif result is None:
            return

    current_file_path = ""

    textbox.delete("1.0", "end")
    textbox.edit_reset()
    textbox.edit_modified(False)

    update_title()


# Select all text in the file
def select_all_text(event=None):
    textbox.tag_add("sel", "1.0", "end-1c")
    return "break"


# Select the text in the currently selected line
def select_current_line(event=None):
    textbox.tag_remove("sel", "1.0", "end")
    textbox.tag_add("sel", "insert linestart", "insert lineend")
    return "break"


# Go back and forward in time to fix mistakes
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
        pass
    return "break"


# Makes sure you don't quite withou saving
def on_closing(event=None):
    if textbox.edit_modified():
        result = messagebox.askyesnocancel(
            "Confirmation", "Do you want to save before closing?"
        )

        if result is True:
            save_file()
            root.destroy()
        elif result is False:
            root.destroy()
        else:
            return

    else:
        root.destroy()


# Updates the window title based on the save status of file
def on_modified(event=None):
    update_title()


# changes fontsize to simulate zooming in or out
def zoom(action, event=None):
    global textbox_font

    current_size = textbox_font.cget("size")
    if action == "in":
        if current_size < 250:
            textbox_font.configure(size=current_size + 1)
    elif action == "out":
        if current_size > 1:
            textbox_font.configure(size=current_size - 1)


# Calls the font selection menu
def change_font(event=None):
    global textbox_font
    global root

    root.tk.call(
        "tk",
        "fontchooser",
        "configure",
        "-font",
        textbox_font,
        "-command",
        root.register(font_changed),
    )
    root.tk.call("tk", "fontchooser", "show")


# Changes the font to the one chosen i nthe fint selection menu
def font_changed(font_desc):
    actual = font.Font(font=font_desc).actual()
    textbox_font.configure(**actual)


# Calls the main function
if __name__ == "__main__":
    main()
