# Generated by Django 5.0.1 on 2024-03-01 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_rename_total_paid_amount_allstudent_paid_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='installment',
            name='comment',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='installment',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
