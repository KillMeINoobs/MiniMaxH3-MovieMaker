"""Create explicitly synthetic contract fixtures and a registration-only UI graph."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.contracts.example_data import project, segment, window, control, result, future_records, media, profile, spatial, audio, settings

if __name__ == '__main__':
    examples = {'project': project(), 'segment': segment(), 'generation_window': window(),
        'control_spec': control(), 'render_result': result(), **future_records(),
        'media_ref': media(), 'render_profile': profile(), 'spatial_transform': spatial(),
        'audio_timeline': audio(), 'settings': settings()}
    folder = ROOT / 'tests/contracts/fixtures'
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in examples.items():
        (folder / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    p = json.dumps(project(), ensure_ascii=False, indent=2)
    nodes = [
        {'id':1,'type':'KVD_ProjectJSON','pos':[30,80],'size':[450,540],'flags':{},'order':0,'mode':0,
         'inputs':[], 'outputs':[{'name':'project','type':'KVD_PROJECT','links':[1],'slot_index':0},
            {'name':'project_json','type':'STRING','links':None}, {'name':'validation_report','type':'STRING','links':None}],
         'properties':{'Node name for S&R':'KVD_ProjectJSON'},'widgets_values':[p]},
        {'id':2,'type':'KVD_ValidateProject','pos':[570,80],'size':[380,280],'flags':{},'order':1,'mode':0,
         'inputs':[{'name':'project','type':'KVD_PROJECT','link':1}],
         'outputs':[{'name':'project','type':'KVD_PROJECT','links':[2],'slot_index':0},
            {'name':'validation_report','type':'STRING','links':None}],
         'properties':{'Node name for S&R':'KVD_ValidateProject'},'widgets_values':[]},
        {'id':3,'type':'KVD_SaveProject','pos':[1040,80],'size':[410,340],'flags':{},'order':2,'mode':0,
         'inputs':[{'name':'project','type':'KVD_PROJECT','link':2}],
         'outputs':[{'name':'project','type':'KVD_PROJECT','links':None}, {'name':'saved_file','type':'STRING','links':None},
            {'name':'validation_report','type':'STRING','links':None}],
         'properties':{'Node name for S&R':'KVD_SaveProject'},'widgets_values':['','project.kvd.json',False]},
        {'id':4,'type':'KVD_LoadProject','pos':[570,410],'size':[410,310],'flags':{},'order':3,'mode':0,
         'inputs':[], 'outputs':[{'name':'project','type':'KVD_PROJECT','links':None},
            {'name':'project_json','type':'STRING','links':None}, {'name':'validation_report','type':'STRING','links':None}],
         'properties':{'Node name for S&R':'KVD_LoadProject'},'widgets_values':['','project.kvd.json']},
    ]
    workflow = {'last_node_id':4,'last_link_id':2,'nodes':nodes,
        'links':[[1,1,0,2,0,'KVD_PROJECT'],[2,2,0,3,0,'KVD_PROJECT']], 'groups':[],
        'config':{},'extra':{'kvd':{'purpose':'Synthetic metadata registration/UI fixture. Do not queue. Not a V2V generation workflow.',
            'gpu':'not_performed','schema_version':'2.0.0'}},'version':0.4}
    output = ROOT / 'workflows/foundation_project.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    web_output = ROOT / 'web/examples/foundation_project.json'
    web_output.parent.mkdir(exist_ok=True)
    web_output.write_bytes(output.read_bytes())
