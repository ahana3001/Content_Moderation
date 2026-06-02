from dataclasses import dataclass, field


@dataclass(frozen=True)
class PolicyThresholds:
    allow_below: float = 0.45
    review_below: float = 0.8
    block_at: float = 0.8


@dataclass(frozen=True)
class SurfaceThresholdOverrides:
    chat: PolicyThresholds = field(default_factory=PolicyThresholds)
    comment: PolicyThresholds = field(default_factory=PolicyThresholds)
    livestream: PolicyThresholds = field(
        default_factory=lambda: PolicyThresholds(
            allow_below=0.4,
            review_below=0.72,
            block_at=0.72,
        )
    )
    signup: PolicyThresholds = field(
        default_factory=lambda: PolicyThresholds(
            allow_below=0.3,
            review_below=0.65,
            block_at=0.65,
        )
    )


DEFAULT_THRESHOLDS = SurfaceThresholdOverrides()
