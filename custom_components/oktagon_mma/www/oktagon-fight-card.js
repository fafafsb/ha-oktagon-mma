/* OKTAGON MMA — standalone Lovelace card, no frontend dependencies. */
class OktagonFightCard extends HTMLElement {
  static getConfigElement() {
    return document.createElement("oktagon-fight-card-editor");
  }
  static getStubConfig() { return {type: "custom:oktagon-fight-card", entity: "sensor.next_oktagon_fight_card"}; }
  constructor() {
    super();
    this.attachShadow({mode: "open"});
    this._expanded = false;
    this._config = {entity: "sensor.next_oktagon_fight_card"};
  }
  setConfig(config) {
    if (!config || (config.entity && typeof config.entity !== "string")) throw new Error("Invalid entity");
    this._config = {...config, entity: config.entity || "sensor.next_oktagon_fight_card"};
    this._render();
  }
  set hass(hass) { this._hass = hass; this._render(); }
  getCardSize() { return this._expanded ? 12 : 5; }
  _render() {
    if (!this.shadowRoot || !this._hass) return;
    const state = this._hass.states[this._config.entity];
    const attrs = state?.attributes || {};
    const fights = Array.isArray(attrs.fights) ? attrs.fights : [];
    const escape = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
    const image = url => typeof url === "string" && /^https:\/\/assets\.oktagonmma\.com\//.test(url)
      ? '<img loading="lazy" src="' + escape(url) + '" alt="">' : '<span class="placeholder">🥊</span>';
    const renderFight = (fight, main, number) => {
      const first = escape(fight.fighter_one || "TBA");
      const second = escape(fight.fighter_two || "TBA");
      return '<section class="fight ' + (main ? 'main' : '') + '">' +
        '<div class="meta"><span>' + (main ? '★ MAIN EVENT ★' : 'KAMPF ' + number) +
        '</span><span>' + escape(fight.weight_class || "Gewichtsklasse offen") + '</span></div>' +
        '<div class="match"><div class="fighter">' + image(fight.fighter_one_image) +
        '<strong>' + first + '</strong></div><b class="versus">VS</b><div class="fighter">' +
        image(fight.fighter_two_image) + '<strong>' + second + '</strong></div></div></section>';
    };
    const mainIndex = Math.max(0, fights.findIndex(f => f.main_event === true));
    const others = fights.filter((_, i) => i !== mainIndex);
    const html = '<style>:host{display:block}ha-card{display:block;background:linear-gradient(145deg,#1b1b1b,#090909);color:white;border:1px solid #48402a;border-radius:20px;padding:18px;box-sizing:border-box;font-family:inherit}' +
      '.eyebrow{color:#ffce22;font-size:11px;font-weight:800;letter-spacing:2px}.title{font-size:22px;font-weight:900;margin:7px 0;overflow-wrap:anywhere}.count{font-size:12px;color:#aaa;margin-bottom:16px}' +
      '.fight{background:#171717;border:1px solid #343434;border-radius:14px;padding:13px 12px;margin-top:9px}.fight.main{background:linear-gradient(145deg,#302711,#111);border:2px solid #c59a12;text-align:center;padding:16px 12px}' +
      '.meta{display:flex;justify-content:space-between;gap:8px;font-size:10px;font-weight:800;letter-spacing:.5px;margin-bottom:10px}.meta span:first-child{color:#ffce22}.meta span:last-child{color:#bbb}.main .meta{display:flex;flex-direction:column;align-items:center}' +
      '.match{display:grid;grid-template-columns:minmax(0,1fr) 38px minmax(0,1fr);gap:7px;align-items:center}.fighter{min-width:0;text-align:center}.fighter img{width:100%;height:68px;object-fit:contain;object-position:center bottom;display:block}.main .fighter img{height:175px}.fighter strong{display:block;font-size:13px;overflow-wrap:anywhere}.main .fighter strong{font-size:17px;margin-top:7px}.versus{color:#ffce22;text-align:center;font-size:16px}.main .versus{font-size:23px}.placeholder{display:grid;place-items:center;height:68px}.main .placeholder{height:175px}' +
      'button{display:block;width:100%;margin-top:12px;padding:14px;border-radius:12px;border:1px solid #a17d11;background:#242424;color:#ffce22;font-weight:800;font-size:13px;cursor:pointer}button:focus-visible{outline:2px solid #ffce22;outline-offset:2px}.empty{color:#aaa}</style>' +
      '<ha-card><div class="eyebrow">OKTAGON MMA · FIGHT CARD</div><div class="title">' +
      escape(attrs.event || "Nächstes OKTAGON Event") + '</div><div class="count">' + fights.length +
      ' Kämpfe</div>' + (fights.length ? renderFight(fights[mainIndex], true, mainIndex + 1) : '<p class="empty">Noch keine Fight Card verfügbar.</p>') +
      (this._expanded ? others.map((f, i) => renderFight(f, false, fights.indexOf(f) + 1)).join("") : "") +
      (others.length ? '<button type="button" id="toggle" aria-expanded="' + this._expanded + '">' +
      (this._expanded ? '▲ Kämpfe ausblenden' : '▼ Weitere ' + others.length + ' Kämpfe anzeigen') + '</button>' : '') +
      '</ha-card>';
    this.shadowRoot.innerHTML = html;
    const toggle = this.shadowRoot.getElementById("toggle");
    if (toggle) toggle.addEventListener("click", event => {event.stopPropagation(); this._expanded = !this._expanded; this._render();});
  }
}
if (!customElements.get("oktagon-fight-card")) customElements.define("oktagon-fight-card", OktagonFightCard);
window.customCards = window.customCards || [];
if (!window.customCards.some(card => card.type === "oktagon-fight-card")) window.customCards.push({
  type: "oktagon-fight-card", name: "OKTAGON Fight Card",
  description: "Official event pairings with an expandable fight card, no extra frontend dependencies."
});
class OktagonFightCardEditor extends HTMLElement {
  setConfig(config) { this._config = config; this.innerHTML = '<p>OKTAGON Fight Card — entity: ' + (config.entity || "sensor.next_oktagon_fight_card") + '</p>'; }
  set hass(hass) { this._hass = hass; }
}
if (!customElements.get("oktagon-fight-card-editor")) customElements.define("oktagon-fight-card-editor", OktagonFightCardEditor);
