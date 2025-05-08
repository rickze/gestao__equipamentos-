#!/bin/bash
set -e

echo '🔧 A preparar o ambiente de desenvolvimento...'

if [ -f packages.txt ]; then
  sudo apt update
  sudo apt install -y $(cat packages.txt)
fi

if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

pip install streamlit

echo '✅ Ambiente pronto!'
