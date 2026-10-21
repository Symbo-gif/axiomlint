"""Exact Python body executed via stdin ON LAPTOP ONLY during readiness review.

For reproduction from the authoritative laptop repo:
env -i PATH=/usr/local/bin:/usr/bin:/bin LANG=C.UTF-8 LC_ALL=C.UTF-8 TZ=UTC \
 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src:$PWD/tools:$PWD/tests" python3 -

All hypothetical state changes stay in Python objects; no live files are edited.
"""
from pathlib import Path
from unittest.mock import patch
import copy
from axiomlint.schema import load_json
import axiomlint.governance as g
import test_wp_001_ratification as r
import test_governance as t
from local_check import source_identity
root=Path.cwd()
before=source_identity(root)
sessions=load_json(root/'governance/sessions/index.json')
sessions[0].update(status='CLOSED', commit=before[0])
def closed_loader(path):
    if str(path).endswith('governance/sessions/index.json'):
        return copy.deepcopy(sessions)
    return load_json(path)
with patch.object(g,'load_json',side_effect=closed_loader):
    problems=g.check(root)
    print('S1_CLOSED_WITH_S2_BLOCKED_GOVERNANCE_ERRORS=',problems)
    assert not problems
case=r.RatificationTests('test_adoption_does_not_close_live_sessions_or_packages')
case.root=root
with patch.object(r,'load_json',side_effect=closed_loader):
    try:
        case.test_adoption_does_not_close_live_sessions_or_packages()
    except AssertionError as exc:
        print('REPRODUCED_PHASE_FREEZING_ASSERTION=',repr(str(exc)))
    else:
        raise RuntimeError('Expected original test failure was not reproduced')
state={}
def loader(path):
    if str(path).endswith('governance/sessions/index.json'):
        return copy.deepcopy(state.get('sessions',sessions))
    return load_json(path)
case2=t.GovernanceTests('test_s2_cannot_start_before_s1_closes')
case2.root=root
def mutate(path,fn):
    value=loader(root/path)
    fn(value)
    state['sessions']=value
case2.mutate=mutate
with patch.object(g,'load_json',side_effect=loader):
    try:
        case2.test_s2_cannot_start_before_s1_closes()
    except AssertionError as exc:
        print('REPRODUCED_NEGATIVE_FIXTURE_DEPENDS_ON_LIVE_S1_OPEN=',repr(str(exc)))
        print('S1_CLOSED_S2_IN_PROGRESS_GOVERNANCE_ERRORS=',g.check(root))
    else:
        raise RuntimeError('Expected original negative-fixture failure was not reproduced')
assert source_identity(root)==before
print('PROBE=PASS expected_assertion_failures=2 actual_source_unchanged=True')
print('All session state changes existed only in Python objects; no live records or tracked files edited.')
