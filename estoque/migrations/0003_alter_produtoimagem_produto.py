# Generated by Django 4.2.1 on 2023-05-08 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0002_alter_produtoimagem_produto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtoimagem',
            name='produto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtoimagem_set', to='estoque.produto'),
        ),
    ]
