import slack
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response, make_response
from slackeventsapi import SlackEventAdapter
from datetime import datetime, timedelta
import random
import json
import requests
from carbon_footprint import findCO2FootPrint

env_path = Path(".")/'.env'
load_dotenv(dotenv_path=env_path)

funFacts = [
    "Meatless Monday !! : One less serving of beef a week for a year saves the same amount of CO2 as driving 348 fewer miles",
    "Loaded Laundry : always opt for fully loaded laundry to decrease ur CO2 footprint",
    "Switch to CFLs : Did you know switching to Compact fluorescent light bulbs (CFLs) save 75% energy when compared to incandescent and last up to 10 times longer"
]

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNIN_TOKEN'],'/slack/events',app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# client.chat_postMessage(channel='#co2_free', text="Hello World")
BOT_ID = client.api_call("auth.test")["user_id"]



client.chat_postMessage(
    channel='#co2_free',
    blocks=[
        {

            "type":"section",
            "text":{
                "type":"mrkdwn",
                "text":"Please complete the CO2 Footprint survey"
            }
        },
        {
            "type":"actions",
            "elements":[
                {
                    "type":"button",
                    "text":{
                        "type":"plain_text",
                        "text":"Click to start",
                    }
                }
            ]
        }
    ]
)


@slack_event_adapter.on('message')
def message(payload):
    # print("ok")
    # print(payload)
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('bot_id')
    text = event.get('text')
    if BOT_ID is None:
        client.chat_postMessage(channel=channel_id,text=text)

def schedule_messages(messages):
    ids = []
    for msg in messages:
        response = client.chat_scheduleMessage(
            channel=msg['channel'], text=msg['text'], post_at=msg['post_at']).data
        id_ = response.get('scheduled_message_id')
        ids.append(id_)

    return ids


@app.route("/quickTips", methods=['POST'])
def funFact():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    client.chat_postMessage(channel=channel_id,text=random.choice(funFacts))
    response = make_response("",200)
    response.headers["Content-Type"] = "application/text"
    return response



@app.route("/slack/interactive-endpoint", methods=['POST'])
def survey():
    payload = json.loads(request.form.get('payload'))
    print(payload)
    if payload["type"] == "block_actions":
        trigger_id = payload['trigger_id']
        # callback_id = payload['callback_id']
        print(payload)
        api_url = 'https://slack.com/api/dialog.open'
        dialog = {
            "callback_id": "select_simple_1234",
            "title" : "Calc CO2 Footprint",
            "submit_label": "Submit",
            "notify_on_cancel": True,
            "elements": [
                {
                    "type":"text",
                    "label": "How many people are in your household? (e.g. 2)",
                    "name":"household_count"
                },
                {
                    "type":"text",
                    "label": "Monthly electric bill (in $$)? (e.g. 50)",
                    "name":"electricity_bill"
                },
                {
                    "type":"text",
                    "label": "How many flights do you take per year? (e.g. 10)",
                    "name":"flightPerYear"
                },
                {
                    "type":"text",
                    "label": "Do you own a car? (e.g. n | y)",
                    "name":"own_car"
                },
                {
                    "type":"text",
                    "label": "Average miles to commute work? (e.g. 10)",
                    "name":"average_commute_to_work"
                },
                {
                    "type":"text",
                    "label": "Do you use public transportation? (e.g. y | n)",
                    "name":"public_transport_usage"
                },
                {
                    "type":"text",
                    "label": "Total ride-sharing trips per month? (e.g. 10)",
                    "name":"total_rides_per_month"
                },
                {
                    "type":"text",
                    "label": "Are you a vegetarian? (e.g. y|n)",
                    "name":"isVeg"
                },
                {
                    "type":"text",
                    "label": "Do you eat meat 3>  each week? (e.g. y|n)",
                    "name":"meatConsumtion"
                },
                {
                    "type":"text",
                    "label": "Monthly Amazon spending in $$? (e.g. 50)",
                    "name":"amazonSpending"
                }
            ]
        }

        api_data = {
            "token" : os.environ['SLACK_TOKEN'],
            "trigger_id" : trigger_id,
            "dialog" : json.dumps(dialog)
        }

        print(api_data)
        res = requests.post(api_url,data=api_data)
        print(res.json())

    elif payload["type"] == "dialog_submission":
        response = payload["submission"]
        user = payload["user"]["name"]
        isrideShareAppUser = 'y' if int(response["total_rides_per_month"])>0 else 'n'
        response = findCO2FootPrint(user,response["household_count"],response["electricity_bill"],response["flightPerYear"],response["own_car"],response["average_commute_to_work"],response["public_transport_usage"],isrideShareAppUser,response["total_rides_per_month"],response["isVeg"],response["meatConsumtion"],response["amazonSpending"],False,False)
        print(response)
        client.chat_postMessage(
            channel="#co2_free",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": user+ " here is your Co2 Footprint summary"
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Electricity Co2 emission "+str(response['electric (kg Co2/year)']) +"(kg Co2/year)"
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Electricity Co2 emission "+str(response['electric (kg Co2/year)']) +"(kg Co2/year)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Air Travel Co2 emission "+str(response['flight (kg Co2/year)']) +"(kg Co2/year)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Road Travel Co2 emission "+str(response['transportation (kg Co2/year)']) +"(kg Co2/year)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Food Co2 emission "+str(response['food (kg Co2/year)']) +"(kg Co2/year)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Retail Co2 emission "+str(response['retail (kg Co2/year)']) +"(kg Co2/year)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Summary : Your total Co2 footprint is "+str(response['Total Co2 Footprint'])+" (kg Co2/year) and "+response['Conclusion']
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Actions to be taken to reduce Co2 emission : "+response['Actions Required to reduce CO2 Emission']
                    }
                }
            ]
        )

    response = make_response("",200)
    response.headers["Content-Type"] = "application/text"
    return response


if __name__ == "__main__":
    # schedule_messages(SCHEDULED_MESSAGES)
    app.run(debug=True)
    



