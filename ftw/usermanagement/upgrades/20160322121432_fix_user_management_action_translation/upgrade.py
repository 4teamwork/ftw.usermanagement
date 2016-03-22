from ftw.upgrade import UpgradeStep


class FixUserManagementActionTranslation(UpgradeStep):
    """Fix user management action translation.
    """

    def __call__(self):
        self.install_upgrade_profile()
