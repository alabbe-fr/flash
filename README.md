# Flash Cards

![](./docs/app.png)

## Development

### Get started

```bash
docker compose up -d --build
```

The application should be accessible by default from http://localhost:8000

### Add example data

- Download example data [here](https://github.com/alabbe-fr/flash/releases/download/latest/flash.zip)
- Unzip it
- Update the value `dataPath` in the file `scripts/config.json` (`scripts/config.example.json` can serve as an example) with the path of the unzipped archive.
- Inside the folder `scripts`, run the script `populate.py`

### Database migrations

#### Update db

```bash
flask db migrate
flask db upgrade
```

#### Downgrade to the last migration

```bash
flask db downgrade
```

## Production

Coming soon...
