# Srija Biswas Portfolio CMS

A responsive portfolio and content-management system built with Django, MongoEngine, MongoDB Atlas, and SQLite. It provides a public portfolio website and a custom administration workspace for managing profile information, page content, projects, skills, blogs, resumes, and contact submissions.

## Features

### Public website

- Responsive light and dark themes with saved user preference
- Home, About, Skills, Projects, Blog, Resume, and Contact pages
- Dynamic profile and social links
- Project and blog search
- Blog categories and tags
- Links to articles published on Medium, Blogger, and other platforms
- Custom PDF resume viewer powered by PDF.js
- Active/inactive content visibility controls
- Responsive navigation, cards, forms, animations, and accessibility states

### Content-management panel

- Custom authenticated admin dashboard
- Profile, social-link, image, and resume management
- Editable Home, About, and Contact page content
- Education, experience, achievement, interest, value, and research management
- Project and skill management
- Internal blog editor with rich-text content
- Blog categories with active/inactive controls
- External Medium/Blogger article management
- Multiple PDF resumes with one active resume at a time
- Contact-submission inbox and bulk actions

## Technology stack

- Python 3.10.13
- Django 4.2.7
- MongoDB Atlas
- MongoEngine 0.29.1
- SQLite
- Tailwind CSS through CDN
- Custom CSS and vanilla JavaScript
- Quill rich-text editor
- Mozilla PDF.js
- WhiteNoise
- Gunicorn
- Render deployment configuration

## Data architecture

The application uses two databases:

| Storage | Purpose |
| --- | --- |
| SQLite | Django users, superusers, authentication, sessions, and permissions |
| MongoDB | Portfolio profile, pages, skills, projects, blogs, categories, resumes, and contact submissions |

MongoEngine documents do not use Django migrations. MongoDB collections and new document fields are created when records are saved. Django migrations are still required for SQLite authentication and session tables.

Profile pictures, internal blog cover images, and resume PDFs are stored as binary data in MongoDB so they survive Render deployments. Some older project/media fields still use Django filesystem storage.

## Project structure

```text
portfolio-cms/
├── apps/
│   ├── accounts/          # Login and logout
│   ├── admin_panel/       # Custom CMS views, routes, and forms
│   └── public/            # Public pages and MongoEngine documents
├── portfolio_project/     # Django settings and root URLs
├── scripts/               # Deployment superuser helper
├── static/
│   ├── css/
│   ├── images/
│   └── js/
├── templates/
│   ├── admin/
│   └── public/
├── manage.py
├── requirements.txt
├── render.yaml
└── runtime.txt
```

## Requirements

- Python 3.10
- pip
- MongoDB Atlas cluster or another reachable MongoDB deployment
- Git, if cloning from GitHub
- Internet access for CDN-hosted frontend dependencies

Python 3.10 is recommended because the project pins packages designed for that runtime. Avoid using the system's Python 3.14 interpreter for this environment.

## Local installation

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/srijabiswas-01/portfolio-cms.git
cd portfolio-cms
```

Create a Python 3.10 virtual environment on Windows:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Environment configuration

Create a `.env` file in the project root. Do not commit this file.

```dotenv
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER.mongodb.net/portfolio_db?retryWrites=true&w=majority
DATABASE_NAME=portfolio_db
SKIP_MONGO_CONNECT=False

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=replace-with-a-strong-password
```

For MongoDB Atlas, add your current public IP address under **Security → Network Access** and ensure the configured database user has access to the selected database.

## Initialize the application

Create the SQLite tables:

```powershell
python manage.py migrate
```

Create a superuser interactively:

```powershell
python manage.py createsuperuser
```

Alternatively, create or update the superuser using the configured environment variables:

```powershell
python scripts/create_superuser.py
```

Start the development server:

```powershell
python manage.py runserver
```

Open the application:

| Page | Local URL |
| --- | --- |
| Public website | <http://127.0.0.1:8000/> |
| CMS login | <http://127.0.0.1:8000/accounts/login/> |
| CMS dashboard | <http://127.0.0.1:8000/admin/dashboard/> |
| Django admin | <http://127.0.0.1:8000/django-admin/> |
| Health check | <http://127.0.0.1:8000/healthz> |

## CMS workflows

### Publishing an internal blog

1. Open **Admin → Blogs**.
2. Create or activate a blog category.
3. Select **New Blog Post**.
4. Enter the title, content, summary, tags, category, read time, and cover image.
5. Select **Published** and enable the public visibility checkbox.
6. Save the post.

A public blog must be both **Published** and **Active**. A post assigned to an inactive category is also hidden from the public website.

### Adding Medium or Blogger articles

Use the external-article form under **Admin → Blogs**. Provide the original article URL, platform, title, summary, publication date, and an optional direct cover-image URL. Only active external articles appear publicly.

### Managing resumes

1. Open **Admin → Profile**.
2. Upload one or more PDF files.
3. Mark one resume as active.
4. View, deactivate, or permanently delete individual resume records.

Only one resume can be active at a time. If no resume is active, the public Resume navigation link and About-page download button are hidden.

Resume uploads must:

- Use the `.pdf` extension
- Have the `application/pdf` content type
- Contain a valid PDF signature
- Be 10 MB or smaller

### Blog cover images

Internal blog cover images are limited to 5 MB and stored inside the blog's MongoDB document. Uploading a replacement overwrites the existing binary image. Deleting the blog also deletes its cover data.

## Running checks

Run Django's system checks:

```powershell
python manage.py check
```

Run the available tests:

```powershell
python manage.py test
```

## Deploying to Render

The repository includes `render.yaml`, `Procfile`, and `runtime.txt`.

Configure these environment variables in the Render service:

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com,your-custom-domain.com`
- `MONGODB_URI`
- `DATABASE_NAME`
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`
- `PYTHON_VERSION=3.10.13`

The configured build process installs dependencies, runs SQLite migrations, creates the configured superuser, and collects static files. Gunicorn starts the Django WSGI application.

After deployment, upload profile images, blog covers, and resumes using the hosted CMS so the latest MongoDB documents contain the required binary data.

## Important Render limitation

Render's default filesystem is ephemeral. Files written to local storage can disappear after restarts or deployments. This project avoids that problem for profile images, internal blog covers, and resume PDFs by storing them in MongoDB. Any feature that still uses local media storage should be migrated to database or cloud-object storage before relying on it in production.

## Security

- Never commit `.env`, database passwords, Django secret keys, or administrator passwords.
- Rotate any credential that has previously appeared in Git history, screenshots, logs, or chat messages.
- Use `DEBUG=False` in production.
- Restrict MongoDB Atlas Network Access instead of allowing all addresses when possible.
- Use strong, unique administrator credentials.
- Review uploaded content and file-size limits before expanding public upload functionality.

## License

No license is currently included. Add a license file before distributing or accepting external contributions.
