from django.templatetags import tz
from django.test import TestCase
from django.utils import timezone

from lsb.models import Champion
from lsb.models import Product
from lsb.models import Skin


class TestWithIsDisabled(TestCase):
    def setUp(self):
        future = timezone.now() + timezone.timedelta(days=1)
        Product.objects.create(username="valid0")
        Product.objects.create(
            username="valid1", disabled_until=timezone.now()
        )
        Product.objects.create(username="disabled0", disabled_until=future)

    def test(self):
        valid = Product.objects.with_is_disabled().filter(is_disabled=False)
        disabled = Product.objects.with_is_disabled().filter(is_disabled=True)
        self.assertEqual(valid.count(), 2)
        self.assertEqual(disabled.count(), 1)


class TestWithIsOldStock(TestCase):
    def setUp(self):
        Product.objects.create(
            username="old0",
            date_last_played=timezone.datetime(
                2020, 1, 1, tzinfo=timezone.utc
            ),
        )
        Product.objects.create(
            username="new0",
            date_last_played=timezone.datetime(
                2023, 1, 1, tzinfo=timezone.utc
            ),
        )
        Product.objects.create(
            username="new1",
            date_last_played=None,
        )

    def test(self):
        old = Product.objects.with_is_old_stock().filter(is_old_stock=True)
        new = Product.objects.with_is_old_stock().filter(is_old_stock=False)
        self.assertEqual(old.count(), 1)
        self.assertEqual(new.count(), 2)


class TestWithIsRanked(TestCase):
    def setUp(self):
        Product.objects.create(username="u0", rank="UNRANKED")
        Product.objects.create(username="u1", rank="UNRANKED")
        Product.objects.create(username="r0", rank="GOLD")
        Product.objects.create(username="r1", rank="PLATINUM", division="I")
        Product.objects.create(username="r2", rank="DIAMOND", division="IV")

    def test(self):
        unranked = Product.objects.with_is_ranked().filter(is_ranked=False)
        ranked = Product.objects.with_is_ranked().filter(is_ranked=True)
        self.assertEqual(unranked.count(), 2)
        self.assertEqual(ranked.count(), 3)


class TestSkinGetOrCreateById(TestCase):
    def test(self):
        # skin/champions are empty at first
        assert Skin.objects.count() == 0
        assert Champion.objects.count() == 0
        # this creates a new skin 999999 and champion 999
        Skin.objects.get_or_create_by_id(999999)
        assert Skin.objects.count() == 1
        assert Champion.objects.count() == 1
        assert Skin.objects.get(id=999999).champion.name == "999"


class TestGetIsOldStock(TestCase):
    def test_get_is_old_stock(self):
        obj = Product.objects.create(
            username="old1",
            date_last_played=timezone.datetime(
                2020, 1, 1, tzinfo=timezone.utc
            ),
        )
        self.assertTrue(obj.get_is_old_stock())
        obj = Product.objects.create(
            username="new0",
            date_last_played=timezone.datetime(
                2023, 1, 1, tzinfo=timezone.utc
            ),
        )
        self.assertFalse(obj.get_is_old_stock())
        obj = Product.objects.create(
            username="new1",
            date_last_played=None,
        )
        self.assertFalse(obj.get_is_old_stock())
