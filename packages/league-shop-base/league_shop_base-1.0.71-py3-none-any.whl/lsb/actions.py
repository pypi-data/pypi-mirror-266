import csv
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.html import escape
from django.shortcuts import render
from django.utils import timezone
from form_action import extra_button
from form_action import form_action

from lsb.crypto import decrypt_by_key
from lsb.exceptions import SkinParseException
from lsb.forms import CheckPasswordForm
from lsb.forms import ProductStatusRemarksForm
from lsb.forms import UpdateBannedAccountsForm
from lsb.models import Product
from lsb.models import max_datetime
from lsb.models import min_datetime

from .utils.skins import create_or_update_skins


def mark_as_handleveled(modeladmin, request, queryset):
    updated = queryset.update(is_handleveled=True)
    messages.info(request, f"{updated} product(s) marked as handleveled.")


def clear_handleveled(modeladmin, request, queryset):
    updated = queryset.update(is_handleveled=False)
    messages.info(request, f"Cleared handleveled from {updated} product(s).")


@form_action(ProductStatusRemarksForm, description="Mark as disabled")
def mark_as_disabled_with_status(modeladmin, request, queryset, form):
    status = form.cleaned_data["status"]
    remarks = form.cleaned_data["remarks"]

    to_update = {
        "disabled_until": max_datetime,
    }

    if status != "unchanged":
        to_update["status"] = None if status == "" else status
    if remarks != "unchanged":
        to_update["remarks"] = None if remarks == "" else remarks

    updated = queryset.update(**to_update)
    messages.info(
        request,
        (
            f"{updated} product(s) marked as disabled with status {status} and"
            f" remarks {remarks}."
        ),
    )


@form_action(ProductStatusRemarksForm, description="Clear disabled")
def clear_disabled_with_status(modeladmin, request, queryset, form):
    status = form.cleaned_data["status"]
    remarks = form.cleaned_data["remarks"]

    to_update = {
        "disabled_until": min_datetime,
    }

    if status != "unchanged":
        to_update["status"] = None if status == "" else status
    if remarks != "unchanged":
        to_update["remarks"] = None if remarks == "" else remarks

    updated = queryset.update(**to_update)
    messages.info(
        request,
        (
            f"Cleared disabled from {updated} product(s) marked with status"
            f" {status} and remarks {remarks}."
        ),
    )


@extra_button("Update skins")
def update_skins(request):
    try:
        created_count, updated_count = create_or_update_skins()
        messages.success(
            request,
            (
                f"{created_count}(s) skins created. {updated_count}(s) skins"
                " updated."
            ),
        )
        return HttpResponseRedirect("/admin/lsb/skin/")
    except SkinParseException as e:
        messages.error(request, str(e))
        return HttpResponseRedirect("/admin/lsb/skin/")


@form_action(
    CheckPasswordForm, description="Check password using encryption key"
)
def check_password(modeladmin, request, queryset, form):
    try:
        key = form.cleaned_data["encryption_key"]
        data = queryset.values("username", "password")
        data = [
            d["username"] + ":" + escape(decrypt_by_key(d["password"], key))
            for d in data
        ]
        data = "\n".join(data)
        return HttpResponse("<pre>" + data + "</pre>")
    except ValueError:
        messages.error(request, "Invalid encryption key.")
        return HttpResponseRedirect("/admin/lsb/product/")


@extra_button("Update Banned Accounts")
def update_banned_accounts(request):
    if request.method == "POST":
        form = UpdateBannedAccountsForm(request.POST, request.FILES)
        if form.is_valid():
            delimiter = form.cleaned_data["delimiter"]
            uploaded_file = form.cleaned_data["file"]
            try:
                # read the csv file
                decoded_file = (
                    uploaded_file.read().decode("utf-8").splitlines()
                )
                reader = csv.reader(decoded_file, delimiter=delimiter)

                # validate the selected delimter
                csv_delimiter = csv.Sniffer().sniff(decoded_file[0]).delimiter
                if delimiter != csv_delimiter:
                    messages.error(request, "Choose a valid delimiter.")
                    return HttpResponseRedirect(
                        "/admin/lsb/product/actions/update_banned_accounts/"
                    )

                next(reader)  # skipping the header
                total_count = 0
                update_count = 0
                for row in reader:
                    username, date_banned, ban_reason, *_ = row
                    try:
                        date_banned = datetime.strptime(
                            date_banned, "%d/%m/%Y"
                        )
                    except ValueError:
                        date_banned = datetime.now()

                    # converting naive datetime to aware datetime objects to remove warnings
                    date_banned = timezone.make_aware(date_banned)
                    ban_reason = ban_reason or "THIRD_PARTY_TOOLS"

                    try:
                        product = Product.objects.get(
                            username=username, is_banned=False
                        )

                        # Update the fields
                        product.is_banned = True
                        product.date_banned = date_banned
                        product.ban_reason = ban_reason
                        product.save()
                        update_count += 1

                    except Product.DoesNotExist:
                        pass
                    total_count = total_count + 1
                messages.success(
                    request,
                    f"({update_count}/{total_count}) banned account(s) updated successfully.",
                )
                return HttpResponseRedirect("/admin/lsb/product/")

            except UnicodeDecodeError:
                messages.error(
                    request,
                    "Select valid file format. The file should be in CSV format.",
                )
                return HttpResponseRedirect(
                    "/admin/lsb/product/actions/update_banned_accounts/"
                )

    else:
        form = UpdateBannedAccountsForm()

    return render(request, "lsb/update_ban.html", {"form": form})
