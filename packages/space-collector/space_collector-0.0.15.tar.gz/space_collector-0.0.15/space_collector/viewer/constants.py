import colorsys

from space_collector.game.constants import HIGH_ENERGY_LENGTH, MAP_DIMENSION


class Constants:
    SCREEN_TITLE = "Space collector"
    TEAM_HUES = {
        0: 0,
        1: 30,
        2: 65,
        3: 120,
    }
    TEAM_COLORS = {
        team: tuple(int(c * 255) for c in colorsys.hsv_to_rgb((hue * 2) / 360, 1, 1))
        for team, hue in TEAM_HUES.items()
    }
    # TODO why this hack is necessary?
    TEAM_COLORS[3] = tuple(
        int(c * 255) for c in colorsys.hsv_to_rgb((90 * 2) / 360, 1, 1)
    )

    def resize(self, small_window: bool):
        if not small_window:
            self.SCREEN_WIDTH = 1777
            self.SCREEN_HEIGHT = 1000
            self.SCORE_WIDTH = 500
            self.SCORE_MARGIN = 100
            self.SCORE_FONT_SIZE = 24
            self.SCORE_TEAM_SIZE = 200
            self.MAP_MARGIN = 170
        else:
            self.SCREEN_WIDTH = 800
            self.SCREEN_HEIGHT = 600
            self.SCORE_WIDTH = 300
            self.SCORE_MARGIN = 50
            self.SCORE_FONT_SIZE = 20
            self.SCORE_TEAM_SIZE = 100
            self.MAP_MARGIN = 50

        self.SCORE_TIME_MARGIN = 100
        self.SCORE_HEIGHT = self.SCREEN_HEIGHT
        self.MAP_MIN_X = int(self.SCORE_WIDTH + self.MAP_MARGIN * 1.2)
        self.MAP_MAX_X = int(self.SCREEN_WIDTH - self.MAP_MARGIN * 1.2)
        self.MAP_MIN_Y = self.MAP_MARGIN
        self.MAP_MAX_Y = self.SCREEN_HEIGHT - self.MAP_MARGIN
        self.MAP_WIDTH = self.MAP_MAX_X - self.MAP_MIN_X
        self.MAP_HEIGHT = self.MAP_MAX_Y - self.MAP_MIN_Y
        self.HIGH_ENERGY_SPRITE_LENGTH = int(
            HIGH_ENERGY_LENGTH / MAP_DIMENSION * self.MAP_WIDTH
        )


constants: Constants = Constants()
