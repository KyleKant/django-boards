# Generated by Django 3.2 on 2023-02-22 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='topic',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
