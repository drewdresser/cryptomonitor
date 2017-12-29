import boto3
import os
from botocore.vendored import requests
from boto3.dynamodb.conditions import Key, Attr
import calendar
import time
from decimal import Decimal
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info('Loading function')
dynamo = boto3.client('dynamodb')

SNS_TOPIC = os.environ['SNS_TOPIC']
PHONE_NUMBER = os.environ['PHONE_NUMBER']
PCT_CHANGE_CUTOFF = os.environ['PCT_CHANGE_CUTOFF']
COIN_LIST = os.environ['COIN_LIST']
TABLE_NAME = os.environ['TABLE_NAME']

sns_topic = boto3.resource('sns').Topic(SNS_TOPIC)


def get_coins(string_list):
    coin_list = string_list.split(",")
    return coin_list

def dynamo_response_to_list(response):
    prices = []
    for item in response['Items']:
        new_obj = {'CoinId': item['CoinId']['S'],
                   'Price': Decimal(item['Price']['N']),
                   'TimeStamp': int(item['TimeStamp']['N'])
                   }
        prices.append(new_obj.copy())
    return prices

def get_prices(coin, now):
    tminus1hr = now - 3600

    response = dynamo.query(TableName=TABLE_NAME,
                            KeyConditionExpression="CoinId = :Coin AND #TS > :SortKey",
                            ExpressionAttributeValues={":Coin": {"S": coin},
                                                       ":SortKey": {"N": str(tminus1hr)}},
                            ExpressionAttributeNames={"#TS": "TimeStamp"}
                            )

    return dynamo_response_to_list(response)

def notify_user(big_changes):
    message = "\n"

    for big_change in big_changes:
        message += "{0} changed {1:.3g} percent, the new price is ${2:.4}".format(
            big_change["symbol"],
            big_change["pct_change"],
            big_change["new_price"])
        message += "   \n"
    logger.info("Sending message: ".format(message))
    sns_topic.publish(Message=message)

def get_price_change(coin, prices, percentage_change_cutoff):

    if len(prices) < 2:
        logger.info("Not enough recent data for %s to determine there was a significant price change." % coin)
        return {}

    sorted_prices = sorted(prices, key=lambda k: k['TimeStamp'], reverse=True)

    current_price_obj = sorted_prices[0]
    old_price_objs = sorted_prices[:10]

    for old_price_obj in old_price_objs:
        current_price = current_price_obj['Price']
        old_price = old_price_obj['Price']

        pct_change = ((current_price - old_price) / old_price) * 100

        logger.info("CP: %d \t OP: %d \t Pct: %d" % (current_price, old_price, pct_change))

        if abs(pct_change) > Decimal(percentage_change_cutoff):
            logger.info("Percent price change was big enough for %s" % coin)
            return {"symbol": coin, "pct_change": pct_change, "new_price": current_price}

        logger.info("Percent change wasn't big enough for %s." % coin)
    return {}

def lambda_handler(event, context):
    timestamp = calendar.timegm(time.gmtime())
    big_changes = []

    coins = get_coins(COIN_LIST)

    for coin in coins:
        logger.info("Starting %s" % coin)
        prices = get_prices(coin, timestamp)
        big_change = get_price_change(coin, prices, PCT_CHANGE_CUTOFF)

        if big_change:
            logger.info("Adding big change for %s " % coin)
            logger.info(big_change)
            big_changes.append(big_change)
    logger.info("Big changes:")
    logger.info(big_changes)
    if big_changes:
        notify_user(big_changes)

    return True