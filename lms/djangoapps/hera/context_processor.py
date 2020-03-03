from .models import UserOnboarding, Mascot


def user_onboarding(request):
    #TODO: need to improve this logic, ideally to get onboarding pages via ajax request 
    # in order not to request DB for onboarding data every time page loads
    if request.user.is_authenticated():
        onboarding_data = {
            'is_onboarding_passed': False,
        }
        if UserOnboarding.onboarding_is_passed(request.user.id):
            onboarding_data['is_onboarding_passed'] = True
            onboarding_data['onboarding_pages'] = UserOnboarding.get_static_pages()
            onboarding_data['onboarding_mascot'] = Mascot.onboarding_img_url()
        return onboarding_data
    return {}
