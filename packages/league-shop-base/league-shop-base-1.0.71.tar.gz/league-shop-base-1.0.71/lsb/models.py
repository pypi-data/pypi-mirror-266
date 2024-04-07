from itertools import chain

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from lsb.constants import OLD_STOCK_THRESHOLD
from lsb.managers import ChampionManager
from lsb.managers import ProductManager
from lsb.managers import SkinManager

from .crypto import encrypt
from .crypto import is_encrypted

min_datetime = timezone.datetime(1970, 1, 1, 0, 0, 0, 0, timezone.utc)
max_datetime = timezone.datetime(3000, 1, 1, 0, 0, 0, 0, timezone.utc)


SKIN_TIERS = (
    ("ULTIMATE", "Ultimate"),
    ("MYTHIC", "Mythic"),
    ("LEGENDARY", "Legendary"),
    ("EPIC", "Epic"),
    ("STANDARD", "Standard"),
    ("BUDGET", "Budget"),
    ("LIMITED", "Limited"),
    ("UNKNOWN", "Unknown"),
)

REGION_CHOICES = [
    ("EUW", "EUW"),
    ("EUNE", "EUNE"),
    ("NA", "NA"),
    ("OC1", "OCE"),
    ("RU", "RU"),
    ("TR", "TR"),
    ("LA1", "LAN"),
    ("LA2", "LAS"),
    ("BR", "BR"),
    ("JP", "JP"),
    ("KR", "KR"),
    ("PH2", "PH"),
    ("SG2", "SG"),
    ("TH2", "TH"),
    ("TW2", "TW"),
    ("VN2", "VN"),
    ("PBE", "PBE"),
]


RANK_CHOICES = (
    ("UNRANKED", "Unranked"),
    ("IRON", "Iron"),
    ("BRONZE", "Bronze"),
    ("SILVER", "Silver"),
    ("GOLD", "Gold"),
    ("PLATINUM", "Platinum"),
    ("EMERALD", "Emerald"),
    ("DIAMOND", "Diamond"),
    ("MASTER", "Master"),
    ("GRANDMASTER", "Grandmaster"),
    ("CHALLENGER", "Challenger"),
)


# list of rank values that are ranked
RANKED_VALUES = [r[0] for r in RANK_CHOICES if r[0] != "UNRANKED"]

DIVISION_CHOICES = (
    ("I", "I"),
    ("II", "II"),
    ("III", "III"),
    ("IV", "IV"),
)


class Champion(models.Model):
    """Model representing champion"""

    objects: ChampionManager["Champion"] = ChampionManager()

    name = models.CharField(max_length=50)
    roles = models.TextField(blank=True, null=True)
    lanes = models.TextField(blank=True, null=True)

    date_created = models.DateTimeField(default=None, blank=True, null=True)
    date_modified = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)


class Skin(models.Model):
    """Model representing champion skin"""

    objects: SkinManager["Skin"] = SkinManager()

    tier = models.CharField(max_length=9, choices=SKIN_TIERS, default=None)
    name = models.CharField(max_length=50)
    champion = models.ForeignKey(
        Champion, related_name="skins", on_delete=models.PROTECT
    )
    value = models.IntegerField(blank=True, null=True, default=None)

    date_created = models.DateTimeField(default=None, blank=True, null=True)
    date_modified = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.pk})"

    class Meta:
        verbose_name = "Skin"
        verbose_name_plural = "Skins"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model"""

    objects: ProductManager["Product"] = ProductManager()

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    summoner_name = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    region = models.CharField(
        max_length=4, choices=REGION_CHOICES, default="EUW"
    )
    level = models.FloatField(default=1)
    blue_essence = models.PositiveIntegerField(default=0)
    orange_essence = models.PositiveIntegerField(default=0)
    mythic_essence = models.PositiveIntegerField(default=0)
    discrete_level = models.PositiveIntegerField()
    discrete_blue_essence = models.PositiveIntegerField()
    skins = models.ManyToManyField(Skin, blank=True)
    permanent_skins = models.ManyToManyField(
        Skin, blank=True, related_name="permanent_skin_products"
    )
    owned_skins = models.ManyToManyField(
        Skin, blank=True, related_name="owned_skin_products"
    )
    is_handleveled = models.BooleanField(default=False)
    rank = models.CharField(
        max_length=32,
        choices=RANK_CHOICES,
        default="UNRANKED",
    )
    division = models.CharField(
        max_length=4,
        choices=DIVISION_CHOICES,
        default=None,
        blank=True,
        null=True,
    )
    flash_key = models.CharField(
        max_length=1, null=True, blank=True, default=None
    )
    solo_wins = models.PositiveIntegerField(
        null=True, blank=True, default=None
    )
    solo_losses = models.PositiveIntegerField(
        null=True, blank=True, default=None
    )
    is_safe = models.BooleanField(default=True)
    is_bare_metal = models.BooleanField(default=False)
    is_proxmox = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)

    # use case: aram-only/any-game-mode handleveled
    # False for existing products
    is_aram_only = models.BooleanField(default=False)

    uploaded_by = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
    )
    remarks = models.TextField(blank=True, null=True, default=None)
    status = models.CharField(
        blank=True, null=True, default=None, max_length=32
    )

    # Error fields
    disabled_until = models.DateTimeField(default=min_datetime)
    is_auth_error = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True, default=None)
    date_banned = models.DateTimeField(blank=True, null=True, default=None)

    # Fields to optimize filtering
    all_skins = models.ManyToManyField(
        Skin, blank=True, related_name="all_skins_products"
    )

    # Recovery fields
    email = models.EmailField(blank=True, null=True, default=None)
    date_sign_up = models.DateTimeField(blank=True, null=True, default=None)
    dob = models.DateTimeField(blank=True, null=True, default=None)
    ip_address = models.GenericIPAddressField(
        blank=True, null=True, default=None
    )
    country = models.CharField(
        max_length=50, blank=True, null=True, default=None
    )
    city = models.CharField(
        max_length=256, blank=True, null=True, default=None
    )
    date_last_played = models.DateTimeField(
        blank=True, null=True, default=None
    )

    # whether recovery fields are provided to the owner
    # True for all existing accounts, as no record exists
    # default False for new accounts added
    # example use case (in master-api):
    # (handleveled account with recovery requested can't be auctioned)
    is_recovery_requested = models.BooleanField(default=False)
    # actual (new) recovery requested accounts:
    # is_recovery_requested && tz.now() >= feature_added_date

    date_checked = models.DateTimeField(blank=True, null=True, default=None)
    date_created = models.DateTimeField(default=None, blank=True, null=True)
    date_modified = models.DateTimeField(default=None, blank=True, null=True)

    def update_all_skins(self):
        all_skins = chain(
            self.skins.all(),
            self.permanent_skins.all(),
            self.owned_skins.all(),
        )
        self.all_skins.set(list(all_skins))

    def __str__(self):
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.date_created = timezone.now()
        if not is_encrypted(self.password):
            self.password = encrypt(self.password)

        self.discrete_blue_essence = (self.blue_essence // 10000) * 10000
        self.discrete_level = (self.level // 10) * 10
        self.date_modified = timezone.now()
        super().save(*args, **kwargs)

    def get_is_old_stock(self, threshold=OLD_STOCK_THRESHOLD):
        if not self.date_last_played:
            return False
        return self.date_last_played <= threshold

    class Meta:
        indexes = [
            models.Index(fields=["region"]),
            models.Index(fields=["discrete_level"]),
            models.Index(fields=["discrete_blue_essence"]),
            models.Index(fields=["orange_essence"]),
            models.Index(fields=["rank"]),
        ]


@receiver(m2m_changed, sender=Product.skins.through)
@receiver(m2m_changed, sender=Product.permanent_skins.through)
@receiver(m2m_changed, sender=Product.owned_skins.through)
def skins_changed(sender, instance, **kwargs):
    if kwargs["action"] in ["post_add", "post_remove"]:
        instance.update_all_skins()
        instance.save()
