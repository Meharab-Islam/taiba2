# Generated by Django 5.0.1 on 2024-03-10 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0016_allstudent_extra_money'),
    ]

    operations = [
        migrations.AddField(
            model_name='allstudent',
            name='total_payable_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
