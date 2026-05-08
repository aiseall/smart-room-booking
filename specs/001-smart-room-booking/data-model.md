# Data Model: Smart Room Booking

## Entity Relationship

```
users 1──* bookings *──1 rooms
                |
                1
                |
             check_ins
```

## Entities

### users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT (UUID) | PK | Unique identifier |
| username | TEXT | UNIQUE, NOT NULL | Login username |
| email | TEXT | UNIQUE, NOT NULL | Email address |
| name | TEXT | NOT NULL | Display name |
| password_hash | TEXT | NOT NULL | bcrypt hashed password |
| role | TEXT | NOT NULL, CHECK IN ('employee','team_admin','facility_admin') | RBAC role |
| department | TEXT | | Department name |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |

### rooms

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT (UUID) | PK | Unique identifier |
| name | TEXT | NOT NULL | Room display name (e.g. "A-301") |
| building | TEXT | NOT NULL, CHECK IN ('A','B','C') | Building identifier |
| floor | INTEGER | NOT NULL | Floor number |
| capacity | INTEGER | NOT NULL | Max occupancy |
| equipment | TEXT | | JSON array of equipment ["projector","whiteboard","video_conf"] |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether room is bookable |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |

### bookings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT (UUID) | PK | Unique identifier |
| room_id | TEXT (UUID) | FK rooms.id, NOT NULL | Booked room |
| user_id | TEXT (UUID) | FK users.id, NOT NULL | Booking owner |
| title | TEXT | NOT NULL | Meeting title |
| start_time | DATETIME | NOT NULL | Booking start |
| end_time | DATETIME | NOT NULL | Booking end |
| status | TEXT | NOT NULL, DEFAULT 'confirmed' | See status values below |
| recurrence_rule | TEXT | | RRULE string for recurring bookings |
| recurrence_group_id | TEXT (UUID) | | Groups recurring booking instances |
| created_at | DATETIME | NOT NULL, DEFAULT NOW | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW | Last update timestamp |

**bookings.status valid values**: `confirmed`, `checked_in`, `completed`, `cancelled`, `no_show`, `auto_released`

**Indexes**:
- `idx_booking_conflict` on (room_id, start_time, end_time) WHERE status NOT IN ('cancelled', 'auto_released') — for conflict detection
- `idx_booking_user` on (user_id, start_time) — for "my bookings" queries
- `idx_booking_status` on (status, start_time) — for auto-release scheduler

### check_ins

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | TEXT (UUID) | PK | Unique identifier |
| booking_id | TEXT (UUID) | FK bookings.id, UNIQUE, NOT NULL | Associated booking |
| checked_in_at | DATETIME | NOT NULL, DEFAULT NOW | Check-in timestamp |
