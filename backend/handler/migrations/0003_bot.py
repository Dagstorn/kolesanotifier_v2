# Generated by Django 4.2.9 on 2024-01-02 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('handler', '0002_auto_20201102_1858'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=250)),
            ],
        ),
    ]
