App has endpoints fo create user and enroll user. Also enable endpoint for enable and disable users


Configuration instructions:
Code need next additional settings:

add to lms.auth.json 'EDX_APP_ETC_API_KEY'. It's key for check valid token.
The following token should be available in the python code: 'HTTP_X_APP_ETC_API_KEY'
In admin page for this sites add to site's setting: 'ENABLE_APP_ETC_API': true

Testing instructions:
endpoints:

'api/user/create' - body { Prename, surname, email, username} - Response {user_id}
curl -X POST
http://localhost:8000/api/user/create
-H 'Cache-Control: no-cache'
-H 'Content-Type: application/json'
-H 'Postman-Token: c4ceae4c-7470-4dbc-bf61-79057e3dae71'
-H 'X-APP-ETC-API-KEY: 12345'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F email=andrey.lykhoman12344566@raccoongang.com
-F username=andreylykhoman006
-F prename=Andrey
-F surname=Lykhoman

-'api/user/set/activate/status' - body {user_id, is_active} - Response {user_id, is_active}
curl -X POST
http://localhost:8000/api/user/set/activate/status
-H 'Cache-Control: no-cache'
-H 'Postman-Token: 0dac28e7-18a6-4b6c-9f74-fc53b90ebf7e'
-H 'X-APP-ETC-API-KEY: 12345'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F user_id=21
-F is_active=true

'/api/user/enrollment' - body {User_id, course_id, mode, is_active} - Response {enroll_id}
curl -X POST
http://localhost:8000/api/user/enrollment
-H 'Cache-Control: no-cache'
-H 'Content-Type: application/x-www-form-urlencoded'
-H 'Postman-Token: b86810e9-5644-416e-9331-8ea57e1679b7'
-H 'X-APP-ETC-API-KEY: 12345'
-H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'
-F 'course_id=course-v1:edX+DemoX+Demo_Course'
-F user_id=21
-F is_active=false
-F mode=honor