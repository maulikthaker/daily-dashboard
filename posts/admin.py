from django.contrib import admin
# Register your models here.

from .models import Posts

class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "updated","timestamp" ]
    list_filter = ["title", "updated"]
    search_fields = ["content"]
    class Meta:
        model = Posts



admin.site.register(Posts,PostAdmin)