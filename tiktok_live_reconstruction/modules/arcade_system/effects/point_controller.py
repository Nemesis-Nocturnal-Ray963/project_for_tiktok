def update_point_text(args, window):
    value = args[0]
    if hasattr(window, "point_ui"):
        window.point_ui.update_text(value)
