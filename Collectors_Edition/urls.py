

from django.contrib import admin
from django.urls import path
from account_collections import views  # Import views from the app

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),  # Home page route
    path('login/', views.user_login, name='login'),  # Login page route
    path('signup/', views.signup, name='signup'),  # Signup page route
    path('userHomepage/', views.userHomepage, name = 'userHomepage'),
    path('admin/', admin.site.urls),  # Admin interface route
    path('logout/', views.logout_view, name='logout'),
    path('create-collection/', views.create_collection, name='create_collection'),
    path('collection/<int:collection_id>/', views.collection_detail, name='collection_detail'),
    path('collection/<int:collection_id>/add_item/', views.add_item, name='add_item'),
    path('delete-collection/<int:collection_id>/', views.delete_collection, name='delete_collection'),
    path('collection/<int:collection_id>/item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('collection/<int:collection_id>/item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('collection/<int:collection_id>/item/<int:item_id>/', views.item_detail, name='item_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#allows media files to be served in development ONLY
#production this must be switched to a file server or cloud storage (AWS S3, DigitalOcean Spaces, etc)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)