""" Tests for API permissions classes. """


import ddt
from django.test import TestCase, RequestFactory
from rest_framework.generics import GenericAPIView

from ..permissions import IsStaffOrOwner
from ...test_utils import UserFactory


class FakeObject:
    """ Fake class for object permission tests. """
    def __init__(self, user=None, course_id=None):
        self.user = user
        self.course_id = course_id


@ddt.ddt
class IsStaffOrOwnerTests(TestCase):
    """ Tests for IsStaffOrOwner permission class. """

    def setUp(self):
        super(IsStaffOrOwnerTests, self).setUp()
        self.permission = IsStaffOrOwner()
        self.request = RequestFactory().get('/')
        self.obj = FakeObject()

    def assert_user_has_object_permission(self, user, permitted):
        """
        Asserts whether or not the user has permission to access an object.

        Arguments
            user (User)
            permitted (boolean)
        """
        self.request.user = user
        self.assertEqual(self.permission.has_object_permission(self.request, None, self.obj), permitted)

    def test_staff_user(self):
        """ Staff users should be permitted. """
        user = UserFactory(is_staff=True)
        self.assert_user_has_object_permission(user, True)

    def test_owner(self):
        """ Owners should be permitted. """
        user = UserFactory()
        self.obj.user = user
        self.assert_user_has_object_permission(user, True)

    def test_non_staff_test_non_owner_or_staff_user(self):
        """ Non-staff and non-owner users should not be permitted. """
        user = UserFactory()
        self.assert_user_has_object_permission(user, False)

    def test_has_permission_as_staff(self):
        """ Staff users always have permission. """
        self.request.user = UserFactory(is_staff=True)
        self.assertTrue(self.permission.has_permission(self.request, None))

    def test_has_permission_as_owner_with_get(self):
        """ Owners always have permission to make GET actions. """
        user = UserFactory()
        request = RequestFactory().get('/?username={}'.format(user.username))
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_with_view_kwargs_as_owner_with_get(self):
        """ Owners always have permission to make GET actions. """
        user = UserFactory()
        self.request.user = user
        view = GenericAPIView()
        view.kwargs = {'username': user.username}
        self.assertTrue(self.permission.has_permission(self.request, view))

    @ddt.data('patch', 'post', 'put')
    def test_has_permission_as_owner_with_edit(self, action):
        """ Owners always have permission to edit. """
        user = UserFactory()

        data = {'username': user.username}
        request = getattr(RequestFactory(), action)('/', data, format='json')
        request.user = user
        request.data = data  # Note (CCB): This is a hack that should be fixed. (ECOM-3171)
        self.assertTrue(self.permission.has_permission(request, None))

    def test_has_permission_as_non_owner(self):
        """ Non-owners should not have permission. """
        user = UserFactory()
        request = RequestFactory().get('/?username={}'.format(user.username))
        request.user = UserFactory()
        self.assertFalse(self.permission.has_permission(request, None))

    def test_has_permission_with_view_kwargs_as_non_owner(self):
        """ Non-owners should not have permission. """
        user = UserFactory()
        self.request.user = user
        view = GenericAPIView()
        view.kwargs = {'username': UserFactory().username}
        self.assertFalse(self.permission.has_permission(self.request, view))
