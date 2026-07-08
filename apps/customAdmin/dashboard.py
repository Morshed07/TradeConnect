import json
from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from django.db.models import Sum, Count


def dashboard_callback(request, context):
    """
    Unfold dashboard callback.
    Gathers all data needed for the custom admin dashboard and
    injects it into the template context.
    """
    from django.contrib.auth import get_user_model
    from apps.business.models import BusinessProfile
    from apps.core.models import Service, Country

    User = get_user_model()
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    fourteen_days_ago = now - timedelta(days=14)
    twenty_four_hours_ago = now - timedelta(hours=24)

    # ================================================================
    #  METRIC CARDS
    # ================================================================
    total_businesses = BusinessProfile.objects.count()
    total_profile_views = (
        BusinessProfile.objects.aggregate(total=Sum('profile_views'))['total'] or 0
    )
    active_users_24h = User.objects.filter(
        last_login__gte=twenty_four_hours_ago
    ).count()
    new_this_week = BusinessProfile.objects.filter(
        created_at__gte=seven_days_ago
    ).count()
    locked_accounts = BusinessProfile.objects.filter(is_locked=True).count()
    total_users = User.objects.count()

    # Percentage changes (last 7 days vs previous 7 days)
    prev_new_businesses = BusinessProfile.objects.filter(
        created_at__gte=fourteen_days_ago,
        created_at__lt=seven_days_ago,
    ).count()
    businesses_change = _calc_change(new_this_week, prev_new_businesses)

    prev_active_users = User.objects.filter(
        last_login__gte=now - timedelta(hours=48),
        last_login__lt=twenty_four_hours_ago,
    ).count()
    users_change = _calc_change(active_users_24h, prev_active_users)

    # ================================================================
    #  ACTIVITY OVERVIEW CHART (7-day line chart)
    # ================================================================
    chart_labels = []
    chart_logins = []
    chart_new_businesses = []
    chart_views = []

    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        chart_labels.append(day.strftime("%b %d"))
        chart_logins.append(
            User.objects.filter(
                last_login__gte=start, last_login__lt=end
            ).count()
        )
        chart_new_businesses.append(
            BusinessProfile.objects.filter(
                created_at__gte=start, created_at__lt=end
            ).count()
        )
        day_views = (
            BusinessProfile.objects.filter(
                updated_at__gte=start, updated_at__lt=end
            ).aggregate(v=Sum('profile_views'))['v']
            or 0
        )
        chart_views.append(day_views)

    # ================================================================
    #  RECENT ACTIVITY FEED
    # ================================================================
    recent_biz_qs = (
        BusinessProfile.objects.select_related('user', 'country')
        .order_by('-created_at')[:5]
    )
    recent_user_qs = User.objects.order_by('-created_at')[:5]
    activity_feed = _build_activity_feed(recent_biz_qs, recent_user_qs, now)

    # ================================================================
    #  BUSINESS STATUS (donut chart)
    # ================================================================
    active_count = BusinessProfile.objects.filter(is_locked=False).count()
    locked_count = locked_accounts

    # ================================================================
    #  TOP SERVICES (horizontal bar chart)
    # ================================================================
    top_services = list(
        Service.objects.annotate(usage_count=Count('business_profiles'))
        .order_by('-usage_count')[:5]
        .values('title', 'usage_count')
    )

    # ================================================================
    #  TOP COUNTRIES / COUNTRY OVERVIEW
    # ================================================================
    top_countries = list(
        Country.objects.annotate(business_count=Count('business_profiles'))
        .filter(business_count__gt=0)
        .order_by('-business_count')[:5]
        .values('name', 'business_count')
    )

    total_country_businesses = sum(c['business_count'] for c in top_countries) or 1

    # ================================================================
    #  LATEST BUSINESSES TABLE
    # ================================================================
    latest_businesses = []
    for b in (
        BusinessProfile.objects.select_related('user', 'country')
        .order_by('-created_at')[:7]
    ):
        latest_businesses.append({
            'id': str(b.id)[:8].upper(),
            'business_name': b.business_name,
            'email': b.user.email,
            'country': b.country.name if b.country else 'N/A',
            'status': 'Locked' if b.is_locked else 'Active',
            'profile_views': b.profile_views,
            'created_at': b.created_at.strftime('%b %d, %Y'),
            'last_login': (
                b.user.last_login.strftime('%b %d, %Y %H:%M')
                if b.user.last_login
                else 'Never'
            ),
        })

    # ================================================================
    #  INJECT INTO CONTEXT
    # ================================================================
    context.update({
        # Metrics
        'total_businesses': total_businesses,
        'total_profile_views': f"{total_profile_views:,}",
        'active_users_24h': active_users_24h,
        'new_this_week': new_this_week,
        'locked_accounts': locked_accounts,
        'total_users': total_users,
        'businesses_change': businesses_change,
        'users_change': users_change,

        # Chart JSON (Activity Overview)
        'chart_labels_json': json.dumps(chart_labels),
        'chart_logins_json': json.dumps(chart_logins),
        'chart_businesses_json': json.dumps(chart_new_businesses),
        'chart_views_json': json.dumps(chart_views),

        # Business Status (Donut)
        'active_count': active_count,
        'locked_count': locked_count,
        'status_json': json.dumps([active_count, locked_count]),

        # Top Services (Bar)
        'top_services': top_services,
        'services_labels_json': json.dumps(
            [s['title'] or 'Unnamed' for s in top_services]
        ),
        'services_data_json': json.dumps(
            [s['usage_count'] for s in top_services]
        ),

        # Top Countries
        'top_countries': top_countries,
        'total_country_businesses': total_country_businesses,

        # Table
        'latest_businesses': latest_businesses,

        # Activity Feed
        'activity_feed': activity_feed,
    })

    return context


# ====================================================================
#  HELPER FUNCTIONS
# ====================================================================

def _calc_change(current, previous):
    """Calculate percentage change between two values."""
    if previous == 0:
        return {
            'value': 100.0 if current > 0 else 0.0,
            'is_positive': current > 0,
        }
    change = ((current - previous) / previous) * 100
    return {
        'value': round(abs(change), 1),
        'is_positive': change >= 0,
    }


from django.urls import reverse

def _build_activity_feed(businesses_qs, users_qs, now):
    """Build a merged, time-sorted activity feed."""
    feed = []

    for b in businesses_qs:
        feed.append({
            'type': 'business',
            'title': 'New business registered',
            'description': f"{b.business_name} was created",
            'time': b.created_at,
            'time_display': timesince(b.created_at, now) + ' ago',
            'icon': 'store',
            'url': reverse('admin:business_businessprofile_change', args=[b.pk]),
        })

    for u in users_qs:
        label = u.full_name or u.email
        feed.append({
            'type': 'user',
            'title': 'New user joined',
            'description': f"{label} registered",
            'time': u.created_at,
            'time_display': timesince(u.created_at, now) + ' ago',
            'icon': 'person_add',
            'url': reverse('admin:account_user_change', args=[u.pk]),
        })

    feed.sort(key=lambda x: x['time'], reverse=True)
    return feed[:8]
