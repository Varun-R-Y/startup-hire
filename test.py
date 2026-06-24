from app.auth.jwt_handler import (
    create_access_token,
    verify_access_token
)

token = create_access_token({
    "sub": "varun@gmail.com",
    "user_id": 1,
    "role": "candidate"
})

print(token)

payload = verify_access_token(token)

print(payload)