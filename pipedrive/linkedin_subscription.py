import abstra.forms as af
import pandas as pd
from linkedin_api import (
    fetch_lead_notification_subscriptions,
    create_lead_notification_subscription,
    delete_lead_notification_url,
)


def select_a_subscription_id():
    return af.read_dropdown(
        "Select a subscription",
        options=[
            {"label": ln.webhook, "value": ln.id}
            for ln in fetch_lead_notification_subscriptions()
        ],
    )


df = pd.DataFrame.from_dict(
    e.to_dict() for e in fetch_lead_notification_subscriptions()
)

action = (
    af.Page()
    .display_pandas(df)
    .read_multiple_choice(
        "What you gonna do?", ["Subscribe", "Unsubscribe"], key="action"
    )
    .run()["action"]
)

if action == "Subscribe":
    url = af.read("Webhook URL", hint="URL of 'linkedin event' webhook")
    lead_type = ("SPONSORED",)
    create_lead_notification_subscription(
        webhook=url,
    )


if action == "Unsubscribe":
    id = select_a_subscription_id()
    delete_lead_notification_url(id)
