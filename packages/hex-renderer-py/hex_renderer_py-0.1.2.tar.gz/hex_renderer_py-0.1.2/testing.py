from hex_renderer_py import GridOptions, GridPatternOptions, Point, Lines, Intersections, PatternVariant, HexGrid, Triangle, CollisionOption

example_patterns = [
    PatternVariant("NORTH_EAST", "qaq"),   #Mind's reflection
    PatternVariant("EAST", "aa"),          #Compass Purification
    PatternVariant("NORTH_EAST", "qaq"),   #Mind's reflection
    PatternVariant("EAST", "wa"),          #Alidade's Purification
    PatternVariant("EAST", "wqaawdd"),     #Architects Distillation
    PatternVariant("NORTH_EAST", "qaq"),   #Mind's reflection
    PatternVariant("EAST", "aa"),          #Compass Purification
    PatternVariant("NORTH_EAST", "qaq"),   #Alidade's Purification
    PatternVariant("EAST", "wa"),          #Mind's Reflection
    PatternVariant("EAST", "weddwaa"),     #Archers Distillation
    PatternVariant("NORTH_EAST", "waaw"),  #Add
    PatternVariant("NORTH_EAST", "qqd"),   #Summon Light
]

gradient = GridOptions(
    line_thickness=0.12,
    center_dot=Point.None_(),
    pattern_options=GridPatternOptions.Uniform(
        intersections=Intersections.Nothing(),
        lines=Lines.Gradient(
            colors=palettes["default"],
            bent=True,
            segments_per_color=15,
        )
    ),
)


hex_grid = HexGrid(example_patterns, 50)

img = hex_grid.draw_png(50, gradient)

display(Image(data=bytes(img)))