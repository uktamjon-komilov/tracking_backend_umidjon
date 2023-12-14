from apps.regions.models import COUNTRY, District, Region


def get_or_create_districts():
    region, _ = Region.objects.get_or_create(name=COUNTRY)

    for item in DISTRICTS:
        district = District.get_districts(name=item["name"]).first()
        if district:
            continue

        district = District(
            region=region,
            name=item["name"],
            centroid_longitude=item["longitude"],
            centroid_latitude=item["latitude"],
        )
        district.save()


DISTRICTS = [
    {
        "name": "Toshkent",
        "longitude": 40.4018,
        "latitude": 71.4893,
    },
]
