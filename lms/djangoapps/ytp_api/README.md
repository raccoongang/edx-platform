The application has endpoint for user creating.

Configuration instructions: feature needs next settings:

1) 'EDX_API_KEY' - It is a token for checking authorized api calls. lms.auth.json must contain this token.
                The following token should be available in the python code: 'HTTP_X_EDX_API_KEY,
                    X-Edx-Api-Key HTTP header is present in the request

2) FEATURES['SKIP_EMAIL_VALIDATION'] = True

Testing instructions:

 1. create user
 curl -X POST \
  http://localhost:9000/api/user/create \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -H 'X-Edx-Api-Key: PUT_YOUR_API_KEY_HERE' \
  -H 'content-type: multipart/form-data;
  -F email=sga_test191@raccoongang.com \
  -F username=sga_test191 \
  -F first_name=sga191 \
  -F last_name=test191 \
  -F gender=m


  Gender param can contain: 'm'(male), 'f'(female), 'o'(other, default value)