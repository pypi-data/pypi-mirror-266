from django_user_agents.utils import get_user_agent

def get_user_info(request):
    # Assuming you have a user model with an ID
    user_id = request.user.id if request.user.is_authenticated else 0
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    user_agent = get_user_agent(request)

    return {
        'user_id': user_id,
        'ip_address': ip_address,
        'device_type': 'PC' if user_agent.is_pc else 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'Unknown',
        'device_name': 'Unknown',  # Device name is generally not available from the user agent
        'operating_system': user_agent.os.family if user_agent.os else 'Unknown',
        'browser_name': user_agent.browser.family if user_agent.browser else 'Unknown',
        'browser_version': user_agent.browser.version_string if user_agent.browser else 'Unknown',        
    }