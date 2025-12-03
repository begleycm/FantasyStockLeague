# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_add_day_start_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='last_api_call_time',
        ),
    ]


