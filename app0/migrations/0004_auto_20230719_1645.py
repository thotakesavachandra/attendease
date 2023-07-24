# Generated by Django 3.2.20 on 2023-07-19 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app0', '0003_auto_20230718_1714'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attendancelog',
            old_name='time',
            new_name='startTime',
        ),
        migrations.RemoveField(
            model_name='proxy',
            name='id',
        ),
        migrations.RemoveField(
            model_name='proxy',
            name='studentObj',
        ),
        migrations.AddField(
            model_name='attendancelog',
            name='latitute',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendancelog',
            name='longitude',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proxy',
            name='proxyId',
            field=models.AutoField(default=0, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proxy',
            name='studentObjList',
            field=models.ManyToManyField(to='app0.Student'),
        ),
    ]
