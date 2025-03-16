"""Monitor posts from a specific Bluesky user."""

import logging
from typing import Callable
from atproto import (
    AsyncFirehoseSubscribeReposClient,
    models,
    firehose_models,
    parse_subscribe_repos_message,
)
from atproto_client.models.string_formats import Did

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def monitor_user_posts(
    did: Did, callback: Callable[[models.ComAtprotoSyncSubscribeRepos.Commit], None]
) -> None:
    """Monitor posts from a specific Bluesky user."""
    client = AsyncFirehoseSubscribeReposClient()
    logger.info(f"Monitoring posts from {did}")

    async def on_message_handler(message: firehose_models.MessageFrame) -> None:
        commit = parse_subscribe_repos_message(message)
        if isinstance(commit, models.ComAtprotoSyncSubscribeRepos.Commit):
            if commit.repo == did:
                for op in commit.ops:
                    if op.action == "create" and op.path.startswith(
                        "app.bsky.feed.post"
                    ):
                        callback(commit)

    await client.start(on_message_handler)
