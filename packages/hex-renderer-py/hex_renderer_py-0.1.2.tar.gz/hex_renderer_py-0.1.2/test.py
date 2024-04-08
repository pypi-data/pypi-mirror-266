from hex_renderer_py import GridOptions, GridPatternOptions, Point, Color, Lines, Intersections, Marker, AngleSig, PatternVariant, HexGrid, Triangle, CollisionOption, EndPoint

intersections = Intersections.UniformPoints(
    point=Point.Single(
        marker=Marker(
            color=Color(255, 255, 255, 255),
            radius=0.07,
        ),
    ),
)

gradient = GridOptions(
    line_thickness=0.12,
    center_dot=Point.None_(),
    pattern_options=GridPatternOptions.Changing(
        variations=[
            (
                intersections,
                Lines.Gradient(
                    colors=[
                        Color(214, 9, 177, 255),
                        Color(108, 25, 140, 255),
                        Color(50, 102, 207, 255),
                        Color(102, 110, 125, 255),
                    ],
                    bent=True,
                    segments_per_color=15,
                )
            ),
            (
                intersections,
                Lines.Gradient(
                    colors=[
                        Color(63, 62, 156, 255),
                        Color(65, 150, 255, 255),
                        Color(25, 227, 185, 255),
                        Color(132, 255, 81, 255),
                        Color(223, 223, 55, 255),
                        Color(253, 141, 39, 255),
                        Color(214, 53, 6, 255),
                        Color(122, 4, 3, 255),
                    ],
                    bent=True,
                    segments_per_color=15,
                ),
            ),
        ],
        intros=[AngleSig("qqq")],
        retros=[AngleSig("eee")]
    ),
)

print(gradient)



patterns = [
    PatternVariant("WEST", "qqq"),

    PatternVariant("WEST", "qqq"),

    PatternVariant("NORTH_EAST", "qaq"),
    PatternVariant("EAST", "aa"),
    PatternVariant("NORTH_EAST", "qaq"),
    PatternVariant("EAST", "wa"),
    PatternVariant("EAST", "wqaawdd"),
    PatternVariant("NORTH_EAST", "qaq"),
    PatternVariant("EAST", "aa"),
    PatternVariant("NORTH_EAST", "qaq"),
    PatternVariant("EAST", "wa"),
    PatternVariant("EAST", "weddwaa"),
    PatternVariant("NORTH_EAST", "waaw"),

    PatternVariant("EAST", "eee"),
    PatternVariant("SOUTH_EAST", "deaqq"),

    PatternVariant("NORTH_EAST", "qqd"),
    PatternVariant("EAST", "eee")
]


hex_grid = HexGrid(patterns, 50)


hex_grid.draw_to_file("test.png", 50, gradient)


