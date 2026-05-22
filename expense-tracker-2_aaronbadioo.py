import customtkinter as ctk

# ── theme ─────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

BG          = "#e8f4f0"
CARD_BG     = "#ffffff"
INPUT_BG    = "#f0faf6"
BTN_GREEN   = "#5caa8e"
BTN_GREEN_H = "#3d8a70"
BTN_RED     = "#f5d0d0"
BTN_RED_H   = "#e0a8a8"
ACCENT      = "#a8d8c8"
ACCENT_H    = "#7bbfab"
TEXT_DARK   = "#1a3d30"
TEXT_MID    = "#4a7a6a"
TEXT_MUTED  = "#8bbdaf"
RESULT_BG   = "#5caa8e"
ITEM_BG     = "#f0faf6"
ERR_COLOR   = "#c0404a"


def fmt(n):
    return f"${n:.2f}"


class ExpenseTracker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("460x680")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.total = 0.0
        self.count = 0
        self.empty_lbl = None

        self._build_ui()

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        root.pack(fill="both", expand=True, padx=24, pady=24)

        # ── header ────────────────────────────────────────────────────────────
        ctk.CTkLabel(root, text="💸", font=("Helvetica Neue", 40),
                     text_color=TEXT_DARK, fg_color=BG).pack()
        ctk.CTkLabel(root, text="Expense tracker",
                     font=("Helvetica Neue", 20, "bold"),
                     text_color=TEXT_DARK, fg_color=BG).pack()
        ctk.CTkLabel(root, text="Track your spending, one entry at a time",
                     font=("Helvetica Neue", 11),
                     text_color=TEXT_MID, fg_color=BG).pack(pady=(2, 16))

        # ── stat cards ────────────────────────────────────────────────────────
        stats = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
        stats.pack(fill="x", pady=(0, 12))
        stats.columnconfigure(0, weight=1)
        stats.columnconfigure(1, weight=1)

        # total card
        total_card = ctk.CTkFrame(stats, fg_color=CARD_BG, corner_radius=20,
                                  border_width=2, border_color=ACCENT)
        total_card.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkLabel(total_card, text="TOTAL SPENT",
                     font=("Helvetica Neue", 9), text_color=TEXT_MUTED,
                     fg_color=CARD_BG).pack(anchor="w", padx=14, pady=(12, 0))
        self.total_var = ctk.StringVar(value="$0.00")
        ctk.CTkLabel(total_card, textvariable=self.total_var,
                     font=("Helvetica Neue", 22, "bold"),
                     text_color=TEXT_DARK, fg_color=CARD_BG).pack(anchor="w", padx=14, pady=(0, 12))

        # count card
        count_card = ctk.CTkFrame(stats, fg_color=CARD_BG, corner_radius=20,
                                  border_width=2, border_color=ACCENT)
        count_card.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        ctk.CTkLabel(count_card, text="ENTRIES",
                     font=("Helvetica Neue", 9), text_color=TEXT_MUTED,
                     fg_color=CARD_BG).pack(anchor="w", padx=14, pady=(12, 0))
        self.count_var = ctk.StringVar(value="0")
        ctk.CTkLabel(count_card, textvariable=self.count_var,
                     font=("Helvetica Neue", 22, "bold"),
                     text_color=TEXT_DARK, fg_color=CARD_BG).pack(anchor="w", padx=14, pady=(0, 12))

        # ── transaction card ──────────────────────────────────────────────────
        card = ctk.CTkFrame(root, fg_color=CARD_BG, corner_radius=24,
                            border_width=2, border_color=ACCENT)
        card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(card, text="TRANSACTIONS",
                     font=("Helvetica Neue", 9), text_color=TEXT_MUTED,
                     fg_color=CARD_BG).pack(anchor="w", padx=16, pady=(14, 4))

        # scrollable list
        self.list_frame = ctk.CTkScrollableFrame(card, fg_color=CARD_BG,
                                                  height=180, corner_radius=0,
                                                  scrollbar_button_color=ACCENT,
                                                  scrollbar_button_hover_color=ACCENT_H)
        self.list_frame.pack(fill="x", padx=8)

        self.empty_lbl = ctk.CTkLabel(self.list_frame,
                                       text="No expenses yet — add one below",
                                       font=("Helvetica Neue", 11),
                                       text_color=TEXT_MUTED, fg_color=CARD_BG)
        self.empty_lbl.pack(pady=24)

        # input row
        inp_row = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=0)
        inp_row.pack(fill="x", padx=16, pady=(10, 0))

        self.entry = ctk.CTkEntry(inp_row, placeholder_text="Enter amount e.g. 50.00",
                                   fg_color=INPUT_BG, border_color=ACCENT,
                                   border_width=2, corner_radius=16,
                                   text_color=TEXT_DARK,
                                   placeholder_text_color=TEXT_MUTED,
                                   font=("Helvetica Neue", 13), height=42)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self._add_expense())

        ctk.CTkButton(inp_row, text="+", width=44, height=42,
                      fg_color=ACCENT, hover_color=ACCENT_H,
                      text_color=TEXT_DARK, font=("Helvetica Neue", 18, "bold"),
                      corner_radius=14,
                      command=self._add_expense).pack(side="left", padx=(8, 0))

        # error label
        self.err_var = ctk.StringVar()
        ctk.CTkLabel(card, textvariable=self.err_var,
                     font=("Helvetica Neue", 10), text_color=ERR_COLOR,
                     fg_color=CARD_BG).pack(anchor="w", padx=16, pady=(4, 0))

        # action buttons
        btn_row = ctk.CTkFrame(card, fg_color=CARD_BG, corner_radius=0)
        btn_row.pack(fill="x", padx=16, pady=(8, 16))

        ctk.CTkButton(btn_row, text="✓  Done — show total",
                      fg_color=BTN_GREEN, hover_color=BTN_GREEN_H,
                      text_color="white", font=("Helvetica Neue", 13, "bold"),
                      corner_radius=16, height=44,
                      command=self._show_total).pack(side="left", fill="x",
                                                      expand=True, padx=(0, 8))

        ctk.CTkButton(btn_row, text="🗑", width=44, height=44,
                      fg_color=BTN_RED, hover_color=BTN_RED_H,
                      text_color="#a32d2d", font=("Helvetica Neue", 16),
                      corner_radius=14,
                      command=self._clear_all).pack(side="left")

        # ── result panel ──────────────────────────────────────────────────────
        self.result_frame = ctk.CTkFrame(root, fg_color=RESULT_BG,
                                          corner_radius=24)
        ctk.CTkLabel(self.result_frame, text="FINAL TOTAL",
                     font=("Helvetica Neue", 10), text_color="#a8d8c8",
                     fg_color=RESULT_BG).pack(pady=(18, 0))
        self.result_total_var = ctk.StringVar(value="$0.00")
        ctk.CTkLabel(self.result_frame, textvariable=self.result_total_var,
                     font=("Helvetica Neue", 34, "bold"),
                     text_color="white", fg_color=RESULT_BG).pack()
        self.result_meta_var = ctk.StringVar()
        ctk.CTkLabel(self.result_frame, textvariable=self.result_meta_var,
                     font=("Helvetica Neue", 11), text_color="#a8d8c8",
                     fg_color=RESULT_BG).pack(pady=(0, 18))

    # ── add expense ───────────────────────────────────────────────────────────
    def _add_expense(self):
        self.err_var.set("")
        raw = self.entry.get().strip()
        if not raw:
            self.err_var.set("Please enter an amount.")
            return
        try:
            val = float(raw)
            if val <= 0:
                raise ValueError
        except ValueError:
            self.err_var.set("Invalid input — enter a positive number.")
            return

        self.total += val
        self.count += 1

        if self.empty_lbl:
            self.empty_lbl.destroy()
            self.empty_lbl = None

        row = ctk.CTkFrame(self.list_frame, fg_color=ITEM_BG, corner_radius=14)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=f"●  Entry #{self.count}",
                     font=("Helvetica Neue", 12), text_color=TEXT_MID,
                     fg_color=ITEM_BG).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(row, text=fmt(val),
                     font=("Helvetica Neue", 12, "bold"),
                     text_color=TEXT_DARK, fg_color=ITEM_BG).pack(side="right", padx=12)

        self.total_var.set(fmt(self.total))
        self.count_var.set(str(self.count))
        self.entry.delete(0, "end")
        self.result_frame.pack_forget()

    # ── show total ────────────────────────────────────────────────────────────
    def _show_total(self):
        if self.count == 0:
            self.err_var.set("Add at least one expense first.")
            return
        avg = self.total / self.count
        self.result_total_var.set(fmt(self.total))
        self.result_meta_var.set(
            f"{self.count} transaction{'s' if self.count != 1 else ''} · avg {fmt(avg)}"
        )
        self.result_frame.pack(fill="x", pady=(0, 4))

    # ── clear all ─────────────────────────────────────────────────────────────
    def _clear_all(self):
        self.total = 0.0
        self.count = 0
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.empty_lbl = ctk.CTkLabel(self.list_frame,
                                       text="No expenses yet — add one below",
                                       font=("Helvetica Neue", 11),
                                       text_color=TEXT_MUTED, fg_color=CARD_BG)
        self.empty_lbl.pack(pady=24)
        self.total_var.set("$0.00")
        self.count_var.set("0")
        self.err_var.set("")
        self.result_frame.pack_forget()
        self.entry.delete(0, "end")


if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
