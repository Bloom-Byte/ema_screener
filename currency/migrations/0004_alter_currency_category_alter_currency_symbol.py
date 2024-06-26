# Generated by Django 5.0.3 on 2024-05-05 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0003_alter_currency_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='category',
            field=models.CharField(choices=[('Crypto', 'Crypto'), ('Forex', 'Forex'), ('Metals & commodities', 'Metals & commodities'), ('Stocks', 'Stocks'), ('Indices', 'Indices')], max_length=50),
        ),
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
