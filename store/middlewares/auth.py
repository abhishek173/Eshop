from django.shortcuts import redirect

from urllib.parse import quote

def auth_middleware(get_response):
    def middleware(request):
        customer_id = request.session.get('customer')
        return_url = request.build_absolute_uri(request.get_full_path())  # Get full URL

        print(f"Customer ID: {customer_id}")  # Debugging
        print(f"Requested URL: {return_url}")  # Debugging

        if not customer_id:
            return redirect(f'/login?return_url={quote(return_url)}')  # Encode URL properly

        response = get_response(request)
        return response

    return middleware
