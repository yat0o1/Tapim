# Tap.im API

Backend API for Tap.im — a job platform connecting applicants and recruiters.

**Base URL:** `https://tapim.onrender.com`  
**Docs:** `https://tapim.onrender.com/docs`

---

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — database ORM (Core style)
- **PostgreSQL** — database
- **AuthX** — JWT authentication
- **Passlib + bcrypt** — password hashing
- **FastAPI-Mail** — email sending
- **Docker** — containerization

---

## Authentication

JWT token is returned on login and set as a cookie (`access_token`).  
Decode the token payload to get the current user's ID from the `sub` field.

```js
const payload = JSON.parse(atob(token.split('.')[1]));
const userId = parseInt(payload.sub);
```

---

## Endpoints

### AUTH `/auth`

---

#### `POST /auth/register/applicant`
Register a new applicant.

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| email | string | ✅ | Must be valid email with real domain |
| password | string | ✅ | 6–72 characters |
| confirm_password | string | ✅ | Must match password |
| first_name | string | ✅ | Max 100 chars |
| city | string | ✅ | Max 100 chars |

**Response `200`:**
```json
{
  "message": "Registered successfully, check your email for verification code",
  "user_id": 5
}
```

**Errors:**
- `400` — Email already registered
- `422` — Invalid email or password

---

#### `POST /auth/register/recruiter/step1`
Register a new recruiter (step 1 — personal info).

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| email | string | ✅ | Must be valid email with real domain |
| password | string | ✅ | 6–72 characters |
| confirm_password | string | ✅ | Must match password |
| first_name | string | ✅ | Max 100 chars |

**Response `200`:**
```json
{
  "message": "Step 1 complete, check your email",
  "user_id": 6
}
```

**Errors:**
- `400` — Email already registered
- `422` — Invalid email or password

---

#### `POST /auth/register/recruiter/step2`
Complete recruiter registration (step 2 — company info).

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | integer | ✅ | From step 1 response |
| company_name | string | ✅ | Max 255 chars |
| company_size | string | ✅ | `small`, `medium`, or `big` |
| company_site | string | ❌ | URL to company website |
| user_role_in_company | string | ✅ | Max 100 chars |

**Response `200`:**
```json
{
  "message": "Registration complete!"
}
```

---

#### `POST /auth/login`
Login and receive JWT token.

**Request body:**
| Field | Type | Required |
|-------|------|----------|
| email | string | ✅ |
| password | string | ✅ |

**Response `200`:**
```json
{
  "access_token": "eyJhbGci..."
}
```
Token is also set as `access_token` cookie.

**Errors:**
- `401` — Invalid email or password

---

#### `POST /auth/verify-email`
Verify email using the 6-digit code sent after registration.

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | integer | ✅ | From registration response |
| code | string | ✅ | Exactly 6 digits |

**Response `200`:**
```json
{
  "message": "Email verified successfully"
}
```

**Errors:**
- `400` — Invalid or expired code

---

#### `POST /auth/forgot-password`
Send a password reset code to email.

**Request body:**
| Field | Type | Required |
|-------|------|----------|
| email | string | ✅ |

**Response `200`:**
```json
{
  "message": "If this email exists, a code has been sent"
}
```

---

#### `POST /auth/reset-password`
Reset password using the code received by email.

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| user_id | integer | ✅ | |
| code | string | ✅ | Exactly 6 digits |
| new_password | string | ✅ | 6–72 characters |
| confirm_password | string | ✅ | Must match new_password |

**Response `200`:**
```json
{
  "message": "Password reset successfully"
}
```

**Errors:**
- `400` — Invalid or expired code

---

### PROFILES `/profiles`

---

#### `GET /profiles/{user_id}`
Get full profile of a user including skills, experience and education.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |

**Response `200`:**
```json
{
  "profile": {
    "id": 1,
    "user_id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "city": "Almaty",
    "phone": "+77001234567",
    "specialization": "Backend Developer",
    "level": "middle",
    "work_format": "remote",
    "bio": "Experienced developer...",
    "github_url": "https://github.com/johndoe",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "resume_url": null,
    "salary_min": 300000,
    "salary_max": 600000,
  },
  "skills": [
    {"id": 1, "name": "Python"},
    {"id": 2, "name": "React"}
  ],
  "experience": [
    {
      "id": 1,
      "user_id": 5,
      "position": "Backend Developer",
      "company_name": "Some Company",
      "start_date": "2022-01-01T00:00:00",
      "end_date": null,
      "description": "Worked on..."
    }
  ],
  "education": [
    {
      "id": 1,
      "user_id": 5,
      "specialization": "Computer Science",
      "university": "KBTU",
      "start_date": "2019-09-01T00:00:00",
      "end_date": "2023-06-01T00:00:00"
    }
  ]
}
```

**Errors:**
- `404` — Profile not found

---

#### `PUT /profiles/{user_id}`
Update main profile info. Only send fields you want to update — others stay unchanged.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |

**Request body (all optional):**
| Field | Type | Notes |
|-------|------|-------|
| first_name | string | |
| last_name | string | |
| specialization | string | e.g. "Backend Developer" |
| city | string | |
| work_format | string | `remote`, `hybrid`, or `fulltime` |
| level | string | `junior`, `middle`, or `senior` |

**Response `200`:**
```json
{
  "message": "Profile updated"
}
```

---

#### `PUT /profiles/{user_id}/contacts`
Update contact information. Only send fields you want to update.

**Request body (all optional):**
| Field | Type |
|-------|------|
| phone | string |
| github_url | string |
| linkedin_url | string |

**Response `200`:**
```json
{
  "message": "Contacts updated"
}
```

---

#### `PUT /profiles/{user_id}/bio`
Update bio/about section.

**Request body:**
| Field | Type | Required |
|-------|------|----------|
| bio | string | ✅ |

**Response `200`:**
```json
{
  "message": "Bio updated"
}
```

---

#### `GET /profiles/skills`
Get all available skills to display as selectable options.

**Response `200`:**
```json
[
  {"id": 1, "name": "React"},
  {"id": 2, "name": "TypeScript"},
  {"id": 3, "name": "Node.js"},
  {"id": 4, "name": "Python"}
]
```

---

#### `PUT /profiles/{user_id}/skills`
Replace user's skills. Sends a list of skill IDs (get IDs from `GET /profiles/skills`).

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| skill_ids | integer[] | ✅ | Replaces all previous skills |

**Example:**
```json
{
  "skill_ids": [1, 3, 4]
}
```

**Response `200`:**
```json
{
  "message": "Skills updated"
}
```

---

#### `POST /profiles/{user_id}/experience`
Add a work experience entry. Can be called multiple times to add multiple entries.

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| position | string | ✅ | Job title |
| company_name | string | ✅ | |
| start_date | datetime | ✅ | ISO format: `2022-01-01T00:00:00` |
| end_date | datetime | ❌ | null if currently working here |
| description | string | ❌ | |

**Response `200`:**
```json
{
  "message": "Experience added"
}
```

---

#### `DELETE /profiles/{user_id}/experience/{exp_id}`
Delete a work experience entry.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |
| exp_id | integer |

**Response `200`:**
```json
{
  "message": "Experience deleted"
}
```

---

#### `POST /profiles/{user_id}/education`
Add an education entry. Can be called multiple times to add multiple entries.

**Request body:**
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| specialization | string | ✅ | Field of study |
| university | string | ✅ | |
| start_date | datetime | ✅ | ISO format |
| end_date | datetime | ❌ | null if still studying |

**Response `200`:**
```json
{
  "message": "Education added"
}
```

---

#### `DELETE /profiles/{user_id}/education/{edu_id}`
Delete an education entry.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |
| edu_id | integer |

**Response `200`:**
```json
{
  "message": "Education deleted"
}
```

---

### VACANCIES `/vacancies`

---

#### `GET /vacancies/`
Get all vacancies.

**Response `200`:** Array of vacancy objects.

```json
[
  {
    "id": "uuid",
    "source_id": 123,
    "source_type": "hh",
    "company_name": "Google",
    "position_name": "Senior Backend Developer",
    "location": "Almaty",
    "specialization": "Backend",
    "salary_min": 500000,
    "salary_max": 800000,
    "salary_currency": "KZT",
    "salary_type": "monthly",
    "vacancy_description": "...",
    "tags": ["Python", "FastAPI"],
    "contact_name": "HR Manager",
    "contact_phone": "+77001234567",
    "contact_social": "...",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

---

#### `GET /vacancies/search`
Search vacancies by title and/or tags.

**Query params:**
| Param | Type | Required | Notes |
|-------|------|----------|-------|
| query | string | ❌ | Search in position name (case-insensitive) |
| tags | string[] | ❌ | Filter by tags, can pass multiple |

**Examples:**
```
GET /vacancies/search?query=backend
GET /vacancies/search?query=developer&tags=Python&tags=FastAPI
GET /vacancies/search?tags=React
```

**Response `200`:** Array of matching vacancy objects.

---

#### `GET /vacancies/salary`
Filter vacancies by salary range.

**Query params:**
| Param | Type | Required | Notes |
|-------|------|----------|-------|
| min_salary | integer | ❌ | Minimum salary_min |
| max_salary | integer | ❌ | Maximum salary_max |

**Example:**
```
GET /vacancies/salary?min_salary=300000&max_salary=1000000
```

**Response `200`:** Array of matching vacancy objects.

---

#### `GET /vacancies/this-week`
Get vacancies created in the last 7 days.

**Response `200`:** Array of vacancy objects.

---

#### `GET /vacancies/{vacancy_id}`
Get a single vacancy by ID.

**Path params:**
| Param | Type | Notes |
|-------|------|-------|
| vacancy_id | string (UUID) | |

**Response `200`:** Single vacancy object.

---

### CHAT `/chat`

---

#### `WebSocket /chat/ws/{user_id}`
Connect to real-time chat. Each user connects with their own user ID.

**Connection:**
```js
const ws = new WebSocket(`wss://tapim.onrender.com/chat/ws/${myUserId}`);
```

**Send message:**
```json
{
  "receiver_id": 3,
  "content": "Hello!"
}
```

**Receive message:**
```json
{
  "sender_id": 5,
  "content": "Hello!"
}
```

**Error response (if receiver doesn't exist):**
```json
{
  "error": "Failed to save message, receiver may not exist"
}
```

**Offline response (receiver not connected):**
```json
{
  "info": "Message saved, receiver is offline"
}
```

---

#### `GET /chat/history/{user_id}/{other_user_id}`
Get chat history between two users, ordered oldest to newest.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |
| other_user_id | integer |

**Response `200`:**
```json
[
  {
    "id": 1,
    "sender_id": 5,
    "receiver_id": 3,
    "content": "Hello!",
    "created_at": "2024-01-01T10:00:00",
    "is_read": true
  }
]
```

---

#### `PUT /chat/read/{sender_id}/{receiver_id}`
Mark all messages from a sender as read. Call this when user opens a conversation.

**Path params:**
| Param | Type | Notes |
|-------|------|-------|
| sender_id | integer | The person who sent the messages |
| receiver_id | integer | The current user (who is reading) |

**Response `200`:**
```json
{
  "message": "Messages marked as read"
}
```

---

#### `GET /chat/unread/{user_id}`
Get count of unread messages for a user. Use for notification badges.

**Path params:**
| Param | Type |
|-------|------|
| user_id | integer |

**Response `200`:**
```json
{
  "unread_count": 3
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (e.g. email already registered, invalid code) |
| 401 | Unauthorized (wrong email/password) |
| 403 | Forbidden (wrong admin key) |
| 404 | Not found |
| 422 | Validation error (wrong data format) |
| 500 | Server error |

---

## Registration Flow

### Applicant
```
POST /auth/register/applicant → get user_id
POST /auth/verify-email → verify with code from email
POST /auth/login → get token
PUT /profiles/{user_id} → fill profile
```

### Recruiter
```
POST /auth/register/recruiter/step1 → get user_id
POST /auth/register/recruiter/step2 → add company info
POST /auth/verify-email → verify with code from email
POST /auth/login → get token
```

### Password Reset
```
POST /auth/forgot-password → send code to email
POST /auth/reset-password → set new password with code
```

#### `GET /profiles/`
Get all profiles sorted by completeness (most filled first).

**Response `200`:**
```json
[
  {
    "user_id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "specialization": "Backend Developer",
    "city": "Almaty",
    "level": "middle",
    "salary_min": 300000,
    "salary_max": 600000,
    "skills": ["Python", "FastAPI", "PostgreSQL"]
  }
]
```

#### `GET /profiles/`
Get all profiles sorted by completeness (most filled first).

**Response `200`:**
```json
[
  {
    "user_id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "specialization": "Backend Developer",
    "city": "Almaty",
    "level": "middle",
    "salary_min": 300000,
    "salary_max": 600000,
    "skills": ["Python", "FastAPI", "PostgreSQL"]
  }
]
```