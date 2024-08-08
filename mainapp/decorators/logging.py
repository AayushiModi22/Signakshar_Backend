# import time
# import json
# from functools import wraps
# from django.utils.timezone import now
# from django.http import HttpResponse
# from rest_framework.response import Response
# from django.http import JsonResponse
# from ..models import NewAPILog 

# def log_api_request(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         # Start timing
#         start_time = time.time()
#         user_id = None
#         if request.body:
#             try:
#                 data = json.loads(request.body.decode('utf-8', errors='replace') if request.body else None)
#                 user_id = data.get('user_id')
#             except (json.JSONDecodeError, KeyError):
#                 pass
        
#         print("user_id from request body:", user_id)

#         log_entry = NewAPILog(
#             timestamp=now(),
#             # user_id=request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
#             user_id=user_id,
#             endpoint=request.path,
#             method=request.method,
#             request_headers=json.dumps(dict(request.headers)),
#             request_body=request.body.decode('utf-8', errors='replace') if request.body else None,
#             ip_address=request.META.get('REMOTE_ADDR', None),
#             user_agent=request.META.get('HTTP_USER_AGENT', None),
#         )
        
#         try:
#             # Call the actual view function
#             response = view_func(request, *args, **kwargs)

#             # Ensure the response is fully rendered before accessing its content
#             if hasattr(response, 'render') and callable(response.render):
#                 response.render()

#             # Calculate response time
#             end_time = time.time()
#             response_time = int((end_time - start_time) * 1000)  # Time in milliseconds

#             # Capture response details
#             log_entry.response_status_code = response.status_code
#             log_entry.response_body = response.content.decode('utf-8', errors='replace') if response.content else None
#             log_entry.response_time = response_time

#             return response

#         except Exception as e:
#             # Capture error details
#             log_entry.response_status_code = 500
#             log_entry.error_message = str(e)
#             log_entry.error_code = 'Exception'
#             response = JsonResponse({'success': False, 'error': str(e)}, status=500)  # Ensure a response is still returned

#             # Re-raise the exception after logging
#             raise

#         finally:
#             # Save log entry to the database
#             log_entry.save()

#     return _wrapped_view

# //////////////user id without aws
# import time
# import json
# from functools import wraps
# from django.utils.timezone import now
# from django.http import JsonResponse
# from rest_framework.response import Response
# from ..models import NewAPILog

# def log_api_request(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if request.method == 'GET':
#             return view_func(request, *args, **kwargs)

#         start_time = time.time()
#         user_id = None
#         log_entry = NewAPILog(
#             timestamp=now(),
#             user_id=None,
#             endpoint=request.path,
#             method=request.method,
#             request_headers=json.dumps(dict(request.headers)),
#             request_body=None,
#             ip_address=request.META.get('REMOTE_ADDR', None),
#             user_agent=request.META.get('HTTP_USER_AGENT', None),
#         )

#         # print("reeeee:",request.body)
#         print("request.POST:",request.POST.get('user_id'))
#         if request.body:
#             try:
#                 data = json.loads(request.body.decode('utf-8', errors='replace') if request.body else '{}')
#                 user_id = data.get('user_id')
#                 log_entry.user_id = user_id if user_id is not None else request.POST.get('user_id')
#                 log_entry.request_body = json.dumps(data)
#             except (json.JSONDecodeError, KeyError):
#                 pass


#         try:
#             # Call the actual view function
#             response = view_func(request, *args, **kwargs)

#             # Ensure the response is fully rendered before accessing its content
#             if hasattr(response, 'render') and callable(response.render):
#                 response.render()

#             # Calculate response time
#             end_time = time.time()
#             response_time = int((end_time - start_time) * 1000)  # Time in milliseconds

#             # Capture response details
#             log_entry.response_status_code = response.status_code
#             log_entry.response_body = response.content.decode('utf-8', errors='replace') if response.content else None
#             log_entry.response_time = response_time

#             return response

#         except Exception as e:
#             # Capture error details
#             log_entry.response_status_code = 500
#             log_entry.error_message = str(e)
#             log_entry.error_code = 'Exception'
#             response = JsonResponse({'success': False, 'error': str(e)}, status=500)  # Ensure a response is still returned

#             # Re-raise the exception after logging
#             raise

#         finally:
#             # Save log entry to the database
#             log_entry.save()

#     return _wrapped_view


#--------
import time
import json
from functools import wraps
from django.utils.timezone import now
from django.http import JsonResponse
from ..models import NewAPILog

def log_api_request(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'GET':
            return view_func(request, *args, **kwargs)

        start_time = time.time()
        user_id = None
        log_entry = NewAPILog(
            timestamp=now(),
            user_id=None,
            endpoint=request.path,
            method=request.method,
            request_headers=json.dumps(dict(request.headers)),
            request_body=None,
            ip_address=request.META.get('REMOTE_ADDR', None),
            user_agent=request.META.get('HTTP_USER_AGENT', None),
        )
        
        content_type = request.content_type
        if content_type == 'application/json':
            if request.body:
                try:
                    data = json.loads(request.body.decode('utf-8', errors='replace') if request.body else '{}')
                    user_id = data.get('user_id')
                    log_entry.user_id = user_id
                    log_entry.request_body = json.dumps(data)
                except (json.JSONDecodeError, KeyError):
                    pass
        elif content_type.startswith('multipart/form-data'):
            user_id = request.POST.get('user_id')
            log_entry.user_id = user_id

            request_body_data = request.POST.dict()
            request_body_data.pop('file', None)  # Exclude file data from request body log
            log_entry.request_body = json.dumps(request_body_data)

        print("content_type::::",request.body)
        try:
            # Call the actual view function
            response = view_func(request, *args, **kwargs)

            # Ensure the response is fully rendered before accessing its content
            if hasattr(response, 'render') and callable(response.render):
                response.render()

            # Calculate response time
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)  # Time in milliseconds

            # Capture response details
            log_entry.response_status_code = response.status_code
            log_entry.response_body = response.content.decode('utf-8', errors='replace') if response.content else None
            log_entry.response_time = response_time

            return response

        except Exception as e:
            # Capture error details
            log_entry.response_status_code = 500
            log_entry.error_message = str(e)
            log_entry.error_code = 'Exception'
            response = JsonResponse({'success': False, 'error': str(e)}, status=500)  # Ensure a response is still returned

            # Re-raise the exception after logging
            raise

        finally:
            # Save log entry to the database
            log_entry.save()

    return _wrapped_view
