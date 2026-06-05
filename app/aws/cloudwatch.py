import logging
import watchtower

logger = logging.getLogger("cloudlearn")

logger.setLevel(logging.INFO)

logger.addHandler(
    watchtower.CloudWatchLogHandler(
        log_group_name="/cloudlearn/application"
    )
)