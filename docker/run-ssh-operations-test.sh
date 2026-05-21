#!/usr/bin/env bash
set -euo pipefail

: "${FWBACKUPS_TEST_SSH_USER:=fwbackupstest}"
: "${FWBACKUPS_TEST_SSH_PASSWORD:=fwbackupstest}"
: "${FWBACKUPS_TEST_SSH_PORT:=22}"
: "${FWBACKUPS_TEST_REMOTE_FOLDER:=/home/${FWBACKUPS_TEST_SSH_USER}/remote}"
: "${FWBACKUPS_TEST_FILE_SIZE_BYTES:=8192}"
: "${FWBACKUPS_TEST_FILE_COUNT:=12}"

export FWBACKUPS_TEST_NONINTERACTIVE=1
export FWBACKUPS_TEST_CLEAN=1
export FWBACKUPS_TEST_SSH_HOST=127.0.0.1
export FWBACKUPS_TEST_SSH_USER
export FWBACKUPS_TEST_SSH_PASSWORD
export FWBACKUPS_TEST_SSH_PORT
export FWBACKUPS_TEST_REMOTE_FOLDER
export FWBACKUPS_TEST_FILE_SIZE_BYTES
export FWBACKUPS_TEST_FILE_COUNT
export PYTHONPATH=/workspace

if ! id -u "${FWBACKUPS_TEST_SSH_USER}" >/dev/null 2>&1; then
    useradd --create-home --shell /bin/bash "${FWBACKUPS_TEST_SSH_USER}"
fi

echo "${FWBACKUPS_TEST_SSH_USER}:${FWBACKUPS_TEST_SSH_PASSWORD}" | chpasswd

mkdir -p /run/sshd "${FWBACKUPS_TEST_REMOTE_FOLDER}"
mkdir -p /root/.fwbackups/Sets
chown -R "${FWBACKUPS_TEST_SSH_USER}:${FWBACKUPS_TEST_SSH_USER}" "/home/${FWBACKUPS_TEST_SSH_USER}"

cat >/etc/ssh/sshd_config.d/fwbackups-test.conf <<EOF
PasswordAuthentication yes
KbdInteractiveAuthentication no
PermitRootLogin no
UsePAM no
AllowUsers ${FWBACKUPS_TEST_SSH_USER}
Port ${FWBACKUPS_TEST_SSH_PORT}
EOF

ssh-keygen -A
/usr/sbin/sshd -D -e &
sshd_pid=$!

cleanup() {
    kill "${sshd_pid}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

python - <<'PY'
import os
import socket
import time

host = os.environ["FWBACKUPS_TEST_SSH_HOST"]
port = int(os.environ["FWBACKUPS_TEST_SSH_PORT"])
deadline = time.time() + 10

while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except OSError:
        if time.time() >= deadline:
            raise
        time.sleep(0.2)
PY

cd /workspace/test
python test.operations.py
