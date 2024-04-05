from manim import *
import random

color_list = [
    BLUE_A,
    BLUE_B,
    BLUE_C,
    BLUE_D,
    BLUE_E,
    PURE_BLUE,
    BLUE,
    DARK_BLUE,
    TEAL_A,
    TEAL_B,
    TEAL_C,
    TEAL_D,
    TEAL_E,
    TEAL,
    GREEN_A,
    GREEN_B,
    GREEN_C,
    GREEN_D,
    GREEN_E,
    PURE_GREEN,
    GREEN,
    YELLOW_A,
    YELLOW_B,
    YELLOW_C,
    YELLOW_D,
    YELLOW_E,
    YELLOW,
    GOLD_A,
    GOLD_B,
    GOLD_C,
    GOLD_D,
    GOLD_E,
    GOLD,
    RED_A,
    RED_B,
    RED_C,
    RED_D,
    RED_E,
    PURE_RED,
    RED,
    MAROON_A,
    MAROON_B,
    MAROON_C,
    MAROON_D,
    MAROON_E,
    MAROON,
    PURPLE_A,
    PURPLE_B,
    PURPLE_C,
    PURPLE_D,
    PURPLE_E,
    PURPLE,
    PINK,
    LIGHT_PINK,
    ORANGE,
    LIGHT_BROWN,
    DARK_BROWN,
    LOGO_GREEN,
    LOGO_BLUE,
    LOGO_RED,
]


class T2M(Scene):
    def __init__(self, t: str, n: int = 0):
        config["pixel_width"] = 960
        config["pixel_height"] = 360

        super().__init__()
        t2c_dict: dict = {}
        for i, c in enumerate(t):
            if c != ' ':
                # r_color = random_bright_color()
                # r_color = random_color()
                # if str(r_color) == '#000000':
                #     r_color = '#ffffff'

                r_color = random.choice(color_list)

                t2c_dict['[{0}:{1}]'.format(i, i + 1)] = r_color

        mtext = Text(t, t2c=t2c_dict, fill_opacity=1, weight='BOLD')
        if n == 1:
            # self.play(Write(mtext.shift(DOWN * 1)))
            self.play(Write(mtext))
        else:
            self.play(Create(mtext))

        self.play(mtext.animate.scale(2))

        self.wait()


def t2m(text: str, out_filename: str = "t2m", quality: str = "low_quality", out_format: str = 'gif',
        style: int = 0, preview: bool = False):
    with tempconfig(
            {'output_file': out_filename, 'quality': quality, 'format': out_format, 'preview': preview}):
        scene = T2M(t=text, n=style)
        scene.render()


if __name__ == '__main__':
    t2m("BTC-USDT")
