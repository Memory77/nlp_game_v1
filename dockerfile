# Utiliser une image Python comme base
FROM python:3.8-slim

# Installer les dépendances système nécessaires pour pygame.mixer et PulseAudio
RUN apt-get update && apt-get install -y \
    libasound2-dev \
    libglib2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-2.0-0 \
    alsa-utils \
    pulseaudio \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances et installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . /app

# Exposer le port sur lequel l'application va fonctionner
EXPOSE 8000

# Définir les variables d'environnement pour SDL et X11
ENV SDL_AUDIODRIVER=pulseaudio
ENV AUDIODEV=hw:0,0
ENV DISPLAY=:0
ENV PULSE_SERVER=unix:/run/pulse/native

# Définir la commande par défaut pour exécuter l'application
CMD ["python", "triv_poursuit.py"]
