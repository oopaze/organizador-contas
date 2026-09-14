from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations, models

GOAL_FIELDS = ("spending_goal_percent", "savings_goal_percent", "essentials_goal_percent")


def goals_to_percent(apps, schema_editor):
    Profile = apps.get_model("userdata", "Profile")
    for profile in Profile.objects.all():
        salary = Decimal(str(profile.salary or 0))
        changed = []
        for field in GOAL_FIELDS:
            value = getattr(profile, field)
            if value is None:
                continue
            if salary > 0:
                percent = (Decimal(value) / salary * 100).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                setattr(profile, field, percent)
            else:
                setattr(profile, field, None)
            changed.append(field)
        if changed:
            profile.save(update_fields=changed)


def percent_to_goals(apps, schema_editor):
    Profile = apps.get_model("userdata", "Profile")
    for profile in Profile.objects.all():
        salary = Decimal(str(profile.salary or 0))
        changed = []
        for field in GOAL_FIELDS:
            value = getattr(profile, field)
            if value is None:
                continue
            amount = (Decimal(value) * salary / 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            setattr(profile, field, amount)
            changed.append(field)
        if changed:
            profile.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ("userdata", "0005_profile_monthly_essentials_goal_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="monthly_spending_goal",
            new_name="spending_goal_percent",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="monthly_savings_goal",
            new_name="savings_goal_percent",
        ),
        migrations.RenameField(
            model_name="profile",
            old_name="monthly_essentials_goal",
            new_name="essentials_goal_percent",
        ),
        migrations.RunPython(goals_to_percent, percent_to_goals),
        migrations.AlterField(
            model_name="profile",
            name="spending_goal_percent",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="savings_goal_percent",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=5, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="essentials_goal_percent",
            field=models.DecimalField(
                blank=True, decimal_places=2, default=None, max_digits=5, null=True
            ),
        ),
    ]
