"""Check the promised skill inventory and its proposal separation without nTop."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'docs/skills/source-provenance.json').read_text(encoding='utf-8'))
    entries = manifest['skills']
    names = [entry['id'] for entry in entries]
    assert len(names) == len(set(names)) == 18, 'The paper inventory requires 18 distinct skills'
    for entry in entries:
        expected = Path('.agents/skills') / entry['id'] / 'SKILL.md'
        assert Path(entry['destination']) == expected, entry
        assert (ROOT / expected).is_file(), expected
        for source in entry['source_files']:
            assert not Path(source['path']).is_absolute(), source
            assert len(source['sha256']) == 64, source
    for name in manifest['additional_existing_skills']:
        assert (ROOT / '.agents/skills' / name / 'SKILL.md').is_file(), name
    proposed = (ROOT / 'docs/skills/future-engineering-skills.md').read_text(encoding='utf-8')
    ids = [line.split('`')[1] for line in proposed.splitlines() if line.startswith('**Proposed ID:**')]
    assert len(ids) == len(set(ids)) == 10, 'Expected ten distinct proposal IDs'
    for name in ids:
        assert not (ROOT / '.agents/skills' / name).exists(), f'Proposal installed as skill: {name}'
    total = len(list((ROOT / '.agents/skills').glob('*/SKILL.md')))
    print(f'PASS: 18 inventory skills, 10 separate proposals, {total} total repository skill entries')


if __name__ == '__main__':
    main()
