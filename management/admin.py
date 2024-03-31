from django.contrib import admin
from .models import AllStudent,Course, Installment
# Register your models here.
admin.site.register(AllStudent)
admin.site.register(Course)
admin.site.register(Installment)