# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import rastertiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('rastertiles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rasterfile',
            name='file',
            field=rastertiles.models.FileField(upload_to=b'rasters'),
        ),
    ]
