import io
import tempfile
from datetime import timedelta

from django.test import override_settings
from django.utils import timezone
from PIL import Image
from rest_framework.test import APITestCase

from .models import Account, AuthToken, MealRecord, Membership, Space


def png_upload(name="picture.png", size=(32, 32)):
    stream = io.BytesIO()
    Image.new("RGB", size, "#E98D74").save(stream, format="PNG")
    stream.name = name
    stream.seek(0)
    return stream


class V2ApiTestCase(APITestCase):
    password = "DiningTogether!2026"

    def register(self, email, nickname):
        response = self.client.post("/api/v2/auth/register", {"email": email, "password": self.password, "nickname": nickname}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def authorize(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def create_space(self, name="两个人的小餐桌"):
        response = self.client.post("/api/v2/spaces", {"name": name}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def test_h5_auth_issues_opaque_revokeable_token(self):
        payload = self.register("one@example.com", "小一")
        token = payload["token"]
        self.assertGreater(len(token), 40)
        stored = AuthToken.objects.get(account_id=payload["account"]["id"])
        self.assertNotEqual(stored.digest, token)
        self.assertEqual(len(stored.digest), 64)

        self.authorize("known-openid-is-not-a-token")
        self.assertEqual(self.client.get("/api/v2/auth/me").status_code, 401)
        self.authorize(token)
        self.assertEqual(self.client.get("/api/v2/auth/me").status_code, 200)
        self.assertEqual(self.client.post("/api/v2/auth/logout").status_code, 204)
        self.assertEqual(self.client.get("/api/v2/auth/me").status_code, 401)

    def test_every_resource_is_isolated_by_space_membership(self):
        first = self.register("first@example.com", "甲")
        self.authorize(first["token"])
        space = self.create_space()
        menu_id = self.client.get(f"/api/v2/spaces/{space['id']}/menus").data[0]["id"]

        self.client.credentials()
        second = self.register("second@example.com", "乙")
        self.authorize(second["token"])
        for url in [
            f"/api/v2/spaces/{space['id']}",
            f"/api/v2/spaces/{space['id']}/appearance",
            f"/api/v2/spaces/{space['id']}/menus",
            f"/api/v2/menus/{menu_id}",
            f"/api/v2/spaces/{space['id']}/meal-sessions",
            f"/api/v2/spaces/{space['id']}/records",
            f"/api/v2/spaces/{space['id']}/preferences/me",
        ]:
            self.assertEqual(self.client.get(url).status_code, 404, url)
        self.assertEqual(self.client.patch(f"/api/v2/menus/{menu_id}", {"name": "越权改名"}, format="json").status_code, 404)

    def test_theme_navigation_and_member_personalization_are_validated(self):
        payload = self.register("theme@example.com", "布丁")
        self.authorize(payload["token"])
        space = self.create_space()
        themes = self.client.get("/api/v2/themes")
        self.assertEqual(themes.status_code, 200)
        self.assertGreaterEqual(len(themes.data), 4)

        response = self.client.patch(
            f"/api/v2/spaces/{space['id']}/appearance",
            {
                "preset_slug": "berry-date",
                "palette_overrides": {"primary": "#B04A62", "surface": "#FFF8FA"},
                "background_type": "gradient",
                "background_value": "berry",
                "card_style": "glass",
                "corner_radius": 24,
                "menu_image_style": "polaroid",
                "home_title": "今晚的约会菜单",
                "navigation_labels": {"today": "今晚", "menu": "小菜单", "records": "回忆", "us": "我们"},
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["navigation_labels"]["records"], "回忆")

        bad = self.client.patch(
            f"/api/v2/spaces/{space['id']}/appearance",
            {"navigation_labels": {"today": "今天", "script": "alert(1)"}, "palette_overrides": {"primary": "red;position:fixed"}},
            format="json",
        )
        self.assertEqual(bad.status_code, 400)

        member = self.client.patch(
            f"/api/v2/spaces/{space['id']}/members/me",
            {"display_name": "专属大厨", "avatar_frame": "heart", "accent_color": "#E98D74", "avatar_url": "https://example.com/avatar.png"},
            format="json",
        )
        self.assertEqual(member.status_code, 200, member.data)
        self.assertEqual(member.data["avatar_frame"], "heart")

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_authenticated_image_upload_checks_real_image_and_membership(self):
        payload = self.register("media@example.com", "相册")
        self.authorize(payload["token"])
        space = self.create_space()
        response = self.client.post(
            "/api/v2/media-assets",
            {"purpose": "background", "space_id": space["id"], "file": png_upload("picture.png")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["content_type"], "image/png")
        self.assertEqual(response.data["width"], 32)
        self.assertTrue(response.data["url"].startswith("http://testserver/media/v2/"))

        fake = io.BytesIO(b"not an image")
        fake.name = "bad.png"
        rejected = self.client.post("/api/v2/media-assets", {"purpose": "avatar", "file": fake}, format="multipart")
        self.assertEqual(rejected.status_code, 400)

    def test_invite_join_and_main_meal_flow(self):
        first = self.register("cook@example.com", "做饭的人")
        self.authorize(first["token"])
        space = self.create_space("周末小厨房")
        menus = self.client.get(f"/api/v2/spaces/{space['id']}/menus")
        self.assertEqual(menus.status_code, 200)
        self.assertEqual(len(menus.data), 1)
        self.assertEqual(menus.data[0]["image_style"], "polaroid")
        self.assertGreaterEqual(len(menus.data[0]["sections"]), 3)
        dish = menus.data[0]["sections"][0]["dishes"][0]

        invite = self.client.post(f"/api/v2/spaces/{space['id']}/invites", {}, format="json")
        self.assertEqual(invite.status_code, 201, invite.data)
        self.client.credentials()
        second = self.register("partner@example.com", "一起吃的人")
        self.authorize(second["token"])
        joined = self.client.post("/api/v2/spaces/join", {"code": invite.data["code"]}, format="json")
        self.assertEqual(joined.status_code, 201, joined.data)
        self.assertEqual(Membership.objects.filter(space_id=space["id"]).count(), 2)

        scheduled_for = (timezone.now() + timedelta(hours=2)).isoformat()
        session = self.client.post(
            f"/api/v2/spaces/{space['id']}/meal-sessions",
            {"title": "今晚一起吃", "meal_type": "dinner", "scheduled_for": scheduled_for},
            format="json",
        )
        self.assertEqual(session.status_code, 201, session.data)
        choice = self.client.post(
            f"/api/v2/meal-sessions/{session.data['id']}/choices",
            {"dish": dish["id"], "note": "想吃这个"},
            format="json",
        )
        self.assertEqual(choice.status_code, 201, choice.data)
        confirmed = self.client.post(f"/api/v2/meal-sessions/{session.data['id']}/confirm", {}, format="json")
        self.assertEqual(confirmed.status_code, 200, confirmed.data)
        self.assertEqual(confirmed.data["status"], "confirmed")
        self.assertEqual(len(confirmed.data["plan_items"]), 1)
        started = self.client.post(f"/api/v2/meal-sessions/{session.data['id']}/start", {}, format="json")
        self.assertEqual(started.status_code, 200, started.data)
        invalid_memory = self.client.post(
            f"/api/v2/meal-sessions/{session.data['id']}/complete",
            {"photo_url": "javascript:alert(1)", "note": "x" * 501},
            format="json",
        )
        self.assertEqual(invalid_memory.status_code, 400, invalid_memory.data)
        completed = self.client.post(
            f"/api/v2/meal-sessions/{session.data['id']}/complete",
            {"rating": 5, "note": "下次还做"},
            format="json",
        )
        self.assertEqual(completed.status_code, 201, completed.data)
        self.assertEqual(completed.data["rating"], 5)
        self.assertEqual(completed.data["title"], "今晚一起吃")
        active = self.client.get(f"/api/v2/spaces/{space['id']}/meal-sessions?active=true")
        self.assertEqual(active.status_code, 200)
        self.assertEqual(active.data, [])
        records = self.client.get(f"/api/v2/spaces/{space['id']}/records")
        self.assertEqual(records.status_code, 200)
        self.assertEqual(len(records.data), 1)
        self.assertEqual(MealRecord.objects.filter(space_id=space["id"]).count(), 1)

    def test_only_one_active_session_and_duplicate_choices_are_rejected(self):
        payload = self.register("concurrency@example.com", "一起选")
        self.authorize(payload["token"])
        space = self.create_space("不会开出两张桌")
        dish = self.client.get(f"/api/v2/spaces/{space['id']}/menus").data[0]["sections"][0]["dishes"][0]
        session_payload = {
            "title": "第一桌",
            "meal_type": "dinner",
            "scheduled_for": timezone.now().isoformat(),
        }
        first = self.client.post(f"/api/v2/spaces/{space['id']}/meal-sessions", session_payload, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        second = self.client.post(f"/api/v2/spaces/{space['id']}/meal-sessions", session_payload, format="json")
        self.assertEqual(second.status_code, 400, second.data)
        self.assertIn("已有正在进行", str(second.data))

        choice_url = f"/api/v2/meal-sessions/{first.data['id']}/choices"
        self.assertEqual(self.client.post(choice_url, {"dish": dish["id"]}, format="json").status_code, 201)
        self.assertEqual(self.client.post(choice_url, {"dish": dish["id"]}, format="json").status_code, 400)
        self.assertEqual(self.client.post(choice_url, {"custom_name": "神秘料理"}, format="json").status_code, 201)
        self.assertEqual(self.client.post(choice_url, {"custom_name": "神秘料理"}, format="json").status_code, 400)
