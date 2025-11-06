from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="articulo",
            name="image_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="articulo",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8),
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                ("service", models.CharField(max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
