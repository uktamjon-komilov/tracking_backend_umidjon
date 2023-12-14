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
        "name": "Andijon viloyati",
        "longitude": 72.166667,
        "latitude": 40.75,
    },
    {
        "name": "Buxoro viloyati",
        "longitude": 63.666667,
        "latitude": 40.166667,
    },
    {
        "name": "Fargʻona viloyati",
        "longitude": 71.35,
        "latitude": 40.43,
    },
    {
        "name": "Jizzax viloyati",
        "longitude": 67.666667,
        "latitude": 40.416667,
    },
    {
        "name": "Xorazm viloyati",
        "longitude": 61,
        "latitude": 41.333333,
    },
    {
        "name": "Namangan viloyati",
        "longitude": 71.166667,
        "latitude": 41,
    },
    {
        "name": "Navoiy viloyati",
        "longitude": 64.25,
        "latitude": 42,
    },
    {
        "name": "Qashqadaryo viloyati",
        "longitude": 66.083333,
        "latitude": 38.833333,
    },
    {
        "name": "Qoraqalpogʻiston Respublikasi",
        "longitude": 58.86,
        "latitude": 43.04,
    },
    {
        "name": "Samarqand viloyati",
        "longitude": 66.25,
        "latitude": 39.833333,
    },
    {
        "name": "Sirdaryo viloyati",
        "longitude": 68.666667,
        "latitude": 40.416667,
    },
    {
        "name": "Surxondaryo viloyati",
        "longitude": 67.5,
        "latitude": 38,
    },
    {
        "name": "Toshkent viloyati",
        "longitude": 69.75,
        "latitude": 41.166667,
    },
]
