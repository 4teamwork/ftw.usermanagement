from ftw.usermanagement import user_management_factory as _
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getUtility


class UserRegister(BrowserView):
    """validate and register a new member"""

    def __init__(self, context, request):
        super(UserRegister, self).__init__(context, request)

        self.mtool = getToolByName(self, 'portal_membership')
        self.registration = getToolByName(self.context, 'portal_registration')

    def __call__(self):
        return self.validate_registration()

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
            return False
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
            return False

        if self.mtool.memberareaCreationFlag:
            # Create the user's member area
            self.mtool.createMemberarea(username)

        IStatusMessage(self.request).addStatusMessage(
            _(u"User added."), type='info')
        self.request.response.redirect(
            self.context.absolute_url() +
            '/@@user_management')
        return True
