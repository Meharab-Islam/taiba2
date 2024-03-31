# Generated by Django 5.0.1 on 2024-03-01 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_allstudent_due_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='allstudent',
            name='total_payment_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]