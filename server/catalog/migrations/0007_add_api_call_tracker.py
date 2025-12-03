# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_add_last_api_call_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiCallTracker',
            fields=[
                ('id', models.IntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ('api_call_count', models.IntegerField(default=0, help_text='Number of API calls in current window')),
                ('window_start_time', models.DateTimeField(blank=True, help_text='Start time of current 30-minute window', null=True)),
                ('last_api_call_time', models.DateTimeField(blank=True, help_text='Timestamp of the last API call', null=True)),
            ],
            options={
                'verbose_name': 'API Call Tracker',
                'verbose_name_plural': 'API Call Tracker',
            },
        ),
    ]


