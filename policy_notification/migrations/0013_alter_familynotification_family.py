# Generated by Django 4.2.11 on 2024-06-04 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('policy_notification', '0012_familynotification_family_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familynotification',
            name='family',
            field=models.IntegerField(db_column='FamilyID', primary_key=True, serialize=False),
        ),
    ]
