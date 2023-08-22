FROM node:18.17.1

# Create app directory
WORKDIR /app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./
RUN npm ci

# compile project
COPY tsconfig.json ./
COPY src ./src
RUN npm run-script build

# non-root user
ARG USER_UID=1001
ARG USER_GID=$USER_UID
RUN addgroup --gid ${USER_GID} app
RUN adduser app --home /app --uid ${USER_UID} --gid ${USER_GID} --no-create-home --disabled-password
# resolve cache issue
RUN chown -R ${USER_GID}:${USER_UID} /app/
USER ${USER_UID}

CMD ["npm", "run-script", "start"]