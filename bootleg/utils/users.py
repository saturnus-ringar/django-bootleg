
def user_is_staff(request):
    if request.user.is_staff:
        return True

    return False
