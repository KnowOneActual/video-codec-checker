"""Legacy compatibility checker modules."""

from .advanced_playout import (  # noqa: F401
    PlaybackProChecker,
    ProVideoPlayerChecker,
    ResolumeChecker,
    WirecastChecker,
)
from .editing_platforms import (  # noqa: F401
    AdobePremiereProChecker,
    AfterEffectsChecker,
    AvidMediaComposerChecker,
    DaVinciResolveChecker,
    FinalCutProChecker,
)
from .streaming_checkers import (  # noqa: F401
    DiscordChecker,
    KickChecker,
    RestreamChecker,
    TwitchChecker,
    YouTubeLiveChecker,
    ZoomChecker,
)
