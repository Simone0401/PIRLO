#!/usr/bin/env bash
set -uo pipefail

find_ip_by_pattern() {
  local pattern=$1
  for iface in $(ifconfig -l | tr ' ' '\n' | grep "^${pattern}"); do
    ip=$(ifconfig "$iface" 2>/dev/null | awk '/inet / {print $2; exit}')
    if [[ -n "$ip" ]]; then
      return 0
    fi
  done
  return 1
}

HOST_IP=$(find_ip_by_pattern "utun")

if [[ -z "${HOST_IP:-}" ]]; then
  HOST_IP=$(ipconfig getifaddr en0 2>/dev/null || true)
fi

if [[ -z "${HOST_IP:-}" ]]; then
  echo "⚠️  Nessun IP trovato: assicurati che una interfaccia utun* o en0 sia attiva." >&2
  exit 1
fi

export HOST_IP
echo "🌐 IP impostato: $HOST_IP"

docker compose "$@"
