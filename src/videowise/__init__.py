"""VideoWise - Video codec compatibility checker and explainer."""

from .compatibility import (  # noqa: F401
    AdobePremiereProChecker,
    AfterEffectsChecker,
    AvidMediaComposerChecker,
    CasparCGChecker,
    ChromeChecker,
    CompatibilityChecker,
    CompatibilityIssue,
    CompatibilityLevel,
    DaVinciResolveChecker,
    FinalCutProChecker,
    FirefoxChecker,
    InstagramChecker,
    OBSChecker,
    PlayoutBeeChecker,
    ProPresenterChecker,
    QLabChecker,
    SafariChecker,
    TikTokChecker,
    TwitchChecker,
    TwitterChecker,
    VmixChecker,
    YouTubeChecker,
    YouTubeLiveChecker,
    ZoomChecker,
    check_compatibility,
    get_available_systems,
)

__version__ = "0.1.0"
