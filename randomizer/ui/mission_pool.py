"""Faction/category selection for a persistent run, independent of its party."""

import tkinter as tk
from tkinter import ttk

from randomizer.missions.unified import (
    POOL_FACTIONS, POOL_ROWS, legacy_pool_selection, normalize_pool_selection,
    pool_cell_counts, pool_cell_status,
)
from randomizer.ui.tooltips import WidgetTooltip


_FACTION_LABELS = {
    'Allies': 'Allied', 'Soviets': 'Soviet', 'Epsilon': 'Yuri',
    'Foehn': 'Foehn', 'Mixed': 'Mixed',
}


class MissionPoolMatrix(ttk.Frame):
    """Tri-state category and faction selectors with installed-map counts."""

    def __init__(self, parent, *, selection, command):
        super().__init__(parent)
        self.command = command
        self.selection = normalize_pool_selection(selection)
        self.counts = {}
        self._enabled = True
        self._updating = False
        self._cells = {}
        self._rows = {}
        self._columns = {}
        self._presets = []
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text='Build your next run', style='Section.TLabel').grid(
            row=0, column=0, sticky='w')
        ttk.Label(
            self, text='Combine categories and factions. Your house never limits the pool.',
            style='Muted.TLabel', wraplength=600,
        ).grid(row=1, column=0, sticky='w', pady=(3, 12))
        presets = ttk.Frame(self)
        presets.grid(row=2, column=0, sticky='ew', pady=(0, 12))
        for index, (label, preset) in enumerate((
            ('All campaigns', 'campaign'), ('Co-op playable', 'coop'),
            ('Solo playable', 'solo'), ('Everything', 'all'), ('Clear', 'clear'),
        )):
            button = ttk.Button(
                presets, text=label, style='Compact.TButton',
                command=lambda value=preset: self._apply_preset(value),
            )
            button.grid(row=0, column=index, padx=(0, 5), sticky='ew')
            presets.columnconfigure(index, weight=1)
            self._presets.append(button)

        matrix = ttk.Frame(self)
        matrix.grid(row=3, column=0, sticky='ew')
        ttk.Label(matrix, text='MISSION CATEGORY', style='Eyebrow.TLabel').grid(
            row=0, column=0, sticky='w', padx=(0, 10), pady=(0, 8))
        for column, faction in enumerate(POOL_FACTIONS, 1):
            matrix.columnconfigure(column, weight=1, uniform='pool-faction')
            variable = tk.IntVar(self, 0)
            widget = ttk.Checkbutton(
                matrix, text=_FACTION_LABELS[faction], variable=variable,
                style=f'Pool.{faction}.TCheckbutton',
                command=lambda value=faction: self._toggle_group(faction=value),
            )
            widget.grid(row=0, column=column, sticky='w', padx=5, pady=(0, 8))
            self._columns[faction] = (variable, widget)
        for row, (row_id, label) in enumerate(POOL_ROWS, 1):
            variable = tk.IntVar(self, 0)
            widget = ttk.Checkbutton(
                matrix, text=label, variable=variable,
                command=lambda value=row_id: self._toggle_group(row=value),
            )
            widget.grid(row=row, column=0, sticky='w', padx=(0, 12), pady=7)
            self._rows[row_id] = (variable, widget)
            for column, faction in enumerate(POOL_FACTIONS, 1):
                cell = f'{row_id}:{faction}'
                selected = tk.BooleanVar(self, cell in self.selection['cells'])
                check = ttk.Checkbutton(
                    matrix, text='—', variable=selected,
                    style=f'Pool.{faction}.TCheckbutton',
                    command=lambda value=cell: self._toggle_cell(value),
                )
                check.grid(row=row, column=column, sticky='w', padx=5, pady=7)
                tooltip = WidgetTooltip(check, '')
                self._cells[cell] = (selected, check, tooltip)
        ttk.Label(
            self, text='APRA2 co-op is not included in the installed addon. '
            'Challenge colors describe the enemy faction.',
            style='Muted.TLabel', wraplength=600,
        ).grid(row=4, column=0, sticky='w', pady=(9, 12))
        ttk.Separator(self).grid(row=5, column=0, sticky='ew')

        policy = ttk.Frame(self)
        policy.grid(row=6, column=0, sticky='ew', pady=(12, 0))
        ttk.Label(policy, text='Progression').grid(row=0, column=0, padx=(0, 12))
        self.policy_var = tk.StringVar(self)
        self.policy_combo = ttk.Combobox(
            policy, textvariable=self.policy_var,
            values=('Flexible · finish solo', 'Co-op required'),
            state='readonly', width=25,
        )
        self.policy_combo.grid(row=0, column=1, sticky='w')
        self.policy_combo.bind('<<ComboboxSelected>>', self._change_policy)
        self.policy_combo.bind('<MouseWheel>', lambda _event: 'break')
        self.summary = ttk.Label(self, style='Pool.Summary.TLabel', wraplength=600)
        self.summary.grid(row=7, column=0, sticky='ew', pady=(10, 0))
        self.note = ttk.Label(self, style='Muted.TLabel', wraplength=600)
        self.note.grid(row=8, column=0, sticky='ew', pady=(4, 0))
        self.refresh(selection=self.selection)

    def refresh(self, *, missions=None, selection=None):
        if missions is not None:
            self.counts = pool_cell_counts(missions)
        if selection is not None:
            self.selection = normalize_pool_selection(selection)
        self._updating = True
        selected = set(self.selection['cells'])
        for cell, (variable, check, tooltip) in self._cells.items():
            row, faction = cell.split(':', 1)
            count = self.counts.get(cell, 0)
            variable.set(cell in selected)
            check.configure(text=str(count) if count else '—')
            check.state(['!alternate'])
            check.state(['!disabled'] if count and self._enabled else ['disabled'])
            tooltip.text = (
                f'{count} installed missions. Select this category and faction for the next run.'
                if count else pool_cell_status(row, faction, self.counts)
            )
        for row, (variable, widget) in self._rows.items():
            self._refresh_group(variable, widget, selected, row=row)
        for faction, (variable, widget) in self._columns.items():
            self._refresh_group(variable, widget, selected, faction=faction)
        policy = self.selection['cooperative_policy']
        self.policy_var.set('Co-op required' if policy == 'required' else 'Flexible · finish solo')
        self.policy_combo.configure(state='readonly' if self._enabled else 'disabled')
        for button in self._presets:
            button.configure(state='normal' if self._enabled else 'disabled')
        total = sum(count for cell, count in self.counts.items() if cell in selected)
        coop = sum(count for cell, count in self.counts.items()
                   if cell in selected and cell.split(':')[0] in ('mo_coop', 'apra2_coop'))
        self.summary.configure(text=f'{total} installed missions selected  ·  '
                               f'{total - coop} solo / AI capable  ·  {coop} human co-op')
        self.note.configure(text=(
            'A human teammate may be needed to finish. Join or leave between missions.'
            if policy == 'required' else
            'Your mission goal follows a solo-capable path. Human co-op missions are optional '
            'bonus branches; challenges can use an AI helper.'
        ) + '\nChanges apply to the next run. Individual exclusions remain in Advanced Pool.')
        self._updating = False

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        self.refresh()

    def _group_cells(self, *, row=None, faction=None):
        return {cell for cell, count in self.counts.items() if count
                and (row is None or cell.split(':')[0] == row)
                and (faction is None or cell.split(':')[1] == faction)}

    def _refresh_group(self, variable, widget, selected, **group):
        cells = self._group_cells(**group)
        chosen = cells & selected
        variable.set(bool(cells) and chosen == cells)
        widget.state(['alternate'] if chosen and chosen != cells else ['!alternate'])
        widget.state(['!disabled'] if cells and self._enabled else ['disabled'])

    def _commit(self, cells=None, policy=None):
        if not self._enabled or self._updating:
            return
        updated = {
            'cells': list(cells if cells is not None else self.selection['cells']),
            'cooperative_policy': policy or self.selection['cooperative_policy'],
        }
        self.refresh(selection=updated)
        self.command(dict(self.selection, cells=list(self.selection['cells'])))

    def _toggle_cell(self, cell):
        cells = set(self.selection['cells'])
        if self._cells[cell][0].get():
            cells.add(cell)
        else:
            cells.discard(cell)
        self._commit(cells)

    def _toggle_group(self, **group):
        cells = set(self.selection['cells'])
        targets = self._group_cells(**group)
        self._commit(cells - targets if targets <= cells else cells | targets)

    def _apply_preset(self, preset):
        rows = {
            'campaign': {'mo_campaign', 'apra2_campaign'},
            'coop': {'mo_coop', 'apra2_coop', 'challenges'},
            'solo': {'mo_campaign', 'apra2_campaign', 'challenges'},
            'all': {row for row, _ in POOL_ROWS}, 'clear': set(),
        }[preset]
        self._commit({cell for cell, count in self.counts.items()
                      if count and cell.split(':')[0] in rows})

    def _change_policy(self, _event=None):
        self._commit(policy='required' if self.policy_var.get() == 'Co-op required' else 'flexible')


def build_unified_pool_controls(self, parent):
    selection = getattr(self, 'mission_pool_selection', None)
    if selection is None:
        selection = legacy_pool_selection(
            self.selected_mission_category(), self.campaign_var.get(),
            bool(self.include_challenge_missions_var.get()),
        )
        self.mission_pool_selection = selection
    self.mission_pool_matrix = MissionPoolMatrix(
        parent, selection=selection, command=self.on_unified_pool_changed,
    )
    self.mission_pool_matrix.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 14))
    self.mission_pool_matrix.refresh(missions=getattr(self, 'missions', ()))
