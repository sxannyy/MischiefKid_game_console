#!/bin/bash

process_info=$(sudo netstat -tulnp | grep 5432)

if [ -z "$process_info" ]; then
  echo "Порт уже свободен"
  exit 1
fi

process_id=$(echo $process_info | awk '{print $7}' | cut -d'/' -f1)

sudo kill $process_id

if [ $? -eq 0 ]; then
  echo "Порт 5432 был освобождён."
else
  echo "Ошибка выполнения скрипта."
  exit 1
fi