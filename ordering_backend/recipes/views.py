from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe, RecipeIngredient, RecipeStep, RecipeNote
from wechat_auth.models import WeChatUser, Family
import json

# Create your views here.

class RecipeListView(APIView):
    """菜谱列表API"""
    
    def get(self, request):
        """获取菜谱列表"""
        try:
            # 获取查询参数
            category = request.GET.get('category', '')
            author_openid = request.GET.get('author', '')
            family_id = request.GET.get('family_id', '')
            mode = request.GET.get('mode', 'all')  # 'all' 或 'user'
            current_user_openid = request.GET.get('current_user', '')  # 当前用户openid，用于权限判断
            
            # 根据模式构建查询条件
            if mode == 'user':
                # 我的菜谱模式：只返回指定用户的菜谱
                if not author_openid:
                    return Response({'error': '我的菜谱模式需要指定作者'}, status=400)
                try:
                    author = WeChatUser.objects.get(openid=author_openid)
                    recipes = Recipe.objects.filter(author=author)
                except WeChatUser.DoesNotExist:
                    return Response({'error': '用户不存在'}, status=404)
            else:
                # 菜谱大全模式：显示所有公开菜谱 + 当前用户的私有菜谱
                from django.db.models import Q
                
                if current_user_openid:
                    # 登录用户：公开菜谱 + 自己的私有菜谱
                    recipes = Recipe.objects.filter(
                        Q(is_public=True) | Q(author__openid=current_user_openid)
                    )
                else:
                    # 未登录用户：只显示公开菜谱
                    recipes = Recipe.objects.filter(is_public=True)
                
                # 按作者筛选（在大全模式下可选）
                if author_openid:
                    try:
                        author = WeChatUser.objects.get(openid=author_openid)
                        recipes = recipes.filter(author=author)
                    except WeChatUser.DoesNotExist:
                        return Response({'error': '作者不存在'}, status=404)
            
            # 其他筛选条件
            if category and category != 'all':
                recipes = recipes.filter(category=category)
            
            if family_id:
                try:
                    family = Family.objects.get(id=family_id)
                    recipes = recipes.filter(family=family)
                except Family.DoesNotExist:
                    return Response({'error': '家庭不存在'}, status=404)
            
            # 排序：最新创建的在前
            recipes = recipes.order_by('-created_at')
            
            # 序列化数据
            recipe_list = []
            for recipe in recipes[:20]:  # 限制返回20条
                recipe_data = {
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'category': recipe.category,
                    'difficulty': recipe.difficulty,
                    'cook_time': recipe.cook_time,
                    'servings': recipe.servings,
                    'cover_image': recipe.cover_image,
                    'tags': recipe.tags,
                    'author': {
                        'openid': recipe.author.openid,
                        'nickname': recipe.author.nickname,
                        'avatar': recipe.author.avatar
                    },
                    'family': {
                        'id': recipe.family.id,
                        'name': recipe.family.name
                    } if recipe.family else None,
                    'is_public': recipe.is_public,
                    'success_rate': recipe.success_rate,
                    'rating': recipe.rating,
                    'likes': recipe.likes,
                    'created_at': recipe.created_at.isoformat(),
                    'updated_at': recipe.updated_at.isoformat(),
                    # 添加是否可编辑的标识（只有作者可以编辑）
                    'can_edit': recipe.author.openid == current_user_openid if current_user_openid else False
                }
                recipe_list.append(recipe_data)
            
            return Response({
                'success': True,
                'data': recipe_list,
                'count': len(recipe_list),
                'mode': mode,
                'total_available': recipes.count()  # 总可用数量
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def post(self, request):
        """创建新菜谱"""
        try:
            data = request.data
            
            # 验证必要字段
            if not data.get('name'):
                return Response({'error': '菜谱名称不能为空'}, status=400)
            
            if not data.get('author_openid'):
                return Response({'error': '作者信息不能为空'}, status=400)
            
            # 检查菜谱名称是否已存在（同一作者不能有重复名称）
            author_openid = data['author_openid']
            recipe_name = data['name'].strip()
            
            try:
                author = WeChatUser.objects.get(openid=author_openid)
            except WeChatUser.DoesNotExist:
                return Response({'error': '作者不存在'}, status=404)
            
            # 检查该作者是否已有同名菜谱
            existing_recipe = Recipe.objects.filter(author=author, name=recipe_name).first()
            if existing_recipe:
                return Response({'error': f'您已创建过名为"{recipe_name}"的菜谱，请使用不同的名称'}, status=400)
            
            # 获取家庭（可选）
            family = None
            if data.get('family_id'):
                try:
                    family = Family.objects.get(id=data['family_id'])
                except Family.DoesNotExist:
                    return Response({'error': '家庭不存在'}, status=404)
            
            # 创建菜谱
            recipe = Recipe.objects.create(
                name=recipe_name,
                description=data.get('description', ''),
                category=data.get('category', 'other'),
                difficulty=data.get('difficulty', 1),
                cook_time=data.get('cook_time', 30),
                servings=data.get('servings', 2),
                cover_image=data.get('cover_image', ''),
                tags=data.get('tags', []),
                author=author,
                family=family,
                is_public=data.get('is_public', False)
            )
            
            # 创建食材
            ingredients_data = data.get('ingredients', [])
            for idx, ingredient_data in enumerate(ingredients_data):
                if ingredient_data.get('name', '').strip():
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        name=ingredient_data['name'].strip(),
                        amount=ingredient_data.get('amount', ''),
                        unit=ingredient_data.get('unit', ''),
                        category=ingredient_data.get('category', ''),
                        notes=ingredient_data.get('notes', ''),
                        order=idx
                    )
            
            # 创建制作步骤
            steps_data = data.get('steps', [])
            for idx, step_data in enumerate(steps_data):
                if step_data.get('description', '').strip():
                    RecipeStep.objects.create(
                        recipe=recipe,
                        step_number=idx + 1,
                        title=step_data.get('title', ''),
                        description=step_data['description'].strip(),
                        images=step_data.get('images', []),
                        time_required=step_data.get('time_required'),
                        temperature=step_data.get('temperature', ''),
                        tips=step_data.get('tips', '')
                    )
            
            # 验证菜谱完整性
            if not recipe.ingredients.exists():
                recipe.delete()
                return Response({'error': '菜谱必须包含至少一个食材'}, status=400)
            
            if not recipe.steps.exists():
                recipe.delete()
                return Response({'error': '菜谱必须包含至少一个制作步骤'}, status=400)
            
            return Response({
                'success': True,
                'data': {
                    'id': recipe.id,
                    'name': recipe.name,
                    'ingredients_count': recipe.ingredients.count(),
                    'steps_count': recipe.steps.count(),
                    'created_at': recipe.created_at.isoformat()
                },
                'message': '菜谱创建成功'
            }, status=201)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class RecipeDetailView(APIView):
    """菜谱详情API"""
    
    def get(self, request, recipe_id):
        """获取菜谱详情"""
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            
            # 获取食材列表
            ingredients = []
            for ingredient in recipe.ingredients.all():
                ingredients.append({
                    'id': ingredient.id,
                    'name': ingredient.name,
                    'amount': ingredient.amount,
                    'unit': ingredient.unit,
                    'category': ingredient.category,
                    'notes': ingredient.notes,
                    'order': ingredient.order
                })
            
            # 获取制作步骤
            steps = []
            for step in recipe.steps.all():
                steps.append({
                    'id': step.id,
                    'step_number': step.step_number,
                    'title': step.title,
                    'description': step.description,
                    'images': step.images,
                    'time_required': step.time_required,
                    'temperature': step.temperature,
                    'tips': step.tips
                })
            
            # 获取制作笔记
            notes = []
            for note in recipe.notes.all()[:10]:  # 只返回最新10条
                notes.append({
                    'id': note.id,
                    'content': note.content,
                    'images': note.images,
                    'rating': note.rating,
                    'success': note.success,
                    'modifications': note.modifications,
                    'cooking_date': note.cooking_date.isoformat(),
                    'author': {
                        'openid': note.author.openid,
                        'nickname': note.author.nickname,
                        'avatar': note.author.avatar
                    }
                })
            
            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'description': recipe.description,
                'category': recipe.category,
                'difficulty': recipe.difficulty,
                'cook_time': recipe.cook_time,
                'servings': recipe.servings,
                'cover_image': recipe.cover_image,
                'tags': recipe.tags,
                'author': {
                    'openid': recipe.author.openid,
                    'nickname': recipe.author.nickname,
                    'avatar': recipe.author.avatar
                },
                'family': {
                    'id': recipe.family.id,
                    'name': recipe.family.name
                } if recipe.family else None,
                'is_public': recipe.is_public,
                'first_try_date': recipe.first_try_date.isoformat() if recipe.first_try_date else None,
                'success_count': recipe.success_count,
                'total_attempts': recipe.total_attempts,
                'success_rate': recipe.success_rate,
                'rating': recipe.rating,
                'likes': recipe.likes,
                'created_at': recipe.created_at.isoformat(),
                'updated_at': recipe.updated_at.isoformat(),
                'ingredients': ingredients,
                'steps': steps,
                'notes': notes
            }
            
            return Response({
                'success': True,
                'data': recipe_data
            })
            
        except Recipe.DoesNotExist:
            return Response({'error': '菜谱不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def put(self, request, recipe_id):
        """更新菜谱"""
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            data = request.data
            
            # 更新基本信息
            if 'name' in data:
                recipe.name = data['name']
            if 'description' in data:
                recipe.description = data['description']
            if 'category' in data:
                recipe.category = data['category']
            if 'difficulty' in data:
                recipe.difficulty = data['difficulty']
            if 'cook_time' in data:
                recipe.cook_time = data['cook_time']
            if 'servings' in data:
                recipe.servings = data['servings']
            if 'cover_image' in data:
                recipe.cover_image = data['cover_image']
            if 'tags' in data:
                recipe.tags = data['tags']
            if 'is_public' in data:
                recipe.is_public = data['is_public']
            
            recipe.save()
            
            # 更新食材清单
            if 'ingredients' in data:
                # 删除现有食材
                recipe.ingredients.all().delete()
                # 添加新食材
                for idx, ingredient_data in enumerate(data['ingredients']):
                    if ingredient_data.get('name', '').strip():
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            name=ingredient_data['name'],
                            amount=ingredient_data.get('amount', ''),
                            unit=ingredient_data.get('unit', ''),
                            order=idx
                        )
            
            # 更新制作步骤
            if 'steps' in data:
                # 删除现有步骤
                recipe.steps.all().delete()
                # 添加新步骤
                for idx, step_data in enumerate(data['steps']):
                    if step_data.get('description', '').strip():
                        RecipeStep.objects.create(
                            recipe=recipe,
                            step_number=idx + 1,
                            title=step_data.get('title', ''),
                            description=step_data['description'],
                            images=step_data.get('images', []),
                            time_required=step_data.get('time_required'),
                            temperature=step_data.get('temperature', ''),
                            tips=step_data.get('tips', '')
                        )
            
            return Response({
                'success': True,
                'message': '菜谱更新成功',
                'data': {'id': recipe.id}
            })
            
        except Recipe.DoesNotExist:
            return Response({'error': '菜谱不存在'}, status=404)
        except Exception as e:
            print(f"更新菜谱时发生错误: {e}")
            return Response({'error': str(e)}, status=500)
    
    def delete(self, request, recipe_id):
        """删除菜谱"""
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            recipe.delete()
            
            return Response({
                'success': True,
                'message': '菜谱删除成功'
            })
            
        except Recipe.DoesNotExist:
            return Response({'error': '菜谱不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class RecipeNoteView(APIView):
    """菜谱笔记API"""
    
    def post(self, request, recipe_id):
        """创建制作笔记"""
        try:
            # 验证菜谱是否存在
            try:
                recipe = Recipe.objects.get(id=recipe_id)
            except Recipe.DoesNotExist:
                return Response({'error': '菜谱不存在'}, status=404)
            
            # 获取作者
            author_openid = request.data.get('author_openid')
            if not author_openid:
                return Response({'error': '缺少作者信息'}, status=400)
            
            try:
                author = WeChatUser.objects.get(openid=author_openid)
            except WeChatUser.DoesNotExist:
                return Response({'error': '用户不存在'}, status=404)
            
            # 创建笔记
            note_data = {
                'recipe': recipe,
                'author': author,
                'content': request.data.get('content', ''),
                'images': request.data.get('images', []),
                'rating': request.data.get('rating'),
                'success': request.data.get('success', True),
                'modifications': request.data.get('modifications', '')
            }
            
            # 验证必填字段
            if not note_data['content'].strip():
                return Response({'error': '笔记内容不能为空'}, status=400)
            
            note = RecipeNote.objects.create(**note_data)
            
            # 更新菜谱统计信息
            recipe.total_attempts += 1
            if note_data['success']:
                recipe.success_count += 1
            recipe.save()
            
            # 返回创建的笔记信息
            response_data = {
                'id': note.id,
                'recipe_id': recipe.id,
                'content': note.content,
                'images': note.images,
                'rating': note.rating,
                'success': note.success,
                'modifications': note.modifications,
                'cooking_date': note.cooking_date.isoformat(),
                'author': {
                    'openid': author.openid,
                    'nickname': author.nickname,
                    'avatar': author.avatar
                }
            }
            
            return Response({
                'success': True,
                'data': response_data,
                'message': '笔记创建成功'
            }, status=201)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def get(self, request, recipe_id):
        """获取菜谱的所有笔记"""
        try:
            # 验证菜谱是否存在
            try:
                recipe = Recipe.objects.get(id=recipe_id)
            except Recipe.DoesNotExist:
                return Response({'error': '菜谱不存在'}, status=404)
            
            # 获取笔记列表
            notes = RecipeNote.objects.filter(recipe=recipe).order_by('-cooking_date')
            
            note_list = []
            for note in notes:
                note_data = {
                    'id': note.id,
                    'content': note.content,
                    'images': note.images,
                    'rating': note.rating,
                    'success': note.success,
                    'modifications': note.modifications,
                    'cooking_date': note.cooking_date.isoformat(),
                    'author': {
                        'openid': note.author.openid,
                        'nickname': note.author.nickname,
                        'avatar': note.author.avatar
                    }
                }
                note_list.append(note_data)
            
            return Response({
                'success': True,
                'data': note_list,
                'count': len(note_list)
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class RecipeNoteDetailView(APIView):
    """单个笔记详情API"""
    
    def get(self, request, recipe_id, note_id):
        """获取单个笔记详情"""
        try:
            note = RecipeNote.objects.get(id=note_id, recipe_id=recipe_id)
            
            note_data = {
                'id': note.id,
                'recipe_id': note.recipe.id,
                'content': note.content,
                'images': note.images,
                'rating': note.rating,
                'success': note.success,
                'modifications': note.modifications,
                'cooking_date': note.cooking_date.isoformat(),
                'author': {
                    'openid': note.author.openid,
                    'nickname': note.author.nickname,
                    'avatar': note.author.avatar
                }
            }
            
            return Response({
                'success': True,
                'data': note_data
            })
            
        except RecipeNote.DoesNotExist:
            return Response({'error': '笔记不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def put(self, request, recipe_id, note_id):
        """更新笔记"""
        try:
            note = RecipeNote.objects.get(id=note_id, recipe_id=recipe_id)
            
            # 验证作者权限
            author_openid = request.data.get('author_openid')
            if note.author.openid != author_openid:
                return Response({'error': '无权限修改此笔记'}, status=403)
            
            # 更新笔记信息
            note.content = request.data.get('content', note.content)
            note.images = request.data.get('images', note.images)
            note.rating = request.data.get('rating', note.rating)
            note.success = request.data.get('success', note.success)
            note.modifications = request.data.get('modifications', note.modifications)
            
            note.save()
            
            # 返回更新后的笔记信息
            note_data = {
                'id': note.id,
                'recipe_id': note.recipe.id,
                'content': note.content,
                'images': note.images,
                'rating': note.rating,
                'success': note.success,
                'modifications': note.modifications,
                'cooking_date': note.cooking_date.isoformat(),
                'author': {
                    'openid': note.author.openid,
                    'nickname': note.author.nickname,
                    'avatar': note.author.avatar
                }
            }
            
            return Response({
                'success': True,
                'data': note_data,
                'message': '笔记更新成功'
            })
            
        except RecipeNote.DoesNotExist:
            return Response({'error': '笔记不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    def delete(self, request, recipe_id, note_id):
        """删除笔记"""
        try:
            note = RecipeNote.objects.get(id=note_id, recipe_id=recipe_id)
            
            # 验证作者权限
            author_openid = request.data.get('author_openid')
            if note.author.openid != author_openid:
                return Response({'error': '无权限删除此笔记'}, status=403)
            
            note.delete()
            
            return Response({
                'success': True,
                'message': '笔记删除成功'
            })
            
        except RecipeNote.DoesNotExist:
            return Response({'error': '笔记不存在'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class RecipeNameCheckView(APIView):
    """菜谱名称检查API"""
    
    def post(self, request):
        """检查菜谱名称是否重复"""
        try:
            name = request.data.get('name', '').strip()
            author_openid = request.data.get('author_openid', '')
            
            if not name:
                return Response({'error': '菜谱名称不能为空'}, status=400)
            
            if not author_openid:
                return Response({'error': '作者信息不能为空'}, status=400)
            
            # 获取作者
            try:
                author = WeChatUser.objects.get(openid=author_openid)
            except WeChatUser.DoesNotExist:
                return Response({'error': '作者不存在'}, status=404)
            
            # 检查该作者是否已有同名菜谱
            existing_recipe = Recipe.objects.filter(author=author, name=name).first()
            
            return Response({
                'success': True,
                'exists': existing_recipe is not None,
                'message': f'名称"{name}"已存在，请使用不同的名称' if existing_recipe else f'名称"{name}"可以使用'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
