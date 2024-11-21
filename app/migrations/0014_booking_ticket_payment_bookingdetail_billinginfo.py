# Generated by Django 4.0.2 on 2022-03-07 17:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_train_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(auto_created=True, blank=True, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Canceled', 'Canceled')], default='Pending', max_length=50, null=True)),
                ('booking_date', models.DateField(auto_now_add=True, null=True)),
                ('booking_time', models.TimeField(auto_now_add=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.booking')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(auto_created=True, blank=True, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid', max_length=50, null=True)),
                ('pay_amount', models.PositiveIntegerField(blank=True, null=True)),
                ('pay_method', models.CharField(blank=True, max_length=25, null=True)),
                ('phone', models.CharField(blank=True, max_length=14, null=True)),
                ('trxid', models.CharField(blank=True, max_length=255, null=True, verbose_name='Transaction Id')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.booking')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BookingDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('train', models.CharField(blank=True, max_length=255, null=True)),
                ('source', models.CharField(blank=True, max_length=255, null=True)),
                ('destination', models.CharField(blank=True, max_length=255, null=True)),
                ('travel_date', models.DateField(blank=True, null=True)),
                ('travel_time', models.TimeField(blank=True, null=True)),
                ('nop', models.PositiveIntegerField(blank=True, null=True, verbose_name='Number of Passengers')),
                ('adult', models.PositiveIntegerField(blank=True, null=True)),
                ('child', models.PositiveIntegerField(blank=True, null=True)),
                ('class_type', models.CharField(blank=True, max_length=255, null=True)),
                ('fpp', models.PositiveIntegerField(blank=True, null=True, verbose_name='Fare Per Passenger')),
                ('total_fare', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.booking')),
            ],
        ),
        migrations.CreateModel(
            name='BillingInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('booking', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.booking')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]