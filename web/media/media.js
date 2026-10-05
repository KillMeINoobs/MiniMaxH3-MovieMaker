import {app} from '../../../scripts/app.js';
import {getLanguage, onLanguageChange} from '../common/presentation.js';
import {MEDIA_PRESENTATIONS, mediaStatus} from './presentation.js';

function refresh(node) {
  if (!node._kvdMediaSummary) return;
  node._kvdMediaSummary.lang = getLanguage();
  node._kvdMediaSummary.textContent = mediaStatus(node._kvdMediaReport);
}
app.registerExtension({
  name:'KVD.Media',
  setup() {
    const link = document.createElement('link'); link.rel = 'stylesheet';
    link.href = new URL('./media.css',import.meta.url).href; document.head.append(link);
    onLanguageChange(()=>{for (const node of app.graph?._nodes || []) refresh(node);});
  },
  nodeCreated(node) {
    if (!MEDIA_PRESENTATIONS[node.comfyClass || node.type] || node._kvdMediaSummary) return;
    const summary = document.createElement('p'); summary.className = 'kvd-media-summary';
    summary.setAttribute('role','status');
    const widget = node.addDOMWidget('kvd_media_summary','KVD_MEDIA_SUMMARY',summary,{serialize:false,hideOnZoom:false});
    widget.serialize = false; widget.serializeValue = ()=>undefined;
    widget.computeSize = width=>[width,42];
    node._kvdMediaSummary = summary;
    const original = node.onExecuted;
    node.onExecuted = function(message) {
      const returned = original?.call(this,message);
      this._kvdMediaReport = message?.kvd_report?.[0]; refresh(this); return returned;
    };
    node.size[0] = Math.max(node.size[0],420);
    refresh(node);
  },
  loadedGraphNode(node) {refresh(node);},
});
