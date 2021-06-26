# Generated by Django 3.0.3 on 2021-06-13 11:25

import core.fields
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FamilySMS',
            fields=[
                ('validity_from', core.fields.DateTimeField(db_column='ValidityFrom', default=datetime.datetime.now)),
                ('validity_to', core.fields.DateTimeField(blank=True, db_column='ValidityTo', null=True)),
                ('id', models.AutoField(db_column='FamilySmsID', primary_key=True, serialize=False)),
                ('approval_of_notification', models.BooleanField(db_column='ApprovalOfSMS', default=False)),
                ('language_of_notification', models.CharField(db_column='LanguageOfSMS', default='en', max_length=5)),
            ],
            options={
                'db_table': 'tblFamilySMS',
                'managed': False,
            },
        ),
    ]
