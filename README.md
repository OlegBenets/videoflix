
# Videoflix Backend

Backend for the video streaming platform **Videoflix**. Provides server logic, API endpoints, and video processing for a modern streaming application.

---
## Contents

- Project Overview  
- Key Features  
- Technologies Used  
- Installation & Setup  
- Development  
- Production & Deployment  
- Testing  
- Configuration & Environment Variables  
- Video Upload & HLS Conversion  

---

## Project Overview

The **Videoflix Backend** is the server component of a video platform. It allows uploading, managing, and serving videos in various resolutions and formats. Frontend applications can access content via a REST API.

---

## Key Features

- User registration, login, and authentication (JWT or sessions)  
- Video upload with automatic processing: HLS streams, thumbnails, transcoding  
- Background tasks using **Redis** and **django-rq**  
- Storage of videos, thumbnails, and HLS segments  
- Management of categories, watchlists, and viewing history  
- Docker support for easy installation and deployment  

---

## Technologies Used

- **Python & Django** – backend framework  
- **Django REST Framework** – API endpoints  
- **Redis + RQ / django-rq** – asynchronous processing  
- **FFmpeg** – video conversion and HLS generation  
- **PostgreSQL** – database  
- **Docker & docker-compose** – containerization and deployment  

---

## Installation & Setup

### Requirements

- Python 3.x  
- PostgreSQL  
- Redis  
- FFmpeg  
- Docker & docker-compose (optional, recommended)  

### Step-by-Step (Local Development)

1. Clone the repository:

```bash
git clone https://github.com/OlegBenets/videoflix.git
cd videoflix

2. Create environment file:

```bash
cp .env.template .env
# Passe .env an: SECRET_KEY, DATABASE_URL, REDIS_URL, ALLOWED_HOSTS etc.
```

3. Create and activate a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start with Docker (optional):

```bash
docker-compose up --build
```

6. Apply migrations:

```bash
docker-compose exec web python manage.py migrate
```

7. Create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Development

- Code changes can be tested directly in Docker or the local virtual environment. 
- Background jobs (video conversion) run via **RQ Worker**.  

---

## Production & Deployment

- Uses Docker for consistent environments 
- Gunicorn as the WSGI server
- Optional reverse proxy (e.g., Nginx) for static files
---

## Testing

- Django tests can be run with `python manage.py test`.
- Background tasks should be tested separately in a development environment. 

---

## Configuration & Environment Variables

Important variables in `.env`:

- `SECRET_KEY` – Django secret key  
- `DATABASE_URL` – PostgreSQL connection string  
- `REDIS_URL` – Redis connection string  
- `ALLOWED_HOSTS` – List of allowed hosts  

---

## Video Upload & HLS Conversion

1. Videos can be uploaded via the Django admin interface.  
2. After uploading, **RQ workers** automatically start background processing:  
   - Generation of thumbnails  
   - Conversion to HLS streams (different resolutions: 480p, 720p, 1080p)  
3. All generated files are stored under `media/videos/<video_id>/<resolution>/`.  
4. The API then provides URLs for the frontend so that videos can be streamed directly via HLS.

---

