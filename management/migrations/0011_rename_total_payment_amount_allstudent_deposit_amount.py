# Generated by Django 5.0.1 on 2024-03-03 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_rename_paid_amount_allstudent_total_paid_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='allstudent',
            old_name='total_payment_amount',
            new_name='deposit_amount',
        ),
    ]
