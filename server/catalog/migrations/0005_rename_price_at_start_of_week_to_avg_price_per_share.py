# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_league_end_date_alter_league_start_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userleaguestock',
            old_name='price_at_start_of_week',
            new_name='avg_price_per_share',
        ),
    ]

