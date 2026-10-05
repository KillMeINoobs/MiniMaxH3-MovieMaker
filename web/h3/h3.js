import {app} from '../../../scripts/app.js';
import {api} from '../../../scripts/api.js';
import {OWN_IDS,reportText} from './presentation.mjs';
import {applyPresentation,getLanguage,onLanguageChange} from '../common/presentation.js';

const owned=node=>OWN_IDS.includes(node?.comfyClass||node?.type);
function refresh(node) {
  if(!owned(node)) return;
  applyPresentation(node);
  if(node._h3Panel) {
    node._h3Panel.lang=getLanguage();
    node._h3Panel.textContent=reportText(node._h3Report);
  }
}
app.registerExtension({
  name:'KVD.H3',
  setup() {
    onLanguageChange(()=>{for(const node of app.graph?._nodes||[]) refresh(node);});
    api.addEventListener('execution_error',event=>{
      const node=app.graph?.getNodeById(event.detail?.node_id);
      if(!owned(node)) return;
      node._h3Report={code:String(event.detail?.exception_message||'').match(/\b([A-Z][A-Z_]+):/)?.[1]||'INVALID_RECORD'};
      refresh(node);
    });
  },
  nodeCreated(node) {
    if(!owned(node)) return;
    const panel=document.createElement('p');
    panel.className='kvd-panel__status'; panel.setAttribute('aria-live','polite');
    const widget=node.addDOMWidget('h3_status','KVD_H3_STATUS',panel,{serialize:false,hideOnZoom:false});
    widget.serialize=false; widget.serializeValue=()=>undefined; widget.computeSize=width=>[width,48];
    node._h3Panel=panel;
    const previous=node.onExecuted;
    node.onExecuted=function(message) {
      const out=previous?.call(this,message);
      this._h3Report=message?.h3_report?.[0]||this._h3Report;
      refresh(this);
      return out;
    };
    refresh(node);
  },
  loadedGraphNode(node){refresh(node);},
  afterConfigureGraph(){for(const node of app.graph?._nodes||[]) refresh(node);},
});
