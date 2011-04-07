from ftw.table.interfaces import ITableGenerator
from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope import schema
from zope.component import queryUtility, getUtility
from Products.CMFCore.interfaces import IPropertiesTool
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zope.i18n import translate
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from ftw.tabbedview.browser.listing import ListingView
from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import implements


def checkbox(item, value):
     return '<input type="checkbox" name="userids:list" value="%s" />' % \
        item['email']

def userpreflink(item, value):
    url = './@@user-information?userid=%s' % item['email']
    return '<a href="%s">%s</a>' % (url, item['name'])


class IUserTabSourceConfig(ITableSourceConfig):
    """Marker interface for a TableSourceConfig interface"""


class UserManagement(ListingView):
    """
    A ftw.table based user management view
    """
    implements(IUserTabSourceConfig)

    columns = (
        {'column': 'counter',
         'column_title': _(u'label_nr', default='Nr.'),
         },
        {'transform': checkbox},
        {'column': 'name',
         'column_title': _(u'label_name', default='Name'),
         'transform': userpreflink},
        {'column': 'email',
         'column_title': _(u'label_email', default='Email'), },
        {'column': 'groups',
         'column_title': _(u'label_groups', default='Groups'), })

    field_names = ['firstname', 'lastname', 'email', 'password']

    template = ViewPageTemplateFile('users.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.acl_users = getToolByName(context, 'acl_users')
        self.gtool = getToolByName(self, 'portal_groups')
        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')

    def __call__(self):
        if self.request.get('add_member_form', ''):
            return self.validate_registration()


        userids = self.request.get('userids', [])
        if self.request.get('delete.user', False):
            return self.delete_users(userids)

        if self.request.get('notify.users'):
            for userid in userids:
                self.send_user_notification(userid)

        if self.request.get('notify.users.password'):
            for userid in userids:
                self.send_user_notification(userid, reset_pw=True)

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
            for index, t in enumerate(users_terms):
                member = self.mtool.getMemberById(t.token)
                user_groups = []
                for g in self.groups_by_member(member):
                    groupname = g.getId()
                    if 'AuthenticatedUsers' != groupname:
                        user_groups.append(g.getGroupTitleOrName())

                if user_groups:
                    user_groups = ', '.join(user_groups)
                else:
                    if 0:
                    # -- i18ndude hint --
                        _(u'no_group',
                          default=u'No Group',)
                    # / -- i18ndude hint --
                    # do not use translation messages - translate directly
                    user_groups = translate(u'no_group',
                                     domain='ftw.usermanagement',
                                     context=self.request,
                                     default=u'No Group')

                group_link = '<a href="./user_membership?userid=%s">%s</a>' % \
                    (t.value, user_groups)

                userinfo = dict(
                    counter = index + 1,
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
            fullname='%s %s' % (lastname, firstname),
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

        if self.mtool.memberareaCreationFlag:
            # Create the user's member area
            self.mtool.createMemberarea(username)

        IStatusMessage(self.request).addStatusMessage(
            _(u"User added."), type='info')
        self.request.response.redirect(
            self.context.absolute_url() +
            '/@@user_management?searchstring=' + username)

    def delete_users(self, userids):
        if not userids:
            return self.template()
        self.mtool.deleteMembers(userids, delete_memberareas=0, delete_localroles=1, REQUEST=self.request)
        msg = _(u'text_user_deleted')
        IStatusMessage(self.request).addStatusMessage(msg, type="info")
        return self.template()


    def send_user_notification(self, userid, reset_pw=False):
        """notifies a user, that he has been registered on the portal"""

        member = self.mtool.getMemberById(userid)
        username = member.id

        if self.context.unrestrictedTraverse(
            '@@overview-controlpanel').mailhost_warning():
            IStatusMessage(self.request).addStatusMessage(
                _(
                    u'No mailhost defined. contact site Administrator.'),
                    type='error')

        pw = None
        if reset_pw:
            rolemakers = self.acl_users.plugins.listPlugins(IRolesPlugin)
            all_assigned_roles = []
            # Get all assigned roles
            for rolemaker_id, rolemaker in rolemakers:
                all_assigned_roles.extend(
                    rolemaker.getRolesForPrincipal(
                        self.acl_users.getUserById(username)))


            pw = self.registration.generatePassword()
            self.acl_users.userFolderEditUser(
                username,
                pw,
                all_assigned_roles,
                member.getDomains(),
                REQUEST=self.request)

        email = member.getProperty('email')
        fullname = member.getProperty('fullname', userid)
        properties = getUtility(IPropertiesTool)
        site_title = self.context.portal_url \
            .getPortalObject().Title().decode('utf-8')
        contact_email = self.request.get(
            'contact.email',
            properties.email_from_address.decode)
        # prepare from address for header
        header_from = Header(properties.email_from_name.encode('utf-8'),
                             'utf-8')
        header_from.append(u'<%s>' % properties.email_from_address.
                           encode('utf-8'),
                           'utf-8')
        # get subject
        header_subject = Header(
            unicode(self.get_subject(site_title)), 'iso-8859-1')

        # prepare options
        options = {
            'email': email,
            'username': username,
            'fullname': fullname,
            'site_title': site_title,
            'contact_email': contact_email,
            'pw': pw,
            'reset_pw': reset_pw,
            }

        # get the body views
        html_view = self.context.unrestrictedTraverse('@@usermanagament_notify_user')

        # make the mail
        msg = MIMEMultipart('alternative')
        msg['Subject'] = header_subject
        msg['From'] = header_from
        msg['To'] = email

        # render and embedd html
        html_body = html_view(**options).encode('utf-8')
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        # send the mail
        mh = getToolByName(self.context, 'MailHost')
        mh.send(msg, mto=email)

        IStatusMessage(self.request).addStatusMessage(
            _(u'text_usermanagament_user_notified',
                default=u"User ${fullname} (${email}) has been notified",
                mapping={
                    'fullname': fullname.decode('utf-8'),
                    'email': email.decode('utf-8')}),
            type='info')

    def get_subject(self, site_title):
        """Returns the translated subject of the email.
        """
        # -- i18ndude hint --
        if 0:
            _(u'usermanagement_mail_notification_subjectation_subject',
              default=u'Welcome on ${title}',
              mapping=dict(title=site_title))
        # / -- i18ndude hint --
        # do not use translation messages - translate directly
        return translate(u'usermanagement_mail_notification_subject',
                         domain='ftw.usermanagement',
                         context=self.request,
                         default=u'Welcome on ${title}',
                         mapping=dict(title=site_title))


class UserTabSource(BaseTableSource):
    """"""

    def validate_base_query(self, query):

        # results = list(SharingHelpers.get_Items())
        return query

    def search_results(self, results):
        return results