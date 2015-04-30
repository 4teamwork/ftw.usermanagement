from ftw.upgrade import UpgradeStep


class TranslateActionsMenuItem(UpgradeStep):
    """Translate actions menu item.
    """

    def __call__(self):
        self.install_upgrade_profile()
