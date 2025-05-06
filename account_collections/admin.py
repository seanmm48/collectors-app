from django.contrib import admin

from .models import Collection, Item  # Import models

# Register your models here.
# this will show them in the admin app

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'collection_name', 'purchased_price', 'retail_price', 'date_purchased')  # Add collection_name here

    def collection_name(self, obj):
        return obj.collection.name  # Fetches the collection's name

    collection_name.admin_order_field = 'collection'  # Enables sorting by collection
    collection_name.short_description = 'Collection'  # Column label in admin panel

# Register models
admin.site.register(Collection)
admin.site.register(Item)