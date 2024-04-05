import copy
from pathlib import Path

import matplotlib as mpl
from matplotlib import colors
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.load_default()
path_to_dir = Path(__file__).parent.resolve()
size = 100

white = colors.to_hex("w")
black = colors.to_hex("k")
red = colors.to_hex("r")
cyan = colors.to_hex("c")
blue = colors.to_hex("b")
magenta = colors.to_hex("m")
yellow = colors.to_hex("y")
grey = (196, 196, 196)
green = colors.to_hex("g")
start_color = (191, 128, 255)
neon_green = (128, 255, 0)
dark_green = (64, 127, 0)
light_grey = (220, 220, 220)
ice_color = (102, 212, 237)
sand_color = (234, 182, 118)
road_break_color = (44, 48, 48)
other_car_color = (0, 102, 0)
orange = (168, 62, 50)

line_colors = [red, yellow, cyan, blue, green, black]

marking_image = Image.new("RGBA", (size, size), white)
draw = ImageDraw.Draw(marking_image)
for i1 in range(11):
    for i2 in range(11):
        draw.ellipse((i1 * 10 - 4, i2 * 10 - 4, (i1 * 10 + 4, i2 * 10 + 4)), orange)
# marking_image.save("mark_test.png")


def get_tile(x, y, map, hide_start_line, marking=False, potentials=None):
    rectangle_color = (0, 0, 0) if not marking else orange
    rectangle_width = 2 if not marking else 5
    if map.feature_at(x, y, "wall"):
        wall = Image.new("RGBA", (size, size), grey)
        draw = ImageDraw.Draw(wall)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        draw.line((10, 10, size - 10, size - 10), fill=(0, 0, 0), width=2)
        draw.line((size - 10, 10, 10, size - 10), fill=(0, 0, 0), width=2)
        return wall
    elif map.feature_at(x, y, "start") and not hide_start_line:
        start = Image.new("RGBA", (size, size), start_color)
        draw = ImageDraw.Draw(start)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return start
    elif map.feature_at(x, y, "subgoal"):
        subgoal = Image.new("RGBA", (size, size), neon_green)
        draw = ImageDraw.Draw(subgoal)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return subgoal
    elif map.feature_at(x, y, "used subgoal"):
        used_subgoal = Image.new("RGBA", (size, size), dark_green)
        draw = ImageDraw.Draw(used_subgoal)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return used_subgoal
    elif map.feature_at(x, y, "final goal"):
        finish = Image.new("RGBA", (size, size), red)
        draw = ImageDraw.Draw(finish)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return finish
    elif map.feature_at(x, y, "ice"):
        ice = Image.new("RGBA", (size, size), ice_color)
        draw = ImageDraw.Draw(ice)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return ice
    # sAnd
    elif map.feature_at(x, y, "sand"):
        sand = Image.new("RGBA", (size, size), sand_color)
        draw = ImageDraw.Draw(sand)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return sand
    elif map.feature_at(x, y, "broken road"):
        road_break = Image.open(Path.joinpath(path_to_dir, "pics", "road_break.png"))
        draw = ImageDraw.Draw(road_break)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return road_break
    elif map.feature_at(x, y, "car_spawner"):
        beginning = Image.open(Path.joinpath(path_to_dir, "pics", "beginning.png"))
        draw = ImageDraw.Draw(beginning)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return beginning
    else:
        empty = Image.new("RGBA", (size, size), white)
        draw = ImageDraw.Draw(empty)
        draw.rectangle(
            ((0, 0), (size - 1, size - 1)),
            outline=rectangle_color,
            width=rectangle_width,
        )
        return empty


# specified font size
# font = ImageFont.truetype('SpaceMonoBoldItalic.ttf', 40)


def _transform_coordinates(x, y, offset=0.5, size=100):
    return (x + offset) * size, (y + offset) * size


def create_map(
    env,
    show_path=False,
    hide_start_line=False,
):
    """create the map

    Args:
        env (Environment): Instance of rt game.
        show_path (bool, optional): show the taken path in the current episode. Defaults to False.
        hide_start_line (bool, optional): Hide the start line. Defaults to False.

    Returns:
        PIL: graphical way to represent the current state of game
    """
    h = env.map.width
    w = env.map.height
    result = Image.new(
        "RGBA",
        (size * h, size * w),
        (
            0,
            0,
            0,
        ),
    )

    for x in range(env.map.width):
        for y in range(env.map.height):
            tile = get_tile(x, y, env.map, hide_start_line)
            result.paste(
                tile,
                (x * size, y * size),
                mask=tile,
            )

    path = copy.copy(env.positions_path)
    path.append(path[-1])
    tile_path = copy.copy(env.tile_path)
    noise_path = copy.copy(env.noise_path)
    color = line_colors[0]
    o = 0.5
    circle_radius = 15
    rectangle_half_width = 50
    triangle_offset = 40
    car_half_width = 20
    draw = ImageDraw.Draw(result)

    if show_path:
        for i in range(len(path) - 1):
            f = path[i]
            t = path[i + 1]

            draw = ImageDraw.Draw(result)
            x1 = (f[0] + o) * size
            y1 = (f[1] + o) * size
            x2 = (t[0] + o) * size
            y2 = (t[1] + o) * size
            cx1 = x1 - 15
            cx2 = x1 + 15
            cy1 = y1 - 15
            cy2 = y1 + 15
            draw.line((x1, y1, x2, y2), fill=color, width=5)
            draw.ellipse((cx1, cy1, cx2, cy2), color)

        for x1, y1 in tile_path:
            x1, y1 = _transform_coordinates(x1, y1)
            draw.rectangle(
                (
                    (x1 - rectangle_half_width, y1 - rectangle_half_width),
                    (x1 + rectangle_half_width, y1 + rectangle_half_width),
                ),
                outline=color,
                width=5,
            )

        for x1, y1 in noise_path:
            x1, y1 = _transform_coordinates(x1, y1)
            draw.line(
                (
                    (x1 + triangle_offset, y1 + triangle_offset),
                    (x1, y1 - triangle_offset),
                    (x1 - triangle_offset, y1 + triangle_offset),
                    (x1 + triangle_offset, y1 + triangle_offset),
                ),
                fill=color,
                width=5,
            )

    new_position = copy.copy(env.position) + copy.copy(env.velocity)
    x0, y0 = copy.copy(env.position)
    x0, y0 = _transform_coordinates(x0, y0)
    x1, y1 = new_position
    x1, y1 = _transform_coordinates(x1, y1)

    draw.rectangle(
        (
            (x1 - rectangle_half_width, y1 - rectangle_half_width),
            (x1 + rectangle_half_width, y1 + rectangle_half_width),
        ),
        outline=(0, 0, 0),
        width=5,
    )
    if x0 < x1:
        draw.line((x0, y0, x1 - size * 0.5, y1 - size * 0.5), fill=(0, 0, 0), width=3)
        draw.line((x0, y0, x1 - size * 0.5, y1 + size * 0.5), fill=(0, 0, 0), width=3)
    elif x0 > x1:
        draw.line((x0, y0, x1 + size * 0.5, y1 - size * 0.5), fill=(0, 0, 0), width=3)
        draw.line((x0, y0, x1 + size * 0.5, y1 + size * 0.5), fill=(0, 0, 0), width=3)

    for car in [car["position"] for car in env.cars]:
        x, y = car
        x, y = _transform_coordinates(x, y)
        draw.rectangle(
            (
                x - car_half_width,
                y - car_half_width,
                x + car_half_width,
                y + car_half_width,
            ),
            other_car_color,
        )

    return result


def print_heatmap(
    values,
    bounds=None,
    colormap=None,
    print_path=None,
    show=True,
    fig_size=None,
    font_size=None,
):
    """Builds a heatmap of a two dimensional array.

    :param values: 2D array from which the heatmap is generated
    :param bounds: bound array for the colors used in the heatmap
    :param colormap: a matplotlib colormap
    :param print_path: the path to where a png representation is saved
    :param show: boolean flag if the heatmap should be printed
    :returns: the figure object
    """
    if bounds is None:
        bounds = [-1, 0, 0.25, 0.5, 0.75, 0.9, 0.97, 0.99, 0.998, 1]
    if colormap is None:
        colormap = mpl.colors.ListedColormap(
            [
                "grey",
                "black",
                "red",
                "orange",
                "yellow",
                "lime",
                "limegreen",
                "green",
                "darkgreen",
            ]
        )
    norm = mpl.colors.BoundaryNorm(bounds, colormap.N)
    if fig_size is None:
        fig = plt.figure()
    else:
        fig = plt.figure(figsize=fig_size)
    fig.add_subplot(111)
    im = plt.pcolormesh(
        values, edgecolors="lightgray", linewidth=0.005, cmap=colormap, norm=norm
    )
    ax = plt.gca()
    plt.xticks([])
    plt.yticks([])
    ax.invert_yaxis()
    ax.set_aspect("equal")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)

    if font_size is not None:
        cbar.ax.tick_params(labelsize=font_size)

    if print_path is not None:
        plt.savefig(print_path)
    if show:
        plt.show()
    return fig
