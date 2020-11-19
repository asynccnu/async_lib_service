# base image
FROM python:3.6
# environment setting
ENV DEPLOY_PATH /lib_api
# run command in container
RUN mkdir -p $DEPLOY_PATH
WORKDIR $DEPLOY_PATH
# first add files to container
ADD . .
# install
RUN pip install --index-url http://pypi.doubanio.com/simple/ -r requirements.txt --trusted-host=pypi.doubanio.com
