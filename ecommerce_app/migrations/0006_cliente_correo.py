# Generated by Django 3.1 on 2020-10-02 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0005_auto_20200928_0114'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='correo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
