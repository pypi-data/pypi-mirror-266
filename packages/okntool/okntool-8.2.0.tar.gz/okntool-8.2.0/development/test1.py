is_sweep = "TT"

sweep_yes_indicator = ["y", "yes", "true", "t", "1"]
is_sweep = True if str(is_sweep).lower() in sweep_yes_indicator else False
print(is_sweep)
