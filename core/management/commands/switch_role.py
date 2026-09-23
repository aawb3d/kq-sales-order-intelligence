from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User


class Command(BaseCommand):
    help = "Dev utility: assign a role to a user so you can test role-gated screens without the Django shell."

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username of the account to update")
        parser.add_argument(
            "role",
            type=str,
            choices=[choice[0] for choice in Role.RoleName.choices],
            help="One of: " + ", ".join(choice[0] for choice in Role.RoleName.choices),
        )

    def handle(self, *args, **options):
        username = options["username"]
        role_name = options["role"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"No user found with username '{username}'")

        role, _ = Role.objects.get_or_create(role_name=role_name)
        user.role = role
        user.save()

        self.stdout.write(self.style.SUCCESS(f"'{username}' is now assigned the '{role.get_role_name_display()}' role."))