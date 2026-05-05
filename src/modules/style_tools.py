import re
import tkinter as tk
from tkinter import ttk


# THEME
DARK = {
    "bg": "#2e2e2e",
    "fg": "#ffffff",
    "entry": "#3a3a3a",
    "button": "#444444",
    "hover": "#555555",
    "select": "#5aa2ff"
}

# TTK STYLES
def setup_ttk():
    style = ttk.Style()
    style.theme_use("clam")

    # base
    style.configure(".", background=DARK["bg"], foreground=DARK["fg"])

    # frames / containers
    style.configure("TFrame", background=DARK["bg"])
    style.configure("TLabelframe", background=DARK["bg"])
    style.configure("TLabelframe.Label", background=DARK["bg"], foreground=DARK["fg"])

    # text
    style.configure("TLabel", background=DARK["bg"], foreground=DARK["fg"])

    style.configure("TEntry",
        fieldbackground=DARK["entry"],
        foreground=DARK["fg"]
    )

    # buttons
    style.configure("TButton",
        background=DARK["button"],
        foreground=DARK["fg"]
    )
    style.map("TButton",
        background=[("active", DARK["hover"])]
    )

    # check / radio
    style.configure("TCheckbutton", background=DARK["bg"], foreground=DARK["fg"])
    style.configure("TRadiobutton", background=DARK["bg"], foreground=DARK["fg"])

    # combobox / menubutton
    style.configure("TCombobox",
        fieldbackground=DARK["entry"],
        foreground=DARK["fg"]
    )

    style.configure("TMenubutton",
        background=DARK["button"],
        foreground=DARK["fg"]
    )

    # notebook (IMPORTANT)
    style.configure("TNotebook",
        background=DARK["bg"],
        borderwidth=0
    )

    style.configure("TNotebook.Tab",
        background=DARK["button"],
        foreground=DARK["fg"],
        padding=[10, 5]
    )

    style.map("TNotebook.Tab",
        background=[("selected", DARK["hover"])],
        foreground=[("selected", DARK["fg"])]
    )

    # treeview
    style.configure("Treeview",
        background=DARK["entry"],
        foreground=DARK["fg"],
        fieldbackground=DARK["entry"]
    )

    style.configure("Treeview.Heading",
        background=DARK["button"],
        foreground=DARK["fg"]
    )

# TK APPLIER (recursive)
def apply_tk(widget):
    try:
        # root / containers
        if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame, tk.LabelFrame, tk.PanedWindow)):
            widget.configure(
                bg=DARK["bg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # labels
        elif isinstance(widget, tk.Label):
            widget.configure(
                bg=DARK["bg"],
                fg=DARK["fg"],
                bd=0,
                highlightthickness=0
            )

        # buttons
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=DARK["button"],
                fg=DARK["fg"],
                activebackground=DARK["hover"],
                activeforeground=DARK["fg"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2"
            )

        # entry fields
        elif isinstance(widget, tk.Entry):
            widget.configure(
                bg=DARK["entry"],
                fg=DARK["fg"],
                insertbackground=DARK["fg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # text areas
        elif isinstance(widget, tk.Text):
            widget.configure(
                bg=DARK["entry"],
                fg=DARK["fg"],
                insertbackground=DARK["fg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # listboxes
        elif isinstance(widget, tk.Listbox):
            widget.configure(
                bg=DARK["entry"],
                fg=DARK["fg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # canvas
        elif isinstance(widget, tk.Canvas):
            widget.configure(
                bg=DARK["bg"],
                bd=0,
                highlightthickness=0
            )

        # scrollbars
        elif isinstance(widget, tk.Scrollbar):
            widget.configure(
                bg=DARK["bg"],
                troughcolor=DARK["bg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # checkbuttons
        elif isinstance(widget, tk.Checkbutton):
            widget.configure(
                bg=DARK["bg"],
                fg=DARK["fg"],
                selectcolor=DARK["bg"],
                activebackground=DARK["bg"],
                bd=0,
                highlightthickness=0,
                relief="flat",
                cursor="hand2"
            )

        # radiobuttons
        elif isinstance(widget, tk.Radiobutton):
            widget.configure(
                bg=DARK["bg"],
                fg=DARK["fg"],
                selectcolor=DARK["bg"],
                activebackground=DARK["bg"],
                bd=0,
                highlightthickness=0,
                relief="flat"
            )

        # menubuttons
        elif isinstance(widget, tk.Menubutton):
            widget.configure(
                bg=DARK["button"],
                fg=DARK["fg"],
                activebackground=DARK["hover"],
                activeforeground=DARK["fg"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2"
            )

        # menus
        elif isinstance(widget, tk.Menu):
            widget.configure(
                bg=DARK["bg"],
                fg=DARK["fg"],
                activebackground=DARK["hover"],
                activeforeground=DARK["fg"],
                bd=0,
                tearoff=0,
                relief="flat"
            )

    except:
        pass

    # recurse through all children
    for child in widget.winfo_children():
        apply_tk(child)

# ENTRY POINT
def auto_hook(root):
    setup_ttk()
    apply_tk(root)


def enable_auto_refresh(root):
    setup_ttk()  # safe to call again (idempotent)

    def refresh(event=None):
        try:
            apply_tk(root)
        except:
            pass

    # fires when new widgets appear
    root.bind_all("<Map>", refresh)

    # initial pass
    apply_tk(root)