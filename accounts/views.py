from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import User, FeaturePermission
from question_bank.models import QuestionBank
from question_bank.models import *

# ---------------- Feature List ----------------
FEATURE_CHOICES = [
    ("add_question", "Add Questions"),
    ("view_question", "View Questions"),
    ("upload_excel", "Upload Excel File"),
    ("input_suggestion", "Input Suggestions"),
    ("lecture_notes", "Lecture Notes"),
    ("ai_notes", "Notes AI"),
    ("ai_image", "Mirror Your Imagination"),
    ("question_curator", "QuestCurator"),
]

# ---------------- Helper ----------------
def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(user):
    otp = generate_otp()
    user.verification_code = otp
    user.otp_created_at = timezone.now()
    user.otp_attempts = 0  # reset attempts
    user.save()
    try:
        send_mail(
            "Your Verification Code",
            f"Your OTP is: {otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"✅ OTP sent to {user.email}: {otp}")
    except Exception as e:
        print("❌ Email send failed:", e)


# ---------------- Unified Register (Student / Staff) ----------------
def register_user(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        user_type = request.POST.get("user_type")  # ✅ captured from dropdown

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register_user")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register_user")

        # OTP
        otp = generate_otp()

        # Students & Staff need admin approval
        is_approved = False if user_type in ["student", "staff"] else True

        user = User.objects.create_user(
            email=email,
            password=password,
            user_type=user_type,
            is_verified=False,
            is_approved=is_approved,
            verification_code=otp,
            otp_created_at=timezone.now(),
        )

        # Send OTP email
        try:
            send_mail(
                "Your Verification Code",
                f"Your OTP is: {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(
                request,
                f"{user_type.capitalize()} account created! Check your email for OTP. Wait for admin approval."
            )
        except Exception as e:
            print("❌ Failed to send email:", e)
            messages.error(request, "Failed to send OTP email. Please try again.")

        return redirect("verify_otp")

    return render(request, "accounts/register.html")


# ---------------- Verify OTP ----------------
def verify_otp(request):
    if request.method == "POST":
        email = request.POST["email"]
        otp = request.POST["otp"]

        try:
            user = User.objects.get(email=email)

            if user.is_verified:
                messages.info(request, "Account already verified. Please log in.")
                return redirect("login")

            if user.otp_is_expired():
                messages.error(request, "OTP expired. Please request again.")
                return redirect("resend_otp")

            if user.otp_attempts >= 3:
                messages.error(request, "Too many failed attempts. Request new OTP.")
                return redirect("resend_otp")

            if user.verification_code == otp:
                user.is_verified = True
                user.verification_code = ""
                user.otp_attempts = 0
                user.save()

                login(request, user)  # auto login

                # ✅ Redirect depending on approval
                if not user.is_approved:
                    return render(request, "accounts/pending_approval.html", {"user": user})

                if user.user_type == "student":
                    return redirect("student_dashboard")
                elif user.user_type == "staff":
                    return redirect("staff_dashboard")
                else:
                    return redirect("admin_dashboard")
            else:
                user.otp_attempts += 1
                user.save()
                remaining = 3 - user.otp_attempts
                if remaining > 0:
                    messages.error(request, f"Invalid OTP. {remaining} attempts left.")
                else:
                    messages.error(request, "Too many wrong attempts. Request new OTP.")
                return redirect("verify_otp")

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")

    return render(request, "accounts/verify_otp.html")


# ---------------- Resend OTP ----------------
def resend_otp(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email, is_verified=False)

            if not user.can_resend_otp():
                messages.error(request, "Wait 1 minute before requesting a new OTP.")
                return redirect("resend_otp")

            send_otp_email(user)
            messages.success(request, "New OTP sent to your email.")
            return redirect("verify_otp")

        except User.DoesNotExist:
            messages.error(request, "No unverified user found with this email.")
    return render(request, "accounts/resend_otp.html")


# ---------------- Login ----------------
def login_view(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.is_verified:
                messages.error(request, "Account not verified. Check your email for OTP.")
                return redirect('verify_otp')

            if user.user_type in ['student', 'staff'] and not user.is_approved:
                return render(request, "accounts/pending_approval.html", {"user": user})

            login(request, user)

            if user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'staff':
                return redirect('staff_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, "accounts/login.html")


# ---------------- Logout ----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------- Dashboards ----------------
@login_required
def student_dashboard(request):
    return render(request, "accounts/student_dashboard.html")


@login_required
def staff_dashboard(request):
    # ✅ Fetch all granted permissions for this staff
    staff_permissions = list(
        FeaturePermission.objects.filter(user=request.user).values_list("feature", flat=True)
    )

    return render(
        request,
        "accounts/staff_dashboard.html",
        {"staff_permissions": staff_permissions},
    )


from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# from .models import QuestionBank, InputSuggestion


@login_required
def admin_dashboard(request):
    # ==========================
    # 🟩 QuestionBank Statistics
    # ==========================
    # Count unique base_question_id for valid questions (avoid counting Hindi/English twice)
    total_questions = (
        QuestionBank.objects.filter(question_number__isnull=False)
        .values('base_question_id')
        .distinct()
        .count()
    )

    total_pyqs = (
        QuestionBank.objects.filter(type_of_question='pyq', question_number__isnull=False)
        .values('base_question_id')
        .distinct()
        .count()
    )

    total_moqs = (
        QuestionBank.objects.filter(type_of_question='moq', question_number__isnull=False)
        .values('base_question_id')
        .distinct()
        .count()
    )

    total_osqs = (
        QuestionBank.objects.filter(type_of_question='osq', question_number__isnull=False)
        .values('base_question_id')
        .distinct()
        .count()
    )

    # Optional: percentage indicator for PYQs
    progress_percentage = round((total_pyqs / total_questions) * 100, 2) if total_questions else 0

    # ==========================
    # 🟦 InputSuggestion Statistics
    # ==========================
    total_suggestions = InputSuggestion.objects.count()

    total_approved = InputSuggestion.objects.filter(
        Q(approval_status='approved') | Q(approval_status='approved_with_modification')
    ).count()

    total_pending = InputSuggestion.objects.filter(
        Q(approval_status='pending_faculty') | Q(approval_status='pending_director')
    ).count()

    now = timezone.now()
    total_this_month = InputSuggestion.objects.filter(
        created_at__year=now.year,
        created_at__month=now.month
    ).count()

    # ✅ Progress bars (avoid division by zero)
    progress_approved = round((total_approved / total_suggestions) * 100, 2) if total_suggestions else 0
    progress_pending = round((total_pending / total_suggestions) * 100, 2) if total_suggestions else 0
    progress_month = round((total_this_month / total_suggestions) * 100, 2) if total_suggestions else 0

    # ==========================
    # 🟨 Context
    # ==========================
    context = {
        # QuestionBank stats (counting English–Hindi pair as one)
        'total_questions': total_questions,
        'total_pyqs': total_pyqs,
        'total_moqs': total_moqs,
        'total_osqs': total_osqs,
        'progress_percentage': progress_percentage,

        # InputSuggestion stats
        'total_suggestions': total_suggestions,
        'total_approved': total_approved,
        'total_pending': total_pending,
        'total_this_month': total_this_month,
        'progress_approved': progress_approved,
        'progress_pending': progress_pending,
        'progress_month': progress_month,
    }

    return render(request, "accounts/admin_dashboard.html", context)



# ---------------- Password Reset Views ----------------
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def password_reset_view(request):
    """Send password reset email"""
    return auth_views.PasswordResetView.as_view(
        template_name="accounts/password_reset.html",
        email_template_name="accounts/password_reset_email.html",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url="/password-reset/done/"
    )(request)

@csrf_exempt
def password_reset_done_view(request):
    """Password reset email sent"""
    return auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"
    )(request)

@csrf_exempt
def password_reset_confirm_view(request, uidb64=None, token=None):
    """Password reset link clicked"""
    return auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url="/reset/done/"
    )(request, uidb64=uidb64, token=token)

@csrf_exempt
def password_reset_complete_view(request):
    """Password successfully reset"""
    return auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"
    )(request)


# ---------------- Pending Users ----------------
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@user_passes_test(is_admin)
def pending_users(request):
    users = User.objects.filter(is_verified=True, is_approved=False)
    
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        try:
            user = User.objects.get(id=user_id)
            if action == "approve":
                user.is_approved = True
                user.save()
                messages.success(request, f"{user.email} has been approved ✅")
            elif action == "reject":
                user.delete()
                messages.warning(request, f"{user.email} has been rejected ❌")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, "accounts/pending_users.html", {"users": users})


# ---------------- Manage Permissions (Admin Only) ----------------
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import FeaturePermission, User

# Custom Features (synced with FeaturePermission model)
FEATURE_CHOICES = [
    ("add_question", "Add Questions"),
    ("view_question", "View Questions"),
    ("upload_excel", "Upload Excel File"),

    # Input Suggestions
    ("add_input_suggestion", "Add Input Suggestion"),
    ("view_input_suggestion", "View Input Suggestion"),

    # Lecture Notes
    ("add_lecture_notes", "Add Lecture Notes"),
    ("view_lecture_notes", "View Lecture Notes"),

    # AI & Tools
    ("notes_ai", "Notes AI"),
    ("generate_image", "Mirror Your Imagination"),
    ("questcurator", "QuestCurator"),
    ("database_view", "Database View"),
]

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@user_passes_test(is_admin)
def manage_permissions(request):
    users = User.objects.filter(user_type__in=["staff", "student"], is_approved=True)

    selected_user = None
    granted_permissions = []
    granted_features = []

    # ✅ Fetch ALL Django permissions dynamically
    all_permissions = Permission.objects.select_related("content_type").all().order_by(
        "content_type__app_label", "content_type__model"
    )

    # Group permissions by app/model for neat display in frontend
    grouped_permissions = {}
    for perm in all_permissions:
        app = perm.content_type.app_label
        model = perm.content_type.model
        grouped_permissions.setdefault(app, {}).setdefault(model, []).append(perm)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        selected_user = User.objects.get(id=user_id)

        # --- Save Django Permissions ---
        selected_user.user_permissions.clear()
        selected_perms = request.POST.getlist("permissions")
        for perm_id in selected_perms:
            perm = Permission.objects.get(id=perm_id)
            selected_user.user_permissions.add(perm)

        # --- Save Custom Feature Permissions ---
        FeaturePermission.objects.filter(user=selected_user).delete()
        selected_features = request.POST.getlist("features")
        for feature in selected_features:
            FeaturePermission.objects.create(user=selected_user, feature=feature)

        messages.success(request, f"Permissions updated for {selected_user.email}")

        granted_permissions = selected_perms
        granted_features = selected_features

    elif request.method == "GET" and request.GET.get("user_id"):
        selected_user = User.objects.get(id=request.GET.get("user_id"))
        granted_permissions = list(selected_user.user_permissions.values_list("id", flat=True))
        granted_features = list(
            FeaturePermission.objects.filter(user=selected_user).values_list("feature", flat=True)
        )

    return render(
        request,
        "permissions/manage_permissions.html",
        {
            "users": users,
            "grouped_permissions": grouped_permissions,
            "features": FEATURE_CHOICES,
            "selected_user": selected_user,
            "granted_permissions": granted_permissions,
            "granted_features": granted_features,
        },
    )
