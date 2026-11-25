# Manual bàsic de Docker i Docker Compose

Aquest manual explica què és Docker, en què es diferencia d'una màquina virtual, què aporta Docker Compose, com instal·lar-ho a Linux, Windows i macOS, com executar el fitxer [`docker-compose.yml`](./docker-compose.yml) d'aquest projecte, que aixeca un servidor de correu de proves (**Mailpit**), com afegir-hi una base de dades MySQL o PostgreSQL i com executar la pròpia aplicació Flask dins de Docker.

> Tots els exemples fan servir **Docker Compose v2**, la comanda del qual és `docker compose` (amb un espai). L'antic `docker-compose` (amb guionet) és la versió 1 i està obsolet.

---

## Índex

1. [Què és Docker i diferències amb les màquines virtuals](#1-què-és-docker-i-diferències-amb-les-màquines-virtuals)
2. [Què és Docker Compose](#2-què-és-docker-compose)
3. [Com instal·lar Docker i Docker Compose](#3-com-instal·lar-docker-i-docker-compose)
4. [Com executar el docker-compose.yml](#4-com-executar-el-docker-composeyml)
5. [Afegir una base de dades](#5-afegir-una-base-de-dades)
6. [Afegir l'aplicació Flask](#6-afegir-laplicació-flask)
7. [Resum de comandes](#7-resum-de-comandes)

---

## 1. Què és Docker i diferències amb les màquines virtuals

**Docker** és una plataforma per empaquetar una aplicació amb totes les seves dependències dins d'una **imatge** i executar-la de manera aïllada en un **contenidor**. L'objectiu és que l'aplicació funcioni igual a l'ordinador de desenvolupament, al servidor de proves i a producció: «funciona a la meva màquina» deixa de ser una excusa.

### Conceptes bàsics

| Concepte | Què és |
| --- | --- |
| **Imatge** (*image*) | Plantilla de només lectura amb el sistema de fitxers i la configuració de l'aplicació. Es construeix per capes. |
| **Contenidor** (*container*) | Instància en execució d'una imatge. És un o diversos processos aïllats del sistema amfitrió. |
| **Registre** (*registry*) | Magatzem d'imatges. El més conegut és [Docker Hub](https://hub.docker.com/). |
| **Dockerfile** | Fitxer de text amb les instruccions per construir una imatge pròpia. |
| **Volum** (*volume*) | Emmagatzematge persistent gestionat per Docker, perquè les dades sobrevisquin a la vida del contenidor. |
| **Xarxa** (*network*) | Xarxa virtual que connecta contenidors entre si i amb l'amfitrió. |

La relació és la mateixa que entre una classe i un objecte: la **imatge** és la classe (no s'executa, només descriu) i el **contenidor** és l'objecte (una instància que s'executa). D'una mateixa imatge en pots crear tants contenidors com vulguis.

### Contenidor vs màquina virtual

Una **màquina virtual (VM)** simula un ordinador complet: un *hipervisor* (VMware, VirtualBox, Hyper-V…) virtualitza el maquinari i dins s'instal·la un sistema operatiu sencer amb el seu propi nucli. Un **contenidor**, en canvi, no virtualitza maquinari: és un procés normal de l'amfitrió, però aïllat amb mecanismes del nucli de Linux:

- **namespaces**: aïllen el que el procés pot veure (processos, xarxa, sistema de fitxers, usuaris…).
- **cgroups**: limiten i mesuren els recursos que pot consumir (CPU, memòria, E/S).

Per això els contenidors comparteixen el **nucli del sistema amfitrió** i no en porten un de propi.

| Característica | Contenidor | Màquina virtual |
| --- | --- | --- |
| Nucli | Comparteix el de l'amfitrió | Té un nucli propi |
| Sistema operatiu | Només les llibreries de l'aplicació | SO complet instal·lat |
| Temps d'arrencada | Mil·lisegons o pocs segons | Desenes de segons o minuts |
| Mida típica | Megabytes | Gigabytes |
| Consum de recursos | Baix (processos normals) | Alt (maquinari virtualitzat) |
| Nombre per amfitrió | Molts | Pocs |
| Aïllament | Bo, però comparteix nucli | Molt fort, a nivell de maquinari |
| Portabilitat | Molt alta (mateixa imatge a tot arreu) | Mitjana (depèn del format de disc) |

### Avantatges i limitacions

**Avantatges**

- Entorns reproduïbles: la imatge fixa versions de llibreries i configuració.
- Arrencada ràpida i poc consum, ideal per a microserveis i CI/CD.
- Fàcil d'esborrar i tornar a crear: si un contenidor es trenca, el reemplacis.
- Ecosistema enorme d'imatges llestes per usar (bases de dades, servidors web…).

**Limitacions**

- L'aïllament és més feble que el d'una VM: comparteixen nucli. No és una bona barrera de seguretat entre usuaris no confiables.
- Els contenidors Linux necessiten un nucli Linux. A Windows i macOS, Docker Desktop executa una VM Linux lleugera per poder-los fer córrer.
- No són adequats per a aplicacions d'escriptori amb interfície gràfica.
- Les dades no persisteixen soles: cal fer servir volums o *bind mounts*.
- No substitueixen una estratègia de *backup* ni d'alta disponibilitat.

---

## 2. Què és Docker Compose

**Docker Compose** és l'eina que permet descriure **diversos contenidors** (i les seves xarxes i volums) en un únic fitxer YAML, normalment `docker-compose.yml`, i gestionar-los com una unitat amb una sola comanda.

Sense Compose, per aixecar una aplicació amb diversos serveis hauries d'executar diversos `docker run` llargs, crear la xarxa a mà i recordar l'ordre. Amb Compose escrius la configuració una vegada i executes `docker compose up`.

### Vocabulari de Compose

| Terme | Significat |
| --- | --- |
| **Projecte** | Conjunt de serveis definit pel fitxer. El nom per defecte és el de la carpeta. |
| **Servei** (*service*) | Cada entrada sota `services:`. Defineix com es crea un o més contenidors. |
| **Contenidor** | Instància real d'un servei en execució. |
| **Xarxa** | Compose crea una xarxa pròpia del projecte; els serveis es poden comunicar pel nom del servei. |
| **Volum** | Emmagatzematge persistent declarat al fitxer. |

### Versions: `docker compose` vs `docker-compose`

| | v1 (antic) | v2 (actual) |
| --- | --- | --- |
| Comanda | `docker-compose` | `docker compose` |
| Implementació | Python | Go (plugin del CLI de Docker) |
| Instal·lació | Paquet `docker-compose` | Paquet `docker-compose-plugin` (o inclòs a Docker Desktop) |
| Estat | Obsolet | Recomanat |

El fitxer YAML és compatible en tots dos casos. Si un tutorial fa servir `docker-compose`, normalment n'hi ha prou de canviar-ho per `docker compose`.

### Estructura mínima

```yaml
services:                 # Obligatori: contenidors que formen el projecte
  web:                    # Nom del servei (també és el nom DNS dins la xarxa)
    image: nginx:alpine   # Imatge a executar (es descarrega del registre si no hi és)
    ports:
      - "8080:80"         # HOST:CONTENIDOR -> http://localhost:8080
    environment:          # Variables d'entorn del contenidor
      - TZ=Europe/Madrid
    volumes:
      - dades:/usr/share/nginx/html   # Volum persistent
    depends_on:           # Ordre d'arrencada (no espera que estigui "llest")
      - cache
    restart: unless-stopped

  cache:                  # Servei de memòria cau
    image: redis:7-alpine
    volumes:
      - dades_cache:/data

volumes:                  # Declaració dels volums amb nom
  dades:
  dades_cache:
```

> La clau `version:` que apareix en tutorials antics ja **no cal** a Compose v2 i provoca un avís si la poses.

Claus que veuràs més sovint:

| Clau | Funció |
| --- | --- |
| `image` | Imatge a executar. |
| `build` | Construeix la imatge a partir d'un `Dockerfile` en lloc de descarregar-la. |
| `ports` | Publica ports del contenidor a l'amfitrió. |
| `environment` / `env_file` | Variables d'entorn. |
| `volumes` | Persistència i fitxers compartits. |
| `depends_on` | Ordre d'arrencada dels serveis. |
| `restart` | Política de reinici (per exemple, `unless-stopped`). |
| `command` | Substitueix la comanda per defecte de la imatge. |
| `healthcheck` | Comprovació de salut del servei. |

---

## 3. Com instal·lar Docker i Docker Compose

Docker té dos components que et calen:

1. **Docker Engine** (o Docker Desktop): el dimoni que executa els contenidors.
2. **Docker Compose**: el plugin que llig el YAML. A Docker Desktop ja ve inclòs.

### 3.1 Linux (Ubuntu i Debian)

La manera recomanada és el repositori oficial de Docker, que dona versions més recents que els paquets de la distribució.

```bash
# 1. Paquets previs i clau GPG oficial
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 2. Repositori (format deb822)
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

# 3. Instal·lació d'Engine i Compose
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

> **Debian:** canvia `linux/ubuntu` per `linux/debian` tant a la clau com a `URIs`, i la distribució ha de ser la teva (per exemple `bookworm`). Consulta sempre la [documentació oficial](https://docs.docker.com/engine/install/) per a la teva distribució.

**Permisos sense `sudo`.** Per defecte, només `root` pot parlar amb el dimoni. Afegeix el teu usuari al grup `docker` i torna a iniciar la sessió (o executa `newgrp docker`):

```bash
sudo usermod -aG docker $USER
newgrp docker
```

> Formar part del grup `docker` equival a tenir permisos de `root` sobre la màquina. En un servidor compartit, valora-ho bé.

**Alternativa ràpida (no recomanada per a producció).** L'script oficial instal·la l'última versió en un pas:

```bash
curl -fsSL https://get.docker.com | sudo sh
```

**Comprovació:**

```bash
docker --version
docker compose version
docker run --rm hello-world
```

Si `docker run hello-world` mostra un missatge de benvinguda, tot funciona.

### 3.2 Windows 10/11

Docker no corre de manera nativa sobre el nucli de Windows (per als contenidors Linux): **Docker Desktop** executa una màquina virtual Linux lleugera gràcies a **WSL 2**. Cal:

1. Windows 10 de 64 bits (versió 22H2 o posterior) o Windows 11.
2. Virtualització activada a la BIOS/UEFI (Intel VT-x o AMD-V).
3. **WSL 2** instal·lat.

```powershell
# Instal·la WSL 2 (pot requerir reiniciar)
wsl --install

# Instal·la Docker Desktop
winget install --id Docker.DockerDesktop -e
```

També el pots descarregar de [docker.com](https://www.docker.com/products/docker-desktop/). Després:

1. Obre **Docker Desktop** i espera que l'indicador passi a *Running*.
2. A **Settings → General**, comprova que està activat *Use the WSL 2 based engine*.
3. A **Settings → Resources → WSL Integration**, activa la teva distribució (per exemple Ubuntu) si vols usar `docker` des del terminal de WSL.

**Comprovació** (PowerShell, CMD o terminal WSL):

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

> Assegura't que Docker Desktop està en mode **Linux containers** (ho indica la barra d'estat). Els contenidors Windows existeixen, però aquest manual no els tracta.

### 3.3 macOS

Docker Desktop també fa servir una VM Linux interna. Requisits: macOS recent (consulta la documentació per a la versió mínima) i un Mac amb Apple Silicon o Intel.

**Amb Homebrew:**

```bash
brew install --cask docker
open -a Docker
```

**Amb l'instal·lador:** descarrega el `.dmg` de [docker.com](https://www.docker.com/products/docker-desktop/), arrossega l'aplicació a *Applications* i obre-la. La primera vegada demanarà permisos d'administrador.

Espera que la icona de la barra de menús indiqui *Docker Desktop is running* i comprova:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

**Alternativa sense Docker Desktop: Colima.** És una VM Linux lleugera de codi obert que funciona amb el CLI de Docker:

```bash
brew install colima docker docker-compose
colima start
```

Amb aquesta opció, `docker compose` pot necessitar que enllacis el binari com a plugin (Homebrew mostra les instruccions en instal·lar `docker-compose`):

```bash
mkdir -p ~/.docker/cli-plugins
ln -sfn "$(brew --prefix)/opt/docker-compose/bin/docker-compose" \
  ~/.docker/cli-plugins/docker-compose
```

### 3.4 Què s'ha instal·lat

| Component | Linux | Windows/macOS |
| --- | --- | --- |
| Dimoni | `dockerd` (servei del sistema) | Dins de Docker Desktop |
| Client | `docker` | `docker` |
| Compose | `docker compose` (plugin) | `docker compose` (inclòs) |
| Buildx | `docker buildx` | `docker buildx` |

---

## 4. Com executar el `docker-compose.yml`

### 4.1 El fitxer del projecte

```yaml
services:
  mailpit:
    image: axllent/mailpit
    ports:
      - "127.0.0.1:8025:8025"  # Web Inbox UI
      - "127.0.0.1:1025:1025"  # SMTP Port
```

Línia a línia:

- `services:`: arrel del projecte. Aquí només hi ha un servei.
- `mailpit:`: nom del servei. Compose crearà un contenidor a partir d'aquest nom i el del projecte (per exemple, `<carpeta>-mailpit-1`).
- `image: axllent/mailpit`: imatge oficial de [Mailpit](https://mailpit.axllent.org/), un servidor SMTP de proves amb interfície web. Sense etiqueta, s'usa `latest`; en projectes reals és millor fixar una versió (`axllent/mailpit:v1.x`).
- `ports`: format `IP_AMFITRIÓ:PORT_AMFITRIÓ:PORT_CONTENIDOR`.
  - `8025`: interfície web on es veuen els correus rebuts.
  - `1025`: port SMTP on l'aplicació envia els correus.
  - `127.0.0.1` vol dir que els ports només s'obrin a la mateixa màquina. Això és intencionat: Mailpit no té autenticació i no ha d'estar exposat a la xarxa.

Mailpit **no envia correus a l'exterior**: els intercepta i els mostra a la interfície web. És perfecte per desenvolupar sense enviar correus reals.

### 4.2 Requisits previs

- Docker i Docker Compose instal·lats (secció 3).
- El dimoni de Docker en marxa (Docker Desktop obert, o servei `docker` actiu).
- Estar dins de la carpeta que conté el `docker-compose.yml`:

```bash
cd 2daw-abp-p1-example
ls docker-compose.yml
```

### 4.3 Aixecar el servei

```bash
# Opcional: descarrega la imatge abans d'arrencar
docker compose pull

# Crea la xarxa i arrenca el contenidor en segon pla (-d = detached)
docker compose up -d
```

Sortida semblant a:

```text
[+] Running 2/2
 ✔ Network 2daw-abp-p1-example_default  Created
 ✔ Container 2daw-abp-p1-example-mailpit-1  Started
```

Comprova l'estat:

```bash
docker compose ps
```

Hauries de veure el servei `mailpit` amb estat `running` i els ports `127.0.0.1:8025->8025/tcp` i `127.0.0.1:1025->1025/tcp`.

Segueix els registres (logs) en directe. Per sortir, prem `Ctrl+C`: això **no** atura el contenidor.

```bash
docker compose logs -f mailpit
```

### 4.4 Utilitzar Mailpit

1. Obre [http://127.0.0.1:8025](http://127.0.0.1:8025) al navegador. Veuràs la safata d'entrada buida.
2. Comprova que el `.env` del projecte apunta al SMTP de Mailpit. Els valors per defecte ja hi coincideixen:

   ```dotenv
   MAIL_SMTP_SERVER="127.0.0.1"
   MAIL_SMTP_PORT=1025
   ```

3. Arrenca l'aplicació Flask (`flask run --debug`) i envia un correu des d'alguna funcionalitat que el generi (per exemple, el formulari de contacte).
4. El correu apareixerà a la safata de Mailpit. No sortirà d'aquella màquina.

> Si el correu no arriba, revisa que el contenidor estigui `running` i que l'aplicació usi `127.0.0.1` i no `localhost`: en alguns sistemes `localhost` es resol a `::1` (IPv6) i el port només està publicat a IPv4.

### 4.5 Aturar i eliminar

| Comanda | Què fa | Dades |
| --- | --- | --- |
| `docker compose stop` | Atura els contenidors sense eliminar-los. | Es perden els missatges en memòria. |
| `docker compose start` | Torna a arrencar els contenidors aturats. | Comença buit. |
| `docker compose restart` | Reinicia els contenidors. | Igual que `stop` + `start`. |
| `docker compose down` | Atura i **elimina** contenidors i xarxa. | Es perden els missatges. |
| `docker compose down --rmi all` | A més, elimina les imatges descarregades. | Es perden els missatges. |

Per defecte, Mailpit guarda els missatges **en memòria**: en aturar o eliminar el contenidor, es perden.

### 4.6 Comandes útils del projecte

```bash
# Valida i mostra la configuració final (útil per detectar errors de YAML)
docker compose config

# Veure l'estat dels serveis
docker compose ps

# Veure els logs d'un servei concret
docker compose logs -f mailpit

# Reiniciar només un servei
docker compose restart mailpit

# Arrencar i reconstruir si has canviat el YAML o la imatge
docker compose up -d --force-recreate
```

---

## 5. Afegir una base de dades

Fins ara, el projecte només aixeca Mailpit. Si necessites una base de dades real, pots afegir-la com un servei més al mateix `docker-compose.yml`: d'aquesta manera no cal instal·lar MySQL ni PostgreSQL a l'ordinador i tothom treballa amb la mateixa versió.

> Tria **una** de les dues opcions. Els exemples de MySQL i PostgreSQL són alternatius i tots dos fan servir el nom de servei `db`; no els facis servir alhora.

### 5.1 Consideracions generals

- Afegeix el servei `db` dins de la secció `services:` que ja tens i el volum dins de `volumes:`. No copiïs el bloc sencer substituint el fitxer ni esborris el servei `mailpit`.
- Fes servir una versió fixa de la imatge (`mysql:8.4`, `postgres:17`) en lloc de `latest`.
- Publica el port només a `127.0.0.1` si l'aplicació Flask s'executa a l'ordinador. Si l'aplicació també va dins de Compose, no cal publicar-lo: es connecta pel nom del servei (`db`) i el port intern.
- Les contrasenyes dels exemples són per a desenvolupament. En un projecte real, posa-les en un fitxer `.env` i referencia-les amb `${NOM_VARIABLE}`.
- El contenidor de base de dades és independent del de Mailpit: tots dos poden conviure al mateix projecte de Compose.
- Després de desar el fitxer, executa `docker compose up -d` per crear i arrencar el servei. La primera vegada pot trigar una mica més perquè descarrega la imatge i inicialitza la base de dades.

| | MySQL | PostgreSQL |
| --- | --- | --- |
| Imatge | `mysql:8.4` | `postgres:17` |
| Base de dades | `MYSQL_DATABASE` | `POSTGRES_DB` |
| Usuari | `MYSQL_USER` | `POSTGRES_USER` |
| Contrasenya | `MYSQL_PASSWORD` | `POSTGRES_PASSWORD` |
| Directori de dades | `/var/lib/mysql` | `/var/lib/postgresql/data` |
| URI de SQLAlchemy | `mysql+pymysql://...` | `postgresql+psycopg2://...` |

### 5.2 MySQL

Afegeix aquest servei i aquest volum al `docker-compose.yml`:

```yaml
services:
  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: root_pass
      MYSQL_DATABASE: my_app
      MYSQL_USER: my_app
      MYSQL_PASSWORD: my_app_pass
    ports:
      - "127.0.0.1:3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/database.sql:/docker-entrypoint-initdb.d/01-database.sql:ro

volumes:
  mysql_data:
```

- `MYSQL_ROOT_PASSWORD`: contrasenya del superusuari `root`. És obligatòria (o cal usar `MYSQL_RANDOM_ROOT_PASSWORD`).
- `MYSQL_DATABASE`: crea la base de dades `my_app`.
- `MYSQL_USER` i `MYSQL_PASSWORD`: creen un usuari normal amb tots els permisos sobre `my_app`. L'aplicació ha d'usar aquest usuari, no `root`.
- El volum `mysql_data` guarda les dades a `/var/lib/mysql`, de manera que sobreviuen a reinicis.
- El fitxer `./mysql/database.sql` es munta a `/docker-entrypoint-initdb.d/` i s'executa la primera vegada que el volum és buit.

> El projecte ja inclou `mysql/database.sql` amb les taules i les dades de prova. Si el teu projecte no el té, crea'l amb les sentències `CREATE TABLE` i `INSERT` que necessitis.

Amb l'aplicació Flask a l'ordinador, canvia el `.env`:

```dotenv
SQLALCHEMY_DATABASE_URI="mysql+pymysql://my_app:my_app_pass@127.0.0.1:3306/my_app"
```

El projecte ja té `PyMySQL` a `requirements.txt`. Reinicia Flask després de canviar el `.env`.

### 5.3 PostgreSQL

Afegeix aquest servei i aquest volum al `docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_DB: my_app
      POSTGRES_USER: my_app
      POSTGRES_PASSWORD: my_app_pass
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/database.sql:/docker-entrypoint-initdb.d/01-database.sql:ro

volumes:
  postgres_data:
```

- `POSTGRES_DB`: crea la base de dades `my_app`.
- `POSTGRES_USER` i `POSTGRES_PASSWORD`: creen l'usuari administrador de la instància i li assignen la contrasenya. Per a desenvolupament, l'aplicació pot usar aquest mateix usuari.
- El volum `postgres_data` guarda les dades a `/var/lib/postgresql/data`.
- El fitxer `./postgres/database.sql` s'executa la primera vegada que el volum és buit.

> El projecte ja inclou `postgres/database.sql` amb les taules i les dades de prova. Si fas servir `postgres:18` o posterior, el volum es munta a `/var/lib/postgresql` i les dades van a `/var/lib/postgresql/18/docker`; revisa la documentació de la imatge.

Amb l'aplicació Flask a l'ordinador, canvia el `.env`:

```dotenv
SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://my_app:my_app_pass@127.0.0.1:5432/my_app"
```

El projecte ja té `psycopg2-binary` a `requirements.txt`. Reinicia Flask després de canviar el `.env`.

### 5.4 Crear les taules automàticament

Els contenidors oficials de MySQL i PostgreSQL executen els fitxers que troben a `/docker-entrypoint-initdb.d/` **només la primera vegada**, quan el directori de dades és buit. Això permet crear l'esquema i carregar dades inicials sense entrar al contenidor.

- Els fitxers poden ser `.sql`, `.sql.gz` o `.sh`.
- S'executen en ordre alfabètic. Per això es numeren amb prefixos com `01-`, `02-`.
- En els exemples, el fitxer SQL es munta amb `:ro` perquè el contenidor no el pugui modificar.
- Si canvies el fitxer SQL, els canvis **no** s'apliquen sols: el script ja s'ha executat i el volum conté dades. Cal reinicialitzar la base de dades (apartat 5.5).
- Per a canvis d'esquema freqüents durant el desenvolupament, és més còmode fer servir migracions (per exemple, Flask-Migrate) que no reinicialitzar el volum cada vegada.

### 5.5 Reiniciar o reinicialitzar la base de dades

**Reiniciar el servei** sense perdre les dades:

```bash
docker compose restart db
```

També pots aturar-lo i tornar-lo a arrencar:

```bash
docker compose stop db
docker compose start db
```

**Reinicialitzar la base de dades des de zero**, és a dir, esborrar les dades i tornar a executar els scripts d'inicialització:

```bash
# Atura i elimina només el contenidor de la base de dades
docker compose rm -sf db

# Comprova el nom exacte del volum (porta el nom del projecte com a prefix)
docker volume ls

# Esborra el volum de dades (MySQL; per a PostgreSQL, canvia mysql_data per postgres_data)
docker volume rm 2daw-abp-p1-example_mysql_data

# Torna a crear el contenidor; els scripts s'executaran de nou
docker compose up -d db
```

> `docker compose down -v` també ho fa en una sola ordre, però elimina **tots** els contenidors i **tots** els volums amb nom del projecte. Fes-ho només en desenvolupament i comprova abans què hi ha.

**Comprovar que funciona:**

```bash
docker compose ps
docker compose logs -f db
```

**Entrar a la base de dades:**

```bash
# MySQL
docker compose exec db mysql -u my_app -p my_app

# PostgreSQL
docker compose exec db psql -U my_app -d my_app
```

A dins, comprova les taules amb `SHOW TABLES;` (MySQL) o `\dt` (PostgreSQL). La contrasenya és la que has posat a `MYSQL_PASSWORD` o `POSTGRES_PASSWORD`.

> Si el port 3306 o 5432 ja està ocupat per un altre servei, canvia el port de l'amfitrió: per exemple, `"127.0.0.1:3307:3306"` i connecta't al 3307.

---

## 6. Afegir l'aplicació Flask

Fins ara, el `docker-compose.yml` només aixeca serveis de suport (Mailpit i, si l'has afegida, una base de dades). També pots executar la pròpia aplicació Flask dins de Docker. En desenvolupament, el més pràctic és muntar el codi amb un **volum** (*bind mount*) i deixar que la imatge només aporti Python i les dependències: així els canvis es veuen sense reconstruir la imatge.

> Aquesta secció és opcional. Si prefereixes executar Flask a l'ordinador amb `flask run --debug` i fer servir Docker només per a Mailpit o la base de dades, no cal fer res del que hi ha a continuació.

### 6.1 Crear el Dockerfile

A l'arrel del projecte, crea un fitxer `Dockerfile` amb aquest contingut:

```dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
```

Què fa cada part:

- `FROM python:3.13-slim`: imatge base lleugera de Python 3.13, la mateixa versió que fa servir el projecte.
- `ENV`: evita generar fitxers `.pyc`, fa que els logs surtin sense buffering i indica a Flask quin és el fitxer d'entrada.
- `WORKDIR /app`: fixa el directori de treball dins del contenidor.
- `COPY requirements.txt .` i `RUN pip install`: instal·la les dependències abans de muntar el codi, per aprofitar la memòria cau de capes de Docker. Així, si només canvies el codi, no es tornen a instal·lar les dependències.
- `EXPOSE 5000`: documenta el port que escolta l'aplicació; la publicació real es fa amb `ports` al Compose.
- `CMD`: arrenca Flask escoltant a `0.0.0.0`, necessari perquè el port sigui accessible des de fora del contenidor.

Fixa't que **no hi ha cap `COPY . .`**: el codi de l'aplicació no es copia a la imatge. L'única cosa que es copia és `requirements.txt`, per poder instal·lar les dependències; el codi va pel volum. En arrencar el contenidor, es munta des de l'ordinador amb un volum. Així la imatge només conté Python i les dependències, i els canvis de codi són immediats.

El `CMD` executa el servidor de desenvolupament de Flask. Per a producció, canvia'l per un servidor WSGI com Gunicorn, crea un usuari sense privilegis i no facis servir `--debug`.

### 6.2 Afegir el servei `app` al Compose

Un exemple complet de `docker-compose.yml` amb l'aplicació i Mailpit, fent servir SQLite i un *bind mount* per al codi:

```yaml
services:
  app:
    build: .
    restart: unless-stopped
    ports:
      - "127.0.0.1:5000:5000"
    env_file:
      - .env
    environment:
      MAIL_SMTP_SERVER: mailpit
      MAIL_SMTP_PORT: 1025
      SQLALCHEMY_DATABASE_URI: sqlite:////app/sqlite/database.db
    volumes:
      - .:/app
    command: flask run --host=0.0.0.0 --port=5000 --debug
    depends_on:
      - mailpit

  mailpit:
    image: axllent/mailpit
    ports:
      - "127.0.0.1:8025:8025"
      - "127.0.0.1:1025:1025"
```

- `build: .`: construeix la imatge de l'aplicació amb el `Dockerfile` de l'arrel. La imatge només instal·la les dependències.
- `ports`: publica el port 5000 del contenidor a `127.0.0.1:5000` de l'ordinador.
- `env_file: .env`: carrega la configuració de l'aplicació. Si encara no tens el `.env`, copia `.env.exemple` a `.env` i ajusta els valors.
- `environment`: sobreescriu els valors que calen dins de la xarxa de Compose.
- `volumes`: munta el projecte de l'ordinador a `/app` del contenidor. És un *bind mount*, no un volum amb nom com els de MySQL o PostgreSQL. El codi, les plantilles, els fitxers estàtics i la base de dades SQLite surten d'aquí.
- `command`: arrenca Flask amb `--debug` perquè el servidor es reiniciï automàticament quan canvia el codi.
- `depends_on`: fa que Mailpit arrenqui abans que l'aplicació.

`MAIL_SMTP_SERVER: mailpit` és imprescindible: dins de Compose, `127.0.0.1` seria el mateix contenidor de l'aplicació, no l'ordinador on corre Mailpit. Per això es fa servir el nom del servei (`mailpit`) i el port intern (`1025`). La clau `environment` té prioritat sobre el valor equivalent del `.env`.

Com que el codi es munta amb `.:/app` (un *bind mount*), els canvis que facis a l'ordinador es veuen de seguida al contenidor. No cal reconstruir la imatge per canviar codi; només cal fer-ho si canvies `requirements.txt` o el `Dockerfile`.

Si `sqlite/database.db` no existeix, copia `sqlite/database.db.initial` a `sqlite/database.db` o crea la base de dades amb `sqlite/database.sql`.

### 6.3 Fer servir MySQL o PostgreSQL

Si has afegit una base de dades de la secció 5, canvia la URI i afegeix el servei `db` a `depends_on`. Aquests fragments substitueixen les claus `environment` i `depends_on` del servei `app`. Per a MySQL:

```yaml
    environment:
      MAIL_SMTP_SERVER: mailpit
      MAIL_SMTP_PORT: 1025
      SQLALCHEMY_DATABASE_URI: mysql+pymysql://my_app:my_app_pass@db:3306/my_app
    depends_on:
      - db
      - mailpit
```

Per a PostgreSQL, només canvia la URI:

```yaml
      SQLALCHEMY_DATABASE_URI: postgresql+psycopg2://my_app:my_app_pass@db:5432/my_app
```

El host `db` és el nom del servei de base de dades dins de la xarxa de Compose. No facis servir `127.0.0.1` per a la base de dades ni per a Mailpit dins del contenidor de l'aplicació.

> No posis `db` al `.env`: si també executes Flask a l'ordinador, allí `db` no existeix. Fes el canvi només a la secció `environment` del servei `app`.

`depends_on` només ordena l'arrencada; no espera que la base de dades estigui llesta per acceptar connexions. Si l'aplicació falla just després d'arrencar, espera uns segons i torna-ho a provar; per a entorns més exigents, afegeix un `healthcheck` al servei `db`.

### 6.4 Construir i arrencar

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f app
```

Obre [http://127.0.0.1:5000](http://127.0.0.1:5000). La primera vegada es descarrega la imatge base i s'instal·len les dependències; pot trigar una mica. Com que el codi es munta amb un *bind mount*, els canvis posteriors no requereixen reconstruir la imatge.

Quan canvies `requirements.txt` o el `Dockerfile`, sí que cal reconstruir: `docker compose up -d --build`.

Per aturar-ho, executa `docker compose down`.

> Si el port 5000 ja està ocupat, canvia el port de l'amfitrió: per exemple, `"127.0.0.1:5001:5000"`, i obre `http://127.0.0.1:5001`.

### 6.5 Imatge autònoma (sense volum)

Aquest muntatge és molt còmode per desenvolupar, però la imatge resultant no conté el codi: depèn de la carpeta del projecte. Si vols una imatge que es pugui executar tota sola (per exemple, per publicar-la en un registre), afegeix `COPY . .` al `Dockerfile` després de `RUN pip install` i elimina el muntatge `.:/app` i la línia `command` del servei `app`. La part final del Dockerfile quedaria així:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
```

En aquest cas, el `.dockerignore` és important (apartat 6.6) perquè el context de build no inclogui `.env`, `.venv`, claus, etc. Si uses SQLite, encara necessites un volum per a `./sqlite` si vols conservar les dades; si uses MySQL o PostgreSQL, les dades són al volum de la base de dades.

| | Bind mount (desenvolupament) | `COPY` (imatge autònoma) |
| --- | --- | --- |
| Codi | Muntat des de l'ordinador | Dins de la imatge |
| Canvis de codi | Immediats | Cal reconstruir |
| Mida de la imatge | Només dependències | Codi i dependències |
| Portabilitat | Depèn de la carpeta | Alta |
| Ús recomanat | Desenvolupament | Producció o CI |

> Per a producció, canvia el `CMD` per Gunicorn, crea un usuari sense privilegis i no facis servir `--debug`.

### 6.6 Crear el `.dockerignore`

Al costat del `Dockerfile`, crea un fitxer `.dockerignore`:

```text
.venv
__pycache__
*.pyc
.git
.env
sqlite/database.db
```

En la configuració de desenvolupament no fem `COPY . .`, així que el `.dockerignore` té menys impacte; tot i això, és important si vols construir una imatge autònoma (apartat 6.5). Evita enviar al dimoni de Docker el virtualenv, les carpetes `__pycache__`, el repositori Git, el fitxer `.env` i la base de dades SQLite local.

Recorda que el `.dockerignore` només afecta el build de la imatge: el muntatge `.:/app` de l'apartat 6.2 munta tota la carpeta del projecte, incloent-hi fitxers que el `.dockerignore` exclouria.

---

## 7. Resum de comandes

| Objectiu | Comanda |
| --- | --- |
| Comprovar la instal·lació | `docker --version` · `docker compose version` |
| Prova bàsica | `docker run --rm hello-world` |
| Descarregar imatges del projecte | `docker compose pull` |
| Arrencar en segon pla | `docker compose up -d` |
| Reconstruir la imatge de l'aplicació i arrencar | `docker compose up -d --build` |
| Veure estat | `docker compose ps` |
| Veure logs en directe | `docker compose logs -f [servei]` |
| Aturar sense eliminar | `docker compose stop` |
| Tornar a arrencar | `docker compose start` |
| Reiniciar | `docker compose restart` |
| Reiniciar el contenidor de base de dades | `docker compose restart db` |
| Aturar i eliminar | `docker compose down` |
| Validar el YAML | `docker compose config` |
| Llistar contenidors actius | `docker ps` |
| Llistar totes les imatges | `docker images` |
| Eliminar un contenidor | `docker rm -f <nom>` |
| Eliminar una imatge | `docker rmi <imatge>` |
| Netejar recursos no usats | `docker system prune` |

> Per reinicialitzar la base de dades des de zero, consulta l'apartat 5.5.

---

## Enllaços

- [Documentació oficial de Docker](https://docs.docker.com/)
- [Instal·lació de Docker Engine](https://docs.docker.com/engine/install/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Referència del fitxer Compose](https://docs.docker.com/compose/compose-file/)
- [Mailpit](https://mailpit.axllent.org/)
- [Docker Hub: axllent/mailpit](https://hub.docker.com/r/axllent/mailpit)
