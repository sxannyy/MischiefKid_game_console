#!/bin/bash

set -e
set -o pipefail

echo "Обновляем списки пакетов…"
sudo apt update -qq

echo "Устанавливаем системные утилиты…"
sudo apt install -y net-tools docker-compose python3 python3-venv python3-pip

echo "Создаём/обновляем виртуальное окружение ./.venv"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

if [[ ! -f requirements.txt ]]; then
  echo "Файл requirements.txt не найден!"
  deactivate
  exit 1
fi

echo "→ Ставим зависимости из requirements.txt"
pip install -r requirements.txt

echo -e "\nГотово.
