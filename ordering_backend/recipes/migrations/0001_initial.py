# Generated manually

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
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='菜谱名称')),
                ('description', models.TextField(blank=True, default='', verbose_name='菜谱描述')),
                ('category', models.CharField(choices=[('meat', '荤菜'), ('vegetable', '素菜'), ('soup', '汤品'), ('staple', '主食'), ('snack', '小食'), ('dessert', '甜品'), ('other', '其他')], default='other', max_length=20, verbose_name='菜品分类')),
                ('difficulty', models.IntegerField(choices=[(1, '简单'), (2, '一般'), (3, '中等'), (4, '困难'), (5, '大师级')], default=1, verbose_name='难度等级')),
                ('cook_time', models.IntegerField(default=30, verbose_name='制作时间(分钟)')),
                ('servings', models.IntegerField(default=2, verbose_name='份量(人份)')),
                ('cover_image', models.URLField(blank=True, null=True, verbose_name='封面图片')),
                ('tags', models.JSONField(default=list, verbose_name='标签列表')),
                ('is_public', models.BooleanField(default=False, verbose_name='是否公开分享')),
                ('first_try_date', models.DateField(blank=True, null=True, verbose_name='初学日期')),
                ('success_count', models.IntegerField(default=0, verbose_name='成功制作次数')),
                ('total_attempts', models.IntegerField(default=0, verbose_name='总尝试次数')),
                ('rating', models.FloatField(default=0.0, verbose_name='平均评分')),
                ('likes', models.IntegerField(default=0, verbose_name='点赞数')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wechat_auth.wechatuser', verbose_name='作者')),
                ('family', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wechat_auth.family', verbose_name='所属家庭')),
            ],
            options={
                'verbose_name': '菜谱',
                'verbose_name_plural': '菜谱',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.IntegerField(verbose_name='步骤序号')),
                ('title', models.CharField(blank=True, default='', max_length=64, verbose_name='步骤标题')),
                ('description', models.TextField(verbose_name='详细描述')),
                ('images', models.JSONField(default=list, verbose_name='步骤图片列表')),
                ('time_required', models.IntegerField(blank=True, null=True, verbose_name='所需时间(分钟)')),
                ('temperature', models.CharField(blank=True, default='', max_length=32, verbose_name='温度要求')),
                ('tips', models.TextField(blank=True, default='', verbose_name='小贴士')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='recipes.recipe', verbose_name='菜谱')),
            ],
            options={
                'verbose_name': '制作步骤',
                'verbose_name_plural': '制作步骤',
                'ordering': ['step_number'],
            },
        ),
        migrations.CreateModel(
            name='RecipeNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='笔记内容')),
                ('images', models.JSONField(default=list, verbose_name='相关图片')),
                ('rating', models.IntegerField(blank=True, choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')], null=True, verbose_name='本次评分')),
                ('success', models.BooleanField(default=True, verbose_name='是否成功')),
                ('modifications', models.TextField(blank=True, default='', verbose_name='改进建议')),
                ('cooking_date', models.DateTimeField(auto_now_add=True, verbose_name='制作时间')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wechat_auth.wechatuser', verbose_name='笔记作者')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='recipes.recipe', verbose_name='菜谱')),
            ],
            options={
                'verbose_name': '制作笔记',
                'verbose_name_plural': '制作笔记',
                'ordering': ['-cooking_date'],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='食材名称')),
                ('amount', models.CharField(default='适量', max_length=32, verbose_name='用量')),
                ('unit', models.CharField(blank=True, default='', max_length=16, verbose_name='单位')),
                ('category', models.CharField(choices=[('main', '主料'), ('auxiliary', '辅料'), ('seasoning', '调料')], default='main', max_length=20, verbose_name='食材分类')),
                ('notes', models.CharField(blank=True, default='', max_length=128, verbose_name='备注')),
                ('order', models.IntegerField(default=0, verbose_name='排序')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe', verbose_name='菜谱')),
            ],
            options={
                'verbose_name': '食材',
                'verbose_name_plural': '食材',
                'ordering': ['category', 'order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='recipestep',
            unique_together={('recipe', 'step_number')},
        ),
    ]
