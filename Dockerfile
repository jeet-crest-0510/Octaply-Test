FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg curl unzip wget xvfb \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils lsb-release && \
    rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install NVM and Node.js v22.9.0
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash \
    && export NVM_DIR="$HOME/.nvm" \
    && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" \
    && nvm install 22.9.0 \
    && nvm alias default 22.9.0 \
    && nvm use default \
    && npm install -g npm@latest

# Add Node/NPM to PATH for all future shells
ENV NODE_VERSION=22.9.0
ENV PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH"

WORKDIR /app/airtop_module
RUN npm install

WORKDIR /app

EXPOSE 80
CMD ["python", "auto_apply.py"]