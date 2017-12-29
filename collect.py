import boto3
import os
from botocore.vendored import requests
import calendar
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')

logger.info('Loading function')
dynamo = boto3.client('dynamodb')

TABLE_NAME = os.environ['TABLE_NAME']

def insert(json, timestamp):
    # dynamo db insert logic
    response = dynamo.put_item(TableName=TABLE_NAME,
                               Item={
                                   'CoinId': {"S": str(json['symbol'])},
                                   'Price': {"N": str(json['price_usd'])},
                                   'TimeStamp': {"N": str(timestamp)},
                                   'Name': {"S": str(json['name'])},
                                   'Rank': {"N": str(json['rank'])},
                                   'PriceBTC': {"S": str(json['price_btc'])},
                                   '24hVolumeUSD': {"S": str(json['24h_volume_usd'])},
                                   'MarketCapUSD': {"S": str(json['market_cap_usd'])},
                                   'AvailableSupply': {"S": str(json['available_supply'])},
                                   'TotalSupply': {"S": str(json['total_supply'])},
                                   'MaxSupply': {"S": str(json['max_supply'])},
                                   'PctChange1hr': {"S": str(json['percent_change_1h'])},
                                   'PctChange24hr': {"S": str(json['percent_change_24h'])},
                                   'PctChange7d': {"S": str(json['percent_change_7d'])}
                               }
                            )

def lambda_handler(event, context):
    all_current_prices = requests.get("https://api.coinmarketcap.com/v1/ticker/?limit=200").json()
    timestamp = calendar.timegm(time.gmtime())
    counter = 0

    for price in all_current_prices:
        counter += 1
        logger.info("Starting %s" % price['name'])
        insert(price, timestamp)

    return "Successfully inserted {} coins.".format(counter)