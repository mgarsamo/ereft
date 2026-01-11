# Generated migration to add vacation home fields and availability models

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0009_add_vacation_home_property_type'),
    ]

    operations = [
        # Add vacation home specific fields to Property model
        migrations.AddField(
            model_name='property',
            name='availability_start_date',
            field=models.DateField(blank=True, help_text='Earliest date property can be booked', null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='availability_end_date',
            field=models.DateField(blank=True, help_text='Latest date property is available (optional)', null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='min_stay_nights',
            field=models.PositiveIntegerField(default=1, help_text='Minimum number of nights per booking'),
        ),
        migrations.AddField(
            model_name='property',
            name='max_stay_nights',
            field=models.PositiveIntegerField(blank=True, help_text='Maximum number of nights per booking (optional)', null=True),
        ),
        migrations.AddField(
            model_name='property',
            name='booking_preference',
            field=models.CharField(choices=[('instant', 'Instant Booking'), ('request', 'Request to Book (Requires Approval)')], default='request', help_text='Booking preference for vacation homes', max_length=20),
        ),
        # Create Availability model
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Specific date for availability status')),
                ('status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked / Reserved'), ('blocked', 'Blocked / Unavailable')], default='available', max_length=20)),
                ('notes', models.TextField(blank=True, help_text='Optional notes (e.g., maintenance, personal use)', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_dates', to='listings.property')),
            ],
            options={
                'verbose_name_plural': 'Availabilities',
                'ordering': ['date'],
            },
        ),
        migrations.AddIndex(
            model_name='availability',
            index=models.Index(fields=['property', 'date'], name='listings_av_propert_8a1b2c_idx'),
        ),
        migrations.AddIndex(
            model_name='availability',
            index=models.Index(fields=['date', 'status'], name='listings_av_date_9d3e4f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='availability',
            unique_together={('property', 'date')},
        ),
        # Create Booking model
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(help_text='Guest name (if not logged in)', max_length=255)),
                ('guest_email', models.EmailField(max_length=254)),
                ('guest_phone', models.CharField(max_length=50)),
                ('check_in_date', models.DateField()),
                ('check_out_date', models.DateField()),
                ('nights', models.PositiveIntegerField(help_text='Number of nights')),
                ('total_price', models.DecimalField(decimal_places=2, help_text='Total booking price', max_digits=12)),
                ('message', models.TextField(blank=True, help_text='Guest inquiry message', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=20)),
                ('is_instant_booking', models.BooleanField(default=False, help_text='Whether this was an instant booking')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('guest', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='auth.user')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='listings.property')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['property', 'check_in_date', 'check_out_date'], name='listings_bo_propert_1a2b3c_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['status'], name='listings_bo_status_4d5e6f_idx'),
        ),
        # Create RecurringAvailabilityRule model
        migrations.CreateModel(
            name='RecurringAvailabilityRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(choices=[('weekly', 'Weekly Pattern'), ('monthly', 'Monthly Pattern'), ('yearly', 'Yearly Pattern (Holidays)')], max_length=20)),
                ('status', models.CharField(choices=[('available', 'Available'), ('booked', 'Booked / Reserved'), ('blocked', 'Blocked / Unavailable')], default='available', max_length=20)),
                ('days_of_week', models.JSONField(blank=True, default=list, help_text='List of day numbers (0=Monday, 6=Sunday) for weekly patterns')),
                ('day_of_month', models.PositiveIntegerField(blank=True, help_text='Day of month (1-31) for monthly patterns', null=True)),
                ('month', models.PositiveIntegerField(blank=True, help_text='Month (1-12) for yearly patterns', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('day', models.PositiveIntegerField(blank=True, help_text='Day of month for yearly patterns', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(31)])),
                ('start_date', models.DateField(help_text='Rule applies from this date')),
                ('end_date', models.DateField(blank=True, help_text='Rule applies until this date (optional)', null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_rules', to='listings.property')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
