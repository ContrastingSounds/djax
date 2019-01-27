#!/bin/sh

# DJAX INSTALL SCRIPT FOR LOCAL DEVELOPMENT (TESTED ON MAC ONLY)
#
# 1. Check Python version
# 2. Check .env existence and content
# 3. Create the python environment and install the dependencies
# 4. Create the database schema
# 5. Create the admin user


# Check Python version
if python --version =~ "^Python 3.7" ; then
    echo "Checking environment: Python 3.7+ found"
    echo
else
    echo "ERROR: Python 3.7 not found"
    exit 1
fi

# Check .env existence and content
if [ ! -f .env ]; then
    echo "ERROR: .env environment file not found."
    exit 1
fi

git clone https://github.com/ContrastingSounds/djax.git
cp .env djax/
cd djax
git checkout $(git describe --abbrev=0 --tags)

DEFAULTS_FOUND=0

if [[ `grep "LOOKER_INSTANCE" .env` =~ ^LOOKER_INSTANCE=(.*) ]] ; then
    if [ ${BASH_REMATCH[1]} = "your-instance.looker.com" ] ; then
        echo "ERROR: .env still contains template value for LOOKER_INSTANCE"
        echo
        DEFAULTS_FOUND=1
    else
        INSTANCE=${BASH_REMATCH[1]}
    fi
fi

if [[ `grep "LOOKER_CLIENT_ID" .env` =~ ^LOOKER_CLIENT_ID=(.*) ]] ; then
    if [ ${BASH_REMATCH[1]} = "123abc" ] ; then
        echo "ERROR: .env still contains template value for LOOKER_CLIENT_ID"
        echo
        DEFAULTS_FOUND=1
    else
        CLIENT_ID=${BASH_REMATCH[1]}
    fi
fi

if [[ `grep "LOOKER_CLIENT_SECRET" .env` =~ ^LOOKER_CLIENT_SECRET=(.*) ]] ; then
    if [ ${BASH_REMATCH[1]} = "123abc123abc" ] ; then
        echo "ERROR: .env still contains template value for LOOKER_CLIENT_SECRET"
        echo
        DEFAULTS_FOUND=1
    else
        CLIENT_SECRET=${BASH_REMATCH[1]}
    fi
fi

if [ $DEFAULTS_FOUND = 1 ]; then
    echo "Exiting setup due to invalid .env file."
    echo "Djax requires a .env file with details for a default instance e.g."
    echo
    echo "LOOKER_INSTANCE=mycompany.looker.com"
    echo "LOOKER_CLIENT_ID=ZGyDH9skynnVF7bBqTkb"
    echo "LOOKER_CLIENT_SECRET=n5tHHy3PhHJ46STDfRqKX8Ft"
    echo
    exit 1
fi

# Create the python environment and install the dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create the database schema
python manage.py migrate

# Create the admin user
echo "Creating admin user..."
echo

# Register the default instance
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'pass')" | python manage.py shell

python manage.py collectstatic --no-input
