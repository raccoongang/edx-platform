App has endpoints fo create user and enroll user. Also enable endpoint for enable and disable users


Configuration instructions:
Code need next additional settings:

Add to lms.auth.json 'EDX_API_KEY'. It's key for check valid token.
The following token should be available in the python code: 'HTTP_X_EDX_API_KEY,
X-Edx-Api-Key HTTP header is present in the request


Testing instructions:
endpoints:

'api/user/create' - body { Prename, surname, email, username} - Response {user_id}
curl -X POST
http://localhost:8000/api/user/create
-H 'Cache-Control: no-cache'
-H 'Content-Type: application/json'
-H 'X-Edx-Api-Key: PUT_YOUR_API_KEY_HERE'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F email=andrey.lykhoman12344566@raccoongang.com
-F username=andreylykhoman006
-F prename=Andrey
-F surname=Lykhoman

-'api/user/set/activate/status' - body {user_id, is_active} - Response {user_id, is_active}
curl -X POST
http://localhost:8000/api/user/set/activate/status
-H 'Cache-Control: no-cache'
-H 'X-Edx-Api-Key: PUT_YOUR_API_KEY_HERE'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F user_id=21
-F is_active=true

'/api/user/enrollment' - body {User_id, course_id, mode, is_active} - Response {enroll_id}
curl -X POST
http://localhost:8000/api/user/enrollment
-H 'Cache-Control: no-cache'
-H 'Content-Type: application/x-www-form-urlencoded'
-H 'X-Edx-Api-Key: PUT_YOUR_API_KEY_HERE'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F 'course_id=course-v1:edX+DemoX+Demo_Course'
-F user_id=21
-F is_active=false
-F mode=honor