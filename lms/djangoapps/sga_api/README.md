App has endpoints fo create user and bulk enroll users.

Configuration instructions: Code need next additional settings:

Add to lms.auth.json 'EDX_API_KEY'. It's key for check valid token.
The following token should be available in the python code:
'HTTP_X_EDX_API_KEY,

X-Edx-Api-Key HTTP header is present in the request


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
  -F country=Brazil \
  -F language=en \
  -F phone=53453453453453


 2. bulk enroll users

 curl -X POST \
  http://localhost:9000/api/user/bulkenrollment \
  -H 'Cache-Control: no-cache' \
  -H 'Content-Type: application/json' \
  -H 'Postman-Token: 46eb6561-76d8-4fea-8036-3a037e9bdac3' \
  -H 'X-Edx-Api-Key: PUT_YOUR_API_KEY_HERE' \
  -d '{
	"users": [
	         "sga_test18",
	         "sga_test10@raccoongang.com",
	         "sga_test3@raccoongang.com",
	         "sga_test20_errr@raccoongang.com"
	],
	"courses":[
		"course-v1:test+test_1+2014_1",
		"course-v1:test+test_1+2014_5"
	],
	"action": "enroll",
	"email_students": false,
	"auto_enroll": false
}'
