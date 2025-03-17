"""subscribe to some handles, and DM me when a new post is made by one of them"""

import argparse
import asyncio
import logging
from bsky_subscribe.monitor import monitor_user_posts
from atproto import models, Client, IdResolver, client_utils
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BlueskySettings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="BLUESKY_", extra="ignore", env_file=".env"
    )

    handle: str = Field(default=...)
    password: str = Field(default=...)
    recipient_did: str = Field(default=...)


bluesky_settings = BlueskySettings()
bluesky_client = None
id_resolver = IdResolver()


def init_bluesky_client():
    global bluesky_client
    if bluesky_client is None:
        client = Client()
        client.login(bluesky_settings.handle, bluesky_settings.password)
        bluesky_client = client.with_bsky_chat_proxy()
    return bluesky_client


def dm_me(text_content: str, link_url: str | None = None) -> str:
    """Send a direct message to the user on Bluesky."""
    client = init_bluesky_client()
    dm = client.chat.bsky.convo

    convo = dm.get_convo_for_members(
        models.ChatBskyConvoGetConvoForMembers.Params(
            members=[bluesky_settings.recipient_did]
        ),
    ).convo

    if link_url:
        text_builder = client_utils.TextBuilder()
        text_builder.text(text_content)
        text_builder.text("\n\n")
        text_builder.link("View post", link_url)

        dm.send_message(
            models.ChatBskyConvoSendMessage.Data(
                convo_id=convo.id,
                message=models.ChatBskyConvoDefs.MessageInput(
                    text=text_builder.build_text(),
                    facets=text_builder.build_facets(),
                ),
            )
        )
    else:
        dm.send_message(
            models.ChatBskyConvoSendMessage.Data(
                convo_id=convo.id,
                message=models.ChatBskyConvoDefs.MessageInput(
                    text=text_content,
                ),
            )
        )

    return f"Message sent: {text_content}"


def get_handle_from_did(did: str) -> str:
    """Get the handle for a DID."""
    try:
        client = Client()
        client.login(bluesky_settings.handle, bluesky_settings.password)
        profile = client.app.bsky.actor.get_profile({"actor": did})
        return profile.handle
    except Exception as e:
        logger.error(f"Error getting handle for DID {did}: {e}")
        return did  # Return the DID if resolution fails


def notify_new_post(commit: models.ComAtprotoSyncSubscribeRepos.Commit):
    rkey = commit.ops[0].path.split("/")[-1]
    post_url = f"https://bsky.app/profile/{commit.repo}/post/{rkey}"

    message = f"🔔 New post from @{get_handle_from_did(commit.repo)}"
    print(f"{message}\n{post_url}")
    dm_me(message, post_url)


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

    while True:
        try:
            logger.info(f"Starting monitor for handles: {args.handle}")
            await monitor_user_posts(set(args.handle), notify_new_post)
        except Exception as e:
            logger.error(f"Error in monitor: {e}")
            logger.info("Reconnecting in 10 seconds...")
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nKeyboard interrupt")
