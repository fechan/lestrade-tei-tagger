echo "Activating virtual environment"
. venv/bin/activate

echo "Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

echo "Starting service"
cd src
python -m app &
