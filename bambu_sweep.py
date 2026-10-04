#!/usr/bin/env python3
"""Measure how Bambu Studio settings change a project's print time, by slicing headlessly.

Usage:
  bambu_sweep.py IN.3mf --variant NAME 'key=value' ['key=value' ...] [--variant ...]
  bambu_sweep.py IN.3mf --write OUT.3mf 'key=value' ...      # edited project, no slicing

Each variant edits Metadata/project_settings.config inside a copy of the 3MF, slices it with
the Bambu Studio CLI, and reports the slicer's total time estimate, filament changes and
grams. A "baseline" variant with no overrides always runs first.

Overrides:
  key=value     scalar keys are set as-is; per-filament list keys get value in every slot
  key=a,b,c     per-filament list keys get one value per slot
  key[2]=value  set slot 2 (0-based) of a per-filament list key only

Traps this avoids:
  - An override the CLI silently ignores looks exactly like "no effect". Every overridden key
    is read back from the sliced gcode's config block and printed as APPLIED or NOT APPLIED.
  - Overridden keys are added to different_settings_to_system so the GUI shows them as
    modified rather than snapping back to the preset value.
  - Per-feature times in the slicer's result overlap and don't sum to the total. Compare
    total_predication only, and slice combinations as their own variant (savings don't add).
  - --write re-zips the ORIGINAL 3MF with edited settings. It does not hand back the CLI's
    re-exported 3MF, which is stamped with whatever CLI version happens to be installed.

Times are slicer estimates, not measured wall-clock. If the CLI here is older than the
Bambu Studio that saved the file, trust the deltas more than the absolute numbers.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

BAMBU = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
CFG = "Metadata/project_settings.config"


def parse_override(s):
    m = re.match(r"^([A-Za-z0-9_]+)(?:\[(\d+)\])?=(.*)$", s)
    if not m:
        sys.exit(f"bad override: {s!r} (want key=value, key=a,b or key[i]=value)")
    return m.group(1), (int(m.group(2)) if m.group(2) is not None else None), m.group(3)


def apply_overrides(cfg, overrides):
    for key, idx, val in overrides:
        if key not in cfg:
            print(f"  warning: {key} not in project config; adding it as a new key", file=sys.stderr)
            cfg[key] = val
        elif isinstance(cfg[key], list):
            cur = cfg[key]
            if idx is not None:
                if idx >= len(cur):
                    sys.exit(f"{key}[{idx}]: only {len(cur)} slots")
                cur[idx] = val
            elif "," in val:
                parts = val.split(",")
                if len(parts) != len(cur):
                    sys.exit(f"{key}: {len(parts)} values given for {len(cur)} slots")
                cfg[key] = parts
            else:
                cfg[key] = [val] * len(cur)
        else:
            cfg[key] = val
        diff = cfg.get("different_settings_to_system")
        if isinstance(diff, list) and diff:
            names = [n for n in diff[0].split(";") if n]
            if key not in names:
                names.append(key)
                diff[0] = ";".join(sorted(names))
    return cfg


def write_3mf(src, dst, overrides):
    with zipfile.ZipFile(src) as zin:
        cfg = json.loads(zin.read(CFG))
        apply_overrides(cfg, overrides)
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == CFG:
                    data = json.dumps(cfg, indent=4).encode()
                zout.writestr(item, data)


def gcode_config_value(gcode, key):
    m = re.search(rf"^; {re.escape(key)} = (.*)$", gcode, re.M)
    return m.group(1).strip() if m else None


def slice_one(src, name, overrides, workdir):
    vdir = os.path.join(workdir, name)
    os.makedirs(vdir, exist_ok=True)
    proj = os.path.join(vdir, "in.3mf")
    write_3mf(src, proj, overrides)
    r = subprocess.run(
        [BAMBU, "--debug", "1", "--allow-newer-file", "--slice", "1", "--outputdir", vdir, proj],
        capture_output=True, text=True)
    res_path = os.path.join(vdir, "result.json")
    if not os.path.exists(res_path):
        return {"name": name, "error": f"no result.json (rc={r.returncode}) {r.stderr[-300:]}"}
    res = json.load(open(res_path))
    if res.get("return_code") != 0:
        return {"name": name, "error": res.get("error_string")}
    plate = res["sliced_plates"][0]
    gpath = os.path.join(vdir, "plate_1.gcode")
    gcode = open(gpath, errors="replace").read(400_000) if os.path.exists(gpath) else ""
    # config block sits at the top of Bambu gcode; read only the head to keep this fast
    checks = []
    for key, idx, val in overrides:
        got = gcode_config_value(gcode, key)
        want = val if idx is None else None
        ok = got is not None and (want is None or want.replace(" ", "") in got.replace(" ", ""))
        if idx is not None and got is not None:
            parts = [p.strip() for p in got.split(",")]
            # the gcode writes flush_volumes_matrix already scaled by flush_multiplier
            mult = float((gcode_config_value(gcode, "flush_multiplier") or "1").split(",")[0]) \
                if key == "flush_volumes_matrix" else 1.0
            try:
                ok = idx < len(parts) and abs(float(parts[idx]) - float(val) * mult) < 0.01
            except ValueError:
                ok = idx < len(parts) and parts[idx] == val
        checks.append((key if idx is None else f"{key}[{idx}]", got, ok))
    return {
        "name": name,
        "total_s": plate["total_predication"],
        "print_s": plate["main_predication"],
        "changes": plate.get("filament_change_times"),
        "grams": sum(f["total_used_g"] for f in plate.get("filaments", [])),
        "model_g": sum(f["main_used_g"] for f in plate.get("filaments", [])),
        "checks": checks,
    }


def hm(s):
    return f"{int(s // 3600)}h{int(s % 3600 // 60):02d}m"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--variant", nargs="+", action="append", default=[], metavar=("NAME", "KEY=VALUE"))
    ap.add_argument("--write", metavar="OUT.3mf")
    ap.add_argument("overrides", nargs="*", help="with --write: the overrides to bake in")
    ap.add_argument("--workdir", help="keep sliced outputs here (default: temp dir, deleted)")
    a = ap.parse_args()

    if a.write:
        write_3mf(a.project, a.write, [parse_override(o) for o in a.overrides])
        print(f"wrote {a.write}")
        return

    workdir = a.workdir or tempfile.mkdtemp(prefix="bambu_sweep_")
    variants = [("baseline", [])] + [(v[0], [parse_override(o) for o in v[1:]]) for v in a.variant]
    rows = []
    for name, ov in variants:
        print(f"slicing {name} ...", file=sys.stderr, flush=True)
        rows.append(slice_one(a.project, name, ov, workdir))

    base = rows[0].get("total_s")
    print(f"\n{'variant':28} {'total':>8} {'saved':>8} {'print':>8} {'swaps':>6} {'grams':>7}")
    for r in rows:
        if "error" in r:
            print(f"{r['name']:28} ERROR {r['error']}")
            continue
        saved = (base - r["total_s"]) if base else 0
        print(f"{r['name']:28} {hm(r['total_s']):>8} {hm(saved) if saved >= 0 else '-' + hm(-saved):>8} "
              f"{hm(r['print_s']):>8} {r['changes']:>6} {r['grams']:>7.1f}")
        for key, got, ok in r["checks"]:
            print(f"    {'APPLIED    ' if ok else 'NOT APPLIED'} {key} -> {got}")
    if not a.workdir:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
