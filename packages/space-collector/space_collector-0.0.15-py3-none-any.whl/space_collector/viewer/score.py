from dataclasses import dataclass
from importlib.resources import files

import arcade

from space_collector.viewer.constants import constants


class TextDrawer:
    # TODO implement LRU
    def __init__(self) -> None:
        self.cache: dict[tuple, list[arcade.Text]] = {}

    def draw(self, text: str, x: int, y: int, team: int, size: int) -> None:
        key = (text, x, y, team)
        if key not in self.cache:
            texts: list[arcade.Text] = []
            halo_color = (255, 255, 255, 50)
            for offset_x in (-1, 1):
                for offset_y in (-1, 1):
                    texts.append(
                        arcade.Text(
                            text,
                            x + offset_x,
                            y + offset_y,
                            halo_color,
                            font_size=size,
                            font_name="Sportrop",
                        )
                    )
            texts.append(
                arcade.Text(
                    text,
                    x,
                    y,
                    constants.TEAM_COLORS[team],
                    font_size=size,
                    font_name="Sportrop",
                )
            )
            self.cache[key] = texts
        for predrawn_text in self.cache[key]:
            predrawn_text.draw()


text = TextDrawer()


@dataclass(frozen=True)
class TeamData:
    name: str
    blocked: bool
    nb_saved_planets: int
    nb_planets: int
    score: int
    team: int


class Score:
    def __init__(self):
        self.sprite_list = arcade.SpriteList()
        self.teams_data: list[TeamData] = []
        self.time = 0

    def setup(self) -> None:
        font_file = files("space_collector.viewer").joinpath("images/Sportrop.ttf")
        image_file = files("space_collector.viewer").joinpath(
            "images/score_background.png"
        )

        arcade.load_font(font_file)
        self.sprite_list = arcade.SpriteList()
        background = arcade.Sprite(image_file)
        background.width = constants.SCORE_WIDTH
        background.height = constants.SCORE_HEIGHT
        background.position = constants.SCORE_WIDTH // 2, constants.SCORE_HEIGHT // 2
        self.sprite_list.append(background)

    def draw(self) -> None:
        self.sprite_list.draw()
        text.draw(
            f"Time: {int(self.time)}",
            constants.SCORE_MARGIN,
            constants.SCORE_HEIGHT - constants.SCORE_TIME_MARGIN,
            1,
            size=constants.SCORE_FONT_SIZE,
        )
        for index, team_data in enumerate(
            sorted(self.teams_data, key=lambda td: td.score)
        ):
            team_offset = constants.SCORE_TEAM_SIZE + index * constants.SCORE_TEAM_SIZE

            text.draw(
                team_data.name[:30],
                constants.SCORE_MARGIN,
                team_offset,
                team_data.team,
                size=constants.SCORE_FONT_SIZE,
            )
            if team_data.blocked:
                text.draw(
                    "BLOCKED",
                    constants.SCORE_MARGIN,
                    team_offset - constants.SCORE_TEAM_SIZE // 5,
                    index,
                    size=constants.SCORE_FONT_SIZE - 5,
                )
            else:
                text.draw(
                    f"Score: {team_data.score}",
                    constants.SCORE_MARGIN,
                    team_offset - constants.SCORE_TEAM_SIZE // 5,
                    team_data.team,
                    size=constants.SCORE_FONT_SIZE - 5,
                )
                text.draw(
                    f"Planets: {team_data.nb_saved_planets}/{team_data.nb_planets}",
                    constants.SCORE_MARGIN,
                    team_offset - 2 * constants.SCORE_TEAM_SIZE // 5,
                    team_data.team,
                    size=constants.SCORE_FONT_SIZE - 5,
                )

    def update(self, server_data: dict) -> None:
        self.time = server_data["time"]
        self.teams_data.clear()
        for team, player_data in enumerate(server_data["players"]):
            nb_planets = len(player_data["planets"])
            nb_saved_planets = len(
                [
                    planet_data
                    for planet_data in player_data["planets"]
                    if planet_data["saved"]
                ]
            )
            self.teams_data.append(
                TeamData(
                    name=player_data["name"],
                    blocked=player_data["blocked"],
                    nb_saved_planets=nb_saved_planets,
                    nb_planets=nb_planets,
                    score=player_data["score"],
                    team=team,
                )
            )
