#!/usr/bin/env python3
"""Chili Farm Planner.

Generates a playful farm layout made of random shapes and assigns chili
varieties to each plot. Outputs an SVG map and a JSON plan.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Tuple


CHILI_VARIETIES = [
    {
        "name": "Jalapeño",
        "heat_scoville": "2,500–8,000",
        "days_to_maturity": 75,
        "notes": "Reliable, medium heat, great for pickling.",
    },
    {
        "name": "Habanero",
        "heat_scoville": "100,000–350,000",
        "days_to_maturity": 95,
        "notes": "High heat with fruity flavor; needs warm temps.",
    },
    {
        "name": "Cayenne",
        "heat_scoville": "30,000–50,000",
        "days_to_maturity": 80,
        "notes": "Thin pods; great for drying into powder.",
    },
    {
        "name": "Poblano",
        "heat_scoville": "1,000–2,000",
        "days_to_maturity": 90,
        "notes": "Mild, large pods; perfect for roasting.",
    },
    {
        "name": "Thai Bird",
        "heat_scoville": "50,000–100,000",
        "days_to_maturity": 85,
        "notes": "Compact plants; prolific small pods.",
    },
    {
        "name": "Ghost (Bhut Jolokia)",
        "heat_scoville": "855,000–1,041,427",
        "days_to_maturity": 100,
        "notes": "Extreme heat; handle with care.",
    },
    {
        "name": "Shishito",
        "heat_scoville": "50–200",
        "days_to_maturity": 70,
        "notes": "Mostly mild; blistering for snacks.",
    },
    {
        "name": "Serrano",
        "heat_scoville": "10,000–23,000",
        "days_to_maturity": 75,
        "notes": "Crisp heat; excellent for salsa.",
    },
]

COLORS = [
    "#e63946",
    "#f4a261",
    "#2a9d8f",
    "#e9c46a",
    "#8d99ae",
    "#ffb703",
    "#90be6d",
    "#577590",
]


@dataclass
class PlotShape:
    plot_id: int
    shape: str
    variety: str
    heat_scoville: str
    days_to_maturity: int
    notes: str
    area: float
    color: str
    points: List[Tuple[float, float]]


def random_rect(rng: random.Random, width: float, height: float) -> List[Tuple[float, float]]:
    w = rng.uniform(8, 20)
    h = rng.uniform(6, 16)
    x = rng.uniform(2, width - w - 2)
    y = rng.uniform(2, height - h - 2)
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def random_circle(rng: random.Random, width: float, height: float, points: int = 18) -> List[Tuple[float, float]]:
    radius = rng.uniform(5, 12)
    cx = rng.uniform(radius + 2, width - radius - 2)
    cy = rng.uniform(radius + 2, height - radius - 2)
    coords = []
    for idx in range(points):
        angle = 2 * math.pi * (idx / points)
        coords.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return coords


def random_triangle(rng: random.Random, width: float, height: float) -> List[Tuple[float, float]]:
    points = []
    for _ in range(3):
        points.append((rng.uniform(3, width - 3), rng.uniform(3, height - 3)))
    return points


def polygon_area(points: List[Tuple[float, float]]) -> float:
    area = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        area += (x1 * y2) - (x2 * y1)
    return abs(area) / 2.0


def build_plots(rng: random.Random, count: int, width: float, height: float) -> List[PlotShape]:
    plots: List[PlotShape] = []
    generators = [
        ("rectangle", random_rect),
        ("circle", random_circle),
        ("triangle", random_triangle),
    ]

    for idx in range(1, count + 1):
        variety = rng.choice(CHILI_VARIETIES)
        shape_name, generator = rng.choice(generators)
        points = generator(rng, width, height)
        plot = PlotShape(
            plot_id=idx,
            shape=shape_name,
            variety=variety["name"],
            heat_scoville=variety["heat_scoville"],
            days_to_maturity=variety["days_to_maturity"],
            notes=variety["notes"],
            area=polygon_area(points),
            color=rng.choice(COLORS),
            points=points,
        )
        plots.append(plot)
    return plots


def svg_polygon(points: List[Tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def render_svg(plots: List[PlotShape], width: float, height: float) -> str:
    shapes = []
    for plot in plots:
        polygon = svg_polygon(plot.points)
        shapes.append(
            f"<polygon points=\"{polygon}\" fill=\"{plot.color}\" "
            f"fill-opacity=\"0.6\" stroke=\"#1f1f1f\" stroke-width=\"0.8\" />"
        )
        centroid_x = sum(p[0] for p in plot.points) / len(plot.points)
        centroid_y = sum(p[1] for p in plot.points) / len(plot.points)
        shapes.append(
            f"<text x=\"{centroid_x:.1f}\" y=\"{centroid_y:.1f}\" "
            f"font-size=\"3.5\" text-anchor=\"middle\" fill=\"#1f1f1f\">"
            f"{plot.plot_id}</text>"
        )

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {width} {height}\" "
        f"width=\"{width * 8}\" height=\"{height * 8}\">\n"
        "<rect width=\"100%\" height=\"100%\" fill=\"#f7f3e9\" />\n"
        + "\n".join(shapes)
        + "\n</svg>\n"
    )


def build_plan_report(plots: List[PlotShape]) -> str:
    lines = ["Chili Farm Plan", "=" * 15]
    for plot in plots:
        lines.append(
            f"Plot {plot.plot_id} ({plot.shape}, {plot.area:.1f} sq units): "
            f"{plot.variety} | Heat {plot.heat_scoville} | "
            f"{plot.days_to_maturity} days\n  Notes: {plot.notes}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a random chili farm game plan.")
    parser.add_argument("--plots", type=int, default=8, help="Number of plots to generate.")
    parser.add_argument("--width", type=float, default=100.0, help="Map width in units.")
    parser.add_argument("--height", type=float, default=60.0, help="Map height in units.")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible plans.")
    parser.add_argument(
        "--output-prefix",
        default="chili_farm_plan",
        help="Prefix for output SVG and JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    plots = build_plots(rng, args.plots, args.width, args.height)
    svg = render_svg(plots, args.width, args.height)
    plan = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "plots": [asdict(plot) for plot in plots],
        "map": {"width": args.width, "height": args.height},
    }

    svg_path = f"{args.output_prefix}.svg"
    json_path = f"{args.output_prefix}.json"

    with open(svg_path, "w", encoding="utf-8") as handle:
        handle.write(svg)

    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2)

    report = build_plan_report(plots)
    print(report)
    print(f"\nSaved map to {svg_path} and plan to {json_path}.")


if __name__ == "__main__":
    main()
