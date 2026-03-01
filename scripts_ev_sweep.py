import json, yaml, pathlib, subprocess
root=pathlib.Path('.')
base=yaml.safe_load((root/'configs/stability_realdata.yaml').read_text(encoding='utf-8'))
profiles=[
    {'name':'p1','min_edge_bps':6.0,'cooldown_bars':2},
    {'name':'p2','min_edge_bps':4.0,'cooldown_bars':2},
    {'name':'p3','min_edge_bps':4.0,'cooldown_bars':1},
]
summary=[]
for p in profiles:
    cfg=dict(base)
    cfg['strategy']={'name':'ev_threshold','params':{'short_window':20,'long_window':50,'min_edge_bps':p['min_edge_bps'],'cooldown_bars':p['cooldown_bars']}}
    cfg_path=root/f"configs/stability_realdata_ev_{p['name']}.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding='utf-8')
    out_path=root/f"reports/robustness_walkforward_realdata_ev_{p['name']}.json"
    cmd=[str(root/'.venv/Scripts/python.exe'),'-m','edge_lab','walkforward','--config',str(cfg_path),'--output',str(out_path),'--train','756','--test','126','--step','63','--mode','dev']
    subprocess.run(cmd, check=True)
    data=json.loads(out_path.read_text(encoding='utf-8'))
    summary.append({
        'profile':p,
        'status':data['status'],
        'promotable':data['promotable'],
        'collapse_ratio':data['aggregate']['collapse_ratio'],
        'trades_total':data['aggregate']['trades_total'],
        'min_trades_window':min(data['validity']['observed_trades_per_window']) if data['validity']['observed_trades_per_window'] else 0,
        'failed_reasons':data['validity']['failed_reasons'],
    })
(root/'reports/phase3a_ev_sweep.json').write_text(json.dumps({'profiles':summary}, indent=2), encoding='utf-8')
print(json.dumps(summary, indent=2))
