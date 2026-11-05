/* ai-model-benchmarks — shared language handling and page rendering.
   Plain ES2020, no dependencies. All data goes into the DOM through
   createElement/createElementNS and textContent; innerHTML, eval and
   new Function are not used. Colours and classes come from fixed maps,
   never from data strings. */

(function () {
  'use strict';

  var LANG_KEY = 'ai-model-benchmarks:lang';
  var LANGS = ['tr', 'en'];

  var UI = {
    en: {
      /* index */
      indexTitle: 'Model benchmarks',
      indexLede: 'Benchmark reports, designed, run and verified by Claude Opus 5.5 (Claude Code), for Hasan Furkan (HFK).',
      openReport: 'Open report',
      reportsEmpty: 'No benchmarks published yet.',
      benchmarksLabel: 'Benchmarks',
      readReport: 'Read the report',

      /* report shell */
      reportLabel: 'Benchmark report',
      decision: 'Decision',
      sectionsNav: 'Report sections',
      whoTitle: 'Who ran this',
      owner: 'Owner',
      manager: 'Manager — tests and verification',
      setupTitle: 'Setup',
      model: 'Model',
      levels: 'Levels exposed',
      noXhigh: 'No xhigh',
      clamp: 'Claude Code clamp',
      harness: 'Harness',
      machine: 'Machine',
      agentsTitle: 'Runs and agents',
      codingRuns: 'Coding-agent runs',
      blindReviewers: 'Blind reviewers',
      directApi: 'Direct API calls',
      smokeRuns: 'Smoke-test runs',
      effortProbes: 'Effort probes',
      managerRuns: 'Manager',
      costTitle: 'Cost',
      dashboardCaption: 'OpenCode Go quota dashboard (manager account)',
      before: 'Before',
      after: 'After',
      rolling: 'Short-term quota (rolling window)',
      weekly: 'Weekly quota',
      monthly: 'Monthly quota',
      todayUsd: 'Today, USD',
      todayRequests: 'Today, requests',
      todayTokens: 'Today, tokens',
      perArmCaption: 'Coding-agent runs per arm',
      apiCallsCaption: 'Direct API calls per arm',
      runs: 'Runs',
      cost: 'Cost',
      minutes: 'Minutes',
      inputTokens: 'Input tokens',
      outputTokens: 'Output tokens',
      reasoningTokens: 'Reasoning tokens',
      cacheReadTokens: 'Cache-read tokens',
      calls: 'Calls',
      pricingUsed: 'Pricing used',
      realTitle: 'Real project tasks',
      realCaption: 'Per task and arm',
      task: 'Task',
      arm: 'Arm',
      duration: 'Duration',
      reasoning: 'Reasoning',
      gate: 'Gate',
      blindScore: 'Blind score',
      note: 'Note',
      metric: 'Measure',
      blindTotal: 'Blind review total',
      passed: 'passed',
      trapsTitle: 'Traps',
      hiddenTest: 'What the hidden test measures',
      hiddenPassed: 'Hidden tests',
      contaminated: 'contaminated',
      phantomTitle: 'Phantom bug',
      phantomApi: 'Direct API',
      phantomProject: 'Real project',
      complaint: 'What was reported',
      result: 'What happened',
      verdict: 'Verdict',
      isolationTitle: 'Isolation incident',
      plantedTitle: 'Planted errors',
      plantedCaption: 'Errors found, by round and arm',
      plantedRound: 'Round',
      hardTitle: 'Hard questions',
      hardCaption: 'Answers by token cap and arm',
      question: 'Question',
      cap64: '64k cap',
      cap300: '300k cap',
      conclusionsTitle: 'Conclusions',
      limitationsTitle: 'Limitations',
      nextTitle: 'Next steps',
      chosen: 'chosen',
      loadErrorBody: 'Open this page from a web server (for example',
      loadErrorHint: 'Opening the file directly with file:// blocks fetch().',

      /* generic layout */
      best: '(best)',
      lowest: 'lowest',
      dataTable: 'Data table',
      mean: 'mean',
      minLabel: 'min',
      medianLabel: 'median',
      maxLabel: 'max',
      armLabel: 'Arm',
      valueLabel: 'Value',
      runLabel: 'Run',
      totalLabel: 'Total',
      chartEmpty: 'No chart data.'
    },
    tr: {
      indexTitle: 'Model benchmarkları',
      indexLede: 'Claude Opus 5.5 (Claude Code) tarafından tasarlanan, çalıştırılan ve doğrulanan; Hasan Furkan (HFK) için hazırlanan benchmark raporları.',
      openReport: 'Raporu aç',
      reportsEmpty: 'Henüz yayımlanmış benchmark yok.',
      benchmarksLabel: 'Benchmarklar',
      readReport: 'Raporu oku',

      reportLabel: 'Benchmark raporu',
      decision: 'Karar',
      sectionsNav: 'Rapor bölümleri',
      whoTitle: 'Kim yaptı',
      owner: 'Sahip',
      manager: 'Yönetici — testler ve doğrulama',
      setupTitle: 'Kurulum',
      model: 'Model',
      levels: 'Sunulan seviyeler',
      noXhigh: 'xhigh yok',
      clamp: "Claude Code'un kısıtlaması",
      harness: 'Düzenek',
      machine: 'Makine',
      agentsTitle: 'Koşular ve ajanlar',
      codingRuns: 'Kodlama ajanı koşusu',
      blindReviewers: 'Kör inceleyici',
      directApi: 'Doğrudan API çağrısı',
      smokeRuns: 'Duman testi koşusu',
      effortProbes: 'Effort denemeleri',
      managerRuns: 'Yönetici',
      costTitle: 'Maliyet',
      dashboardCaption: 'OpenCode Go kota paneli (yönetici hesabı)',
      before: 'Önce',
      after: 'Sonra',
      rolling: 'Kısa süreli kota (kayan pencere)',
      weekly: 'Haftalık kota',
      monthly: 'Aylık kota',
      todayUsd: 'Bugün, $',
      todayRequests: 'Bugün, istek',
      todayTokens: 'Bugün, token',
      perArmCaption: 'Kol başına kodlama ajanı koşuları',
      apiCallsCaption: 'Kol başına doğrudan API çağrısı',
      runs: 'Koşu',
      cost: 'Maliyet',
      minutes: 'Dakika',
      inputTokens: 'Girdi token',
      outputTokens: 'Çıktı token',
      reasoningTokens: 'Düşünme token',
      cacheReadTokens: 'Önbellek okuma token',
      calls: 'Çağrı',
      pricingUsed: 'Kullanılan fiyat',
      realTitle: 'Gerçek proje görevleri',
      realCaption: 'Görev ve kol başına',
      task: 'Görev',
      arm: 'Kol',
      duration: 'Süre',
      reasoning: 'Düşünme',
      gate: 'Kapı',
      blindScore: 'Kör puan',
      note: 'Not',
      metric: 'Ölçü',
      blindTotal: 'Kör puan toplamı',
      passed: 'geçti',
      trapsTitle: 'Tuzaklı görevler',
      hiddenTest: 'Gizli testin ölçtüğü şey',
      hiddenPassed: 'Gizli testler',
      contaminated: 'kirli',
      phantomTitle: 'Hayalet hata',
      phantomApi: 'Doğrudan API',
      phantomProject: 'Gerçek proje',
      complaint: 'Bildirilen şikâyet',
      result: 'Ne oldu',
      verdict: 'Karar',
      isolationTitle: 'Yalıtım olayı',
      plantedTitle: 'Bilerek konmuş hatalar',
      plantedCaption: 'Bulunan hatalar, tur ve kol başına',
      plantedRound: 'Tur',
      hardTitle: 'Zor sorular',
      hardCaption: 'Token tavanı ve kola göre cevaplar',
      question: 'Soru',
      cap64: '64k tavan',
      cap300: '300k tavan',
      conclusionsTitle: 'Sonuçlar',
      limitationsTitle: 'Sınırlamalar',
      nextTitle: 'Sonraki adımlar',
      chosen: 'seçilen',
      loadErrorBody: 'Bu sayfayı bir web sunucusundan açın (ör.',
      loadErrorHint: 'Dosyayı doğrudan file:// ile açmak fetch() çağrısını engeller.',

      best: '(en iyi)',
      lowest: 'en düşük',
      dataTable: 'Veri tablosu',
      mean: 'ortalama',
      minLabel: 'en kısa',
      medianLabel: 'medyan',
      maxLabel: 'en uzun',
      armLabel: 'Kol',
      valueLabel: 'Değer',
      runLabel: 'Koşu',
      totalLabel: 'Toplam',
      chartEmpty: 'Grafik verisi yok.'
    }
  };

  var lang = 'en';
  var rerender = null;
  var activeRedraw = null;
  var chartQueue = [];
  var reportArms = Object.create(null);
  var uid = 0;

  function L(key) {
    var table = UI[lang] || UI.en;
    return table[key] !== undefined ? table[key] : UI.en[key];
  }

  function t(value) {
    if (value && typeof value === 'object') {
      if (typeof value[lang] === 'string') return value[lang];
      if (typeof value.en === 'string') return value.en;
      if (typeof value.tr === 'string') return value.tr;
      return '';
    }
    return value === null || value === undefined ? '' : String(value);
  }

  function tList(value) {
    if (Array.isArray(value)) return value;
    if (value && typeof value === 'object') {
      if (Array.isArray(value[lang])) return value[lang];
      if (Array.isArray(value.en)) return value.en;
      if (Array.isArray(value.tr)) return value.tr;
    }
    return [];
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function isObject(value) {
    return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
  }

  function locale() {
    return lang === 'tr' ? 'tr-TR' : 'en-US';
  }

  function readStoredLang() {
    try {
      var saved = window.localStorage.getItem(LANG_KEY);
      if (saved === 'tr' || saved === 'en') return saved;
    } catch (err) {
      /* storage blocked: fall through to the browser setting */
    }
    var nav = (navigator.language || '').toLowerCase();
    return nav.indexOf('tr') === 0 ? 'tr' : 'en';
  }

  function persistLang() {
    try {
      window.localStorage.setItem(LANG_KEY, lang);
    } catch (err) {
      /* storage blocked: the choice simply lasts for this page */
    }
  }

  function updateButtons() {
    var buttons = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < buttons.length; i += 1) {
      var value = buttons[i].getAttribute('data-lang');
      buttons[i].setAttribute('aria-pressed', value === lang ? 'true' : 'false');
    }
  }

  function setLang(next) {
    if (LANGS.indexOf(next) === -1 || next === lang) return;
    lang = next;
    document.documentElement.lang = lang;
    updateButtons();
    persistLang();
    if (rerender) rerender();
  }

  /* ---------- formatters ---------- */

  function fmtInt(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    try {
      return new Intl.NumberFormat(locale()).format(n);
    } catch (err) {
      return String(n);
    }
  }

  function fmtUsd(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    // Fixed precision keeps columns comparable: $0.194 next to $0.200, not $0.20.
    return '$' + n.toFixed(n < 1 ? 3 : 2);
  }

  function fmtPercent(value) {
    if (value === null || value === undefined) return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    return fmtInt(n) + '%';
  }

  function fmtSeconds(total) {
    if (total === null || total === undefined || total === '') return '—';
    var n = Number(total);
    if (!isFinite(n)) return '—';
    var whole = Math.round(n);
    var m = Math.floor(whole / 60);
    var s = whole % 60;
    if (m === 0) return lang === 'tr' ? s + ' sn' : s + ' s';
    return lang === 'tr' ? m + ' dk ' + s + ' sn' : m + ' min ' + s + ' s';
  }

  function fmtMinutes(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    var rounded = Math.round(n * 10) / 10;
    return numberFixed(rounded, 1, 1) + (lang === 'tr' ? ' dk' : ' min');
  }

  function numberFixed(value, minDigits, maxDigits) {
    try {
      return new Intl.NumberFormat(locale(), {
        minimumFractionDigits: minDigits,
        maximumFractionDigits: maxDigits
      }).format(value);
    } catch (err) {
      return Number(value).toFixed(maxDigits);
    }
  }

  function fmtMoney(value, digits) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    var body = numberFixed(n, digits, digits);
    return lang === 'tr' ? body + ' $' : '$' + body;
  }

  function fmtDec(value, digits) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    return numberFixed(n, digits, digits);
  }

  /* Block and chart formatter: fmt in usd3 | usd4 | int | seconds | dec2. */
  function fmtValue(value, fmt) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return '—';
    switch (fmt) {
      case 'usd3':
        return fmtMoney(n, 3);
      case 'usd4':
        return fmtMoney(n, 4);
      case 'seconds':
        return fmtSeconds(n);
      case 'dec2':
        return fmtDec(n, 2);
      case 'int':
      default:
        return fmtInt(n);
    }
  }

  function fmtDate(iso) {
    if (typeof iso !== 'string') return '';
    var match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    if (!match) return iso;
    var date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
    try {
      return new Intl.DateTimeFormat(lang === 'tr' ? 'tr-TR' : 'en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        timeZone: 'UTC'
      }).format(date);
    } catch (err) {
      return iso;
    }
  }

  function shortManager(value) {
    var text = t(value);
    if (!text) return '';
    var cut = text.split(/[(,–—]/)[0];
    cut = cut.replace(/\s+/g, ' ').trim();
    if (cut.length > 48) cut = cut.slice(0, 47).trim() + '…';
    return cut;
  }

  function toNumber(value) {
    if (value === null || value === undefined || value === '') return null;
    var n = Number(value);
    return isFinite(n) ? n : null;
  }

  function clamp(n, low, high) {
    return Math.min(high, Math.max(low, n));
  }

  function fetchJSON(url) {
    return fetch(url, { cache: 'no-cache', headers: { Accept: 'application/json' } }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    });
  }

  /* ---------- DOM builders shared by both pages ---------- */

  function el(tag, opts, children) {
    var node = document.createElement(tag);
    if (opts) {
      if (opts.cls) node.className = opts.cls;
      if (opts.text !== undefined && opts.text !== null) node.textContent = t(opts.text);
      if (opts.attrs) {
        Object.keys(opts.attrs).forEach(function (name) {
          var v = opts.attrs[name];
          if (v !== null && v !== undefined) node.setAttribute(name, String(v));
        });
      }
    }
    append(node, children);
    return node;
  }

  function append(node, children) {
    if (children === null || children === undefined || children === false) return;
    if (Array.isArray(children)) {
      children.forEach(function (child) { append(node, child); });
      return;
    }
    if (children instanceof Node) {
      node.appendChild(children);
      return;
    }
    // Any data field may be a plain string or a {tr, en} pair.
    node.appendChild(document.createTextNode(t(children)));
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  var SVG_NS = 'http://www.w3.org/2000/svg';

  function svgEl(name, attrs) {
    var node = document.createElementNS(SVG_NS, name);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        var value = attrs[key];
        if (value !== null && value !== undefined) node.setAttribute(key, String(value));
      });
    }
    return node;
  }

  function svgText(x, y, text, cls, anchor) {
    var node = svgEl('text', { x: x, y: y, 'text-anchor': anchor || 'start' });
    if (cls) node.setAttribute('class', cls);
    node.textContent = String(text);
    return node;
  }

  function svgTitle(text) {
    var node = svgEl('title');
    node.textContent = String(text);
    return node;
  }

  var ICONS = {
    notebook: ['M6 3.5h12a.75.75 0 0 1 .75.75v15.5a.75.75 0 0 1-.75.75H6a.75.75 0 0 1-.75-.75V4.25A.75.75 0 0 1 6 3.5Z', 'M9.25 3.5v17', 'M12.75 9h3.5', 'M12.75 13h3.5'],
    check: ['m5 12.5 4.5 4.5L19 7'],
    alert: ['M12 4 2.75 20h18.5L12 4Z', 'M12 10v4', 'M12 17.4h.01'],
    info: ['M12 3.25a8.75 8.75 0 1 0 0 17.5 8.75 8.75 0 0 0 0-17.5Z', 'M12 11v5', 'M12 8h.01'],
    inbox: ['M4.5 13.5h3.75l1.75 2.75h4l1.75-2.75h3.75', 'M3.75 13.5 5.5 4.75h13l1.75 8.75v5.75H3.75V13.5Z'],
    arrow: ['M5 12h14', 'm13 6 6 6-6 6'],
    external: ['M7.5 16.5 16.5 7.5', 'M9 7.5h7.5V15']
  };

  function icon(name, cls) {
    var node = svgEl('svg', {
      viewBox: '0 0 24 24',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': '1.75',
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      'aria-hidden': 'true',
      focusable: 'false'
    });
    if (cls) node.setAttribute('class', cls);
    asArray(ICONS[name]).forEach(function (d) {
      node.appendChild(svgEl('path', { d: d }));
    });
    return node;
  }

  function decorateBrands() {
    var brands = document.querySelectorAll('.brand');
    for (var i = 0; i < brands.length; i += 1) {
      var brand = brands[i];
      if (!brand || brand.querySelector('.brand-mark')) continue;
      var name = el('span', { cls: 'brand-name' });
      var nodes = [];
      for (var j = 0; j < brand.childNodes.length; j += 1) nodes.push(brand.childNodes[j]);
      nodes.forEach(function (node) {
        if (node.nodeType === 3) name.appendChild(node);
      });
      if (name.firstChild) brand.appendChild(name);
      var mark = el('span', { cls: 'brand-mark' });
      mark.appendChild(icon('notebook'));
      brand.insertBefore(mark, brand.firstChild);
    }
  }

  /* ---------- small builders ---------- */

  function sectionTitle(text) {
    return el('h2', { cls: 'section-title', text: text });
  }

  function chosenTag() {
    var tag = el('span', { cls: 'chosen-tag' });
    tag.appendChild(icon('check'));
    tag.appendChild(el('span', { text: L('chosen') }));
    return tag;
  }

  function chip(tone, text) {
    var node = el('span', { cls: 'chip ' + toneToClass(tone) });
    node.appendChild(el('span', { cls: 'chip-dot' }));
    node.appendChild(el('span', { text: text }));
    return node;
  }

  function toneToClass(tone) {
    if (tone === 'pass') return 'chip-pass';
    if (tone === 'warn') return 'chip-warn';
    if (tone === 'info') return 'chip-info';
    return 'chip-neutral';
  }

  function calloutTone(tone) {
    return tone === 'warn' ? 'callout-warn' : tone === 'info' ? 'callout-info' : 'callout-neutral';
  }

  function armKeyClass(key) {
    var k = typeof key === 'string' ? key.toUpperCase() : '';
    if (k === 'A') return 'arm-a';
    if (k === 'B') return 'arm-b';
    if (k === 'C') return 'arm-c';
    return 'arm-neutral';
  }

  function armLetter(key) {
    if (typeof key === 'string' && key.length) return key.charAt(0).toUpperCase();
    return '—';
  }

  function armName(key) {
    if (typeof key === 'string' && Object.prototype.hasOwnProperty.call(reportArms, key)) {
      var name = t(reportArms[key].name);
      if (name) return name;
    }
    return typeof key === 'string' && key ? key : '—';
  }

  function armBadge(key) {
    return el('span', { cls: 'arm-badge ' + armKeyClass(key), text: armLetter(key) });
  }

  function badgePass(text) {
    return el('span', { cls: 'badge pass', text: text });
  }

  function badgeDirty() {
    /* both words on purpose: the badge has to read the same in either language */
    return el('span', { cls: 'badge dirty', text: L('contaminated') });
  }

  function personCard(role, body) {
    var card = el('div', { cls: 'person' });
    card.appendChild(el('span', { cls: 'role', text: role }));
    card.appendChild(el('p', { text: body }));
    return card;
  }

  function addKV(list, term, value) {
    var row = el('div');
    row.appendChild(el('dt', { text: term }));
    var dd = el('dd');
    append(dd, value);
    row.appendChild(dd);
    list.appendChild(row);
  }

  function statCard(name, value, detail) {
    var card = el('div', { cls: 'stat' });
    card.appendChild(el('span', { cls: 'num', text: fmtInt(value) }));
    card.appendChild(el('span', { cls: 'name', text: name }));
    if (detail) card.appendChild(el('span', { cls: 'detail', text: detail }));
    return card;
  }

  function normalizeCell(spec) {
    if (spec instanceof Node) return { content: spec };
    if (isObject(spec)) return spec;
    return { content: spec };
  }

  function buildTable(caption, headSpecs, bodyRows) {
    var labelText = caption ? t(caption) : L('dataTable');
    var wrap = el('div', {
      cls: 'table-scroll',
      attrs: { role: 'region', tabindex: '0', 'aria-label': labelText }
    });
    var table = el('table', { cls: 'data-table' });
    if (caption) table.appendChild(el('caption', { text: caption }));

    var thead = el('thead');
    var headRow = el('tr');
    asArray(headSpecs).forEach(function (spec) {
      spec = isObject(spec) ? spec : { text: spec };
      var cls = [];
      if (spec.num) cls.push('num');
      if (spec.arm) cls.push(armKeyClass(spec.arm));
      if (spec.chosen) cls.push('is-chosen');
      var th = el('th', { cls: cls.join(' '), attrs: { scope: 'col' } }, spec.text);
      if (spec.chosen) {
        th.appendChild(document.createTextNode(' '));
        th.appendChild(chosenTag());
      }
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    asArray(bodyRows).forEach(function (rowSpec) {
      rowSpec = isObject(rowSpec) ? rowSpec : { cells: [] };
      var tr = el('tr', { cls: rowSpec.cls || '' });
      asArray(rowSpec.cells).forEach(function (raw, index) {
        renderTableCell(tr, raw, index, headSpecs);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function renderTableCell(tr, raw, index, headSpecs) {
    var spec = normalizeCell(raw);
    var column = asArray(headSpecs)[index];
    column = isObject(column) ? column : {};
    var isRowHead = Boolean(spec.th);
    var cls = [];
    if (spec.cls) cls.push(spec.cls);
    if (spec.num || column.num) cls.push('num');
    if (spec.chosen) cls.push('is-chosen');
    var cell = el(isRowHead ? 'th' : 'td', { cls: cls.join(' ') });
    if (isRowHead) {
      cell.setAttribute('scope', 'row');
      if (spec.rowspan && spec.rowspan > 1) cell.setAttribute('rowspan', String(spec.rowspan));
    }

    if (spec.v !== undefined) {
      var text = fmtValue(spec.v, spec.fmt);
      if (spec.best) {
        cell.className = (cell.className + ' cell-best').trim();
        cell.appendChild(el('span', { cls: 'best-pill', text: text }));
        cell.appendChild(el('span', { cls: 'sr-only', text: ' ' + L('best') }));
      } else {
        cell.appendChild(document.createTextNode(text));
      }
      tr.appendChild(cell);
      return cell;
    }
    if (spec.content !== undefined) {
      append(cell, spec.content);
    } else if (spec.tr !== undefined || spec.en !== undefined) {
      append(cell, spec);
    } else {
      cell.textContent = '—';
    }
    tr.appendChild(cell);
  }

  function notesNote(text) {
    return el('p', { cls: 'table-note', text: text });
  }

  function armBox(heading, chosen, dirty, facts, note) {
    var box = el('div', { cls: 'arm-box' + (chosen ? ' is-chosen' : '') });
    var head = el('div', { cls: 'arm-head' });
    head.appendChild(el('span', { cls: 'badge arm', text: heading }));
    if (chosen) head.appendChild(chosenTag());
    if (dirty) head.appendChild(badgeDirty());
    box.appendChild(head);
    if (facts && facts.length) box.appendChild(el('p', { cls: 'facts', text: facts.join(' · ') }));
    if (note) box.appendChild(el('p', { text: note }));
    return box;
  }

  function errorParagraph(body, hint) {
    var p = el('p');
    append(p, body + ' ');
    p.appendChild(el('code', { text: 'python -m http.server' }));
    append(p, '). ' + hint);
    return p;
  }

  function calloutBlock(tone, title, text, headingTag) {
    var box = el('div', { cls: 'callout ' + calloutTone(tone) });
    var holder = el('span', { cls: 'callout-icon' });
    holder.appendChild(icon(tone === 'warn' ? 'alert' : 'info'));
    box.appendChild(holder);
    var body = el('div', { cls: 'callout-body' });
    if (title !== null && title !== undefined && t(title) !== '') {
      body.appendChild(el(headingTag || 'h3', { cls: 'callout-title', text: title }));
    }
    body.appendChild(el('p', { cls: 'callout-text', text: text }));
    box.appendChild(body);
    return box;
  }

  function showLoadError(root, fileName) {
    clear(root);
    document.documentElement.lang = lang;
    activeRedraw = null;
    chartQueue = [];
    var box = el('div', { cls: 'notice', attrs: { role: 'alert' } });
    var holder = el('span', { cls: 'notice-icon' });
    holder.appendChild(icon('alert'));
    box.appendChild(holder);
    var body = el('div', { cls: 'notice-body' });
    body.appendChild(el('strong', { text: 'Rapor verisi yüklenemedi / Could not load the data' }));
    body.appendChild(el('p', { cls: 'mono', text: fileName }));
    body.appendChild(errorParagraph(UI.tr.loadErrorBody, UI.tr.loadErrorHint));
    body.appendChild(errorParagraph(UI.en.loadErrorBody, UI.en.loadErrorHint));
    box.appendChild(body);
    root.appendChild(box);
  }

  /* ---------- report page: old layout (contract 7.3) ---------- */

  function renderReport(root, data) {
    clear(root);
    chartQueue = [];
    activeRedraw = null;
    document.title = t(data.title) + ' — ai-model-benchmarks';
    var frag = document.createDocumentFragment();

    var header = el('header', { cls: 'page-header report-header' });
    header.appendChild(el('p', { cls: 'page-label eyebrow', text: L('reportLabel') }));
    header.appendChild(el('h1', { text: t(data.title) }));
    header.appendChild(el('p', { cls: 'meta-line', text: fmtDate(data.date) }));
    frag.appendChild(header);

    /* who */
    frag.appendChild(sectionTitle(L('whoTitle')));
    var people = el('div', { cls: 'grid-1' });
    people.appendChild(personCard(L('manager'), (data.people || {}).manager));
    frag.appendChild(people);

    /* setup */
    var setup = isObject(data.setup) ? data.setup : {};
    frag.appendChild(sectionTitle(L('setupTitle')));
    var setupCard = el('div', { cls: 'card' });
    var kv = el('dl', { cls: 'kv' });
    addKV(kv, L('model'), setup.model);
    var pills = el('div', { cls: 'pill-row' });
    asArray(setup.levels_available).forEach(function (level) {
      pills.appendChild(el('span', { cls: 'pill', text: level }));
    });
    addKV(kv, L('levels'), pills);
    addKV(kv, L('noXhigh'), setup.no_xhigh);
    addKV(kv, L('clamp'), setup.claude_code_clamp);
    addKV(kv, L('harness'), setup.harness);
    addKV(kv, L('machine'), setup.machine);
    setupCard.appendChild(kv);
    frag.appendChild(setupCard);

    /* agents */
    var agents = isObject(data.agents) ? data.agents : {};
    frag.appendChild(sectionTitle(L('agentsTitle')));
    var stats = el('div', { cls: 'stats' });
    stats.appendChild(statCard(L('codingRuns'), agents.coding_agent_runs, agents.coding_agent_runs_detail));
    stats.appendChild(statCard(L('blindReviewers'), agents.blind_reviewers, agents.blind_reviewers_detail));
    stats.appendChild(statCard(L('directApi'), agents.direct_api_calls, agents.direct_api_calls_detail));
    stats.appendChild(statCard(L('smokeRuns'), agents.smoke_test_runs));
    stats.appendChild(statCard(L('effortProbes'), agents.effort_probe_runs));
    stats.appendChild(statCard(L('managerRuns'), agents.manager));
    frag.appendChild(stats);

    /* cost */
    var cost = isObject(data.cost) ? data.cost : {};
    frag.appendChild(sectionTitle(L('costTitle')));
    var before = isObject(cost.go_dashboard_before) ? cost.go_dashboard_before : {};
    var after = isObject(cost.go_dashboard_after) ? cost.go_dashboard_after : {};
    frag.appendChild(buildTable(L('dashboardCaption'), [
      { text: L('metric') },
      { text: L('before') },
      { text: L('after') }
    ], [
      { cells: [{ th: true, content: L('rolling') }, { content: fmtPercent(before.rolling_pct) }, { content: fmtPercent(after.rolling_pct) }] },
      { cells: [{ th: true, content: L('weekly') }, { content: fmtPercent(before.weekly_pct) }, { content: fmtPercent(after.weekly_pct) }] },
      { cells: [{ th: true, content: L('monthly') }, { content: fmtPercent(before.monthly_pct) }, { content: fmtPercent(after.monthly_pct) }] },
      { cells: [{ th: true, content: L('todayUsd') }, { content: fmtUsd(before.today_usd) }, { content: fmtUsd(after.today_usd) }] },
      { cells: [{ th: true, content: L('todayRequests') }, { content: fmtInt(before.today_requests) }, { content: fmtInt(after.today_requests) }] },
      { cells: [{ th: true, content: L('todayTokens') }, { content: '—' }, { content: after.today_tokens || '—' }] }
    ]));

    var perArm = isObject(cost.per_arm_agent_runs) ? cost.per_arm_agent_runs : {};
    var highRuns = isObject(perArm.high) ? perArm.high : {};
    var maxRuns = isObject(perArm.max) ? perArm.max : {};
    frag.appendChild(buildTable(L('perArmCaption'), [
      { text: L('metric') },
      { text: 'high', cls: 'num', chosen: true },
      { text: 'max', cls: 'num' }
    ], [
      { cells: [{ th: true, content: L('runs') }, { content: fmtInt(highRuns.runs), cls: 'num is-chosen' }, { content: fmtInt(maxRuns.runs), cls: 'num' }] },
      { cells: [{ th: true, content: L('cost') }, { content: fmtUsd(highRuns.usd), cls: 'num is-chosen' }, { content: fmtUsd(maxRuns.usd), cls: 'num' }] },
      { cells: [{ th: true, content: L('minutes') }, { content: fmtMinutes(highRuns.minutes), cls: 'num is-chosen' }, { content: fmtMinutes(maxRuns.minutes), cls: 'num' }] },
      { cells: [{ th: true, content: L('inputTokens') }, { content: fmtInt(highRuns.input_tokens), cls: 'num is-chosen' }, { content: fmtInt(maxRuns.input_tokens), cls: 'num' }] },
      { cells: [{ th: true, content: L('outputTokens') }, { content: fmtInt(highRuns.output_tokens), cls: 'num is-chosen' }, { content: fmtInt(maxRuns.output_tokens), cls: 'num' }] },
      { cells: [{ th: true, content: L('reasoningTokens') }, { content: fmtInt(highRuns.reasoning_tokens), cls: 'num is-chosen' }, { content: fmtInt(maxRuns.reasoning_tokens), cls: 'num' }] },
      { cells: [{ th: true, content: L('cacheReadTokens') }, { content: fmtInt(highRuns.cache_read_tokens), cls: 'num is-chosen' }, { content: fmtInt(maxRuns.cache_read_tokens), cls: 'num' }] }
    ]));

    var api = isObject(cost.per_arm_api_calls) ? cost.per_arm_api_calls : {};
    var apiHigh = isObject(api.high) ? api.high : {};
    var apiMax = isObject(api.max) ? api.max : {};
    frag.appendChild(buildTable(L('apiCallsCaption'), [
      { text: L('metric') },
      { text: 'high', cls: 'num', chosen: true },
      { text: 'max', cls: 'num' }
    ], [
      { cells: [{ th: true, content: L('calls') }, { content: fmtInt(apiHigh.calls), cls: 'num is-chosen' }, { content: fmtInt(apiMax.calls), cls: 'num' }] },
      { cells: [{ th: true, content: L('outputTokens') }, { content: fmtInt(apiHigh.output_tokens), cls: 'num is-chosen' }, { content: fmtInt(apiMax.output_tokens), cls: 'num' }] }
    ]));

    if (cost.note) frag.appendChild(el('p', { cls: 'small', text: cost.note }));
    if (cost.pricing_used) {
      frag.appendChild(el('p', { cls: 'muted small', text: L('pricingUsed') + ': ' + t(cost.pricing_used) }));
    }

    /* real project */
    var real = isObject(data.real_project) ? data.real_project : {};
    frag.appendChild(sectionTitle(L('realTitle')));
    if (real.project) {
      frag.appendChild(el('p', { cls: 'muted small', text: real.project }));
    }
    var projectUrl = real.project_url;
    if (typeof projectUrl === 'string' && /^https:\/\/github\.com\//.test(projectUrl)) {
      frag.appendChild(el('p', { cls: 'small' }, [
        el('a', { text: projectUrl.replace('https://', ''), attrs: { href: projectUrl, rel: 'noopener' } })
      ]));
    }
    var realRows = [];
    asArray(real.tasks).forEach(function (task) {
      if (!isObject(task)) return;
      var arms = [
        { key: 'high', label: 'high', chosen: true },
        { key: 'max', label: 'max', chosen: false }
      ];
      var scores = { high: Number((task.high || {}).blind_score), max: Number((task.max || {}).blind_score) };
      arms.forEach(function (arm, index) {
        var a = isObject(task[arm.key]) ? task[arm.key] : {};
        var other = arm.key === 'high' ? 'max' : 'high';
        var wins = scores[arm.key] > scores[other];
        var cells = [];
        if (index === 0) {
          /* the task name spans both arm rows; the max row starts at the arm cell */
          cells.push({ th: true, content: t(task.name), rowspan: 2 });
        }
        cells.push({ content: arm.chosen ? [arm.label, chosenTag()] : arm.label, cls: arm.chosen ? 'is-chosen' : '' });
        cells.push({ content: fmtSeconds(a.seconds), cls: 'num' + (arm.chosen ? ' is-chosen' : '') });
        cells.push({ content: fmtUsd(a.usd), cls: 'num' + (arm.chosen ? ' is-chosen' : '') });
        cells.push({ content: fmtInt(a.reasoning_tokens), cls: 'num' + (arm.chosen ? ' is-chosen' : '') });
        cells.push({ content: a.gate === 'passed' ? badgePass(L('passed')) : String(a.gate || '—'), cls: arm.chosen ? 'is-chosen' : '' });
        cells.push({ content: fmtInt(a.blind_score), cls: 'num' + (arm.chosen ? ' is-chosen' : '') + (wins ? ' win' : '') });
        cells.push({ content: t({ tr: a.note_tr, en: a.note_en }), cls: 'small' + (arm.chosen ? ' is-chosen' : '') });
        realRows.push({
          cls: index === 0 ? 'task-start' : '',
          cells: cells
        });
      });
    });
    frag.appendChild(buildTable(L('realCaption'), [
      { text: L('task') },
      { text: L('arm') },
      { text: L('duration'), cls: 'num' },
      { text: L('cost'), cls: 'num' },
      { text: L('reasoning'), cls: 'num' },
      { text: L('gate') },
      { text: L('blindScore'), cls: 'num' },
      { text: L('note') }
    ], realRows));

    var total = isObject(real.blind_review_total) ? real.blind_review_total : {};
    var totalP = el('p', { cls: 'small' });
    totalP.appendChild(el('strong', { text: L('blindTotal') + ': ' }));
    totalP.appendChild(document.createTextNode('high ' + fmtInt(total.high) + ' · max ' + fmtInt(total.max)));
    frag.appendChild(totalP);

    /* traps */
    frag.appendChild(sectionTitle(L('trapsTitle')));
    asArray(data.traps).forEach(function (trap) {
      if (!isObject(trap)) return;
      var card = el('article', { cls: 'trap' });
      card.appendChild(el('h3', { text: t(trap.name) }));
      var hidden = el('div', { cls: 'hidden-test' });
      hidden.appendChild(el('span', { cls: 'label', text: L('hiddenTest') }));
      hidden.appendChild(el('span', { text: trap.hidden }));
      card.appendChild(hidden);

      var arms = el('div', { cls: 'trap-arms' });
      [
        { key: 'high', label: 'high', chosen: true },
        { key: 'max', label: 'max', chosen: false }
      ].forEach(function (arm) {
        var a = isObject(trap[arm.key]) ? trap[arm.key] : {};
        var facts = [
          L('hiddenPassed') + ': ' + (a.hidden_passed === undefined ? '—' : a.hidden_passed),
          fmtSeconds(a.seconds),
          fmtUsd(a.usd)
        ];
        arms.appendChild(armBox(
          arm.label,
          arm.chosen,
          Boolean(a.contaminated),
          facts,
          t({ tr: a.note_tr, en: a.note_en })
        ));
      });
      card.appendChild(arms);
      frag.appendChild(card);
    });

    /* phantom bug */
    frag.appendChild(sectionTitle(L('phantomTitle')));
    var phantom = isObject(data.phantom_bug) ? data.phantom_bug : {};
    var phantomApi = isObject(phantom.api) ? phantom.api : {};

    var apiBlock = el('div', { cls: 'card' });
    apiBlock.appendChild(el('h3', { text: L('phantomApi') }));
    var apiSetup = el('p', { cls: 'small' });
    apiSetup.appendChild(el('strong', { text: L('complaint') + ': ' }));
    apiSetup.appendChild(document.createTextNode(t({ tr: phantomApi.setup_tr, en: phantomApi.setup_en })));
    apiBlock.appendChild(apiSetup);
    var apiResult = el('p', { cls: 'small' });
    apiResult.appendChild(el('strong', { text: L('result') + ': ' }));
    apiResult.appendChild(document.createTextNode(t({ tr: phantomApi.result_tr, en: phantomApi.result_en })));
    apiBlock.appendChild(apiResult);
    frag.appendChild(apiBlock);

    var realPhantom = isObject(phantom.real_project) ? phantom.real_project : {};
    var realBlock = el('div', { cls: 'trap' });
    realBlock.appendChild(el('h3', { text: L('phantomProject') }));
    var realSetup = el('p', { cls: 'small' });
    realSetup.appendChild(el('strong', { text: L('complaint') + ': ' }));
    realSetup.appendChild(document.createTextNode(t({ tr: realPhantom.setup_tr, en: realPhantom.setup_en })));
    realBlock.appendChild(realSetup);

    var realArms = el('div', { cls: 'trap-arms' });
    [
      { key: 'high', label: 'high', chosen: true },
      { key: 'max', label: 'max', chosen: false }
    ].forEach(function (arm) {
      var a = isObject(realPhantom[arm.key]) ? realPhantom[arm.key] : {};
      var facts = [fmtSeconds(a.seconds), fmtUsd(a.usd), L('reasoningTokens') + ': ' + fmtInt(a.reasoning_tokens)];
      realArms.appendChild(armBox(
        arm.label,
        arm.chosen,
        Boolean(a.contaminated),
        facts,
        L('verdict') + ': ' + t({ tr: a.verdict_tr, en: a.verdict_en })
      ));
    });
    realBlock.appendChild(realArms);
    frag.appendChild(realBlock);

    /* isolation */
    frag.appendChild(calloutBlock('warn', L('isolationTitle'), t(data.isolation_incident), 'h2'));

    /* planted errors */
    frag.appendChild(sectionTitle(L('plantedTitle')));
    var planted = isObject(data.planted_errors) ? data.planted_errors : {};
    var plantedRows = asArray(planted.rows).map(function (rowItem) {
      rowItem = isObject(rowItem) ? rowItem : {};
      return {
        cells: [
          { th: true, content: t({ tr: rowItem.name_tr, en: rowItem.name_en }) },
          { content: rowItem.high === undefined ? '—' : rowItem.high, cls: 'small is-chosen' },
          { content: rowItem.max === undefined ? '—' : rowItem.max, cls: 'small' }
        ]
      };
    });
    frag.appendChild(buildTable(L('plantedCaption'), [
      { text: L('plantedRound') },
      { text: 'high', chosen: true },
      { text: 'max' }
    ], plantedRows));
    if (planted.note_tr || planted.note_en) {
      frag.appendChild(notesNote(t({ tr: planted.note_tr, en: planted.note_en })));
    }

    /* hard questions */
    frag.appendChild(sectionTitle(L('hardTitle')));
    var hard = isObject(data.hard_questions) ? data.hard_questions : {};
    if (hard.setup_tr || hard.setup_en) {
      frag.appendChild(el('p', { cls: 'muted small', text: t({ tr: hard.setup_tr, en: hard.setup_en }) }));
    }
    var hardRows = asArray(hard.rows).map(function (q) {
      q = isObject(q) ? q : {};
      return {
        cells: [
          { th: true, content: t({ tr: q.q_tr, en: q.q_en }) },
          { content: q.cap64k_high === undefined ? '—' : q.cap64k_high, cls: 'small is-chosen' },
          { content: q.cap64k_max === undefined ? '—' : q.cap64k_max, cls: 'small' },
          { content: q.cap300k_high === undefined ? '—' : q.cap300k_high, cls: 'small is-chosen' },
          { content: q.cap300k_max === undefined ? '—' : q.cap300k_max, cls: 'small' }
        ]
      };
    });
    frag.appendChild(buildTable(L('hardCaption'), [
      { text: L('question') },
      { text: L('cap64') + ' · high', cls: 'num', chosen: true },
      { text: L('cap64') + ' · max', cls: 'num' },
      { text: L('cap300') + ' · high', cls: 'num' },
      { text: L('cap300') + ' · max', cls: 'num' }
    ], hardRows));
    if (hard.note_tr || hard.note_en) {
      frag.appendChild(notesNote(t({ tr: hard.note_tr, en: hard.note_en })));
    }

    /* conclusions */
    frag.appendChild(sectionTitle(L('conclusionsTitle')));
    var conclusions = el('ul', { cls: 'plain' });
    tList(data.conclusions).forEach(function (line) {
      conclusions.appendChild(el('li', { text: line }));
    });
    frag.appendChild(conclusions);

    /* limitations */
    frag.appendChild(sectionTitle(L('limitationsTitle')));
    frag.appendChild(el('p', { cls: 'prose', text: t(data.limitations) }));

    /* next */
    frag.appendChild(sectionTitle(L('nextTitle')));
    frag.appendChild(el('p', { cls: 'prose', text: t(data.next) }));

    /* footer */
    var footer = el('footer', { cls: 'report-footer' });
    footer.appendChild(el('p', {
      text: 'Prepared and verified by Claude Opus 5.5 (Claude Code) for Hasan Furkan. / Hasan Furkan için Claude Opus 5.5 (Claude Code) tarafından hazırlandı ve doğrulandı.'
    }));
    var fine = el('p', { cls: 'fine' });
    append(fine, fmtDate(data.date) + ' · ');
    fine.appendChild(el('a', { text: 'ai-model-benchmarks', attrs: { href: '../' } }));
    append(fine, ' · ');
    fine.appendChild(el('a', { text: 'data.json', attrs: { href: 'data.json' } }));
    footer.appendChild(fine);
    frag.appendChild(footer);

    root.appendChild(frag);
  }

  /* ---------- report page: generic "sections" layout (contract 7.2) ---------- */

  function safeSectionId(raw, index, used) {
    var base = typeof raw === 'string' ? raw.trim() : '';
    if (!/^[A-Za-z0-9_-]+$/.test(base) || used[base]) base = 'section-' + (index + 1);
    used[base] = true;
    return base;
  }

  function renderSectionsReport(root, data) {
    clear(root);
    chartQueue = [];
    activeRedraw = null;
    reportArms = Object.create(null);
    document.title = t(data.title) + ' — ai-model-benchmarks';

    var arms = asArray(data.arms).filter(isObject);
    arms.forEach(function (arm) {
      if (typeof arm.key === 'string') reportArms[arm.key] = arm;
    });
    var chosenArm = null;
    arms.forEach(function (arm) {
      if (arm.chosen === true && !chosenArm) chosenArm = arm;
    });

    var frag = document.createDocumentFragment();

    /* 1. page header */
    var header = el('header', { cls: 'page-header' });
    header.appendChild(el('p', { cls: 'page-label', text: L('reportLabel') }));
    header.appendChild(el('h1', { text: t(data.title) }));
    var lede = t(data.lede);
    if (lede) header.appendChild(el('p', { cls: 'lede', text: lede }));
    var meta = el('p', { cls: 'meta-line' });
    var dateText = fmtDate(data.date);
    if (dateText) meta.appendChild(document.createTextNode(dateText));
    var manager = shortManager((isObject(data.people) ? data.people : {}).manager);
    if (manager) {
      if (dateText) meta.appendChild(el('span', { cls: 'meta-dot', text: '·' }));
      meta.appendChild(el('span', { text: manager }));
    }
    if (meta.firstChild) header.appendChild(meta);
    frag.appendChild(header);

    /* 2. hero bento */
    var hero = isObject(data.hero) ? data.hero : null;
    var decisionText = t(data.decision);
    if (hero || decisionText) {
      var bento = el('div', { cls: 'hero-bento' + (hero ? '' : ' no-hero') });
      if (hero) {
        var focal = el('article', { cls: 'focal-card' });
        if (hero.label) focal.appendChild(el('p', { cls: 'focal-label', text: hero.label }));
        focal.appendChild(el('p', {
          cls: 'focal-value',
          text: hero.value === undefined || hero.value === null || hero.value === '' ? '—' : hero.value
        }));
        if (hero.caption) focal.appendChild(el('p', { cls: 'focal-caption', text: hero.caption }));
        var heroChips = asArray(hero.chips);
        if (heroChips.length) {
          var chipRow = el('div', { cls: 'chip-row' });
          heroChips.forEach(function (entry) {
            entry = isObject(entry) ? entry : { text: entry };
            chipRow.appendChild(chip(entry.tone, entry.text));
          });
          focal.appendChild(chipRow);
        }
        bento.appendChild(focal);
      }
      if (decisionText) {
        var decisionCard = el('article', { cls: 'card decision-card' });
        decisionCard.appendChild(el('p', { cls: 'card-label', text: L('decision') }));
        decisionCard.appendChild(el('p', { cls: 'decision-text', text: data.decision }));
        if (chosenArm) {
          var decisionArm = el('div', { cls: 'decision-arm' });
          decisionArm.appendChild(armBadge(chosenArm.key));
          decisionArm.appendChild(el('span', { cls: 'arm-name', text: t(chosenArm.name) }));
          decisionArm.appendChild(chosenTag());
          decisionCard.appendChild(decisionArm);
        }
        bento.appendChild(decisionCard);
      }
      frag.appendChild(bento);
    }

    /* 3. arms row */
    if (arms.length) {
      var armsRow = el('div', { cls: 'arms-row' });
      arms.forEach(function (arm) {
        var card = el('article', { cls: 'card arm-card' + (arm.chosen === true ? ' is-chosen' : '') });
        var head = el('div', { cls: 'arm-head-row' });
        head.appendChild(armBadge(arm.key));
        head.appendChild(el('span', { cls: 'arm-name', text: t(arm.name) }));
        card.appendChild(head);
        if (arm.detail) card.appendChild(el('p', { cls: 'arm-detail', text: arm.detail }));
        if (arm.chosen === true) {
          var chosenRow = el('div', { cls: 'chip-row' });
          chosenRow.appendChild(chosenTag());
          card.appendChild(chosenRow);
        }
        armsRow.appendChild(card);
      });
      frag.appendChild(armsRow);
    }

    /* 4. sticky section nav, 5. sections */
    var sections = asArray(data.sections).filter(isObject);
    var usedIds = Object.create(null);
    var ids = sections.map(function (section, index) {
      return safeSectionId(section.id, index, usedIds);
    });

    if (sections.length) {
      var nav = el('nav', { cls: 'section-nav', attrs: { 'aria-label': L('sectionsNav') } });
      sections.forEach(function (section, index) {
        var navText = t(section.label) || t(section.title) || String(index + 1);
        nav.appendChild(el('a', { cls: 'nav-pill', text: navText, attrs: { href: '#' + ids[index] } }));
      });
      frag.appendChild(nav);
    }

    sections.forEach(function (section, index) {
      var sec = el('section', { cls: 'report-section', attrs: { id: ids[index] } });
      if (section.label) sec.appendChild(el('p', { cls: 'section-label', text: section.label }));
      if (section.title) sec.appendChild(el('h2', { cls: 'section-title', text: section.title }));
      if (section.lede) sec.appendChild(el('p', { cls: 'section-lede', text: section.lede }));
      var grid = el('div', { cls: 'block-grid' });
      asArray(section.blocks).forEach(function (block) {
        var node = renderBlock(block);
        if (node) grid.appendChild(node);
      });
      if (grid.firstChild) sec.appendChild(grid);
      frag.appendChild(sec);
    });

    /* footer */
    var footer = el('footer', { cls: 'report-footer' });
    footer.appendChild(el('p', {
      text: 'Prepared and verified by Claude Opus 5.5 (Claude Code) for Hasan Furkan. / Hasan Furkan için Claude Opus 5.5 (Claude Code) tarafından hazırlandı ve doğrulandı.'
    }));
    var managerFull = (isObject(data.people) ? data.people : {}).manager;
    if (managerFull) {
      footer.appendChild(el('p', { cls: 'footer-note', text: L('manager') + ': ' + t(managerFull) }));
    }
    var fine = el('p', { cls: 'fine' });
    append(fine, (dateText ? dateText + ' · ' : ''));
    fine.appendChild(el('a', { text: 'ai-model-benchmarks', attrs: { href: '../' } }));
    append(fine, ' · ');
    fine.appendChild(el('a', { text: 'data.json', attrs: { href: 'data.json' } }));
    footer.appendChild(fine);
    frag.appendChild(footer);

    root.appendChild(frag);
    drawCharts();
    activeRedraw = drawCharts;
  }

  function renderBlock(block) {
    if (!isObject(block)) return null;
    switch (block.type) {
      case 'kv':
        return renderKVBlock(block);
      case 'table':
        return renderTableBlock(block);
      case 'tasks':
        return renderTasksBlock(block);
      case 'list':
        return renderListBlock(block);
      case 'paragraph':
        return renderParagraphBlock(block);
      case 'callout':
        return renderCalloutBlock(block);
      case 'verdicts':
        return renderVerdictsBlock(block);
      case 'links':
        return renderLinksBlock(block);
      case 'bars':
      case 'rings':
      case 'gauges':
      case 'strip':
      case 'ranges':
        return renderChartBlock(block);
      default:
        /* unknown block types are skipped silently */
        return null;
    }
  }

  function renderKVBlock(block) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return null;
    var card = el('div', { cls: 'card block block--full kv-card' });
    var list = el('dl', { cls: 'kv' });
    items.forEach(function (item) {
      addKV(list, item.term, item.value);
    });
    card.appendChild(list);
    return card;
  }

  function renderTableBlock(block) {
    var wrap = el('div', { cls: 'block block--full' });
    wrap.appendChild(buildTable(block.caption, block.columns, block.rows));
    if (block.note) wrap.appendChild(notesNote(block.note));
    return wrap;
  }

  function renderTasksBlock(block) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return null;
    var wrap = el('div', { cls: 'block block--full' });
    var list = el('ul', { cls: 'task-list' });
    items.forEach(function (item) {
      var li = el('li', { cls: 'task' });
      if (item.id !== undefined && item.id !== null && item.id !== '') {
        li.appendChild(el('span', { cls: 'task-id', text: item.id }));
      }
      var body = el('div', { cls: 'task-body' });
      if (item.name) body.appendChild(el('p', { cls: 'task-name', text: item.name }));
      if (item.measures) body.appendChild(el('p', { cls: 'task-measures', text: item.measures }));
      li.appendChild(body);
      list.appendChild(li);
    });
    wrap.appendChild(list);
    return wrap;
  }

  function renderListBlock(block) {
    var items = asArray(block.items);
    if (!items.length) return null;
    var list = el('ul', { cls: 'bullet-list block block--full' });
    items.forEach(function (item) {
      list.appendChild(el('li', { text: item }));
    });
    return list;
  }

  function renderParagraphBlock(block) {
    var text = t(block.text);
    if (!text) return null;
    return el('div', { cls: 'block block--full' }, [el('p', { cls: 'prose', text: block.text })]);
  }

  function renderCalloutBlock(block) {
    var text = t(block.text);
    if (!text && !t(block.title)) return null;
    var wrap = el('div', { cls: 'block block--full' });
    wrap.appendChild(calloutBlock(block.tone, block.title, block.text, 'h3'));
    return wrap;
  }

  function renderVerdictsBlock(block) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return null;
    var wrap = el('div', { cls: 'block block--full' });
    var grid = el('div', { cls: 'verdicts-grid' });
    items.forEach(function (item) {
      var isChosen = typeof item.arm === 'string' &&
        Object.prototype.hasOwnProperty.call(reportArms, item.arm) &&
        reportArms[item.arm].chosen === true;
      var card = el('article', { cls: 'verdict-card' + (isChosen ? ' is-chosen' : '') });
      var head = el('div', { cls: 'verdict-head' });
      head.appendChild(armBadge(item.arm));
      head.appendChild(el('span', { cls: 'arm-name', text: armName(item.arm) }));
      if (item.verdict) head.appendChild(chip(item.tone, item.verdict));
      card.appendChild(head);
      if (item.text) card.appendChild(el('p', { cls: 'verdict-text', text: item.text }));
      grid.appendChild(card);
    });
    wrap.appendChild(grid);
    return wrap;
  }

  function renderLinksBlock(block) {
    var items = asArray(block.items).filter(function (item) {
      return isObject(item) || typeof item === 'string';
    });
    if (!items.length) return null;
    var card = el('div', { cls: 'card block block--full' });
    var list = el('ul', { cls: 'link-list' });
    items.forEach(function (raw) {
      var item = isObject(raw) ? raw : { text: raw, href: raw };
      var href = safeReportHref(item.href);
      var li = el('li', { cls: 'link-item' + (href ? '' : ' is-plain') });
      if (href) {
        var link = el('a', { attrs: { href: href } });
        link.appendChild(el('span', { text: item.text }));
        link.appendChild(icon('external'));
        li.appendChild(link);
      } else {
        li.appendChild(el('span', { cls: 'link-label', text: item.text }));
      }
      if (typeof item.href === 'string' && item.href) {
        li.appendChild(el('span', { cls: 'link-path', text: item.href }));
      }
      list.appendChild(li);
    });
    card.appendChild(list);
    return card;
  }

  function renderChartBlock(block) {
    var card = el('article', { cls: 'card chart-card block block--chart' });
    if (block.caption) card.appendChild(el('h3', { cls: 'card-title', text: block.caption }));
    var holder = el('div', { cls: 'chart-holder' });
    card.appendChild(holder);
    chartQueue.push({ holder: holder, block: block });
    return card;
  }

  /* ---------- charts ---------- */

  function drawCharts() {
    for (var i = 0; i < chartQueue.length; i += 1) {
      var entry = chartQueue[i];
      var holder = entry.holder;
      if (!holder || !holder.isConnected) continue;
      var width = Math.floor(holder.clientWidth || 0);
      if (width < 80) continue;
      drawChart(holder, entry.block, width);
    }
  }

  function drawChart(holder, block, width) {
    var height = width >= 420 ? 240 : 200;
    clear(holder);
    holder.style.height = height + 'px';
    var spec;
    try {
      spec = buildChart(block, width, height);
    } catch (err) {
      spec = chartEmpty(block, width, height);
    }
    holder.appendChild(spec.svg);
    holder.appendChild(srTable(
      (t(block.caption) ? t(block.caption) + ' — ' : '') + L('dataTable'),
      spec.headers,
      spec.rows
    ));
  }

  function buildChart(block, width, height) {
    switch (block.type) {
      case 'rings':
        return chartRings(block, width, height);
      case 'gauges':
        return chartGauges(block, width, height);
      case 'bars':
        return chartBars(block, width, height);
      case 'strip':
        return chartStrip(block, width, height);
      case 'ranges':
        return chartRanges(block, width, height);
      default:
        return chartEmpty(block, width, height);
    }
  }

  function chartSvg(width, height) {
    return svgEl('svg', {
      class: 'chart-svg',
      viewBox: '0 0 ' + width + ' ' + height,
      width: width,
      height: height,
      role: 'img',
      focusable: 'false'
    });
  }

  function chartEmpty(block, width, height) {
    var caption = t(block.caption);
    var svg = chartSvg(width, height);
    svg.appendChild(svgText(width / 2, height / 2, L('chartEmpty'), 'chart-label', 'middle'));
    svg.setAttribute('aria-label', (caption ? caption + '. ' : '') + L('chartEmpty'));
    return { svg: svg, headers: [L('armLabel'), L('valueLabel')], rows: [] };
  }

  function chartLabel(caption, parts) {
    var head = caption || L('dataTable');
    return parts.length ? head + ': ' + parts.join(', ') : head;
  }

  function estimateWidth(text, size) {
    return Math.max(0, String(text).length * size * 0.56);
  }

  function armLabel(key) {
    var name = armName(key);
    if (typeof key !== 'string' || !key || name === key) return name;
    return armLetter(key) + ' · ' + name;
  }

  function wrapName(text, perLine, maxLines) {
    var rest = String(text === null || text === undefined ? '' : text).trim();
    var lines = [];
    while (rest && lines.length < maxLines) {
      if (rest.length <= perLine) {
        lines.push(rest);
        rest = '';
        break;
      }
      var cut = rest.lastIndexOf(' ', perLine);
      if (cut < Math.floor(perLine * 0.5)) cut = perLine;
      lines.push(rest.slice(0, cut).trim());
      rest = rest.slice(cut).trim();
    }
    if (rest && lines.length) {
      lines[lines.length - 1] = lines[lines.length - 1].replace(/.$/, '…');
    }
    return lines;
  }

  function srTable(caption, headers, rows) {
    var wrap = el('div', { cls: 'sr-only' });
    var table = el('table');
    if (caption) table.appendChild(el('caption', { text: caption }));
    var thead = el('thead');
    var tr = el('tr');
    asArray(headers).forEach(function (header) {
      tr.appendChild(el('th', { text: header, attrs: { scope: 'col' } }));
    });
    thead.appendChild(tr);
    table.appendChild(thead);
    var tbody = el('tbody');
    asArray(rows).forEach(function (row) {
      var rowNode = el('tr');
      asArray(row).forEach(function (cell, index) {
        rowNode.appendChild(el(index === 0 ? 'th' : 'td', {
          text: cell,
          attrs: index === 0 ? { scope: 'row' } : null
        }));
      });
      tbody.appendChild(rowNode);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  /* rings: one ring per arm, arc = v / total, centre text "15/15" */

  function chartRings(block, width, height) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return chartEmpty(block, width, height);
    var caption = t(block.caption);
    var cols = Math.min(items.length, 3);
    var rows = Math.ceil(items.length / cols);
    var cellW = width / cols;
    var cellH = height / rows;
    var r = Math.max(14, Math.min(cellW / 2 - 12, cellH / 2 - 52));
    var stroke = clamp(r * 0.22, 6, 14);
    var circumference = 2 * Math.PI * r;
    var svg = chartSvg(width, height);
    var parts = [];
    var tableRows = [];

    items.forEach(function (item, index) {
      var col = index % cols;
      var row = Math.floor(index / cols);
      var cx = col * cellW + cellW / 2;
      var cy = row * cellH + cellH / 2 - 10;
      var v = toNumber(item.v);
      var total = toNumber(item.total);
      var ratio = (v !== null && total !== null && total > 0) ? clamp(v / total, 0, 1) : 0;
      var group = svgEl('g', { class: armKeyClass(item.arm) });
      group.appendChild(svgEl('circle', {
        cx: cx, cy: cy, r: r, class: 'chart-track', 'stroke-width': stroke
      }));
      if (ratio > 0) {
        var dash = circumference * ratio;
        var arc = svgEl('circle', {
          cx: cx,
          cy: cy,
          r: r,
          class: 'chart-arc',
          'stroke-width': stroke,
          'stroke-dasharray': dash.toFixed(2) + ' ' + (circumference - dash).toFixed(2),
          transform: 'rotate(-90 ' + cx + ' ' + cy + ')'
        });
        arc.style.setProperty('--sweep-from', dash.toFixed(2) + 'px');
        group.appendChild(arc);
      }
      var centre = (v === null || total === null) ? '—' : fmtInt(v) + '/' + fmtInt(total);
      var valueSize = Math.round(clamp(r * 0.5, 12, 18));
      var valueNode = svgText(cx, cy + valueSize * 0.35, centre, 'chart-value', 'middle');
      valueNode.style.fontSize = valueSize + 'px';
      group.appendChild(valueNode);
      group.appendChild(svgText(cx, cy + r + 18, armLetter(item.arm), 'chart-letter', 'middle'));

      var name = armName(item.arm);
      var perLine = Math.max(6, Math.floor((cellW - 10) / 6.4));
      wrapName(name, perLine, 2).forEach(function (line, lineIndex) {
        group.appendChild(svgText(cx, cy + r + 34 + lineIndex * 15, line, 'chart-label', 'middle'));
      });

      svg.appendChild(group);
      parts.push(name + ' ' + centre);
      tableRows.push([
        armLabel(item.arm),
        v === null ? '—' : fmtInt(v),
        total === null ? '—' : fmtInt(total)
      ]);
    });

    svg.setAttribute('aria-label', chartLabel(caption, parts));
    return {
      svg: svg,
      headers: [L('armLabel'), L('valueLabel'), L('totalLabel')],
      rows: tableRows
    };
  }

  /* gauges: one semicircle per arm from min to max, value in the centre */

  function chartGauges(block, width, height) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return chartEmpty(block, width, height);
    var caption = t(block.caption);
    var fmt = block.fmt || 'dec2';
    var min = toNumber(block.min);
    var max = toNumber(block.max);
    if (min === null) min = 0;
    if (max === null || max === min) max = min + 1;
    var cols = Math.min(items.length, 3);
    var rows = Math.ceil(items.length / cols);
    var cellW = width / cols;
    var cellH = height / rows;
    var r = Math.max(16, Math.min(cellW / 2 - 16, cellH - 70, 96));
    var svg = chartSvg(width, height);
    var parts = [];
    var tableRows = [];

    items.forEach(function (item, index) {
      var col = index % cols;
      var row = Math.floor(index / cols);
      var cx = col * cellW + cellW / 2;
      var blockH = r + 62;
      var oy = row * cellH + Math.max(6, (cellH - blockH) / 2);
      var labelY = oy + 14;
      var cy = labelY + 12 + r;
      var v = toNumber(item.v);
      var ratio = v === null ? 0 : clamp((v - min) / (max - min), 0, 1);
      var group = svgEl('g', { class: armKeyClass(item.arm) });

      group.appendChild(svgEl('path', {
        d: 'M ' + (cx - r) + ' ' + cy + ' A ' + r + ' ' + r + ' 0 0 1 ' + (cx + r) + ' ' + cy,
        class: 'chart-gauge-track'
      }));
      if (ratio > 0) {
        var angle = Math.PI - Math.PI * ratio;
        var ex = cx + r * Math.cos(angle);
        var ey = cy - r * Math.sin(angle);
        var arc = svgEl('path', {
          d: 'M ' + (cx - r) + ' ' + cy + ' A ' + r + ' ' + r + ' 0 0 1 ' + ex.toFixed(2) + ' ' + ey.toFixed(2),
          class: 'chart-gauge'
        });
        arc.setAttribute('pathLength', '1');
        arc.setAttribute('stroke-dasharray', '1');
        arc.style.setProperty('--sweep-from', '1');
        group.appendChild(arc);
      }

      var valueSize = Math.round(clamp(cellW * 0.13, 15, 26));
      var valueNode = svgText(cx, cy - 12, v === null ? '—' : fmtValue(v, fmt), 'chart-value', 'middle');
      valueNode.style.fontSize = valueSize + 'px';
      group.appendChild(valueNode);
      group.appendChild(svgText(cx - r, cy + 20, fmtValue(min, fmt), 'chart-label', 'start'));
      group.appendChild(svgText(cx + r, cy + 20, fmtValue(max, fmt), 'chart-label', 'end'));
      group.appendChild(svgText(cx, labelY, armLetter(item.arm), 'chart-letter', 'middle'));

      svg.appendChild(group);
      parts.push(armName(item.arm) + ' ' + (v === null ? '—' : fmtValue(v, fmt)));
      tableRows.push([armLabel(item.arm), v === null ? '—' : fmtValue(v, fmt)]);
    });

    var rangeText = fmtValue(min, fmt) + '–' + fmtValue(max, fmt);
    svg.setAttribute('aria-label', chartLabel(caption ? caption + ' (' + rangeText + ')' : '', parts));
    return { svg: svg, headers: [L('armLabel'), L('valueLabel')], rows: tableRows };
  }

  /* bars: one horizontal bar per arm, lowest value gets a chip */

  function chartBars(block, width, height) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return chartEmpty(block, width, height);
    var caption = t(block.caption);
    var fmt = block.fmt || 'int';
    var values = items.map(function (item) { return toNumber(item.v); });
    var finite = values.filter(function (n) { return n !== null; });
    var maxV = finite.length ? Math.max.apply(null, finite) : 0;
    var minV = finite.length ? Math.min.apply(null, finite) : null;
    var markLowest = finite.length > 1 && maxV > minV;

    var left = 26;
    var valueTexts = items.map(function (item) {
      var v = toNumber(item.v);
      return v === null ? '—' : fmtValue(v, fmt);
    });
    var valueW = Math.max.apply(null, valueTexts.map(function (text) {
      return estimateWidth(text, 13);
    }).concat([24]));
    var chipW = markLowest ? estimateWidth(L('lowest'), 12) + 18 : 0;
    var barMax = width - left - 10 - valueW - (markLowest ? chipW + 6 : 0) - 6;
    if (barMax < 36) barMax = Math.max(20, width - left - 10 - valueW - 6);

    var rowH = height / items.length;
    var barH = clamp(rowH * 0.4, 12, 26);
    var svg = chartSvg(width, height);
    var defs = svgEl('defs');
    var gradientIds = items.map(function (item) {
      var id = 'chart-grad-' + (uid += 1);
      var grad = svgEl('linearGradient', {
        id: id,
        x1: '0', y1: '0', x2: '1', y2: '0',
        class: 'chart-grad ' + armKeyClass(item.arm)
      });
      grad.appendChild(svgEl('stop', { offset: '0' }));
      grad.appendChild(svgEl('stop', { offset: '1' }));
      defs.appendChild(grad);
      return id;
    });
    svg.appendChild(defs);

    var parts = [];
    var tableRows = [];

    items.forEach(function (item, index) {
      var v = values[index];
      var cy = index * rowH + rowH / 2;
      var group = svgEl('g', { class: armKeyClass(item.arm) });
      group.appendChild(svgText(2, cy + 4.5, armLetter(item.arm), 'chart-letter', 'start'));

      var ratio = (v !== null && v > 0 && maxV > 0) ? v / maxV : 0;
      var barW = barMax * ratio;
      var bar = svgEl('rect', {
        x: left,
        y: cy - barH / 2,
        width: Math.max(0, barW),
        height: barH,
        rx: Math.min(barH / 2, 10),
        class: 'chart-bar'
      });
      bar.style.fill = 'url(#' + gradientIds[index] + ')';
      group.appendChild(bar);

      group.appendChild(svgText(left + barW + 8, cy + 4.5, valueTexts[index], 'chart-value', 'start'));

      var isLowest = markLowest && v !== null && v === minV;
      if (isLowest) {
        var chipX = left + barMax + 8 + valueW + 6;
        group.appendChild(svgEl('rect', {
          x: chipX,
          y: cy - 10,
          width: chipW,
          height: 20,
          rx: 10,
          class: 'chart-chip-bg'
        }));
        group.appendChild(svgText(chipX + chipW / 2, cy + 4, L('lowest'), 'chart-chip-text', 'middle'));
      }

      svg.appendChild(group);
      parts.push(armName(item.arm) + ' ' + valueTexts[index] + (isLowest ? ' (' + L('lowest') + ')' : ''));
      tableRows.push([armLabel(item.arm), valueTexts[index]]);
    });

    svg.setAttribute('aria-label', chartLabel(caption, parts));
    return { svg: svg, headers: [L('armLabel'), L('valueLabel')], rows: tableRows };
  }

  /* strip: one row per arm, one dot per point, mean as a short tick */

  function chartStrip(block, width, height) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return chartEmpty(block, width, height);
    var caption = t(block.caption);
    var fmt = block.fmt || 'int';
    var allValues = [];
    items.forEach(function (item) {
      asArray(item.points).forEach(function (point) {
        if (!isObject(point)) return;
        var n = toNumber(point.v);
        if (n !== null) allValues.push(n);
      });
    });
    if (!allValues.length) return chartEmpty(block, width, height);

    var vmin = Math.min.apply(null, allValues);
    var vmax = Math.max.apply(null, allValues);
    var left = 26;
    var right = 14;
    var top = 18;
    var bottom = 30;
    var plotW = Math.max(20, width - left - right);
    var rowH = (height - top - bottom) / items.length;
    var axisY = height - bottom;

    function xOf(value) {
      if (vmax === vmin) return left + plotW / 2;
      return left + ((value - vmin) / (vmax - vmin)) * plotW;
    }

    var svg = chartSvg(width, height);
    svg.appendChild(svgEl('line', { x1: left, y1: axisY, x2: left + plotW, y2: axisY, class: 'chart-axis' }));
    var tickCount = width >= 420 ? 4 : 3;
    for (var tick = 0; tick < tickCount; tick += 1) {
      var frac = tick / (tickCount - 1);
      var tickX = left + plotW * frac;
      svg.appendChild(svgEl('line', { x1: tickX, y1: axisY, x2: tickX, y2: axisY + 4, class: 'chart-axis' }));
      svg.appendChild(svgText(
        tickX,
        axisY + 18,
        fmtValue(vmin + (vmax - vmin) * frac, fmt),
        'chart-label',
        tick === 0 ? 'start' : tick === tickCount - 1 ? 'end' : 'middle'
      ));
    }

    var parts = [];
    var tableRows = [];

    items.forEach(function (item, index) {
      var cy = top + rowH * index + rowH / 2;
      var group = svgEl('g', { class: armKeyClass(item.arm) });
      group.appendChild(svgText(2, cy + 4.5, armLetter(item.arm), 'chart-letter', 'start'));
      var values = [];

      asArray(item.points).forEach(function (point) {
        if (!isObject(point)) return;
        var v = toNumber(point.v);
        if (v === null) return;
        values.push(v);
        var dot = svgEl('circle', { cx: xOf(v), cy: cy, r: 4.2, class: 'chart-dot' });
        dot.appendChild(svgTitle((point.label === undefined ? '' : t(point.label)) + ': ' + fmtValue(v, fmt)));
        group.appendChild(dot);
        tableRows.push([
          armLabel(item.arm),
          point.label === undefined ? '—' : t(point.label),
          fmtValue(v, fmt)
        ]);
      });

      if (values.length) {
        var sum = values.reduce(function (a, b) { return a + b; }, 0);
        var mean = sum / values.length;
        var meanX = xOf(mean);
        group.appendChild(svgEl('line', {
          x1: meanX, y1: cy - 9, x2: meanX, y2: cy + 9, class: 'chart-mean'
        }));
        var lo = Math.min.apply(null, values);
        var hi = Math.max.apply(null, values);
        parts.push(
          armName(item.arm) + ': ' + values.length + ' ' + L('runs') + ', ' +
          L('mean') + ' ' + fmtValue(mean, fmt) + ', ' + fmtValue(lo, fmt) + '–' + fmtValue(hi, fmt)
        );
        tableRows.push([armLabel(item.arm), L('mean'), fmtValue(mean, fmt)]);
      } else {
        parts.push(armName(item.arm) + ': —');
      }

      svg.appendChild(group);
    });

    svg.setAttribute('aria-label', chartLabel(caption, parts));
    return {
      svg: svg,
      headers: [L('armLabel'), L('runLabel'), L('valueLabel')],
      rows: tableRows
    };
  }

  /* ranges: line from min to max, larger dot at the median, labels at all three */

  function chartRanges(block, width, height) {
    var items = asArray(block.items).filter(isObject);
    if (!items.length) return chartEmpty(block, width, height);
    var caption = t(block.caption);
    var fmt = block.fmt || 'seconds';
    var all = [];
    items.forEach(function (item) {
      ['min', 'median', 'max'].forEach(function (key) {
        var n = toNumber(item[key]);
        if (n !== null) all.push(n);
      });
    });
    if (!all.length) return chartEmpty(block, width, height);

    var dmin = Math.min.apply(null, all);
    var dmax = Math.max.apply(null, all);
    if (dmax === dmin) {
      dmin -= 1;
      dmax += 1;
    }
    var left = 26;
    var right = 16;
    var top = 16;
    var bottom = 16;
    var plotW = Math.max(20, width - left - right);
    var rowH = (height - top - bottom) / items.length;

    function xOf(value) {
      return left + ((value - dmin) / (dmax - dmin)) * plotW;
    }

    var svg = chartSvg(width, height);
    var parts = [];
    var tableRows = [];

    items.forEach(function (item, index) {
      var cy = top + rowH * index + rowH / 2;
      var group = svgEl('g', { class: armKeyClass(item.arm) });
      group.appendChild(svgText(2, cy + 4.5, armLetter(item.arm), 'chart-letter', 'start'));

      var min = toNumber(item.min);
      var median = toNumber(item.median);
      var max = toNumber(item.max);

      if (min !== null && max !== null) {
        group.appendChild(svgEl('line', {
          x1: xOf(min), y1: cy, x2: xOf(max), y2: cy, class: 'chart-range'
        }));
        group.appendChild(svgText(xOf(min), cy + 22, fmtValue(min, fmt), 'chart-label', 'start'));
        group.appendChild(svgText(xOf(max), cy + 22, fmtValue(max, fmt), 'chart-label', 'end'));
      }
      if (median !== null) {
        group.appendChild(svgEl('circle', {
          cx: xOf(median), cy: cy, r: 6, class: 'chart-median'
        }));
        group.appendChild(svgText(xOf(median), cy - 14, fmtValue(median, fmt), 'chart-label', 'middle'));
      }

      svg.appendChild(group);
      parts.push(
        armName(item.arm) + ': ' + L('minLabel') + ' ' + fmtValue(min, fmt) +
        ', ' + L('medianLabel') + ' ' + fmtValue(median, fmt) +
        ', ' + L('maxLabel') + ' ' + fmtValue(max, fmt)
      );
      tableRows.push([
        armLabel(item.arm),
        fmtValue(min, fmt),
        fmtValue(median, fmt),
        fmtValue(max, fmt)
      ]);
    });

    svg.setAttribute('aria-label', chartLabel(caption, parts));
    return {
      svg: svg,
      headers: [L('armLabel'), L('minLabel'), L('medianLabel'), L('maxLabel')],
      rows: tableRows
    };
  }

  /* ---------- index page (contract 7.1) ---------- */

  function safeReportHref(path) {
    if (typeof path !== 'string') return null;
    var value = path.trim();
    if (!value) return null;
    if (value.indexOf('..') !== -1) return null;
    if (value.indexOf(':') !== -1) return null;
    if (value.charAt(0) === '/' || value.charAt(0) === '\\') return null;
    if (!/^[A-Za-z0-9._~\-\/]+$/.test(value)) return null;
    return value;
  }

  function indexFooter() {
    var footer = el('footer', { cls: 'report-footer' });
    footer.appendChild(el('p', {
      text: lang === 'tr'
        ? 'Hasan Furkan (HFK) için Claude Opus 5.5 (Claude Code) tarafından yönetilir ve doğrulanır.'
        : 'Managed and verified by Claude Opus 5.5 (Claude Code) for Hasan Furkan (HFK).'
    }));
    return footer;
  }

  function renderIndex(root, items) {
    clear(root);
    chartQueue = [];
    activeRedraw = null;
    var frag = document.createDocumentFragment();

    var header = el('header', { cls: 'page-header' });
    header.appendChild(el('p', { cls: 'page-label', text: L('benchmarksLabel') }));
    header.appendChild(el('h1', { text: L('indexTitle') }));
    header.appendChild(el('p', { cls: 'lede', text: L('indexLede') }));
    frag.appendChild(header);

    var list = asArray(items).filter(isObject);

    if (!list.length) {
      var empty = el('div', { cls: 'card empty-state' });
      var emptyIcon = el('span', { cls: 'empty-icon' });
      emptyIcon.appendChild(icon('inbox'));
      empty.appendChild(emptyIcon);
      var emptyBody = el('div', { cls: 'empty-body' });
      emptyBody.appendChild(el('p', { cls: 'card-title', text: L('reportsEmpty') }));
      empty.appendChild(emptyBody);
      frag.appendChild(empty);
      frag.appendChild(indexFooter());
      root.appendChild(frag);
      return;
    }

    /* newest report: brand-filled focal card */
    var newest = list[0];
    var newestHref = safeReportHref(newest.path);
    var focal = el('article', { cls: 'focal-report' });
    var newestDate = fmtDate(newest.date);
    if (newestDate) focal.appendChild(el('p', { cls: 'focal-date', text: newestDate }));
    var newestTitle = t(newest.title);
    if (newestHref) {
      focal.appendChild(el('h2', { cls: 'focal-title' }, [
        el('a', { text: newestTitle, attrs: { href: newestHref } })
      ]));
    } else {
      focal.appendChild(el('h2', { cls: 'focal-title', text: newestTitle }));
    }
    var newestSummary = t(newest.summary);
    if (newestSummary) focal.appendChild(el('p', { cls: 'focal-summary', text: newestSummary }));
    if (newestHref) {
      var cta = el('a', { cls: 'pill-button', attrs: { href: newestHref } });
      append(cta, L('readReport'));
      cta.appendChild(icon('arrow', 'pill-arrow'));
      focal.appendChild(cta);
    }
    frag.appendChild(focal);

    /* earlier reports: normal cards, two columns on desktop */
    var rest = list.slice(1);
    if (rest.length) {
      var grid = el('div', { cls: 'report-grid' });
      rest.forEach(function (item) {
        var card = el('article', { cls: 'card report-card' });
        var dateText = fmtDate(item.date);
        if (dateText) card.appendChild(el('p', { cls: 'report-date', text: dateText }));
        var href = safeReportHref(item.path);
        var titleText = t(item.title);
        if (href) {
          card.appendChild(el('h2', { cls: 'report-title' }, [
            el('a', { text: titleText, attrs: { href: href } })
          ]));
        } else {
          card.appendChild(el('h2', { cls: 'report-title', text: titleText }));
        }
        var summary = t(item.summary);
        if (summary) card.appendChild(el('p', { cls: 'report-summary', text: summary }));
        if (href) {
          var open = el('a', { cls: 'report-link', attrs: { href: href } });
          append(open, L('openReport'));
          open.appendChild(icon('arrow'));
          card.appendChild(open);
        }
        grid.appendChild(card);
      });
      frag.appendChild(grid);
    }

    frag.appendChild(indexFooter());
    root.appendChild(frag);
  }

  /* ---------- page entry points ---------- */

  function initReport() {
    var root = document.getElementById('report');
    if (!root) return;
    fetchJSON('data.json').then(function (data) {
      var payload = isObject(data) ? data : {};
      rerender = function () {
        if (payload.layout === 'sections') renderSectionsReport(root, payload);
        else renderReport(root, payload);
      };
      rerender();
    }).catch(function () {
      rerender = function () { showLoadError(root, 'data.json'); };
      showLoadError(root, 'data.json');
    });
  }

  function initIndex() {
    var root = document.getElementById('content');
    if (!root) return;
    fetchJSON('benchmarks.json').then(function (items) {
      var list = asArray(items).filter(isObject);
      var sorted = list.slice().sort(function (a, b) {
        return String(b.date || '').localeCompare(String(a.date || ''));
      });
      rerender = function () { renderIndex(root, sorted); };
      renderIndex(root, sorted);
    }).catch(function () {
      rerender = function () { showLoadError(root, 'benchmarks.json'); };
      showLoadError(root, 'benchmarks.json');
    });
  }

  /* ---------- boot ---------- */

  function boot() {
    /* sync from the stored choice, without re-rendering: pages render after fetch */
    var stored = readStoredLang();
    if (stored !== lang) lang = stored;
    document.documentElement.lang = lang;
    updateButtons();
    decorateBrands();

    var buttons = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener('click', function (event) {
        setLang(event.currentTarget.getAttribute('data-lang'));
      });
    }

    /* charts are drawn at the measured width, so a resize needs a redraw */
    var resizeTimer = null;
    window.addEventListener('resize', function () {
      if (resizeTimer) window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function () {
        resizeTimer = null;
        if (activeRedraw) activeRedraw();
      }, 160);
    });

    var page = document.body.getAttribute('data-page');
    if (page === 'report') initReport();
    else if (page === 'index') initIndex();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
