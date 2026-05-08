# Tasks: Smart Room Booking

**Input**: Design documents from `/specs/001-smart-room-booking/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup

- [x] T001 Create backend project structure per plan in backend/
- [x] T002 Create frontend project structure per plan in frontend/
- [ ] T003 [P] Configure backend lint (ruff) in backend/pyproject.toml
- [ ] T004 [P] Configure frontend lint (eslint) in frontend/eslint.config.js

## Phase 2: Foundational

- [ ] T005 Implement app config with pydantic-settings in backend/app/core/config.py
- [ ] T006 Implement async SQLite database engine in backend/app/core/db.py
- [ ] T007 Implement User model in backend/app/models/user.py
- [ ] T008 Implement Room model in backend/app/models/room.py
- [ ] T009 Implement Booking and CheckIn models in backend/app/models/booking.py
- [ ] T010 Implement auth schemas in backend/app/schemas/auth.py
- [ ] T011 [P] Implement room schemas in backend/app/schemas/room.py
- [ ] T012 [P] Implement booking schemas in backend/app/schemas/booking.py
- [ ] T013 Implement JWT auth service in backend/app/services/auth_service.py
- [ ] T014 Implement RBAC middleware in backend/app/core/rbac.py
- [ ] T015 Implement health endpoint in backend/app/api/v1/health.py
- [ ] T016 Implement seed data script in backend/app/scripts/seed.py
- [ ] T017 Implement FastAPI app with lifespan in backend/app/main.py

**Checkpoint**: Backend starts, /health returns 200, login returns JWT

## Phase 3: US1 — Room Search and Booking (P1) MVP

- [ ] T018 [US1] Implement room service in backend/app/services/room_service.py
- [ ] T019 [US1] Implement booking service in backend/app/services/booking_service.py
- [ ] T020 [US1] Implement auth endpoints in backend/app/api/v1/auth.py
- [ ] T021 [US1] Implement room endpoints in backend/app/api/v1/rooms.py
- [ ] T022 [US1] Implement booking endpoints in backend/app/api/v1/bookings.py
- [ ] T023 [US1] Implement API v1 router in backend/app/api/v1/router.py

## Phase 4: US2 — Check-in and Auto-Release (P1)

- [ ] T024 [US2] Implement check-in logic in booking_service.py
- [ ] T025 [US2] Implement auto-release scheduler in booking_service.py
- [ ] T026 [US2] Add check-in endpoint in bookings.py

## Phase 5: US3 — Recurring Bookings (P2)

- [ ] T027 [US3] Implement recurring booking creation in booking_service.py

## Phase 6: US4 — Admin & Analytics (P2)

- [ ] T028 [US4] Implement admin endpoints in backend/app/api/v1/admin.py
- [ ] T029 [US4] Implement utilization query service in room_service.py

## Phase 7: Frontend

- [ ] T030 [P] Create React + Vite + TypeScript project setup
- [ ] T031 [P] Implement i18n setup with zh/en translations
- [ ] T032 Implement API service client
- [ ] T033 Implement login page
- [ ] T034 Implement layout with nav
- [ ] T035 Implement room search page
- [ ] T036 Implement booking form component
- [ ] T037 Implement my bookings page
- [ ] T038 Implement admin dashboard page
- [ ] T039 Implement App with routing

## Phase 8: Testing

- [ ] T040 Implement test conftest with fixtures
- [ ] T041 [P] Implement auth tests
- [ ] T042 [P] Implement room tests
- [ ] T043 [P] Implement booking tests
- [ ] T044 Implement conflict detection tests
- [ ] T045 Implement RBAC tests
- [ ] T046 Implement E2E booking flow test

## Phase 9: DevOps & Deployment

- [ ] T047 Create Dockerfile
- [ ] T048 Create docker-compose.yml
- [ ] T049 Create .dockerignore
- [ ] T050 Create nginx.conf
- [ ] T051 Create GitHub Actions CI workflow
- [ ] T052 Create GitHub Actions Deploy workflow
- [ ] T053 Create Azure setup script
- [ ] T054 Create production verification script
