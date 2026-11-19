# Mon Super Blog (Django)

## Lancer en local (VS Code)

```bash
python -m venv venv
# Windows :  venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations blogapp
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000/

## Tests

```bash
python manage.py test
```

## Déploiement

Voir les variables d'environnement dans `.env.example`.
Commande de démarrage : `gunicorn monblogprojet.wsgi:application`
Commande de build : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
