def recycling_company(request):
    if not request.user.is_authenticated:
        return {'recycling_company': None}
    try:
        return {'recycling_company': request.user.recycling_company}
    except Exception:
        return {'recycling_company': None}
