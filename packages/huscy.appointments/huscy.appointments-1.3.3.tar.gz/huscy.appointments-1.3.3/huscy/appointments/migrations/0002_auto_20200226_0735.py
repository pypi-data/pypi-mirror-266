from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import huscy.appointments.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appointment',
            options={'verbose_name': 'Appointment', 'verbose_name_plural': 'Appointments'},
        ),
        migrations.AlterModelOptions(
            name='invitation',
            options={'verbose_name': 'Invitation', 'verbose_name_plural': 'Invitations'},
        ),
        migrations.AlterModelOptions(
            name='reminder',
            options={'verbose_name': 'Reminder', 'verbose_name_plural': 'Reminders'},
        ),
        migrations.AlterModelOptions(
            name='resource',
            options={'verbose_name': 'Resource', 'verbose_name_plural': 'Resources'},
        ),
        migrations.AlterModelOptions(
            name='token',
            options={'verbose_name': 'Token', 'verbose_name_plural': 'Tokens'},
        ),
        migrations.AlterField(
            model_name='appointment',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='end',
            field=models.DateTimeField(verbose_name='End'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='resource',
            field=models.CharField(blank=True, default='', max_length=128, verbose_name='Resource'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='start',
            field=models.DateTimeField(verbose_name='Start'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='title',
            field=models.CharField(blank=True, default='New appointment', max_length=255, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='appointments.Appointment', verbose_name='Appointment'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='participant',
            field=models.CharField(max_length=128, verbose_name='Participant'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Pending'), (1, 'Accepted'), (2, 'Declined')], default=0, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='reminder',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='appointments.Appointment', verbose_name='Appointment'),
        ),
        migrations.AlterField(
            model_name='reminder',
            name='remind_at',
            field=models.DateTimeField(verbose_name='Remind at'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='token',
            name='key',
            field=models.CharField(default=huscy.appointments.models.create_token, max_length=64, unique=True, verbose_name='Key'),
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
