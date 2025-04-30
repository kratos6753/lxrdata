from django.http import JsonResponse
from django.conf import settings
from fetcher.models import ClientAPICredentials

class APIAuthenticationMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response
  
  def __call__(self, request):
    # Skip authentication for excluded paths
    if request.path in settings.API_AUTH_EXCLUDED_PATHS:
      return self.get_response(request)
    api_key = request.headers.get('X-API-Key') or request.GET.get('api_key')
    api_secret = request.headers.get('X-API-Secret') or request.GET.get('api_secret')

    if not api_key or not api_secret:
      return JsonResponse(
        {'error': 'Missing API Credentials'},
        status=401
      )
    try:
      creds = ClientAPICredentials.objects.get(api_key=api_key, is_active=True)
      if creds.api_secret != api_secret:
        raise ClientAPICredentials.DoesNotExist
      request.client = creds.client
    except ClientAPICredentials.DoesNotExist:
      return JsonResponse(
        {'error': 'Invalid API credentials'},
        status=401
      )
    return self.get_response(request)