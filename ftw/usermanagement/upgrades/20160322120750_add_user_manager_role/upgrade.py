from ftw.upgrade import UpgradeStep


class AddUserManagerRole(UpgradeStep):
    """Add User Manager role.
    """

    def __call__(self):
        self.install_upgrade_profile()
