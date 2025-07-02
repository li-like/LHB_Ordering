from django.urls import path
from .views import RecipeListView, RecipeDetailView, RecipeNoteView, RecipeNoteDetailView, RecipeNameCheckView

app_name = 'recipes'

urlpatterns = [
    # 菜谱相关API
    path('recipes/', RecipeListView.as_view(), name='recipe-list'),
    path('recipes/check-name/', RecipeNameCheckView.as_view(), name='recipe-name-check'),
    path('recipes/<int:recipe_id>/', RecipeDetailView.as_view(), name='recipe-detail'),
    
    # 菜谱笔记相关API
    path('recipes/<int:recipe_id>/notes/', RecipeNoteView.as_view(), name='recipe-notes'),
    path('recipes/<int:recipe_id>/notes/<int:note_id>/', RecipeNoteDetailView.as_view(), name='recipe-note-detail'),
]
