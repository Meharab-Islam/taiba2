# Generated by Django 5.0.1 on 2024-02-29 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_installment_installment_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='admission_fee',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
