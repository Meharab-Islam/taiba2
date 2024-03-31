# Generated by Django 5.0.1 on 2024-03-16 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0019_remove_allstudent_total_payable_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='allstudent',
            name='total_payable_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
