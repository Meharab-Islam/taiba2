from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

class Course(models.Model):
    name = models.CharField(max_length=50)
    course_fee = models.DecimalField(max_digits=10, decimal_places=2)
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, null = True,  blank = True) 
    course_start_date = models.DateField(null=True, blank=True)
    course_end_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return self.name
    

class AllStudentManager(models.Manager):
    def get_unpaid_students(self):
        current_month = timezone.now().month
        current_year = timezone.now().year

        unpaid_students = self.exclude(
            installments__installment_date__month=current_month,
            installments__installment_date__year=current_year,
        ).distinct()

        return unpaid_students.order_by("-join_date")
    

    

class AllStudent(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    nid_card = models.CharField(max_length=50, null=True, blank=True, unique = True)
    phone_number = models.CharField(max_length = 50, null=True, blank=True, unique = True)
    nationality = models.CharField(max_length = 50, null=True, blank=True)
    country = models.CharField(max_length = 50, null=True, blank=True)
    addmission_date = models.DateField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)
    class_or_level = models.IntegerField(null = True, blank =True, default = 1)
    is_paid = models.BooleanField(default = False)
    addmision_fee = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)
    join_date = models.DateField(auto_now_add = True)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True, default = 0)
    per_month_installment_amount = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)
    total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True, default = 0)
    extra_money = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True, default = 0)
    total_payable_amount = models.DecimalField(max_digits=10, decimal_places=2, null = True, blank = True)

    



    objects = AllStudentManager()
    

    
    def get_installments(self):
        return self.installments.all()
    
    def __str__(self):
        return self.name
    

class Installment(models.Model):
    MAX_INSTALLMENTS = 30

    student = models.ForeignKey(AllStudent, on_delete=models.CASCADE, related_name='installments')
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installment_number = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=500, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    installment_date = models.DateField()
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field

    objects = models.Manager()

    def save(self, *args, **kwargs):
        existing_installments = Installment.objects.filter(student=self.student)
        if self.pk is None and existing_installments.count() >= self.MAX_INSTALLMENTS:
            raise ValueError(f"A student can have at most {self.MAX_INSTALLMENTS} installments.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - Installment {self.installment_number}"

@receiver(pre_save, sender=Installment)
def prevent_extra_installments(sender, instance, **kwargs):
    existing_installments = Installment.objects.filter(student=instance.student)
    if instance.pk is None and existing_installments.count() >= Installment.MAX_INSTALLMENTS:
        raise ValueError(f"A student can have at most {Installment.MAX_INSTALLMENTS} installments.")
    