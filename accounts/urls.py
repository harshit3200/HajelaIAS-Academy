from django.urls import path
from .views import (
    login_view, logout_view,
    register_user,  # ✅ unified registration
    verify_otp, resend_otp,
    student_dashboard, staff_dashboard, admin_dashboard,
    password_reset_view, password_reset_done_view,
    password_reset_confirm_view, password_reset_complete_view,
    pending_users,  # ✅ approval dashboard
    manage_permissions,  # ✅ new view for permissions
)

urlpatterns = [
    path("", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Registration
    path("register/", register_user, name="register_user"),

    # OTP
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),

    # Dashboards
    path("dashboard/student/", student_dashboard, name="student_dashboard"),
    path("dashboard/staff/", staff_dashboard, name="staff_dashboard"),
    path("dashboard/admin/", admin_dashboard, name="admin_dashboard"),

    # Pending Approval (Admin Only)
    path("accounts/pending-users/", pending_users, name="pending_users"),

    # Permissions Management (Admin Only)
    path("accounts/manage-permissions/", manage_permissions, name="manage_permissions"),

    # Password Reset
    path("password-reset/", password_reset_view, name="password_reset"),
    path("password-reset/done/", password_reset_done_view, name="password_reset_done"),
    path("reset/<uidb64>/<token>/", password_reset_confirm_view, name="password_reset_confirm"),
    path("reset/done/", password_reset_complete_view, name="password_reset_complete"),
]
