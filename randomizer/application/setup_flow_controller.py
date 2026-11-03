"""One owner for each next-run control, separate from the active run."""

from randomizer.missions.unified import APRA2_OPERATION_CODES


class SetupFlowController:
    def selected_setup_category(self):
        if self.final_fortress_mode_selected():
            return 'campaign'
        if self.shop_mode_selected():
            return 'coop' if self.coop_mode_var.get() else 'campaign'
        if self.archipelago_run_active():
            return self.state.get('mission_category', 'campaign')
        if self.progression_mode_var.get() in ('Grid Mode', 'Mission List'):
            return 'mixed'
        variable = getattr(self, 'setup_category_var', None)
        return {'Campaign': 'campaign', 'Co-op': 'coop', 'Challenges': 'challenge'}.get(
            variable.get() if variable is not None else '', 'campaign')

    def effective_setup_campaign(self):
        """Ignore hidden legacy faction drafts where another pool owns selection."""
        if self.selected_setup_category() == 'mixed' or self.shop_mode_selected():
            return 'All Campaigns'
        if self.archipelago_run_active():
            return self.state.get('campaign_filter', 'All Campaigns')
        return self.campaign_var.get()

    def mission_pool_operation_exemptions(self):
        return APRA2_OPERATION_CODES if self.selected_setup_category() == 'mixed' else ()

    def refresh_setup_flow(self):
        required = ('setup_mode_frame', 'legacy_mission_pool_frame',
                    'include_operation_missions_check', 'challenge_local_frame')
        if not all(hasattr(self, name) for name in required):
            return
        fortress = self.final_fortress_mode_selected()
        shop = not fortress and self.shop_mode_selected()
        category = self.selected_setup_category()
        matrix = not (fortress or shop) and category == 'mixed'
        legacy = not (fortress or shop or matrix)
        locked = self.coop_guest_connected() or self.gameplay_settings_locked() or self.archipelago_run_active()
        self.mission_pool_matrix.grid() if matrix else self.mission_pool_matrix.grid_remove()
        self.mission_pool_matrix.set_enabled(not locked)
        self.legacy_mission_pool_frame.grid() if legacy else self.legacy_mission_pool_frame.grid_remove()
        self.setup_category_combo.configure(
            state='disabled' if locked else 'readonly',
            values=('Campaign', 'Co-op') if self.archipelago_run_active()
            else ('Campaign', 'Co-op', 'Challenges'))
        # The sole optional-challenge control belongs to Classic's pool.
        include_challenges = legacy and category != 'challenge' and not self.archipelago_run_active()
        widget = self.include_challenge_missions_check
        widget.configure(state='disabled' if locked else 'normal')
        widget.grid() if include_challenges else widget.grid_remove()
        self.legacy_mission_type_frame.grid() if include_challenges else self.legacy_mission_type_frame.grid_remove()
        self.campaign_label.grid() if legacy else self.campaign_label.grid_remove()
        self.campaign_combo.grid() if legacy else self.campaign_combo.grid_remove()
        self.campaign_label.configure(text='Reward faction' if category == 'challenge' else 'Mission faction')
        factions = ('All Campaigns', 'Allies', 'Soviets', 'Epsilon')
        if category != 'coop':
            factions += ('Foehn',)
        self.campaign_combo.configure(values=factions, state='disabled' if locked else 'readonly')
        if legacy and self.campaign_var.get() not in factions:
            self.campaign_var.set('All Campaigns')
        self.include_operation_missions_check.configure(text=(
            'Include MO special operations' if matrix else 'Include special operations'))
        for name in ('include_no_build_missions_check', 'include_no_build_production_missions_check',
                     'include_operation_missions_check', 'prioritize_no_build_missions_check'):
            control = getattr(self, name)
            control.grid() if matrix or (legacy and category != 'challenge') else control.grid_remove()
        skirmish = getattr(self, 'include_skirmishes_check', None)
        if skirmish is not None:
            skirmish.grid() if matrix and self.progression_mode_var.get() == 'Grid Mode' else skirmish.grid_remove()
        fixed_rewards = fortress or shop
        self.reward_mode_combo.grid_remove() if fixed_rewards else self.reward_mode_combo.grid()
        self.setup_reward_policy_label.grid() if fixed_rewards else self.setup_reward_policy_label.grid_remove()
        self.setup_reward_policy_var.set('Fortress perks' if fortress else 'Shop economy' if shop else '')
        self.setup_mode_help_var.set(
            'Choose the defense map and perks in Final Fortress, then set up your players.' if fortress else
            'Filter solo or native co-op missions below. Shop stock has its own faction and economy.' if shop else
            'Choose categories and factions below. The matrix owns mission inclusion; Party only configures players.' if matrix else
            'Classic follows catalogue order. Choose one base category and its optional challenges below.'
        )
        # Campaign cosmetics must not compete with native challenge player colors.
        if hasattr(self, 'map_colors_frame'):
            challenge = self.challenge_mission()
            self.map_colors_frame.grid_remove() if fortress or challenge else self.map_colors_frame.grid()
        signature = (fortress, shop, matrix, category)
        if signature != getattr(self, '_setup_flow_signature', None):
            self._setup_flow_signature = signature
            self.__dict__.pop('_settings_layout_signature', None)
            if hasattr(self, 'settings_canvas'):
                self.after_idle(lambda: self.layout_settings_sections(self.settings_canvas.winfo_width()))
