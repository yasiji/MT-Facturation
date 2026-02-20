#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${ROOT_DIR}/generated/launch"
BACKEND_PID_FILE="${LOG_DIR}/backend.pid"
FRONTEND_PID_FILE="${LOG_DIR}/frontend.pid"

info() {
  echo "[INFO] $*"
}

warn() {
  echo "[WARN] $*"
}

kill_pid_file() {
  local pid_file="$1"
  local label="$2"

  if [[ ! -f "${pid_file}" ]]; then
    return 0
  fi

  local pid
  pid="$(cat "${pid_file}" 2>/dev/null || true)"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
    info "Stopping ${label} (pid=${pid}) from ${pid_file}"
    kill "${pid}" >/dev/null 2>&1 || true
    sleep 1
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill -9 "${pid}" >/dev/null 2>&1 || true
    fi
  else
    warn "PID file exists but process is not running: ${pid_file}"
  fi

  rm -f "${pid_file}"
}

stop_pattern() {
  local pattern="$1"
  local label="$2"
  local pids=""

  pids="$(pgrep -f "${pattern}" || true)"
  if [[ -z "${pids}" ]]; then
    return 0
  fi

  info "Stopping ${label}: ${pids}"
  # shellcheck disable=SC2086
  kill ${pids} >/dev/null 2>&1 || true
  sleep 1
  # shellcheck disable=SC2086
  kill -9 ${pids} >/dev/null 2>&1 || true
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

  info "Freeing port ${port}: ${pids}"
  # shellcheck disable=SC2086
  kill ${pids} >/dev/null 2>&1 || true
  sleep 1
  # shellcheck disable=SC2086
  kill -9 ${pids} >/dev/null 2>&1 || true
}

mkdir -p "${LOG_DIR}"

kill_pid_file "${BACKEND_PID_FILE}" "backend"
kill_pid_file "${FRONTEND_PID_FILE}" "frontend"

# Fallbacks when pid files are stale/missing.
stop_pattern "uvicorn app.main:app" "backend runtime"
stop_pattern "npm run dev -- --host 0.0.0.0" "frontend npm dev"
stop_pattern "vite --host 0.0.0.0" "frontend vite runtime"

# Also free known launcher ports.
for port in 8000 8010 5173 5174; do
  stop_port_listener "${port}"
done

info "Stop sequence completed."