# Chili-Farm

Make a chili farm.

## Chili farm planner script

Generate a random "design game" layout with plot shapes and chili variety info:

```bash
./chili_farm_planner.py --plots 10 --seed 42 --output-prefix my_farm
```

This creates:
- `my_farm.svg`: a farm map with random shapes for plots.
- `my_farm.json`: structured data with each plot's chili variety details.

The script prints a friendly plan summary to the terminal so you can decide
which plots to grow first.
