#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
FRONTEND_DIR="${ROOT_DIR}/frontend"
BACKEND_VENV="${BACKEND_DIR}/.venv"

BACKEND_APP="app.main:app"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
SMOKE_TIMEOUT_SECONDS="${SMOKE_TIMEOUT_SECONDS:-45}"

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-Yassine1@;}"
DB_NAME="${DB_NAME:-mt_facturation}"

LOG_DIR="${ROOT_DIR}/generated/launch"
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

STARTED_PIDS=()

info() {
  echo "[INFO] $*"
}

warn() {
  echo "[WARN] $*"
}

error() {
  echo "[ERROR] $*" >&2
}

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    error "Required command not found: ${cmd}"
    exit 1
  fi
}

is_port_listening() {
  local port="$1"

  if command -v lsof >/dev/null 2>&1; then
    lsof -iTCP:"${port}" -sTCP:LISTEN -nP >/dev/null 2>&1
    return $?
  fi

  if command -v ss >/dev/null 2>&1; then
    ss -ltn "sport = :${port}" 2>/dev/null | awk 'NR > 1 { found = 1 } END { exit !found }'
    return $?
  fi

  return 1
}

stop_port_listener() {
  local port="$1"
  local pids=""

  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -tiTCP:"${port}" -sTCP:LISTEN -nP 2>/dev/null || true)"
  elif command -v fuser >/dev/null 2>&1; then
    pids="$(fuser -n tcp "${port}" 2>/dev/null || true)"
  fi

  if [[ -z "${pids}" ]]; then
    return 0
  fi

  info "Stopping listeners on port ${port}: ${pids}"
  # shellcheck disable=SC2086
  kill ${pids} >/dev/null 2>&1 || true
  sleep 1
  # shellcheck disable=SC2086
  kill -9 ${pids} >/dev/null 2>&1 || true
}

kill_pid_file() {
  local pid_file="$1"
  if [[ ! -f "${pid_file}" ]]; then
    return 0
  fi

  local pid
  pid="$(cat "${pid_file}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
    info "Stopping stale process from ${pid_file} (pid=${pid})"
    kill "${pid}" >/dev/null 2>&1 || true
    sleep 1
    kill -9 "${pid}" >/dev/null 2>&1 || true
  fi
  rm -f "${pid_file}"
}

stop_backend_runtime_processes() {
  local pids=""
  pids="$(pgrep -f "uvicorn ${BACKEND_APP}" || true)"
  if [[ -n "${pids}" ]]; then
    info "Stopping stale backend runtime process(es): ${pids}"
    # shellcheck disable=SC2086
    kill ${pids} >/dev/null 2>&1 || true
    sleep 1
    # shellcheck disable=SC2086
    kill -9 ${pids} >/dev/null 2>&1 || true
  fi
}

wait_for_http_get() {
  local name="$1"
  local url="$2"
  local expected="$3"
  local timeout="$4"
  shift 4

  local deadline=$((SECONDS + timeout))
  while (( SECONDS < deadline )); do
    local code
    code="$(curl -sS -o /dev/null -w "%{http_code}" "$@" "${url}" || true)"
    if [[ "${code}" == "${expected}" ]]; then
      info "${name} smoke check passed (${code})."
      return 0
    fi
    sleep 1
  done

  error "${name} smoke check failed (expected status ${expected})."
  return 1
}

check_openapi_path() {
  local url="$1"
  local path="$2"

  "${PY_BOOTSTRAP}" - "${url}" "${path}" <<'PY'
import json
import sys
import urllib.request

url = sys.argv[1]
path = sys.argv[2]

with urllib.request.urlopen(url, timeout=4) as response:
    payload = json.load(response)

paths = payload.get("paths", {})
sys.exit(0 if path in paths else 1)
PY
}

wait_for_openapi_path() {
  local name="$1"
  local url="$2"
  local path="$3"
  local timeout="$4"
  local deadline=$((SECONDS + timeout))

  while (( SECONDS < deadline )); do
    if check_openapi_path "${url}" "${path}" >/dev/null 2>&1; then
      info "${name} smoke check passed (path found: ${path})."
      return 0
    fi
    sleep 1
  done

  error "${name} smoke check failed (missing path: ${path})."
  return 1
}

register_started_pid() {
  local pid="$1"
  STARTED_PIDS+=("${pid}")
}

cleanup_on_failure() {
  local exit_code="$1"
  if [[ "${exit_code}" -eq 0 ]]; then
    return 0
  fi

  warn "Launcher failed. Stopping services started in this run."
  for pid in "${STARTED_PIDS[@]}"; do
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
      sleep 1
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
  done
}

trap 'cleanup_on_failure $?' EXIT

mkdir -p "${LOG_DIR}"

info "Root directory: ${ROOT_DIR}"
info "Checking required tooling..."

if command -v python3 >/dev/null 2>&1; then
  PY_BOOTSTRAP="python3"
elif command -v python >/dev/null 2>&1; then
  PY_BOOTSTRAP="python"
else
  error "Python was not found. Install Python 3.12+ and retry."
  exit 1
fi

require_cmd node
require_cmd npm
require_cmd curl

info "Tooling check passed."
info "Cleaning stale launcher runtime processes and port listeners..."

kill_pid_file "${BACKEND_PID_FILE}"
kill_pid_file "${FRONTEND_PID_FILE}"
stop_backend_runtime_processes

stop_port_listener "${BACKEND_PORT}"
stop_port_listener "${FRONTEND_PORT}"

if is_port_listening "${BACKEND_PORT}"; then
  warn "Backend port ${BACKEND_PORT} is still busy after cleanup. Falling back to port 8010."
  BACKEND_PORT="8010"
  stop_port_listener "${BACKEND_PORT}"
fi

if is_port_listening "${FRONTEND_PORT}"; then
  warn "Frontend port ${FRONTEND_PORT} is still busy after cleanup. Falling back to port 5174."
  FRONTEND_PORT="5174"
  stop_port_listener "${FRONTEND_PORT}"
fi

if [[ -d "${BACKEND_DIR}" ]]; then
  info "Backend directory found: ${BACKEND_DIR}"

  pushd "${BACKEND_DIR}" >/dev/null

  if [[ ! -x ".venv/bin/python" ]]; then
    info "Backend virtual environment missing, creating: ${BACKEND_VENV}"
    "${PY_BOOTSTRAP}" -m venv "${BACKEND_VENV}"
  else
    info "Backend virtual environment found."
  fi

  "${BACKEND_VENV}/bin/python" -m pip install --upgrade pip

  if [[ -f "requirements.txt" ]]; then
    info "Installing backend dependencies from requirements.txt"
    "${BACKEND_VENV}/bin/python" -m pip install -r "requirements.txt"
  elif [[ -f "pyproject.toml" ]]; then
    info "Installing backend package from pyproject.toml"
    "${BACKEND_VENV}/bin/python" -m pip install -e "."
  else
    warn "No backend dependency file found: requirements.txt or pyproject.toml."
  fi

  info "Running backend dependency check: pip check"
  "${BACKEND_VENV}/bin/python" -m pip check

  export PGHOST="${DB_HOST}"
  export PGPORT="${DB_PORT}"
  export PGUSER="${DB_USER}"
  export PGPASSWORD="${DB_PASSWORD}"
  export PGDATABASE="${DB_NAME}"
  export PYTHONPATH="${BACKEND_DIR}"

  info "Running backend DB bootstrap: create database and initialize schema"
  "${BACKEND_VENV}/bin/python" -m app.db.bootstrap

  popd >/dev/null

  if [[ -x "${BACKEND_DIR}/start-backend.sh" ]]; then
    info "Starting backend using custom starter: ${BACKEND_DIR}/start-backend.sh"
    (
      cd "${BACKEND_DIR}"
      export BACKEND_ENABLE_RELOAD=false
      export BACKEND_PORT
      nohup "${BACKEND_DIR}/start-backend.sh" >"${BACKEND_LOG}" 2>&1 &
      echo $! > "${BACKEND_PID_FILE}"
    )
  else
    if [[ -f "${BACKEND_DIR}/app/main.py" ]]; then
      info "Starting backend with uvicorn fallback..."
      (
        cd "${BACKEND_DIR}"
        export BACKEND_ENABLE_RELOAD=false
        export BACKEND_PORT
        nohup "${BACKEND_VENV}/bin/python" -m uvicorn "${BACKEND_APP}" --host 0.0.0.0 --port "${BACKEND_PORT}" >"${BACKEND_LOG}" 2>&1 &
        echo $! > "${BACKEND_PID_FILE}"
      )
    else
      error "No backend start file found. Expected app/main.py."
      exit 1
    fi
  fi

  backend_pid="$(cat "${BACKEND_PID_FILE}")"
  register_started_pid "${backend_pid}"
  info "Backend started (pid=${backend_pid}, log=${BACKEND_LOG})."
else
  warn "Backend directory not found at ${BACKEND_DIR}. Backend launch skipped."
fi

if [[ -d "${FRONTEND_DIR}" ]]; then
  info "Frontend directory found: ${FRONTEND_DIR}"
  pushd "${FRONTEND_DIR}" >/dev/null

  if [[ ! -d "node_modules" ]]; then
    if [[ -f "package-lock.json" ]]; then
      info "Frontend node_modules missing. Installing with npm ci..."
      npm ci
    else
      info "Frontend node_modules missing. Installing with npm install..."
      npm install
    fi
  else
    info "Frontend node_modules found. Verifying dependency health..."
    if ! npm ls --depth=0 >/dev/null 2>&1; then
      warn "Frontend dependency health check failed. Repairing with npm install..."
      npm install
    else
      info "Frontend dependencies are healthy. Skipping reinstall."
    fi
  fi

  info "Running frontend dependency check: npm ls --depth=0"
  npm ls --depth=0 >/dev/null
  popd >/dev/null

  if [[ -f "${FRONTEND_DIR}/package.json" ]]; then
    info "Starting frontend with npm run dev..."
    (
      cd "${FRONTEND_DIR}"
      export VITE_API_BASE_URL="http://localhost:${BACKEND_PORT}"
      export FRONTEND_PORT
      nohup npm run dev -- --host 0.0.0.0 --port "${FRONTEND_PORT}" --strictPort >"${FRONTEND_LOG}" 2>&1 &
      echo $! > "${FRONTEND_PID_FILE}"
    )
  else
    error "No frontend start file found. Expected package.json."
    exit 1
  fi

  frontend_pid="$(cat "${FRONTEND_PID_FILE}")"
  register_started_pid "${frontend_pid}"
  info "Frontend started (pid=${frontend_pid}, log=${FRONTEND_LOG})."
else
  warn "Frontend directory not found at ${FRONTEND_DIR}. Frontend launch skipped."
fi

if [[ ! -f "${BACKEND_PID_FILE}" && ! -f "${FRONTEND_PID_FILE}" ]]; then
  error "No service was started. Ensure backend/frontend project folders exist."
  exit 1
fi

info "Running smoke checks..."
wait_for_http_get "Backend health" "http://127.0.0.1:${BACKEND_PORT}/api/v1/health" 200 "${SMOKE_TIMEOUT_SECONDS}"
wait_for_http_get \
  "Backend customers list" \
  "http://127.0.0.1:${BACKEND_PORT}/api/v1/customers?page=1&size=1" \
  200 \
  "${SMOKE_TIMEOUT_SECONDS}" \
  -H "Authorization: Bearer launch-smoke:admin,ops"
wait_for_openapi_path \
  "Backend catalog API contract" \
  "http://127.0.0.1:${BACKEND_PORT}/openapi.json" \
  "/api/v1/offer-categories" \
  "${SMOKE_TIMEOUT_SECONDS}"
wait_for_http_get "Frontend root" "http://127.0.0.1:${FRONTEND_PORT}" 200 "${SMOKE_TIMEOUT_SECONDS}"

info "Launch sequence completed."
info "Backend URL:  http://localhost:${BACKEND_PORT}"
info "Frontend URL: http://localhost:${FRONTEND_PORT}"
info "Backend log:  ${BACKEND_LOG}"
info "Frontend log: ${FRONTEND_LOG}"
