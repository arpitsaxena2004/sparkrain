# Generated migration for WaterTank and FloodPredictionLog models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_vendor'),
    ]

    operations = [
        migrations.CreateModel(
            name='WaterTank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40)),
                ('name', models.CharField(default='Main Tank', max_length=100)),
                ('capacity_liters', models.FloatField(help_text='Total tank capacity in liters')),
                ('current_level_liters', models.FloatField(help_text='Current water level in liters')),
                ('location', models.CharField(blank=True, max_length=200)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='water_tanks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'water_tank',
                'ordering': ['-last_updated'],
            },
        ),
        migrations.CreateModel(
            name='FloodPredictionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('risk_level', models.CharField(max_length=20)),
                ('confidence', models.FloatField()),
                ('predicted_rainfall_7days', models.FloatField()),
                ('tank_level_pct', models.FloatField()),
                ('recommended_action', models.TextField()),
                ('system_action', models.TextField()),
                ('alert_message', models.TextField()),
                ('prediction_time', models.DateTimeField(auto_now_add=True)),
                ('tank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='predictions', to='core.watertank')),
            ],
            options={
                'db_table': 'flood_prediction_log',
                'ordering': ['-prediction_time'],
            },
        ),
    ]
