@echo off
echo Starting Student Management System Deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo Docker Compose is not installed.
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "backend\logs" mkdir "backend\logs"
if not exist "backend\media" mkdir "backend\media"
if not exist "backend\staticfiles" mkdir "backend\staticfiles"

REM Create .env file if not exists
if not exist ".env" (
    echo Creating environment file...
    (
        echo # Database Configuration
        echo DB_PASSWORD=1997yx0912
        echo DB_NAME=DataSystem
        echo DB_USER=root
        echo DB_HOST=db
        echo DB_PORT=3306
        echo.
        echo # Django Configuration
        echo SECRET_KEY=django-secret-key-for-student-management-system-2024
        echo DEBUG=False
        echo ALLOWED_HOSTS=localhost,127.0.0.1,backend,frontend
        echo.
        echo # Security Configuration
        echo CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
    ) > .env
    echo Environment file created successfully.
)

REM Stop existing containers
echo Stopping existing containers...
docker-compose down

REM Build and start services
echo Building Docker images...
docker-compose build --no-cache

echo Starting database services...
docker-compose up -d db redis

REM Wait for database to start
echo Waiting for database to start...
timeout /t 30 /nobreak >nul

REM Run database migrations
echo Running database migrations...
docker-compose run --rm backend python manage.py makemigrations
docker-compose run --rm backend python manage.py migrate

REM Ask to create superuser
echo Do you want to create a Django superuser? (y/n)
set /p create_superuser=
if /i "%create_superuser%"=="y" (
    docker-compose run --rm backend python manage.py createsuperuser
)

REM Start all services
echo Starting all services...
docker-compose up -d

REM Wait for services to start
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

REM Check service status
echo Checking service status...
docker-compose ps

echo.
echo Deployment completed!
echo Frontend: http://localhost
echo Admin Panel: http://localhost/api/admin/
echo View Logs: docker-compose logs -f
echo Stop Services: docker-compose down
echo.
pause 