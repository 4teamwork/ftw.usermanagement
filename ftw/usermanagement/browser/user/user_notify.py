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

    def __init__(self, context, request):
        super(UserNotify, self).__init__(context, request)

        self.acl_users = getToolByName(context, 'acl_users')
        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')

    def __call__(self):
        userids = self.request.get('userids', [])
        reset_pw = self.request.get('reset_pw', False)

        if type(userids) != list:
            userids = [userids]

        for userid in userids:
            self.send_user_notification(userid, reset_pw)

        return True

    def send_user_notification(self, userid, reset_pw=False):
        """Notifies a user, that he has been registered on the portal"""

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
        header_from = properties.email_from_name.encode('utf-8') + u'<%s>' \
        % properties.email_from_address.encode('utf-8')
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
        html_view = self.context.unrestrictedTraverse(
            '@@usermanagament_notify_user')

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
