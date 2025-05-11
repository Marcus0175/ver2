- Install requirements:

```
pip3 install -r /path/to/requirements.txt
```

- Install MySQL if not already installed.
- Create a new database:

```
CREATE DATABASE food_delivery_restaurant;
```

- Import the `.sql` file from project folder
- Adjust `.env` file in project folder, its content likes below, replace your PASSWORD of MySQL:

```
SECRET_KEY="a5a77b02217117f8a71d0fbdefbb55c8871d30e5494d1ed9f93a3788f868a174"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
PASSWORD="144819"
```

- Run, in project folder, execute following command, you could change the `port`:

```
uvicorn app.main:app --reload
```