#!/usr/bin/env python3
# pyright: basic

"""Composite a small SVG (e.g. a legend) onto a larger SVG at a fixed position.

Usage: compose-legend.py MAIN.svg OVERLAY.svg OUT.svg --x X --y Y
"""

import argparse
import re

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {"svg": SVG_NS}


def dim(value):
    """Parse a graphviz SVG width/height like '123pt' into a float."""
    return float(re.sub(r"[a-z]+$", "", value))


def prefix_ids(tree, prefix):
    id_map = {}
    for el in tree.iter():
        id_attr = el.get("id")
        if id_attr is not None:
            new_id = f"{prefix}{id_attr}"
            id_map[id_attr] = new_id
            el.set("id", new_id)

    for el in tree.iter():
        for attr in (
            "{http://www.w3.org/1999/xlink}href",
            "href",
            "clip-path",
            "fill",
            "mask",
        ):
            val = el.get(attr)
            if val and val.startswith("#") and val[1:] in id_map:
                el.set(attr, f"#{id_map[val[1:]]}")
            elif val and "url(#" in val:
                for old, new in id_map.items():
                    val = val.replace(f"url(#{old})", f"url(#{new})")
                el.set(attr, val)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("main_svg")
    parser.add_argument("overlay_svg")
    parser.add_argument("out_svg")
    parser.add_argument(
        "--x",
        type=float,
        required=True,
        help="overlay x offset, in main SVG's point units",
    )
    parser.add_argument(
        "--y",
        type=float,
        required=True,
        help="overlay y offset, in main SVG's point units",
    )
    args = parser.parse_args()

    main_tree = etree.parse(args.main_svg)
    main_root = main_tree.getroot()

    overlay_tree = etree.parse(args.overlay_svg)
    overlay_root = overlay_tree.getroot()

    main_w = dim(main_root.get("width"))
    main_h = dim(main_root.get("height"))
    overlay_w = dim(overlay_root.get("width"))
    overlay_h = dim(overlay_root.get("height"))

    prefix_ids(overlay_root, "legend-")

    # grow the canvas if the overlay would otherwise spill outside it
    needed_w = max(main_w, args.x + overlay_w)
    needed_h = max(main_h, args.y + overlay_h)
    if needed_w != main_w or needed_h != main_h:
        main_root.set("width", f"{needed_w:g}pt")
        main_root.set("height", f"{needed_h:g}pt")
        main_root.set("viewBox", f"0.00 0.00 {needed_w:g} {needed_h:g}")

    wrapper = etree.SubElement(main_root, f"{{{SVG_NS}}}g")
    wrapper.set("transform", f"translate({args.x:g} {args.y:g})")
    for child in list(overlay_root):
        if not isinstance(child.tag, str):
            continue  # skip comments/PIs
        wrapper.append(child)

    main_tree.write(args.out_svg, xml_declaration=True, encoding="UTF-8")


if __name__ == "__main__":
    main()
