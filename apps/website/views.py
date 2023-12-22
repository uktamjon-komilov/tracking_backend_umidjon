from django.shortcuts import render


def privacy_policy_view(request):
    return render(request, "privacy_policy.html")


def account_deletion_view(request):
    return render(request, "account_deletion.html")
