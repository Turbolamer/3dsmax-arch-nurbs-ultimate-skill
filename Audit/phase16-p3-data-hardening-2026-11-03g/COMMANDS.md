# Executed shell command ledger

This is the verbatim shell-command history, in order. Read-only file/search/skill
tool calls and patch-tool edits are not shell commands. All commands ran in the
workspace root; `python` resolved to `C:\Python314\python.exe` in the recorder.
The `xb` commands below are historical: re-running them will refuse to overwrite
already retained evidence. Results and recorded hashes are in `REPORT.md`,
`results.json`, `v2-results.json`, and `v3-results.json`. Intermediate direct
test outputs remain in the session transcript, not raw files; their earlier
source bytes were not all snapshotted. Recorder outputs are retained as raw logs.

## 1. Pre-edit source/hash verification and exclusive copy — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
source = Path('scripts/wall_surface_runtime.py')
expected = '3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf'
data = source.read_bytes()
digest = sha256(data).hexdigest()
print('source bytes:', len(data))
print('source sha256:', digest)
if digest != expected:
    raise SystemExit('STOP: source hash mismatch; no directory or copy created')
directory = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
directory.mkdir(exist_ok=False)
snapshot = directory / 'wall_surface_runtime.pre-edit.py'
with snapshot.open('xb') as f:
    f.write(data)
saved = snapshot.read_bytes()
if saved != data or sha256(saved).hexdigest() != expected:
    raise SystemExit('STOP: snapshot verification failed')
print('exclusive snapshot:', snapshot)
print('snapshot bytes:', len(saved))
print('snapshot sha256:', sha256(saved).hexdigest())
PY
```

## 2. First direct test — exit 1, 14 methods / 2 test-harness failures

```bash
python -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py
```

## 3. Ad-hoc diff diagnostic — exit 1, Python import/dataclasses error

```bash
python -B - <<'PY'
from pathlib import Path
import importlib.util
from difflib import unified_diff
p=Path('Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py')
spec=importlib.util.spec_from_file_location('t',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
oldspec=importlib.util.spec_from_file_location('old',Path('Audit/phase16-p3-data-hardening-2026-11-03g/wall_surface_runtime.pre-edit.py')); old=importlib.util.module_from_spec(oldspec); oldspec.loader.exec_module(old)
a=m.sample_emission(old); b=m.sample_emission(m.runtime)
for i,line in enumerate(unified_diff(a.splitlines(), b.splitlines(), n=2)):
    if i<80: print(line)
    else: break
print('lengths',len(a),len(b))
PY
```

## 4. Corrected direct test — exit 0, 14 methods OK

```bash
python -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py
```

## 5. Earlier legacy suite — exit 1, 42 methods / 2 failures

```bash
python -B Audit/test_phase16_p3_runtime.py
```

## 6. Intermediate recorded run — exit 1, legacy suite 1 failure

```bash
python -B Audit/phase16-p3-data-hardening-2026-11-03g/run_checks.py
```

That recorder launched three subprocess commands, with exact executable and
statuses recorded in `results.json`:

```text
C:\Python314\python.exe -B Audit/phase16-p3-data-hardening-2026-11-03g/test_data_hardening.py
C:\Python314\python.exe -B Audit/phase16-p3-runtime-hardening-2026-11-03f/test_protection.py
C:\Python314\python.exe -B Audit/test_phase16_p3_runtime.py
```

## 7. Intermediate exact runtime snapshot and diff — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
from difflib import unified_diff
folder = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
old_path = folder / 'wall_surface_runtime.pre-edit.py'
new_path = Path('scripts/wall_surface_runtime.py')
old = old_path.read_bytes()
new = new_path.read_bytes()
expected_old = '3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf'
expected_new = 'ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2'
if sha256(old).hexdigest() != expected_old or sha256(new).hexdigest() != expected_new:
    raise SystemExit('STOP: snapshot/source drift; no post-edit snapshot or diff created')
post = folder / 'wall_surface_runtime.post-edit.py.bin'
with post.open('xb') as f:
    f.write(new)
if post.read_bytes() != new:
    raise SystemExit('STOP: post-edit snapshot readback mismatch')
diff = ''.join(unified_diff(old.decode('utf-8').splitlines(keepends=True), new.decode('utf-8').splitlines(keepends=True), fromfile='wall_surface_runtime.pre-edit.py', tofile='wall_surface_runtime.post-edit.py', n=3)).encode('utf-8')
with (folder / 'runtime.diff').open('xb') as f:
    f.write(diff)
for path in (old_path, new_path, post, folder / 'runtime.diff'):
    data = path.read_bytes()
    print(str(path), 'bytes=', len(data), 'sha256=', sha256(data).hexdigest())
PY
```

## 8. Intermediate test/runner exclusive snapshots — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
folder = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
for original, saved, expected in (
    ('test_data_hardening.py', 'test_data_hardening.v1.py.bin', '94ae49883cf1fd1396e1ec01a4ed7886103e0f0f3fa513db2260d5fe3b3cf46f'),
    ('run_checks.py', 'run_checks.v1.py.bin', 'd24f9e14f7eb54aae13cea9d84b3029803777c5f71048fcab588b9e3b765a2a7'),
):
    data = (folder / original).read_bytes()
    if sha256(data).hexdigest() != expected:
        raise SystemExit('STOP: intermediate file drift: ' + original)
    with (folder / saved).open('xb') as out:
        out.write(data)
    if (folder / saved).read_bytes() != data:
        raise SystemExit('STOP: intermediate snapshot mismatch: ' + saved)
    print(saved, len(data), sha256(data).hexdigest())
PY
```

## 9. V2 recorded run — exit 1, legacy suite 1 failure

```bash
python -B Audit/phase16-p3-data-hardening-2026-11-03g/run_checks.py v2
```

This launches the same three subprocess commands as §6; exact output, hashes,
input stability, Python AST checks and exits are in `v2-results.json`.

## 10. V2 exact runtime snapshot and diff — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
from difflib import unified_diff
folder = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
old_path = folder / 'wall_surface_runtime.pre-edit.py'
new_path = Path('scripts/wall_surface_runtime.py')
old, new = old_path.read_bytes(), new_path.read_bytes()
if sha256(old).hexdigest() != '3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf' or sha256(new).hexdigest() != '2503fbfcfbe1bc0480512f2f7e3fbcfe740a56f9478f37affdbddeeca8edf56a':
    raise SystemExit('STOP: source/snapshot drift')
snapshot = folder / 'wall_surface_runtime.final.py.bin'
with snapshot.open('xb') as f:
    f.write(new)
if snapshot.read_bytes() != new:
    raise SystemExit('STOP: final snapshot readback mismatch')
diff = ''.join(unified_diff(old.decode('utf-8').splitlines(keepends=True), new.decode('utf-8').splitlines(keepends=True), fromfile='wall_surface_runtime.pre-edit.py', tofile='wall_surface_runtime.final.py', n=3)).encode('utf-8')
diff_path = folder / 'runtime.final.diff'
with diff_path.open('xb') as f:
    f.write(diff)
for path in (old_path, new_path, snapshot, diff_path):
    data = path.read_bytes()
    print(str(path), 'bytes=', len(data), 'sha256=', sha256(data).hexdigest())
PY
```

## 11. Input/artifact/log re-hash — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
import json
p = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
ledger = json.loads((p / 'v2-results.json').read_text(encoding='utf-8'))
for name, expected in ledger['input_sha256_before'].items():
    actual = sha256(Path(name).read_bytes()).hexdigest()
    print(('MATCH' if actual == expected else 'DRIFT'), name, actual)
    if actual != expected:
        raise SystemExit('STOP: recorded input drift')
for name in ['wall_surface_runtime.pre-edit.py', 'wall_surface_runtime.post-edit.py.bin', 'wall_surface_runtime.final.py.bin', 'runtime.diff', 'runtime.final.diff', 'test_data_hardening.v1.py.bin', 'run_checks.v1.py.bin', 'results.json', 'v2-results.json', 'REPORT.md']:
    data = (p / name).read_bytes()
    print('ARTIFACT', name, len(data), sha256(data).hexdigest())
for suite in ledger['suites']:
    for kind, record in suite['logs'].items():
        actual = sha256(Path(record['path']).read_bytes()).hexdigest()
        if actual != record['sha256']:
            raise SystemExit('STOP: log drift ' + record['path'])
print('v2 raw logs all match recorded hashes')
PY
```

## 12. Reconstruct/hash-verify edited v2 test and runner — exit 0

The files had already changed when this command ran. These snapshots are
**reconstructed**, and were created only after matching the hashes in the v2
ledger; they are not contemporaneous captures.

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
p = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
test = (p / 'test_data_hardening.py').read_text(encoding='utf-8')
test = test.replace('p3RequireState (vn >= 0 and vn <= 100 and en >= 0 and en <= 100)', 'p3RequireState (vn >= 0 and vn <= 100 and en >= 0 and en <= 10)')
test = test.replace('("vn >= 0 and vn <= 100 and en >= 0 and en <= 100", "true")', '("vn >= 0 and vn <= 100 and en >= 0 and en <= 10", "true")')
needle = '        self.assertEqual(api.support_calls, list(range(1, 101)))\n'
extra = '''        api = FakeAPI(10, {i: False for i in range(1, 11)}, {})
        self.assertEqual(len(model_snapshot(api, 0, [], 256, channel_cap=10)), 10)
        self.assertEqual(api.support_calls, list(range(1, 11)))
        too_many = FakeAPI(11, {}, {})
        with self.assertRaises(Incomplete):
            model_snapshot(too_many, 0, [], 256, channel_cap=10)
        self.assertEqual(too_many.support_calls, [])
'''
if test.count(needle) != 1:
    raise SystemExit('STOP: cannot reconstruct v2 test uniquely')
test = test.replace(needle, needle + extra)
runner = (p / 'run_checks.py').read_text(encoding='utf-8')
runner = runner.replace('if len(sys.argv) != 2 or sys.argv[1] not in ("v2", "v3"):', 'if len(sys.argv) != 2 or sys.argv[1] != "v2":')
runner = runner.replace('expected the one-use output label: v2 or v3', 'expected the one-use output label: v2')
for name, value, expected in (
    ('test_data_hardening.v2.py.bin', test, '80ae5a26f8afd6e94c16b2d8b1d96a5eb24f5a67cae70bf7792f58eb557ff67a'),
    ('run_checks.v2.py.bin', runner, '84cd23d6297533fec6f28ab00573ca920d94708147e3390911b741930ba4cbfa'),
):
    data = value.encode('utf-8')
    digest = sha256(data).hexdigest()
    if digest != expected:
        raise SystemExit('STOP: reconstructed v2 hash mismatch: ' + name + ' ' + digest)
    with (p / name).open('xb') as out:
        out.write(data)
    if (p / name).read_bytes() != data:
        raise SystemExit('STOP: reconstructed v2 readback mismatch: ' + name)
    print(name, len(data), digest, 'reconstructed and verified')
PY
```

## 13. Final v3 recorded run — exit 1, legacy suite 1 failure

```bash
python -B Audit/phase16-p3-data-hardening-2026-11-03g/run_checks.py v3
```

The same three subprocess commands as §6 ran; `v3-results.json` records the
exact exits, Python AST checks, input hashes and raw-log hashes.

## 14. Final v3 exact runtime snapshot and diff — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
from difflib import unified_diff
p = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
old = (p / 'wall_surface_runtime.pre-edit.py').read_bytes()
new = Path('scripts/wall_surface_runtime.py').read_bytes()
if sha256(old).hexdigest() != '3a7a38dbd1ac3554fdeb63e6ae11acf0818ec1bd90afa71bb81e74f968973acf' or sha256(new).hexdigest() != 'ab806d2054fb9af74aaf0a4f43044450f8ffc1217d1f15331bea1b735364efc2':
    raise SystemExit('STOP: unexpected snapshot/source hash')
items = [
    ('wall_surface_runtime.v3-final.py.bin', new),
    ('runtime.v3-final.diff', ''.join(unified_diff(old.decode('utf-8').splitlines(keepends=True), new.decode('utf-8').splitlines(keepends=True), fromfile='wall_surface_runtime.pre-edit.py', tofile='wall_surface_runtime.v3-final.py', n=3)).encode('utf-8')),
]
for name, data in items:
    with (p / name).open('xb') as out:
        out.write(data)
    if (p / name).read_bytes() != data:
        raise SystemExit('STOP: readback mismatch ' + name)
    print(name, 'bytes=', len(data), 'sha256=', sha256(data).hexdigest())
PY
```

## 15. Final v3 input, evidence and documentation hash verification — exit 0

```bash
python -B - <<'PY'
from pathlib import Path
from hashlib import sha256
import json
p = Path('Audit/phase16-p3-data-hardening-2026-11-03g')
result = json.loads((p / 'v3-results.json').read_text(encoding='utf-8'))
for name, expected in result['input_sha256_before'].items():
    actual = sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit('STOP: input drift ' + name)
    print('MATCH', name, actual)
for suite in result['suites']:
    for record in suite['logs'].values():
        if sha256(Path(record['path']).read_bytes()).hexdigest() != record['sha256']:
            raise SystemExit('STOP: raw log drift ' + record['path'])
if Path('scripts/wall_surface_runtime.py').read_bytes() != (p / 'wall_surface_runtime.v3-final.py.bin').read_bytes():
    raise SystemExit('STOP: final source/snapshot mismatch')
for name in ('REPORT.md', 'COMMANDS.md', 'v3-results.json', 'runtime.v3-final.diff'):
    data = (p / name).read_bytes()
    print('ARTIFACT', name, len(data), sha256(data).hexdigest())
print('v3 source/snapshot, recorded inputs and raw logs match')
PY
```
