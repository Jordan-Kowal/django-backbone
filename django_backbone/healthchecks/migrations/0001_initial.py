# Generated by Django 3.1.5 on 2021-04-05 17:05

# Django
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="HealthcheckDummy",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.CharField(max_length=100, verbose_name="Content")),
            ],
            options={
                "verbose_name": "Healthcheck Dummy",
                "verbose_name_plural": "Healthcheck Dummies",
                "db_table": "core_healthcheck_dummies",
                "ordering": ["-id"],
            },
        ),
    ]