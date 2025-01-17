# Generated by Django 3.1.6 on 2021-10-06 03:38

from django.db import migrations

from scionlab.models.core import Service as ServiceNew


def create_colibri_services(apps, schema_editor):
    """ will create a new colibri service located where the cs is """
    Service = apps.get_model('scionlab', 'Service')
    assert Service.objects.filter(type=ServiceNew.CO).count() == 0  # should be empty
    for cs in Service.objects.filter(type=ServiceNew.CS):
        Service.objects.create(type=ServiceNew.CO, AS=cs.AS, host=cs.host)
    Host = apps.get_model('scionlab', 'Host')
    Host.objects.bump_config()


def delete_colibri_services(apps, schema_editor):
    """ deletes all colibri services """
    Service = apps.get_model('scionlab', 'Service')
    Service.objects.filter(type=ServiceNew.CO).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('scionlab', '0002_colibri_service_schema'),
    ]

    operations = [
        migrations.RunPython(create_colibri_services,   # forward
                             delete_colibri_services),  # backward
    ]
