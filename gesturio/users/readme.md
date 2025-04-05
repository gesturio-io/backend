# Authentication APIs - README

This APIs provide user authentication and profile management features including registration, login, logout, email verification, and profile updates. JWT-based authentication is used to maintain session state.

## Endpoints

### 1. `GET /`
**Description**: Basic test endpoint. Returns a welcome message.

### 2. `GET /cache_test`
**Description**: (Test Endpoint) Stores and retrieves a test cache key-value pair.
**Returns**: `{"message": "Hello, World!"}`

### 3. `GET /get_ip_address`
**Description**: (Test endpoint) Returns the IP address associated with the request.

---

### 4. `POST /register`
**Description**: Register a new user.
**Request Body**:
```json
{
  "username": "exampleuser",
  "email": "user@example.com",
  "password": "strongpassword"
}
```
**Success Response**: `201 Created`
```json
{
  "status": "success",
  "message": "User registered successfully"
}
```

---

### 5. `POST /login`
**Description**: Log in using username or email and password(should be at least 5 char long)
**Request Body**:
```json
{
  "username": "exampleuser",  // or email
  "password": "strongpassword"
}
```
**Success Response**:
- JWT and Refresh Token are set in cookies.
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "exampleuser",
  "login_type": "email"
}
```

---

### 6. `GET /login`
**Auth Required**: Yes (JWT in cookies)
**Description**: Get basic user info.
**Success Response**:
```json
{
  "id": 1,
  "username": "exampleuser",
  "email": "user@example.com",
  "login_type": "email"
}
```

---

### 7. `POST /logout`
**Auth Required**: Yes
**Description**: Logs out the user and deletes cookies.
**Success Response**:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### 8. `GET /profile`
**Auth Required**: Yes
**Description**: Retrieves the current user profile.
**Success Response**:
```json
{
  "firstname": "John",
  "lastname": "Doe",
  "profile_picture": "https://example.com/pic.jpg",
  "bio": "Loves tech",
  "country": "India",
  "native_language": "Hindi",
  "gender": "Male",
  "date_of_birth": "2000-01-01",
  "phone_number": "9876543210",
  "daily_goal": 10,
  "requirement": "casual"
}
```

---

### 9. `POST /profile`
**Auth Required**: Yes
**Description**: Updates the user's profile.
**Request Body**:
```json
{
  "firstname": "John",
  "lastname": "Doe",
  "profile_picture": "https://example.com/pic.jpg",
  "bio": "Loves tech",
  "country": "India",
  "native_language": "Hindi",
  "gender": "Male",
  "date_of_birth": "2000-01-01",
  "phone_number": "9876543210",
  "requirement": "casual",
  "daily_goal": 10
}
```
**Success Response**:
```json
{
  "status": "success",
  "message": "Profile updated successfully"
}
```

---

### 10. `POST /email/request`
**Description**: Sends an OTP to user's email for verification.
**Request Body**:
```json
{
  "email": "user@example.com"
}
```
**Success Response**:
```json
{
  "status": "success",
  "message": "OTP sent successfully"
}
```

---

### 11. `POST /email/verify`
**Description**: Verifies email with OTP.
**Request Body**:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```
**Success Response**:
```json
{
  "status": "success",
  "message": "Email verified successfully"
}
```

---

## Notes:
- JWTs are stored in cookies for authentication.
- OTPs are stored in Django cache and expire after a configured TTL.
- Profile completeness is enforced during login.

---

### Requirements for Frontend:
- Validate required profile fields before calling `/profile` POST.
- Handle OTP expiry and error messages cleanly.
- Ensure secure cookie handling for JWT.

---

### Environment Variables Required:
- `OTP_TTL`: Time for OTP expiration.
- SMTP credentials if using `send_email` utility.

---

### Developed by:
**Gesturio Team**

