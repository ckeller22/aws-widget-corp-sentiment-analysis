# AWS Widget Corp Sentiment Analysis

This service uses a machine learning model to perform sentiment analysis on text data, specifically movie reviews. It is implemented as a serverless function in AWS Lambda using the Serverless Framework. It will determine the sentiment of a movie review, either positive or negative. 

## Prerequisites

- Node.js and npm
- Python 3.11
- Serverless Framework
-  Docker `*` if not using Linux

## Setup

1. Install the Serverless Framework and sign in with AWS provider:

    ```bash
    npm install -g serverless
    serverless login
    ```

    > Feel free to connect with your AWS credentials another way. I just utlized Serverless's recommended defaults as this not necessarily production ready.

2. Install the project dependencies:

    ```bash
    npm install
    pip install -r requirements.txt
    ```

3. Create an `assets` directory in the root of the project and add your model.

    > Feel free to download my model here: TODO: URL

4. Ensure following variables are set in your serverless.yml to your match your own:

```bash
    AWS_S3_BUCKET_NAME: your-unique-bucket-name-${self:provider.stage}
    AWS_MODEL_FILE_NAME: your-ml-model.pickle
```

## Deployment

To deploy the service to AWS, run:

```bash
serverless deploy
```

Note that this will sync all files that are contained in the assets directory to the S3 Bucket that you declared. If files have not changed since last time, sync will not occur. To prevent syncing manually, pass `--nos3sync` as an argument.

After deployment, you should see output similar to:
```bash
Deploying sentiment-analysis-service to stage dev (us-east-1)
✔ Service deployed to stack sentiment-analysis-service-dev (112s)
functions:
  analyze: sentiment-analysis-service-dev-analyze (1.5 kB)
```
### Invocation

After successful deployment, you can invoke the deployed function by using the following command or by creating a test in the AWS console with sample review data:

```bash
serverless invoke --function analyze --data '{"review": "I absolutely love this movie!"}'
```
You can also define a path to a JSON file:

```bash
serverless invoke --function analyze --path assets/data.json
```

All of which should result in response similar to the following:

```json
{
    "statusCode": 200,
    "body": {
        "sentiment": "pos"
    }
}
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function analyze --data '{"review": "I love this product!"}'
```