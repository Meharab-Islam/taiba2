# Generated by Django 5.0.1 on 2024-03-03 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_alter_allstudent_extra_installments_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='allstudent',
            name='payment_date_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]