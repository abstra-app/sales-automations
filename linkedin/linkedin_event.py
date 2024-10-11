import abstra.hooks as ah
import os
import hmac
import hashlib
import linkedin_api
from slack_util import send_message
from abstra.workflows import set_data
from utils.date_format import relative_dt_format

def generate_challenge_response(challenge_code, client_secret):
    hmac_obj = hmac.new(client_secret.encode(), challenge_code.encode(), hashlib.sha256)
    challenge_response = hmac_obj.hexdigest()
    return challenge_response

body, query, headers = ah.get_request()

print(body)
print(query)
print(headers)

if 'challengeCode' in query:
    client_secret = os.environ['LINKEDIN_CLIENT_SECRET']
    challenge_code = query['challengeCode']
    challenge_response = generate_challenge_response(challenge_code, client_secret)

    ah.send_json({
        "challengeCode" : challenge_code,
        "challengeResponse" : challenge_response
    }, headers={
        'Content-Type': 'application/json'
    })

    print("challengeCode in query")
    
elif body['type'] == 'LEAD_ACTION' and body['leadAction'] == 'CREATED':
    form_urn = body["leadGenForm"]
    form_id = form_urn.split(":", 4)[-1]
    form_id = form_id[1:-1]
    form_id = form_id.split(":", 4)[-1]
    form_id = form_id.split(",", 2)[0]
    form = linkedin_api.get_lead_form(form_id)

    form_response_urn = body["leadGenFormResponse"]
    form_response_id = form_response_urn.split(":", 4)[-1]
    form_response = linkedin_api.get_lead_form_response(form_response_id)

    entity = body["associatedEntity"]
    if 'sponsoredCreative' in entity:
        sponsored_creative_urn = entity['sponsoredCreative']
        campaign_id = sponsored_creative_urn.split(':')[-1]
    else:
        raise NotImplementedError("Only sponsored leads are supported")

    answers = {}
    predefined_fields = {}

    for question in form['content']['questions']:
        key = question["name"]
        field = question["predefinedField"]

        for answer in form_response["formResponse"]["answers"]:
            answer_value = answer["answerDetails"]["textQuestionAnswer"]["answer"]
            if answer["questionId"] == question["questionId"]:
                value = answer_value
                break
        else:
            value = None

        answers[key] = value
        predefined_fields[field] = value

    campaign = linkedin_api.get_campaign_from_lead_action(body)
    campaign_name = campaign["name"]

    data = {
        "addName": campaign_name,
        "formName": form["name"],
        "formId": form_id,
        "owner": body["owner"],
        "leadGenFormResponse": body["leadGenFormResponse"],
        "answers": answers
    }
    moment = form_response["submittedAt"]
    moment = relative_dt_format(int(moment))
    msg = "\n".join([
        f"{data['formName']} ({moment})",
        "\n".join([
            f"• {k}: {v}"
            for k,v in data['answers'].items()
        ]),
        
    ])

    send_message(msg)
    set_data("lead", data)
    set_data("campaign_id", campaign_id)
    set_data("form_answer", predefined_fields)
    set_data("type", body['type'])
    print(predefined_fields)

else:
    print("Unhandled event type")
