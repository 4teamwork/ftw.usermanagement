from ftw.table.interfaces import ITableGenerator
from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import queryUtility, getUtility


class UserManagement(BrowserView):
    """
    A ftw.table based user management view
    """

    columns = (
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'), },
        {'column': 'email',
         'column_title': _(u'label_email', default='Email'), },
        {'column': 'groups',
         'column_title': _(u'label_groups', default='Groups'), })

    field_names = ['firstname', 'lastname', 'email', 'password']

    template = ViewPageTemplateFile('users.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')

    def __call__(self):
        if self.request.get('add_member_form', ''):
            return self.validate_registration()
        return self.template()

    def render_table(self):
        """Renders a table usfing ftw.table"""

        generator = queryUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(self.users, self.columns, sortable = True)

    @property
    def users(self):
        context = self.context
        users = []
        factory = getUtility(
            schema.interfaces.IVocabularyFactory,
            name='plone.principalsource.Users',
            context=context)

        if factory:
            users_terms = factory(context)
            # convert to a dict for now, because ftw.table cannot hanndle
            # SimpleTerms
            for t in users_terms:
                member = self.mtool.getMemberById(t.value)
                user_groups = []
                for g in self.groups_by_member(member):
                    groupname = g.getId()
                    if 'AuthenticatedUsers' != groupname:
                        user_groups.append(g.getGroupTitleOrName())

                if user_groups:
                    user_groups = ', '.join(user_groups)
                else:
                    user_groups = _(u'no_group')
                group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                    (t.value, user_groups)

                userinfo = dict(
                    name = t.title,
                    email = t.value,
                    groups = group_link)
                users.append(userinfo)
        return users

    def groups_by_member(self, userid):
        groupResults = [self.gtool.getGroupById(m) \
            for m in self.gtool.getGroupsForPrincipal(userid)]
        groupResults.sort(
            key=lambda x: x is not None and x.getGroupTitleOrName().lower())
        return filter(None, groupResults)

    def validate_registration(self):
        """Copied from plone.app.user.browser.register."""

        errors = {}
        portal = getUtility(ISiteRoot)

        # Email == Login is hardcoded
        # use_email_as_login = props.getProperty('use_email_as_login')


        # Required fields
        firstname = self.request.get('firstname', '')
        lastname = self.request.get('lastname', '')
        username = email = self.request.get('email', '')

        if not email:
            errors['email'] = _(u'text_missing_email')
        if not firstname:
            errors['firstname'] = _(u'text_missing_firstname')
        if not lastname:
            errors['lastname'] = _(u'text_missing_lastname')


        # check if username is valid
        # Skip this check if username was already in error list
        if not 'email' in errors:
            portal = getUtility(ISiteRoot)
            if username == portal.getId():
                errors['email'] = _(u"This username is reserved. Please "
                    "choose a different name.")


        # check if username is allowed
        if not 'email' in errors:
            if not self.registration.isMemberIdAllowed(username):
                errors['email'] = _(u"The login name you selected is already"
                    "in use or is not valid. Please choose another.")


        # Skip this check if email was already in error list
        if not 'email' in errors:
            if not self.registration.isValidEmail(email):
                errors['email'] = _(u'You must enter a valid email address.')

        if errors:
            self.request.set('errors', errors)
            for field, msg in errors.items():
                IStatusMessage(self.request).addStatusMessage(
                    msg,
                    type="error")
            return self.template()
        else:
            # Everything is fine, so register our new member
            return self.register()

    def register(self):
        """Register the new Member"""

        # Email == Login is hardcoded
        # Required fields
        firstname = self.request.get('firstname', '')
        lastname = self.request.get('lastname', '')
        username = email = self.request.get('email', '')

        # Collect data for registration
        data = dict(
            username=username,
            firstname=firstname,
            lastname=lastname,
            fullname='%s %s' % (firstname, lastname),
            email=email)

        # Get given password or generate one
        password = self.request.get('password', '') or \
            self.registration.generatePassword()

        try:
            self.registration.addMember(
                username,
                password,
                properties=data,
                REQUEST=self.request)
        except (AttributeError, ValueError), err:
            IStatusMessage(self.request).addStatusMessage(err, type="error")
            return self.template()

        IStatusMessage(self.request).addStatusMessage(
            _(u"User added."), type='info')
        self.request.response.redirect(
            self.context.absolute_url() +
            '/@@user_management?searchstring=' + username)
