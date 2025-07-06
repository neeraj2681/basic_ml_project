#pushing docker image to public ECR repository

#set the AWS region
AWS_REGION="us-east-1"

#set the ECR repository name
ECR_REPOSITORY_NAME="ml_testing/ml_testingv1"

#set the image name
IMAGE_NAME="basic-ml-app"

#set the image tag
IMAGE_TAG="latest"

#creating a new tag for the image - for public ECR repository
docker tag ${IMAGE_NAME}:${IMAGE_TAG} public.ecr.aws/i2n7c7b4/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}

#login to the ECR repository
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/i2n7c7b4


#push the image to the ECR repository
docker push public.ecr.aws/i2n7c7b4/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}