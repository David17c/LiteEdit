import tkinter as tk
from tkinter import filedialog, messagebox

PROGRAM_NAME = "LiteEdit"

current_file_path = ""
textbox = None
root = tk.Tk()

FRAME_BACKGROUND_COLOR = "#161A21"

TEXTBOX_BACKGROUND_COLOR = "#1E222A"  
TEXTBOX_FOREGROUND_COLOR = "#ECEFF4"
TEXTBOX_TEXTSELECT_FOREGROUND_COLOR = "#FFFFFF"
TEXTBOX_TEXTSELECT_BACKGROUND_COLOR = "#5E81AC"
TEXTBOX_CURSOR_COLOR = "#88C0D0"

MENU_BACKGROUND_COLOR = "#1E222A"
MENU_FOREGROUND_COLOR = "#ECEFF4"
MENU_ACTIVE_BACKGROUND_COLOR = "#5E81AC"
MENU_ACTIVE_FOREGROUND_COLOR = "#FFFFFF"

def update_title():
    prefix = "*" if textbox.edit_modified() else ""
    root.title(f"{prefix}{current_file_path or PROGRAM_NAME}")


def main():
    global textbox

    root.title(PROGRAM_NAME)
    icon = tk.PhotoImage(file="image/liteedit_icon.png")
    root.iconphoto(True, icon)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.6)

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    menubar = tk.Menu(
        root,
        bg=MENU_BACKGROUND_COLOR,
        fg=MENU_FOREGROUND_COLOR,
        activebackground=MENU_ACTIVE_BACKGROUND_COLOR,
        activeforeground=MENU_ACTIVE_FOREGROUND_COLOR,
        tearoff=0
    )
    root.config(menu=menubar)

    file_menu = tk.Menu(
        menubar,
        tearoff=0,
        bg=MENU_BACKGROUND_COLOR,
        fg=MENU_FOREGROUND_COLOR,
        activebackground=MENU_ACTIVE_BACKGROUND_COLOR,
        activeforeground=MENU_ACTIVE_FOREGROUND_COLOR
    )

    file_menu.add_command(label="New", command=new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Open...", command=open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Save", command=save_file, accelerator="Ctrl+S")
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=on_closing, accelerator="Ctrl+Q")

    menubar.add_cascade(label="File", menu=file_menu)

    edit_menu = tk.Menu(
        menubar,
        tearoff=0,
        bg=MENU_BACKGROUND_COLOR,
        fg=MENU_FOREGROUND_COLOR,
        activebackground=MENU_ACTIVE_BACKGROUND_COLOR,
        activeforeground=MENU_ACTIVE_FOREGROUND_COLOR
    )

    edit_menu.add_command(label="Undo", command=undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", command=select_all_text, accelerator="Ctrl+A")
    edit_menu.add_command(label="Select Current Line", command=select_current_line, accelerator="Ctrl+L")

    menubar.add_cascade(label="Edit", menu=edit_menu)

    textbox = tk.Text(
        root,
        wrap="word",
        bg=TEXTBOX_BACKGROUND_COLOR,
        fg=TEXTBOX_FOREGROUND_COLOR,
        selectbackground=TEXTBOX_TEXTSELECT_BACKGROUND_COLOR,
        selectforeground=TEXTBOX_TEXTSELECT_FOREGROUND_COLOR,
        insertbackground=TEXTBOX_CURSOR_COLOR,
        undo=True,
        font=("TkDefaultFont", 13)
    )

    textbox.pack(fill="both", expand=True)
    textbox.focus_set()

    # Keyboard Shortcuts
    textbox.bind("<Control-s>", save_file)
    textbox.bind("<Control-a>", select_all_text)
    textbox.bind("<Control-l>", select_current_line)
    textbox.bind("<Control-o>", open_file)
    textbox.bind("<Control-n>", new_file)
    textbox.bind("<Control-q>", on_closing)
    textbox.bind("<Control-z>", undo)
    textbox.bind("<Control-y>", redo)

    textbox.bind("<<Modified>>", on_modified)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

def open_file(event=None):
    global current_file_path

    if textbox.edit_modified():
        result = messagebox.askyesnocancel("Confirmation", "Do you want to save before continuing?")

        if result is True:
            save_file()

        elif result is None:
            return 

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
        result = messagebox.askyesnocancel("Confirmation", "Do you want to save before continuing?")

        if result is True:
            save_file()

        elif result is None:
            return 

    current_file_path = ""

    textbox.delete("1.0", "end")
    textbox.edit_reset()
    textbox.edit_modified(False)

    update_title()


def select_all_text(event=None):
    textbox.tag_add("sel", "1.0", "end-1c")
    return "break"

def select_current_line(event=None):
    textbox.tag_remove("sel", "1.0", "end")
    textbox.tag_add("sel", "insert linestart", "insert lineend")
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
        result = messagebox.askyesnocancel(
            "Confirmation",
            "Do you want to save before closing?"
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


def on_modified(event=None):
    update_title()


if __name__ == "__main__":
    main()
