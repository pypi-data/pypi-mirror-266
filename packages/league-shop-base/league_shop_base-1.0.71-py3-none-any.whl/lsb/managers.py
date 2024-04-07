from typing import TypeVar

from django.db import models
from django.db.models import ExpressionWrapper
from django.db.models import Q
from django.utils import timezone

import lsb.models
from lsb.constants import OLD_STOCK_THRESHOLD

T = TypeVar("T")


class ProductQuerySet(models.QuerySet[T]):
    def valid(self):
        return self.filter(
            is_purchased=False,
            is_banned=False,
            is_auth_error=False,
            disabled_until__lt=timezone.now(),
        )

    def with_is_disabled(self):
        return self.annotate(
            is_disabled=ExpressionWrapper(
                Q(disabled_until__gt=timezone.now()),
                output_field=models.BooleanField(),
            )
        )

    def with_is_old_stock(self, threshold=OLD_STOCK_THRESHOLD):
        return self.annotate(
            is_old_stock=ExpressionWrapper(
                # important note:
                # date last played null is marked as new stock
                # even though it can be old stock
                Q(date_last_played__lte=threshold)
                & Q(date_last_played__isnull=False),
                output_field=models.BooleanField(),
            )
        )

    def with_is_ranked(self):
        return self.annotate(
            is_ranked=ExpressionWrapper(
                ~Q(rank="UNRANKED"),
                output_field=models.BooleanField(),
            )
        )


class ProductManager(models.Manager[T]):
    def get_queryset(self) -> ProductQuerySet[T]:
        return ProductQuerySet(self.model, using=self._db)

    def valid(self):
        return self.get_queryset().valid()

    def with_is_disabled(self):
        return self.get_queryset().with_is_disabled()

    def with_is_old_stock(self, threshold=OLD_STOCK_THRESHOLD):
        return self.get_queryset().with_is_old_stock(threshold)

    def with_is_ranked(self):
        return self.get_queryset().with_is_ranked()


class ChampionManager(models.Manager[T]):
    def get_or_create_by_id(self, id):
        return self.get_or_create(id=id, defaults={"name": str(id)})


class SkinManager(models.Manager[T]):
    def get_or_create_by_id(self, id):
        champion = int(id / 1000)  # remove last 3 digits
        champion, _ = lsb.models.Champion.objects.get_or_create_by_id(champion)
        return self.get_or_create(
            id=id,
            defaults={
                "champion": champion,
                "name": str(id),
                "tier": "UNKNOWN",
            },
        )
