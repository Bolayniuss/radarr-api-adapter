FROM python:3.8-slim

WORKDIR /app

EXPOSE 7879


ARG BUILD_COMMIT_SHA1
ARG BUILD_COMMIT_DATE
ARG BUILD_BRANCH
ARG BUILD_DATE
ARG BUILD_REPO_ORIGIN

ENV BUILD_COMMIT_SHA1=$BUILD_COMMIT_SHA1
ENV BUILD_COMMIT_DATE=$BUILD_COMMIT_DATE
ENV BUILD_BRANCH=$BUILD_BRANCH
ENV BUILD_DATE=$BUILD_DATE
ENV BUILD_REPO_ORIGIN=$BUILD_REPO_ORIGIN



ADD ./requirements.txt /app/requirements.txt

RUN \
   pip install -U pip \
&& pip install -r /app/requirements.txt

#
# Add local scripts
#
ADD ./src /app
#ADD ./.env /app/.env

# I specified this file as entrypoint, CMD will be arguments passed in the file which can be overriden in Kuberenetes or CLI docker
ENTRYPOINT ["python", "app.py", "7879"]

