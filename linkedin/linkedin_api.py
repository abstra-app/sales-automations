import requests
from dataclasses import dataclass
import os


@dataclass
class SponsoredLeadNotification:
    id: int
    webhook: str

    @staticmethod
    def from_dict(data):
        return SponsoredLeadNotification(
            id=data["id"],
            webhook=data["webhook"],
        )

    def to_dict(self):
        return {"id": self.id, "webhook": self.webhook, "leadType": "SPONSORED"}


@dataclass
class Paging:
    count: int
    start: int

    @staticmethod
    def from_dict(data):
        return Paging(
            count=data["count"],
            start=data["start"],
        )

    def to_dict(self):
        return {"count": self.count, "start": self.start}


@dataclass
class SubscriptionsResponse:
    elements: list[SponsoredLeadNotification]
    paging: Paging

    @staticmethod
    def from_dict(data):
        return SubscriptionsResponse(
            elements=[
                SponsoredLeadNotification.from_dict(element)
                for element in data["elements"]
            ],
            paging=Paging.from_dict(data["paging"]),
        )


client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
client_id = os.getenv("LINKEDIN_CLIENT_ID")
access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

base_url = "https://api.linkedin.com/rest/leadNotifications"
organization_urn = "urn:li:organization:424525160"
sponsored_account_urn = os.getenv("LINKEDIN_SPONSORED_ACCOUNT_URN")
headers = {
    "Authorization": f"Bearer {access_token}",
    "LinkedIn-Version": "202407",
    "X-Restli-Protocol-Version": "2.0.0",
}


def fetch_lead_notification_subscriptions():
    get_url = base_url

    escaped_urn = sponsored_account_urn.replace(":", "%3A")
    sponsored_response = requests.get(
        get_url
        + f"?q=criteria&owner=(value:(sponsoredAccount:{escaped_urn}))&leadType=(leadType:SPONSORED)",
        headers=headers,
    )
    sponsored_response = SubscriptionsResponse.from_dict(sponsored_response.json())

    return sponsored_response.elements


def create_lead_notification_subscription(webhook: str):
    data = {
        "webhook": webhook,
        "owner": {"sponsoredAccount": sponsored_account_urn},
        "leadType": "SPONSORED",
    }

    response = requests.post(base_url, headers=headers, json=data)
    response.raise_for_status()


def delete_lead_notification_url(id):
    delete_url = base_url + f"/{id}"
    response = requests.delete(delete_url, headers=headers)
    response.raise_for_status()


def get_lead_form_response(id: str):
    url = f"https://api.linkedin.com/rest/leadFormResponses/{id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_lead_form(id: str):
    url = f"https://api.linkedin.com/rest/leadForms/{id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_creative(urn: str):
    id = urn.split(":")[-1]
    url = f"https://api.linkedin.com/v2/adCreativesV2/{id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_campaign(urn: str):
    campaign_id = urn.split(":")[-1]
    account_id = sponsored_account_urn.split(":")[-1]
    url = f"https://api.linkedin.com/rest/adAccounts/{account_id}/adCampaigns/{campaign_id}"
    response = requests.get(url, headers=headers)
    return response.json()


def get_campaign_from_lead_action(body):
    entity = body["associatedEntity"]
    if "sponsoredCreative" in entity:
        sponsored_creative_urn = entity["sponsoredCreative"]
        creative = get_creative(sponsored_creative_urn)
        campaign_urn = creative["campaign"]
        campaign = get_campaign(campaign_urn)
        return campaign
    else:
        raise NotImplementedError("Only sponsored leads are supported")
