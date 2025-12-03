# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_rename_price_at_start_of_week_to_avg_price_per_share'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='last_api_call_time',
            field=models.DateTimeField(blank=True, help_text='Timestamp of the last API call to Twelve Data', null=True),
        ),
    ]

