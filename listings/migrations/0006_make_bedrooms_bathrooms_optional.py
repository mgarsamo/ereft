# Generated migration for making bedrooms and bathrooms optional

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0005_userprofile_google_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='bedrooms',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='bathrooms',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True),
        ),
    ]

