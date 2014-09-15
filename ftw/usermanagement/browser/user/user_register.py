from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility

ERROR_MSG = {
    'no_firstname': _(u'text_missing_firstname'),
    'no_lastname': _(u'text_missing_lastname'),
    'no_email': _(u'text_missing_email'),
    'reserved_uid': _(u"This username is reserved. Please "
        "choose a different name."),
    'invalid_uid': _(u"The login name you selected is already"
            "in use or is not valid. Please choose another."),
    'invalid_email': _(u'You must enter a valid email address.'),
}


class UserRegister(BrowserView):
    """Validate and register a new member
    """

    def __call__(self):
        return self.register()

    def register(self):
        """Register the new Member
        """
        registration = getToolByName(self.context, 'portal_registration')
        mtool = getToolByName(self, 'portal_membership')
        data = self._get_register_values()

        if not self.validate_registration(data):
            return False

        try:
            registration.addMember(
                data.get('username'),
                self._get_password(),
                properties=data,
                REQUEST=self.request)
        except (AttributeError, ValueError), err:
            self._add_statusmessage(err, "error")
            return False

        if mtool.memberareaCreationFlag:
            # Create the user's member area
            mtool.createMemberarea(data.get('username'))

        self._add_statusmessage(_(u"User added."), 'info')

        return True

    def validate_registration(self, data):
        """ Validate the registration
        """

        errors = {}
        portal = getUtility(ISiteRoot)
        registration = getToolByName(self.context, 'portal_registration')

        if not data.get('firstname'):
            errors['firstname'] = ERROR_MSG.get('no_firstname')

        if not data.get('lastname'):
            errors['lastname'] = ERROR_MSG.get('no_lastname')

        if not data.get('email'):
            errors['email'] = ERROR_MSG.get('no_email')

        # Check if username is valid
        elif data.get('username') == portal.getId():
            errors['email'] = ERROR_MSG.get('reserved_uid')

        # Check if username is allowed
        elif not registration.isMemberIdAllowed(data.get('username')):
            errors['email'] = ERROR_MSG.get('invalid_uid')

        # Check for valid email-address
        elif not registration.isValidEmail(data.get('email')):
            errors['email'] = ERROR_MSG.get('invalid_email')

        for msg in errors.values():
            self._add_statusmessage(msg, "error")

        return not errors

    def _add_statusmessage(self, msg, mtype):
        """ Add a statusmessage
        """
        IStatusMessage(self.request).addStatusMessage(msg, type=mtype)

    def _get_password(self):
        """ Get given password or generate one
        """
        registration = getToolByName(self.context, 'portal_registration')

        return self.request.get('password', '') or \
            registration.getPassword(length=8)

    def _get_register_values(self):
        """ Return the required values for a registration
        """
        firstname = self.request.get('firstname', '')
        lastname = self.request.get('lastname', '')
        email = self.request.get('email', '')
        username = email

        data = dict(
            username=username,
            firstname=firstname,
            lastname=lastname,
            fullname='%s %s' % (lastname, firstname),
            email=email)

        return data
