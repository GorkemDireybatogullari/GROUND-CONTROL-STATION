#!/usr/bin/env bash
# Install system-level dependencies on Ubuntu 22.04 (ROS2 Humble target).
# Run once on a fresh machine.
set -euo pipefail

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "[install-system-deps] This script targets Ubuntu 22.04. Skipping."
    exit 0
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "[install-system-deps] apt-get not found. This script requires Debian/Ubuntu."
    exit 1
fi

SUDO=""
if [[ $EUID -ne 0 ]]; then SUDO="sudo"; fi

echo "[install-system-deps] Updating apt cache..."
$SUDO apt-get update

echo "[install-system-deps] Installing base build deps..."
$SUDO apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    pkg-config \
    libgeos-dev \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip

# Node.js 20.x via NodeSource
if ! command -v node >/dev/null 2>&1; then
    echo "[install-system-deps] Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | $SUDO -E bash -
    $SUDO apt-get install -y nodejs
fi

# uv (Astral) — Python package manager
if ! command -v uv >/dev/null 2>&1; then
    echo "[install-system-deps] Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# ROS2 Humble (optional — large download). Set INSTALL_ROS=1 to opt in.
if [[ "${INSTALL_ROS:-0}" == "1" ]]; then
    echo "[install-system-deps] Installing ROS2 Humble..."
    $SUDO apt-get install -y software-properties-common
    $SUDO add-apt-repository -y universe
    $SUDO curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
        -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        | $SUDO tee /etc/apt/sources.list.d/ros2.list >/dev/null
    $SUDO apt-get update
    $SUDO apt-get install -y \
        ros-humble-ros-base \
        ros-humble-common-interfaces \
        python3-rosdep \
        python3-colcon-common-extensions
    if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
        $SUDO rosdep init || true
    fi
    rosdep update || true
fi

echo "[install-system-deps] Done."
