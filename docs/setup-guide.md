# Setup Guide --- AI Inventory Tracker

This guide explains how to recreate the AI Inventory Tracker using AWS.

## Prerequisites

- AWS account
- Node.js installed
- npm installed
- Git installed

## Step 1 --- Create DynamoDB Table

AWS Console → DynamoDB → Create Table

Configuration:

Table Name: InventoryItems Partition Key: itemId Capacity Mode: 
On-demand

## Step 2 --- Create Lambda Function

AWS Console → Lambda → Create Function

Configuration:

Function Name: inventory-handler Runtime: Python 3.14

Attach IAM permissions:

AmazonDynamoDBFullAccess AmazonBedrockFullAccess AmazonSNSFullAccess

## Step 3 --- Add Environment Variables

TABLE_NAME = InventoryItems MODEL_ID = amazon.nova-lite-v1:0 
SNS_TOPIC_ARN = arn:aws:sns:REGION:ACCOUNT_ID:inventory-alerts

## Step 4 --- Deploy Lambda Code

Upload the inventory_handler.py file containing the Lambda function.

## Step 5 --- Create API Gateway

API Gateway → Create API

Choose HTTP API

Add routes:

POST /items GET /items PUT /items/{itemId} DELETE /items/{itemId} POST 
/inventory-summary

Integrate all routes with the inventory-handler Lambda and enable 
CORS.

## Step 6 --- Create SNS Topic

SNS → Topics → Create Topic

Topic name: inventory-alerts

Create subscription:

Protocol: Email Endpoint: your email

Confirm subscription via email.

## Step 7 --- Configure EventBridge Scheduler

EventBridge Scheduler → Create Schedule

Schedule expression:

rate(1 day)

Target:

Lambda → inventory-handler

## Step 8 --- Create Frontend

Create React app:

npm create vite@latest inventory-dashboard

Install dependencies:

npm install

Configure API base URL in App.jsx.

## Step 9 --- Deploy Frontend

Build project:

npm run build

Deploy to:

AWS Amplify → New App → Deploy without Git

Upload the contents of the dist/ folder.

## Step 10 --- Test Application

Verify the following:

- Add inventory item
- Update item quantity
- Delete item
- Generate AI inventory summary
- Receive daily SNS email report

## Final Result

You now have a fully serverless AI-powered inventory management system 
running on AWS.

