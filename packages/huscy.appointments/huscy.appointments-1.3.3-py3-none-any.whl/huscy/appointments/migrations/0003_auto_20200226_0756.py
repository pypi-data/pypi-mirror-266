from django.db import migrations, models
import huscy.appointments.models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_auto_20200226_0735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='key',
            field=models.CharField(default=huscy.appointments.models.create_token, max_length=128, unique=True, verbose_name='Key'),
        ),
    ]
