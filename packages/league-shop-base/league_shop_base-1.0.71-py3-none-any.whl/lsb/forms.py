from django import forms


class ProductStatusRemarksForm(forms.Form):
    status = forms.CharField(initial="unchanged", required=False)
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": "5"}),
        initial="unchanged",
    )


class CheckPasswordForm(forms.Form):
    encryption_key = forms.CharField()


class UpdateBannedAccountsForm(forms.Form):
    delimiter = forms.ChoiceField(
        label="Delimiter",
        choices=[
            (",", "Comma ,"),
            (":", "Colon : "),
            (";", "Semicolon ;"),
        ],
    )
    file = forms.FileField()
