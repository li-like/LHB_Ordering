from django.db import transaction

from .models import Dish, Membership, Menu, MenuSection, Preference, SpaceAppearance, ThemePreset


DEFAULT_MENU = [
    ("暖心主食", "bowl", [
        ("番茄鸡蛋面", "酸甜温暖的家常面", ["面食", "快手"]),
        ("咖喱鸡肉饭", "浓郁咖喱配软嫩鸡肉", ["米饭", "下饭"]),
        ("鲜虾蛋炒饭", "适合一起分享的粒粒香", ["米饭", "快手"]),
    ]),
    ("一起吃菜", "heart", [
        ("可乐鸡翅", "甜咸入味的人气菜", ["肉类", "甜咸"]),
        ("蒜蓉西兰花", "清爽又简单的蔬菜", ["蔬菜", "清淡"]),
        ("麻婆豆腐", "微辣下饭的经典家常菜", ["豆制品", "辣"]),
    ]),
    ("甜蜜收尾", "sparkle", [
        ("草莓酸奶杯", "酸甜清爽的小甜品", ["甜品", "水果"]),
        ("焦糖布丁", "细腻柔软的甜蜜收尾", ["甜品", "烘焙"]),
    ]),
]


@transaction.atomic
def initialize_space(space, account):
    membership = Membership.objects.create(
        space=space, account=account, role="owner", display_name=account.nickname or "我"
    )
    Preference.objects.create(membership=membership)
    preset = ThemePreset.objects.filter(slug="warm-table", is_active=True).first() or ThemePreset.objects.filter(is_active=True).first()
    SpaceAppearance.objects.create(space=space, preset=preset)
    menu = Menu.objects.create(
        space=space, name="我们的默认菜单", description="随时可以改名、换图和增删菜品",
        cover_url="", image_style="polaroid", is_default=True,
    )
    section_colors = ["#E98D74", "#88A47C", "#E8B65A"]
    for section_order, (section_name, icon, dishes) in enumerate(DEFAULT_MENU):
        section = MenuSection.objects.create(
            menu=menu, name=section_name, icon=icon,
            accent_color=section_colors[section_order], sort_order=section_order,
        )
        Dish.objects.bulk_create([
            Dish(section=section, name=name, description=description, tags=tags, sort_order=index)
            for index, (name, description, tags) in enumerate(dishes)
        ])
    return membership
