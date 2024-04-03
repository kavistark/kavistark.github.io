from django.contrib import admin
from .models import User ,RequestToAdmin , Folder,File,Student ,ProfileVisitLink,QRCode

admin.site.register(User)
admin.site.register(RequestToAdmin)
admin.site.register(Folder)
admin.site.register(File)
admin.site.register(Student)
admin.site.register(ProfileVisitLink)
@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('url', 'user', 'qr_code_image_thumbnail')  # Customize the fields displayed in the admin list view

    def qr_code_image_thumbnail(self, obj):
        return obj.qr_code_image.url if obj.qr_code_image else None  # Display a thumbnail of the QR code image in the admin list view
    qr_code_image_thumbnail.short_description = 'QR Code Image'