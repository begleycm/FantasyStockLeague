# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_merge_0007_add_api_call_tracker_0007_delete_matchup'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='day_start_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Price at the start of current trading day (last closing price)', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='day_start_date',
            field=models.DateField(blank=True, help_text='Date when day_start_price was last updated', null=True),
        ),
    ]


