from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility
from zope.i18n import translate


class UserNotify(BrowserView):
    """Notify a registered user.
    Possible to reset password with notification
    """

    def __call__(self):
        userids = self.request.get('userids', [])
        reset_pw = self.request.get('reset_pw', False)

        if not isinstance(userids, list):
            userids = [userids]

        for userid in userids:
            self.send_user_notification(userid, reset_pw)

    def send_user_notification(self, userid, reset_pw=False):
        """Notifies a user, that he has been registered on the portal
        """
        options = self.get_options(userid, reset_pw)

        if not self.validate(options):
            return False

        mail = self.get_mail_object(options)

        # send the mail
        mh = getToolByName(self.context, 'MailHost')
        mh.send(mail, mto=options.get('email'))

        self._add_statusmessage(
            _(u'text_usermanagament_user_notified',
                default=u"User ${fullname} (${email}) has been notified",
                mapping={
                    'fullname': options.get('fullname').decode('utf-8'),
                    'email': options.get('email').decode('utf-8')}),
            'info')

    def validate(self, options):
        """ Validate the received data
        """
        if not options:
            self._add_statusmessage(
                _(u'There was an error to look up a user'),
                'error',
            )
            return False

        if not self._check_mailhost():
            self._add_statusmessage(
                _(u'No mailhost defined. contact site Administrator.'),
                'error')
            return False

        if not options.get('email'):
            self._add_statusmessage(_(
                u'no_email_for_user',
                default='For the user ${user} exist no email address',
                mapping=dict(user=options.get('username'))),
                'error',
            )
            return False
        return True

    def get_mail_object(self, options):
        """ Return a multipart mail object
        """
        title = self._get_site_title()
        body = self._get_html_body(options)

        mail = MIMEMultipart('alternative')
        mail['Subject'] = Header(
            self._get_subject(title.decode('utf-8')), 'utf-8')
        mail['From'] = '%s<%s>' % (
            self._get_contact_name(), self._get_contact_email())
        mail['To'] = options.get('email')
        mail.attach(MIMEText(body, 'html', 'utf-8'))

        return mail

    def reset_password(self, member):
        """ Reset and return the password for the given user
        """
        acl_users = getToolByName(self.context, 'acl_users')
        registration = getToolByName(self.context, 'portal_registration')

        rolemakers = acl_users.plugins.listPlugins(IRolesPlugin)
        all_assigned_roles = []

        # Get all assigned roles
        for rolemaker in rolemakers:
            all_assigned_roles.extend(
                rolemaker[1].getRolesForPrincipal(
                    acl_users.getUserById(member.id)))

        # Generate new password
        password = registration.getPassword(length=8)

        # Update user properties
        acl_users.userFolderEditUser(
            member.id,
            password,
            all_assigned_roles,
            member.getDomains(),
            REQUEST=self.request)

        return password

    def get_options(self, userid, reset_pw):
        """ Return a map with all required infos for the mail template
        """
        mtool = getToolByName(self, 'portal_membership')
        portal_url = getToolByName(self, 'portal_url')
        member = mtool.getMemberById(userid)
        homefolder = mtool.getHomeFolder(userid)

        if not member:
            return False

        options = {}

        options['email'] = member.getProperty('email')
        options['username'] = member.id
        options['fullname'] = member.getProperty('fullname', member.id)
        options['homefolder'] = \
            homefolder.absolute_url() if homefolder else None
        options['pw_reset_url'] = portal_url() + '/@@change-password'
        options['site_title'] = self._get_site_title()
        options['contact_email'] = self._get_contact_email()
        options['pw'] = reset_pw and self.reset_password(member) or None
        options['reset_pw'] = reset_pw

        return options

    def _check_mailhost(self):
        """ Check for mailhost warnings. If we have any, we abort the
        notification
        """
        mailhost = self.context.unrestrictedTraverse('@@overview-controlpanel')
        if mailhost.mailhost_warning():
            return False
        return True

    def _get_contact_email(self):
        """ Return the contact email from the request or propertiestool
        """
        properties = getUtility(IPropertiesTool)
        contact_mail = self.request.get('contact.email',
                                        properties.email_from_address)

        return contact_mail

    def _get_contact_name(self):
        """ Return the contact name from propertiestool
        """
        properties = getUtility(IPropertiesTool)
        return properties.email_from_name

    def _get_site_title(self):
        """ Return site-title from portal_url
        """
        portal_url = getToolByName(self.context, 'portal_url')
        return portal_url.getPortalObject().Title()

    def _get_html_body(self, options):
        """ Return the html body of the email
        """
        html_view = self.context.unrestrictedTraverse(
            '@@usermanagament_notify_user')

        html_body = html_view(**options)

        return html_body.encode('utf-8')

    def _add_statusmessage(self, msg, mtype):
        """ Add a statusmessage
        """
        IStatusMessage(self.request).addStatusMessage(msg, type=mtype)

    def _get_subject(self, site_title):
        """Returns the translated subject of the email.
        """
        return translate(u'usermanagement_mail_notification_subject',
                         domain='ftw.usermanagement',
                         context=self.request,
                         default=u'Welcome on ${title}',
                         mapping=dict(title=site_title))
