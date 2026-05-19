import customtkinter as ctk
from tkinter import messagebox
import json
import os
from datetime import date

# ─── THEME ───────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

TASKS_FILE = "tasks.json"

# ─── CLAYMORPHISM PALETTE ─────────────────────────────────
BG_MAIN        = "#EEF2FF"        # soft lavender page bg
CLAY_CARD      = "#FFFFFF"        # white card surface
CLAY_PRIMARY   = "#7C6EF5"        # violet — primary action
CLAY_PRIMARY_H = "#6355D8"        # hover
CLAY_ADD       = "#6EE7B7"        # mint green — add button
CLAY_ADD_H     = "#34D399"
CLAY_DEL       = "#FDA4AF"        # rose — delete
CLAY_DEL_H     = "#FB7185"
CLAY_DONE      = "#93C5FD"        # sky blue — mark done
CLAY_DONE_H    = "#60A5FA"
CLAY_SHADOW    = "#C7D2FE"        # shadow tint
TEXT_DARK      = "#1E1B4B"        # deep indigo text
TEXT_MID       = "#6B7280"        # muted label
PENDING_TAG    = "#FDE68A"        # amber pill
DONE_TAG       = "#BBF7D0"        # green pill
TAG_TEXT_P     = "#92400E"
TAG_TEXT_D     = "#065F46"

FONT_TITLE  = ("Segoe UI", 26, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 13)
FONT_SMALL  = ("Segoe UI", 11)
FONT_BTN    = ("Segoe UI", 12, "bold")
FONT_INPUT  = ("Segoe UI", 13)


# ─── TASK DATA ────────────────────────────────────────────
tasks      = []
id_counter = 1

def load_tasks():
    global tasks, id_counter
    if not os.path.exists(TASKS_FILE):
        return
    with open(TASKS_FILE, "r") as f:
        tasks = json.load(f)
    if tasks:
        id_counter = max(t["id"] for t in tasks) + 1

def save_tasks():
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def check_overdue(task):
    if task["status"] == "Complete":
        return
    due = date(task["due_year"], task["due_month"], task["due_day"])
    if date.today() > due:
        task["status"] = "Overdue"

# ─── MAIN APP ─────────────────────────────────────────────
class ToDoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("860x680")
        self.minsize(780, 580)
        self.configure(fg_color=BG_MAIN)
        self.resizable(True, False)

        load_tasks()
        self._build_ui()
        self.refresh_list()


    # ── LAYOUT ────────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=CLAY_PRIMARY,
                              corner_radius=24, height=72)
        header.pack(fill="x", padx=24, pady=(20, 0))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="My To-Do List",
                     font=FONT_TITLE, text_color="#FFFFFF"
                     ).pack(side="left", padx=28, pady=14)

        # ctk.CTkLabel(f, text="RoniKid",
        #              font=FONT_SMALL, text_color="#C7D2FE"
        #              ).pack(side="right", padx=28)

        # ── Body (left card + right card) ────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        self._build_input_card(body)
        self._build_list_card(body)


    # ── INPUT CARD ────────────────────────────────────────
    def _build_input_card(self, parent):
        card = self._clay_card(parent)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(card, text="Add New Task",
                     font=FONT_HEAD, text_color=TEXT_DARK
                     ).pack(anchor="w", padx=24, pady=(22, 4))

        ctk.CTkLabel(card, text="Task title",
                     font=FONT_SMALL, text_color=TEXT_MID
                     ).pack(anchor="w", padx=24)
        self.entry_title = self._clay_entry(card, "e.g. Finish Python project")
        self.entry_title.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(card, text="Priority",
                     font=FONT_SMALL, text_color=TEXT_MID
                     ).pack(anchor="w", padx=24)
        self.priority_var = ctk.StringVar(value="Medium")
        self._clay_segmented(card, ["High", "Medium", "Low"],
                             self.priority_var
                             ).pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(card, text="Due date  (DD / MM / YYYY)",
                     font=FONT_SMALL, text_color=TEXT_MID
                     ).pack(anchor="w", padx=24)

        date_row = ctk.CTkFrame(card, fg_color="transparent")
        date_row.pack(fill="x", padx=24, pady=(4, 18))
        self.entry_dd   = self._clay_entry(date_row, "DD",   width=60)
        self.entry_mm   = self._clay_entry(date_row, "MM",   width=60)
        self.entry_yyyy = self._clay_entry(date_row, "YYYY", width=80)
        for w in (self.entry_dd, self.entry_mm, self.entry_yyyy):
            w.pack(side="left", padx=(0, 8))

        # Add button
        add_btn = ctk.CTkButton(
            card, text="＋  Add Task", font=FONT_BTN,
            fg_color=CLAY_ADD, hover_color=CLAY_ADD_H,
            text_color=TEXT_DARK, corner_radius=16,
            height=44, command=self.add_task
        )
        add_btn.pack(fill="x", padx=24, pady=(0, 8))

        # Filter
        ctk.CTkLabel(card, text="Filter tasks",
                     font=FONT_SMALL, text_color=TEXT_MID
                     ).pack(anchor="w", padx=24, pady=(12, 2))
        self.filter_var = ctk.StringVar(value="All")
        self._clay_segmented(card, ["All", "Pending", "Complete", "Overdue"],
                             self.filter_var, command=self.refresh_list
                             ).pack(fill="x", padx=24, pady=(0, 16))

        # Stats
        self.stats_label = ctk.CTkLabel(
            card, text="", font=FONT_SMALL, text_color=TEXT_MID
        )
        self.stats_label.pack(anchor="w", padx=24, pady=(4, 16))


    # ── LIST CARD ─────────────────────────────────────────
    def _build_list_card(self, parent):
        card = self._clay_card(parent)
        card.grid(row=0, column=1, sticky="nsew")

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkLabel(header_row, text="Task Board",
                     font=FONT_HEAD, text_color=TEXT_DARK
                     ).pack(side="left")

        clear_btn = ctk.CTkButton(
            header_row, text="Clear All", font=FONT_SMALL,
            fg_color=CLAY_DEL, hover_color=CLAY_DEL_H,
            text_color="#7F1D1D", corner_radius=12,
            width=80, height=30, command=self.clear_all
        )
        clear_btn.pack(side="right")

        # Scrollable list area
        self.scroll_frame = ctk.CTkScrollableFrame(
            card, fg_color="transparent", corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=12, pady=(0, 16))


    # ── CLAY HELPERS ──────────────────────────────────────
    def _clay_card(self, parent):
        return ctk.CTkFrame(
            parent, fg_color=CLAY_CARD, corner_radius=24,
            border_width=2, border_color=CLAY_SHADOW
        )

    def _clay_entry(self, parent, placeholder="", width=None):
        kwargs = dict(
            master=parent, placeholder_text=placeholder,
            font=FONT_INPUT, fg_color="#F5F3FF",
            border_color=CLAY_SHADOW, border_width=2,
            corner_radius=12, text_color=TEXT_DARK,
            height=40
        )
        if width:
            kwargs["width"] = width
        return ctk.CTkEntry(**kwargs)

    def _clay_segmented(self, parent, values, variable, command=None):
        kwargs = dict(
            master=parent, values=values, variable=variable,
            font=FONT_SMALL, corner_radius=12,
            fg_color=CLAY_SHADOW,
            selected_color=CLAY_PRIMARY,
            selected_hover_color=CLAY_PRIMARY_H,
            unselected_color="#E0E7FF",
            unselected_hover_color="#C7D2FE",
            text_color=TEXT_DARK,
            height=34
        )
        if command:
            kwargs["command"] = command
        return ctk.CTkSegmentedButton(**kwargs)


    # ── TASK CARD ROW ─────────────────────────────────────
    def _task_row(self, parent, task):
        status  = task["status"]
        pill_bg = DONE_TAG if status == "Complete" else (
                  "#FCA5A5" if status == "Overdue" else PENDING_TAG)
        pill_fg = TAG_TEXT_D if status == "Complete" else (
                  "#7F1D1D" if status == "Overdue" else TAG_TEXT_P)

        row = ctk.CTkFrame(
            parent, fg_color="#F5F3FF",
            corner_radius=16, border_width=2,
            border_color=CLAY_SHADOW
        )
        row.pack(fill="x", padx=4, pady=6)
        row.columnconfigure(1, weight=1)

        # Priority dot
        pri_colors = {"High": "#F87171", "Medium": "#FBBF24", "Low": "#6EE7B7"}
        dot_color  = pri_colors.get(task.get("priority", "Low"), "#A5B4FC")
        dot = ctk.CTkFrame(row, width=10, height=10,
                           fg_color=dot_color, corner_radius=5)
        dot.grid(row=0, column=0, padx=(14, 8), pady=18, sticky="n")

        # Task info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, sticky="ew", pady=10)

        title_text = task["title"]
        ctk.CTkLabel(info, text=title_text, font=FONT_BODY,
                     text_color=TEXT_DARK, anchor="w"
                     ).pack(anchor="w")

        meta = f"Due: {task['due_day']:02d}/{task['due_month']:02d}/{task['due_year']}   ·   {task.get('priority','—')}"
        ctk.CTkLabel(info, text=meta, font=FONT_SMALL,
                     text_color=TEXT_MID, anchor="w"
                     ).pack(anchor="w")

        # Status pill
        ctk.CTkLabel(row, text=status, font=FONT_SMALL,
                     fg_color=pill_bg, text_color=pill_fg,
                     corner_radius=10, width=72, height=24
                     ).grid(row=0, column=2, padx=8)

        # Action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.grid(row=0, column=3, padx=(0, 12))

        if status != "Complete":
            ctk.CTkButton(
                btn_frame, text="✓", width=34, height=34,
                fg_color=CLAY_DONE, hover_color=CLAY_DONE_H,
                text_color="#1E3A5F", corner_radius=10, font=FONT_BTN,
                command=lambda t=task: self.mark_complete(t)
            ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_frame, text="✕", width=34, height=34,
            fg_color=CLAY_DEL, hover_color=CLAY_DEL_H,
            text_color="#7F1D1D", corner_radius=10, font=FONT_BTN,
            command=lambda t=task: self.delete_task(t)
        ).pack(side="left")


    # ── ACTIONS ───────────────────────────────────────────
    def add_task(self):
        global id_counter
        title = self.entry_title.get().strip()
        dd    = self.entry_dd.get().strip()
        mm    = self.entry_mm.get().strip()
        yyyy  = self.entry_yyyy.get().strip()

        if not title:
            messagebox.showwarning("Missing", "Please enter a task title.")
            return
        if not (dd.isdigit() and mm.isdigit() and yyyy.isdigit()):
            messagebox.showwarning("Invalid Date", "Enter a valid DD / MM / YYYY.")
            return

        task = {
            "id": id_counter,
            "title": title,
            "priority": self.priority_var.get(),
            "status": "Pending",
            "due_day":   int(dd),
            "due_month": int(mm),
            "due_year":  int(yyyy)
        }
        check_overdue(task)
        tasks.append(task)
        id_counter += 1
        save_tasks()

        self.entry_title.delete(0, "end")
        self.entry_dd.delete(0, "end")
        self.entry_mm.delete(0, "end")
        self.entry_yyyy.delete(0, "end")
        self.priority_var.set("Medium")
        self.refresh_list()

    def mark_complete(self, task):
        task["status"] = "Complete"
        save_tasks()
        self.refresh_list()

    def delete_task(self, task):
        if messagebox.askyesno("Delete", f'Delete "{task["title"]}"?'):
            tasks.remove(task)
            save_tasks()
            self.refresh_list()

    def clear_all(self):
        if not tasks:
            return
        if messagebox.askyesno("Clear All", "Delete ALL tasks?"):
            tasks.clear()
            save_tasks()
            self.refresh_list()

    def refresh_list(self, *_):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        filt = self.filter_var.get()
        shown = []
        for t in tasks:
            check_overdue(t)
            if filt == "All" or t["status"] == filt:
                shown.append(t)

        if not shown:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No tasks here yet.\nAdd one on the left!",
                font=FONT_BODY, text_color=TEXT_MID
            ).pack(expand=True, pady=60)
        else:
            for t in shown:
                self._task_row(self.scroll_frame, t)

        # Stats
        total    = len(tasks)
        pending  = sum(1 for t in tasks if t["status"] == "Pending")
        complete = sum(1 for t in tasks if t["status"] == "Complete")
        overdue  = sum(1 for t in tasks if t["status"] == "Overdue")
        self.stats_label.configure(
            text=f"Total {total}  ·  Pending {pending}  ·  Done {complete}  ·  Overdue {overdue}"
        )

# ─── ENTRY POINT ─────────────────────────────────────────
if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
