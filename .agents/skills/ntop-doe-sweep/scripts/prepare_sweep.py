"""Prepare typed ntopCL input grids as NDJSON without executing a notebook.

Adapted from the recorded Orchestrate make_ndjson helper. File-path values are
preserved unless explicitly set by name. The output file must not exist.
"""
import argparse
import copy
import itertools
import json
import math
from pathlib import Path


def coerce(raw, spec):
    kind = spec.get('type')
    if kind in ('real', 'scalar', 'length', 'angle'):
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError('numeric inputs must be finite')
        return value
    if kind == 'integer':
        return int(raw)
    if kind == 'boolean':
        words = {'true': True, 'false': False, '1': True, '0': False}
        if raw.lower() not in words:
            raise ValueError('boolean values must be true, false, 1, or 0')
        return words[raw.lower()]
    if kind in ('point', 'vector', 'direction'):
        values = [float(v) for v in raw.split(',')]
        if len(values) != 3 or not all(math.isfinite(v) for v in values):
            raise ValueError(f'{kind} requires three finite components')
        return values
    if kind == 'enum':
        value = json.loads(raw)
        template_value = spec.get('value')
        if isinstance(template_value, list):
            if not isinstance(value, list) or not value or any(type(v) is not int for v in value):
                raise ValueError('this enum template requires a JSON integer array')
        elif type(template_value) is int:
            if type(value) is not int:
                raise ValueError('this enum template requires a JSON integer')
        else:
            raise ValueError('enum template has no supported scalar/array default')
        return value
    if kind in ('file_path', 'text'):
        return raw
    raise ValueError(f'unsupported input type {kind!r}; preserve the template or supply a supported type')


def inputs_by_name(template):
    entries = template.get('inputs')
    if not isinstance(entries, list):
        raise ValueError('template requires an inputs array')
    result = {}
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get('name'), str):
            raise ValueError('each input requires a string name')
        if item['name'] in result:
            raise ValueError(f'duplicate input name: {item["name"]}')
        if 'values' in item:
            raise ValueError('use a single-value input template, not an iterative values file')
        result[item['name']] = item
    return result


def assignment(text, specs):
    if '=' not in text:
        raise ValueError('expected NAME=VALUE')
    name, raw = text.split('=', 1)
    if name not in specs:
        raise ValueError(f'unknown input: {name}')
    return name, raw


def prepare(template, sweeps=(), linspaces=(), constants=(), zipped=False, max_tasks=10000):
    base = copy.deepcopy(template)
    specs = inputs_by_name(base)
    changed = set()

    def claim(name):
        if name in changed:
            raise ValueError(f'input assigned more than once: {name}')
        changed.add(name)

    for item in constants:
        name, raw = assignment(item, specs)
        claim(name)
        specs[name]['value'] = coerce(raw, specs[name])

    axes = []
    for item in sweeps:
        name, raw = assignment(item, specs)
        claim(name)
        separator = ';' if specs[name].get('type') in ('point', 'vector', 'direction', 'enum') else ','
        values = [coerce(v, specs[name]) for v in raw.split(separator)]
        axes.append((name, values))
    for item in linspaces:
        name, raw = assignment(item, specs)
        claim(name)
        if specs[name].get('type') not in ('real', 'scalar', 'length', 'angle', 'integer'):
            raise ValueError('linspace requires a numeric scalar input')
        lo, hi, count = raw.split(':')
        lo, hi, count = float(lo), float(hi), int(count)
        if count < 2 or count > max_tasks or not all(map(math.isfinite, (lo, hi))):
            raise ValueError('linspace requires finite bounds and 2..max-tasks points')
        values = [lo + (hi - lo) * i / (count - 1) for i in range(count)]
        if specs[name]['type'] == 'integer':
            if any(abs(v - round(v)) > 1e-10 for v in values):
                raise ValueError('integer linspace must land on integer values')
            values = [int(round(v)) for v in values]
        axes.append((name, values))

    sizes = [len(v) for _, v in axes]
    if zipped and len(set(sizes)) > 1:
        raise ValueError('zip requires equal axis lengths')
    count = sizes[0] if zipped and sizes else math.prod(sizes)
    if count < 1 or count > max_tasks:
        raise ValueError(f'task count {count} is outside 1..{max_tasks}')
    combos = zip(*(v for _, v in axes)) if zipped and axes else itertools.product(*(v for _, v in axes))
    result = []
    for combo in combos:
        task = copy.deepcopy(base)
        task_specs = inputs_by_name(task)
        for (name, _), value in zip(axes, combo):
            task_specs[name]['value'] = value
        result.append(task)
    # Also reject nonfinite values inherited from a nonstandard JSON template.
    json.dumps(result, allow_nan=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--sweep', action='append', default=[])
    parser.add_argument('--linspace', action='append', default=[])
    parser.add_argument('--set', dest='constants', action='append', default=[])
    parser.add_argument('--zip', dest='zipped', action='store_true')
    parser.add_argument('--max-tasks', type=int, default=10000, help='Explicit preparation limit, not a compute budget')
    args = parser.parse_args()
    try:
        template = json.loads(Path(args.template).read_text(encoding='utf-8-sig'))
        tasks = prepare(template, args.sweep, args.linspace, args.constants, args.zipped, args.max_tasks)
        destination = Path(args.out)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x', encoding='utf-8', newline='\n') as stream:
            for task in tasks:
                stream.write(json.dumps(task, allow_nan=False) + '\n')
    except (ValueError, OSError, TypeError) as exc:
        parser.error(str(exc))
    print(f'Prepared {len(tasks)} inputs in {destination}; no native execution performed.')


if __name__ == '__main__':
    main()
