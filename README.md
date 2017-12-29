# Cryptomonitor

This application was built for the AWS Serverless Repository. The application serves two purposes. 1) Collects prices for the top 200 coins according to market cap, every 5 minutes. 2) Alert the user if their coins have increased in price.

## Getting Started

Please refer to the AWS Serverless repository, found [here.](https://aws.amazon.com/serverless/serverlessrepo/).

Please be aware that the following services will be used:
* Two AWS Lambda functions:
	* alert.py - check if the price has changed significantly over the past 10 observations.
	* collect.py - use coinmarketcap to get the current price of the top 200 cryptocurrencies.
* DynamoDB table to store the prices every 5 minutes
* AWS Simple Notification Service to send an SMS to the user’s phone number.


## To Deploy

I run the following commands, assuming the AWS CLI is configured:

* aws cloudformation package --template-file cloudformation.yaml --output-template-file serverless-output.yaml --s3-bucket <<S3BucketName>>
* aws cloudformation deploy --template-file serverless-output.yaml --stack-name cryptomonitor --capabilities CAPABILITY_IAM --parameter-overrides=PhoneNumber=<<YOURPHONENUMBER>>

This can also be deployed using the AWS Serverless Repository.
