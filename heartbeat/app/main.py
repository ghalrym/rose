"""Entry point for the heartbeat service: config, logging, run loop."""

import logging
import sys

from heartbeat.app.config import HeartbeatConfig
from heartbeat.app.loop import HeartbeatLoop


def run() -> None:
    """Load config, configure logging, and run the heartbeat loop forever."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stdout,
    )
    config = HeartbeatConfig()
    HeartbeatLoop(config).run()


if __name__ == "__main__":
    run()
