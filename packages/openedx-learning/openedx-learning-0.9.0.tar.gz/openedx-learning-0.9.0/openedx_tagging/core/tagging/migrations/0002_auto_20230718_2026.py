# Generated by Django 3.2.19 on 2023-07-18 05:54

import django.db.models.deletion
from django.db import migrations, models

import openedx_learning.lib.fields


class Migration(migrations.Migration):
    dependencies = [
        ("oel_tagging", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taxonomy",
            name="system_defined",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="Indicates that tags and metadata for this taxonomy are maintained by the system; taxonomy admins will not be permitted to modify them.",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="parent",
            field=models.ForeignKey(
                default=None,
                help_text="Tag that lives one level up from the current tag, forming a hierarchy.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="oel_tagging.tag",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="taxonomy",
            field=models.ForeignKey(
                default=None,
                help_text="Namespace and rules for using a given set of tags.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="oel_tagging.taxonomy",
            ),
        ),
        migrations.AddField(
            model_name="taxonomy",
            name="visible_to_authors",
            field=models.BooleanField(
                default=True,
                editable=False,
                help_text="Indicates whether this taxonomy should be visible to object authors.",
            ),
        ),
        migrations.RemoveField(
            model_name="objecttag",
            name="object_type",
        ),
        migrations.AddField(
            model_name="taxonomy",
            name="_taxonomy_class",
            field=models.CharField(
                help_text="Taxonomy subclass used to instantiate this instance; must be a fully-qualified module and class name. If the module/class cannot be imported, an error is logged and the base Taxonomy class is used instead.",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="objecttag",
            name="object_id",
            field=openedx_learning.lib.fields.MultiCollationCharField(
                db_collations={"mysql": "utf8mb4_unicode_ci", "sqlite": "NOCASE"},
                editable=False,
                help_text="Identifier for the object being tagged",
                max_length=255,
            ),
        ),
    ]
