from apps.accounts.models import SocialAccount


class SocialAccountSelector:
    @staticmethod
    def get_provider(provider_id: str, provider_name: str):
        social = SocialAccount.objects.filter(
            provider=provider_name,
            provider_user_id=provider_id
        ).first()
        return social
