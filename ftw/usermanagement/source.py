from plone.principalsource.source import PrincipalSourceBinder, PrincipalSource


class FtwPrincipalSource(PrincipalSource):
    """ Optimized PrincipalSource to get a faster user overview
    """

    def __iter__(self):
        seen = set()
        for result in self.acl_users.searchUsers():
            if result['id'] in seen:
                continue

            seen.add(result['id'])
            yield result


class FtwPrincipalSourceBinder(PrincipalSourceBinder):
    """Bind the principal source with either users or groups
    """

    def __call__(self, context):
        return FtwPrincipalSource(context, self.users, self.groups)


UsersVocabularyFactory = FtwPrincipalSourceBinder(users=True, groups=False)
GroupsVocabularyFactory = FtwPrincipalSourceBinder(users=False, groups=True)
