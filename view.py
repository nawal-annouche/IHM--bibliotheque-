"""
View.py - Interface graphique Tkinter
Responsabilité : Affichage et interaction utilisateur

UI refaite pour correspondre au design de la capture :
- formulaire "Informations du livre" (Titre/Auteur puis Année/Genre)
- barre de recherche (entre formulaire et liste)
- tableau avec en-têtes (ID, Titre, Auteur, Année, Genre) + alternance de lignes
- barre d'actions en bas (Ajouter, Réinitialiser | Modifier, Supprimer, Afficher tout | Quitter)

Note: Tkinter ne gère pas le "border-radius" nativement. Les coins arrondis sont une approximation via Canvas.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Tuple


class _RoundedCard(tk.Canvas):
    """Canvas qui dessine un rectangle arrondi (approximation) + un frame 'content'."""

    def __init__(
        self,
        parent,
        radius: int = 14,
        bg: str = "#ffffff",
        border: str = "#d1d5db",
        border_width: int = 1,
        padding: int = 12,
        **kwargs,
    ):
        super().__init__(parent, highlightthickness=0, bd=0, bg=parent["bg"], **kwargs)
        self._radius = radius
        self._card_bg = bg
        self._border = border
        self._bw = border_width
        self._padding = padding

        self.content = tk.Frame(self, bg=bg)
        self._win = self.create_window(padding, padding, anchor="nw", window=self.content)

        self.bind("<Configure>", self._redraw)
        self.content.bind("<Configure>", self._fit_to_content)

    def _fit_to_content(self, _event=None):
        self.update_idletasks()
        h = self.content.winfo_reqheight() + 2 * self._padding
        self.configure(height=max(h, 10))

    def _round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    def _redraw(self, _event=None):
        self.delete("card")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 2 or h <= 2:
            return

        r = min(self._radius, (w - 2) // 2, (h - 2) // 2)
        x1, y1 = self._bw, self._bw
        x2, y2 = w - self._bw, h - self._bw

        # Border
        self._round_rect(x1, y1, x2, y2, r, fill=self._border, outline="", tags="card")
        # Inner bg
        inner = self._bw
        self._round_rect(
            x1 + inner,
            y1 + inner,
            x2 - inner,
            y2 - inner,
            max(r - inner, 1),
            fill=self._card_bg,
            outline="",
            tags="card",
        )

        pad = self._padding
        self.coords(self._win, pad, pad)
        self.itemconfigure(self._win, width=max(w - 2 * pad, 10), height=max(h - 2 * pad, 10))


class BibliothequeView:
    """Vue de l'application bibliothèque (Tkinter)."""

    _PLACEHOLDERS = {"Ex : Les Misérables", "Ex : Victor Hugo", "Ex : 1862"}
    _SEARCH_PLACEHOLDER = "Rechercher par titre ou auteur"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Bibliothèque personnelle")
        self.root.geometry("1050x720")
        self.root.minsize(950, 650)
        self.root.configure(bg="#e9edf3")

        # Variables
        self.var_titre = tk.StringVar()
        self.var_auteur = tk.StringVar()
        self.var_annee = tk.StringVar()
        self.var_genre = tk.StringVar()
        self.var_recherche = tk.StringVar()

        self.selected_id: Optional[int] = None

        self._setup_styles()
        self._build_interface()

    # ----------------- Styles -----------------

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Books.Treeview",
            background="#ffffff",
            foreground="#111827",
            rowheight=34,
            fieldbackground="#ffffff",
            borderwidth=1,
            relief="solid",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Books.Treeview.Heading",
            background="#eef2f7",
            foreground="#111827",
            font=("Segoe UI", 10, "bold"),
            relief="solid",
            borderwidth=1,
        )
        style.map(
            "Books.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#111827")],
        )

        style.configure(
            "Vertical.TScrollbar",
            troughcolor="#f3f4f6",
            bordercolor="#f3f4f6",
            arrowcolor="#6b7280",
        )

    # ----------------- Helpers placeholders -----------------

    def _attach_placeholder(self, entry: tk.Entry, placeholder: str):
        """Ajoute un placeholder dans un Entry."""
        normal_fg = "#111827"
        hint_fg = "#9ca3af"

        def show_hint():
            if entry.get().strip() == "":
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
                entry.config(fg=hint_fg)

        def hide_hint():
            if entry.get().strip() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=normal_fg)

        entry.bind("<FocusIn>", lambda _e: hide_hint())
        entry.bind("<FocusOut>", lambda _e: show_hint())
        entry.bind("<Key>", lambda _e: entry.config(fg=normal_fg))
        show_hint()

    def _is_placeholder(self, text: str) -> bool:
        return text.strip() in self._PLACEHOLDERS

    # ----------------- Layout -----------------

    def _build_interface(self):
        self.page = tk.Frame(self.root, bg="#e9edf3")
        self.page.pack(fill=tk.BOTH, expand=True, padx=18, pady=14)

        self._build_top_bar()
        self._build_book_info_section()   # 1) formulaire
        self._build_search_section()      # 2) recherche
        self._build_action_buttons()      # 3) boutons — packés en bas AVANT la liste
        self._build_list_section()        # 4) liste — prend le reste

    def _build_top_bar(self):
        top = tk.Frame(self.page, bg="#e9edf3")
        top.pack(fill=tk.X, pady=(0, 10))

        title = tk.Label(
            top,
            text="Bibliothèque personnelle",
            bg="#e9edf3",
            fg="#111827",
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(pady=(0, 2))

    def _build_book_info_section(self):
        # Formulaire compact
        card = _RoundedCard(self.page, radius=16, bg="#ffffff", border="#d1d5db", padding=10)
        card.pack(fill=tk.X, padx=6, pady=(0, 10))

        wrap = card.content
        wrap.columnconfigure(0, weight=1, uniform="col")
        wrap.columnconfigure(1, weight=1, uniform="col")

        title = tk.Label(
            wrap,
            text="Informations du livre",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#111827",
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        def field(parent, label, var, row, col, widget="entry"):
            box = tk.Frame(parent, bg="#ffffff")
            box.grid(row=row, column=col, sticky="ew", padx=(0, 18) if col == 0 else (0, 0), pady=(0, 6))

            label_frame = tk.Frame(box, bg="#ffffff")
            label_frame.pack(anchor="w", pady=(0, 4))

            tk.Label(
                label_frame,
                text=label,
                font=("Segoe UI", 9),
                bg="#ffffff",
                fg="#374151",
            ).pack(side=tk.LEFT)

            tk.Label(
                label_frame,
                text=" *",
                font=("Segoe UI", 9, "bold"),
                bg="#ffffff",
                fg="#dc2626",
            ).pack(side=tk.LEFT)

            if widget == "combo":
                GENRES   = ["Roman", "Histoire", "Science", "Fiction", "Fantasy",
                            "Aventure", "Philosophie", "Science-Fiction", "Biographie", "Thriller"]
                FIELD_BG  = "#f3f4f6"
                ARROW_BG  = "#e2e8f0"   # fond du bouton flèche — visible
                ARROW_BGH = "#cbd5e1"   # hover
                FIELD_H   = 36
                ARROW_W   = 30
                F_RADIUS  = 10

                def _rr_cb(cvs, x1, y1, x2, y2, r, **kw):
                    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
                           x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
                           x1,y2, x1,y2-r, x1,y1+r, x1,y1]
                    cvs.create_polygon(pts, smooth=True, splinesteps=24, **kw)

                # ── Canvas conteneur arrondi ──────────────────────────────
                cb_cvs = tk.Canvas(box, height=FIELD_H, bg="#ffffff",
                                   highlightthickness=0, bd=0)
                cb_cvs.pack(fill=tk.X)

                # ── Entry réelle embarquée (saisie libre) ─────────────────
                genre_entry = tk.Entry(
                    cb_cvs,
                    textvariable=var,
                    bd=0, relief=tk.FLAT,
                    font=("Segoe UI", 10),
                    bg=FIELD_BG, fg="#111827",
                    insertbackground="#111827",
                    highlightthickness=0,
                )
                entry_win_cb = cb_cvs.create_window(0, 0, anchor="nw", window=genre_entry)

                _st = {"focus": False, "popup": None, "arrow_hover": False}

                def _draw_cb(w_=None, *_):
                    if w_ is None or not isinstance(w_, int):
                        w_ = cb_cvs.winfo_width()
                    if w_ < 4:
                        return
                    cb_cvs.delete("bg_shape")
                    cb_cvs.delete("arrow_bg")
                    cb_cvs.delete("arrow_txt")

                    # Fond principal arrondi
                    border = "#16a34a" if _st.get("green") else ("#93c5fd" if _st["focus"] else "#d1d5db")
                    _rr_cb(cb_cvs, 1, 1, w_-1, FIELD_H-1, F_RADIUS,
                           fill=FIELD_BG, outline=border, width=1, tags="bg_shape")
                    cb_cvs.tag_lower("bg_shape")

                    # Bouton flèche — rectangle arrondi côté droit
                    ax = w_ - ARROW_W - 2
                    ab = ARROW_BGH if _st["arrow_hover"] else ARROW_BG
                    # fond rectangle droit arrondi côté droit uniquement
                    cb_cvs.create_rectangle(ax, 3, w_-3, FIELD_H-3,
                                            fill=ab, outline="", tags="arrow_bg")
                    # flèche ▾ bien contrastée
                    cb_cvs.create_text(w_ - ARROW_W//2 - 2, FIELD_H//2,
                                       text="▾", font=("Segoe UI", 12, "bold"),
                                       fill="#374151", tags="arrow_txt")

                    # positionner l'entry (laisser la place au bouton)
                    cb_cvs.coords(entry_win_cb, 10, 4)
                    cb_cvs.itemconfigure(entry_win_cb,
                                         width=max(w_ - 10 - ARROW_W - 6, 10),
                                         height=FIELD_H - 8)

                cb_cvs.bind("<Configure>", lambda e: _draw_cb(e.width))
                var.trace_add("write", lambda *_: _draw_cb())

                def _close_popup():
                    if _st["popup"]:
                        try: _st["popup"].destroy()
                        except Exception: pass
                        _st["popup"] = None
                    _draw_cb()

                def _open_popup(event=None):
                    if _st["popup"]:
                        _close_popup()
                        return
                    popup = tk.Toplevel(cb_cvs)
                    popup.overrideredirect(True)
                    popup.configure(bg="#d1d5db")
                    _st["popup"] = popup
                    cb_cvs.update_idletasks()
                    px  = cb_cvs.winfo_rootx()
                    py  = cb_cvs.winfo_rooty() + FIELD_H + 2
                    pw  = cb_cvs.winfo_width()
                    rh  = 32
                    popup.geometry(f"{pw}x{len(GENRES)*rh + 2}+{px}+{py}")
                    inner_p = tk.Frame(popup, bg="#ffffff")
                    inner_p.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
                    for g in GENRES:
                        lbl = tk.Label(inner_p, text=g, font=("Segoe UI", 10),
                                       bg="#ffffff", fg="#111827",
                                       anchor="w", padx=12, height=2, cursor="hand2")
                        lbl.pack(fill=tk.X)
                        lbl.bind("<Enter>",    lambda e, l=lbl: l.config(bg="#eff6ff", fg="#1d4ed8"))
                        lbl.bind("<Leave>",    lambda e, l=lbl: l.config(bg="#ffffff", fg="#111827"))
                        lbl.bind("<Button-1>", lambda e, v=g: (var.set(v), _close_popup(),
                                                                genre_entry.focus_set()))
                    popup.bind("<FocusOut>", lambda e: _close_popup())
                    popup.bind("<Escape>",   lambda e: _close_popup())
                    popup.focus_set()

                # Clic zone flèche (droite) → ouvre liste ; ailleurs → focus entry
                def _on_canvas_click(e):
                    if e.x >= cb_cvs.winfo_width() - ARROW_W - 4:
                        _open_popup()
                    else:
                        genre_entry.focus_set()

                cb_cvs.bind("<Button-1>", _on_canvas_click)

                # Hover sur la zone flèche
                def _on_motion(e):
                    in_arrow = e.x >= cb_cvs.winfo_width() - ARROW_W - 4
                    if in_arrow != _st["arrow_hover"]:
                        _st["arrow_hover"] = in_arrow
                        cb_cvs.config(cursor="hand2" if in_arrow else "xterm")
                        _draw_cb()

                cb_cvs.bind("<Motion>", _on_motion)
                cb_cvs.bind("<Leave>",  lambda e: (_st.update(arrow_hover=False), _draw_cb()))

                # Focus entry → bordure bleue
                genre_entry.bind("<FocusIn>",  lambda _e: (_st.update(focus=True),  _draw_cb()))
                genre_entry.bind("<FocusOut>", lambda _e: (_st.update(focus=False), _draw_cb()))
                # ↓ / F4 ouvrent la liste
                genre_entry.bind("<Down>", lambda e: _open_popup())
                genre_entry.bind("<F4>",   lambda e: _open_popup())

                cb_cvs.set = lambda v: var.set(v)
                cb_cvs._genre_entry = genre_entry
                cb_cvs._draw = _draw_cb
                cb_cvs._st   = _st
                return cb_cvs

            # Champ arrondi via Canvas (même technique que la barre de recherche)
            FIELD_BG = "#f3f4f6"
            FIELD_H  = 36
            F_RADIUS = 10

            def _rr_field(cvs, x1, y1, x2, y2, r, **kw):
                pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
                       x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
                       x1, y2, x1, y2-r, x1, y1+r, x1, y1]
                cvs.create_polygon(pts, smooth=True, splinesteps=24, **kw)

            field_cvs = tk.Canvas(box, height=FIELD_H, bg="#ffffff",
                                  highlightthickness=0, bd=0)
            field_cvs.pack(fill=tk.X)

            entry = tk.Entry(
                field_cvs,
                textvariable=var,
                bd=0, relief=tk.FLAT,
                font=("Segoe UI", 10),
                bg=FIELD_BG, fg="#111827",
                insertbackground="#111827",
                highlightthickness=0,
            )
            entry_win = field_cvs.create_window(0, 0, anchor="nw", window=entry)
            focus_st = {"on": False}

            def _make_redraw(cvs, ew, fs, fh, fr, fbg):
                def _redraw(w_=None):
                    if w_ is None:
                        w_ = cvs.winfo_width()
                    if w_ < 4:
                        return
                    cvs.delete("bg_shape")
                    border = "#93c5fd" if fs["on"] else "#d1d5db"
                    _rr_field(cvs, 1, 1, w_-1, fh-1, fr,
                              fill=fbg, outline=border, width=1, tags="bg_shape")
                    cvs.tag_lower("bg_shape")
                    px, py = 10, 5
                    cvs.coords(ew, px, py)
                    cvs.itemconfigure(ew, width=max(w_ - px*2, 10), height=fh - 2*py)
                return _redraw

            redraw = _make_redraw(field_cvs, entry_win, focus_st, FIELD_H, F_RADIUS, FIELD_BG)
            field_cvs.bind("<Configure>", lambda e, rd=redraw: rd(e.width))
            field_cvs.bind("<Button-1>",  lambda _, e=entry: e.focus_set())
            entry.bind("<FocusIn>",  lambda _e, fs=focus_st, rd=redraw: (fs.update(on=True),  rd()))
            entry.bind("<FocusOut>", lambda _e, fs=focus_st, rd=redraw: (fs.update(on=False), rd()))

            return entry

        self.titre_entry  = field(wrap, "Titre",  self.var_titre,  row=1, col=0)
        self.auteur_entry = field(wrap, "Auteur", self.var_auteur, row=1, col=1)
        self.annee_entry  = field(wrap, "Année",  self.var_annee,  row=2, col=0)
        self.genre_combo  = field(wrap, "Genre",  self.var_genre,  row=2, col=1, widget="combo")

        # Canvas parents pour surbrillance verte
        self._field_canvases = [
            self.titre_entry.master,
            self.auteur_entry.master,
            self.annee_entry.master,
            self.genre_combo,
        ]

        info_required = tk.Label(
            wrap,
            text="(* champs obligatoires)",
            font=("Segoe UI", 8),
            bg="#ffffff",
            fg="#ef4444",
        )
        info_required.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Placeholders
        self._attach_placeholder(self.titre_entry, "Ex : Les Misérables")
        self._attach_placeholder(self.auteur_entry, "Ex : Victor Hugo")
        self._attach_placeholder(self.annee_entry, "Ex : 1862")

    # ═════════════════════════════════════════════════════════════════════════
    # SEARCH SECTION — repris du fichier de référence (Canvas arrondi + pill)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_search_section(self):
        card = _RoundedCard(self.page, radius=16, bg="#ffffff",
                            border="#d1d5db", padding=10, height=62)
        card.pack(fill=tk.X, padx=6, pady=(0, 10))
        inner = card.content

        FG_HINT   = "#9ca3af"
        FG_NORMAL = "#111827"
        FIELD_BG  = "#f3f4f6"
        RADIUS    = 16
        BTN_W, BTN_H = 138, 38

        def _rr(cvs, x1, y1, x2, y2, r, **kw):
            pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
                   x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
                   x1, y2, x1, y2-r, x1, y1+r, x1, y1]
            cvs.create_polygon(pts, smooth=True, splinesteps=24, **kw)

        def _lighten(hex_c, amt):
            hx = hex_c.lstrip("#")
            r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
            return "#{:02x}{:02x}{:02x}".format(
                min(255, int(r + (255 - r) * amt)),
                min(255, int(g + (255 - g) * amt)),
                min(255, int(b + (255 - b) * amt)))

        # Canvas pour le champ arrondi
        FIELD_H = 38
        field_cvs = tk.Canvas(inner, height=FIELD_H, bg="#ffffff",
                              highlightthickness=0, bd=0)
        field_cvs.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.search_entry = tk.Entry(
            field_cvs,
            textvariable=self.var_recherche,
            bd=0, relief=tk.FLAT,
            font=("Segoe UI", 11),
            bg=FIELD_BG, fg=FG_HINT,
            insertbackground=FG_NORMAL,
            highlightthickness=0,
        )
        entry_win = field_cvs.create_window(0, 0, anchor="nw", window=self.search_entry)

        focus_state = {"on": False}

        def _redraw_field(w=None):
            if w is None:
                w = field_cvs.winfo_width()
            if w < 4:
                return
            field_cvs.delete("bg_shape")
            border = "#93c5fd" if focus_state["on"] else "#d1d5db"
            _rr(field_cvs, 1, 1, w-1, FIELD_H-1, RADIUS,
                fill=FIELD_BG, outline=border, width=1, tags="bg_shape")
            field_cvs.tag_lower("bg_shape")
            pad_x, pad_y = 32, 5
            field_cvs.coords(entry_win, pad_x, pad_y)
            field_cvs.itemconfigure(entry_win,
                                    width=max(w - pad_x - 8, 10),
                                    height=FIELD_H - 2 * pad_y)
            field_cvs.delete("icon")
            field_cvs.create_text(16, FIELD_H // 2, text="🔍",
                                  font=("Segoe UI", 11), fill="#6b7280",
                                  tags="icon")
            field_cvs.tag_raise("icon")

        field_cvs.bind("<Configure>", lambda e: _redraw_field(e.width))
        field_cvs.bind("<Button-1>", lambda _: self.search_entry.focus_set())

        self.search_entry.insert(0, self._SEARCH_PLACEHOLDER)

        def on_focus_in(_e):
            focus_state["on"] = True
            _redraw_field()
            if self.search_entry.get() == self._SEARCH_PLACEHOLDER:
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg=FG_NORMAL)

        def on_focus_out(_e):
            focus_state["on"] = False
            _redraw_field()
            if self.search_entry.get().strip() == "":
                self.search_entry.insert(0, self._SEARCH_PLACEHOLDER)
                self.search_entry.config(fg=FG_HINT)

        self.search_entry.bind("<FocusIn>",  on_focus_in)
        self.search_entry.bind("<FocusOut>", on_focus_out)

        # Bouton Rechercher — style pill
        self.search_button = tk.Canvas(inner, width=BTN_W, height=BTN_H,
                                       highlightthickness=0, bd=0,
                                       bg="#ffffff", cursor="hand2")
        self.search_button.pack(side=tk.RIGHT)

        btn_state = {"hovered": False}

        def _draw_btn():
            self.search_button.delete("all")
            fill = _lighten("#dbeafe", 0.06) if btn_state["hovered"] else "#dbeafe"
            _rr(self.search_button, 1, 1, BTN_W-1, BTN_H-1, RADIUS,
                fill=fill, outline="#111827", width=1)
            self.search_button.create_text(BTN_W // 2, BTN_H // 2,
                                           text=" Rechercher",
                                           font=("Segoe UI", 10, "bold"),
                                           fill="#1d4ed8")

        self.search_button.bind("<Enter>", lambda _: (btn_state.update(hovered=True),  _draw_btn()))
        self.search_button.bind("<Leave>", lambda _: (btn_state.update(hovered=False), _draw_btn()))
        _draw_btn()

    def _build_list_section(self):
        card = _RoundedCard(self.page, radius=16, bg="#ffffff", border="#d1d5db", padding=12)
        card.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 12))

        table_wrap = card.content

        columns = ("ID", "Titre", "Auteur", "Année", "Genre")
        self.tree = ttk.Treeview(
            table_wrap,
            columns=columns,
            show="headings",
            style="Books.Treeview",
        )

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("ID", width=70, anchor=tk.CENTER, stretch=False)
        self.tree.column("Titre", width=340, anchor=tk.CENTER)
        self.tree.column("Auteur", width=260, anchor=tk.CENTER)
        self.tree.column("Année", width=120, anchor=tk.CENTER, stretch=False)
        self.tree.column("Genre", width=180, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(table_wrap, orient=tk.VERTICAL, command=self.tree.yview, style="Vertical.TScrollbar")
        hsb = ttk.Scrollbar(table_wrap, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        table_wrap.rowconfigure(0, weight=1)
        table_wrap.columnconfigure(0, weight=1)

        # Alternance lignes (jaune / blanc)
        self.tree.tag_configure("odd", background="#fff8e1")
        self.tree.tag_configure("even", background="#ffffff")

    # ═════════════════════════════════════════════════════════════════════════
    # ACTION BUTTONS — repris du fichier de référence (Canvas pill, selectable)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_action_buttons(self):
        bar = tk.Frame(self.page, bg="#e9edf3")
        bar.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=(8, 0))

        # LEFT group : Ajouter + Réinitialiser
        left = tk.Frame(bar, bg="#e9edf3")
        left.pack(side=tk.LEFT)

        # MIDDLE group : Modifier + Supprimer + Afficher tout
        mid = tk.Frame(bar, bg="#e9edf3")
        mid.pack(side=tk.LEFT, expand=True)

        # RIGHT group : Quitter
        right = tk.Frame(bar, bg="#e9edf3")
        right.pack(side=tk.RIGHT)

        RADIUS = 14
        BG     = "#e9edf3"

        def _lighten(hex_c, amt):
            hx = hex_c.lstrip("#")
            r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
            return "#{:02x}{:02x}{:02x}".format(
                min(255, int(r + (255 - r) * amt)),
                min(255, int(g + (255 - g) * amt)),
                min(255, int(b + (255 - b) * amt)))

        def _round_rect(cvs, x1, y1, x2, y2, r, **kw):
            pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
                   x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
                   x1, y2, x1, y2-r, x1, y1+r, x1, y1]
            cvs.create_polygon(pts, smooth=True, splinesteps=24, **kw)

        # selectable=True  → grisé quand aucune sélection dans le tableau
        # selectable=False → toujours actif
        def mk_btn(parent, text, text_color, bg_color,
                   w=148, h=40, font=("Segoe UI", 10, "bold"),
                   selectable=False):
            cvs = tk.Canvas(parent, width=w, height=h,
                            highlightthickness=0, bd=0, bg=BG)
            state = {"active": not selectable, "hovered": False}

            def _draw():
                cvs.delete("all")
                is_on = state["active"]
                fill  = _lighten(bg_color, 0.06) if state["hovered"] and is_on else bg_color
                txt   = text_color if is_on else "#b0b5be"
                _round_rect(cvs, 2, 2, w-2, h-2, RADIUS,
                            fill=fill, outline="#111827", width=1)
                cvs.create_text(w // 2, h // 2, text=text, font=font, fill=txt)

            def _enter(_=None):
                state["hovered"] = True
                cvs.config(cursor="hand2" if state["active"] else "arrow")
                _draw()

            def _leave(_=None):
                state["hovered"] = False
                _draw()

            def set_active(val: bool):
                state["active"] = val
                cvs.config(cursor="hand2" if val else "arrow")
                _draw()

            cvs.bind("<Enter>", _enter)
            cvs.bind("<Leave>", _leave)
            _draw()
            return cvs, set_active

        # LEFT : Ajouter + Réinitialiser
        self.add_btn, _ = mk_btn(left, "➕  Ajouter",        "#15803d", "#dcfce7")
        self.add_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_btn, _ = mk_btn(left, "↺  Annuler", "#374151", "#e5e7eb", w=158)
        self.clear_btn.pack(side=tk.LEFT)

        # MIDDLE : Modifier + Supprimer + Afficher tout
        self.modify_btn, self._set_modify_state = mk_btn(
            mid, "✏  Modifier", "#b45309", "#fef9c3", selectable=True)
        self.modify_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.delete_btn, self._set_delete_state = mk_btn(
            mid, "🗑  Supprimer", "#b91c1c", "#fee2e2", selectable=True)
        self.delete_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.show_all_btn, _ = mk_btn(mid, "📋  Afficher tout", "#1d4ed8", "#dbeafe", w=158)
        self.show_all_btn.pack(side=tk.LEFT)

        # RIGHT : Quitter
        self.quit_btn, _ = mk_btn(right, "✖  Quitter", "#7f1d1d", "#fecaca")
        self.quit_btn.pack(side=tk.LEFT)

    # helper — toggle Modifier/Supprimer selon sélection tableau
    def _update_selection_buttons(self, has_selection: bool):
        try:
            self._set_modify_state(has_selection)
            self._set_delete_state(has_selection)
        except AttributeError:
            pass

    # ----------------- Surbrillance champs -----------------

    def highlight_fields(self):
        """Bordure verte fine sur tous les champs — reste jusqu'à désélection."""
        # Champs Entry normaux
        for cvs in self._field_canvases[:-1]:
            try:
                w_, h_ = cvs.winfo_width(), cvs.winfo_height()
                if w_ < 4: continue
                cvs.delete("bg_shape")
                r = 10
                x1, y1, x2, y2 = 1, 1, w_-1, h_-1
                pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
                       x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
                cvs.create_polygon(pts, smooth=True, splinesteps=24,
                                   fill="#f3f4f6", outline="#16a34a",
                                   width=1, tags="bg_shape")
                cvs.tag_lower("bg_shape")
                for item in cvs.find_all():
                    if cvs.type(item) == "window":
                        cvs.coords(item, 10, 4)
                        cvs.itemconfigure(item, width=max(w_-20, 10), height=max(h_-8, 10))
            except Exception:
                pass
        # Combo genre — utilise son propre _draw avec flag green
        try:
            self.genre_combo._st["green"] = True
            self.genre_combo._draw()
        except Exception:
            pass

    def reset_fields_highlight(self):
        """Remet la bordure grise normale."""
        for cvs in self._field_canvases[:-1]:
            try:
                w_, h_ = cvs.winfo_width(), cvs.winfo_height()
                if w_ < 4: continue
                cvs.delete("bg_shape")
                r = 10
                x1, y1, x2, y2 = 1, 1, w_-1, h_-1
                pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
                       x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
                cvs.create_polygon(pts, smooth=True, splinesteps=24,
                                   fill="#f3f4f6", outline="#d1d5db",
                                   width=1, tags="bg_shape")
                cvs.tag_lower("bg_shape")
                for item in cvs.find_all():
                    if cvs.type(item) == "window":
                        cvs.coords(item, 10, 4)
                        cvs.itemconfigure(item, width=max(w_-20, 10), height=max(h_-8, 10))
            except Exception:
                pass
        try:
            self.genre_combo._st["green"] = False
            self.genre_combo._draw()
        except Exception:
            pass

    # ----------------- API vue (contrôleur) -----------------

    def get_inputs(self) -> Tuple[str, str, str, str]:
        titre = self.var_titre.get().strip()
        auteur = self.var_auteur.get().strip()
        annee = self.var_annee.get().strip()
        genre = self.var_genre.get().strip()

        if self._is_placeholder(titre):
            titre = ""
        if self._is_placeholder(auteur):
            auteur = ""
        if self._is_placeholder(annee):
            annee = ""
        if genre == "Sélectionner un genre":
            genre = ""

        return (titre, auteur, annee, genre)

    def set_inputs(self, titre: str, auteur: str, annee: str, genre: str):
        self.var_titre.set(titre or "")
        self.var_auteur.set(auteur or "")
        self.var_annee.set(str(annee) if annee is not None else "")

        if genre:
            self.var_genre.set(genre)
        else:
            self.var_genre.set("")

        self._attach_placeholder(self.titre_entry, "Ex : Les Misérables")
        self._attach_placeholder(self.auteur_entry, "Ex : Victor Hugo")
        self._attach_placeholder(self.annee_entry, "Ex : 1862")

    def clear_inputs(self):
        self.var_titre.set("")
        self.var_auteur.set("")
        self.var_annee.set("")
        self.var_genre.set("")
        try:
            self.genre_combo.set("")
        except Exception:
            pass

        self._attach_placeholder(self.titre_entry, "Ex : Les Misérables")
        self._attach_placeholder(self.auteur_entry, "Ex : Victor Hugo")
        self._attach_placeholder(self.annee_entry, "Ex : 1862")

    def get_search_text(self) -> str:
        text = self.var_recherche.get().strip()
        if text == self._SEARCH_PLACEHOLDER:
            return ""
        return text

    def afficher_liste(self, livres: list):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, livre in enumerate(livres):
            id_livre, titre, auteur, annee, genre = livre
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=(id_livre, titre, auteur, annee, genre), tags=(tag,))

    def get_selected_book(self) -> Optional[int]:
        selection = self.tree.selection()
        if not selection:
            return None
        item = self.tree.item(selection[0])
        try:
            return int(item["values"][0])
        except Exception:
            return None

    def clear_selection(self):
        """Supprime la sélection dans le tableau"""
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # ----------------- Dialogs -----------------

    def show_info(self, titre: str, message: str):
        messagebox.showinfo(titre, message)

    def show_error(self, titre: str, message: str):
        messagebox.showerror(titre, message)

    def ask_confirmation(self, titre: str, message: str) -> bool:
        return messagebox.askyesno(titre, message)

    # ----------------- Bindings -----------------

    def bind_add_button(self, callback: Callable):
        self.add_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_modify_button(self, callback: Callable):
        self.modify_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_delete_button(self, callback: Callable):
        self.delete_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_show_all_button(self, callback: Callable):
        self.show_all_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_search_button(self, callback: Callable):
        self.search_button.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_clear_button(self, callback: Callable):
        self.clear_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_quit_button(self, callback: Callable):
        self.quit_btn.bind("<ButtonRelease-1>", lambda _e: callback())

    def bind_tree_selection(self, callback: Callable):
        def _on_select(_e):
            has = bool(self.tree.selection())
            self._update_selection_buttons(has)
            callback()
            if has:
                self.root.after(50, self.highlight_fields)
            else:
                self.reset_fields_highlight()
        self.tree.bind("<<TreeviewSelect>>", _on_select)


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None

        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
        y = self.widget.winfo_rooty() + 4

        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            bg="#FFFFFF",
            fg="black",
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#4b5563",
        )
        label.pack()

    def hide(self, _event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None