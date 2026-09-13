"""Bounded live identifier lookup; retain overloads when selecting versions."""
import re
_VERSION = re.compile(r'\[(\d+)\.(\d+)\.(\d+)\]$')

def newest_only(identifiers):
    keep = {}
    for identifier in identifiers:
        match = _VERSION.search(identifier)
        key = _VERSION.sub('', identifier)
        version = tuple(map(int, match.groups())) if match else (-1, -1, -1)
        if key not in keep or version > keep[key][0]:
            keep[key] = (version, identifier)
    return sorted(item[1] for item in keep.values())

def lookup(notebook, mask, *, all_versions=False, limit=40):
    if not mask.strip() or mask in {'real', 'point', 'vector', 'real_field', 'core.', 'core.var<', 'core.list<'}:
        raise ValueError('Use a narrow function mask or complete core type identifier')
    identifiers = notebook.list_available_blocks(mask)
    if len(identifiers) > limit:
        raise ValueError(f'{len(identifiers)} matches; narrow the mask before requesting identifiers')
    return sorted(identifiers) if all_versions else newest_only(identifiers)
