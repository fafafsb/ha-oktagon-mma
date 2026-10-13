/* Native OKTAGON event overview card */
class OktagonEventCard extends HTMLElement {
  static getStubConfig() { return {type:"custom:oktagon-event-card"}; }
  constructor() { super(); this.attachShadow({mode:"open"}); this._config={}; }
  setConfig(config) { this._config=config || {}; this.render(); }
  set hass(value) { this._hass=value; this.render(); }
  getCardSize() { return 4; }
  render() {
    if (!this._hass) return;
    const get=(key,fallback="–")=>this._hass.states[this._config[key] || {
      event:"sensor.next_oktagon_event",days:"sensor.days_until_next_oktagon",
      date:"sensor.next_oktagon_date",location:"sensor.next_oktagon_location"
    }[key]]?.state || fallback;
    const escape=v=>String(v).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
    const title=get("event","Keine Daten");
    const match=title.match(/^(OKTAGON\s+\d+)(?:\s*:\s*(.*))?$/i);
    const eventName=match?match[1]:title;
    const fight=match?(match[2] || "Nächstes Event"):"Nächstes Event";
    const raw=get("date","");
    const date=/^\d{4}-\d{2}-\d{2}$/.test(raw)?raw.slice(8,10)+"."+raw.slice(5,7)+"."+raw.slice(0,4):"–";
    const cell=(label,value,sub,wide=false)=>'<div class="cell '+(wide?'wide':'')+'"><small>'+label+'</small><strong>'+escape(value)+'</strong><span>'+sub+'</span></div>';
    this.shadowRoot.innerHTML='<style>:host{display:block}ha-card{display:block;background:linear-gradient(145deg,#171717,#080808);color:#fff;border:1px solid #38342a;border-radius:22px;padding:18px;box-sizing:border-box;font-family:inherit}.heading{display:flex;gap:14px;align-items:center}.logo{width:64px;height:64px;object-fit:contain}.overline{font-size:11px;color:#aaa;letter-spacing:1.5px;font-weight:700}.title{font-size:25px;font-weight:850;line-height:1.1;margin:6px 0 3px}.subtitle{color:#ffcf22;font-size:13px;font-weight:750}.stats{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 12px;border-top:1px solid #343434;margin-top:17px;padding-top:17px}.cell{min-width:0}.cell small{display:block;color:#aaa;font-size:10px;letter-spacing:1px;font-weight:700;margin-bottom:7px}.cell strong{display:block;color:#ffcf22;font-size:24px;overflow-wrap:anywhere}.cell span{display:block;color:#aaa;font-size:11px;margin-top:5px}.cell.wide{grid-column:1/-1;border-top:1px solid #343434;padding-top:12px}.cell.wide strong{font-size:17px}.footer{border-top:1px solid #343434;margin-top:16px;padding-top:12px;color:#999;font-size:11px}</style>'+
      '<ha-card><div class="heading"><img class="logo" src="/oktagon_mma/icon.png" alt="OKTAGON"><div><div class="overline">NÄCHSTES EVENT</div><div class="title">'+escape(eventName)+'</div><div class="subtitle">'+escape(fight)+'</div></div></div>'+
      '<div class="stats">'+cell("COUNTDOWN",get("days"),"Tage")+cell("DATUM",date,"Nächstes Event")+cell("ORT",get("location"),"Veranstaltungsort",true)+'</div>'+
      '<div class="footer">🥊 OKTAGON MMA · Automatisch aktualisiert</div></ha-card>';
  }
}
if (!customElements.get("oktagon-event-card")) customElements.define("oktagon-event-card",OktagonEventCard);
window.customCards=window.customCards||[];
if (!window.customCards.some(x=>x.type==="oktagon-event-card")) window.customCards.push({type:"oktagon-event-card",name:"OKTAGON Event Card",description:"Next event, countdown, full date and venue."});
