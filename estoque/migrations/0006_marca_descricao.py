# Generated by Django 4.2 on 2023-04-23 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0005_remove_marca_estoque_remove_produto_marca_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='marca',
            name='descricao',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]