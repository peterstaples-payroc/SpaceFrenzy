from dataclasses import dataclass


@dataclass
class HudData:
    level: int
    asteroids_generated_in_level: int
    asteroids_destroyed_in_level: int
    asteroids_destroyed_total: int
    time_to_next_asteroid: int
    message: str
