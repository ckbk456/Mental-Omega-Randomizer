"""Tk theme application for the launcher window."""

import tkinter as tk
from tkinter import font as tkfont


def _apply_checkbox_indicators(self, palette, accent, accent_text):
    """A clear tick and a distinct partial-selection bar at the current DPI."""
    size = max(16, round(16 * self.winfo_fpixels('1i') / 96))
    key = (self.dark_mode_var.get(), size, accent, palette['field'], palette['border'])
    cache = getattr(self, '_modern_checkbox_images', {})
    if key not in cache:
        def picture(mark=None, disabled=False):
            # Transparent space belongs to the indicator so every label keeps
            # a readable gap, including colored matrix headers and counts.
            photo = tk.PhotoImage(master=self, width=size + max(5, round(size * .35)), height=size)
            scale = size / 16
            border = palette['muted'] if not disabled else palette['border']
            fill = (palette['panel'] if disabled else accent) if mark else palette['field']
            ink = palette['muted'] if disabled else accent_text
            photo.put(border, to=(0, 0, size, size))
            edge = max(1, round(scale))
            photo.put(fill, to=(edge, edge, size-edge, size-edge))
            if mark == 'partial':
                photo.put(ink, to=(round(4*scale), round(7*scale),
                                   round(12*scale), round(9*scale)))
            elif mark == 'tick':
                for x, y in ((3, 8), (4, 9), (5, 10), (6, 11),
                             (7, 10), (8, 9), (9, 8), (10, 7), (11, 6), (12, 5)):
                    photo.put(ink, to=(round(x*scale), round(y*scale),
                                      min(size, round((x+2)*scale)),
                                      min(size, round((y+2)*scale))))
            return photo

        images = [picture(), picture('tick'), picture('partial'),
                  picture(disabled=True), picture('tick', True), picture('partial', True)]
        element = f'Modern{len(cache)}.Checkbutton.indicator'
        self.style.element_create(
            element, 'image', images[0],
            ('disabled', 'alternate', images[5]), ('disabled', 'selected', images[4]),
            ('disabled', images[3]), ('alternate', images[2]), ('selected', images[1]),
            sticky='',
        )
        cache[key] = (element, images)
        self._modern_checkbox_images = cache
    self.style.layout('TCheckbutton', [
        ('Checkbutton.padding', {'sticky': 'nswe', 'children': [
            (cache[key][0], {'side': 'left', 'sticky': ''}),
            ('Checkbutton.focus', {'side': 'left', 'sticky': 'w', 'children': [
                ('Checkbutton.label', {'sticky': 'nswe'}),
            ]}),
        ]}),
    ])


def _apply_type_and_native_surfaces(self, palette):
    """Make menus, text surfaces and future dialogs match the ttk theme."""
    if not getattr(self, '_modern_fonts_initialized', False):
        for name, size, weight in (
            ('TkDefaultFont', 10, 'normal'), ('TkTextFont', 10, 'normal'),
            ('TkMenuFont', 10, 'normal'), ('TkHeadingFont', 10, 'bold'),
            ('TkCaptionFont', 10, 'bold'), ('TkSmallCaptionFont', 9, 'normal'),
            ('TkTooltipFont', 9, 'normal'),
        ):
            try:
                tkfont.nametofont(name, root=self).configure(
                    family='Segoe UI', size=size, weight=weight)
            except tk.TclError:
                pass
        self._modern_fonts_initialized = True
    self.option_add('*Toplevel.background', palette['background'])
    self.option_add('*Menu.background', palette['panel'])
    self.option_add('*Menu.foreground', palette['foreground'])
    self.option_add('*Menu.activeBackground', palette['select'])
    self.option_add('*Menu.activeForeground', palette['select_foreground'])
    self.option_add('*Menu.relief', 'flat')
    self.option_add('*Menu.borderWidth', 1)
    self.option_add('*Text.font', 'TkTextFont')
    self.option_add('*Text.highlightThickness', 0)
    self.option_add('*Text.borderWidth', 0)

    def visit(widget):
        # Faction tiles intentionally keep their native colors and animation.
        if isinstance(widget, (tk.Text, tk.Listbox)):
            widget.configure(
                background=palette['field'], foreground=palette['foreground'],
                selectbackground=palette['select'],
                selectforeground=palette['select_foreground'],
                relief='flat', borderwidth=0,
                highlightthickness=1, highlightbackground=palette['border'],
                highlightcolor=palette['select'],
            )
            if isinstance(widget, tk.Text):
                widget.configure(insertbackground=palette['foreground'], padx=10, pady=8)
        elif isinstance(widget, tk.Menu):
            widget.configure(
                background=palette['panel'], foreground=palette['foreground'],
                activebackground=palette['select'],
                activeforeground=palette['select_foreground'],
                relief='flat', borderwidth=1,
            )
        for child in widget.winfo_children():
            visit(child)

    visit(self)


def apply_color_mode(self):
    """Apply the current launcher palette to all constructed widgets."""
    palette = self.ui_palette()
    style = self.style
    # Native Windows themes ignore several color and state overrides. Clam
    # honors the complete palette in both modes and keeps tab geometry stable.
    target_theme = 'clam'
    if target_theme in style.theme_names() and style.theme_use() != target_theme:
        style.theme_use(target_theme)

    background = palette['background']
    panel = palette['panel']
    foreground = palette['foreground']
    field = palette['field']
    border = palette['border']
    selected = palette['select']
    selected_foreground = palette['select_foreground']
    self.configure(background=background)
    _apply_type_and_native_surfaces(self, palette)

    accent = '#4ed1c0' if self.dark_mode_var.get() else '#127b71'
    accent_text = '#092622' if self.dark_mode_var.get() else '#ffffff'
    accent_hover = '#79e1d4' if self.dark_mode_var.get() else '#0d665e'
    style.configure('.', font='TkDefaultFont', bordercolor=border,
                    lightcolor=border, darkcolor=border, focuscolor=selected)

    style.configure('TFrame', background=background)
    style.configure('TLabel', background=background, foreground=foreground)
    style.configure('Muted.TLabel', background=background, foreground=palette['muted'])
    style.configure('Section.TLabel', background=background, foreground=foreground,
                    font=('Segoe UI', 12, 'bold'))
    style.configure('Eyebrow.TLabel', background=background, foreground=palette['muted'],
                    font=('Segoe UI', 8, 'bold'))
    style.configure('Pool.Summary.TLabel', background=background, foreground=accent,
                    font=('Segoe UI', 10, 'bold'))
    style.configure('Tooltip.TLabel', background=panel, foreground=foreground,
                    bordercolor=border, borderwidth=1, padding=(12, 9),
                    font=('Segoe UI', 9))
    shop_colors = {
        'Stage': '#79c0ff' if self.dark_mode_var.get() else '#0969da',
        'Status': '#7ee787' if self.dark_mode_var.get() else '#1a7f37',
        'Ore': '#f2cc60' if self.dark_mode_var.get() else '#9a6700',
        'Gem': '#d2a8ff' if self.dark_mode_var.get() else '#8250df',
        'Reroll': '#76e3ea' if self.dark_mode_var.get() else '#096b72',
        'Reward': '#f2cc60' if self.dark_mode_var.get() else '#825800',
        'Help': '#79c0ff' if self.dark_mode_var.get() else '#0550ae',
        'PlayerBuff': '#7ee787' if self.dark_mode_var.get() else '#1a7f37',
        'EnemyBuff': '#ff7b72' if self.dark_mode_var.get() else '#cf222e',
    }
    for name, color in shop_colors.items():
        style.configure(
            f'Shop.{name}.TLabel', background=background, foreground=color
        )
    shop_difficulty_colors = {
        'Casual': '#7ee787' if self.dark_mode_var.get() else '#1a7f37',
        'Normal': '#ffa657' if self.dark_mode_var.get() else '#bc4c00',
        'Mental': '#ff7b72' if self.dark_mode_var.get() else '#cf222e',
    }
    for name, color in shop_difficulty_colors.items():
        style.configure(
            f'Shop.Difficulty.{name}.TLabel',
            background=background,
            foreground=color,
        )
    style.configure(
        'Archipelago.Disconnected.TLabel',
        background=background,
        foreground='#ff6b6b' if self.dark_mode_var.get() else '#b00020',
    )
    style.configure(
        'Archipelago.Connected.TLabel',
        background=background,
        foreground='#55d67a' if self.dark_mode_var.get() else '#087a2f',
    )
    style.configure(
        'Archipelago.Waiting.TLabel',
        background=background,
        foreground='#f0c75e' if self.dark_mode_var.get() else '#8a5a00',
    )
    style.configure(
        'Error.TLabel',
        background=background,
        foreground='#ff7b72' if self.dark_mode_var.get() else '#b00020',
    )
    # ttk's canonical style name uses a lowercase "f". The old spelling
    # configured an unused style and left Settings group interiors light.
    style.configure('TLabelframe', background=background, bordercolor=border,
                    borderwidth=1, relief='solid')
    style.configure('TLabelframe.Label', background=background, foreground=foreground,
                    font=('Segoe UI', 11, 'bold'))
    style.configure('TCheckbutton', background=background, foreground=foreground,
                    padding=(0, 3), focusthickness=1)
    self.ensure_checkbutton_indicator()
    _apply_checkbox_indicators(self, palette, accent, accent_text)
    style.configure('TRadiobutton', background=background, foreground=foreground, padding=(0, 3))
    style.configure('TButton', background=panel, foreground=foreground, bordercolor=border,
                    borderwidth=1, relief='flat', padding=(12, 7), focusthickness=1)
    style.configure('Compact.TButton', padding=(8, 5), font=('Segoe UI', 9))
    style.configure('TMenubutton', background=panel, foreground=foreground,
                    bordercolor=border, borderwidth=1, relief='flat',
                    padding=(10, 7), arrowcolor=foreground)
    style.map('TMenubutton', background=[('active', selected)],
              foreground=[('disabled', palette['muted']), ('active', selected_foreground)])
    for name in ('Primary.TButton', 'Launch.TButton', 'Shop.StartNewRun.TButton'):
        style.configure(name, background=accent, foreground=accent_text,
                        bordercolor=accent, padding=(16, 9), font=('Segoe UI', 10, 'bold'))
        style.map(name, background=[('disabled', panel), ('pressed', accent_hover),
                                    ('active', accent_hover)],
                  foreground=[('disabled', palette['muted']), ('!disabled', accent_text)],
                  bordercolor=[('focus', foreground), ('!focus', accent)])
    for faction, color in {
        'Allies': '#78b6f7', 'Soviets': '#ff9298', 'Epsilon': '#c7a0f7',
        'Foehn': '#59d2c6', 'Mixed': '#f1cc7c',
    }.items():
        if not self.dark_mode_var.get():
            color = {'Allies': '#285f9e', 'Soviets': '#a53636', 'Epsilon': '#70429a',
                     'Foehn': '#087b75', 'Mixed': '#806018'}[faction]
        style.configure(f'Pool.{faction}.TCheckbutton', foreground=color)
        style.map(f'Pool.{faction}.TCheckbutton',
                  foreground=[('disabled', palette['muted']), ('!disabled', color)])
    style.configure(
        'Danger.TButton',
        background='#5c2327' if self.dark_mode_var.get() else '#ffebe9',
        foreground='#ffb3b8' if self.dark_mode_var.get() else '#cf222e',
        bordercolor='#f85149' if self.dark_mode_var.get() else '#cf222e',
    )
    style.map(
        'Danger.TButton',
        background=[
            ('disabled', panel),
            ('active', '#8b3036' if self.dark_mode_var.get() else '#ffcecb'),
        ],
        foreground=[('disabled', palette['muted'])],
    )
    style.map(
        'TButton',
        background=[
            ('disabled', panel), ('active', selected), ('pressed', selected),
        ],
        foreground=[
            ('disabled', palette['muted']),
            ('active', selected_foreground),
            ('pressed', selected_foreground),
        ],
    )
    style.map(
        'TCheckbutton',
        background=[('disabled', background), ('active', background)],
        foreground=[('disabled', palette['muted']), ('active', foreground)],
    )
    style.map(
        'TRadiobutton',
        background=[('disabled', background), ('active', background)],
        foreground=[('disabled', palette['muted']), ('active', foreground)],
    )
    style.configure('TEntry', fieldbackground=field, foreground=foreground, insertcolor=foreground,
                    borderwidth=1, padding=(8, 6))
    style.configure('TSpinbox', fieldbackground=field, foreground=foreground, arrowcolor=foreground,
                    borderwidth=1, padding=(8, 6), arrowsize=12)
    style.map(
        'TEntry',
        fieldbackground=[('disabled', field)],
        foreground=[('disabled', foreground)],
    )
    style.map(
        'TSpinbox',
        fieldbackground=[('disabled', field)],
        background=[('disabled', panel)],
        foreground=[('disabled', foreground)],
        arrowcolor=[('disabled', foreground)],
    )
    style.configure(
        'TCombobox',
        fieldbackground=field,
        background=panel,
        foreground=foreground,
        arrowcolor=foreground,
        padding=(8, 6),
        arrowsize=12,
        borderwidth=1,
    )
    # ttk combobox popdowns are Tk Listboxes, not ttk widgets. Keep their
    # palette aligned with the themed field instead of using native light
    # colors in dark mode.
    self.option_add('*TCombobox*Listbox.background', field)
    self.option_add('*TCombobox*Listbox.foreground', foreground)
    self.option_add('*TCombobox*Listbox.selectBackground', selected)
    self.option_add(
        '*TCombobox*Listbox.selectForeground', selected_foreground
    )
    for combo_map_name in (
        'advanced_unit_bulk_buff_combos',
        'advanced_power_bulk_buff_combos',
    ):
        for combo in getattr(self, combo_map_name, {}).values():
            try:
                popdown = self.tk.call(
                    'ttk::combobox::PopdownWindow', str(combo)
                )
                listbox = f'{popdown}.f.l'
                self.tk.call(
                    listbox,
                    'configure',
                    '-background', field,
                    '-foreground', foreground,
                    '-selectbackground', selected,
                    '-selectforeground', selected_foreground,
                )
            except Exception:
                pass
    style.map(
        'TCombobox',
        fieldbackground=[('disabled', field), ('readonly', field)],
        background=[('disabled', panel)],
        foreground=[('disabled', foreground), ('readonly', foreground)],
        arrowcolor=[('disabled', foreground)],
        selectbackground=[('readonly', selected)],
        selectforeground=[('readonly', selected_foreground)],
    )
    style.configure('TNotebook', background=background, bordercolor=border, borderwidth=1)
    style.configure(
        'TNotebook.Tab',
        background=panel,
        foreground=foreground,
        padding=(8, 6),
    )
    style.map(
        'TNotebook.Tab',
        background=[
            ('selected', selected),
            ('active', palette['canvas']),
            ('disabled', panel),
        ],
        foreground=[
            ('selected', selected_foreground),
            ('active', foreground),
            ('disabled', palette['muted']),
        ],
        padding=[('selected', (8, 6)), ('active', (8, 6))],
    )
    style.configure('Randomizer.TNotebook', background=background, bordercolor=border, tabposition='nw')
    style.configure(
        'Randomizer.TNotebook.Tab',
        background=panel,
        foreground=foreground,
        padding=(16, 10),
        font=('Segoe UI', 10, 'bold'),
    )
    style.map(
        'Randomizer.TNotebook.Tab',
        background=[
            ('selected', selected),
            ('active', palette['canvas']),
            ('disabled', panel),
        ],
        foreground=[
            ('selected', selected_foreground),
            ('active', foreground),
            ('disabled', palette['muted']),
        ],
        padding=[('selected', (16, 10)), ('active', (16, 10))],
    )
    style.configure('Info.TNotebook', background=background, bordercolor=border, tabposition='nw')
    style.configure(
        'Info.TNotebook.Tab',
        background=panel,
        foreground=foreground,
        padding=(7, 5),
        font=('Segoe UI', 9, 'bold'),
    )
    style.map(
        'Info.TNotebook.Tab',
        background=[
            ('selected', selected),
            ('active', palette['canvas']),
            ('disabled', panel),
        ],
        foreground=[
            ('selected', selected_foreground),
            ('active', foreground),
            ('disabled', palette['muted']),
        ],
        padding=[('selected', (7, 5)), ('active', (7, 5))],
    )
    style.configure('Unlocks.TNotebook', background=background, bordercolor=border, tabposition='nw')
    style.configure(
        'Unlocks.TNotebook.Tab',
        background=panel,
        foreground=foreground,
        padding=(4, 5),
        font=('Segoe UI', 9, 'bold'),
    )
    style.map(
        'Unlocks.TNotebook.Tab',
        background=[
            ('selected', selected),
            ('active', palette['canvas']),
            ('disabled', panel),
        ],
        foreground=[
            ('selected', selected_foreground),
            ('active', foreground),
            ('disabled', palette['muted']),
        ],
        padding=[('selected', (4, 5)), ('active', (4, 5))],
    )
    style.configure(
        'Treeview',
        background=field,
        fieldbackground=field,
        foreground=foreground,
        bordercolor=border,
        borderwidth=0,
        rowheight=30,
        font=('Segoe UI', 10),
    )
    style.configure('StartingUnlocks.Treeview', rowheight=52)
    style.configure('ShopCameo.Treeview', rowheight=52)
    style.map(
        'Treeview',
        background=[('selected', selected)],
        foreground=[('selected', selected_foreground)],
    )
    style.configure('Treeview.Heading', background=panel, foreground=palette['muted'],
                    bordercolor=border, relief='flat', padding=(8, 9),
                    font=('Segoe UI', 9, 'bold'))
    style.map('Treeview.Heading', background=[('active', palette['canvas'])])
    if hasattr(self, 'configure_shop_tree_tags'):
        self.configure_shop_tree_tags()
    style.configure(
        'TScrollbar',
        background=panel,
        troughcolor=background,
        bordercolor=border,
        arrowcolor=foreground,
        arrowsize=12,
        borderwidth=0,
        relief='flat',
    )
    style.configure('TSeparator', background=border)
    style.configure('TProgressbar', background=accent, troughcolor=field,
                    bordercolor=field, lightcolor=accent, darkcolor=accent)

    if hasattr(self, 'missions_tree'):
        self.missions_tree.tag_configure(
            'completed',
            background='#244a32' if self.dark_mode_var.get() else '#dff2df',
            foreground='#b8efc5' if self.dark_mode_var.get() else '#176b2c',
        )
        self.missions_tree.tag_configure(
            'unlock_available',
            foreground='#65f58c' if self.dark_mode_var.get() else '#087a2f',
            font=('Segoe UI', 9, 'bold underline'),
        )
    if hasattr(self, 'enemy_buff_catalogue_frame'):
        self._enemy_buffs_view_dirty = True
        if self.enemy_buffs_view_visible():
            self.after_idle(self.refresh_enemy_buffs_view)
    for canvas_name in (
        'settings_canvas', 'grid_canvas', 'shop_canvas', 'enemy_buffs_canvas'
    ):
        canvas = getattr(self, canvas_name, None)
        if canvas is not None:
            canvas.configure(background=palette['canvas'])
    for card in getattr(self, 'shop_mission_cards', ()):
        card['detail_canvas'].configure(background=background)
    for canvas in getattr(self, 'advanced_pool_canvases', {}).values():
        canvas.configure(background=palette['canvas'])
    for slider in getattr(self, 'reward_weight_slider_controls', ()):
        slider.refresh_theme(palette)
    for slider in (
        getattr(self, 'unit_access_limit_slider', None),
        getattr(self, 'power_access_limit_slider', None),
    ):
        if slider is not None:
            slider.refresh_theme(palette)
    for text_name in (
        'rewards_text', 'unlocks_text', 'archipelago_history_text'
    ):
        text_widget = getattr(self, text_name, None)
        if text_widget is not None:
            text_widget.configure(
                background=field,
                foreground=foreground,
                insertbackground=foreground,
                selectbackground=selected,
                selectforeground=selected_foreground,
            )
    if hasattr(self, 'unlocks_text'):
        self.unlocks_text.tag_configure(
            'search_match',
            background='#665c20' if self.dark_mode_var.get() else '#fff0a6',
            foreground=foreground,
        )
        self.unlocks_text.tag_configure(
            'search_current',
            background='#9b5d1f' if self.dark_mode_var.get() else '#ffbf69',
            foreground=foreground,
        )
    if hasattr(self, 'log_text'):
        self.log_text.configure(
            background=field,
            foreground=foreground,
            insertbackground=foreground,
            selectbackground=selected,
            selectforeground=selected_foreground,
        )
        self.log_text.tag_config(
            'error',
            foreground='#ff7b72' if self.dark_mode_var.get() else '#b00020',
        )
    if hasattr(self, 'busy_overlay'):
        self.busy_overlay.configure(background=palette['busy'])
        self.busy_card.configure(
            background=palette['busy_card'],
            highlightbackground=selected,
        )
        self.busy_title.configure(
            background=palette['busy_card'],
            foreground=palette['busy_title'],
        )
        self.busy_detail.configure(
            background=palette['busy_card'],
            foreground=palette['busy_detail'],
        )
