from django.test import TestCase
from accounts.models import User, Department
from django.utils.translation import gettext_lazy as _

class UserModelTest(TestCase):
    
    def setUp(self):
        self.department = Department.objects.create(name="Computer Science")
        self.user = User.objects.create_user(
            email="user@example.com", 
            password="password123", 
            user_type="staff", 
            department=self.department
        )

    def test_create_user(self):
        """Test if user is created successfully."""
        self.assertEqual(self.user.email, "user@example.com")
        self.assertTrue(self.user.check_password("password123"))

    def test_user_department_relation(self):
        """Test if the user is linked to the department."""
        self.assertEqual(self.user.department.name, "Computer Science")

    def test_is_staff_approver(self):
        """Test if the staff user has approval rights."""
        self.user.staff_approval_rights = True
        self.assertTrue(self.user.is_staff_approver())

    def test_is_admin_approver(self):
        """Test if the admin user has approval rights."""
        self.user.user_type = 'admin'
        self.user.admin_approval_rights = True
        self.assertTrue(self.user.is_admin_approver())

class DepartmentModelTest(TestCase):

    def setUp(self):
        self.department = Department.objects.create(name="Mathematics")

    def test_department_creation(self):
        """Test if department is created successfully."""
        self.assertEqual(self.department.name, "Mathematics")
        self.assertEqual(str(self.department), "Mathematics")
