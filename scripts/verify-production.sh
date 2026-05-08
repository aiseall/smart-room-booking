#!/bin/bash
# scripts/verify-production.sh
# 生产环境上线验证 / Production go-live verification

set -euo pipefail

BASE_URL="https://$1/api/v1"
PASS=0
FAIL=0

check() {
  local name="$1"
  local expected="$2"
  local actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  ✅ $name: PASS (got $actual)"
    ((PASS++))
  else
    echo "  ❌ $name: FAIL (expected $expected, got $actual)"
    ((FAIL++))
  fi
}

echo "=============================================="
echo "🔍 Smart Room Booking - 上线验证 / Go-Live Verification"
echo "   Target: $BASE_URL"
echo "=============================================="
echo ""

# ── Test 1: 健康检查 / Health Check ──
echo "1️⃣ 健康检查 / Health Check"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
check "GET /health" "200" "$HTTP_CODE"
echo ""

# ── Test 2: 登录 / Login ──
echo "2️⃣ 登录 / Login"
LOGIN_RESP=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}')
TOKEN=$(echo "$LOGIN_RESP" | jq -r '.access_token // .token // empty')
if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo "  ✅ Login: PASS (token received)"
  ((PASS++))
else
  echo "  ❌ Login: FAIL (no token)"
  ((FAIL++))
fi
echo ""

# ── Test 3: 搜索空闲会议室 / Search Available Rooms ──
echo "3️⃣ 搜索空闲会议室 / Search Available Rooms"
ROOMS=$(curl -s "$BASE_URL/rooms/available?\
start=2026-05-09T14:00:00&\
end=2026-05-09T15:00:00&\
min_capacity=6" \
  -H "Authorization: Bearer $TOKEN")
ROOM_COUNT=$(echo "$ROOMS" | jq 'length // 0')
if [ "$ROOM_COUNT" -gt 0 ]; then
  echo "  ✅ Search: PASS (found $ROOM_COUNT rooms)"
  ((PASS++))
else
  echo "  ❌ Search: FAIL (no rooms found)"
  ((FAIL++))
fi
ROOM_ID=$(echo "$ROOMS" | jq -r '.[0].id // empty')
echo ""

# ── Test 4: 创建预约 / Create Booking ──
echo "4️⃣ 创建预约 / Create Booking"
if [ -n "$ROOM_ID" ]; then
  BOOKING_CODE=$(curl -s -o /tmp/booking.json -w "%{http_code}" \
    -X POST "$BASE_URL/bookings" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"room_id\": \"$ROOM_ID\",
      \"start_time\": \"2026-05-09T14:00:00\",
      \"end_time\": \"2026-05-09T15:00:00\",
      \"title\": \"Production Verification Test\"
    }")
  check "POST /bookings" "201" "$BOOKING_CODE"
  BOOKING_ID=$(jq -r '.id // empty' /tmp/booking.json)
else
  echo "  ⚠️ SKIPPED (no room available)"
fi
echo ""

# ── Test 5: 冲突检测 / Conflict Detection ──
echo "5️⃣ 冲突检测 / Conflict Detection (CRITICAL)"
if [ -n "$ROOM_ID" ]; then
  CONFLICT_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$BASE_URL/bookings" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"room_id\": \"$ROOM_ID\",
      \"start_time\": \"2026-05-09T14:00:00\",
      \"end_time\": \"2026-05-09T15:00:00\",
      \"title\": \"This Should Fail\"
    }")
  check "POST /bookings (duplicate)" "409" "$CONFLICT_CODE"
else
  echo "  ⚠️ SKIPPED"
fi
echo ""

# ── Test 6: 取消预约 / Cancel Booking ──
echo "6️⃣ 取消预约 / Cancel Booking"
if [ -n "${BOOKING_ID:-}" ]; then
  CANCEL_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X DELETE "$BASE_URL/bookings/$BOOKING_ID" \
    -H "Authorization: Bearer $TOKEN")
  check "DELETE /bookings/{id}" "200" "$CANCEL_CODE"
else
  echo "  ⚠️ SKIPPED"
fi
echo ""

# ── Test 7: 权限测试 / RBAC Test ──
echo "7️⃣ 权限测试 / RBAC Test"
ADMIN_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "$BASE_URL/admin/utilization" \
  -H "Authorization: Bearer $TOKEN")
check "GET /admin/* as non-admin" "403" "$ADMIN_CODE"
echo ""

# ── 结果汇总 / Summary ──
echo "=============================================="
echo "📊 验证结果 / Verification Results"
echo "   ✅ PASS: $PASS"
echo "   ❌ FAIL: $FAIL"
echo "=============================================="

if [ "$FAIL" -eq 0 ]; then
  echo ""
  echo "🎉 所有验证通过！系统已成功上线！"
  echo "🎉 All checks passed! System is live!"
  exit 0
else
  echo ""
  echo "⚠️ 有 $FAIL 项验证失败，请检查。"
  echo "⚠️ $FAIL checks failed. Please investigate."
  exit 1
fi
