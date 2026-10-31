"""Summarize measured CAD/source point pairs; does not compute closest points."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

COLUMNS = ['cad_x', 'cad_y', 'cad_z', 'source_x', 'source_y', 'source_z']


def statistics(values):
    quantiles = np.percentile(values, [50, 95, 99, 100])
    return {'count': len(values), 'median_mm': float(quantiles[0]),
            'p95_mm': float(quantiles[1]), 'p99_mm': float(quantiles[2]),
            'max_mm': float(quantiles[3]), 'rms_mm': float(np.sqrt(np.mean(values**2)))}


def summarize(path, residual_limit=None):
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if not all(name in headers for name in COLUMNS):
            raise ValueError('Missing required columns: ' + ', '.join(COLUMNS))
        rows = list(reader)
    if not rows:
        raise ValueError('No measurement rows')
    values = np.array([[float(row[name]) for name in COLUMNS] for row in rows])
    if not np.isfinite(values).all():
        raise ValueError('Point coordinates must all be finite; retain and resolve failed projections')
    distance = np.linalg.norm(values[:, :3] - values[:, 3:], axis=1)
    if not np.isfinite(distance).all():
        raise ValueError('Point distance overflow')
    regions = np.array([(r.get('region') or 'unassigned') for r in rows])
    residuals = None
    if 'source_residual_mm' in headers:
        residuals = np.abs(np.array([float(r['source_residual_mm']) for r in rows]))
        if not np.isfinite(residuals).all():
            raise ValueError('Every source residual must be finite')
    if residual_limit is not None and residuals is None:
        raise ValueError('A residual limit requires source_residual_mm values')
    failed = 0 if residual_limit is None else int(np.sum(residuals > residual_limit))
    worst = np.argsort(distance)[-10:][::-1]
    return {
        'input_csv': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'units': 'mm', 'method': 'Euclidean distance between supplied point pairs; equal weight per row.',
        'limitation': 'Pairs and source membership are not verified here. No closest-point or Hausdorff guarantee.',
        'global': statistics(distance),
        'regions': {str(name): statistics(distance[regions == name]) for name in np.unique(regions)},
        'source_residual_mm_max': None if residuals is None else float(residuals.max()),
        'source_residual_limit_mm': residual_limit,
        'source_residual_exceedances': None if residual_limit is None else failed,
        'residual_requirement_passed': None if residual_limit is None else failed == 0,
        'worst_samples': [{'csv_line': int(i) + 2, 'region': str(regions[i]),
                           'cad_mm': values[i, :3].tolist(), 'source_mm': values[i, 3:].tolist(),
                           'distance_mm': float(distance[i])} for i in worst],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--max-source-residual-mm', type=float)
    args = parser.parse_args()
    if args.output.resolve() == args.csv.resolve():
        parser.error('Output must not overwrite the input CSV')
    limit = args.max_source_residual_mm
    if limit is not None and (not math.isfinite(limit) or limit < 0):
        parser.error('Residual limit must be finite and nonnegative')
    try:
        report = summarize(args.csv, limit)
        code = 2 if report['residual_requirement_passed'] is False else 0
    except (ValueError, OSError, KeyError, csv.Error) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'global': report['global'],
                      'residual_requirement_passed': report['residual_requirement_passed']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
