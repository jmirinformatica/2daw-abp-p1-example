# 2daw-abp-p1-example

Exemple de suport pel projecte 1 de 2n de DAW.

## Setup

### Python Virtual Environment

#### Linux

Crea l'entorn:

    python3 -m venv .venv

L'activa:

    source .venv/bin/activate

Instal·la el requisits:

    pip install -r requirements.txt

Per a generar el fitxer de requiriments:

    pip freeze > requirements.txt

Per desactivar l'entorn:

    deactivate

#### Windows

Crea l'entorn:

    python -m venv .venv

L'activa:

    .venv\Scripts\activate

Instal·la el requisits:

    pip install -r requirements.txt

Per a generar el fitxer de requiriments:

    pip freeze > requirements.txt

Per desactivar l'entorn:

    deactivate

### Base de dades

La base de dades SQLite és dins de la carpeta [sqlite](./sqlite) s'ha de dir `database.db`, tot i que es pot configurar un nom diferent al fitxer de configuració. S'ha creat amb l'script [database.sql](./sqlite/database.sql). Aquest script conté dos usuaris de prova:

* `e@mir.cat` amb la contrasenya `patata` i el rol **editor**.
* `v@mir.cat` amb la contrasenya `patata` i el rol **viewer**.

### Fitxer de configuració

Crea un fitxer `.env` amb els paràmetres de configuració. Pots fer servir com a base el fitxer [.env.exemple](./.env.exemple).

## Run

Executa:

    flask run --debug

I obre un navegador a l'adreça: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Debug amb Visual Code

Des de l'opció de `Run and Debug`, crea un fitxer anomenat `launch.json` amb el contingut següent:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "MY APP",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```
