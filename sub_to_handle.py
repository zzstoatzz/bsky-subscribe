# copy of sub_to_did.py, but

import argparse
import asyncio
from bsky_subscribe.monitor import monitor_user_posts
from atproto import models


from typing import Annotated

import httpx
from pydantic import BeforeValidator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SurgeSettings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="SURGE_", extra="ignore", env_file=".env"
    )

    api_key: str = Field(default=...)
    account_id: str = Field(default=...)
    my_phone_number: Annotated[
        str, BeforeValidator(lambda v: "+" + v if not v.startswith("+") else v)
    ] = Field(default=...)
    my_first_name: str = Field(default=...)
    my_last_name: str = Field(default=...)


surge_settings = SurgeSettings()


def text_me(text_content: str) -> str:
    """Send a text message to the user that you operate on behalf of."""
    with httpx.Client() as client:
        response = client.post(
            "https://api.surgemsg.com/messages",
            headers={
                "Authorization": f"Bearer {surge_settings.api_key}",
                "Surge-Account": surge_settings.account_id,
                "Content-Type": "application/json",
            },
            json={
                "body": text_content,
                "conversation": {
                    "contact": {
                        "first_name": surge_settings.my_first_name,
                        "last_name": surge_settings.my_last_name,
                        "phone_number": surge_settings.my_phone_number,
                    }
                },
            },
        )
        response.raise_for_status()
        return f"Message sent: {text_content}"


def notify_new_post(commit: models.ComAtprotoSyncSubscribeRepos.Commit):
    rkey = commit.ops[0].path.split("/")[-1]
    post_url = f"https://bsky.app/profile/{commit.repo}/post/{rkey}"
    message = f"New post from {commit.repo!r}, link: {post_url}"
    print(message)
    text_me(message)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--handle",
        type=str,
        action="append",
        required=True,
        help="Handles to monitor (can be specified multiple times)",
    )
    args = parser.parse_args()
    await monitor_user_posts(set(args.handle), notify_new_post)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt")
