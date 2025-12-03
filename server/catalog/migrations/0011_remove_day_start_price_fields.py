# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_remove_last_api_call_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='day_start_price',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='day_start_date',
        ),
    ]


