"""
Management command to seed the database with realistic demo data
for the TradeConnect admin dashboard.
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.core.models import Country, Service, Certification
from apps.business.models import (
    BusinessProfile,
    ContactPerson,
    BranchLocation,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo data for the dashboard"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("[SEED] Seeding database..."))

        self._create_countries()
        self._create_services()
        self._create_certifications()
        self._create_users_and_businesses()

        self.stdout.write(self.style.SUCCESS("[OK] Seeding complete!"))
        self._print_summary()

    # ==============================================================
    #  COUNTRIES
    # ==============================================================
    def _create_countries(self):
        countries = [
            "United Kingdom", "United States", "Canada", "Australia",
            "Germany", "France", "India", "Bangladesh",
            "United Arab Emirates", "Singapore", "Japan", "Brazil",
            "South Africa", "Netherlands", "Sweden",
        ]
        created = 0
        for name in countries:
            _, was_created = Country.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(f"   Countries: {created} created, {len(countries) - created} already existed")

    # ==============================================================
    #  SERVICES
    # ==============================================================
    def _create_services(self):
        services = [
            "Import & Export", "Freight Forwarding", "Customs Brokerage",
            "Warehousing", "Supply Chain Management", "Logistics",
            "Trade Finance", "Market Research", "Product Sourcing",
            "Quality Inspection", "Legal Consulting", "Business Consulting",
            "Digital Marketing", "IT Solutions", "Manufacturing",
        ]
        created = 0
        for title in services:
            _, was_created = Service.objects.get_or_create(title=title)
            if was_created:
                created += 1
        self.stdout.write(f"   Services:  {created} created, {len(services) - created} already existed")

    # ==============================================================
    #  CERTIFICATIONS
    # ==============================================================
    def _create_certifications(self):
        certs = [
            "ISO 9001", "ISO 14001", "ISO 27001",
            "CE Marking", "FDA Approved", "HACCP",
            "Fair Trade", "B Corp", "GMP Certified",
        ]
        created = 0
        for name in certs:
            _, was_created = Certification.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(f"   Certs:     {created} created, {len(certs) - created} already existed")

    # ==============================================================
    #  USERS + BUSINESS PROFILES
    # ==============================================================
    def _create_users_and_businesses(self):
        now = timezone.now()
        countries = list(Country.objects.all())
        services = list(Service.objects.all())
        certs = list(Certification.objects.all())

        businesses_data = [
            {
                "email": "john.smith@acmecorp.com",
                "full_name": "John Smith",
                "business_name": "Acme International Corp",
                "phone": "+441234567890",
                "address": "123 Oxford Street, London",
                "website": "https://acmecorp.com",
                "about": "Leading import/export company specializing in consumer electronics and industrial equipment across Europe and Asia.",
                "days_ago": 1,
                "views": 245,
                "locked": False,
            },
            {
                "email": "maria.garcia@globaltraders.com",
                "full_name": "Maria Garcia",
                "business_name": "Global Traders LLC",
                "phone": "+12125551234",
                "address": "456 5th Avenue, New York, NY",
                "website": "https://globaltraders.com",
                "about": "Full-service trade facilitation company with a network spanning 40+ countries.",
                "days_ago": 1,
                "views": 189,
                "locked": False,
            },
            {
                "email": "akira.tanaka@nipponexport.jp",
                "full_name": "Akira Tanaka",
                "business_name": "Nippon Export Co.",
                "phone": "+81312345678",
                "address": "7-1 Marunouchi, Chiyoda, Tokyo",
                "website": "https://nipponexport.jp",
                "about": "Japanese export specialist in automotive parts and precision machinery.",
                "days_ago": 2,
                "views": 312,
                "locked": False,
            },
            {
                "email": "sarah.jones@eurologistics.de",
                "full_name": "Sarah Jones",
                "business_name": "Euro Logistics GmbH",
                "phone": "+493012345678",
                "address": "Friedrichstraße 100, Berlin",
                "website": "https://eurologistics.de",
                "about": "Premium freight forwarding and warehousing solutions across the European Union.",
                "days_ago": 2,
                "views": 156,
                "locked": False,
            },
            {
                "email": "rajesh.kumar@bharattrade.in",
                "full_name": "Rajesh Kumar",
                "business_name": "Bharat Trade Solutions",
                "phone": "+919876543210",
                "address": "42 MG Road, Bangalore",
                "website": "https://bharattrade.in",
                "about": "India's trusted partner for textile and spice exports with sustainable sourcing practices.",
                "days_ago": 3,
                "views": 423,
                "locked": False,
            },
            {
                "email": "emily.chen@pacificrim.sg",
                "full_name": "Emily Chen",
                "business_name": "Pacific Rim Trading",
                "phone": "+6562345678",
                "address": "1 Raffles Place, Singapore",
                "website": "https://pacificrim.sg",
                "about": "Southeast Asian commodity trading house specializing in palm oil and rubber.",
                "days_ago": 3,
                "views": 201,
                "locked": False,
            },
            {
                "email": "ahmed.hassan@dubaicommerce.ae",
                "full_name": "Ahmed Hassan",
                "business_name": "Dubai Commerce Group",
                "phone": "+97142345678",
                "address": "DIFC, Sheikh Zayed Road, Dubai",
                "website": "https://dubaicommerce.ae",
                "about": "Middle East's premier trade finance and re-export hub connecting Africa, Asia and Europe.",
                "days_ago": 4,
                "views": 178,
                "locked": False,
            },
            {
                "email": "lucas.silva@brasilexport.br",
                "full_name": "Lucas Silva",
                "business_name": "Brasil Export Partners",
                "phone": "+5511987654321",
                "address": "Av. Paulista 1000, São Paulo",
                "website": "https://brasilexport.br",
                "about": "Brazilian agri-export company specializing in coffee, soybeans, and tropical fruits.",
                "days_ago": 4,
                "views": 134,
                "locked": False,
            },
            {
                "email": "anna.muller@nordicfreight.se",
                "full_name": "Anna Müller",
                "business_name": "Nordic Freight Solutions",
                "phone": "+46812345678",
                "address": "Kungsgatan 44, Stockholm",
                "website": "https://nordicfreight.se",
                "about": "Scandinavian logistics provider specializing in cold-chain and pharmaceutical transport.",
                "days_ago": 5,
                "views": 98,
                "locked": False,
            },
            {
                "email": "david.okonkwo@africonnect.za",
                "full_name": "David Okonkwo",
                "business_name": "AfriConnect Trade",
                "phone": "+27211234567",
                "address": "V&A Waterfront, Cape Town",
                "website": "https://africonnect.za",
                "about": "Pan-African trade platform connecting manufacturers with international buyers.",
                "days_ago": 5,
                "views": 87,
                "locked": True,
            },
            {
                "email": "sophie.martin@parisimport.fr",
                "full_name": "Sophie Martin",
                "business_name": "Paris Import House",
                "phone": "+33145678901",
                "address": "25 Rue du Faubourg, Paris",
                "website": "https://parisimport.fr",
                "about": "Luxury goods import specialists — wine, fashion, and artisanal products.",
                "days_ago": 5,
                "views": 267,
                "locked": False,
            },
            {
                "email": "mohammad.rahman@dhakatrade.bd",
                "full_name": "Mohammad Rahman",
                "business_name": "Dhaka Trade Hub",
                "phone": "+8801712345678",
                "address": "Gulshan 2, Dhaka",
                "website": "https://dhakatrade.bd",
                "about": "Bangladesh's garment export leader connecting RMG factories with global fashion brands.",
                "days_ago": 6,
                "views": 345,
                "locked": False,
            },
            {
                "email": "james.wilson@canadalog.ca",
                "full_name": "James Wilson",
                "business_name": "Canada Logistics Inc.",
                "phone": "+16041234567",
                "address": "200 Burrard St, Vancouver, BC",
                "website": "https://canadalog.ca",
                "about": "Cross-border logistics between Canada and the US, specializing in timber and mineral exports.",
                "days_ago": 6,
                "views": 112,
                "locked": True,
            },
            {
                "email": "mei.wong@shenzhentech.cn",
                "full_name": "Mei Wong",
                "business_name": "Shenzhen Tech Exports",
                "phone": "+8613812345678",
                "address": "Nanshan District, Shenzhen",
                "website": "https://shenzhentech.cn",
                "about": "Electronics and IoT device manufacturer and exporter serving B2B markets worldwide.",
                "days_ago": 7,
                "views": 534,
                "locked": False,
            },
            {
                "email": "peter.vdberg@hollandport.nl",
                "full_name": "Peter van den Berg",
                "business_name": "Holland Port Services",
                "phone": "+31102345678",
                "address": "Wilhelminakade 1, Rotterdam",
                "website": "https://hollandport.nl",
                "about": "Port logistics, customs brokerage and container shipping from Europe's largest port.",
                "days_ago": 8,
                "views": 198,
                "locked": False,
            },
            {
                "email": "olivia.brown@aussieminerals.au",
                "full_name": "Olivia Brown",
                "business_name": "Aussie Minerals Ltd",
                "phone": "+61298765432",
                "address": "100 George St, Sydney",
                "website": "https://aussieminerals.au",
                "about": "Australian mining and mineral export company with operations across Queensland and Western Australia.",
                "days_ago": 10,
                "views": 223,
                "locked": False,
            },
            {
                "email": "carlos.mendez@meximport.mx",
                "full_name": "Carlos Mendez",
                "business_name": "MexImport SA",
                "phone": "+525551234567",
                "address": "Paseo de la Reforma 505, CDMX",
                "website": "https://meximport.mx",
                "about": "Mexican import/export firm specializing in automotive parts and agricultural products.",
                "days_ago": 12,
                "views": 76,
                "locked": True,
            },
            {
                "email": "fatima.ali@gulfspice.om",
                "full_name": "Fatima Ali",
                "business_name": "Gulf Spice Trading",
                "phone": "+96824123456",
                "address": "Muscat, Oman",
                "website": "https://gulfspice.om",
                "about": "Omani spice and frankincense trading house with centuries of heritage.",
                "days_ago": 14,
                "views": 145,
                "locked": False,
            },
        ]

        # Also create some non-business users
        regular_users_data = [
            {"email": "buyer1@example.com", "full_name": "Alex Thompson", "days_ago": 1},
            {"email": "buyer2@example.com", "full_name": "Lisa Park", "days_ago": 2},
            {"email": "buyer3@example.com", "full_name": "Omar Farooq", "days_ago": 3},
            {"email": "buyer4@example.com", "full_name": "Nina Petrov", "days_ago": 4},
            {"email": "buyer5@example.com", "full_name": "Tom Richards", "days_ago": 5},
            {"email": "researcher@example.com", "full_name": "Dr. Hannah Lee", "days_ago": 6},
            {"email": "analyst@example.com", "full_name": "Mark Johnson", "days_ago": 7},
        ]

        contact_roles = ['ceo', 'managing_director', 'operations_manager',
                         'sales_manager', 'business_development_manager']

        biz_created = 0
        user_created = 0

        # --- Create business users + profiles ---
        for data in businesses_data:
            if User.objects.filter(email=data["email"]).exists():
                continue

            created_at = now - timedelta(days=data["days_ago"], hours=random.randint(0, 12))

            # Create user
            user = User(
                email=data["email"],
                full_name=data["full_name"],
                phone_number=data.get("phone", ""),
                is_business=True,
                is_staff=False,
                is_superuser=False,
            )
            user.set_password("demo1234!")
            user.save()

            # Backdate created_at
            User.objects.filter(pk=user.pk).update(
                created_at=created_at,
                last_login=now - timedelta(hours=random.randint(1, 72)),
            )

            # Pick a random country
            country = random.choice(countries) if countries else None

            # Create business profile
            bp = BusinessProfile(
                user=user,
                business_name=data["business_name"],
                phone_number=data.get("phone", ""),
                country=country,
                full_address=data["address"],
                website=data.get("website"),
                about_business=data["about"],
                is_locked=data["locked"],
                profile_views=data["views"],
            )
            bp.save()

            # Backdate
            BusinessProfile.objects.filter(pk=bp.pk).update(created_at=created_at)

            # Assign random services (2-5)
            bp.service.set(random.sample(services, min(random.randint(2, 5), len(services))))

            # Assign random certifications (1-3)
            bp.certifications.set(random.sample(certs, min(random.randint(1, 3), len(certs))))

            # Create a contact person
            ContactPerson.objects.create(
                business_profile=bp,
                full_name=data["full_name"],
                email=data["email"],
                phone_number=data.get("phone", ""),
                role=random.choice(contact_roles),
                is_primary=True,
            )

            # 50% chance of a branch location
            if random.random() > 0.5:
                BranchLocation.objects.create(
                    business_profile=bp,
                    full_name=f"{data['business_name']} - Branch",
                    address=f"Branch office at {data['address']}",
                    city=data["address"].split(",")[-1].strip(),
                    country=country,
                    phone_number=data.get("phone", ""),
                )

            biz_created += 1

        # --- Create regular (non-business) users ---
        for data in regular_users_data:
            if User.objects.filter(email=data["email"]).exists():
                continue

            created_at = now - timedelta(days=data["days_ago"], hours=random.randint(0, 8))

            user = User(
                email=data["email"],
                full_name=data["full_name"],
                is_business=False,
                is_staff=False,
                is_superuser=False,
            )
            user.set_password("demo1234!")
            user.save()

            User.objects.filter(pk=user.pk).update(
                created_at=created_at,
                last_login=now - timedelta(hours=random.randint(1, 48)),
            )

            user_created += 1

        self.stdout.write(f"   Businesses: {biz_created} created")
        self.stdout.write(f"   Users:      {user_created} regular users created")

    # ==============================================================
    #  SUMMARY
    # ==============================================================
    def _print_summary(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("--- Database Summary ---"))
        self.stdout.write(f"   Users:           {User.objects.count()}")
        self.stdout.write(f"   Business Users:  {User.objects.filter(is_business=True).count()}")
        self.stdout.write(f"   Businesses:      {BusinessProfile.objects.count()}")
        self.stdout.write(f"   Countries:       {Country.objects.count()}")
        self.stdout.write(f"   Services:        {Service.objects.count()}")
        self.stdout.write(f"   Certifications:  {Certification.objects.count()}")
        self.stdout.write(f"   Active:          {BusinessProfile.objects.filter(is_locked=False).count()}")
        self.stdout.write(f"   Locked:          {BusinessProfile.objects.filter(is_locked=True).count()}")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo login: any seeded email / demo1234!"))
        self.stdout.write(self.style.SUCCESS("Visit: http://localhost:8000/admin/"))
