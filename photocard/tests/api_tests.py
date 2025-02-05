from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from photocard.exceptions import UnauthorizedException
from photocard.models import PhotoCardSaleStatus
from photocard.scripts.init_photo_card_data import init_photo_card_data
from user.tasks import create_welcome_cash

User = get_user_model()


class PhotocardAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.userA = User.objects.create_user(email="tester1@example.com", nickname="김포카", password="111111")
        self.userB = User.objects.create_user(email="tester2@exmaple.com", nickname="김포카2", password="111111")
        self.userC = User.objects.create_user(email="tester3@exmaple.com", nickname="김포카3", password="111111")
        create_welcome_cash(self.userA.id)
        create_welcome_cash(self.userB.id)
        create_welcome_cash(self.userC.id)

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        for i in range(0, 3):
            init_photo_card_data()  # 테스트 포토카드 15개 생성

    def __login(self, user: User):
        login_response = self.client.post("/api/users/auth/login/", {"email": user.email, "password": "111111"})
        access = login_response.data.get("token", {}).get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_포토카드_조회(self):
        response = self.client.get("/api/photocards/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data.get("results")), 10)
        self.assertIsNotNone(len(response.data.get("next")))

    def test_포토카드_판매_등록(self):
        self.__login(self.userA)

        param = {"price": 10000}
        response = self.client.post("/api/photocards/1/sales/", param)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(response.data.get("price"), param.get("price"))
        self.assertEqual(response.data.get("total_price"), response.data.get("price") + response.data.get("fee"))
        self.assertEqual(response.data.get("seller_id"), self.userA.id)

    def test_포토카드_판매_수정(self):
        self.__login(self.userA)
        param = {"price": 10000}
        response = self.client.post("/api/photocards/1/sales/", param)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(response.data.get("price"), param.get("price"))
        self.assertEqual(response.data.get("total_price"), response.data.get("price") + response.data.get("fee"))
        self.assertEqual(response.data.get("seller_id"), self.userA.id)

        sale_id = response.data.get("uuid")

        param = {"price": 5000}
        update_response = self.client.patch(f"/api/photocards/1/sales/{sale_id}/", param)

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(update_response.data.get("price"), param.get("price"))
        self.assertEqual(
            update_response.data.get("total_price"), update_response.data.get("price") + update_response.data.get("fee")
        )
        self.assertEqual(update_response.data.get("seller", {}).get("id"), self.userA.id)

    def test_포토카드_판매_수정_권한없음_예외(self):
        self.__login(self.userA)
        param = {"price": 10000}
        response = self.client.post("/api/photocards/1/sales/", param)
        sale_id = response.data.get("uuid")

        # userB로 로그인
        self.__login(self.userB)
        param = {"price": 5000}
        update_response = self.client.patch(f"/api/photocards/1/sales/{sale_id}/", param)
        self.assertEqual(update_response.status_code, UnauthorizedException.status_code)

    def test_포토카드_판매_목록(self):
        self.__login(self.userA)
        # 12개의 테스트 데이터
        for i in range(1, 13):
            self.client.post(f"/api/photocards/{i}/sales/", {"price": i * 100})

        # 3개의 중복 데이터를 만든다.
        # 가장 마지막에 추가된 판매건이 첫번째로 조회된다.
        self.client.post(f"/api/photocards/10/sales/", {"price": 300})
        self.client.post(f"/api/photocards/3/sales/", {"price": 200})
        self.client.post(f"/api/photocards/5/sales/", {"price": 0})

        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")
        # pagination limit이 10이므로 10보단 작다.
        # 중복이 제거되었을 것이다.
        self.assertLessEqual(len(results), 10)
        self.assertEqual(results[0]["price"], 0)
        self.assertEqual(results[0]["photo_card_id"], 5)

        photo_card_id_set = {result["photo_card_id"] for result in results}
        # photo_card_id에 대한 중복이 존재하지 않는다.
        self.assertEqual(len(results), len(photo_card_id_set))

    def test_포토카드_판매_목록_업데이트(self):
        self.__login(self.userA)
        photo_card_id_to_be_updated = 10
        sale_id_to_be_updated = ""

        # 12개의 테스트 데이터
        for i in range(1, 13):
            sale = self.client.post(f"/api/photocards/{i}/sales/", {"price": i * 100})
            if i == photo_card_id_to_be_updated:
                sale_id_to_be_updated = sale.data.get("uuid")

        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")

        # 가장 마지막에 추가된 12가 첫 번째로 조회될 것이다.
        self.assertEqual(results[0]["photo_card_id"], 12)

        # 10번을 수정하면 10이 제일 먼저 조회 될 것이다.
        self.client.patch(f"/api/photocards/10/sales/{sale_id_to_be_updated}/", {"price": 12000})

        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")

        # 가장 최근에 수정된 10이 첫 번째로 조회될 것이다.
        self.assertEqual(results[0]["photo_card_id"], photo_card_id_to_be_updated)
        self.assertEqual(results[0]["price"], 12000)

        # 가격이 더 저렴한 판매건이 추가되면 가격이 변경될 것이다.
        self.client.post(f"/api/photocards/{photo_card_id_to_be_updated}/sales/", {"price": 0})
        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")

        # 10번 판매건의 가격이 좀 더 저렴하게 변경된다.
        self.assertEqual(results[0]["photo_card_id"], photo_card_id_to_be_updated)
        self.assertEqual(results[0]["price"], 0)

    def test_포토카드_구매(self):
        self.__login(self.userA)
        # 15개의 테스트 데이터
        for i in range(1, 16):
            result = self.client.post(f"/api/photocards/{i}/sales/", {"price": i * 100})

        # userB로 로그인
        self.__login(self.userB)

        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")

        photo_card_id = results[0]["photo_card_id"]
        sale_id = results[0]["uuid"]

        response = self.client.post(f"/api/photocards/{photo_card_id}/sales/{sale_id}/purchase/")

        self.assertEqual(response.data.get("seller", {}).get("id"), self.userA.id)
        self.assertEqual(response.data.get("buyer", {}).get("id"), self.userB.id)

        self.assertEqual(10000 - self.userB.cash, response.data.get("total_price"))

        photo_card_sale = self.client.get(f"/api/photocards/{photo_card_id}/sales/{sale_id}/")
        self.assertEqual(photo_card_sale.data.get("status"), PhotoCardSaleStatus.COMPLETED.value)

    def test_포토카드_구매_실패(self):
        self.__login(self.userA)
        # 15개의 테스트 데이터
        for i in range(1, 16):
            result = self.client.post(f"/api/photocards/{i}/sales/", {"price": i * 100})

        # userB로 로그인
        self.__login(self.userB)

        response = self.client.get("/api/photocards/sales/")
        results = response.data.get("results")

        photo_card_id = results[0]["photo_card_id"]
        sale_id = results[0]["uuid"]

        self.client.post(f"/api/photocards/{photo_card_id}/sales/{sale_id}/purchase/")

        response = self.client.post(f"/api/photocards/{photo_card_id}/sales/{sale_id}/purchase/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
