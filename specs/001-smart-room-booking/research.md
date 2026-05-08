# Research: Smart Room Booking

**Date**: 2026-05-08
**Spec**: specs/001-smart-room-booking/spec.md

## Decision 1: SQLite with aiosqlite for MVP Database

**Choice**: SQLite + aiosqlite + SQLAlchemy async
**Rationale**: Constitution mandates SQLite for MVP. aiosqlite provides async support compatible with FastAPI's async request handling. SQLAlchemy provides the abstraction layer for future PostgreSQL migration.
**Alternatives Rejected**:
- PostgreSQL: Violates Constitution Principle II (MVP uses SQLite)
- Raw SQL: Lacks migration path; SQLAlchemy provides ORM with easy driver swap

## Decision 2: Manual Check-in Button

**Choice**: Manual "I'm here" button in the UI
**Rationale**: Simplest implementation for MVP. User clicks a button when they arrive at the room.
**Alternatives Rejected**:
- IoT sensor / motion detection: Violates Constitution Principle VII (YAGNI)
- QR code scan: Requires mobile app; out of scope
- NFC tap: Requires hardware; out of scope

## Decision 3: Synchronous Conflict Detection at Booking Time

**Choice**: Synchronous SQL query checking for overlapping bookings at creation time
**Rationale**: 200 bookings/day ≈ 0.003 TPS. A simple SELECT with WHERE clause on (room_id, start_time, end_time) is more than sufficient. No concurrency issues at this scale.
**Alternatives Rejected**:
- Queue-based async check: Violates Constitution Principle VII (YAGNI for 200/day)
- Distributed locking: Overkill for single-instance SQLite
- Optimistic locking with retry: Unnecessary complexity

## Decision 4: Cron-based Auto-Release Scheduler

**Choice**: Background task using FastAPI's lifespan event, checking every 60 seconds for no-show bookings past the 15-minute grace period.
**Rationale**: Simple, reliable, and stays within the single-process architecture. Uses asyncio.create_task within FastAPI.
**Alternatives Rejected**:
- External cron job: Adds operational complexity
- Event-driven with message queue: Violates Constitution Principle VII (YAGNI)
- Celery worker: Overkill for a single periodic check

## Decision 5: Docker Multi-Stage Build

**Choice**: Two-stage Dockerfile: Node.js for frontend build, Python slim for production
**Rationale**: Constitution Principle VIII mandates Docker + Azure Container Apps. Multi-stage build keeps image < 300MB by excluding build tools from final image.
**Alternatives Rejected**:
- VM deployment: Violates Constitution Principle VIII
- Single-stage build: Produces oversized image with unnecessary build dependencies

## Decision 6: Health Endpoint for Azure Container Apps

**Choice**: GET /api/v1/health returns {"status": "ok", "version": "1.0.0"}
**Rationale**: Azure Container Apps requires a health probe endpoint. Liveness, readiness, and startup probes all point to this endpoint.
**Alternatives Rejected**:
- TCP probe only: Less informative, can't check app-level health
- No health endpoint: Azure Container Apps deployment would fail
