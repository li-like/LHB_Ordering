from django.db import migrations


THEMES = [
    {
        "slug": "warm-table", "name": "暖心餐桌", "description": "米白、珊瑚橙与鼠尾草绿",
        "palette": {"primary": "#E98D74", "secondary": "#88A47C", "accent": "#E8B65A", "background": "#FFF8EF", "surface": "#FFFFFF", "text": "#3E332D", "muted": "#8A7D75"},
        "background_type": "color", "background_value": "#FFF8EF", "card_style": "soft", "corner_radius": 18, "sort_order": 0,
    },
    {
        "slug": "berry-date", "name": "莓果约会", "description": "克制的莓红与奶油粉",
        "palette": {"primary": "#B8576B", "secondary": "#D9909E", "accent": "#F0B86E", "background": "#FFF5F6", "surface": "#FFFFFF", "text": "#432E33", "muted": "#92777D"},
        "background_type": "gradient", "background_value": "berry", "card_style": "glass", "corner_radius": 22, "sort_order": 1,
    },
    {
        "slug": "sage-kitchen", "name": "鼠尾草厨房", "description": "自然、平静的清新绿色",
        "palette": {"primary": "#6E8B74", "secondary": "#A9B8A5", "accent": "#D8A85D", "background": "#F4F7F1", "surface": "#FFFFFF", "text": "#2F3B31", "muted": "#758078"},
        "background_type": "gradient", "background_value": "sage", "card_style": "solid", "corner_radius": 14, "sort_order": 2,
    },
    {
        "slug": "night-bistro", "name": "夜色小馆", "description": "适合晚餐记录的深色主题",
        "palette": {"primary": "#E39A6D", "secondary": "#78909C", "accent": "#E4C06A", "background": "#202326", "surface": "#303438", "text": "#F7F2EA", "muted": "#B8B0A6"},
        "background_type": "color", "background_value": "#202326", "card_style": "solid", "corner_radius": 12, "sort_order": 3,
    },
]


def seed_themes(apps, schema_editor):
    ThemePreset = apps.get_model("v2", "ThemePreset")
    for theme in THEMES:
        ThemePreset.objects.update_or_create(slug=theme["slug"], defaults=theme)


def unseed_themes(apps, schema_editor):
    apps.get_model("v2", "ThemePreset").objects.filter(slug__in=[item["slug"] for item in THEMES]).delete()


class Migration(migrations.Migration):
    dependencies = [("v2", "0001_initial")]
    operations = [migrations.RunPython(seed_themes, unseed_themes)]
