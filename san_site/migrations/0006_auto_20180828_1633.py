# Generated by Django 2.1 on 2018-08-28 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('san_site', '0005_auto_20180828_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventories',
            name='product',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='san_site.Product'),
        ),
        migrations.AlterField(
            model_name='inventories',
            name='store',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='san_site.Store'),
        ),
    ]
