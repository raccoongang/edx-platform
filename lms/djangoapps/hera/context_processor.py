from .models import UserOnboarding


def user_onboarding(request):
    #TODO: need to improve this logic, ideally to get onboarding pages via ajax request 
    # in order not to request DB for onboarding data every time page loads
    if request.user.is_authenticated():
        user_onboarding = UserOnboarding.objects.filter(user=request.user).first()
        onboarding_data = {
            'is_onboarding_passed': False,
        }
        if user_onboarding and user_onboarding.is_passed():
            onboarding_data['is_onboarding_passed'] = True
            onboarding_data['onboarding_pages'] = user_onboarding.get_pages()
        return onboarding_data
    return {}
