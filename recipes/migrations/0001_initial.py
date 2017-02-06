# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-06 02:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import recipes.models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
                ('kind', enumfields.fields.EnumIntegerField(enum=recipes.models.Kind, verbose_name='kind')),
                ('weight_unit', enumfields.fields.EnumIntegerField(enum=recipes.models.WeightUnit, verbose_name='weight unit')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, null=True, upload_to='', verbose_name='image')),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
            },
        ),
        migrations.CreateModel(
            name='RecipePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('percentage', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='percentage')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient', verbose_name='ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='recipe')),
            ],
            options={
                'verbose_name': 'Recipe part',
                'verbose_name_plural': 'Recipe parts',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.RecipePart', to='recipes.Ingredient', verbose_name='ingredients'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
