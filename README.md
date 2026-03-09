# AI Inventory Tracker (AWS Serverless Capstone)

## Overview

An AI-powered inventory management system built using a fully serverless 
AWS architecture. The application allows users to track inventory items, 
detect low-stock conditions, generate AI-driven insights, and automate 
daily inventory health reports.

## Live Demo

Frontend hosted with AWS Amplify  

https://staging.d3o3t6xcji7yyp.amplifyapp.com/

## Features

### Inventory Management

- Add inventory items
- Update quantities
- Delete items
- Track inventory categories

### Low Stock Detection

- Automatically highlights items below reorder threshold

### AI Inventory Insights

- Uses Amazon Bedrock to generate inventory health summaries
- Identifies items that may require restocking

### Automated Reports

- EventBridge Scheduler triggers daily inventory analysis
- SNS sends inventory health alerts via email
  
## Tech Stack
### Frontend

- React
- Vite
- AWS Amplify Hosting

### Backend

- AWS Lambda
- API Gateway
- DynamoDB

### AI

- Amazon Bedrock

### Automation

- EventBridge Scheduler
- SNS notifications

## Example Inventory Item

```
{ "itemId": "uuid", "name": "USB-C Charger", "category": "Electronics", 
"quantity": 8, "reorderThreshold": 3, "lastUpdated": 
"2026-03-09T18:21:00Z" }
```

## API Endpoints

```
POST /items GET /items PUT /items/{itemId} DELETE /items/{itemId} POST 
/inventory-summary
```

## Example AI Inventory Summary

```
Inventory Health Report

• 2 items are currently below reorder threshold • Electronics 
accessories category is trending low • Recommend restocking USB-C 
chargers
```

## Key Learning Outcomes

This project demonstrates:

- Serverless architecture design
- API development with API Gateway
- Event-driven automation with EventBridge
- AI integration with Amazon Bedrock
- DynamoDB data modeling
- Full-stack cloud application development
