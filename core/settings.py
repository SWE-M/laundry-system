"""
Django settings for core project - Almarona_V2.
"""
import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🛡️ إعدادات الأمان (Security Settings)
# ==========================================
# ⚠️ تنبيه: في السيرفر الحقيقي، يجب وضع هذا المفتاح في ملف .env
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-ity7!%39vyfe-9ik^mbdi^6uhm(f_u#gvjepfplyc-ujy*j=@l')

# تفعيل وضع التصحيح (True للتطوير المحلي، False للسيرفر الحقيقي)
# استخدام os.getenv يسمح لنا بتغييرها من السيرفر بدون لمس الكود
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# النطاقات المسموح لها بالوصول للنظام
ALLOWED_HOSTS = ['*']  # غيّرها لاحقاً إلى IP السيرفر أو الدومين، مثل: ['almarona.com', '192.168.1.100']

# النطاقات الموثوقة لعمليات (POST/PUT/DELETE) خصوصاً مع Ngrok
CSRF_TRUSTED_ORIGINS = [
    'https://*.ngrok-free.dev',
    'http://*.ngrok-free.dev',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
]


# ==========================================
# 📦 التطبيقات (Apps)
# ==========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # تطبيقات الطرف الثالث
    'rest_framework',
    'corsheaders',

    # تطبيقات مشروع المارونا V2
    'accounts',
    'orders',
    'branches',
    'services', # تطبيق الخدمات والأسعار الجديد
]

# ==========================================
# ⚙️ البرمجيات الوسيطة (Middleware)
# ==========================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # يجب أن يكون الأول دائماً
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', # لتغيير اللغة تلقائياً
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n', # لدعم اللغات
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================
# 🗄️ قاعدة البيانات (Database)
# ==========================================
# SQLite ممتاز للتطوير الحالي. 
# عند الرفع للسيرفر الفعلي يُفضل الانتقال إلى PostgreSQL للتعامل مع ضغط الكاشير.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==========================================
# 🔑 التحقق من كلمات المرور (Password Validation)
# ==========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==========================================
# 🌍 إعدادات اللغات والتوقيت (Internationalization)
# ==========================================
LANGUAGE_CODE = 'ar' # اللغة الافتراضية
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

TIME_ZONE = 'Asia/Qatar' # التوقيت المحلي للمغسلة

USE_I18N = True
USE_TZ = True

# مسار ملفات الترجمة
LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

# ==========================================
# 📁 الملفات الثابتة والصور (Static & Media Files)
# ==========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# 🌟 مهم جداً للرفع على السيرفر الحقيقي (يجمع كل ملفات الـ CSS/JS في مجلد واحد)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# إعدادات رفع الصور والملفات (ضروري لصور الملابس)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==========================================
# 🌐 إعدادات الـ CORS
# ==========================================
# ⚠️ تنبيه: للسيرفر الحي، يُفضل تحديد الدومينات المسموحة بدلاً من True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# ==========================================
# ⏱️ إعدادات الجلسات وتسجيل الخروج التلقائي
# ==========================================
# إنهاء الجلسة فوراً عند إغلاق المتصفح
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# أو إنهاء الجلسة تلقائياً بعد 8 ساعات من الخمول (اختياري لزيادة الأمان)
SESSION_COOKIE_AGE = 28800

# السماح بتشغيل السكربتات الداخلية (حل مشكلة الصورة image_b9ff45.png)
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'ALLOWALL'
CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "*")