from django.urls import path

from . import views


urlpatterns = [
    path("auth/register", views.RegisterView.as_view(), name="v2-register"),
    path("auth/login", views.LoginView.as_view(), name="v2-login"),
    path("auth/wechat", views.WechatLoginView.as_view(), name="v2-wechat"),
    path("auth/logout", views.LogoutView.as_view(), name="v2-logout"),
    path("auth/me", views.MeView.as_view(), name="v2-me"),

    path("spaces", views.SpaceListCreateView.as_view(), name="v2-spaces"),
    path("spaces/join", views.JoinSpaceView.as_view(), name="v2-spaces-join"),
    path("spaces/<int:space_id>", views.SpaceDetailView.as_view(), name="v2-space-detail"),
    path("spaces/<int:space_id>/members", views.MembersView.as_view(), name="v2-members"),
    path("spaces/<int:space_id>/members/me", views.MyMembershipView.as_view(), name="v2-member-me"),
    path("spaces/<int:space_id>/invites", views.InviteCreateView.as_view(), name="v2-invites"),

    path("themes", views.ThemeListView.as_view(), name="v2-themes"),
    path("spaces/<int:space_id>/appearance", views.AppearanceView.as_view(), name="v2-appearance"),

    path("spaces/<int:space_id>/menus", views.MenuListCreateView.as_view(), name="v2-menus"),
    path("menus/<int:menu_id>", views.MenuDetailView.as_view(), name="v2-menu-detail"),
    path("menus/<int:menu_id>/sections", views.MenuSectionCreateView.as_view(), name="v2-section-create"),
    path("sections/<int:section_id>", views.MenuSectionDetailView.as_view(), name="v2-section-detail"),
    path("sections/<int:section_id>/dishes", views.DishCreateView.as_view(), name="v2-dish-create"),
    path("dishes/<int:dish_id>", views.DishDetailView.as_view(), name="v2-dish-detail"),

    path("spaces/<int:space_id>/meal-sessions", views.MealSessionListCreateView.as_view(), name="v2-meal-sessions"),
    path("meal-sessions/<int:session_id>", views.MealSessionDetailView.as_view(), name="v2-meal-session-detail"),
    path("meal-sessions/<int:session_id>/choices", views.ChoiceCreateView.as_view(), name="v2-choice-create"),
    path("meal-sessions/<int:session_id>/confirm", views.ConfirmSessionView.as_view(), name="v2-session-confirm"),
    path("meal-sessions/<int:session_id>/start", views.StartSessionView.as_view(), name="v2-session-start"),
    path("meal-sessions/<int:session_id>/complete", views.CompleteSessionView.as_view(), name="v2-session-complete"),

    path("spaces/<int:space_id>/records", views.RecordListView.as_view(), name="v2-records"),
    path("spaces/<int:space_id>/preferences/me", views.PreferenceView.as_view(), name="v2-preference-me"),
    path("media-assets", views.MediaAssetCreateView.as_view(), name="v2-media-assets"),
]
