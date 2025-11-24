from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns  # Import i18n_patterns
from django.views.i18n import set_language  # Import set_language view

from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language  # This is correct
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Home.urls')),
    path('question-bank/', include('question_bank.urls')),
    path('', include('accounts.urls')),
]
# Adding i18n patterns for language switching
urlpatterns += i18n_patterns(
    path('set_language/', set_language, name='set_language'),  # This is correct
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
