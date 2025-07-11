# Generated by Django 5.2.3 on 2025-06-26 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_data', '0005_transferrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdata',
            name='status',
            field=models.CharField(choices=[('active', '在校'), ('transferred_out', '已转出'), ('graduated', '已毕业'), ('suspended', '休学')], default='active', max_length=20, verbose_name='学生状态'),
        ),
    ]
