/* ai-model-benchmarks — shared language handling and page rendering.
   Plain ES2020, no dependencies. All data goes into the DOM through
   createElement/textContent; innerHTML, eval and new Function are not used. */

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

      /* report shell */
      reportLabel: 'Benchmark report',
      decision: 'Decision',
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
      loadErrorHint: 'Opening the file directly with file:// blocks fetch().'
    },
    tr: {
      indexTitle: 'Model benchmarkları',
      indexLede: 'Claude Opus 5.5 (Claude Code) tarafından tasarlanan, çalıştırılan ve doğrulanan; Hasan Furkan (HFK) için hazırlanan benchmark raporları.',
      openReport: 'Raporu aç',
      reportsEmpty: 'Henüz yayımlanmış benchmark yok.',

      reportLabel: 'Benchmark raporu',
      decision: 'Karar',
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
      loadErrorHint: 'Dosyayı doğrudan file:// ile açmak fetch() çağrısını engeller.'
    }
  };

  var lang = 'en';
  var rerender = null;

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

  function fmtInt(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return String(value);
    try {
      return new Intl.NumberFormat(lang === 'tr' ? 'tr-TR' : 'en-US').format(n);
    } catch (err) {
      return String(n);
    }
  }

  function fmtUsd(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return String(value);
    // Fixed precision keeps columns comparable: $0.194 next to $0.200, not $0.20.
    return '$' + n.toFixed(n < 1 ? 3 : 2);
  }

  function fmtPercent(value) {
    if (value === null || value === undefined) return '—';
    return fmtInt(value) + '%';
  }

  function fmtSeconds(total) {
    if (total === null || total === undefined || total === '') return '—';
    var n = Number(total);
    if (!isFinite(n)) return String(total);
    var whole = Math.round(n);
    var m = Math.floor(whole / 60);
    var s = whole % 60;
    if (m === 0) return lang === 'tr' ? s + ' sn' : s + ' s';
    return lang === 'tr' ? m + ' dk ' + s + ' sn' : m + ' min ' + s + ' s';
  }

  function fmtMinutes(value) {
    if (value === null || value === undefined || value === '') return '—';
    var n = Number(value);
    if (!isFinite(n)) return String(value);
    var rounded = Math.round(n * 10) / 10;
    var text;
    try {
      text = new Intl.NumberFormat(lang === 'tr' ? 'tr-TR' : 'en-US', {
        maximumFractionDigits: 1,
        minimumFractionDigits: 1
      }).format(rounded);
    } catch (err) {
      text = String(rounded);
    }
    return lang === 'tr' ? text + ' dk' : text + ' min';
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

  function fetchJSON(url) {
    return fetch(url, { cache: 'no-cache', headers: { Accept: 'application/json' } }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    });
  }

  /* ---------- small DOM builders shared by both pages ---------- */

  function sectionTitle(text) {
    return el('h2', { text: text });
  }

  function chosenTag() {
    return el('span', { cls: 'chosen-tag', text: L('chosen') });
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
    if (spec && typeof spec === 'object') return spec;
    return { content: spec };
  }

  function buildTable(caption, headSpecs, bodyRows) {
    var wrap = el('div', { cls: 'table-wrap' });
    var table = el('table');
    if (caption) table.appendChild(el('caption', { text: caption }));

    var thead = el('thead');
    var headRow = el('tr');
    headSpecs.forEach(function (spec) {
      var cls = [];
      if (spec.cls) cls.push(spec.cls);
      if (spec.chosen) cls.push('is-chosen');
      var th = el('th', { cls: cls.join(' '), attrs: { scope: 'col' } }, spec.text);
      if (spec.chosen) th.appendChild(chosenTag());
      headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    var tbody = el('tbody');
    bodyRows.forEach(function (rowSpec) {
      var tr = el('tr', { cls: rowSpec.cls || '' });
      rowSpec.cells.forEach(function (raw) {
        var spec = normalizeCell(raw);
        var isRowHead = Boolean(spec.th);
        var cls = [];
        if (spec.cls) cls.push(spec.cls);
        if (spec.chosen) cls.push('is-chosen');
        var cell = el(isRowHead ? 'th' : 'td', { cls: cls.join(' ') });
        if (isRowHead) {
          cell.setAttribute('scope', 'row');
          if (spec.rowspan && spec.rowspan > 1) cell.setAttribute('rowspan', String(spec.rowspan));
        }
        append(cell, spec.content);
        tr.appendChild(cell);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    return wrap;
  }

  function notesNote(text) {
    return el('p', { cls: 'muted small', text: text });
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

  function showLoadError(root, fileName) {
    clear(root);
    document.documentElement.lang = lang;
    var box = el('div', { cls: 'notice', attrs: { role: 'alert' } });
    box.appendChild(el('strong', { text: 'Rapor verisi yüklenemedi / Could not load the data' }));
    box.appendChild(el('p', { cls: 'small', text: fileName }));
    box.appendChild(errorParagraph(
      UI.tr.loadErrorBody,
      UI.tr.loadErrorHint
    ));
    box.appendChild(errorParagraph(
      UI.en.loadErrorBody,
      UI.en.loadErrorHint
    ));
    root.appendChild(box);
  }

  /* ---------- report page ---------- */

  function renderReport(root, data) {
    clear(root);
    document.title = t(data.title) + ' — ai-model-benchmarks';
    var frag = document.createDocumentFragment();

    var header = el('header', { cls: 'report-header' });
    header.appendChild(el('p', { cls: 'eyebrow', text: L('reportLabel') }));
    header.appendChild(el('h1', { text: t(data.title) }));
    header.appendChild(el('p', { cls: 'meta-line', text: fmtDate(data.date) }));
    frag.appendChild(header);

    /* who */
    frag.appendChild(sectionTitle(L('whoTitle')));
    var people = el('div', { cls: 'grid-1' });
    people.appendChild(personCard(L('manager'), data.people.manager));
    frag.appendChild(people);

    /* setup */
    frag.appendChild(sectionTitle(L('setupTitle')));
    var setupCard = el('div', { cls: 'card' });
    var kv = el('dl', { cls: 'kv' });
    addKV(kv, L('model'), data.setup.model);
    var pills = el('div', { cls: 'pill-row' });
    (data.setup.levels_available || []).forEach(function (level) {
      pills.appendChild(el('span', { cls: 'pill', text: level }));
    });
    addKV(kv, L('levels'), pills);
    addKV(kv, L('noXhigh'), data.setup.no_xhigh);
    addKV(kv, L('clamp'), data.setup.claude_code_clamp);
    addKV(kv, L('harness'), data.setup.harness);
    addKV(kv, L('machine'), data.setup.machine);
    setupCard.appendChild(kv);
    frag.appendChild(setupCard);

    /* agents */
    frag.appendChild(sectionTitle(L('agentsTitle')));
    var stats = el('div', { cls: 'stats' });
    stats.appendChild(statCard(L('codingRuns'), data.agents.coding_agent_runs, data.agents.coding_agent_runs_detail));
    stats.appendChild(statCard(L('blindReviewers'), data.agents.blind_reviewers, data.agents.blind_reviewers_detail));
    stats.appendChild(statCard(L('directApi'), data.agents.direct_api_calls, data.agents.direct_api_calls_detail));
    stats.appendChild(statCard(L('smokeRuns'), data.agents.smoke_test_runs));
    stats.appendChild(statCard(L('effortProbes'), data.agents.effort_probe_runs));
    stats.appendChild(statCard(L('managerRuns'), data.agents.manager));
    frag.appendChild(stats);

    /* cost */
    frag.appendChild(sectionTitle(L('costTitle')));
    var before = (data.cost && data.cost.go_dashboard_before) || {};
    var after = (data.cost && data.cost.go_dashboard_after) || {};
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

    var perArm = data.cost.per_arm_agent_runs || {};
    var highRuns = perArm.high || {};
    var maxRuns = perArm.max || {};
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

    var api = data.cost.per_arm_api_calls || {};
    var apiHigh = api.high || {};
    var apiMax = api.max || {};
    frag.appendChild(buildTable(L('apiCallsCaption'), [
      { text: L('metric') },
      { text: 'high', cls: 'num', chosen: true },
      { text: 'max', cls: 'num' }
    ], [
      { cells: [{ th: true, content: L('calls') }, { content: fmtInt(apiHigh.calls), cls: 'num is-chosen' }, { content: fmtInt(apiMax.calls), cls: 'num' }] },
      { cells: [{ th: true, content: L('outputTokens') }, { content: fmtInt(apiHigh.output_tokens), cls: 'num is-chosen' }, { content: fmtInt(apiMax.output_tokens), cls: 'num' }] }
    ]));

    if (data.cost.note) frag.appendChild(el('p', { cls: 'small', text: data.cost.note }));
    if (data.cost.pricing_used) {
      frag.appendChild(el('p', { cls: 'muted small', text: L('pricingUsed') + ': ' + t(data.cost.pricing_used) }));
    }

    /* real project */
    frag.appendChild(sectionTitle(L('realTitle')));
    if (data.real_project.project) {
      frag.appendChild(el('p', { cls: 'muted small', text: data.real_project.project }));
    }
    var projectUrl = data.real_project.project_url;
    if (typeof projectUrl === 'string' && /^https:\/\/github\.com\//.test(projectUrl)) {
      frag.appendChild(el('p', { cls: 'small' }, [
        el('a', { text: projectUrl.replace('https://', ''), attrs: { href: projectUrl, rel: 'noopener' } })
      ]));
    }
    var realRows = [];
    (data.real_project.tasks || []).forEach(function (task) {
      var arms = [
        { key: 'high', label: 'high', chosen: true },
        { key: 'max', label: 'max', chosen: false }
      ];
      var scores = { high: Number((task.high || {}).blind_score), max: Number((task.max || {}).blind_score) };
      arms.forEach(function (arm, index) {
        var a = task[arm.key] || {};
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

    var total = data.real_project.blind_review_total || {};
    var totalP = el('p', { cls: 'small' });
    totalP.appendChild(el('strong', { text: L('blindTotal') + ': ' }));
    totalP.appendChild(document.createTextNode('high ' + fmtInt(total.high) + ' · max ' + fmtInt(total.max)));
    frag.appendChild(totalP);

    /* traps */
    frag.appendChild(sectionTitle(L('trapsTitle')));
    (data.traps || []).forEach(function (trap) {
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
        var a = trap[arm.key] || {};
        var facts = [
          L('hiddenPassed') + ': ' + a.hidden_passed,
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
    var phantom = data.phantom_bug || {};

    var apiBlock = el('div', { cls: 'card' });
    apiBlock.appendChild(el('h3', { text: L('phantomApi') }));
    var apiSetup = el('p', { cls: 'small' });
    apiSetup.appendChild(el('strong', { text: L('complaint') + ': ' }));
    apiSetup.appendChild(document.createTextNode(t({ tr: phantom.api && phantom.api.setup_tr, en: phantom.api && phantom.api.setup_en })));
    apiBlock.appendChild(apiSetup);
    var apiResult = el('p', { cls: 'small' });
    apiResult.appendChild(el('strong', { text: L('result') + ': ' }));
    apiResult.appendChild(document.createTextNode(t({ tr: phantom.api && phantom.api.result_tr, en: phantom.api && phantom.api.result_en })));
    apiBlock.appendChild(apiResult);
    frag.appendChild(apiBlock);

    var realPhantom = (phantom && phantom.real_project) || {};
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
      var a = realPhantom[arm.key] || {};
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
    frag.appendChild(el('div', { cls: 'callout warn' }, [
      el('h2', { text: L('isolationTitle') }),
      el('p', { text: t(data.isolation_incident) })
    ]));

    /* planted errors */
    frag.appendChild(sectionTitle(L('plantedTitle')));
    var planted = data.planted_errors || {};
    var plantedRows = (planted.rows || []).map(function (rowItem) {
      return {
        cells: [
          { th: true, content: t({ tr: rowItem.name_tr, en: rowItem.name_en }) },
          { content: rowItem.high, cls: 'small is-chosen' },
          { content: rowItem.max, cls: 'small' }
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
    var hard = data.hard_questions || {};
    if (hard.setup_tr || hard.setup_en) {
      frag.appendChild(el('p', { cls: 'muted small', text: t({ tr: hard.setup_tr, en: hard.setup_en }) }));
    }
    var hardRows = (hard.rows || []).map(function (q) {
      return {
        cells: [
          { th: true, content: t({ tr: q.q_tr, en: q.q_en }) },
          { content: q.cap64k_high, cls: 'small is-chosen' },
          { content: q.cap64k_max, cls: 'small' },
          { content: q.cap300k_high, cls: 'small is-chosen' },
          { content: q.cap300k_max, cls: 'small' }
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
    (tList(data.conclusions)).forEach(function (line) {
      conclusions.appendChild(el('li', { text: line }));
    });
    frag.appendChild(conclusions);

    /* limitations */
    frag.appendChild(sectionTitle(L('limitationsTitle')));
    frag.appendChild(el('p', { text: t(data.limitations) }));

    /* next */
    frag.appendChild(sectionTitle(L('nextTitle')));
    frag.appendChild(el('p', { text: t(data.next) }));

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

  function initReport() {
    var root = document.getElementById('report');
    if (!root) return;
    fetchJSON('data.json').then(function (data) {
      rerender = function () { renderReport(root, data); };
      renderReport(root, data);
    }).catch(function () {
      rerender = function () { showLoadError(root, 'data.json'); };
      showLoadError(root, 'data.json');
    });
  }

  /* ---------- index page ---------- */

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

  function renderIndex(root, items) {
    clear(root);
    var frag = document.createDocumentFragment();

    var header = el('header', { cls: 'report-header' });
    header.appendChild(el('h1', { text: L('indexTitle') }));
    header.appendChild(el('p', { cls: 'lede', text: L('indexLede') }));
    frag.appendChild(header);

    if (!items.length) {
      frag.appendChild(el('p', { cls: 'muted', text: L('reportsEmpty') }));
      root.appendChild(frag);
      return;
    }

    var list = el('ul', { cls: 'report-list' });
    items.forEach(function (item) {
      var li = el('li');
      var article = el('article', { cls: 'report-card' });
      article.appendChild(el('span', { cls: 'date', text: fmtDate(item.date) }));

      var title = el('h2');
      var href = safeReportHref(item.path);
      if (href) {
        title.appendChild(el('a', { cls: 'title-link', text: t(item.title), attrs: { href: href } }));
      } else {
        title.appendChild(document.createTextNode(t(item.title)));
      }
      article.appendChild(title);

      article.appendChild(el('p', { cls: 'summary', text: t(item.summary) }));
      if (href) {
        article.appendChild(el('a', { cls: 'open', text: L('openReport') + ' →', attrs: { href: href } }));
      }
      li.appendChild(article);
      list.appendChild(li);
    });
    frag.appendChild(list);

    var footer = el('footer', { cls: 'report-footer' });
    footer.appendChild(el('p', {
      text: lang === 'tr'
        ? 'Hasan Furkan (HFK) için Claude Opus 5.5 (Claude Code) tarafından yönetilir ve doğrulanır.'
        : 'Managed and verified by Claude Opus 5.5 (Claude Code) for Hasan Furkan (HFK).'
    }));
    frag.appendChild(footer);

    root.appendChild(frag);
  }

  function initIndex() {
    var root = document.getElementById('content');
    if (!root) return;
    fetchJSON('benchmarks.json').then(function (items) {
      var list = Array.isArray(items) ? items : [];
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

  document.addEventListener('DOMContentLoaded', function () {
    /* sync from the stored choice, without re-rendering: pages render after fetch */
    var stored = readStoredLang();
    if (stored !== lang) lang = stored;
    document.documentElement.lang = lang;
    updateButtons();

    var buttons = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener('click', function (event) {
        var target = event.currentTarget.getAttribute('data-lang');
        setLang(target);
      });
    }

    var page = document.body.getAttribute('data-page');
    if (page === 'report') initReport();
    else if (page === 'index') initIndex();
  });
})();
