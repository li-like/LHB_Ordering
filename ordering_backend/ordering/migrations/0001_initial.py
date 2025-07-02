# Generated manually to create ordering models

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wechat_auth', '0005_auto_20250701_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='分类名称')),
                ('description', models.TextField(blank=True, verbose_name='分类描述')),
                ('icon', models.URLField(blank=True, null=True, verbose_name='分类图标')),
                ('sort_order', models.IntegerField(default=0, verbose_name='排序')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wechat_auth.wechatuser', verbose_name='创建者')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_categories', to='wechat_auth.family', verbose_name='所属家庭')),
            ],
            options={
                'verbose_name': '餐品分类',
                'verbose_name_plural': '餐品分类',
                'ordering': ['sort_order', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='MealItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='餐品名称')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('image', models.URLField(blank=True, null=True, verbose_name='餐品图片')),
                ('meal_type', models.CharField(choices=[('breakfast', '早餐'), ('lunch', '午餐'), ('dinner', '晚餐'), ('snack', '零食'), ('dessert', '甜品')], default='lunch', max_length=20, verbose_name='餐品类型')),
                ('difficulty', models.CharField(choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难')], default='medium', max_length=20, verbose_name='制作难度')),
                ('prep_time', models.IntegerField(default=30, verbose_name='预计制作时间(分钟)')),
                ('ingredients', models.JSONField(default=list, verbose_name='所需食材')),
                ('cooking_steps', models.JSONField(default=list, verbose_name='制作步骤')),
                ('tags', models.JSONField(default=list, verbose_name='标签')),
                ('popularity', models.IntegerField(default=0, verbose_name='受欢迎程度')),
                ('is_available', models.BooleanField(default=True, verbose_name='是否可点餐')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='ordering.mealcategory', verbose_name='所属分类')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wechat_auth.wechatuser', verbose_name='创建者')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_items', to='wechat_auth.family', verbose_name='所属家庭')),
            ],
            options={
                'verbose_name': '餐品',
                'verbose_name_plural': '餐品',
                'ordering': ['-popularity', 'name'],
            },
        ),
        migrations.CreateModel(
            name='MealRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='数量')),
                ('priority', models.CharField(choices=[('low', '不急'), ('normal', '一般'), ('high', '比较急'), ('urgent', '很急')], default='normal', max_length=20, verbose_name='优先级')),
                ('preferred_time', models.DateTimeField(blank=True, null=True, verbose_name='希望用餐时间')),
                ('special_requests', models.TextField(blank=True, verbose_name='特殊要求')),
                ('status', models.CharField(choices=[('pending', '等待确认'), ('confirmed', '已确认'), ('cooking', '制作中'), ('completed', '已完成'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='状态')),
                ('notes', models.TextField(blank=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='点餐时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_requests', to='wechat_auth.family', verbose_name='所属家庭')),
                ('meal_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='ordering.mealitem', verbose_name='餐品')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_requests', to='wechat_auth.wechatuser', verbose_name='点餐人')),
            ],
            options={
                'verbose_name': '点餐需求',
                'verbose_name_plural': '点餐需求',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MealConfirmation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('accepted', '接受制作'), ('declined', '拒绝制作'), ('delegated', '委托他人')], max_length=20, verbose_name='确认状态')),
                ('estimated_time', models.DateTimeField(blank=True, null=True, verbose_name='预计完成时间')),
                ('actual_start_time', models.DateTimeField(blank=True, null=True, verbose_name='实际开始时间')),
                ('actual_completion_time', models.DateTimeField(blank=True, null=True, verbose_name='实际完成时间')),
                ('notes', models.TextField(blank=True, verbose_name='备注')),
                ('difficulty_rating', models.IntegerField(blank=True, null=True, verbose_name='制作难度评分(1-5)')),
                ('satisfaction_rating', models.IntegerField(blank=True, null=True, verbose_name='满意度评分(1-5)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='确认时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('confirmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmations', to='wechat_auth.wechatuser', verbose_name='确认人')),
                ('delegated_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delegated_confirmations', to='wechat_auth.wechatuser', verbose_name='委托给')),
                ('meal_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='confirmation', to='ordering.mealrequest', verbose_name='关联点餐')),
            ],
            options={
                'verbose_name': '制作确认',
                'verbose_name_plural': '制作确认',
            },
        ),
        migrations.CreateModel(
            name='MealOrderBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='批次名称')),
                ('target_time', models.DateTimeField(verbose_name='目标用餐时间')),
                ('status', models.CharField(choices=[('planning', '规划中'), ('confirmed', '已确认'), ('cooking', '制作中'), ('completed', '已完成'), ('cancelled', '已取消')], default='planning', max_length=20, verbose_name='批次状态')),
                ('notes', models.TextField(blank=True, verbose_name='批次备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('coordinator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coordinated_batches', to='wechat_auth.wechatuser', verbose_name='协调人')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_batches', to='wechat_auth.family', verbose_name='所属家庭')),
                ('meal_requests', models.ManyToManyField(related_name='batches', to='ordering.mealrequest', verbose_name='包含的点餐需求')),
            ],
            options={
                'verbose_name': '批量点餐',
                'verbose_name_plural': '批量点餐',
                'ordering': ['-target_time'],
            },
        ),
        migrations.CreateModel(
            name='FamilyMealStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_meals_ordered', models.IntegerField(default=0, verbose_name='总点餐次数')),
                ('total_meals_completed', models.IntegerField(default=0, verbose_name='总完成次数')),
                ('most_popular_meal', models.CharField(blank=True, max_length=128, verbose_name='最受欢迎餐品')),
                ('most_active_requester', models.CharField(blank=True, max_length=128, verbose_name='最活跃点餐人')),
                ('most_active_cook', models.CharField(blank=True, max_length=128, verbose_name='最活跃制作人')),
                ('average_completion_time', models.IntegerField(default=0, verbose_name='平均制作时间(分钟)')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='最后更新时间')),
                ('family', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meal_stats', to='wechat_auth.family', verbose_name='家庭')),
            ],
            options={
                'verbose_name': '家庭用餐统计',
                'verbose_name_plural': '家庭用餐统计',
            },
        ),
        migrations.AlterUniqueTogether(
            name='mealitem',
            unique_together={('family', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='mealcategory',
            unique_together={('family', 'name')},
        ),
    ]
