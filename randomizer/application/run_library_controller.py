"""Run selection and next-run mission pool, independent of the current party."""

import copy
from tkinter import messagebox, ttk
import tkinter as tk

from randomizer.config.player import save_config
from randomizer.core.paths import APP_DIR
from randomizer.core.run_library import RunLibrary
from randomizer.missions.unified import legacy_pool_selection, normalize_pool_selection


class RunLibraryController:
    def show_party_setup(self):
        """Reach the selected mission's player options without hunting in Settings."""
        self.workspace_tabs.select(self.settings_tab)
        self.refresh_coop_controls()

        def reveal():
            self.update_idletasks()
            target = self.shop_coop_row if self.shop_mode_selected() else self.coop_controls_frame
            offset = target.winfo_rooty() - self.settings_frame.winfo_rooty()
            height = max(1, self.settings_frame.winfo_height())
            self.settings_canvas.yview_moveto(max(0, (offset - 12) / height))
            target.focus_set()

        self.after(120, reveal)

    def initialize_mission_pool_selection(self):
        saved = self.config.get('mission_pool_selection')
        if saved is None:
            saved = legacy_pool_selection(
                self.selected_mission_category(), self.campaign_var.get(),
                self.optional_challenges_enabled(),
            )
        self.mission_pool_selection = normalize_pool_selection(saved)

    def on_unified_pool_changed(self, selection):
        if self.coop_guest_connected() or self.gameplay_settings_locked():
            self.refresh_unified_pool()
            return
        self.mission_pool_selection = normalize_pool_selection(selection)
        self.config['mission_pool_selection'] = copy.deepcopy(self.mission_pool_selection)
        save_config(self.config)
        self.update_mission_goal_limit()
        self.redraw_mission_tree()
        self.refresh_coop_controls()
        self.update_header_summary()
        self.append_log('Mission pool saved for the next run. The active run keeps its seed, missions and rewards.')

    def refresh_unified_pool(self):
        matrix = getattr(self, 'mission_pool_matrix', None)
        if matrix is not None:
            matrix.refresh(missions=self.missions, selection=self.mission_pool_selection)
            matrix.set_enabled(not (self.coop_guest_connected() or self.gameplay_settings_locked()))

    def run_switch_locked(self):
        process = getattr(self, 'active_game_process', None)
        return bool(
            getattr(self, '_coop_lobby', None)
            or self.gameplay_settings_locked()
            or getattr(self, '_coop_busy', False)
            or getattr(self, '_challenge_preparing', False)
            or getattr(self, '_skirmish_busy', False)
            or getattr(self, 'busy_depth', 0)
            or (process is not None and process.poll() is None)
        )

    def resume_library_run(self, run_id):
        if self.run_switch_locked():
            messagebox.showinfo('Run library', 'Finish the match and leave the party before switching runs.', parent=self)
            return False
        library = RunLibrary(APP_DIR)
        try:
            # Validate before changing the active pointer or current state.
            incoming = library.load(run_id)
            if self.state:
                self.save_state()
            self.state = library.activate(run_id)
        except (OSError, ValueError) as exc:
            messagebox.showerror('Cannot open run', str(exc), parent=self)
            return False
        category = incoming.get('mission_category', 'campaign')
        self.mission_category_var.set(category)
        self.coop_mode_var.set(bool(incoming.get('coop_mode', False)))
        self.config['mission_category'] = category
        self.config['coop_mode'] = self.coop_mode_var.get()
        self.config['active_run_id'] = run_id
        for key, attr in (
            ('progression_mode', 'progression_mode_var'), ('reward_mode', 'reward_mode_var'),
            ('campaign_filter', 'campaign_var'), ('mission_goal', 'mission_goal_var'),
            ('rewards_per_check', 'rewards_per_check_var'),
            ('challenge_player_count', 'challenge_player_count_var'),
        ):
            if key in incoming:
                getattr(self, attr).set(incoming[key])
        self.mission_pool_selection = normalize_pool_selection(
            incoming.get('mission_pool_selection') or legacy_pool_selection(
                category, incoming.get('campaign_filter', 'All Campaigns'),
                incoming.get('mission_pool_settings', {}).get('include_challenge_missions', False),
            )
        )
        self.config['mission_pool_selection'] = copy.deepcopy(self.mission_pool_selection)
        save_config(self.config)
        self.migrate_state()
        self.grid_render_signature = None
        self.__dict__.pop('_active_reward_settings_cache', None)
        self.__dict__.pop('_canonical_earned_rewards_cache', None)
        self.__dict__.pop('_unlock_dashboard_sources_cache', None)
        self.__dict__.pop('_configured_reward_pool_cache', None)
        self._unlocks_view_dirty = self._enemy_buffs_view_dirty = True
        self.refresh_unified_pool()
        self.refresh_progress_view()
        self.redraw_mission_tree()
        self.redraw_progression_views()
        self.refresh_coop_controls()
        self.refresh_shop_mode()
        self.update_header_summary()
        self.append_log(f'Resumed {incoming.get("seed", "run")} with its saved missions and rewards.')
        return True

    def open_run_library(self):
        if self.run_switch_locked():
            messagebox.showinfo('Run library', 'Finish the match and leave the party before switching runs.', parent=self)
            return
        library = RunLibrary(APP_DIR)
        if self.state:
            self.save_state()
        try:
            index = library.index()
        except (OSError, ValueError) as exc:
            messagebox.showerror('Run library', str(exc), parent=self)
            return
        dialog = tk.Toplevel(self)
        dialog.title('Your runs')
        dialog.transient(self)
        dialog.configure(background=self.ui_palette()['background'])
        dialog.geometry('820x460')
        dialog.minsize(580, 330)
        body = ttk.Frame(dialog, padding=20)
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(2, weight=1)
        ttk.Label(body, text='Your runs', style='Section.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(body, text='Each run keeps its seed, mission pool, rewards and progress. New runs never replace old ones.',
                  style='Muted.TLabel', wraplength=740).grid(row=1, column=0, sticky='w', pady=(5, 16))
        tree = ttk.Treeview(body, columns=('mode', 'progress', 'saved'), show='tree headings', selectmode='browse')
        tree.heading('#0', text='Run')
        tree.heading('mode', text='Mode')
        tree.heading('progress', text='Completed')
        tree.heading('saved', text='Last saved')
        tree.column('#0', width=300, minwidth=200)
        tree.column('mode', width=120, minwidth=100)
        tree.column('progress', width=85, minwidth=70)
        tree.column('saved', width=130, minwidth=100)
        tree.grid(row=2, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(body, orient='vertical', command=tree.yview)
        scrollbar.grid(row=2, column=1, sticky='ns')
        tree.configure(yscrollcommand=scrollbar.set)
        for run_id, record in sorted(index['runs'].items(), key=lambda pair: pair[1].get('updated_at', ''), reverse=True):
            label = record.get('label', record.get('seed', 'Run'))
            if run_id == self.state.get('run_id'):
                label += '  ·  Active'
            tree.insert('', 'end', iid=run_id, text=label, values=(
                record.get('progression_mode', ''),
                f'{record.get("completed", 0)} / {record.get("missions", 0)}',
                record.get('updated_at', '')[:16].replace('T', ' '),
            ))
        footer = ttk.Frame(body)
        footer.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(16, 0))
        ttk.Label(footer, text='Shop and Final Fortress keep their own saves.', style='Muted.TLabel').pack(side='left')
        def resume(_event=None):
            selection = tree.selection()
            if selection and self.resume_library_run(selection[0]):
                dialog.destroy()
        ttk.Button(footer, text='Resume run', command=resume, style='Primary.TButton').pack(side='right')
        tree.bind('<Double-1>', resume)
        tree.bind('<Return>', resume)
        dialog.bind('<Escape>', lambda _event: dialog.destroy())
        dialog.grab_set()
        tree.focus_set()
