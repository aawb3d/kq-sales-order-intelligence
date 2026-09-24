from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def role_home_redirect(request):
    """
    Smart landing page — redirects each user to their role-appropriate
    home screen instead of throwing a 403 on the wrong page.
    """
    role = getattr(request.user, "role", None)
    if role is None:
        # No role assigned — send to admin to get one assigned
        return render(request, "core/no_role.html")

    role_name = role.role_name

    if role_name == "sales_agent":
        return redirect("orders:track_orders")
    elif role_name == "warehouse_officer":
        return redirect("inventory:confirm_fulfilment")
    elif role_name == "operations_manager":
        return redirect("analytics:dashboard")
    elif role_name == "system_administrator":
        return redirect("analytics:system_settings")

    return redirect("accounts:login")


def custom_permission_denied(request, exception=None):
    """
    Friendly 403 page with a button to go back to the correct home page.
    """
    return render(request, "core/403.html", status=403)
