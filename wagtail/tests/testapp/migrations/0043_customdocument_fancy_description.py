# Generated by Django 2.2.5 on 2019-09-27 14:45

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("tests", "0042_simplechildpage_simpleparentpage"),
    ]

    operations = [
        migrations.AddField(
            model_name="customdocument",
            name="fancy_description",
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
