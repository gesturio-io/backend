# Notifications API Documentation

This API allows authenticated users to **view and update** their notification preferences.

---

## 1. Get User Notification Preferences

### Endpoint
```
GET /settings/notifications/
```

### Authorization
Requires authentication (e.g., JWT token in `Authorization` header)
```
send cookies.
```

### Response

**200 OK**
```json
{
  "email_notifications": true,
  "course_notifications": false,
  "progress_notifications": true
}
```

---

## 2. Update User Notification Preferences

### Endpoint
```
PUT /settings/notifications/
```

### Authorization
Requires authentication (same as above)
```
Send cookies.
```

### Request Body (JSON)

Any of the following fields (all optional, partial update allowed):
```json
{
  "email_notifications": false,
  "course_notifications": true,
  "progress_notifications": false
}
```

### Response

**200 OK**
```json
{
  "email_notifications": false,
  "course_notifications": true,
  "progress_notifications": false
}
```

**400 Bad Request**
```json
{
  "email_notifications": ["Must be a valid boolean."]
}
```

---

## Notes for Frontend

- ✅ Always send the token with the request.
- ✅ Use `GET` to fetch current settings and pre-fill toggle switches.
- ✅ Use `PUT` to submit changes from toggles or checkboxes.
- ⚠️ Request body can be partial; no need to send all fields but   preferably send all


# Password Change API Documentation

This endpoint allows users to **request an OTP to change their password** and then **submit the OTP along with a new password** to update it.

---

## 1. Request OTP to Change Password

### Endpoint
```
POST localhost:8000/settings/password/
```

### Authorization
```
Send cookies with every request.
```

### Request Body (JSON)
```json
{
  "email": "user@example.com",
}
```

### Response

**200 OK**
```json
{
  "message": "OTP sent to your email for verification"
}
```

**400 Bad Request**
```json
{
  "email": ["Email does not match the authenticated user"]
}
```

---

## 2. Submit OTP and Change Password

### Endpoint
```
PUT localhost:8000/settings/password/
```

### Authorization
```
Send cookies.
```

### Request Body (JSON)
```json
{
  "otp": "123456",
  "new_password": "new_secure_password"
}
```
### Validation Rules
- `email` must match the authenticated user's email
- `new_password` and `confirm_password` must match
- `new_password` must be at least 5 characters
- Take care of matching and 5 character limit in the frontend only.
### Response

**200 OK**
```json
{
  "message": "Password changed successfully"
}
```

**400 Bad Request**
```json
{
  "error": "OTP and new password are required"
}
```
or
```json
{
  "error": "Invalid or expired OTP"
}
```

---

## Notes for Frontend

- Call the `POST` endpoint after the user fills out the password change form to **initiate the OTP process**.
- After receiving the OTP on email, prompt the user to enter it along with the new password and call the `PUT` endpoint.
- Do not cache or log OTPs client-side.


# Account Deletion API Documentation

This API allows authenticated users to **verify their password for account deletion** and subsequently **delete their account and associated data**.

---

## 1. Verify Password for Account Deletion

### Endpoint
```
GET localhost:8000/settings/accounts/delete/
```

### Authorization
```
Send cookies.
```

### Request Body (JSON)
```json
{
  "password": "password"
}
```

### Request Parameters

| Parameter | Type | Description |
|---|---|---|
| `password` | string | The user's current password for verification. |

### Response

**200 OK**
```json
{
  "message": "success"
}
```
**400 Bad Request**
```json
{
  "error": "Password is required to confirm account deletion"
}
```
**400 Bad Request**
```json
{
  "error": "Incorrect password"
}
```

- Before allowing the user to delete their account, prompt them to enter their password.
- Use the GET endpoint with the password as a query parameter to verify the password. If the verification is successful, proceed to the actual deletion.
- After successful password verification, if the user confirms, use the DELETE endpoint to initiate the account deletion process.

### Endpoint
```
DELETE localhost:8000/settings/accounts/delete/
```
### Authorization
```
Send cookies.
```
**200 OK**
```json
{
  "message": "Account deleted successfully"
}
```

# User Preferences and Privacy API Documentation

## Overview

These APIs allow authenticated users to view and update their user preferences and privacy settings. Both endpoints require authentication via JWT token in the Authorization header.

## Authentication

All endpoints require authentication using a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

The API also expects cookies to be sent with requests.

---

## 1. User Preferences API

### Get User Preferences

Retrieves the current user's preference settings.

**Endpoint:** `GET localhost:8000/settings/preferences/`

**Authorization:** Required (JWT token)

**Request Headers:**
```
Cookie: <session_cookies>
```

**Response:**

**Success Response (200 OK):**
```json
{
  "preferred_language": "en",
  "difficulty_level": "intermediate",
  "daily_goal": 30
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing authentication token
- `500 Internal Server Error` - Server error

---

### Update User Preferences  

Updates the current user's preference settings. Supports partial updates.

**Endpoint:** `PUT /preferences/`

**Authorization:** Required (JWT token)

**Request Headers:**
```
Cookie: <session_cookies>
```

**Request Body:**
```json
{
  "preferred_language": "es",
  "difficulty_level": "advanced", 
  "daily_goal": 45
}
```

**Note:** All fields are optional for partial updates. You can update individual fields without providing all values.

**Response:**

**Success Response (200 OK):**
```json
{
  "preferred_language": "es",
  "difficulty_level": "advanced",
  "daily_goal": 45
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data format or validation errors
  ```json
  {
    "field_name": ["Error message describing the validation issue"]
  }
  ```
- `401 Unauthorized` - Invalid or missing authentication token
- `500 Internal Server Error` - Server error

---

## 2. User Privacy API

### Get User Privacy Settings

Retrieves the current user's privacy settings.

**Endpoint:** `GET localhost:8000/settings/privacy/`

**Authorization:** Required (JWT token)

**Request Headers:**
```
Cookie: <session_cookies>
```

**Response:**

**Success Response (200 OK):**
```json
{
  "profile_visibility": "public",
  "show_progress": true
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing authentication token
- `500 Internal Server Error` - Server error

---

### Update User Privacy Settings

Updates the current user's privacy settings. Supports partial updates.

**Endpoint:** `PUT localhost:8000/settings/privacy/`

**Authorization:** Required (JWT token)

**Request Headers:**
```
Cookie: <session_cookies>
```

**Request Body:**
```json
{
  "profile_visibility": "private",
  "show_progress": false
}
```

**Note:** All fields are optional for partial updates. You can update individual fields without providing all values.

**Response:**

**Success Response (200 OK):**
```json
{
  "profile_visibility": "private",
  "show_progress": false
}
```

**Error Responses:**
- `400 Bad Request` - Invalid data format or validation errors
  ```json
  {
    "field_name": ["Error message describing the validation issue"]
  }
  ```
- `401 Unauthorized` - Invalid or missing authentication token
- `500 Internal Server Error` - Server error

---

