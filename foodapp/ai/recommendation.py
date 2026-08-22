from foodapp.models import NGO


def find_best_ngos(city=None):
    ngos = NGO.objects.filter(status="Active")

    if city:
        ngos = ngos.filter(city__icontains=city)

    return ngos[:5]