# Generated by Django 5.0.3 on 2024-05-15 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_payment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='banned',
            field=models.BooleanField(default=False),
        ),
    ]
