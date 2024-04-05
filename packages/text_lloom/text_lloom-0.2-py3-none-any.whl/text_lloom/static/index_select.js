var ae = Object.defineProperty;
var de = (e, t, n) => t in e ? ae(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var R = (e, t, n) => (de(e, typeof t != "symbol" ? t + "" : t, n), n);
function C() {
}
function ie(e) {
  return e();
}
function Q() {
  return /* @__PURE__ */ Object.create(null);
}
function A(e) {
  e.forEach(ie);
}
function fe(e) {
  return typeof e == "function";
}
function he(e, t) {
  return e != e ? t == t : e !== t || e && typeof e == "object" || typeof e == "function";
}
function _e(e) {
  return Object.keys(e).length === 0;
}
function o(e, t) {
  e.appendChild(t);
}
function J(e, t, n) {
  e.insertBefore(t, n || null);
}
function y(e) {
  e.parentNode && e.parentNode.removeChild(e);
}
function se(e, t) {
  for (let n = 0; n < e.length; n += 1)
    e[n] && e[n].d(t);
}
function h(e) {
  return document.createElement(e);
}
function m(e) {
  return document.createTextNode(e);
}
function S() {
  return m(" ");
}
function pe() {
  return m("");
}
function W(e, t, n, l) {
  return e.addEventListener(t, n, l), () => e.removeEventListener(t, n, l);
}
function r(e, t, n) {
  n == null ? e.removeAttribute(t) : e.getAttribute(t) !== n && e.setAttribute(t, n);
}
function me(e) {
  return Array.from(e.childNodes);
}
function U(e, t) {
  t = "" + t, e.data !== t && (e.data = /** @type {string} */
  t);
}
let D;
function N(e) {
  D = e;
}
const w = [], X = [];
let k = [];
const Y = [], ge = /* @__PURE__ */ Promise.resolve();
let q = !1;
function ve() {
  q || (q = !0, ge.then(oe));
}
function z(e) {
  k.push(e);
}
const T = /* @__PURE__ */ new Set();
let $ = 0;
function oe() {
  if ($ !== 0)
    return;
  const e = D;
  do {
    try {
      for (; $ < w.length; ) {
        const t = w[$];
        $++, N(t), be(t.$$);
      }
    } catch (t) {
      throw w.length = 0, $ = 0, t;
    }
    for (N(null), w.length = 0, $ = 0; X.length; )
      X.pop()();
    for (let t = 0; t < k.length; t += 1) {
      const n = k[t];
      T.has(n) || (T.add(n), n());
    }
    k.length = 0;
  } while (w.length);
  for (; Y.length; )
    Y.pop()();
  q = !1, T.clear(), N(e);
}
function be(e) {
  if (e.fragment !== null) {
    e.update(), A(e.before_update);
    const t = e.dirty;
    e.dirty = [-1], e.fragment && e.fragment.p(e.ctx, t), e.after_update.forEach(z);
  }
}
function $e(e) {
  const t = [], n = [];
  k.forEach((l) => e.indexOf(l) === -1 ? t.push(l) : n.push(l)), n.forEach((l) => l()), k = t;
}
const we = /* @__PURE__ */ new Set();
function ke(e, t) {
  e && e.i && (we.delete(e), e.i(t));
}
function V(e) {
  return (e == null ? void 0 : e.length) !== void 0 ? e : Array.from(e);
}
function ye(e, t, n) {
  const { fragment: l, after_update: c } = e.$$;
  l && l.m(t, n), z(() => {
    const f = e.$$.on_mount.map(ie).filter(fe);
    e.$$.on_destroy ? e.$$.on_destroy.push(...f) : A(f), e.$$.on_mount = [];
  }), c.forEach(z);
}
function je(e, t) {
  const n = e.$$;
  n.fragment !== null && ($e(n.after_update), A(n.on_destroy), n.fragment && n.fragment.d(t), n.on_destroy = n.fragment = null, n.ctx = []);
}
function Ee(e, t) {
  e.$$.dirty[0] === -1 && (w.push(e), ve(), e.$$.dirty.fill(0)), e.$$.dirty[t / 31 | 0] |= 1 << t % 31;
}
function Oe(e, t, n, l, c, f, i = null, u = [-1]) {
  const d = D;
  N(e);
  const s = e.$$ = {
    fragment: null,
    ctx: [],
    // state
    props: f,
    update: C,
    not_equal: c,
    bound: Q(),
    // lifecycle
    on_mount: [],
    on_destroy: [],
    on_disconnect: [],
    before_update: [],
    after_update: [],
    context: new Map(t.context || (d ? d.$$.context : [])),
    // everything else
    callbacks: Q(),
    dirty: u,
    skip_bound: !1,
    root: t.target || d.$$.root
  };
  i && i(s.root);
  let g = !1;
  if (s.ctx = n ? n(e, t.props || {}, (_, j, ...v) => {
    const b = v.length ? v[0] : j;
    return s.ctx && c(s.ctx[_], s.ctx[_] = b) && (!s.skip_bound && s.bound[_] && s.bound[_](b), g && Ee(e, _)), j;
  }) : [], s.update(), g = !0, A(s.before_update), s.fragment = l ? l(s.ctx) : !1, t.target) {
    if (t.hydrate) {
      const _ = me(t.target);
      s.fragment && s.fragment.l(_), _.forEach(y);
    } else
      s.fragment && s.fragment.c();
    t.intro && ke(e.$$.fragment), ye(e, t.target, t.anchor), oe();
  }
  N(d);
}
class Se {
  constructor() {
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    R(this, "$$");
    /**
     * ### PRIVATE API
     *
     * Do not use, may change at any time
     *
     * @type {any}
     */
    R(this, "$$set");
  }
  /** @returns {void} */
  $destroy() {
    je(this, 1), this.$destroy = C;
  }
  /**
   * @template {Extract<keyof Events, string>} K
   * @param {K} type
   * @param {((e: Events[K]) => void) | null | undefined} callback
   * @returns {() => void}
   */
  $on(t, n) {
    if (!fe(n))
      return C;
    const l = this.$$.callbacks[t] || (this.$$.callbacks[t] = []);
    return l.push(n), () => {
      const c = l.indexOf(n);
      c !== -1 && l.splice(c, 1);
    };
  }
  /**
   * @param {Partial<Props>} props
   * @returns {void}
   */
  $set(t) {
    this.$$set && !_e(t) && (this.$$.skip_bound = !0, this.$$set(t), this.$$.skip_bound = !1);
  }
}
const Ne = "4";
typeof window < "u" && (window.__svelte || (window.__svelte = { v: /* @__PURE__ */ new Set() })).v.add(Ne);
function Z(e, t, n) {
  const l = e.slice();
  return l[6] = t[n][0], l[7] = t[n][1], l[8] = t, l[9] = n, l;
}
function ee(e, t, n) {
  const l = e.slice();
  return l[10] = t[n], l;
}
function te(e) {
  let t, n = V(Object.entries(
    /*concepts*/
    e[0]
  )), l = [];
  for (let c = 0; c < n.length; c += 1)
    l[c] = ce(Z(e, n, c));
  return {
    c() {
      for (let c = 0; c < l.length; c += 1)
        l[c].c();
      t = pe();
    },
    m(c, f) {
      for (let i = 0; i < l.length; i += 1)
        l[i] && l[i].m(c, f);
      J(c, t, f);
    },
    p(c, f) {
      if (f & /*Object, concepts, handleCheck*/
      3) {
        n = V(Object.entries(
          /*concepts*/
          c[0]
        ));
        let i;
        for (i = 0; i < n.length; i += 1) {
          const u = Z(c, n, i);
          l[i] ? l[i].p(u, f) : (l[i] = ce(u), l[i].c(), l[i].m(t.parentNode, t));
        }
        for (; i < l.length; i += 1)
          l[i].d(1);
        l.length = n.length;
      }
    },
    d(c) {
      c && y(t), se(l, c);
    }
  };
}
function ne(e) {
  let t, n = V(
    /*c*/
    e[7].examples
  ), l = [];
  for (let c = 0; c < n.length; c += 1)
    l[c] = le(ee(e, n, c));
  return {
    c() {
      t = h("ul");
      for (let c = 0; c < l.length; c += 1)
        l[c].c();
      r(t, "class", "svelte-1wcpej5");
    },
    m(c, f) {
      J(c, t, f);
      for (let i = 0; i < l.length; i += 1)
        l[i] && l[i].m(t, null);
    },
    p(c, f) {
      if (f & /*Object, concepts*/
      1) {
        n = V(
          /*c*/
          c[7].examples
        );
        let i;
        for (i = 0; i < n.length; i += 1) {
          const u = ee(c, n, i);
          l[i] ? l[i].p(u, f) : (l[i] = le(u), l[i].c(), l[i].m(t, null));
        }
        for (; i < l.length; i += 1)
          l[i].d(1);
        l.length = n.length;
      }
    },
    d(c) {
      c && y(t), se(l, c);
    }
  };
}
function le(e) {
  let t, n, l = (
    /*example*/
    e[10] + ""
  ), c, f;
  return {
    c() {
      t = h("li"), n = m('"'), c = m(l), f = m('"'), r(t, "class", "examples svelte-1wcpej5");
    },
    m(i, u) {
      J(i, t, u), o(t, n), o(t, c), o(t, f);
    },
    p(i, u) {
      u & /*concepts*/
      1 && l !== (l = /*example*/
      i[10] + "") && U(c, l);
    },
    d(i) {
      i && y(t);
    }
  };
}
function ce(e) {
  let t, n, l, c, f, i, u, d, s, g = (
    /*i*/
    e[9] + 1 + ""
  ), _, j, v = (
    /*c*/
    e[7].name + ""
  ), b, L, F, B, I, P = (
    /*c*/
    e[7].prompt + ""
  ), x, G, E, H, M, K;
  function re() {
    e[3].call(
      c,
      /*each_value*/
      e[8],
      /*i*/
      e[9]
    );
  }
  function ue() {
    return (
      /*change_handler*/
      e[4](
        /*c_id*/
        e[6]
      )
    );
  }
  let a = (
    /*c*/
    e[7].examples && ne(e)
  );
  return {
    c() {
      t = h("div"), n = h("div"), l = h("div"), c = h("input"), u = S(), d = h("label"), s = h("b"), _ = m(g), j = m(": "), b = m(v), F = S(), B = h("div"), I = h("p"), x = m(P), G = S(), E = h("div"), a && a.c(), H = S(), r(c, "type", "checkbox"), r(c, "id", f = /*c_id*/
      e[6]), r(c, "name", i = /*c*/
      e[7].name), r(c, "class", "svelte-1wcpej5"), r(d, "for", L = /*c_id*/
      e[6]), r(d, "class", "svelte-1wcpej5"), r(l, "class", "left svelte-1wcpej5"), r(I, "class", "svelte-1wcpej5"), r(B, "class", "mid svelte-1wcpej5"), r(E, "class", "right svelte-1wcpej5"), r(n, "class", "concept-detail svelte-1wcpej5"), r(t, "class", "concept-card");
    },
    m(O, p) {
      J(O, t, p), o(t, n), o(n, l), o(l, c), c.checked = /*c*/
      e[7].active, o(l, u), o(l, d), o(d, s), o(s, _), o(s, j), o(s, b), o(n, F), o(n, B), o(B, I), o(I, x), o(n, G), o(n, E), a && a.m(E, null), o(t, H), M || (K = [
        W(c, "change", re),
        W(c, "change", ue)
      ], M = !0);
    },
    p(O, p) {
      e = O, p & /*concepts*/
      1 && f !== (f = /*c_id*/
      e[6]) && r(c, "id", f), p & /*concepts*/
      1 && i !== (i = /*c*/
      e[7].name) && r(c, "name", i), p & /*Object, concepts*/
      1 && (c.checked = /*c*/
      e[7].active), p & /*concepts*/
      1 && v !== (v = /*c*/
      e[7].name + "") && U(b, v), p & /*concepts*/
      1 && L !== (L = /*c_id*/
      e[6]) && r(d, "for", L), p & /*concepts*/
      1 && P !== (P = /*c*/
      e[7].prompt + "") && U(x, P), /*c*/
      e[7].examples ? a ? a.p(e, p) : (a = ne(e), a.c(), a.m(E, null)) : a && (a.d(1), a = null);
    },
    d(O) {
      O && y(t), a && a.d(), M = !1, A(K);
    }
  };
}
function Ce(e) {
  let t, n, l, c = (
    /*concepts*/
    e[0] && te(e)
  );
  return {
    c() {
      t = h("div"), n = h("p"), n.textContent = "Select concepts to score", l = S(), c && c.c(), r(n, "class", "header svelte-1wcpej5");
    },
    m(f, i) {
      J(f, t, i), o(t, n), o(t, l), c && c.m(t, null);
    },
    p(f, [i]) {
      /*concepts*/
      f[0] ? c ? c.p(f, i) : (c = te(f), c.c(), c.m(t, null)) : c && (c.d(1), c = null);
    },
    i: C,
    o: C,
    d(f) {
      f && y(t), c && c.d();
    }
  };
}
function Ae(e, t, n) {
  let { model: l } = t, c, f = l.get("data");
  f && (c = JSON.parse(f));
  function i(s) {
    s = s.c_id;
    let g = JSON.stringify(c);
    l.set("data", g), l.save_changes();
  }
  function u(s, g) {
    s[g][1].active = this.checked, n(0, c);
  }
  const d = (s) => i({ c_id: s });
  return e.$$set = (s) => {
    "model" in s && n(2, l = s.model);
  }, [c, i, l, u, d];
}
class Je extends Se {
  constructor(t) {
    super(), Oe(this, t, Ae, Ce, he, { model: 2 });
  }
}
function Be({ model: e, el: t }) {
  let n = new Je({ target: t, props: { model: e } });
  return () => n.$destroy();
}
export {
  Be as render
};
