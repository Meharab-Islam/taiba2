# Generated by Django 5.0.1 on 2024-03-18 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0022_alter_allstudent_total_paid_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allstudent',
            name='class_or_level',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]