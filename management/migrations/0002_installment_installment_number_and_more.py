# Generated by Django 5.0.1 on 2024-02-24 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='installment',
            name='installment_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='allstudent',
            name='nid_card',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='allstudent',
            name='phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
