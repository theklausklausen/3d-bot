import os
from errors import *


def exclude_catched_errors(event, hint):
    if HOST_UNREACHABLE in event['logentry']['message']:
        return None
    return event


def init_sentry(debug: bool = False) -> None:
    if os.environ.get(f'SENTRY_GLITCHTIP_DSN'):
        import sentry_sdk
        sentry_sdk.init(
            dsn=os.environ.get(f'SENTRY_GLITCHTIP_DSN', default='localhost'),
            auto_session_tracking=False,
            environment='development' if debug else 'production',
            debug=debug,
            traces_sample_rate=0.01,
            send_default_pii=False,
            ca_certs=os.environ.get(f'CA_CERTS_PATH', default=None),
            attach_stacktrace=True,
            before_send=exclude_catched_errors
        )
