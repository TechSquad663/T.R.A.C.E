import sys
sys.path.insert(0, '.')
errors = []
mods = [
    'ui.transactions.transaction_page',
    'ui.entities.entity_page',
    'ui.anomalies.anomaly_page',
    'ui.alerts.alerts_page',
    'ui.investigations.investigations_page',
    'ui.evidence.evidence_page',
    'ui.reports.reports_page',
    'ui.evaluation.evaluation_page',
    'ui.settings.settings_page',
    'ui.graph.graph_page',
]
for m in mods:
    name = m.split('.')[-1]
    try:
        __import__(m)
        print(f'OK: {name}')
    except Exception as e:
        print(f'FAIL: {name} -> {e}')
        errors.append(m)
print()
if errors:
    print(f'Result: {len(errors)} failures')
else:
    print('All imports OK')
