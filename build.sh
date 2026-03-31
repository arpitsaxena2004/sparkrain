#!/usr/bin/env bash
# Build script for Render deployment
set -o errexit

echo "=== Starting Build Process ==="
echo "Python version:"
python --version

echo ""
echo "=== Installing dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== Verifying Django installation ==="
python -c "import django; print(f'Django version: {django.get_version()}')"

echo ""
echo "=== Checking project structure ==="
ls -la
echo ""
echo "=== Checking if core app exists ==="
ls -la core/

echo ""
echo "=== Testing Django settings import ==="
python -c "from rainwater_ai import settings; print('Settings imported successfully')"

echo ""
echo "=== Collecting static files ==="
python manage.py collectstatic --no-input --verbosity 2

echo ""
echo "=== Running migrations ==="
python manage.py migrate --verbosity 2

echo ""
echo "=== Build completed successfully! ==="
