const {
  SvelteComponent: Or,
  assign: Mr,
  create_slot: Rr,
  detach: Dr,
  element: Ur,
  get_all_dirty_from_scope: Gr,
  get_slot_changes: Fr,
  get_spread_update: jr,
  init: Vr,
  insert: qr,
  safe_not_equal: xr,
  set_dynamic_element_data: Kn,
  set_style: ne,
  toggle_class: Ne,
  transition_in: El,
  transition_out: kl,
  update_slot_base: zr
} = window.__gradio__svelte__internal;
function Xr(e) {
  let t, n, i;
  const l = (
    /*#slots*/
    e[18].default
  ), r = Rr(
    l,
    e,
    /*$$scope*/
    e[17],
    null
  );
  let o = [
    { "data-testid": (
      /*test_id*/
      e[7]
    ) },
    { id: (
      /*elem_id*/
      e[2]
    ) },
    {
      class: n = "block " + /*elem_classes*/
      e[3].join(" ") + " svelte-1t38q2d"
    }
  ], u = {};
  for (let s = 0; s < o.length; s += 1)
    u = Mr(u, o[s]);
  return {
    c() {
      t = Ur(
        /*tag*/
        e[14]
      ), r && r.c(), Kn(
        /*tag*/
        e[14]
      )(t, u), Ne(
        t,
        "hidden",
        /*visible*/
        e[10] === !1
      ), Ne(
        t,
        "padded",
        /*padding*/
        e[6]
      ), Ne(
        t,
        "border_focus",
        /*border_mode*/
        e[5] === "focus"
      ), Ne(t, "hide-container", !/*explicit_call*/
      e[8] && !/*container*/
      e[9]), ne(
        t,
        "height",
        /*get_dimension*/
        e[15](
          /*height*/
          e[0]
        )
      ), ne(t, "width", typeof /*width*/
      e[1] == "number" ? `calc(min(${/*width*/
      e[1]}px, 100%))` : (
        /*get_dimension*/
        e[15](
          /*width*/
          e[1]
        )
      )), ne(
        t,
        "border-style",
        /*variant*/
        e[4]
      ), ne(
        t,
        "overflow",
        /*allow_overflow*/
        e[11] ? "visible" : "hidden"
      ), ne(
        t,
        "flex-grow",
        /*scale*/
        e[12]
      ), ne(t, "min-width", `calc(min(${/*min_width*/
      e[13]}px, 100%))`), ne(t, "border-width", "var(--block-border-width)");
    },
    m(s, a) {
      qr(s, t, a), r && r.m(t, null), i = !0;
    },
    p(s, a) {
      r && r.p && (!i || a & /*$$scope*/
      131072) && zr(
        r,
        l,
        s,
        /*$$scope*/
        s[17],
        i ? Fr(
          l,
          /*$$scope*/
          s[17],
          a,
          null
        ) : Gr(
          /*$$scope*/
          s[17]
        ),
        null
      ), Kn(
        /*tag*/
        s[14]
      )(t, u = jr(o, [
        (!i || a & /*test_id*/
        128) && { "data-testid": (
          /*test_id*/
          s[7]
        ) },
        (!i || a & /*elem_id*/
        4) && { id: (
          /*elem_id*/
          s[2]
        ) },
        (!i || a & /*elem_classes*/
        8 && n !== (n = "block " + /*elem_classes*/
        s[3].join(" ") + " svelte-1t38q2d")) && { class: n }
      ])), Ne(
        t,
        "hidden",
        /*visible*/
        s[10] === !1
      ), Ne(
        t,
        "padded",
        /*padding*/
        s[6]
      ), Ne(
        t,
        "border_focus",
        /*border_mode*/
        s[5] === "focus"
      ), Ne(t, "hide-container", !/*explicit_call*/
      s[8] && !/*container*/
      s[9]), a & /*height*/
      1 && ne(
        t,
        "height",
        /*get_dimension*/
        s[15](
          /*height*/
          s[0]
        )
      ), a & /*width*/
      2 && ne(t, "width", typeof /*width*/
      s[1] == "number" ? `calc(min(${/*width*/
      s[1]}px, 100%))` : (
        /*get_dimension*/
        s[15](
          /*width*/
          s[1]
        )
      )), a & /*variant*/
      16 && ne(
        t,
        "border-style",
        /*variant*/
        s[4]
      ), a & /*allow_overflow*/
      2048 && ne(
        t,
        "overflow",
        /*allow_overflow*/
        s[11] ? "visible" : "hidden"
      ), a & /*scale*/
      4096 && ne(
        t,
        "flex-grow",
        /*scale*/
        s[12]
      ), a & /*min_width*/
      8192 && ne(t, "min-width", `calc(min(${/*min_width*/
      s[13]}px, 100%))`);
    },
    i(s) {
      i || (El(r, s), i = !0);
    },
    o(s) {
      kl(r, s), i = !1;
    },
    d(s) {
      s && Dr(t), r && r.d(s);
    }
  };
}
function Zr(e) {
  let t, n = (
    /*tag*/
    e[14] && Xr(e)
  );
  return {
    c() {
      n && n.c();
    },
    m(i, l) {
      n && n.m(i, l), t = !0;
    },
    p(i, [l]) {
      /*tag*/
      i[14] && n.p(i, l);
    },
    i(i) {
      t || (El(n, i), t = !0);
    },
    o(i) {
      kl(n, i), t = !1;
    },
    d(i) {
      n && n.d(i);
    }
  };
}
function Wr(e, t, n) {
  let { $$slots: i = {}, $$scope: l } = t, { height: r = void 0 } = t, { width: o = void 0 } = t, { elem_id: u = "" } = t, { elem_classes: s = [] } = t, { variant: a = "solid" } = t, { border_mode: f = "base" } = t, { padding: c = !0 } = t, { type: h = "normal" } = t, { test_id: _ = void 0 } = t, { explicit_call: d = !1 } = t, { container: v = !0 } = t, { visible: A = !0 } = t, { allow_overflow: w = !0 } = t, { scale: E = null } = t, { min_width: p = 0 } = t, m = h === "fieldset" ? "fieldset" : "div";
  const k = (g) => {
    if (g !== void 0) {
      if (typeof g == "number")
        return g + "px";
      if (typeof g == "string")
        return g;
    }
  };
  return e.$$set = (g) => {
    "height" in g && n(0, r = g.height), "width" in g && n(1, o = g.width), "elem_id" in g && n(2, u = g.elem_id), "elem_classes" in g && n(3, s = g.elem_classes), "variant" in g && n(4, a = g.variant), "border_mode" in g && n(5, f = g.border_mode), "padding" in g && n(6, c = g.padding), "type" in g && n(16, h = g.type), "test_id" in g && n(7, _ = g.test_id), "explicit_call" in g && n(8, d = g.explicit_call), "container" in g && n(9, v = g.container), "visible" in g && n(10, A = g.visible), "allow_overflow" in g && n(11, w = g.allow_overflow), "scale" in g && n(12, E = g.scale), "min_width" in g && n(13, p = g.min_width), "$$scope" in g && n(17, l = g.$$scope);
  }, [
    r,
    o,
    u,
    s,
    a,
    f,
    c,
    _,
    d,
    v,
    A,
    w,
    E,
    p,
    m,
    k,
    h,
    l,
    i
  ];
}
class Qr extends Or {
  constructor(t) {
    super(), Vr(this, t, Wr, Zr, xr, {
      height: 0,
      width: 1,
      elem_id: 2,
      elem_classes: 3,
      variant: 4,
      border_mode: 5,
      padding: 6,
      type: 16,
      test_id: 7,
      explicit_call: 8,
      container: 9,
      visible: 10,
      allow_overflow: 11,
      scale: 12,
      min_width: 13
    });
  }
}
const {
  SvelteComponent: Jr,
  append: en,
  attr: Ht,
  create_component: Yr,
  destroy_component: Kr,
  detach: $r,
  element: $n,
  init: eo,
  insert: to,
  mount_component: no,
  safe_not_equal: io,
  set_data: lo,
  space: ro,
  text: oo,
  toggle_class: Oe,
  transition_in: so,
  transition_out: ao
} = window.__gradio__svelte__internal;
function uo(e) {
  let t, n, i, l, r, o;
  return i = new /*Icon*/
  e[1]({}), {
    c() {
      t = $n("label"), n = $n("span"), Yr(i.$$.fragment), l = ro(), r = oo(
        /*label*/
        e[0]
      ), Ht(n, "class", "svelte-9gxdi0"), Ht(t, "for", ""), Ht(t, "data-testid", "block-label"), Ht(t, "class", "svelte-9gxdi0"), Oe(t, "hide", !/*show_label*/
      e[2]), Oe(t, "sr-only", !/*show_label*/
      e[2]), Oe(
        t,
        "float",
        /*float*/
        e[4]
      ), Oe(
        t,
        "hide-label",
        /*disable*/
        e[3]
      );
    },
    m(u, s) {
      to(u, t, s), en(t, n), no(i, n, null), en(t, l), en(t, r), o = !0;
    },
    p(u, [s]) {
      (!o || s & /*label*/
      1) && lo(
        r,
        /*label*/
        u[0]
      ), (!o || s & /*show_label*/
      4) && Oe(t, "hide", !/*show_label*/
      u[2]), (!o || s & /*show_label*/
      4) && Oe(t, "sr-only", !/*show_label*/
      u[2]), (!o || s & /*float*/
      16) && Oe(
        t,
        "float",
        /*float*/
        u[4]
      ), (!o || s & /*disable*/
      8) && Oe(
        t,
        "hide-label",
        /*disable*/
        u[3]
      );
    },
    i(u) {
      o || (so(i.$$.fragment, u), o = !0);
    },
    o(u) {
      ao(i.$$.fragment, u), o = !1;
    },
    d(u) {
      u && $r(t), Kr(i);
    }
  };
}
function fo(e, t, n) {
  let { label: i = null } = t, { Icon: l } = t, { show_label: r = !0 } = t, { disable: o = !1 } = t, { float: u = !0 } = t;
  return e.$$set = (s) => {
    "label" in s && n(0, i = s.label), "Icon" in s && n(1, l = s.Icon), "show_label" in s && n(2, r = s.show_label), "disable" in s && n(3, o = s.disable), "float" in s && n(4, u = s.float);
  }, [i, l, r, o, u];
}
class co extends Jr {
  constructor(t) {
    super(), eo(this, t, fo, uo, io, {
      label: 0,
      Icon: 1,
      show_label: 2,
      disable: 3,
      float: 4
    });
  }
}
const {
  SvelteComponent: ho,
  append: Hn,
  attr: Se,
  bubble: _o,
  create_component: mo,
  destroy_component: bo,
  detach: Hl,
  element: Sn,
  init: go,
  insert: Sl,
  listen: po,
  mount_component: vo,
  safe_not_equal: wo,
  set_data: yo,
  set_style: St,
  space: Eo,
  text: ko,
  toggle_class: ie,
  transition_in: Ho,
  transition_out: So
} = window.__gradio__svelte__internal;
function ei(e) {
  let t, n;
  return {
    c() {
      t = Sn("span"), n = ko(
        /*label*/
        e[1]
      ), Se(t, "class", "svelte-lpi64a");
    },
    m(i, l) {
      Sl(i, t, l), Hn(t, n);
    },
    p(i, l) {
      l & /*label*/
      2 && yo(
        n,
        /*label*/
        i[1]
      );
    },
    d(i) {
      i && Hl(t);
    }
  };
}
function Ao(e) {
  let t, n, i, l, r, o, u, s = (
    /*show_label*/
    e[2] && ei(e)
  );
  return l = new /*Icon*/
  e[0]({}), {
    c() {
      t = Sn("button"), s && s.c(), n = Eo(), i = Sn("div"), mo(l.$$.fragment), Se(i, "class", "svelte-lpi64a"), ie(
        i,
        "small",
        /*size*/
        e[4] === "small"
      ), ie(
        i,
        "large",
        /*size*/
        e[4] === "large"
      ), t.disabled = /*disabled*/
      e[7], Se(
        t,
        "aria-label",
        /*label*/
        e[1]
      ), Se(
        t,
        "aria-haspopup",
        /*hasPopup*/
        e[8]
      ), Se(
        t,
        "title",
        /*label*/
        e[1]
      ), Se(t, "class", "svelte-lpi64a"), ie(
        t,
        "pending",
        /*pending*/
        e[3]
      ), ie(
        t,
        "padded",
        /*padded*/
        e[5]
      ), ie(
        t,
        "highlight",
        /*highlight*/
        e[6]
      ), ie(
        t,
        "transparent",
        /*transparent*/
        e[9]
      ), St(t, "color", !/*disabled*/
      e[7] && /*_color*/
      e[11] ? (
        /*_color*/
        e[11]
      ) : "var(--block-label-text-color)"), St(t, "--bg-color", /*disabled*/
      e[7] ? "auto" : (
        /*background*/
        e[10]
      ));
    },
    m(a, f) {
      Sl(a, t, f), s && s.m(t, null), Hn(t, n), Hn(t, i), vo(l, i, null), r = !0, o || (u = po(
        t,
        "click",
        /*click_handler*/
        e[13]
      ), o = !0);
    },
    p(a, [f]) {
      /*show_label*/
      a[2] ? s ? s.p(a, f) : (s = ei(a), s.c(), s.m(t, n)) : s && (s.d(1), s = null), (!r || f & /*size*/
      16) && ie(
        i,
        "small",
        /*size*/
        a[4] === "small"
      ), (!r || f & /*size*/
      16) && ie(
        i,
        "large",
        /*size*/
        a[4] === "large"
      ), (!r || f & /*disabled*/
      128) && (t.disabled = /*disabled*/
      a[7]), (!r || f & /*label*/
      2) && Se(
        t,
        "aria-label",
        /*label*/
        a[1]
      ), (!r || f & /*hasPopup*/
      256) && Se(
        t,
        "aria-haspopup",
        /*hasPopup*/
        a[8]
      ), (!r || f & /*label*/
      2) && Se(
        t,
        "title",
        /*label*/
        a[1]
      ), (!r || f & /*pending*/
      8) && ie(
        t,
        "pending",
        /*pending*/
        a[3]
      ), (!r || f & /*padded*/
      32) && ie(
        t,
        "padded",
        /*padded*/
        a[5]
      ), (!r || f & /*highlight*/
      64) && ie(
        t,
        "highlight",
        /*highlight*/
        a[6]
      ), (!r || f & /*transparent*/
      512) && ie(
        t,
        "transparent",
        /*transparent*/
        a[9]
      ), f & /*disabled, _color*/
      2176 && St(t, "color", !/*disabled*/
      a[7] && /*_color*/
      a[11] ? (
        /*_color*/
        a[11]
      ) : "var(--block-label-text-color)"), f & /*disabled, background*/
      1152 && St(t, "--bg-color", /*disabled*/
      a[7] ? "auto" : (
        /*background*/
        a[10]
      ));
    },
    i(a) {
      r || (Ho(l.$$.fragment, a), r = !0);
    },
    o(a) {
      So(l.$$.fragment, a), r = !1;
    },
    d(a) {
      a && Hl(t), s && s.d(), bo(l), o = !1, u();
    }
  };
}
function To(e, t, n) {
  let i, { Icon: l } = t, { label: r = "" } = t, { show_label: o = !1 } = t, { pending: u = !1 } = t, { size: s = "small" } = t, { padded: a = !0 } = t, { highlight: f = !1 } = t, { disabled: c = !1 } = t, { hasPopup: h = !1 } = t, { color: _ = "var(--block-label-text-color)" } = t, { transparent: d = !1 } = t, { background: v = "var(--background-fill-primary)" } = t;
  function A(w) {
    _o.call(this, e, w);
  }
  return e.$$set = (w) => {
    "Icon" in w && n(0, l = w.Icon), "label" in w && n(1, r = w.label), "show_label" in w && n(2, o = w.show_label), "pending" in w && n(3, u = w.pending), "size" in w && n(4, s = w.size), "padded" in w && n(5, a = w.padded), "highlight" in w && n(6, f = w.highlight), "disabled" in w && n(7, c = w.disabled), "hasPopup" in w && n(8, h = w.hasPopup), "color" in w && n(12, _ = w.color), "transparent" in w && n(9, d = w.transparent), "background" in w && n(10, v = w.background);
  }, e.$$.update = () => {
    e.$$.dirty & /*highlight, color*/
    4160 && n(11, i = f ? "var(--color-accent)" : _);
  }, [
    l,
    r,
    o,
    u,
    s,
    a,
    f,
    c,
    h,
    d,
    v,
    i,
    _,
    A
  ];
}
class We extends ho {
  constructor(t) {
    super(), go(this, t, To, Ao, wo, {
      Icon: 0,
      label: 1,
      show_label: 2,
      pending: 3,
      size: 4,
      padded: 5,
      highlight: 6,
      disabled: 7,
      hasPopup: 8,
      color: 12,
      transparent: 9,
      background: 10
    });
  }
}
const {
  SvelteComponent: Bo,
  append: Co,
  attr: tn,
  binding_callbacks: Io,
  create_slot: Po,
  detach: Lo,
  element: ti,
  get_all_dirty_from_scope: No,
  get_slot_changes: Oo,
  init: Mo,
  insert: Ro,
  safe_not_equal: Do,
  toggle_class: Me,
  transition_in: Uo,
  transition_out: Go,
  update_slot_base: Fo
} = window.__gradio__svelte__internal;
function jo(e) {
  let t, n, i;
  const l = (
    /*#slots*/
    e[5].default
  ), r = Po(
    l,
    e,
    /*$$scope*/
    e[4],
    null
  );
  return {
    c() {
      t = ti("div"), n = ti("div"), r && r.c(), tn(n, "class", "icon svelte-3w3rth"), tn(t, "class", "empty svelte-3w3rth"), tn(t, "aria-label", "Empty value"), Me(
        t,
        "small",
        /*size*/
        e[0] === "small"
      ), Me(
        t,
        "large",
        /*size*/
        e[0] === "large"
      ), Me(
        t,
        "unpadded_box",
        /*unpadded_box*/
        e[1]
      ), Me(
        t,
        "small_parent",
        /*parent_height*/
        e[3]
      );
    },
    m(o, u) {
      Ro(o, t, u), Co(t, n), r && r.m(n, null), e[6](t), i = !0;
    },
    p(o, [u]) {
      r && r.p && (!i || u & /*$$scope*/
      16) && Fo(
        r,
        l,
        o,
        /*$$scope*/
        o[4],
        i ? Oo(
          l,
          /*$$scope*/
          o[4],
          u,
          null
        ) : No(
          /*$$scope*/
          o[4]
        ),
        null
      ), (!i || u & /*size*/
      1) && Me(
        t,
        "small",
        /*size*/
        o[0] === "small"
      ), (!i || u & /*size*/
      1) && Me(
        t,
        "large",
        /*size*/
        o[0] === "large"
      ), (!i || u & /*unpadded_box*/
      2) && Me(
        t,
        "unpadded_box",
        /*unpadded_box*/
        o[1]
      ), (!i || u & /*parent_height*/
      8) && Me(
        t,
        "small_parent",
        /*parent_height*/
        o[3]
      );
    },
    i(o) {
      i || (Uo(r, o), i = !0);
    },
    o(o) {
      Go(r, o), i = !1;
    },
    d(o) {
      o && Lo(t), r && r.d(o), e[6](null);
    }
  };
}
function Vo(e) {
  let t, n = e[0], i = 1;
  for (; i < e.length; ) {
    const l = e[i], r = e[i + 1];
    if (i += 2, (l === "optionalAccess" || l === "optionalCall") && n == null)
      return;
    l === "access" || l === "optionalAccess" ? (t = n, n = r(n)) : (l === "call" || l === "optionalCall") && (n = r((...o) => n.call(t, ...o)), t = void 0);
  }
  return n;
}
function qo(e, t, n) {
  let i, { $$slots: l = {}, $$scope: r } = t, { size: o = "small" } = t, { unpadded_box: u = !1 } = t, s;
  function a(c) {
    if (!c)
      return !1;
    const { height: h } = c.getBoundingClientRect(), { height: _ } = Vo([
      c,
      "access",
      (d) => d.parentElement,
      "optionalAccess",
      (d) => d.getBoundingClientRect,
      "call",
      (d) => d()
    ]) || { height: h };
    return h > _ + 2;
  }
  function f(c) {
    Io[c ? "unshift" : "push"](() => {
      s = c, n(2, s);
    });
  }
  return e.$$set = (c) => {
    "size" in c && n(0, o = c.size), "unpadded_box" in c && n(1, u = c.unpadded_box), "$$scope" in c && n(4, r = c.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty & /*el*/
    4 && n(3, i = a(s));
  }, [o, u, s, i, r, l, f];
}
class xo extends Bo {
  constructor(t) {
    super(), Mo(this, t, qo, jo, Do, { size: 0, unpadded_box: 1 });
  }
}
const {
  SvelteComponent: zo,
  append: nn,
  attr: ue,
  detach: Xo,
  init: Zo,
  insert: Wo,
  noop: ln,
  safe_not_equal: Qo,
  set_style: ge,
  svg_element: At
} = window.__gradio__svelte__internal;
function Jo(e) {
  let t, n, i, l;
  return {
    c() {
      t = At("svg"), n = At("g"), i = At("path"), l = At("path"), ue(i, "d", "M18,6L6.087,17.913"), ge(i, "fill", "none"), ge(i, "fill-rule", "nonzero"), ge(i, "stroke-width", "2px"), ue(n, "transform", "matrix(1.14096,-0.140958,-0.140958,1.14096,-0.0559523,0.0559523)"), ue(l, "d", "M4.364,4.364L19.636,19.636"), ge(l, "fill", "none"), ge(l, "fill-rule", "nonzero"), ge(l, "stroke-width", "2px"), ue(t, "width", "100%"), ue(t, "height", "100%"), ue(t, "viewBox", "0 0 24 24"), ue(t, "version", "1.1"), ue(t, "xmlns", "http://www.w3.org/2000/svg"), ue(t, "xmlns:xlink", "http://www.w3.org/1999/xlink"), ue(t, "xml:space", "preserve"), ue(t, "stroke", "currentColor"), ge(t, "fill-rule", "evenodd"), ge(t, "clip-rule", "evenodd"), ge(t, "stroke-linecap", "round"), ge(t, "stroke-linejoin", "round");
    },
    m(r, o) {
      Wo(r, t, o), nn(t, n), nn(n, i), nn(t, l);
    },
    p: ln,
    i: ln,
    o: ln,
    d(r) {
      r && Xo(t);
    }
  };
}
class Yo extends zo {
  constructor(t) {
    super(), Zo(this, t, null, Jo, Qo, {});
  }
}
const {
  SvelteComponent: Ko,
  append: $o,
  attr: ht,
  detach: es,
  init: ts,
  insert: ns,
  noop: rn,
  safe_not_equal: is,
  svg_element: ni
} = window.__gradio__svelte__internal;
function ls(e) {
  let t, n;
  return {
    c() {
      t = ni("svg"), n = ni("path"), ht(n, "d", "M23,20a5,5,0,0,0-3.89,1.89L11.8,17.32a4.46,4.46,0,0,0,0-2.64l7.31-4.57A5,5,0,1,0,18,7a4.79,4.79,0,0,0,.2,1.32l-7.31,4.57a5,5,0,1,0,0,6.22l7.31,4.57A4.79,4.79,0,0,0,18,25a5,5,0,1,0,5-5ZM23,4a3,3,0,1,1-3,3A3,3,0,0,1,23,4ZM7,19a3,3,0,1,1,3-3A3,3,0,0,1,7,19Zm16,9a3,3,0,1,1,3-3A3,3,0,0,1,23,28Z"), ht(n, "fill", "currentColor"), ht(t, "id", "icon"), ht(t, "xmlns", "http://www.w3.org/2000/svg"), ht(t, "viewBox", "0 0 32 32");
    },
    m(i, l) {
      ns(i, t, l), $o(t, n);
    },
    p: rn,
    i: rn,
    o: rn,
    d(i) {
      i && es(t);
    }
  };
}
class rs extends Ko {
  constructor(t) {
    super(), ts(this, t, null, ls, is, {});
  }
}
const {
  SvelteComponent: os,
  append: ss,
  attr: Je,
  detach: as,
  init: us,
  insert: fs,
  noop: on,
  safe_not_equal: cs,
  svg_element: ii
} = window.__gradio__svelte__internal;
function hs(e) {
  let t, n;
  return {
    c() {
      t = ii("svg"), n = ii("path"), Je(n, "fill", "currentColor"), Je(n, "d", "M26 24v4H6v-4H4v4a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2v-4zm0-10l-1.41-1.41L17 20.17V2h-2v18.17l-7.59-7.58L6 14l10 10l10-10z"), Je(t, "xmlns", "http://www.w3.org/2000/svg"), Je(t, "width", "100%"), Je(t, "height", "100%"), Je(t, "viewBox", "0 0 32 32");
    },
    m(i, l) {
      fs(i, t, l), ss(t, n);
    },
    p: on,
    i: on,
    o: on,
    d(i) {
      i && as(t);
    }
  };
}
class _s extends os {
  constructor(t) {
    super(), us(this, t, null, hs, cs, {});
  }
}
const {
  SvelteComponent: ms,
  append: ds,
  attr: fe,
  detach: bs,
  init: gs,
  insert: ps,
  noop: sn,
  safe_not_equal: vs,
  svg_element: li
} = window.__gradio__svelte__internal;
function ws(e) {
  let t, n;
  return {
    c() {
      t = li("svg"), n = li("path"), fe(n, "d", "M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"), fe(t, "xmlns", "http://www.w3.org/2000/svg"), fe(t, "width", "100%"), fe(t, "height", "100%"), fe(t, "viewBox", "0 0 24 24"), fe(t, "fill", "none"), fe(t, "stroke", "currentColor"), fe(t, "stroke-width", "1.5"), fe(t, "stroke-linecap", "round"), fe(t, "stroke-linejoin", "round"), fe(t, "class", "feather feather-edit-2");
    },
    m(i, l) {
      ps(i, t, l), ds(t, n);
    },
    p: sn,
    i: sn,
    o: sn,
    d(i) {
      i && bs(t);
    }
  };
}
class ys extends ms {
  constructor(t) {
    super(), gs(this, t, null, ws, vs, {});
  }
}
const {
  SvelteComponent: Es,
  append: an,
  attr: j,
  detach: ks,
  init: Hs,
  insert: Ss,
  noop: un,
  safe_not_equal: As,
  svg_element: Tt
} = window.__gradio__svelte__internal;
function Ts(e) {
  let t, n, i, l;
  return {
    c() {
      t = Tt("svg"), n = Tt("rect"), i = Tt("circle"), l = Tt("polyline"), j(n, "x", "3"), j(n, "y", "3"), j(n, "width", "18"), j(n, "height", "18"), j(n, "rx", "2"), j(n, "ry", "2"), j(i, "cx", "8.5"), j(i, "cy", "8.5"), j(i, "r", "1.5"), j(l, "points", "21 15 16 10 5 21"), j(t, "xmlns", "http://www.w3.org/2000/svg"), j(t, "width", "100%"), j(t, "height", "100%"), j(t, "viewBox", "0 0 24 24"), j(t, "fill", "none"), j(t, "stroke", "currentColor"), j(t, "stroke-width", "1.5"), j(t, "stroke-linecap", "round"), j(t, "stroke-linejoin", "round"), j(t, "class", "feather feather-image");
    },
    m(r, o) {
      Ss(r, t, o), an(t, n), an(t, i), an(t, l);
    },
    p: un,
    i: un,
    o: un,
    d(r) {
      r && ks(t);
    }
  };
}
let Al = class extends Es {
  constructor(t) {
    super(), Hs(this, t, null, Ts, As, {});
  }
};
const {
  SvelteComponent: Bs,
  append: ri,
  attr: J,
  detach: Cs,
  init: Is,
  insert: Ps,
  noop: oi,
  safe_not_equal: Ls,
  svg_element: fn
} = window.__gradio__svelte__internal;
function Ns(e) {
  let t, n, i, l;
  return {
    c() {
      t = fn("svg"), n = fn("path"), i = fn("path"), J(n, "stroke", "currentColor"), J(n, "stroke-width", "1.5"), J(n, "stroke-linecap", "round"), J(n, "d", "M16.472 20H4.1a.6.6 0 0 1-.6-.6V9.6a.6.6 0 0 1 .6-.6h2.768a2 2 0 0 0 1.715-.971l2.71-4.517a1.631 1.631 0 0 1 2.961 1.308l-1.022 3.408a.6.6 0 0 0 .574.772h4.575a2 2 0 0 1 1.93 2.526l-1.91 7A2 2 0 0 1 16.473 20Z"), J(i, "stroke", "currentColor"), J(i, "stroke-width", "1.5"), J(i, "stroke-linecap", "round"), J(i, "stroke-linejoin", "round"), J(i, "d", "M7 20V9"), J(t, "xmlns", "http://www.w3.org/2000/svg"), J(t, "viewBox", "0 0 24 24"), J(t, "fill", l = /*selected*/
      e[0] ? "currentColor" : "none"), J(t, "stroke-width", "1.5"), J(t, "color", "currentColor");
    },
    m(r, o) {
      Ps(r, t, o), ri(t, n), ri(t, i);
    },
    p(r, [o]) {
      o & /*selected*/
      1 && l !== (l = /*selected*/
      r[0] ? "currentColor" : "none") && J(t, "fill", l);
    },
    i: oi,
    o: oi,
    d(r) {
      r && Cs(t);
    }
  };
}
function Os(e, t, n) {
  let { selected: i } = t;
  return e.$$set = (l) => {
    "selected" in l && n(0, i = l.selected);
  }, [i];
}
class Ms extends Bs {
  constructor(t) {
    super(), Is(this, t, Os, Ns, Ls, { selected: 0 });
  }
}
const {
  SvelteComponent: Rs,
  append: si,
  attr: le,
  detach: Ds,
  init: Us,
  insert: Gs,
  noop: cn,
  safe_not_equal: Fs,
  svg_element: hn
} = window.__gradio__svelte__internal;
function js(e) {
  let t, n, i;
  return {
    c() {
      t = hn("svg"), n = hn("polyline"), i = hn("path"), le(n, "points", "1 4 1 10 7 10"), le(i, "d", "M3.51 15a9 9 0 1 0 2.13-9.36L1 10"), le(t, "xmlns", "http://www.w3.org/2000/svg"), le(t, "width", "100%"), le(t, "height", "100%"), le(t, "viewBox", "0 0 24 24"), le(t, "fill", "none"), le(t, "stroke", "currentColor"), le(t, "stroke-width", "2"), le(t, "stroke-linecap", "round"), le(t, "stroke-linejoin", "round"), le(t, "class", "feather feather-rotate-ccw");
    },
    m(l, r) {
      Gs(l, t, r), si(t, n), si(t, i);
    },
    p: cn,
    i: cn,
    o: cn,
    d(l) {
      l && Ds(t);
    }
  };
}
class Vs extends Rs {
  constructor(t) {
    super(), Us(this, t, null, js, Fs, {});
  }
}
const qs = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], ai = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
qs.reduce(
  (e, { color: t, primary: n, secondary: i }) => ({
    ...e,
    [t]: {
      primary: ai[t][n],
      secondary: ai[t][i]
    }
  }),
  {}
);
class xs extends Error {
  constructor(t) {
    super(t), this.name = "ShareError";
  }
}
const {
  SvelteComponent: zs,
  create_component: Xs,
  destroy_component: Zs,
  init: Ws,
  mount_component: Qs,
  safe_not_equal: Js,
  transition_in: Ys,
  transition_out: Ks
} = window.__gradio__svelte__internal, { createEventDispatcher: $s } = window.__gradio__svelte__internal;
function ea(e) {
  let t, n;
  return t = new We({
    props: {
      Icon: rs,
      label: (
        /*i18n*/
        e[2]("common.share")
      ),
      pending: (
        /*pending*/
        e[3]
      )
    }
  }), t.$on(
    "click",
    /*click_handler*/
    e[5]
  ), {
    c() {
      Xs(t.$$.fragment);
    },
    m(i, l) {
      Qs(t, i, l), n = !0;
    },
    p(i, [l]) {
      const r = {};
      l & /*i18n*/
      4 && (r.label = /*i18n*/
      i[2]("common.share")), l & /*pending*/
      8 && (r.pending = /*pending*/
      i[3]), t.$set(r);
    },
    i(i) {
      n || (Ys(t.$$.fragment, i), n = !0);
    },
    o(i) {
      Ks(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Zs(t, i);
    }
  };
}
function ta(e, t, n) {
  const i = $s();
  let { formatter: l } = t, { value: r } = t, { i18n: o } = t, u = !1;
  const s = async () => {
    try {
      n(3, u = !0);
      const a = await l(r);
      i("share", { description: a });
    } catch (a) {
      console.error(a);
      let f = a instanceof xs ? a.message : "Share failed.";
      i("error", f);
    } finally {
      n(3, u = !1);
    }
  };
  return e.$$set = (a) => {
    "formatter" in a && n(0, l = a.formatter), "value" in a && n(1, r = a.value), "i18n" in a && n(2, o = a.i18n);
  }, [l, r, o, u, i, s];
}
class na extends zs {
  constructor(t) {
    super(), Ws(this, t, ta, ea, Js, { formatter: 0, value: 1, i18n: 2 });
  }
}
function Ke(e) {
  let t = ["", "k", "M", "G", "T", "P", "E", "Z"], n = 0;
  for (; e > 1e3 && n < t.length - 1; )
    e /= 1e3, n++;
  let i = t[n];
  return (Number.isInteger(e) ? e : e.toFixed(1)) + i;
}
function Xe() {
}
function ia(e) {
  return e();
}
function la(e) {
  e.forEach(ia);
}
function ra(e) {
  return typeof e == "function";
}
function oa(e, t) {
  return e != e ? t == t : e !== t || e && typeof e == "object" || typeof e == "function";
}
function sa(e, ...t) {
  if (e == null) {
    for (const i of t)
      i(void 0);
    return Xe;
  }
  const n = e.subscribe(...t);
  return n.unsubscribe ? () => n.unsubscribe() : n;
}
const Tl = typeof window < "u";
let ui = Tl ? () => window.performance.now() : () => Date.now(), Bl = Tl ? (e) => requestAnimationFrame(e) : Xe;
const tt = /* @__PURE__ */ new Set();
function Cl(e) {
  tt.forEach((t) => {
    t.c(e) || (tt.delete(t), t.f());
  }), tt.size !== 0 && Bl(Cl);
}
function aa(e) {
  let t;
  return tt.size === 0 && Bl(Cl), {
    promise: new Promise((n) => {
      tt.add(t = { c: e, f: n });
    }),
    abort() {
      tt.delete(t);
    }
  };
}
const Ye = [];
function ua(e, t) {
  return {
    subscribe: vt(e, t).subscribe
  };
}
function vt(e, t = Xe) {
  let n;
  const i = /* @__PURE__ */ new Set();
  function l(u) {
    if (oa(e, u) && (e = u, n)) {
      const s = !Ye.length;
      for (const a of i)
        a[1](), Ye.push(a, e);
      if (s) {
        for (let a = 0; a < Ye.length; a += 2)
          Ye[a][0](Ye[a + 1]);
        Ye.length = 0;
      }
    }
  }
  function r(u) {
    l(u(e));
  }
  function o(u, s = Xe) {
    const a = [u, s];
    return i.add(a), i.size === 1 && (n = t(l, r) || Xe), u(e), () => {
      i.delete(a), i.size === 0 && n && (n(), n = null);
    };
  }
  return { set: l, update: r, subscribe: o };
}
function at(e, t, n) {
  const i = !Array.isArray(e), l = i ? [e] : e;
  if (!l.every(Boolean))
    throw new Error("derived() expects stores as input, got a falsy value");
  const r = t.length < 2;
  return ua(n, (o, u) => {
    let s = !1;
    const a = [];
    let f = 0, c = Xe;
    const h = () => {
      if (f)
        return;
      c();
      const d = t(i ? a[0] : a, o, u);
      r ? o(d) : c = ra(d) ? d : Xe;
    }, _ = l.map(
      (d, v) => sa(
        d,
        (A) => {
          a[v] = A, f &= ~(1 << v), s && h();
        },
        () => {
          f |= 1 << v;
        }
      )
    );
    return s = !0, h(), function() {
      la(_), c(), s = !1;
    };
  });
}
function fi(e) {
  return Object.prototype.toString.call(e) === "[object Date]";
}
function An(e, t, n, i) {
  if (typeof n == "number" || fi(n)) {
    const l = i - n, r = (n - t) / (e.dt || 1 / 60), o = e.opts.stiffness * l, u = e.opts.damping * r, s = (o - u) * e.inv_mass, a = (r + s) * e.dt;
    return Math.abs(a) < e.opts.precision && Math.abs(l) < e.opts.precision ? i : (e.settled = !1, fi(n) ? new Date(n.getTime() + a) : n + a);
  } else {
    if (Array.isArray(n))
      return n.map(
        (l, r) => An(e, t[r], n[r], i[r])
      );
    if (typeof n == "object") {
      const l = {};
      for (const r in n)
        l[r] = An(e, t[r], n[r], i[r]);
      return l;
    } else
      throw new Error(`Cannot spring ${typeof n} values`);
  }
}
function ci(e, t = {}) {
  const n = vt(e), { stiffness: i = 0.15, damping: l = 0.8, precision: r = 0.01 } = t;
  let o, u, s, a = e, f = e, c = 1, h = 0, _ = !1;
  function d(A, w = {}) {
    f = A;
    const E = s = {};
    return e == null || w.hard || v.stiffness >= 1 && v.damping >= 1 ? (_ = !0, o = ui(), a = A, n.set(e = f), Promise.resolve()) : (w.soft && (h = 1 / ((w.soft === !0 ? 0.5 : +w.soft) * 60), c = 0), u || (o = ui(), _ = !1, u = aa((p) => {
      if (_)
        return _ = !1, u = null, !1;
      c = Math.min(c + h, 1);
      const m = {
        inv_mass: c,
        opts: v,
        settled: !0,
        dt: (p - o) * 60 / 1e3
      }, k = An(m, a, e, f);
      return o = p, a = e, n.set(e = k), m.settled && (u = null), !m.settled;
    })), new Promise((p) => {
      u.promise.then(() => {
        E === s && p();
      });
    }));
  }
  const v = {
    set: d,
    update: (A, w) => d(A(f, e), w),
    subscribe: n.subscribe,
    stiffness: i,
    damping: l,
    precision: r
  };
  return v;
}
const {
  SvelteComponent: fa,
  append: ce,
  attr: N,
  component_subscribe: hi,
  detach: ca,
  element: ha,
  init: _a,
  insert: ma,
  noop: _i,
  safe_not_equal: da,
  set_style: Bt,
  svg_element: he,
  toggle_class: mi
} = window.__gradio__svelte__internal, { onMount: ba } = window.__gradio__svelte__internal;
function ga(e) {
  let t, n, i, l, r, o, u, s, a, f, c, h;
  return {
    c() {
      t = ha("div"), n = he("svg"), i = he("g"), l = he("path"), r = he("path"), o = he("path"), u = he("path"), s = he("g"), a = he("path"), f = he("path"), c = he("path"), h = he("path"), N(l, "d", "M255.926 0.754768L509.702 139.936V221.027L255.926 81.8465V0.754768Z"), N(l, "fill", "#FF7C00"), N(l, "fill-opacity", "0.4"), N(l, "class", "svelte-43sxxs"), N(r, "d", "M509.69 139.936L254.981 279.641V361.255L509.69 221.55V139.936Z"), N(r, "fill", "#FF7C00"), N(r, "class", "svelte-43sxxs"), N(o, "d", "M0.250138 139.937L254.981 279.641V361.255L0.250138 221.55V139.937Z"), N(o, "fill", "#FF7C00"), N(o, "fill-opacity", "0.4"), N(o, "class", "svelte-43sxxs"), N(u, "d", "M255.923 0.232622L0.236328 139.936V221.55L255.923 81.8469V0.232622Z"), N(u, "fill", "#FF7C00"), N(u, "class", "svelte-43sxxs"), Bt(i, "transform", "translate(" + /*$top*/
      e[1][0] + "px, " + /*$top*/
      e[1][1] + "px)"), N(a, "d", "M255.926 141.5L509.702 280.681V361.773L255.926 222.592V141.5Z"), N(a, "fill", "#FF7C00"), N(a, "fill-opacity", "0.4"), N(a, "class", "svelte-43sxxs"), N(f, "d", "M509.69 280.679L254.981 420.384V501.998L509.69 362.293V280.679Z"), N(f, "fill", "#FF7C00"), N(f, "class", "svelte-43sxxs"), N(c, "d", "M0.250138 280.681L254.981 420.386V502L0.250138 362.295V280.681Z"), N(c, "fill", "#FF7C00"), N(c, "fill-opacity", "0.4"), N(c, "class", "svelte-43sxxs"), N(h, "d", "M255.923 140.977L0.236328 280.68V362.294L255.923 222.591V140.977Z"), N(h, "fill", "#FF7C00"), N(h, "class", "svelte-43sxxs"), Bt(s, "transform", "translate(" + /*$bottom*/
      e[2][0] + "px, " + /*$bottom*/
      e[2][1] + "px)"), N(n, "viewBox", "-1200 -1200 3000 3000"), N(n, "fill", "none"), N(n, "xmlns", "http://www.w3.org/2000/svg"), N(n, "class", "svelte-43sxxs"), N(t, "class", "svelte-43sxxs"), mi(
        t,
        "margin",
        /*margin*/
        e[0]
      );
    },
    m(_, d) {
      ma(_, t, d), ce(t, n), ce(n, i), ce(i, l), ce(i, r), ce(i, o), ce(i, u), ce(n, s), ce(s, a), ce(s, f), ce(s, c), ce(s, h);
    },
    p(_, [d]) {
      d & /*$top*/
      2 && Bt(i, "transform", "translate(" + /*$top*/
      _[1][0] + "px, " + /*$top*/
      _[1][1] + "px)"), d & /*$bottom*/
      4 && Bt(s, "transform", "translate(" + /*$bottom*/
      _[2][0] + "px, " + /*$bottom*/
      _[2][1] + "px)"), d & /*margin*/
      1 && mi(
        t,
        "margin",
        /*margin*/
        _[0]
      );
    },
    i: _i,
    o: _i,
    d(_) {
      _ && ca(t);
    }
  };
}
function pa(e, t, n) {
  let i, l, { margin: r = !0 } = t;
  const o = ci([0, 0]);
  hi(e, o, (h) => n(1, i = h));
  const u = ci([0, 0]);
  hi(e, u, (h) => n(2, l = h));
  let s;
  async function a() {
    await Promise.all([o.set([125, 140]), u.set([-125, -140])]), await Promise.all([o.set([-125, 140]), u.set([125, -140])]), await Promise.all([o.set([-125, 0]), u.set([125, -0])]), await Promise.all([o.set([125, 0]), u.set([-125, 0])]);
  }
  async function f() {
    await a(), s || f();
  }
  async function c() {
    await Promise.all([o.set([125, 0]), u.set([-125, 0])]), f();
  }
  return ba(() => (c(), () => s = !0)), e.$$set = (h) => {
    "margin" in h && n(0, r = h.margin);
  }, [r, i, l, o, u];
}
class Il extends fa {
  constructor(t) {
    super(), _a(this, t, pa, ga, da, { margin: 0 });
  }
}
const {
  SvelteComponent: va,
  append: qe,
  attr: ve,
  binding_callbacks: di,
  check_outros: Pl,
  create_component: wa,
  create_slot: ya,
  destroy_component: Ea,
  destroy_each: Ll,
  detach: B,
  element: Te,
  empty: ut,
  ensure_array_like: Mt,
  get_all_dirty_from_scope: ka,
  get_slot_changes: Ha,
  group_outros: Nl,
  init: Sa,
  insert: C,
  mount_component: Aa,
  noop: Tn,
  safe_not_equal: Ta,
  set_data: se,
  set_style: De,
  space: we,
  text: F,
  toggle_class: re,
  transition_in: nt,
  transition_out: it,
  update_slot_base: Ba
} = window.__gradio__svelte__internal, { tick: Ca } = window.__gradio__svelte__internal, { onDestroy: Ia } = window.__gradio__svelte__internal, Pa = (e) => ({}), bi = (e) => ({});
function gi(e, t, n) {
  const i = e.slice();
  return i[38] = t[n], i[40] = n, i;
}
function pi(e, t, n) {
  const i = e.slice();
  return i[38] = t[n], i;
}
function La(e) {
  let t, n = (
    /*i18n*/
    e[1]("common.error") + ""
  ), i, l, r;
  const o = (
    /*#slots*/
    e[29].error
  ), u = ya(
    o,
    e,
    /*$$scope*/
    e[28],
    bi
  );
  return {
    c() {
      t = Te("span"), i = F(n), l = we(), u && u.c(), ve(t, "class", "error svelte-1txqlrd");
    },
    m(s, a) {
      C(s, t, a), qe(t, i), C(s, l, a), u && u.m(s, a), r = !0;
    },
    p(s, a) {
      (!r || a[0] & /*i18n*/
      2) && n !== (n = /*i18n*/
      s[1]("common.error") + "") && se(i, n), u && u.p && (!r || a[0] & /*$$scope*/
      268435456) && Ba(
        u,
        o,
        s,
        /*$$scope*/
        s[28],
        r ? Ha(
          o,
          /*$$scope*/
          s[28],
          a,
          Pa
        ) : ka(
          /*$$scope*/
          s[28]
        ),
        bi
      );
    },
    i(s) {
      r || (nt(u, s), r = !0);
    },
    o(s) {
      it(u, s), r = !1;
    },
    d(s) {
      s && (B(t), B(l)), u && u.d(s);
    }
  };
}
function Na(e) {
  let t, n, i, l, r, o, u, s, a, f = (
    /*variant*/
    e[8] === "default" && /*show_eta_bar*/
    e[18] && /*show_progress*/
    e[6] === "full" && vi(e)
  );
  function c(p, m) {
    if (
      /*progress*/
      p[7]
    )
      return Ra;
    if (
      /*queue_position*/
      p[2] !== null && /*queue_size*/
      p[3] !== void 0 && /*queue_position*/
      p[2] >= 0
    )
      return Ma;
    if (
      /*queue_position*/
      p[2] === 0
    )
      return Oa;
  }
  let h = c(e), _ = h && h(e), d = (
    /*timer*/
    e[5] && Ei(e)
  );
  const v = [Fa, Ga], A = [];
  function w(p, m) {
    return (
      /*last_progress_level*/
      p[15] != null ? 0 : (
        /*show_progress*/
        p[6] === "full" ? 1 : -1
      )
    );
  }
  ~(r = w(e)) && (o = A[r] = v[r](e));
  let E = !/*timer*/
  e[5] && Ci(e);
  return {
    c() {
      f && f.c(), t = we(), n = Te("div"), _ && _.c(), i = we(), d && d.c(), l = we(), o && o.c(), u = we(), E && E.c(), s = ut(), ve(n, "class", "progress-text svelte-1txqlrd"), re(
        n,
        "meta-text-center",
        /*variant*/
        e[8] === "center"
      ), re(
        n,
        "meta-text",
        /*variant*/
        e[8] === "default"
      );
    },
    m(p, m) {
      f && f.m(p, m), C(p, t, m), C(p, n, m), _ && _.m(n, null), qe(n, i), d && d.m(n, null), C(p, l, m), ~r && A[r].m(p, m), C(p, u, m), E && E.m(p, m), C(p, s, m), a = !0;
    },
    p(p, m) {
      /*variant*/
      p[8] === "default" && /*show_eta_bar*/
      p[18] && /*show_progress*/
      p[6] === "full" ? f ? f.p(p, m) : (f = vi(p), f.c(), f.m(t.parentNode, t)) : f && (f.d(1), f = null), h === (h = c(p)) && _ ? _.p(p, m) : (_ && _.d(1), _ = h && h(p), _ && (_.c(), _.m(n, i))), /*timer*/
      p[5] ? d ? d.p(p, m) : (d = Ei(p), d.c(), d.m(n, null)) : d && (d.d(1), d = null), (!a || m[0] & /*variant*/
      256) && re(
        n,
        "meta-text-center",
        /*variant*/
        p[8] === "center"
      ), (!a || m[0] & /*variant*/
      256) && re(
        n,
        "meta-text",
        /*variant*/
        p[8] === "default"
      );
      let k = r;
      r = w(p), r === k ? ~r && A[r].p(p, m) : (o && (Nl(), it(A[k], 1, 1, () => {
        A[k] = null;
      }), Pl()), ~r ? (o = A[r], o ? o.p(p, m) : (o = A[r] = v[r](p), o.c()), nt(o, 1), o.m(u.parentNode, u)) : o = null), /*timer*/
      p[5] ? E && (E.d(1), E = null) : E ? E.p(p, m) : (E = Ci(p), E.c(), E.m(s.parentNode, s));
    },
    i(p) {
      a || (nt(o), a = !0);
    },
    o(p) {
      it(o), a = !1;
    },
    d(p) {
      p && (B(t), B(n), B(l), B(u), B(s)), f && f.d(p), _ && _.d(), d && d.d(), ~r && A[r].d(p), E && E.d(p);
    }
  };
}
function vi(e) {
  let t, n = `translateX(${/*eta_level*/
  (e[17] || 0) * 100 - 100}%)`;
  return {
    c() {
      t = Te("div"), ve(t, "class", "eta-bar svelte-1txqlrd"), De(t, "transform", n);
    },
    m(i, l) {
      C(i, t, l);
    },
    p(i, l) {
      l[0] & /*eta_level*/
      131072 && n !== (n = `translateX(${/*eta_level*/
      (i[17] || 0) * 100 - 100}%)`) && De(t, "transform", n);
    },
    d(i) {
      i && B(t);
    }
  };
}
function Oa(e) {
  let t;
  return {
    c() {
      t = F("processing |");
    },
    m(n, i) {
      C(n, t, i);
    },
    p: Tn,
    d(n) {
      n && B(t);
    }
  };
}
function Ma(e) {
  let t, n = (
    /*queue_position*/
    e[2] + 1 + ""
  ), i, l, r, o;
  return {
    c() {
      t = F("queue: "), i = F(n), l = F("/"), r = F(
        /*queue_size*/
        e[3]
      ), o = F(" |");
    },
    m(u, s) {
      C(u, t, s), C(u, i, s), C(u, l, s), C(u, r, s), C(u, o, s);
    },
    p(u, s) {
      s[0] & /*queue_position*/
      4 && n !== (n = /*queue_position*/
      u[2] + 1 + "") && se(i, n), s[0] & /*queue_size*/
      8 && se(
        r,
        /*queue_size*/
        u[3]
      );
    },
    d(u) {
      u && (B(t), B(i), B(l), B(r), B(o));
    }
  };
}
function Ra(e) {
  let t, n = Mt(
    /*progress*/
    e[7]
  ), i = [];
  for (let l = 0; l < n.length; l += 1)
    i[l] = yi(pi(e, n, l));
  return {
    c() {
      for (let l = 0; l < i.length; l += 1)
        i[l].c();
      t = ut();
    },
    m(l, r) {
      for (let o = 0; o < i.length; o += 1)
        i[o] && i[o].m(l, r);
      C(l, t, r);
    },
    p(l, r) {
      if (r[0] & /*progress*/
      128) {
        n = Mt(
          /*progress*/
          l[7]
        );
        let o;
        for (o = 0; o < n.length; o += 1) {
          const u = pi(l, n, o);
          i[o] ? i[o].p(u, r) : (i[o] = yi(u), i[o].c(), i[o].m(t.parentNode, t));
        }
        for (; o < i.length; o += 1)
          i[o].d(1);
        i.length = n.length;
      }
    },
    d(l) {
      l && B(t), Ll(i, l);
    }
  };
}
function wi(e) {
  let t, n = (
    /*p*/
    e[38].unit + ""
  ), i, l, r = " ", o;
  function u(f, c) {
    return (
      /*p*/
      f[38].length != null ? Ua : Da
    );
  }
  let s = u(e), a = s(e);
  return {
    c() {
      a.c(), t = we(), i = F(n), l = F(" | "), o = F(r);
    },
    m(f, c) {
      a.m(f, c), C(f, t, c), C(f, i, c), C(f, l, c), C(f, o, c);
    },
    p(f, c) {
      s === (s = u(f)) && a ? a.p(f, c) : (a.d(1), a = s(f), a && (a.c(), a.m(t.parentNode, t))), c[0] & /*progress*/
      128 && n !== (n = /*p*/
      f[38].unit + "") && se(i, n);
    },
    d(f) {
      f && (B(t), B(i), B(l), B(o)), a.d(f);
    }
  };
}
function Da(e) {
  let t = Ke(
    /*p*/
    e[38].index || 0
  ) + "", n;
  return {
    c() {
      n = F(t);
    },
    m(i, l) {
      C(i, n, l);
    },
    p(i, l) {
      l[0] & /*progress*/
      128 && t !== (t = Ke(
        /*p*/
        i[38].index || 0
      ) + "") && se(n, t);
    },
    d(i) {
      i && B(n);
    }
  };
}
function Ua(e) {
  let t = Ke(
    /*p*/
    e[38].index || 0
  ) + "", n, i, l = Ke(
    /*p*/
    e[38].length
  ) + "", r;
  return {
    c() {
      n = F(t), i = F("/"), r = F(l);
    },
    m(o, u) {
      C(o, n, u), C(o, i, u), C(o, r, u);
    },
    p(o, u) {
      u[0] & /*progress*/
      128 && t !== (t = Ke(
        /*p*/
        o[38].index || 0
      ) + "") && se(n, t), u[0] & /*progress*/
      128 && l !== (l = Ke(
        /*p*/
        o[38].length
      ) + "") && se(r, l);
    },
    d(o) {
      o && (B(n), B(i), B(r));
    }
  };
}
function yi(e) {
  let t, n = (
    /*p*/
    e[38].index != null && wi(e)
  );
  return {
    c() {
      n && n.c(), t = ut();
    },
    m(i, l) {
      n && n.m(i, l), C(i, t, l);
    },
    p(i, l) {
      /*p*/
      i[38].index != null ? n ? n.p(i, l) : (n = wi(i), n.c(), n.m(t.parentNode, t)) : n && (n.d(1), n = null);
    },
    d(i) {
      i && B(t), n && n.d(i);
    }
  };
}
function Ei(e) {
  let t, n = (
    /*eta*/
    e[0] ? `/${/*formatted_eta*/
    e[19]}` : ""
  ), i, l;
  return {
    c() {
      t = F(
        /*formatted_timer*/
        e[20]
      ), i = F(n), l = F("s");
    },
    m(r, o) {
      C(r, t, o), C(r, i, o), C(r, l, o);
    },
    p(r, o) {
      o[0] & /*formatted_timer*/
      1048576 && se(
        t,
        /*formatted_timer*/
        r[20]
      ), o[0] & /*eta, formatted_eta*/
      524289 && n !== (n = /*eta*/
      r[0] ? `/${/*formatted_eta*/
      r[19]}` : "") && se(i, n);
    },
    d(r) {
      r && (B(t), B(i), B(l));
    }
  };
}
function Ga(e) {
  let t, n;
  return t = new Il({
    props: { margin: (
      /*variant*/
      e[8] === "default"
    ) }
  }), {
    c() {
      wa(t.$$.fragment);
    },
    m(i, l) {
      Aa(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l[0] & /*variant*/
      256 && (r.margin = /*variant*/
      i[8] === "default"), t.$set(r);
    },
    i(i) {
      n || (nt(t.$$.fragment, i), n = !0);
    },
    o(i) {
      it(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Ea(t, i);
    }
  };
}
function Fa(e) {
  let t, n, i, l, r, o = `${/*last_progress_level*/
  e[15] * 100}%`, u = (
    /*progress*/
    e[7] != null && ki(e)
  );
  return {
    c() {
      t = Te("div"), n = Te("div"), u && u.c(), i = we(), l = Te("div"), r = Te("div"), ve(n, "class", "progress-level-inner svelte-1txqlrd"), ve(r, "class", "progress-bar svelte-1txqlrd"), De(r, "width", o), ve(l, "class", "progress-bar-wrap svelte-1txqlrd"), ve(t, "class", "progress-level svelte-1txqlrd");
    },
    m(s, a) {
      C(s, t, a), qe(t, n), u && u.m(n, null), qe(t, i), qe(t, l), qe(l, r), e[30](r);
    },
    p(s, a) {
      /*progress*/
      s[7] != null ? u ? u.p(s, a) : (u = ki(s), u.c(), u.m(n, null)) : u && (u.d(1), u = null), a[0] & /*last_progress_level*/
      32768 && o !== (o = `${/*last_progress_level*/
      s[15] * 100}%`) && De(r, "width", o);
    },
    i: Tn,
    o: Tn,
    d(s) {
      s && B(t), u && u.d(), e[30](null);
    }
  };
}
function ki(e) {
  let t, n = Mt(
    /*progress*/
    e[7]
  ), i = [];
  for (let l = 0; l < n.length; l += 1)
    i[l] = Bi(gi(e, n, l));
  return {
    c() {
      for (let l = 0; l < i.length; l += 1)
        i[l].c();
      t = ut();
    },
    m(l, r) {
      for (let o = 0; o < i.length; o += 1)
        i[o] && i[o].m(l, r);
      C(l, t, r);
    },
    p(l, r) {
      if (r[0] & /*progress_level, progress*/
      16512) {
        n = Mt(
          /*progress*/
          l[7]
        );
        let o;
        for (o = 0; o < n.length; o += 1) {
          const u = gi(l, n, o);
          i[o] ? i[o].p(u, r) : (i[o] = Bi(u), i[o].c(), i[o].m(t.parentNode, t));
        }
        for (; o < i.length; o += 1)
          i[o].d(1);
        i.length = n.length;
      }
    },
    d(l) {
      l && B(t), Ll(i, l);
    }
  };
}
function Hi(e) {
  let t, n, i, l, r = (
    /*i*/
    e[40] !== 0 && ja()
  ), o = (
    /*p*/
    e[38].desc != null && Si(e)
  ), u = (
    /*p*/
    e[38].desc != null && /*progress_level*/
    e[14] && /*progress_level*/
    e[14][
      /*i*/
      e[40]
    ] != null && Ai()
  ), s = (
    /*progress_level*/
    e[14] != null && Ti(e)
  );
  return {
    c() {
      r && r.c(), t = we(), o && o.c(), n = we(), u && u.c(), i = we(), s && s.c(), l = ut();
    },
    m(a, f) {
      r && r.m(a, f), C(a, t, f), o && o.m(a, f), C(a, n, f), u && u.m(a, f), C(a, i, f), s && s.m(a, f), C(a, l, f);
    },
    p(a, f) {
      /*p*/
      a[38].desc != null ? o ? o.p(a, f) : (o = Si(a), o.c(), o.m(n.parentNode, n)) : o && (o.d(1), o = null), /*p*/
      a[38].desc != null && /*progress_level*/
      a[14] && /*progress_level*/
      a[14][
        /*i*/
        a[40]
      ] != null ? u || (u = Ai(), u.c(), u.m(i.parentNode, i)) : u && (u.d(1), u = null), /*progress_level*/
      a[14] != null ? s ? s.p(a, f) : (s = Ti(a), s.c(), s.m(l.parentNode, l)) : s && (s.d(1), s = null);
    },
    d(a) {
      a && (B(t), B(n), B(i), B(l)), r && r.d(a), o && o.d(a), u && u.d(a), s && s.d(a);
    }
  };
}
function ja(e) {
  let t;
  return {
    c() {
      t = F(" /");
    },
    m(n, i) {
      C(n, t, i);
    },
    d(n) {
      n && B(t);
    }
  };
}
function Si(e) {
  let t = (
    /*p*/
    e[38].desc + ""
  ), n;
  return {
    c() {
      n = F(t);
    },
    m(i, l) {
      C(i, n, l);
    },
    p(i, l) {
      l[0] & /*progress*/
      128 && t !== (t = /*p*/
      i[38].desc + "") && se(n, t);
    },
    d(i) {
      i && B(n);
    }
  };
}
function Ai(e) {
  let t;
  return {
    c() {
      t = F("-");
    },
    m(n, i) {
      C(n, t, i);
    },
    d(n) {
      n && B(t);
    }
  };
}
function Ti(e) {
  let t = (100 * /*progress_level*/
  (e[14][
    /*i*/
    e[40]
  ] || 0)).toFixed(1) + "", n, i;
  return {
    c() {
      n = F(t), i = F("%");
    },
    m(l, r) {
      C(l, n, r), C(l, i, r);
    },
    p(l, r) {
      r[0] & /*progress_level*/
      16384 && t !== (t = (100 * /*progress_level*/
      (l[14][
        /*i*/
        l[40]
      ] || 0)).toFixed(1) + "") && se(n, t);
    },
    d(l) {
      l && (B(n), B(i));
    }
  };
}
function Bi(e) {
  let t, n = (
    /*p*/
    (e[38].desc != null || /*progress_level*/
    e[14] && /*progress_level*/
    e[14][
      /*i*/
      e[40]
    ] != null) && Hi(e)
  );
  return {
    c() {
      n && n.c(), t = ut();
    },
    m(i, l) {
      n && n.m(i, l), C(i, t, l);
    },
    p(i, l) {
      /*p*/
      i[38].desc != null || /*progress_level*/
      i[14] && /*progress_level*/
      i[14][
        /*i*/
        i[40]
      ] != null ? n ? n.p(i, l) : (n = Hi(i), n.c(), n.m(t.parentNode, t)) : n && (n.d(1), n = null);
    },
    d(i) {
      i && B(t), n && n.d(i);
    }
  };
}
function Ci(e) {
  let t, n;
  return {
    c() {
      t = Te("p"), n = F(
        /*loading_text*/
        e[9]
      ), ve(t, "class", "loading svelte-1txqlrd");
    },
    m(i, l) {
      C(i, t, l), qe(t, n);
    },
    p(i, l) {
      l[0] & /*loading_text*/
      512 && se(
        n,
        /*loading_text*/
        i[9]
      );
    },
    d(i) {
      i && B(t);
    }
  };
}
function Va(e) {
  let t, n, i, l, r;
  const o = [Na, La], u = [];
  function s(a, f) {
    return (
      /*status*/
      a[4] === "pending" ? 0 : (
        /*status*/
        a[4] === "error" ? 1 : -1
      )
    );
  }
  return ~(n = s(e)) && (i = u[n] = o[n](e)), {
    c() {
      t = Te("div"), i && i.c(), ve(t, "class", l = "wrap " + /*variant*/
      e[8] + " " + /*show_progress*/
      e[6] + " svelte-1txqlrd"), re(t, "hide", !/*status*/
      e[4] || /*status*/
      e[4] === "complete" || /*show_progress*/
      e[6] === "hidden"), re(
        t,
        "translucent",
        /*variant*/
        e[8] === "center" && /*status*/
        (e[4] === "pending" || /*status*/
        e[4] === "error") || /*translucent*/
        e[11] || /*show_progress*/
        e[6] === "minimal"
      ), re(
        t,
        "generating",
        /*status*/
        e[4] === "generating"
      ), re(
        t,
        "border",
        /*border*/
        e[12]
      ), De(
        t,
        "position",
        /*absolute*/
        e[10] ? "absolute" : "static"
      ), De(
        t,
        "padding",
        /*absolute*/
        e[10] ? "0" : "var(--size-8) 0"
      );
    },
    m(a, f) {
      C(a, t, f), ~n && u[n].m(t, null), e[31](t), r = !0;
    },
    p(a, f) {
      let c = n;
      n = s(a), n === c ? ~n && u[n].p(a, f) : (i && (Nl(), it(u[c], 1, 1, () => {
        u[c] = null;
      }), Pl()), ~n ? (i = u[n], i ? i.p(a, f) : (i = u[n] = o[n](a), i.c()), nt(i, 1), i.m(t, null)) : i = null), (!r || f[0] & /*variant, show_progress*/
      320 && l !== (l = "wrap " + /*variant*/
      a[8] + " " + /*show_progress*/
      a[6] + " svelte-1txqlrd")) && ve(t, "class", l), (!r || f[0] & /*variant, show_progress, status, show_progress*/
      336) && re(t, "hide", !/*status*/
      a[4] || /*status*/
      a[4] === "complete" || /*show_progress*/
      a[6] === "hidden"), (!r || f[0] & /*variant, show_progress, variant, status, translucent, show_progress*/
      2384) && re(
        t,
        "translucent",
        /*variant*/
        a[8] === "center" && /*status*/
        (a[4] === "pending" || /*status*/
        a[4] === "error") || /*translucent*/
        a[11] || /*show_progress*/
        a[6] === "minimal"
      ), (!r || f[0] & /*variant, show_progress, status*/
      336) && re(
        t,
        "generating",
        /*status*/
        a[4] === "generating"
      ), (!r || f[0] & /*variant, show_progress, border*/
      4416) && re(
        t,
        "border",
        /*border*/
        a[12]
      ), f[0] & /*absolute*/
      1024 && De(
        t,
        "position",
        /*absolute*/
        a[10] ? "absolute" : "static"
      ), f[0] & /*absolute*/
      1024 && De(
        t,
        "padding",
        /*absolute*/
        a[10] ? "0" : "var(--size-8) 0"
      );
    },
    i(a) {
      r || (nt(i), r = !0);
    },
    o(a) {
      it(i), r = !1;
    },
    d(a) {
      a && B(t), ~n && u[n].d(), e[31](null);
    }
  };
}
let Ct = [], _n = !1;
async function qa(e, t = !0) {
  if (!(window.__gradio_mode__ === "website" || window.__gradio_mode__ !== "app" && t !== !0)) {
    if (Ct.push(e), !_n)
      _n = !0;
    else
      return;
    await Ca(), requestAnimationFrame(() => {
      let n = [0, 0];
      for (let i = 0; i < Ct.length; i++) {
        const r = Ct[i].getBoundingClientRect();
        (i === 0 || r.top + window.scrollY <= n[0]) && (n[0] = r.top + window.scrollY, n[1] = i);
      }
      window.scrollTo({ top: n[0] - 20, behavior: "smooth" }), _n = !1, Ct = [];
    });
  }
}
function xa(e, t, n) {
  let i, { $$slots: l = {}, $$scope: r } = t, { i18n: o } = t, { eta: u = null } = t, { queue_position: s } = t, { queue_size: a } = t, { status: f } = t, { scroll_to_output: c = !1 } = t, { timer: h = !0 } = t, { show_progress: _ = "full" } = t, { message: d = null } = t, { progress: v = null } = t, { variant: A = "default" } = t, { loading_text: w = "Loading..." } = t, { absolute: E = !0 } = t, { translucent: p = !1 } = t, { border: m = !1 } = t, { autoscroll: k } = t, g, T = !1, S = 0, z = 0, R = null, q = null, x = 0, W = null, ee, te = null, Ee = !0;
  const de = () => {
    n(0, u = n(26, R = n(19, Q = null))), n(24, S = performance.now()), n(25, z = 0), T = !0, be();
  };
  function be() {
    requestAnimationFrame(() => {
      n(25, z = (performance.now() - S) / 1e3), T && be();
    });
  }
  function ke() {
    n(25, z = 0), n(0, u = n(26, R = n(19, Q = null))), T && (T = !1);
  }
  Ia(() => {
    T && ke();
  });
  let Q = null;
  function Ge(H) {
    di[H ? "unshift" : "push"](() => {
      te = H, n(16, te), n(7, v), n(14, W), n(15, ee);
    });
  }
  function Fe(H) {
    di[H ? "unshift" : "push"](() => {
      g = H, n(13, g);
    });
  }
  return e.$$set = (H) => {
    "i18n" in H && n(1, o = H.i18n), "eta" in H && n(0, u = H.eta), "queue_position" in H && n(2, s = H.queue_position), "queue_size" in H && n(3, a = H.queue_size), "status" in H && n(4, f = H.status), "scroll_to_output" in H && n(21, c = H.scroll_to_output), "timer" in H && n(5, h = H.timer), "show_progress" in H && n(6, _ = H.show_progress), "message" in H && n(22, d = H.message), "progress" in H && n(7, v = H.progress), "variant" in H && n(8, A = H.variant), "loading_text" in H && n(9, w = H.loading_text), "absolute" in H && n(10, E = H.absolute), "translucent" in H && n(11, p = H.translucent), "border" in H && n(12, m = H.border), "autoscroll" in H && n(23, k = H.autoscroll), "$$scope" in H && n(28, r = H.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty[0] & /*eta, old_eta, timer_start, eta_from_start*/
    218103809 && (u === null && n(0, u = R), u != null && R !== u && (n(27, q = (performance.now() - S) / 1e3 + u), n(19, Q = q.toFixed(1)), n(26, R = u))), e.$$.dirty[0] & /*eta_from_start, timer_diff*/
    167772160 && n(17, x = q === null || q <= 0 || !z ? null : Math.min(z / q, 1)), e.$$.dirty[0] & /*progress*/
    128 && v != null && n(18, Ee = !1), e.$$.dirty[0] & /*progress, progress_level, progress_bar, last_progress_level*/
    114816 && (v != null ? n(14, W = v.map((H) => {
      if (H.index != null && H.length != null)
        return H.index / H.length;
      if (H.progress != null)
        return H.progress;
    })) : n(14, W = null), W ? (n(15, ee = W[W.length - 1]), te && (ee === 0 ? n(16, te.style.transition = "0", te) : n(16, te.style.transition = "150ms", te))) : n(15, ee = void 0)), e.$$.dirty[0] & /*status*/
    16 && (f === "pending" ? de() : ke()), e.$$.dirty[0] & /*el, scroll_to_output, status, autoscroll*/
    10493968 && g && c && (f === "pending" || f === "complete") && qa(g, k), e.$$.dirty[0] & /*status, message*/
    4194320, e.$$.dirty[0] & /*timer_diff*/
    33554432 && n(20, i = z.toFixed(1));
  }, [
    u,
    o,
    s,
    a,
    f,
    h,
    _,
    v,
    A,
    w,
    E,
    p,
    m,
    g,
    W,
    ee,
    te,
    x,
    Ee,
    Q,
    i,
    c,
    d,
    k,
    S,
    z,
    R,
    q,
    r,
    l,
    Ge,
    Fe
  ];
}
class za extends va {
  constructor(t) {
    super(), Sa(
      this,
      t,
      xa,
      Va,
      Ta,
      {
        i18n: 1,
        eta: 0,
        queue_position: 2,
        queue_size: 3,
        status: 4,
        scroll_to_output: 21,
        timer: 5,
        show_progress: 6,
        message: 22,
        progress: 7,
        variant: 8,
        loading_text: 9,
        absolute: 10,
        translucent: 11,
        border: 12,
        autoscroll: 23
      },
      null,
      [-1, -1]
    );
  }
}
new Intl.Collator(0, { numeric: 1 }).compare;
function Xa(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function Za(e, t, n) {
  return e == null ? n ? `/proxy=${n}file=` : `${t}/file=` : Xa(e) ? e : n ? `/proxy=${n}file=${e}` : `${t}/file=${e}`;
}
const {
  SvelteComponent: Wa,
  append: Ol,
  attr: U,
  bubble: Qa,
  check_outros: Ja,
  create_slot: Ml,
  detach: wt,
  element: zt,
  empty: Ya,
  get_all_dirty_from_scope: Rl,
  get_slot_changes: Dl,
  group_outros: Ka,
  init: $a,
  insert: yt,
  listen: eu,
  safe_not_equal: tu,
  set_style: $,
  space: Ul,
  src_url_equal: Rt,
  toggle_class: $e,
  transition_in: Dt,
  transition_out: Ut,
  update_slot_base: Gl
} = window.__gradio__svelte__internal;
function nu(e) {
  let t, n, i, l, r, o, u = (
    /*icon*/
    e[7] && Ii(e)
  );
  const s = (
    /*#slots*/
    e[15].default
  ), a = Ml(
    s,
    e,
    /*$$scope*/
    e[14],
    null
  );
  return {
    c() {
      t = zt("button"), u && u.c(), n = Ul(), a && a.c(), U(t, "class", i = /*size*/
      e[4] + " " + /*variant*/
      e[3] + " " + /*elem_classes*/
      e[1].join(" ") + " svelte-8huxfn"), U(
        t,
        "id",
        /*elem_id*/
        e[0]
      ), t.disabled = /*disabled*/
      e[8], $e(t, "hidden", !/*visible*/
      e[2]), $(
        t,
        "flex-grow",
        /*scale*/
        e[9]
      ), $(
        t,
        "width",
        /*scale*/
        e[9] === 0 ? "fit-content" : null
      ), $(t, "min-width", typeof /*min_width*/
      e[10] == "number" ? `calc(min(${/*min_width*/
      e[10]}px, 100%))` : null);
    },
    m(f, c) {
      yt(f, t, c), u && u.m(t, null), Ol(t, n), a && a.m(t, null), l = !0, r || (o = eu(
        t,
        "click",
        /*click_handler*/
        e[16]
      ), r = !0);
    },
    p(f, c) {
      /*icon*/
      f[7] ? u ? u.p(f, c) : (u = Ii(f), u.c(), u.m(t, n)) : u && (u.d(1), u = null), a && a.p && (!l || c & /*$$scope*/
      16384) && Gl(
        a,
        s,
        f,
        /*$$scope*/
        f[14],
        l ? Dl(
          s,
          /*$$scope*/
          f[14],
          c,
          null
        ) : Rl(
          /*$$scope*/
          f[14]
        ),
        null
      ), (!l || c & /*size, variant, elem_classes*/
      26 && i !== (i = /*size*/
      f[4] + " " + /*variant*/
      f[3] + " " + /*elem_classes*/
      f[1].join(" ") + " svelte-8huxfn")) && U(t, "class", i), (!l || c & /*elem_id*/
      1) && U(
        t,
        "id",
        /*elem_id*/
        f[0]
      ), (!l || c & /*disabled*/
      256) && (t.disabled = /*disabled*/
      f[8]), (!l || c & /*size, variant, elem_classes, visible*/
      30) && $e(t, "hidden", !/*visible*/
      f[2]), c & /*scale*/
      512 && $(
        t,
        "flex-grow",
        /*scale*/
        f[9]
      ), c & /*scale*/
      512 && $(
        t,
        "width",
        /*scale*/
        f[9] === 0 ? "fit-content" : null
      ), c & /*min_width*/
      1024 && $(t, "min-width", typeof /*min_width*/
      f[10] == "number" ? `calc(min(${/*min_width*/
      f[10]}px, 100%))` : null);
    },
    i(f) {
      l || (Dt(a, f), l = !0);
    },
    o(f) {
      Ut(a, f), l = !1;
    },
    d(f) {
      f && wt(t), u && u.d(), a && a.d(f), r = !1, o();
    }
  };
}
function iu(e) {
  let t, n, i, l, r = (
    /*icon*/
    e[7] && Pi(e)
  );
  const o = (
    /*#slots*/
    e[15].default
  ), u = Ml(
    o,
    e,
    /*$$scope*/
    e[14],
    null
  );
  return {
    c() {
      t = zt("a"), r && r.c(), n = Ul(), u && u.c(), U(
        t,
        "href",
        /*link*/
        e[6]
      ), U(t, "rel", "noopener noreferrer"), U(
        t,
        "aria-disabled",
        /*disabled*/
        e[8]
      ), U(t, "class", i = /*size*/
      e[4] + " " + /*variant*/
      e[3] + " " + /*elem_classes*/
      e[1].join(" ") + " svelte-8huxfn"), U(
        t,
        "id",
        /*elem_id*/
        e[0]
      ), $e(t, "hidden", !/*visible*/
      e[2]), $e(
        t,
        "disabled",
        /*disabled*/
        e[8]
      ), $(
        t,
        "flex-grow",
        /*scale*/
        e[9]
      ), $(
        t,
        "pointer-events",
        /*disabled*/
        e[8] ? "none" : null
      ), $(
        t,
        "width",
        /*scale*/
        e[9] === 0 ? "fit-content" : null
      ), $(t, "min-width", typeof /*min_width*/
      e[10] == "number" ? `calc(min(${/*min_width*/
      e[10]}px, 100%))` : null);
    },
    m(s, a) {
      yt(s, t, a), r && r.m(t, null), Ol(t, n), u && u.m(t, null), l = !0;
    },
    p(s, a) {
      /*icon*/
      s[7] ? r ? r.p(s, a) : (r = Pi(s), r.c(), r.m(t, n)) : r && (r.d(1), r = null), u && u.p && (!l || a & /*$$scope*/
      16384) && Gl(
        u,
        o,
        s,
        /*$$scope*/
        s[14],
        l ? Dl(
          o,
          /*$$scope*/
          s[14],
          a,
          null
        ) : Rl(
          /*$$scope*/
          s[14]
        ),
        null
      ), (!l || a & /*link*/
      64) && U(
        t,
        "href",
        /*link*/
        s[6]
      ), (!l || a & /*disabled*/
      256) && U(
        t,
        "aria-disabled",
        /*disabled*/
        s[8]
      ), (!l || a & /*size, variant, elem_classes*/
      26 && i !== (i = /*size*/
      s[4] + " " + /*variant*/
      s[3] + " " + /*elem_classes*/
      s[1].join(" ") + " svelte-8huxfn")) && U(t, "class", i), (!l || a & /*elem_id*/
      1) && U(
        t,
        "id",
        /*elem_id*/
        s[0]
      ), (!l || a & /*size, variant, elem_classes, visible*/
      30) && $e(t, "hidden", !/*visible*/
      s[2]), (!l || a & /*size, variant, elem_classes, disabled*/
      282) && $e(
        t,
        "disabled",
        /*disabled*/
        s[8]
      ), a & /*scale*/
      512 && $(
        t,
        "flex-grow",
        /*scale*/
        s[9]
      ), a & /*disabled*/
      256 && $(
        t,
        "pointer-events",
        /*disabled*/
        s[8] ? "none" : null
      ), a & /*scale*/
      512 && $(
        t,
        "width",
        /*scale*/
        s[9] === 0 ? "fit-content" : null
      ), a & /*min_width*/
      1024 && $(t, "min-width", typeof /*min_width*/
      s[10] == "number" ? `calc(min(${/*min_width*/
      s[10]}px, 100%))` : null);
    },
    i(s) {
      l || (Dt(u, s), l = !0);
    },
    o(s) {
      Ut(u, s), l = !1;
    },
    d(s) {
      s && wt(t), r && r.d(), u && u.d(s);
    }
  };
}
function Ii(e) {
  let t, n, i;
  return {
    c() {
      t = zt("img"), U(t, "class", "button-icon svelte-8huxfn"), Rt(t.src, n = /*icon_path*/
      e[11]) || U(t, "src", n), U(t, "alt", i = `${/*value*/
      e[5]} icon`);
    },
    m(l, r) {
      yt(l, t, r);
    },
    p(l, r) {
      r & /*icon_path*/
      2048 && !Rt(t.src, n = /*icon_path*/
      l[11]) && U(t, "src", n), r & /*value*/
      32 && i !== (i = `${/*value*/
      l[5]} icon`) && U(t, "alt", i);
    },
    d(l) {
      l && wt(t);
    }
  };
}
function Pi(e) {
  let t, n, i;
  return {
    c() {
      t = zt("img"), U(t, "class", "button-icon svelte-8huxfn"), Rt(t.src, n = /*icon_path*/
      e[11]) || U(t, "src", n), U(t, "alt", i = `${/*value*/
      e[5]} icon`);
    },
    m(l, r) {
      yt(l, t, r);
    },
    p(l, r) {
      r & /*icon_path*/
      2048 && !Rt(t.src, n = /*icon_path*/
      l[11]) && U(t, "src", n), r & /*value*/
      32 && i !== (i = `${/*value*/
      l[5]} icon`) && U(t, "alt", i);
    },
    d(l) {
      l && wt(t);
    }
  };
}
function lu(e) {
  let t, n, i, l;
  const r = [iu, nu], o = [];
  function u(s, a) {
    return (
      /*link*/
      s[6] && /*link*/
      s[6].length > 0 ? 0 : 1
    );
  }
  return t = u(e), n = o[t] = r[t](e), {
    c() {
      n.c(), i = Ya();
    },
    m(s, a) {
      o[t].m(s, a), yt(s, i, a), l = !0;
    },
    p(s, [a]) {
      let f = t;
      t = u(s), t === f ? o[t].p(s, a) : (Ka(), Ut(o[f], 1, 1, () => {
        o[f] = null;
      }), Ja(), n = o[t], n ? n.p(s, a) : (n = o[t] = r[t](s), n.c()), Dt(n, 1), n.m(i.parentNode, i));
    },
    i(s) {
      l || (Dt(n), l = !0);
    },
    o(s) {
      Ut(n), l = !1;
    },
    d(s) {
      s && wt(i), o[t].d(s);
    }
  };
}
function ru(e, t, n) {
  let i, { $$slots: l = {}, $$scope: r } = t, { elem_id: o = "" } = t, { elem_classes: u = [] } = t, { visible: s = !0 } = t, { variant: a = "secondary" } = t, { size: f = "lg" } = t, { value: c = null } = t, { link: h = null } = t, { icon: _ = null } = t, { disabled: d = !1 } = t, { scale: v = null } = t, { min_width: A = void 0 } = t, { root: w = "" } = t, { proxy_url: E = null } = t;
  function p(m) {
    Qa.call(this, e, m);
  }
  return e.$$set = (m) => {
    "elem_id" in m && n(0, o = m.elem_id), "elem_classes" in m && n(1, u = m.elem_classes), "visible" in m && n(2, s = m.visible), "variant" in m && n(3, a = m.variant), "size" in m && n(4, f = m.size), "value" in m && n(5, c = m.value), "link" in m && n(6, h = m.link), "icon" in m && n(7, _ = m.icon), "disabled" in m && n(8, d = m.disabled), "scale" in m && n(9, v = m.scale), "min_width" in m && n(10, A = m.min_width), "root" in m && n(12, w = m.root), "proxy_url" in m && n(13, E = m.proxy_url), "$$scope" in m && n(14, r = m.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty & /*icon, root, proxy_url*/
    12416 && n(11, i = Za(_, w, E));
  }, [
    o,
    u,
    s,
    a,
    f,
    c,
    h,
    _,
    d,
    v,
    A,
    i,
    w,
    E,
    r,
    l,
    p
  ];
}
class ou extends Wa {
  constructor(t) {
    super(), $a(this, t, ru, lu, tu, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      size: 4,
      value: 5,
      link: 6,
      icon: 7,
      disabled: 8,
      scale: 9,
      min_width: 10,
      root: 12,
      proxy_url: 13
    });
  }
}
new Intl.Collator(0, { numeric: 1 }).compare;
function Fl(e, t, n) {
  if (e == null)
    return null;
  if (Array.isArray(e)) {
    const i = [];
    for (const l of e)
      l == null ? i.push(null) : i.push(Fl(l, t, n));
    return i;
  }
  return e.is_stream ? n == null ? new mn({
    ...e,
    url: t + "/stream/" + e.path
  }) : new mn({
    ...e,
    url: "/proxy=" + n + "stream/" + e.path
  }) : new mn({
    ...e,
    url: au(e.path, t, n)
  });
}
function su(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function au(e, t, n) {
  return e == null ? n ? `/proxy=${n}file=` : `${t}/file=` : su(e) ? e : n ? `/proxy=${n}file=${e}` : `${t}/file=${e}`;
}
class mn {
  constructor({
    path: t,
    url: n,
    orig_name: i,
    size: l,
    blob: r,
    is_stream: o,
    mime_type: u,
    alt_text: s
  }) {
    this.path = t, this.url = n, this.orig_name = i, this.size = l, this.blob = n ? void 0 : r, this.is_stream = o, this.mime_type = u, this.alt_text = s;
  }
}
function uu(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var fu = function(t) {
  return cu(t) && !hu(t);
};
function cu(e) {
  return !!e && typeof e == "object";
}
function hu(e) {
  var t = Object.prototype.toString.call(e);
  return t === "[object RegExp]" || t === "[object Date]" || du(e);
}
var _u = typeof Symbol == "function" && Symbol.for, mu = _u ? Symbol.for("react.element") : 60103;
function du(e) {
  return e.$$typeof === mu;
}
function bu(e) {
  return Array.isArray(e) ? [] : {};
}
function gt(e, t) {
  return t.clone !== !1 && t.isMergeableObject(e) ? lt(bu(e), e, t) : e;
}
function gu(e, t, n) {
  return e.concat(t).map(function(i) {
    return gt(i, n);
  });
}
function pu(e, t) {
  if (!t.customMerge)
    return lt;
  var n = t.customMerge(e);
  return typeof n == "function" ? n : lt;
}
function vu(e) {
  return Object.getOwnPropertySymbols ? Object.getOwnPropertySymbols(e).filter(function(t) {
    return Object.propertyIsEnumerable.call(e, t);
  }) : [];
}
function Li(e) {
  return Object.keys(e).concat(vu(e));
}
function jl(e, t) {
  try {
    return t in e;
  } catch {
    return !1;
  }
}
function wu(e, t) {
  return jl(e, t) && !(Object.hasOwnProperty.call(e, t) && Object.propertyIsEnumerable.call(e, t));
}
function yu(e, t, n) {
  var i = {};
  return n.isMergeableObject(e) && Li(e).forEach(function(l) {
    i[l] = gt(e[l], n);
  }), Li(t).forEach(function(l) {
    wu(e, l) || (jl(e, l) && n.isMergeableObject(t[l]) ? i[l] = pu(l, n)(e[l], t[l], n) : i[l] = gt(t[l], n));
  }), i;
}
function lt(e, t, n) {
  n = n || {}, n.arrayMerge = n.arrayMerge || gu, n.isMergeableObject = n.isMergeableObject || fu, n.cloneUnlessOtherwiseSpecified = gt;
  var i = Array.isArray(t), l = Array.isArray(e), r = i === l;
  return r ? i ? n.arrayMerge(e, t, n) : yu(e, t, n) : gt(t, n);
}
lt.all = function(t, n) {
  if (!Array.isArray(t))
    throw new Error("first argument should be an array");
  return t.reduce(function(i, l) {
    return lt(i, l, n);
  }, {});
};
var Eu = lt, ku = Eu;
const Hu = /* @__PURE__ */ uu(ku);
var Bn = function(e, t) {
  return Bn = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(n, i) {
    n.__proto__ = i;
  } || function(n, i) {
    for (var l in i)
      Object.prototype.hasOwnProperty.call(i, l) && (n[l] = i[l]);
  }, Bn(e, t);
};
function Xt(e, t) {
  if (typeof t != "function" && t !== null)
    throw new TypeError("Class extends value " + String(t) + " is not a constructor or null");
  Bn(e, t);
  function n() {
    this.constructor = e;
  }
  e.prototype = t === null ? Object.create(t) : (n.prototype = t.prototype, new n());
}
var O = function() {
  return O = Object.assign || function(t) {
    for (var n, i = 1, l = arguments.length; i < l; i++) {
      n = arguments[i];
      for (var r in n)
        Object.prototype.hasOwnProperty.call(n, r) && (t[r] = n[r]);
    }
    return t;
  }, O.apply(this, arguments);
};
function Su(e, t) {
  var n = {};
  for (var i in e)
    Object.prototype.hasOwnProperty.call(e, i) && t.indexOf(i) < 0 && (n[i] = e[i]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function")
    for (var l = 0, i = Object.getOwnPropertySymbols(e); l < i.length; l++)
      t.indexOf(i[l]) < 0 && Object.prototype.propertyIsEnumerable.call(e, i[l]) && (n[i[l]] = e[i[l]]);
  return n;
}
function dn(e, t, n) {
  if (n || arguments.length === 2)
    for (var i = 0, l = t.length, r; i < l; i++)
      (r || !(i in t)) && (r || (r = Array.prototype.slice.call(t, 0, i)), r[i] = t[i]);
  return e.concat(r || Array.prototype.slice.call(t));
}
var P;
(function(e) {
  e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
})(P || (P = {}));
var D;
(function(e) {
  e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
})(D || (D = {}));
var rt;
(function(e) {
  e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
})(rt || (rt = {}));
function Ni(e) {
  return e.type === D.literal;
}
function Au(e) {
  return e.type === D.argument;
}
function Vl(e) {
  return e.type === D.number;
}
function ql(e) {
  return e.type === D.date;
}
function xl(e) {
  return e.type === D.time;
}
function zl(e) {
  return e.type === D.select;
}
function Xl(e) {
  return e.type === D.plural;
}
function Tu(e) {
  return e.type === D.pound;
}
function Zl(e) {
  return e.type === D.tag;
}
function Wl(e) {
  return !!(e && typeof e == "object" && e.type === rt.number);
}
function Cn(e) {
  return !!(e && typeof e == "object" && e.type === rt.dateTime);
}
var Ql = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/, Bu = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
function Cu(e) {
  var t = {};
  return e.replace(Bu, function(n) {
    var i = n.length;
    switch (n[0]) {
      case "G":
        t.era = i === 4 ? "long" : i === 5 ? "narrow" : "short";
        break;
      case "y":
        t.year = i === 2 ? "2-digit" : "numeric";
        break;
      case "Y":
      case "u":
      case "U":
      case "r":
        throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");
      case "q":
      case "Q":
        throw new RangeError("`q/Q` (quarter) patterns are not supported");
      case "M":
      case "L":
        t.month = ["numeric", "2-digit", "short", "long", "narrow"][i - 1];
        break;
      case "w":
      case "W":
        throw new RangeError("`w/W` (week) patterns are not supported");
      case "d":
        t.day = ["numeric", "2-digit"][i - 1];
        break;
      case "D":
      case "F":
      case "g":
        throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");
      case "E":
        t.weekday = i === 4 ? "long" : i === 5 ? "narrow" : "short";
        break;
      case "e":
        if (i < 4)
          throw new RangeError("`e..eee` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][i - 4];
        break;
      case "c":
        if (i < 4)
          throw new RangeError("`c..ccc` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][i - 4];
        break;
      case "a":
        t.hour12 = !0;
        break;
      case "b":
      case "B":
        throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");
      case "h":
        t.hourCycle = "h12", t.hour = ["numeric", "2-digit"][i - 1];
        break;
      case "H":
        t.hourCycle = "h23", t.hour = ["numeric", "2-digit"][i - 1];
        break;
      case "K":
        t.hourCycle = "h11", t.hour = ["numeric", "2-digit"][i - 1];
        break;
      case "k":
        t.hourCycle = "h24", t.hour = ["numeric", "2-digit"][i - 1];
        break;
      case "j":
      case "J":
      case "C":
        throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");
      case "m":
        t.minute = ["numeric", "2-digit"][i - 1];
        break;
      case "s":
        t.second = ["numeric", "2-digit"][i - 1];
        break;
      case "S":
      case "A":
        throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");
      case "z":
        t.timeZoneName = i < 4 ? "short" : "long";
        break;
      case "Z":
      case "O":
      case "v":
      case "V":
      case "X":
      case "x":
        throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead");
    }
    return "";
  }), t;
}
var Iu = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
function Pu(e) {
  if (e.length === 0)
    throw new Error("Number skeleton cannot be empty");
  for (var t = e.split(Iu).filter(function(h) {
    return h.length > 0;
  }), n = [], i = 0, l = t; i < l.length; i++) {
    var r = l[i], o = r.split("/");
    if (o.length === 0)
      throw new Error("Invalid number skeleton");
    for (var u = o[0], s = o.slice(1), a = 0, f = s; a < f.length; a++) {
      var c = f[a];
      if (c.length === 0)
        throw new Error("Invalid number skeleton");
    }
    n.push({ stem: u, options: s });
  }
  return n;
}
function Lu(e) {
  return e.replace(/^(.*?)-/, "");
}
var Oi = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g, Jl = /^(@+)?(\+|#+)?[rs]?$/g, Nu = /(\*)(0+)|(#+)(0+)|(0+)/g, Yl = /^(0+)$/;
function Mi(e) {
  var t = {};
  return e[e.length - 1] === "r" ? t.roundingPriority = "morePrecision" : e[e.length - 1] === "s" && (t.roundingPriority = "lessPrecision"), e.replace(Jl, function(n, i, l) {
    return typeof l != "string" ? (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length) : l === "+" ? t.minimumSignificantDigits = i.length : i[0] === "#" ? t.maximumSignificantDigits = i.length : (t.minimumSignificantDigits = i.length, t.maximumSignificantDigits = i.length + (typeof l == "string" ? l.length : 0)), "";
  }), t;
}
function Kl(e) {
  switch (e) {
    case "sign-auto":
      return {
        signDisplay: "auto"
      };
    case "sign-accounting":
    case "()":
      return {
        currencySign: "accounting"
      };
    case "sign-always":
    case "+!":
      return {
        signDisplay: "always"
      };
    case "sign-accounting-always":
    case "()!":
      return {
        signDisplay: "always",
        currencySign: "accounting"
      };
    case "sign-except-zero":
    case "+?":
      return {
        signDisplay: "exceptZero"
      };
    case "sign-accounting-except-zero":
    case "()?":
      return {
        signDisplay: "exceptZero",
        currencySign: "accounting"
      };
    case "sign-never":
    case "+_":
      return {
        signDisplay: "never"
      };
  }
}
function Ou(e) {
  var t;
  if (e[0] === "E" && e[1] === "E" ? (t = {
    notation: "engineering"
  }, e = e.slice(2)) : e[0] === "E" && (t = {
    notation: "scientific"
  }, e = e.slice(1)), t) {
    var n = e.slice(0, 2);
    if (n === "+!" ? (t.signDisplay = "always", e = e.slice(2)) : n === "+?" && (t.signDisplay = "exceptZero", e = e.slice(2)), !Yl.test(e))
      throw new Error("Malformed concise eng/scientific notation");
    t.minimumIntegerDigits = e.length;
  }
  return t;
}
function Ri(e) {
  var t = {}, n = Kl(e);
  return n || t;
}
function Mu(e) {
  for (var t = {}, n = 0, i = e; n < i.length; n++) {
    var l = i[n];
    switch (l.stem) {
      case "percent":
      case "%":
        t.style = "percent";
        continue;
      case "%x100":
        t.style = "percent", t.scale = 100;
        continue;
      case "currency":
        t.style = "currency", t.currency = l.options[0];
        continue;
      case "group-off":
      case ",_":
        t.useGrouping = !1;
        continue;
      case "precision-integer":
      case ".":
        t.maximumFractionDigits = 0;
        continue;
      case "measure-unit":
      case "unit":
        t.style = "unit", t.unit = Lu(l.options[0]);
        continue;
      case "compact-short":
      case "K":
        t.notation = "compact", t.compactDisplay = "short";
        continue;
      case "compact-long":
      case "KK":
        t.notation = "compact", t.compactDisplay = "long";
        continue;
      case "scientific":
        t = O(O(O({}, t), { notation: "scientific" }), l.options.reduce(function(s, a) {
          return O(O({}, s), Ri(a));
        }, {}));
        continue;
      case "engineering":
        t = O(O(O({}, t), { notation: "engineering" }), l.options.reduce(function(s, a) {
          return O(O({}, s), Ri(a));
        }, {}));
        continue;
      case "notation-simple":
        t.notation = "standard";
        continue;
      case "unit-width-narrow":
        t.currencyDisplay = "narrowSymbol", t.unitDisplay = "narrow";
        continue;
      case "unit-width-short":
        t.currencyDisplay = "code", t.unitDisplay = "short";
        continue;
      case "unit-width-full-name":
        t.currencyDisplay = "name", t.unitDisplay = "long";
        continue;
      case "unit-width-iso-code":
        t.currencyDisplay = "symbol";
        continue;
      case "scale":
        t.scale = parseFloat(l.options[0]);
        continue;
      case "integer-width":
        if (l.options.length > 1)
          throw new RangeError("integer-width stems only accept a single optional option");
        l.options[0].replace(Nu, function(s, a, f, c, h, _) {
          if (a)
            t.minimumIntegerDigits = f.length;
          else {
            if (c && h)
              throw new Error("We currently do not support maximum integer digits");
            if (_)
              throw new Error("We currently do not support exact integer digits");
          }
          return "";
        });
        continue;
    }
    if (Yl.test(l.stem)) {
      t.minimumIntegerDigits = l.stem.length;
      continue;
    }
    if (Oi.test(l.stem)) {
      if (l.options.length > 1)
        throw new RangeError("Fraction-precision stems only accept a single optional option");
      l.stem.replace(Oi, function(s, a, f, c, h, _) {
        return f === "*" ? t.minimumFractionDigits = a.length : c && c[0] === "#" ? t.maximumFractionDigits = c.length : h && _ ? (t.minimumFractionDigits = h.length, t.maximumFractionDigits = h.length + _.length) : (t.minimumFractionDigits = a.length, t.maximumFractionDigits = a.length), "";
      });
      var r = l.options[0];
      r === "w" ? t = O(O({}, t), { trailingZeroDisplay: "stripIfInteger" }) : r && (t = O(O({}, t), Mi(r)));
      continue;
    }
    if (Jl.test(l.stem)) {
      t = O(O({}, t), Mi(l.stem));
      continue;
    }
    var o = Kl(l.stem);
    o && (t = O(O({}, t), o));
    var u = Ou(l.stem);
    u && (t = O(O({}, t), u));
  }
  return t;
}
var It = {
  "001": [
    "H",
    "h"
  ],
  AC: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  AD: [
    "H",
    "hB"
  ],
  AE: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  AF: [
    "H",
    "hb",
    "hB",
    "h"
  ],
  AG: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  AI: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  AL: [
    "h",
    "H",
    "hB"
  ],
  AM: [
    "H",
    "hB"
  ],
  AO: [
    "H",
    "hB"
  ],
  AR: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  AS: [
    "h",
    "H"
  ],
  AT: [
    "H",
    "hB"
  ],
  AU: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  AW: [
    "H",
    "hB"
  ],
  AX: [
    "H"
  ],
  AZ: [
    "H",
    "hB",
    "h"
  ],
  BA: [
    "H",
    "hB",
    "h"
  ],
  BB: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  BD: [
    "h",
    "hB",
    "H"
  ],
  BE: [
    "H",
    "hB"
  ],
  BF: [
    "H",
    "hB"
  ],
  BG: [
    "H",
    "hB",
    "h"
  ],
  BH: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  BI: [
    "H",
    "h"
  ],
  BJ: [
    "H",
    "hB"
  ],
  BL: [
    "H",
    "hB"
  ],
  BM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  BN: [
    "hb",
    "hB",
    "h",
    "H"
  ],
  BO: [
    "H",
    "hB",
    "h",
    "hb"
  ],
  BQ: [
    "H"
  ],
  BR: [
    "H",
    "hB"
  ],
  BS: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  BT: [
    "h",
    "H"
  ],
  BW: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  BY: [
    "H",
    "h"
  ],
  BZ: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  CA: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  CC: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  CD: [
    "hB",
    "H"
  ],
  CF: [
    "H",
    "h",
    "hB"
  ],
  CG: [
    "H",
    "hB"
  ],
  CH: [
    "H",
    "hB",
    "h"
  ],
  CI: [
    "H",
    "hB"
  ],
  CK: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  CL: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  CM: [
    "H",
    "h",
    "hB"
  ],
  CN: [
    "H",
    "hB",
    "hb",
    "h"
  ],
  CO: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  CP: [
    "H"
  ],
  CR: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  CU: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  CV: [
    "H",
    "hB"
  ],
  CW: [
    "H",
    "hB"
  ],
  CX: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  CY: [
    "h",
    "H",
    "hb",
    "hB"
  ],
  CZ: [
    "H"
  ],
  DE: [
    "H",
    "hB"
  ],
  DG: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  DJ: [
    "h",
    "H"
  ],
  DK: [
    "H"
  ],
  DM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  DO: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  DZ: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  EA: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  EC: [
    "H",
    "hB",
    "h",
    "hb"
  ],
  EE: [
    "H",
    "hB"
  ],
  EG: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  EH: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  ER: [
    "h",
    "H"
  ],
  ES: [
    "H",
    "hB",
    "h",
    "hb"
  ],
  ET: [
    "hB",
    "hb",
    "h",
    "H"
  ],
  FI: [
    "H"
  ],
  FJ: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  FK: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  FM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  FO: [
    "H",
    "h"
  ],
  FR: [
    "H",
    "hB"
  ],
  GA: [
    "H",
    "hB"
  ],
  GB: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  GD: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  GE: [
    "H",
    "hB",
    "h"
  ],
  GF: [
    "H",
    "hB"
  ],
  GG: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  GH: [
    "h",
    "H"
  ],
  GI: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  GL: [
    "H",
    "h"
  ],
  GM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  GN: [
    "H",
    "hB"
  ],
  GP: [
    "H",
    "hB"
  ],
  GQ: [
    "H",
    "hB",
    "h",
    "hb"
  ],
  GR: [
    "h",
    "H",
    "hb",
    "hB"
  ],
  GT: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  GU: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  GW: [
    "H",
    "hB"
  ],
  GY: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  HK: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  HN: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  HR: [
    "H",
    "hB"
  ],
  HU: [
    "H",
    "h"
  ],
  IC: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  ID: [
    "H"
  ],
  IE: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  IL: [
    "H",
    "hB"
  ],
  IM: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  IN: [
    "h",
    "H"
  ],
  IO: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  IQ: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  IR: [
    "hB",
    "H"
  ],
  IS: [
    "H"
  ],
  IT: [
    "H",
    "hB"
  ],
  JE: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  JM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  JO: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  JP: [
    "H",
    "K",
    "h"
  ],
  KE: [
    "hB",
    "hb",
    "H",
    "h"
  ],
  KG: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  KH: [
    "hB",
    "h",
    "H",
    "hb"
  ],
  KI: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  KM: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  KN: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  KP: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  KR: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  KW: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  KY: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  KZ: [
    "H",
    "hB"
  ],
  LA: [
    "H",
    "hb",
    "hB",
    "h"
  ],
  LB: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  LC: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  LI: [
    "H",
    "hB",
    "h"
  ],
  LK: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  LR: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  LS: [
    "h",
    "H"
  ],
  LT: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  LU: [
    "H",
    "h",
    "hB"
  ],
  LV: [
    "H",
    "hB",
    "hb",
    "h"
  ],
  LY: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  MA: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  MC: [
    "H",
    "hB"
  ],
  MD: [
    "H",
    "hB"
  ],
  ME: [
    "H",
    "hB",
    "h"
  ],
  MF: [
    "H",
    "hB"
  ],
  MG: [
    "H",
    "h"
  ],
  MH: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  MK: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  ML: [
    "H"
  ],
  MM: [
    "hB",
    "hb",
    "H",
    "h"
  ],
  MN: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  MO: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  MP: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  MQ: [
    "H",
    "hB"
  ],
  MR: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  MS: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  MT: [
    "H",
    "h"
  ],
  MU: [
    "H",
    "h"
  ],
  MV: [
    "H",
    "h"
  ],
  MW: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  MX: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  MY: [
    "hb",
    "hB",
    "h",
    "H"
  ],
  MZ: [
    "H",
    "hB"
  ],
  NA: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  NC: [
    "H",
    "hB"
  ],
  NE: [
    "H"
  ],
  NF: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  NG: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  NI: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  NL: [
    "H",
    "hB"
  ],
  NO: [
    "H",
    "h"
  ],
  NP: [
    "H",
    "h",
    "hB"
  ],
  NR: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  NU: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  NZ: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  OM: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  PA: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  PE: [
    "H",
    "hB",
    "h",
    "hb"
  ],
  PF: [
    "H",
    "h",
    "hB"
  ],
  PG: [
    "h",
    "H"
  ],
  PH: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  PK: [
    "h",
    "hB",
    "H"
  ],
  PL: [
    "H",
    "h"
  ],
  PM: [
    "H",
    "hB"
  ],
  PN: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  PR: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  PS: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  PT: [
    "H",
    "hB"
  ],
  PW: [
    "h",
    "H"
  ],
  PY: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  QA: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  RE: [
    "H",
    "hB"
  ],
  RO: [
    "H",
    "hB"
  ],
  RS: [
    "H",
    "hB",
    "h"
  ],
  RU: [
    "H"
  ],
  RW: [
    "H",
    "h"
  ],
  SA: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  SB: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  SC: [
    "H",
    "h",
    "hB"
  ],
  SD: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  SE: [
    "H"
  ],
  SG: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  SH: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  SI: [
    "H",
    "hB"
  ],
  SJ: [
    "H"
  ],
  SK: [
    "H"
  ],
  SL: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  SM: [
    "H",
    "h",
    "hB"
  ],
  SN: [
    "H",
    "h",
    "hB"
  ],
  SO: [
    "h",
    "H"
  ],
  SR: [
    "H",
    "hB"
  ],
  SS: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  ST: [
    "H",
    "hB"
  ],
  SV: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  SX: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  SY: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  SZ: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  TA: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  TC: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  TD: [
    "h",
    "H",
    "hB"
  ],
  TF: [
    "H",
    "h",
    "hB"
  ],
  TG: [
    "H",
    "hB"
  ],
  TH: [
    "H",
    "h"
  ],
  TJ: [
    "H",
    "h"
  ],
  TL: [
    "H",
    "hB",
    "hb",
    "h"
  ],
  TM: [
    "H",
    "h"
  ],
  TN: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  TO: [
    "h",
    "H"
  ],
  TR: [
    "H",
    "hB"
  ],
  TT: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  TW: [
    "hB",
    "hb",
    "h",
    "H"
  ],
  TZ: [
    "hB",
    "hb",
    "H",
    "h"
  ],
  UA: [
    "H",
    "hB",
    "h"
  ],
  UG: [
    "hB",
    "hb",
    "H",
    "h"
  ],
  UM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  US: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  UY: [
    "H",
    "h",
    "hB",
    "hb"
  ],
  UZ: [
    "H",
    "hB",
    "h"
  ],
  VA: [
    "H",
    "h",
    "hB"
  ],
  VC: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  VE: [
    "h",
    "H",
    "hB",
    "hb"
  ],
  VG: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  VI: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  VN: [
    "H",
    "h"
  ],
  VU: [
    "h",
    "H"
  ],
  WF: [
    "H",
    "hB"
  ],
  WS: [
    "h",
    "H"
  ],
  XK: [
    "H",
    "hB",
    "h"
  ],
  YE: [
    "h",
    "hB",
    "hb",
    "H"
  ],
  YT: [
    "H",
    "hB"
  ],
  ZA: [
    "H",
    "h",
    "hb",
    "hB"
  ],
  ZM: [
    "h",
    "hb",
    "H",
    "hB"
  ],
  ZW: [
    "H",
    "h"
  ],
  "af-ZA": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "ar-001": [
    "h",
    "hB",
    "hb",
    "H"
  ],
  "ca-ES": [
    "H",
    "h",
    "hB"
  ],
  "en-001": [
    "h",
    "hb",
    "H",
    "hB"
  ],
  "es-BO": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "es-BR": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "es-EC": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "es-ES": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "es-GQ": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "es-PE": [
    "H",
    "h",
    "hB",
    "hb"
  ],
  "fr-CA": [
    "H",
    "h",
    "hB"
  ],
  "gl-ES": [
    "H",
    "h",
    "hB"
  ],
  "gu-IN": [
    "hB",
    "hb",
    "h",
    "H"
  ],
  "hi-IN": [
    "hB",
    "h",
    "H"
  ],
  "it-CH": [
    "H",
    "h",
    "hB"
  ],
  "it-IT": [
    "H",
    "h",
    "hB"
  ],
  "kn-IN": [
    "hB",
    "h",
    "H"
  ],
  "ml-IN": [
    "hB",
    "h",
    "H"
  ],
  "mr-IN": [
    "hB",
    "hb",
    "h",
    "H"
  ],
  "pa-IN": [
    "hB",
    "hb",
    "h",
    "H"
  ],
  "ta-IN": [
    "hB",
    "h",
    "hb",
    "H"
  ],
  "te-IN": [
    "hB",
    "h",
    "H"
  ],
  "zu-ZA": [
    "H",
    "hB",
    "hb",
    "h"
  ]
};
function Ru(e, t) {
  for (var n = "", i = 0; i < e.length; i++) {
    var l = e.charAt(i);
    if (l === "j") {
      for (var r = 0; i + 1 < e.length && e.charAt(i + 1) === l; )
        r++, i++;
      var o = 1 + (r & 1), u = r < 2 ? 1 : 3 + (r >> 1), s = "a", a = Du(t);
      for ((a == "H" || a == "k") && (u = 0); u-- > 0; )
        n += s;
      for (; o-- > 0; )
        n = a + n;
    } else
      l === "J" ? n += "H" : n += l;
  }
  return n;
}
function Du(e) {
  var t = e.hourCycle;
  if (t === void 0 && // @ts-ignore hourCycle(s) is not identified yet
  e.hourCycles && // @ts-ignore
  e.hourCycles.length && (t = e.hourCycles[0]), t)
    switch (t) {
      case "h24":
        return "k";
      case "h23":
        return "H";
      case "h12":
        return "h";
      case "h11":
        return "K";
      default:
        throw new Error("Invalid hourCycle");
    }
  var n = e.language, i;
  n !== "root" && (i = e.maximize().region);
  var l = It[i || ""] || It[n || ""] || It["".concat(n, "-001")] || It["001"];
  return l[0];
}
var bn, Uu = new RegExp("^".concat(Ql.source, "*")), Gu = new RegExp("".concat(Ql.source, "*$"));
function L(e, t) {
  return { start: e, end: t };
}
var Fu = !!String.prototype.startsWith && "_a".startsWith("a", 1), ju = !!String.fromCodePoint, Vu = !!Object.fromEntries, qu = !!String.prototype.codePointAt, xu = !!String.prototype.trimStart, zu = !!String.prototype.trimEnd, Xu = !!Number.isSafeInteger, Zu = Xu ? Number.isSafeInteger : function(e) {
  return typeof e == "number" && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
}, In = !0;
try {
  var Wu = er("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  In = ((bn = Wu.exec("a")) === null || bn === void 0 ? void 0 : bn[0]) === "a";
} catch {
  In = !1;
}
var Di = Fu ? (
  // Native
  function(t, n, i) {
    return t.startsWith(n, i);
  }
) : (
  // For IE11
  function(t, n, i) {
    return t.slice(i, i + n.length) === n;
  }
), Pn = ju ? String.fromCodePoint : (
  // IE11
  function() {
    for (var t = [], n = 0; n < arguments.length; n++)
      t[n] = arguments[n];
    for (var i = "", l = t.length, r = 0, o; l > r; ) {
      if (o = t[r++], o > 1114111)
        throw RangeError(o + " is not a valid code point");
      i += o < 65536 ? String.fromCharCode(o) : String.fromCharCode(((o -= 65536) >> 10) + 55296, o % 1024 + 56320);
    }
    return i;
  }
), Ui = (
  // native
  Vu ? Object.fromEntries : (
    // Ponyfill
    function(t) {
      for (var n = {}, i = 0, l = t; i < l.length; i++) {
        var r = l[i], o = r[0], u = r[1];
        n[o] = u;
      }
      return n;
    }
  )
), $l = qu ? (
  // Native
  function(t, n) {
    return t.codePointAt(n);
  }
) : (
  // IE 11
  function(t, n) {
    var i = t.length;
    if (!(n < 0 || n >= i)) {
      var l = t.charCodeAt(n), r;
      return l < 55296 || l > 56319 || n + 1 === i || (r = t.charCodeAt(n + 1)) < 56320 || r > 57343 ? l : (l - 55296 << 10) + (r - 56320) + 65536;
    }
  }
), Qu = xu ? (
  // Native
  function(t) {
    return t.trimStart();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace(Uu, "");
  }
), Ju = zu ? (
  // Native
  function(t) {
    return t.trimEnd();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace(Gu, "");
  }
);
function er(e, t) {
  return new RegExp(e, t);
}
var Ln;
if (In) {
  var Gi = er("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  Ln = function(t, n) {
    var i;
    Gi.lastIndex = n;
    var l = Gi.exec(t);
    return (i = l[1]) !== null && i !== void 0 ? i : "";
  };
} else
  Ln = function(t, n) {
    for (var i = []; ; ) {
      var l = $l(t, n);
      if (l === void 0 || tr(l) || ef(l))
        break;
      i.push(l), n += l >= 65536 ? 2 : 1;
    }
    return Pn.apply(void 0, i);
  };
var Yu = (
  /** @class */
  function() {
    function e(t, n) {
      n === void 0 && (n = {}), this.message = t, this.position = { offset: 0, line: 1, column: 1 }, this.ignoreTag = !!n.ignoreTag, this.locale = n.locale, this.requiresOtherClause = !!n.requiresOtherClause, this.shouldParseSkeletons = !!n.shouldParseSkeletons;
    }
    return e.prototype.parse = function() {
      if (this.offset() !== 0)
        throw Error("parser can only be used once");
      return this.parseMessage(0, "", !1);
    }, e.prototype.parseMessage = function(t, n, i) {
      for (var l = []; !this.isEOF(); ) {
        var r = this.char();
        if (r === 123) {
          var o = this.parseArgument(t, i);
          if (o.err)
            return o;
          l.push(o.val);
        } else {
          if (r === 125 && t > 0)
            break;
          if (r === 35 && (n === "plural" || n === "selectordinal")) {
            var u = this.clonePosition();
            this.bump(), l.push({
              type: D.pound,
              location: L(u, this.clonePosition())
            });
          } else if (r === 60 && !this.ignoreTag && this.peek() === 47) {
            if (i)
              break;
            return this.error(P.UNMATCHED_CLOSING_TAG, L(this.clonePosition(), this.clonePosition()));
          } else if (r === 60 && !this.ignoreTag && Nn(this.peek() || 0)) {
            var o = this.parseTag(t, n);
            if (o.err)
              return o;
            l.push(o.val);
          } else {
            var o = this.parseLiteral(t, n);
            if (o.err)
              return o;
            l.push(o.val);
          }
        }
      }
      return { val: l, err: null };
    }, e.prototype.parseTag = function(t, n) {
      var i = this.clonePosition();
      this.bump();
      var l = this.parseTagName();
      if (this.bumpSpace(), this.bumpIf("/>"))
        return {
          val: {
            type: D.literal,
            value: "<".concat(l, "/>"),
            location: L(i, this.clonePosition())
          },
          err: null
        };
      if (this.bumpIf(">")) {
        var r = this.parseMessage(t + 1, n, !0);
        if (r.err)
          return r;
        var o = r.val, u = this.clonePosition();
        if (this.bumpIf("</")) {
          if (this.isEOF() || !Nn(this.char()))
            return this.error(P.INVALID_TAG, L(u, this.clonePosition()));
          var s = this.clonePosition(), a = this.parseTagName();
          return l !== a ? this.error(P.UNMATCHED_CLOSING_TAG, L(s, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
            val: {
              type: D.tag,
              value: l,
              children: o,
              location: L(i, this.clonePosition())
            },
            err: null
          } : this.error(P.INVALID_TAG, L(u, this.clonePosition())));
        } else
          return this.error(P.UNCLOSED_TAG, L(i, this.clonePosition()));
      } else
        return this.error(P.INVALID_TAG, L(i, this.clonePosition()));
    }, e.prototype.parseTagName = function() {
      var t = this.offset();
      for (this.bump(); !this.isEOF() && $u(this.char()); )
        this.bump();
      return this.message.slice(t, this.offset());
    }, e.prototype.parseLiteral = function(t, n) {
      for (var i = this.clonePosition(), l = ""; ; ) {
        var r = this.tryParseQuote(n);
        if (r) {
          l += r;
          continue;
        }
        var o = this.tryParseUnquoted(t, n);
        if (o) {
          l += o;
          continue;
        }
        var u = this.tryParseLeftAngleBracket();
        if (u) {
          l += u;
          continue;
        }
        break;
      }
      var s = L(i, this.clonePosition());
      return {
        val: { type: D.literal, value: l, location: s },
        err: null
      };
    }, e.prototype.tryParseLeftAngleBracket = function() {
      return !this.isEOF() && this.char() === 60 && (this.ignoreTag || // If at the opening tag or closing tag position, bail.
      !Ku(this.peek() || 0)) ? (this.bump(), "<") : null;
    }, e.prototype.tryParseQuote = function(t) {
      if (this.isEOF() || this.char() !== 39)
        return null;
      switch (this.peek()) {
        case 39:
          return this.bump(), this.bump(), "'";
        case 123:
        case 60:
        case 62:
        case 125:
          break;
        case 35:
          if (t === "plural" || t === "selectordinal")
            break;
          return null;
        default:
          return null;
      }
      this.bump();
      var n = [this.char()];
      for (this.bump(); !this.isEOF(); ) {
        var i = this.char();
        if (i === 39)
          if (this.peek() === 39)
            n.push(39), this.bump();
          else {
            this.bump();
            break;
          }
        else
          n.push(i);
        this.bump();
      }
      return Pn.apply(void 0, n);
    }, e.prototype.tryParseUnquoted = function(t, n) {
      if (this.isEOF())
        return null;
      var i = this.char();
      return i === 60 || i === 123 || i === 35 && (n === "plural" || n === "selectordinal") || i === 125 && t > 0 ? null : (this.bump(), Pn(i));
    }, e.prototype.parseArgument = function(t, n) {
      var i = this.clonePosition();
      if (this.bump(), this.bumpSpace(), this.isEOF())
        return this.error(P.EXPECT_ARGUMENT_CLOSING_BRACE, L(i, this.clonePosition()));
      if (this.char() === 125)
        return this.bump(), this.error(P.EMPTY_ARGUMENT, L(i, this.clonePosition()));
      var l = this.parseIdentifierIfPossible().value;
      if (!l)
        return this.error(P.MALFORMED_ARGUMENT, L(i, this.clonePosition()));
      if (this.bumpSpace(), this.isEOF())
        return this.error(P.EXPECT_ARGUMENT_CLOSING_BRACE, L(i, this.clonePosition()));
      switch (this.char()) {
        case 125:
          return this.bump(), {
            val: {
              type: D.argument,
              // value does not include the opening and closing braces.
              value: l,
              location: L(i, this.clonePosition())
            },
            err: null
          };
        case 44:
          return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(P.EXPECT_ARGUMENT_CLOSING_BRACE, L(i, this.clonePosition())) : this.parseArgumentOptions(t, n, l, i);
        default:
          return this.error(P.MALFORMED_ARGUMENT, L(i, this.clonePosition()));
      }
    }, e.prototype.parseIdentifierIfPossible = function() {
      var t = this.clonePosition(), n = this.offset(), i = Ln(this.message, n), l = n + i.length;
      this.bumpTo(l);
      var r = this.clonePosition(), o = L(t, r);
      return { value: i, location: o };
    }, e.prototype.parseArgumentOptions = function(t, n, i, l) {
      var r, o = this.clonePosition(), u = this.parseIdentifierIfPossible().value, s = this.clonePosition();
      switch (u) {
        case "":
          return this.error(P.EXPECT_ARGUMENT_TYPE, L(o, s));
        case "number":
        case "date":
        case "time": {
          this.bumpSpace();
          var a = null;
          if (this.bumpIf(",")) {
            this.bumpSpace();
            var f = this.clonePosition(), c = this.parseSimpleArgStyleIfPossible();
            if (c.err)
              return c;
            var h = Ju(c.val);
            if (h.length === 0)
              return this.error(P.EXPECT_ARGUMENT_STYLE, L(this.clonePosition(), this.clonePosition()));
            var _ = L(f, this.clonePosition());
            a = { style: h, styleLocation: _ };
          }
          var d = this.tryParseArgumentClose(l);
          if (d.err)
            return d;
          var v = L(l, this.clonePosition());
          if (a && Di(a == null ? void 0 : a.style, "::", 0)) {
            var A = Qu(a.style.slice(2));
            if (u === "number") {
              var c = this.parseNumberSkeletonFromString(A, a.styleLocation);
              return c.err ? c : {
                val: { type: D.number, value: i, location: v, style: c.val },
                err: null
              };
            } else {
              if (A.length === 0)
                return this.error(P.EXPECT_DATE_TIME_SKELETON, v);
              var w = A;
              this.locale && (w = Ru(A, this.locale));
              var h = {
                type: rt.dateTime,
                pattern: w,
                location: a.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? Cu(w) : {}
              }, E = u === "date" ? D.date : D.time;
              return {
                val: { type: E, value: i, location: v, style: h },
                err: null
              };
            }
          }
          return {
            val: {
              type: u === "number" ? D.number : u === "date" ? D.date : D.time,
              value: i,
              location: v,
              style: (r = a == null ? void 0 : a.style) !== null && r !== void 0 ? r : null
            },
            err: null
          };
        }
        case "plural":
        case "selectordinal":
        case "select": {
          var p = this.clonePosition();
          if (this.bumpSpace(), !this.bumpIf(","))
            return this.error(P.EXPECT_SELECT_ARGUMENT_OPTIONS, L(p, O({}, p)));
          this.bumpSpace();
          var m = this.parseIdentifierIfPossible(), k = 0;
          if (u !== "select" && m.value === "offset") {
            if (!this.bumpIf(":"))
              return this.error(P.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, L(this.clonePosition(), this.clonePosition()));
            this.bumpSpace();
            var c = this.tryParseDecimalInteger(P.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, P.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE);
            if (c.err)
              return c;
            this.bumpSpace(), m = this.parseIdentifierIfPossible(), k = c.val;
          }
          var g = this.tryParsePluralOrSelectOptions(t, u, n, m);
          if (g.err)
            return g;
          var d = this.tryParseArgumentClose(l);
          if (d.err)
            return d;
          var T = L(l, this.clonePosition());
          return u === "select" ? {
            val: {
              type: D.select,
              value: i,
              options: Ui(g.val),
              location: T
            },
            err: null
          } : {
            val: {
              type: D.plural,
              value: i,
              options: Ui(g.val),
              offset: k,
              pluralType: u === "plural" ? "cardinal" : "ordinal",
              location: T
            },
            err: null
          };
        }
        default:
          return this.error(P.INVALID_ARGUMENT_TYPE, L(o, s));
      }
    }, e.prototype.tryParseArgumentClose = function(t) {
      return this.isEOF() || this.char() !== 125 ? this.error(P.EXPECT_ARGUMENT_CLOSING_BRACE, L(t, this.clonePosition())) : (this.bump(), { val: !0, err: null });
    }, e.prototype.parseSimpleArgStyleIfPossible = function() {
      for (var t = 0, n = this.clonePosition(); !this.isEOF(); ) {
        var i = this.char();
        switch (i) {
          case 39: {
            this.bump();
            var l = this.clonePosition();
            if (!this.bumpUntil("'"))
              return this.error(P.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, L(l, this.clonePosition()));
            this.bump();
            break;
          }
          case 123: {
            t += 1, this.bump();
            break;
          }
          case 125: {
            if (t > 0)
              t -= 1;
            else
              return {
                val: this.message.slice(n.offset, this.offset()),
                err: null
              };
            break;
          }
          default:
            this.bump();
            break;
        }
      }
      return {
        val: this.message.slice(n.offset, this.offset()),
        err: null
      };
    }, e.prototype.parseNumberSkeletonFromString = function(t, n) {
      var i = [];
      try {
        i = Pu(t);
      } catch {
        return this.error(P.INVALID_NUMBER_SKELETON, n);
      }
      return {
        val: {
          type: rt.number,
          tokens: i,
          location: n,
          parsedOptions: this.shouldParseSkeletons ? Mu(i) : {}
        },
        err: null
      };
    }, e.prototype.tryParsePluralOrSelectOptions = function(t, n, i, l) {
      for (var r, o = !1, u = [], s = /* @__PURE__ */ new Set(), a = l.value, f = l.location; ; ) {
        if (a.length === 0) {
          var c = this.clonePosition();
          if (n !== "select" && this.bumpIf("=")) {
            var h = this.tryParseDecimalInteger(P.EXPECT_PLURAL_ARGUMENT_SELECTOR, P.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (h.err)
              return h;
            f = L(c, this.clonePosition()), a = this.message.slice(c.offset, this.offset());
          } else
            break;
        }
        if (s.has(a))
          return this.error(n === "select" ? P.DUPLICATE_SELECT_ARGUMENT_SELECTOR : P.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, f);
        a === "other" && (o = !0), this.bumpSpace();
        var _ = this.clonePosition();
        if (!this.bumpIf("{"))
          return this.error(n === "select" ? P.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : P.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, L(this.clonePosition(), this.clonePosition()));
        var d = this.parseMessage(t + 1, n, i);
        if (d.err)
          return d;
        var v = this.tryParseArgumentClose(_);
        if (v.err)
          return v;
        u.push([
          a,
          {
            value: d.val,
            location: L(_, this.clonePosition())
          }
        ]), s.add(a), this.bumpSpace(), r = this.parseIdentifierIfPossible(), a = r.value, f = r.location;
      }
      return u.length === 0 ? this.error(n === "select" ? P.EXPECT_SELECT_ARGUMENT_SELECTOR : P.EXPECT_PLURAL_ARGUMENT_SELECTOR, L(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !o ? this.error(P.MISSING_OTHER_CLAUSE, L(this.clonePosition(), this.clonePosition())) : { val: u, err: null };
    }, e.prototype.tryParseDecimalInteger = function(t, n) {
      var i = 1, l = this.clonePosition();
      this.bumpIf("+") || this.bumpIf("-") && (i = -1);
      for (var r = !1, o = 0; !this.isEOF(); ) {
        var u = this.char();
        if (u >= 48 && u <= 57)
          r = !0, o = o * 10 + (u - 48), this.bump();
        else
          break;
      }
      var s = L(l, this.clonePosition());
      return r ? (o *= i, Zu(o) ? { val: o, err: null } : this.error(n, s)) : this.error(t, s);
    }, e.prototype.offset = function() {
      return this.position.offset;
    }, e.prototype.isEOF = function() {
      return this.offset() === this.message.length;
    }, e.prototype.clonePosition = function() {
      return {
        offset: this.position.offset,
        line: this.position.line,
        column: this.position.column
      };
    }, e.prototype.char = function() {
      var t = this.position.offset;
      if (t >= this.message.length)
        throw Error("out of bound");
      var n = $l(this.message, t);
      if (n === void 0)
        throw Error("Offset ".concat(t, " is at invalid UTF-16 code unit boundary"));
      return n;
    }, e.prototype.error = function(t, n) {
      return {
        val: null,
        err: {
          kind: t,
          message: this.message,
          location: n
        }
      };
    }, e.prototype.bump = function() {
      if (!this.isEOF()) {
        var t = this.char();
        t === 10 ? (this.position.line += 1, this.position.column = 1, this.position.offset += 1) : (this.position.column += 1, this.position.offset += t < 65536 ? 1 : 2);
      }
    }, e.prototype.bumpIf = function(t) {
      if (Di(this.message, t, this.offset())) {
        for (var n = 0; n < t.length; n++)
          this.bump();
        return !0;
      }
      return !1;
    }, e.prototype.bumpUntil = function(t) {
      var n = this.offset(), i = this.message.indexOf(t, n);
      return i >= 0 ? (this.bumpTo(i), !0) : (this.bumpTo(this.message.length), !1);
    }, e.prototype.bumpTo = function(t) {
      if (this.offset() > t)
        throw Error("targetOffset ".concat(t, " must be greater than or equal to the current offset ").concat(this.offset()));
      for (t = Math.min(t, this.message.length); ; ) {
        var n = this.offset();
        if (n === t)
          break;
        if (n > t)
          throw Error("targetOffset ".concat(t, " is at invalid UTF-16 code unit boundary"));
        if (this.bump(), this.isEOF())
          break;
      }
    }, e.prototype.bumpSpace = function() {
      for (; !this.isEOF() && tr(this.char()); )
        this.bump();
    }, e.prototype.peek = function() {
      if (this.isEOF())
        return null;
      var t = this.char(), n = this.offset(), i = this.message.charCodeAt(n + (t >= 65536 ? 2 : 1));
      return i ?? null;
    }, e;
  }()
);
function Nn(e) {
  return e >= 97 && e <= 122 || e >= 65 && e <= 90;
}
function Ku(e) {
  return Nn(e) || e === 47;
}
function $u(e) {
  return e === 45 || e === 46 || e >= 48 && e <= 57 || e === 95 || e >= 97 && e <= 122 || e >= 65 && e <= 90 || e == 183 || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
}
function tr(e) {
  return e >= 9 && e <= 13 || e === 32 || e === 133 || e >= 8206 && e <= 8207 || e === 8232 || e === 8233;
}
function ef(e) {
  return e >= 33 && e <= 35 || e === 36 || e >= 37 && e <= 39 || e === 40 || e === 41 || e === 42 || e === 43 || e === 44 || e === 45 || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || e === 91 || e === 92 || e === 93 || e === 94 || e === 96 || e === 123 || e === 124 || e === 125 || e === 126 || e === 161 || e >= 162 && e <= 165 || e === 166 || e === 167 || e === 169 || e === 171 || e === 172 || e === 174 || e === 176 || e === 177 || e === 182 || e === 187 || e === 191 || e === 215 || e === 247 || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || e === 8216 || e === 8217 || e === 8218 || e >= 8219 && e <= 8220 || e === 8221 || e === 8222 || e === 8223 || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || e === 8249 || e === 8250 || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || e === 8260 || e === 8261 || e === 8262 || e >= 8263 && e <= 8273 || e === 8274 || e === 8275 || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || e === 8608 || e >= 8609 && e <= 8610 || e === 8611 || e >= 8612 && e <= 8613 || e === 8614 || e >= 8615 && e <= 8621 || e === 8622 || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || e === 8658 || e === 8659 || e === 8660 || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || e === 8968 || e === 8969 || e === 8970 || e === 8971 || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || e === 9001 || e === 9002 || e >= 9003 && e <= 9083 || e === 9084 || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || e === 9655 || e >= 9656 && e <= 9664 || e === 9665 || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || e === 9839 || e >= 9840 && e <= 10087 || e === 10088 || e === 10089 || e === 10090 || e === 10091 || e === 10092 || e === 10093 || e === 10094 || e === 10095 || e === 10096 || e === 10097 || e === 10098 || e === 10099 || e === 10100 || e === 10101 || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || e === 10181 || e === 10182 || e >= 10183 && e <= 10213 || e === 10214 || e === 10215 || e === 10216 || e === 10217 || e === 10218 || e === 10219 || e === 10220 || e === 10221 || e === 10222 || e === 10223 || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || e === 10627 || e === 10628 || e === 10629 || e === 10630 || e === 10631 || e === 10632 || e === 10633 || e === 10634 || e === 10635 || e === 10636 || e === 10637 || e === 10638 || e === 10639 || e === 10640 || e === 10641 || e === 10642 || e === 10643 || e === 10644 || e === 10645 || e === 10646 || e === 10647 || e === 10648 || e >= 10649 && e <= 10711 || e === 10712 || e === 10713 || e === 10714 || e === 10715 || e >= 10716 && e <= 10747 || e === 10748 || e === 10749 || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || e === 11158 || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || e === 11778 || e === 11779 || e === 11780 || e === 11781 || e >= 11782 && e <= 11784 || e === 11785 || e === 11786 || e === 11787 || e === 11788 || e === 11789 || e >= 11790 && e <= 11798 || e === 11799 || e >= 11800 && e <= 11801 || e === 11802 || e === 11803 || e === 11804 || e === 11805 || e >= 11806 && e <= 11807 || e === 11808 || e === 11809 || e === 11810 || e === 11811 || e === 11812 || e === 11813 || e === 11814 || e === 11815 || e === 11816 || e === 11817 || e >= 11818 && e <= 11822 || e === 11823 || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || e === 11840 || e === 11841 || e === 11842 || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || e === 11858 || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || e === 12296 || e === 12297 || e === 12298 || e === 12299 || e === 12300 || e === 12301 || e === 12302 || e === 12303 || e === 12304 || e === 12305 || e >= 12306 && e <= 12307 || e === 12308 || e === 12309 || e === 12310 || e === 12311 || e === 12312 || e === 12313 || e === 12314 || e === 12315 || e === 12316 || e === 12317 || e >= 12318 && e <= 12319 || e === 12320 || e === 12336 || e === 64830 || e === 64831 || e >= 65093 && e <= 65094;
}
function On(e) {
  e.forEach(function(t) {
    if (delete t.location, zl(t) || Xl(t))
      for (var n in t.options)
        delete t.options[n].location, On(t.options[n].value);
    else
      Vl(t) && Wl(t.style) || (ql(t) || xl(t)) && Cn(t.style) ? delete t.style.location : Zl(t) && On(t.children);
  });
}
function tf(e, t) {
  t === void 0 && (t = {}), t = O({ shouldParseSkeletons: !0, requiresOtherClause: !0 }, t);
  var n = new Yu(e, t).parse();
  if (n.err) {
    var i = SyntaxError(P[n.err.kind]);
    throw i.location = n.err.location, i.originalMessage = n.err.message, i;
  }
  return t != null && t.captureLocation || On(n.val), n.val;
}
function gn(e, t) {
  var n = t && t.cache ? t.cache : af, i = t && t.serializer ? t.serializer : sf, l = t && t.strategy ? t.strategy : lf;
  return l(e, {
    cache: n,
    serializer: i
  });
}
function nf(e) {
  return e == null || typeof e == "number" || typeof e == "boolean";
}
function nr(e, t, n, i) {
  var l = nf(i) ? i : n(i), r = t.get(l);
  return typeof r > "u" && (r = e.call(this, i), t.set(l, r)), r;
}
function ir(e, t, n) {
  var i = Array.prototype.slice.call(arguments, 3), l = n(i), r = t.get(l);
  return typeof r > "u" && (r = e.apply(this, i), t.set(l, r)), r;
}
function Fn(e, t, n, i, l) {
  return n.bind(t, e, i, l);
}
function lf(e, t) {
  var n = e.length === 1 ? nr : ir;
  return Fn(e, this, n, t.cache.create(), t.serializer);
}
function rf(e, t) {
  return Fn(e, this, ir, t.cache.create(), t.serializer);
}
function of(e, t) {
  return Fn(e, this, nr, t.cache.create(), t.serializer);
}
var sf = function() {
  return JSON.stringify(arguments);
};
function jn() {
  this.cache = /* @__PURE__ */ Object.create(null);
}
jn.prototype.get = function(e) {
  return this.cache[e];
};
jn.prototype.set = function(e, t) {
  this.cache[e] = t;
};
var af = {
  create: function() {
    return new jn();
  }
}, pn = {
  variadic: rf,
  monadic: of
}, ot;
(function(e) {
  e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
})(ot || (ot = {}));
var Zt = (
  /** @class */
  function(e) {
    Xt(t, e);
    function t(n, i, l) {
      var r = e.call(this, n) || this;
      return r.code = i, r.originalMessage = l, r;
    }
    return t.prototype.toString = function() {
      return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
    }, t;
  }(Error)
), Fi = (
  /** @class */
  function(e) {
    Xt(t, e);
    function t(n, i, l, r) {
      return e.call(this, 'Invalid values for "'.concat(n, '": "').concat(i, '". Options are "').concat(Object.keys(l).join('", "'), '"'), ot.INVALID_VALUE, r) || this;
    }
    return t;
  }(Zt)
), uf = (
  /** @class */
  function(e) {
    Xt(t, e);
    function t(n, i, l) {
      return e.call(this, 'Value for "'.concat(n, '" must be of type ').concat(i), ot.INVALID_VALUE, l) || this;
    }
    return t;
  }(Zt)
), ff = (
  /** @class */
  function(e) {
    Xt(t, e);
    function t(n, i) {
      return e.call(this, 'The intl string context variable "'.concat(n, '" was not provided to the string "').concat(i, '"'), ot.MISSING_VALUE, i) || this;
    }
    return t;
  }(Zt)
), Y;
(function(e) {
  e[e.literal = 0] = "literal", e[e.object = 1] = "object";
})(Y || (Y = {}));
function cf(e) {
  return e.length < 2 ? e : e.reduce(function(t, n) {
    var i = t[t.length - 1];
    return !i || i.type !== Y.literal || n.type !== Y.literal ? t.push(n) : i.value += n.value, t;
  }, []);
}
function hf(e) {
  return typeof e == "function";
}
function Lt(e, t, n, i, l, r, o) {
  if (e.length === 1 && Ni(e[0]))
    return [
      {
        type: Y.literal,
        value: e[0].value
      }
    ];
  for (var u = [], s = 0, a = e; s < a.length; s++) {
    var f = a[s];
    if (Ni(f)) {
      u.push({
        type: Y.literal,
        value: f.value
      });
      continue;
    }
    if (Tu(f)) {
      typeof r == "number" && u.push({
        type: Y.literal,
        value: n.getNumberFormat(t).format(r)
      });
      continue;
    }
    var c = f.value;
    if (!(l && c in l))
      throw new ff(c, o);
    var h = l[c];
    if (Au(f)) {
      (!h || typeof h == "string" || typeof h == "number") && (h = typeof h == "string" || typeof h == "number" ? String(h) : ""), u.push({
        type: typeof h == "string" ? Y.literal : Y.object,
        value: h
      });
      continue;
    }
    if (ql(f)) {
      var _ = typeof f.style == "string" ? i.date[f.style] : Cn(f.style) ? f.style.parsedOptions : void 0;
      u.push({
        type: Y.literal,
        value: n.getDateTimeFormat(t, _).format(h)
      });
      continue;
    }
    if (xl(f)) {
      var _ = typeof f.style == "string" ? i.time[f.style] : Cn(f.style) ? f.style.parsedOptions : i.time.medium;
      u.push({
        type: Y.literal,
        value: n.getDateTimeFormat(t, _).format(h)
      });
      continue;
    }
    if (Vl(f)) {
      var _ = typeof f.style == "string" ? i.number[f.style] : Wl(f.style) ? f.style.parsedOptions : void 0;
      _ && _.scale && (h = h * (_.scale || 1)), u.push({
        type: Y.literal,
        value: n.getNumberFormat(t, _).format(h)
      });
      continue;
    }
    if (Zl(f)) {
      var d = f.children, v = f.value, A = l[v];
      if (!hf(A))
        throw new uf(v, "function", o);
      var w = Lt(d, t, n, i, l, r), E = A(w.map(function(k) {
        return k.value;
      }));
      Array.isArray(E) || (E = [E]), u.push.apply(u, E.map(function(k) {
        return {
          type: typeof k == "string" ? Y.literal : Y.object,
          value: k
        };
      }));
    }
    if (zl(f)) {
      var p = f.options[h] || f.options.other;
      if (!p)
        throw new Fi(f.value, h, Object.keys(f.options), o);
      u.push.apply(u, Lt(p.value, t, n, i, l));
      continue;
    }
    if (Xl(f)) {
      var p = f.options["=".concat(h)];
      if (!p) {
        if (!Intl.PluralRules)
          throw new Zt(`Intl.PluralRules is not available in this environment.
Try polyfilling it using "@formatjs/intl-pluralrules"
`, ot.MISSING_INTL_API, o);
        var m = n.getPluralRules(t, { type: f.pluralType }).select(h - (f.offset || 0));
        p = f.options[m] || f.options.other;
      }
      if (!p)
        throw new Fi(f.value, h, Object.keys(f.options), o);
      u.push.apply(u, Lt(p.value, t, n, i, l, h - (f.offset || 0)));
      continue;
    }
  }
  return cf(u);
}
function _f(e, t) {
  return t ? O(O(O({}, e || {}), t || {}), Object.keys(e).reduce(function(n, i) {
    return n[i] = O(O({}, e[i]), t[i] || {}), n;
  }, {})) : e;
}
function mf(e, t) {
  return t ? Object.keys(e).reduce(function(n, i) {
    return n[i] = _f(e[i], t[i]), n;
  }, O({}, e)) : e;
}
function vn(e) {
  return {
    create: function() {
      return {
        get: function(t) {
          return e[t];
        },
        set: function(t, n) {
          e[t] = n;
        }
      };
    }
  };
}
function df(e) {
  return e === void 0 && (e = {
    number: {},
    dateTime: {},
    pluralRules: {}
  }), {
    getNumberFormat: gn(function() {
      for (var t, n = [], i = 0; i < arguments.length; i++)
        n[i] = arguments[i];
      return new ((t = Intl.NumberFormat).bind.apply(t, dn([void 0], n, !1)))();
    }, {
      cache: vn(e.number),
      strategy: pn.variadic
    }),
    getDateTimeFormat: gn(function() {
      for (var t, n = [], i = 0; i < arguments.length; i++)
        n[i] = arguments[i];
      return new ((t = Intl.DateTimeFormat).bind.apply(t, dn([void 0], n, !1)))();
    }, {
      cache: vn(e.dateTime),
      strategy: pn.variadic
    }),
    getPluralRules: gn(function() {
      for (var t, n = [], i = 0; i < arguments.length; i++)
        n[i] = arguments[i];
      return new ((t = Intl.PluralRules).bind.apply(t, dn([void 0], n, !1)))();
    }, {
      cache: vn(e.pluralRules),
      strategy: pn.variadic
    })
  };
}
var bf = (
  /** @class */
  function() {
    function e(t, n, i, l) {
      var r = this;
      if (n === void 0 && (n = e.defaultLocale), this.formatterCache = {
        number: {},
        dateTime: {},
        pluralRules: {}
      }, this.format = function(s) {
        var a = r.formatToParts(s);
        if (a.length === 1)
          return a[0].value;
        var f = a.reduce(function(c, h) {
          return !c.length || h.type !== Y.literal || typeof c[c.length - 1] != "string" ? c.push(h.value) : c[c.length - 1] += h.value, c;
        }, []);
        return f.length <= 1 ? f[0] || "" : f;
      }, this.formatToParts = function(s) {
        return Lt(r.ast, r.locales, r.formatters, r.formats, s, void 0, r.message);
      }, this.resolvedOptions = function() {
        var s;
        return {
          locale: ((s = r.resolvedLocale) === null || s === void 0 ? void 0 : s.toString()) || Intl.NumberFormat.supportedLocalesOf(r.locales)[0]
        };
      }, this.getAst = function() {
        return r.ast;
      }, this.locales = n, this.resolvedLocale = e.resolveLocale(n), typeof t == "string") {
        if (this.message = t, !e.__parse)
          throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
        var o = l || {};
        o.formatters;
        var u = Su(o, ["formatters"]);
        this.ast = e.__parse(t, O(O({}, u), { locale: this.resolvedLocale }));
      } else
        this.ast = t;
      if (!Array.isArray(this.ast))
        throw new TypeError("A message must be provided as a String or AST.");
      this.formats = mf(e.formats, i), this.formatters = l && l.formatters || df(this.formatterCache);
    }
    return Object.defineProperty(e, "defaultLocale", {
      get: function() {
        return e.memoizedDefaultLocale || (e.memoizedDefaultLocale = new Intl.NumberFormat().resolvedOptions().locale), e.memoizedDefaultLocale;
      },
      enumerable: !1,
      configurable: !0
    }), e.memoizedDefaultLocale = null, e.resolveLocale = function(t) {
      if (!(typeof Intl.Locale > "u")) {
        var n = Intl.NumberFormat.supportedLocalesOf(t);
        return n.length > 0 ? new Intl.Locale(n[0]) : new Intl.Locale(typeof t == "string" ? t : t[0]);
      }
    }, e.__parse = tf, e.formats = {
      number: {
        integer: {
          maximumFractionDigits: 0
        },
        currency: {
          style: "currency"
        },
        percent: {
          style: "percent"
        }
      },
      date: {
        short: {
          month: "numeric",
          day: "numeric",
          year: "2-digit"
        },
        medium: {
          month: "short",
          day: "numeric",
          year: "numeric"
        },
        long: {
          month: "long",
          day: "numeric",
          year: "numeric"
        },
        full: {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric"
        }
      },
      time: {
        short: {
          hour: "numeric",
          minute: "numeric"
        },
        medium: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric"
        },
        long: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        },
        full: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        }
      }
    }, e;
  }()
);
function gf(e, t) {
  if (t == null)
    return;
  if (t in e)
    return e[t];
  const n = t.split(".");
  let i = e;
  for (let l = 0; l < n.length; l++)
    if (typeof i == "object") {
      if (l > 0) {
        const r = n.slice(l, n.length).join(".");
        if (r in i) {
          i = i[r];
          break;
        }
      }
      i = i[n[l]];
    } else
      i = void 0;
  return i;
}
const Ue = {}, pf = (e, t, n) => n && (t in Ue || (Ue[t] = {}), e in Ue[t] || (Ue[t][e] = n), n), lr = (e, t) => {
  if (t == null)
    return;
  if (t in Ue && e in Ue[t])
    return Ue[t][e];
  const n = Wt(t);
  for (let i = 0; i < n.length; i++) {
    const l = n[i], r = wf(l, e);
    if (r)
      return pf(e, t, r);
  }
};
let Vn;
const Et = vt({});
function vf(e) {
  return Vn[e] || null;
}
function rr(e) {
  return e in Vn;
}
function wf(e, t) {
  if (!rr(e))
    return null;
  const n = vf(e);
  return gf(n, t);
}
function yf(e) {
  if (e == null)
    return;
  const t = Wt(e);
  for (let n = 0; n < t.length; n++) {
    const i = t[n];
    if (rr(i))
      return i;
  }
}
function Ef(e, ...t) {
  delete Ue[e], Et.update((n) => (n[e] = Hu.all([n[e] || {}, ...t]), n));
}
at(
  [Et],
  ([e]) => Object.keys(e)
);
Et.subscribe((e) => Vn = e);
const Nt = {};
function kf(e, t) {
  Nt[e].delete(t), Nt[e].size === 0 && delete Nt[e];
}
function or(e) {
  return Nt[e];
}
function Hf(e) {
  return Wt(e).map((t) => {
    const n = or(t);
    return [t, n ? [...n] : []];
  }).filter(([, t]) => t.length > 0);
}
function Mn(e) {
  return e == null ? !1 : Wt(e).some(
    (t) => {
      var n;
      return (n = or(t)) == null ? void 0 : n.size;
    }
  );
}
function Sf(e, t) {
  return Promise.all(
    t.map((i) => (kf(e, i), i().then((l) => l.default || l)))
  ).then((i) => Ef(e, ...i));
}
const _t = {};
function sr(e) {
  if (!Mn(e))
    return e in _t ? _t[e] : Promise.resolve();
  const t = Hf(e);
  return _t[e] = Promise.all(
    t.map(
      ([n, i]) => Sf(n, i)
    )
  ).then(() => {
    if (Mn(e))
      return sr(e);
    delete _t[e];
  }), _t[e];
}
const Af = {
  number: {
    scientific: { notation: "scientific" },
    engineering: { notation: "engineering" },
    compactLong: { notation: "compact", compactDisplay: "long" },
    compactShort: { notation: "compact", compactDisplay: "short" }
  },
  date: {
    short: { month: "numeric", day: "numeric", year: "2-digit" },
    medium: { month: "short", day: "numeric", year: "numeric" },
    long: { month: "long", day: "numeric", year: "numeric" },
    full: { weekday: "long", month: "long", day: "numeric", year: "numeric" }
  },
  time: {
    short: { hour: "numeric", minute: "numeric" },
    medium: { hour: "numeric", minute: "numeric", second: "numeric" },
    long: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    },
    full: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    }
  }
}, Tf = {
  fallbackLocale: null,
  loadingDelay: 200,
  formats: Af,
  warnOnMissingMessages: !0,
  handleMissingMessage: void 0,
  ignoreTag: !0
}, Bf = Tf;
function st() {
  return Bf;
}
const wn = vt(!1);
var Cf = Object.defineProperty, If = Object.defineProperties, Pf = Object.getOwnPropertyDescriptors, ji = Object.getOwnPropertySymbols, Lf = Object.prototype.hasOwnProperty, Nf = Object.prototype.propertyIsEnumerable, Vi = (e, t, n) => t in e ? Cf(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n, Of = (e, t) => {
  for (var n in t || (t = {}))
    Lf.call(t, n) && Vi(e, n, t[n]);
  if (ji)
    for (var n of ji(t))
      Nf.call(t, n) && Vi(e, n, t[n]);
  return e;
}, Mf = (e, t) => If(e, Pf(t));
let Rn;
const Gt = vt(null);
function qi(e) {
  return e.split("-").map((t, n, i) => i.slice(0, n + 1).join("-")).reverse();
}
function Wt(e, t = st().fallbackLocale) {
  const n = qi(e);
  return t ? [.../* @__PURE__ */ new Set([...n, ...qi(t)])] : n;
}
function Qe() {
  return Rn ?? void 0;
}
Gt.subscribe((e) => {
  Rn = e ?? void 0, typeof window < "u" && e != null && document.documentElement.setAttribute("lang", e);
});
const Rf = (e) => {
  if (e && yf(e) && Mn(e)) {
    const { loadingDelay: t } = st();
    let n;
    return typeof window < "u" && Qe() != null && t ? n = window.setTimeout(
      () => wn.set(!0),
      t
    ) : wn.set(!0), sr(e).then(() => {
      Gt.set(e);
    }).finally(() => {
      clearTimeout(n), wn.set(!1);
    });
  }
  return Gt.set(e);
}, kt = Mf(Of({}, Gt), {
  set: Rf
}), Qt = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return (i) => {
    const l = JSON.stringify(i);
    return l in t ? t[l] : t[l] = e(i);
  };
};
var Df = Object.defineProperty, Ft = Object.getOwnPropertySymbols, ar = Object.prototype.hasOwnProperty, ur = Object.prototype.propertyIsEnumerable, xi = (e, t, n) => t in e ? Df(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n, qn = (e, t) => {
  for (var n in t || (t = {}))
    ar.call(t, n) && xi(e, n, t[n]);
  if (Ft)
    for (var n of Ft(t))
      ur.call(t, n) && xi(e, n, t[n]);
  return e;
}, ft = (e, t) => {
  var n = {};
  for (var i in e)
    ar.call(e, i) && t.indexOf(i) < 0 && (n[i] = e[i]);
  if (e != null && Ft)
    for (var i of Ft(e))
      t.indexOf(i) < 0 && ur.call(e, i) && (n[i] = e[i]);
  return n;
};
const pt = (e, t) => {
  const { formats: n } = st();
  if (e in n && t in n[e])
    return n[e][t];
  throw new Error(`[svelte-i18n] Unknown "${t}" ${e} format.`);
}, Uf = Qt(
  (e) => {
    var t = e, { locale: n, format: i } = t, l = ft(t, ["locale", "format"]);
    if (n == null)
      throw new Error('[svelte-i18n] A "locale" must be set to format numbers');
    return i && (l = pt("number", i)), new Intl.NumberFormat(n, l);
  }
), Gf = Qt(
  (e) => {
    var t = e, { locale: n, format: i } = t, l = ft(t, ["locale", "format"]);
    if (n == null)
      throw new Error('[svelte-i18n] A "locale" must be set to format dates');
    return i ? l = pt("date", i) : Object.keys(l).length === 0 && (l = pt("date", "short")), new Intl.DateTimeFormat(n, l);
  }
), Ff = Qt(
  (e) => {
    var t = e, { locale: n, format: i } = t, l = ft(t, ["locale", "format"]);
    if (n == null)
      throw new Error(
        '[svelte-i18n] A "locale" must be set to format time values'
      );
    return i ? l = pt("time", i) : Object.keys(l).length === 0 && (l = pt("time", "short")), new Intl.DateTimeFormat(n, l);
  }
), jf = (e = {}) => {
  var t = e, {
    locale: n = Qe()
  } = t, i = ft(t, [
    "locale"
  ]);
  return Uf(qn({ locale: n }, i));
}, Vf = (e = {}) => {
  var t = e, {
    locale: n = Qe()
  } = t, i = ft(t, [
    "locale"
  ]);
  return Gf(qn({ locale: n }, i));
}, qf = (e = {}) => {
  var t = e, {
    locale: n = Qe()
  } = t, i = ft(t, [
    "locale"
  ]);
  return Ff(qn({ locale: n }, i));
}, xf = Qt(
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  (e, t = Qe()) => new bf(e, t, st().formats, {
    ignoreTag: st().ignoreTag
  })
), zf = (e, t = {}) => {
  var n, i, l, r;
  let o = t;
  typeof e == "object" && (o = e, e = o.id);
  const {
    values: u,
    locale: s = Qe(),
    default: a
  } = o;
  if (s == null)
    throw new Error(
      "[svelte-i18n] Cannot format a message without first setting the initial locale."
    );
  let f = lr(e, s);
  if (!f)
    f = (r = (l = (i = (n = st()).handleMissingMessage) == null ? void 0 : i.call(n, { locale: s, id: e, defaultValue: a })) != null ? l : a) != null ? r : e;
  else if (typeof f != "string")
    return console.warn(
      `[svelte-i18n] Message with id "${e}" must be of type "string", found: "${typeof f}". Gettin its value through the "$format" method is deprecated; use the "json" method instead.`
    ), f;
  if (!u)
    return f;
  let c = f;
  try {
    c = xf(f, s).format(u);
  } catch (h) {
    h instanceof Error && console.warn(
      `[svelte-i18n] Message "${e}" has syntax error:`,
      h.message
    );
  }
  return c;
}, Xf = (e, t) => qf(t).format(e), Zf = (e, t) => Vf(t).format(e), Wf = (e, t) => jf(t).format(e), Qf = (e, t = Qe()) => lr(e, t);
at([kt, Et], () => zf);
at([kt], () => Xf);
at([kt], () => Zf);
at([kt], () => Wf);
at([kt, Et], () => Qf);
const {
  SvelteComponent: Jf,
  append: zi,
  attr: Yf,
  check_outros: Xi,
  create_component: xn,
  destroy_component: zn,
  detach: Kf,
  element: $f,
  group_outros: Zi,
  init: e0,
  insert: t0,
  mount_component: Xn,
  safe_not_equal: n0,
  set_style: Wi,
  space: Qi,
  toggle_class: Ji,
  transition_in: Ae,
  transition_out: Ve
} = window.__gradio__svelte__internal, { createEventDispatcher: i0 } = window.__gradio__svelte__internal;
function Yi(e) {
  let t, n;
  return t = new We({
    props: {
      Icon: ys,
      label: (
        /*i18n*/
        e[3]("common.edit")
      )
    }
  }), t.$on(
    "click",
    /*click_handler*/
    e[5]
  ), {
    c() {
      xn(t.$$.fragment);
    },
    m(i, l) {
      Xn(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l & /*i18n*/
      8 && (r.label = /*i18n*/
      i[3]("common.edit")), t.$set(r);
    },
    i(i) {
      n || (Ae(t.$$.fragment, i), n = !0);
    },
    o(i) {
      Ve(t.$$.fragment, i), n = !1;
    },
    d(i) {
      zn(t, i);
    }
  };
}
function Ki(e) {
  let t, n;
  return t = new We({
    props: {
      Icon: Vs,
      label: (
        /*i18n*/
        e[3]("common.undo")
      )
    }
  }), t.$on(
    "click",
    /*click_handler_1*/
    e[6]
  ), {
    c() {
      xn(t.$$.fragment);
    },
    m(i, l) {
      Xn(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l & /*i18n*/
      8 && (r.label = /*i18n*/
      i[3]("common.undo")), t.$set(r);
    },
    i(i) {
      n || (Ae(t.$$.fragment, i), n = !0);
    },
    o(i) {
      Ve(t.$$.fragment, i), n = !1;
    },
    d(i) {
      zn(t, i);
    }
  };
}
function l0(e) {
  let t, n, i, l, r, o = (
    /*editable*/
    e[0] && Yi(e)
  ), u = (
    /*undoable*/
    e[1] && Ki(e)
  );
  return l = new We({
    props: {
      Icon: Yo,
      label: (
        /*i18n*/
        e[3]("common.clear")
      )
    }
  }), l.$on(
    "click",
    /*click_handler_2*/
    e[7]
  ), {
    c() {
      t = $f("div"), o && o.c(), n = Qi(), u && u.c(), i = Qi(), xn(l.$$.fragment), Yf(t, "class", "svelte-1wj0ocy"), Ji(t, "not-absolute", !/*absolute*/
      e[2]), Wi(
        t,
        "position",
        /*absolute*/
        e[2] ? "absolute" : "static"
      );
    },
    m(s, a) {
      t0(s, t, a), o && o.m(t, null), zi(t, n), u && u.m(t, null), zi(t, i), Xn(l, t, null), r = !0;
    },
    p(s, [a]) {
      /*editable*/
      s[0] ? o ? (o.p(s, a), a & /*editable*/
      1 && Ae(o, 1)) : (o = Yi(s), o.c(), Ae(o, 1), o.m(t, n)) : o && (Zi(), Ve(o, 1, 1, () => {
        o = null;
      }), Xi()), /*undoable*/
      s[1] ? u ? (u.p(s, a), a & /*undoable*/
      2 && Ae(u, 1)) : (u = Ki(s), u.c(), Ae(u, 1), u.m(t, i)) : u && (Zi(), Ve(u, 1, 1, () => {
        u = null;
      }), Xi());
      const f = {};
      a & /*i18n*/
      8 && (f.label = /*i18n*/
      s[3]("common.clear")), l.$set(f), (!r || a & /*absolute*/
      4) && Ji(t, "not-absolute", !/*absolute*/
      s[2]), a & /*absolute*/
      4 && Wi(
        t,
        "position",
        /*absolute*/
        s[2] ? "absolute" : "static"
      );
    },
    i(s) {
      r || (Ae(o), Ae(u), Ae(l.$$.fragment, s), r = !0);
    },
    o(s) {
      Ve(o), Ve(u), Ve(l.$$.fragment, s), r = !1;
    },
    d(s) {
      s && Kf(t), o && o.d(), u && u.d(), zn(l);
    }
  };
}
function r0(e, t, n) {
  let { editable: i = !1 } = t, { undoable: l = !1 } = t, { absolute: r = !0 } = t, { i18n: o } = t;
  const u = i0(), s = () => u("edit"), a = () => u("undo"), f = (c) => {
    u("clear"), c.stopPropagation();
  };
  return e.$$set = (c) => {
    "editable" in c && n(0, i = c.editable), "undoable" in c && n(1, l = c.undoable), "absolute" in c && n(2, r = c.absolute), "i18n" in c && n(3, o = c.i18n);
  }, [
    i,
    l,
    r,
    o,
    u,
    s,
    a,
    f
  ];
}
class o0 extends Jf {
  constructor(t) {
    super(), e0(this, t, r0, l0, n0, {
      editable: 0,
      undoable: 1,
      absolute: 2,
      i18n: 3
    });
  }
}
var $i = Object.prototype.hasOwnProperty;
function el(e, t, n) {
  for (n of e.keys())
    if (mt(n, t))
      return n;
}
function mt(e, t) {
  var n, i, l;
  if (e === t)
    return !0;
  if (e && t && (n = e.constructor) === t.constructor) {
    if (n === Date)
      return e.getTime() === t.getTime();
    if (n === RegExp)
      return e.toString() === t.toString();
    if (n === Array) {
      if ((i = e.length) === t.length)
        for (; i-- && mt(e[i], t[i]); )
          ;
      return i === -1;
    }
    if (n === Set) {
      if (e.size !== t.size)
        return !1;
      for (i of e)
        if (l = i, l && typeof l == "object" && (l = el(t, l), !l) || !t.has(l))
          return !1;
      return !0;
    }
    if (n === Map) {
      if (e.size !== t.size)
        return !1;
      for (i of e)
        if (l = i[0], l && typeof l == "object" && (l = el(t, l), !l) || !mt(i[1], t.get(l)))
          return !1;
      return !0;
    }
    if (n === ArrayBuffer)
      e = new Uint8Array(e), t = new Uint8Array(t);
    else if (n === DataView) {
      if ((i = e.byteLength) === t.byteLength)
        for (; i-- && e.getInt8(i) === t.getInt8(i); )
          ;
      return i === -1;
    }
    if (ArrayBuffer.isView(e)) {
      if ((i = e.byteLength) === t.byteLength)
        for (; i-- && e[i] === t[i]; )
          ;
      return i === -1;
    }
    if (!n || typeof e == "object") {
      i = 0;
      for (n in e)
        if ($i.call(e, n) && ++i && !$i.call(t, n) || !(n in t) || !mt(e[n], t[n]))
          return !1;
      return Object.keys(t).length === i;
    }
  }
  return e !== e && t !== t;
}
const {
  SvelteComponent: s0,
  append: tl,
  attr: Z,
  detach: a0,
  init: u0,
  insert: f0,
  noop: nl,
  safe_not_equal: c0,
  svg_element: yn
} = window.__gradio__svelte__internal;
function h0(e) {
  let t, n, i, l;
  return {
    c() {
      t = yn("svg"), n = yn("path"), i = yn("path"), Z(n, "stroke", "currentColor"), Z(n, "stroke-width", "1.5"), Z(n, "stroke-linecap", "round"), Z(n, "d", "M16.472 20H4.1a.6.6 0 0 1-.6-.6V9.6a.6.6 0 0 1 .6-.6h2.768a2 2 0 0 0 1.715-.971l2.71-4.517a1.631 1.631 0 0 1 2.961 1.308l-1.022 3.408a.6.6 0 0 0 .574.772h4.575a2 2 0 0 1 1.93 2.526l-1.91 7A2 2 0 0 1 16.473 20Z"), Z(i, "stroke", "currentColor"), Z(i, "stroke-width", "1.5"), Z(i, "stroke-linecap", "round"), Z(i, "stroke-linejoin", "round"), Z(i, "d", "M7 20V9"), Z(t, "xmlns", "http://www.w3.org/2000/svg"), Z(t, "viewBox", "0 0 24 24"), Z(t, "fill", l = /*selected*/
      e[0] ? "currentColor" : "none"), Z(t, "stroke-width", "1.5"), Z(t, "color", "currentColor"), Z(t, "transform", "rotate(180)");
    },
    m(r, o) {
      f0(r, t, o), tl(t, n), tl(t, i);
    },
    p(r, [o]) {
      o & /*selected*/
      1 && l !== (l = /*selected*/
      r[0] ? "currentColor" : "none") && Z(t, "fill", l);
    },
    i: nl,
    o: nl,
    d(r) {
      r && a0(t);
    }
  };
}
function _0(e, t, n) {
  let { selected: i } = t;
  return e.$$set = (l) => {
    "selected" in l && n(0, i = l.selected);
  }, [i];
}
class m0 extends s0 {
  constructor(t) {
    super(), u0(this, t, _0, h0, c0, { selected: 0 });
  }
}
const {
  SvelteComponent: d0,
  append: Be,
  attr: pe,
  check_outros: b0,
  create_component: il,
  destroy_component: ll,
  detach: Jt,
  element: Ze,
  flush: Pt,
  group_outros: g0,
  init: p0,
  insert: Yt,
  listen: fr,
  mount_component: rl,
  safe_not_equal: v0,
  set_data: cr,
  set_style: w0,
  space: Ot,
  src_url_equal: ol,
  text: hr,
  transition_in: dt,
  transition_out: jt
} = window.__gradio__svelte__internal, { createEventDispatcher: y0 } = window.__gradio__svelte__internal;
function sl(e) {
  let t, n = (
    /*value*/
    e[0].caption + ""
  ), i;
  return {
    c() {
      t = Ze("div"), i = hr(n), pe(t, "class", "foot-label left-label svelte-u350v8");
    },
    m(l, r) {
      Yt(l, t, r), Be(t, i);
    },
    p(l, r) {
      r & /*value*/
      1 && n !== (n = /*value*/
      l[0].caption + "") && cr(i, n);
    },
    d(l) {
      l && Jt(t);
    }
  };
}
function al(e) {
  let t, n, i, l;
  return {
    c() {
      t = Ze("button"), n = hr(
        /*action_label*/
        e[3]
      ), pe(t, "class", "foot-label right-label svelte-u350v8");
    },
    m(r, o) {
      Yt(r, t, o), Be(t, n), i || (l = fr(
        t,
        "click",
        /*click_handler_1*/
        e[6]
      ), i = !0);
    },
    p(r, o) {
      o & /*action_label*/
      8 && cr(
        n,
        /*action_label*/
        r[3]
      );
    },
    d(r) {
      r && Jt(t), i = !1, l();
    }
  };
}
function ul(e) {
  let t, n, i, l, r, o, u;
  return i = new We({
    props: {
      size: "large",
      highlight: (
        /*value*/
        e[0].liked
      ),
      Icon: Ms
    }
  }), i.$on(
    "click",
    /*click_handler_2*/
    e[7]
  ), o = new We({
    props: {
      size: "large",
      highlight: (
        /*value*/
        e[0].liked === !1
      ),
      Icon: m0
    }
  }), o.$on(
    "click",
    /*click_handler_3*/
    e[8]
  ), {
    c() {
      t = Ze("div"), n = Ze("span"), il(i.$$.fragment), l = Ot(), r = Ze("span"), il(o.$$.fragment), w0(n, "margin-right", "1px"), pe(t, "class", "like-button svelte-u350v8");
    },
    m(s, a) {
      Yt(s, t, a), Be(t, n), rl(i, n, null), Be(t, l), Be(t, r), rl(o, r, null), u = !0;
    },
    p(s, a) {
      const f = {};
      a & /*value*/
      1 && (f.highlight = /*value*/
      s[0].liked), i.$set(f);
      const c = {};
      a & /*value*/
      1 && (c.highlight = /*value*/
      s[0].liked === !1), o.$set(c);
    },
    i(s) {
      u || (dt(i.$$.fragment, s), dt(o.$$.fragment, s), u = !0);
    },
    o(s) {
      jt(i.$$.fragment, s), jt(o.$$.fragment, s), u = !1;
    },
    d(s) {
      s && Jt(t), ll(i), ll(o);
    }
  };
}
function E0(e) {
  let t, n, i, l, r, o, u, s, a, f, c = (
    /*value*/
    e[0].caption && sl(e)
  ), h = (
    /*clickable*/
    e[2] && al(e)
  ), _ = (
    /*likeable*/
    e[1] && ul(e)
  );
  return {
    c() {
      t = Ze("div"), n = Ze("img"), r = Ot(), c && c.c(), o = Ot(), h && h.c(), u = Ot(), _ && _.c(), pe(n, "alt", i = /*value*/
      e[0].caption || ""), ol(n.src, l = /*value*/
      e[0].image.url) || pe(n, "src", l), pe(n, "class", "thumbnail-img svelte-u350v8"), pe(n, "loading", "lazy"), pe(t, "class", "thumbnail-image-box svelte-u350v8");
    },
    m(d, v) {
      Yt(d, t, v), Be(t, n), Be(t, r), c && c.m(t, null), Be(t, o), h && h.m(t, null), Be(t, u), _ && _.m(t, null), s = !0, a || (f = fr(
        n,
        "click",
        /*click_handler*/
        e[5]
      ), a = !0);
    },
    p(d, [v]) {
      (!s || v & /*value*/
      1 && i !== (i = /*value*/
      d[0].caption || "")) && pe(n, "alt", i), (!s || v & /*value*/
      1 && !ol(n.src, l = /*value*/
      d[0].image.url)) && pe(n, "src", l), /*value*/
      d[0].caption ? c ? c.p(d, v) : (c = sl(d), c.c(), c.m(t, o)) : c && (c.d(1), c = null), /*clickable*/
      d[2] ? h ? h.p(d, v) : (h = al(d), h.c(), h.m(t, u)) : h && (h.d(1), h = null), /*likeable*/
      d[1] ? _ ? (_.p(d, v), v & /*likeable*/
      2 && dt(_, 1)) : (_ = ul(d), _.c(), dt(_, 1), _.m(t, null)) : _ && (g0(), jt(_, 1, 1, () => {
        _ = null;
      }), b0());
    },
    i(d) {
      s || (dt(_), s = !0);
    },
    o(d) {
      jt(_), s = !1;
    },
    d(d) {
      d && Jt(t), c && c.d(), h && h.d(), _ && _.d(), a = !1, f();
    }
  };
}
function k0(e, t, n) {
  const i = y0();
  let { likeable: l } = t, { clickable: r } = t, { value: o } = t, { action_label: u } = t;
  const s = () => i("click"), a = () => {
    i("label_click");
  }, f = () => {
    if (o.liked) {
      n(0, o.liked = void 0, o), i("like", void 0);
      return;
    }
    n(0, o.liked = !0, o), i("like", !0);
  }, c = () => {
    if (o.liked === !1) {
      n(0, o.liked = void 0, o), i("like", void 0);
      return;
    }
    n(0, o.liked = !1, o), i("like", !1);
  };
  return e.$$set = (h) => {
    "likeable" in h && n(1, l = h.likeable), "clickable" in h && n(2, r = h.clickable), "value" in h && n(0, o = h.value), "action_label" in h && n(3, u = h.action_label);
  }, [
    o,
    l,
    r,
    u,
    i,
    s,
    a,
    f,
    c
  ];
}
class H0 extends d0 {
  constructor(t) {
    super(), p0(this, t, k0, E0, v0, {
      likeable: 1,
      clickable: 2,
      value: 0,
      action_label: 3
    });
  }
  get likeable() {
    return this.$$.ctx[1];
  }
  set likeable(t) {
    this.$$set({ likeable: t }), Pt();
  }
  get clickable() {
    return this.$$.ctx[2];
  }
  set clickable(t) {
    this.$$set({ clickable: t }), Pt();
  }
  get value() {
    return this.$$.ctx[0];
  }
  set value(t) {
    this.$$set({ value: t }), Pt();
  }
  get action_label() {
    return this.$$.ctx[3];
  }
  set action_label(t) {
    this.$$set({ action_label: t }), Pt();
  }
}
const En = [
  {
    key: "xs",
    width: 0
  },
  {
    key: "sm",
    width: 576
  },
  {
    key: "md",
    width: 768
  },
  {
    key: "lg",
    width: 992
  },
  {
    key: "xl",
    width: 1200
  },
  {
    key: "xxl",
    width: 1600
  }
];
async function S0(e) {
  if ("clipboard" in navigator)
    await navigator.clipboard.writeText(e);
  else {
    const t = document.createElement("textarea");
    t.value = e, t.style.position = "absolute", t.style.left = "-999999px", document.body.prepend(t), t.select();
    try {
      document.execCommand("copy");
    } catch (n) {
      return Promise.reject(n);
    } finally {
      t.remove();
    }
  }
}
async function A0(e) {
  return e ? `<div style="display: flex; flex-wrap: wrap; gap: 16px">${(await Promise.all(
    e.map((n) => !n.image || !n.image.url ? "" : n.image.url)
  )).map((n) => `<img src="${n}" style="height: 400px" />`).join("")}</div>` : "";
}
function T0(e) {
  let t = 0;
  for (let n = 0; n < e.length; n++)
    t = e[t] <= e[n] ? t : n;
  return t;
}
function B0(e, {
  getWidth: t,
  setWidth: n,
  getHeight: i,
  setHeight: l,
  getPadding: r,
  setX: o,
  setY: u,
  getChildren: s
}, { cols: a, gap: f }) {
  const [c, h, _, d] = r(e), v = s(e), A = v.length, [w, E] = Array.isArray(f) ? f : [f, f];
  if (A) {
    const p = (t(e) - w * (a - 1) - (d + h)) / a;
    v.forEach((g) => {
      n(g, p);
    });
    const m = v.map((g) => i(g)), k = Array(a).fill(c);
    for (let g = 0; g < A; g++) {
      const T = v[g], S = T0(k);
      u(T, k[S]), o(T, d + (p + w) * S), k[S] += m[g] + E;
    }
    l(e, Math.max(...k) - E + _);
  } else
    l(e, c + _);
}
function fl(e) {
  let t, n = e[0], i = 1;
  for (; i < e.length; ) {
    const l = e[i], r = e[i + 1];
    if (i += 2, (l === "optionalAccess" || l === "optionalCall") && n == null)
      return;
    l === "access" || l === "optionalAccess" ? (t = n, n = r(n)) : (l === "call" || l === "optionalCall") && (n = r((...o) => n.call(t, ...o)), t = void 0);
  }
  return n;
}
const cl = (e) => e.nodeType == 1, Dn = Symbol(), Un = Symbol();
function C0(e, t) {
  let n, i, l = !1;
  function r() {
    l || (l = !0, requestAnimationFrame(() => {
      t(), e[Un] = e.offsetWidth, e[Dn] = e.offsetHeight, l = !1;
    }));
  }
  function o() {
    e && (n = new ResizeObserver((s) => {
      s.some((a) => {
        const f = a.target;
        return f[Un] !== f.offsetWidth || f[Dn] !== f.offsetHeight;
      }) && r();
    }), n.observe(e), Array.from(e.children).forEach((s) => {
      n.observe(s);
    }), i = new MutationObserver((s) => {
      s.forEach((a) => {
        a.addedNodes.forEach(
          (f) => cl(f) && n.observe(f)
        ), a.removedNodes.forEach(
          (f) => cl(f) && n.unobserve(f)
        );
      }), r();
    }), i.observe(e, { childList: !0, attributes: !1 }), r());
  }
  function u() {
    fl([n, "optionalAccess", (s) => s.disconnect, "call", (s) => s()]), fl([i, "optionalAccess", (s) => s.disconnect, "call", (s) => s()]);
  }
  return { layout: r, mount: o, unmount: u };
}
const I0 = (e, t) => C0(e, () => {
  B0(
    e,
    {
      getWidth: (n) => n.offsetWidth,
      setWidth: (n, i) => n.style.width = i + "px",
      getHeight: (n) => (n[Un] = n.offsetWidth, n[Dn] = n.offsetHeight),
      setHeight: (n, i) => n.style.height = i + "px",
      getPadding: (n) => {
        const i = getComputedStyle(n);
        return [
          parseInt(i.paddingTop),
          parseInt(i.paddingRight),
          parseInt(i.paddingBottom),
          parseInt(i.paddingLeft)
        ];
      },
      setX: (n, i) => n.style.left = i + "px",
      setY: (n, i) => n.style.top = i + "px",
      getChildren: (n) => Array.from(n.children)
    },
    t
  );
});
class P0 {
  constructor(t, n = {
    cols: 2,
    gap: 4
  }) {
    this._layout = I0(t, n), this._layout.mount();
  }
  unmount() {
    this._layout.unmount();
  }
  render() {
    this._layout.layout();
  }
}
const {
  SvelteComponent: L0,
  add_iframe_resize_listener: N0,
  add_render_callback: _r,
  append: X,
  assign: O0,
  attr: I,
  binding_callbacks: kn,
  bubble: M0,
  check_outros: xe,
  create_component: Ce,
  destroy_component: Ie,
  destroy_each: mr,
  detach: _e,
  element: K,
  empty: R0,
  ensure_array_like: Vt,
  get_spread_object: D0,
  get_spread_update: U0,
  globals: G0,
  group_outros: ze,
  init: F0,
  insert: me,
  listen: qt,
  mount_component: Pe,
  noop: j0,
  run_all: V0,
  safe_not_equal: q0,
  set_data: dr,
  set_style: Re,
  space: ye,
  src_url_equal: xt,
  text: br,
  toggle_class: oe,
  transition_in: M,
  transition_out: G
} = window.__gradio__svelte__internal, { window: Gn } = G0, { createEventDispatcher: x0, onDestroy: z0, tick: X0 } = window.__gradio__svelte__internal;
function hl(e, t, n) {
  const i = e.slice();
  return i[57] = t[n], i[59] = n, i;
}
function _l(e, t, n) {
  const i = e.slice();
  return i[57] = t[n], i[60] = t, i[59] = n, i;
}
function ml(e) {
  let t, n;
  return t = new co({
    props: {
      show_label: (
        /*show_label*/
        e[2]
      ),
      Icon: Al,
      label: (
        /*label*/
        e[4] || "Gallery"
      )
    }
  }), {
    c() {
      Ce(t.$$.fragment);
    },
    m(i, l) {
      Pe(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l[0] & /*show_label*/
      4 && (r.show_label = /*show_label*/
      i[2]), l[0] & /*label*/
      16 && (r.label = /*label*/
      i[4] || "Gallery"), t.$set(r);
    },
    i(i) {
      n || (M(t.$$.fragment, i), n = !0);
    },
    o(i) {
      G(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Ie(t, i);
    }
  };
}
function Z0(e) {
  let t, n, i, l, r, o, u, s, a, f, c, h = (
    /*selected_image*/
    e[23] && /*allow_preview*/
    e[9] && dl(e)
  ), _ = (
    /*show_share_button*/
    e[10] && vl(e)
  ), d = Vt(
    /*resolved_value*/
    e[18]
  ), v = [];
  for (let m = 0; m < d.length; m += 1)
    v[m] = wl(hl(e, d, m));
  const A = (m) => G(v[m], 1, 1, () => {
    v[m] = null;
  }), w = [J0, Q0], E = [];
  function p(m, k) {
    return (
      /*pending*/
      m[5] ? 0 : 1
    );
  }
  return s = p(e), a = E[s] = w[s](e), {
    c() {
      h && h.c(), t = ye(), n = K("div"), i = K("div"), _ && _.c(), l = ye(), r = K("div");
      for (let m = 0; m < v.length; m += 1)
        v[m].c();
      o = ye(), u = K("p"), a.c(), I(r, "class", "waterfall svelte-yk2d08"), I(i, "class", "grid-container svelte-yk2d08"), Re(
        i,
        "--object-fit",
        /*object_fit*/
        e[1]
      ), Re(
        i,
        "min-height",
        /*height*/
        e[8] + "px"
      ), oe(
        i,
        "pt-6",
        /*show_label*/
        e[2]
      ), I(u, "class", "loading-line svelte-yk2d08"), oe(u, "visible", !/*selected_image*/
      (e[23] && /*allow_preview*/
      e[9]) && /*has_more*/
      e[3]), I(n, "class", "grid-wrap svelte-yk2d08"), Re(
        n,
        "height",
        /*height*/
        e[8] + "px"
      ), _r(() => (
        /*div2_elementresize_handler*/
        e[51].call(n)
      )), oe(n, "fixed-height", !/*height*/
      e[8] || /*height*/
      e[8] === "auto");
    },
    m(m, k) {
      h && h.m(m, k), me(m, t, k), me(m, n, k), X(n, i), _ && _.m(i, null), X(i, l), X(i, r);
      for (let g = 0; g < v.length; g += 1)
        v[g] && v[g].m(r, null);
      e[49](r), X(n, o), X(n, u), E[s].m(u, null), f = N0(
        n,
        /*div2_elementresize_handler*/
        e[51].bind(n)
      ), c = !0;
    },
    p(m, k) {
      if (/*selected_image*/
      m[23] && /*allow_preview*/
      m[9] ? h ? (h.p(m, k), k[0] & /*selected_image, allow_preview*/
      8389120 && M(h, 1)) : (h = dl(m), h.c(), M(h, 1), h.m(t.parentNode, t)) : h && (ze(), G(h, 1, 1, () => {
        h = null;
      }), xe()), /*show_share_button*/
      m[10] ? _ ? (_.p(m, k), k[0] & /*show_share_button*/
      1024 && M(_, 1)) : (_ = vl(m), _.c(), M(_, 1), _.m(i, l)) : _ && (ze(), G(_, 1, 1, () => {
        _ = null;
      }), xe()), k[0] & /*resolved_value, selected_index, likeable, clickable, action_label, dispatch*/
      17045569) {
        d = Vt(
          /*resolved_value*/
          m[18]
        );
        let T;
        for (T = 0; T < d.length; T += 1) {
          const S = hl(m, d, T);
          v[T] ? (v[T].p(S, k), M(v[T], 1)) : (v[T] = wl(S), v[T].c(), M(v[T], 1), v[T].m(r, null));
        }
        for (ze(), T = d.length; T < v.length; T += 1)
          A(T);
        xe();
      }
      (!c || k[0] & /*object_fit*/
      2) && Re(
        i,
        "--object-fit",
        /*object_fit*/
        m[1]
      ), (!c || k[0] & /*height*/
      256) && Re(
        i,
        "min-height",
        /*height*/
        m[8] + "px"
      ), (!c || k[0] & /*show_label*/
      4) && oe(
        i,
        "pt-6",
        /*show_label*/
        m[2]
      );
      let g = s;
      s = p(m), s === g ? E[s].p(m, k) : (ze(), G(E[g], 1, 1, () => {
        E[g] = null;
      }), xe(), a = E[s], a ? a.p(m, k) : (a = E[s] = w[s](m), a.c()), M(a, 1), a.m(u, null)), (!c || k[0] & /*selected_image, allow_preview, has_more*/
      8389128) && oe(u, "visible", !/*selected_image*/
      (m[23] && /*allow_preview*/
      m[9]) && /*has_more*/
      m[3]), (!c || k[0] & /*height*/
      256) && Re(
        n,
        "height",
        /*height*/
        m[8] + "px"
      ), (!c || k[0] & /*height*/
      256) && oe(n, "fixed-height", !/*height*/
      m[8] || /*height*/
      m[8] === "auto");
    },
    i(m) {
      if (!c) {
        M(h), M(_);
        for (let k = 0; k < d.length; k += 1)
          M(v[k]);
        M(a), c = !0;
      }
    },
    o(m) {
      G(h), G(_), v = v.filter(Boolean);
      for (let k = 0; k < v.length; k += 1)
        G(v[k]);
      G(a), c = !1;
    },
    d(m) {
      m && (_e(t), _e(n)), h && h.d(m), _ && _.d(), mr(v, m), e[49](null), E[s].d(), f();
    }
  };
}
function W0(e) {
  let t, n;
  return t = new xo({
    props: {
      unpadded_box: !0,
      size: "large",
      $$slots: { default: [K0] },
      $$scope: { ctx: e }
    }
  }), {
    c() {
      Ce(t.$$.fragment);
    },
    m(i, l) {
      Pe(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l[1] & /*$$scope*/
      1073741824 && (r.$$scope = { dirty: l, ctx: i }), t.$set(r);
    },
    i(i) {
      n || (M(t.$$.fragment, i), n = !0);
    },
    o(i) {
      G(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Ie(t, i);
    }
  };
}
function dl(e) {
  var k;
  let t, n, i, l, r, o, u, s, a, f, c, h, _, d, v, A, w = (
    /*show_download_button*/
    e[13] && bl(e)
  );
  l = new o0({
    props: { i18n: (
      /*i18n*/
      e[14]
    ), absolute: !1 }
  }), l.$on(
    "clear",
    /*clear_handler*/
    e[39]
  );
  let E = (
    /*selected_image*/
    ((k = e[23]) == null ? void 0 : k.caption) && gl(e)
  ), p = Vt(
    /*resolved_value*/
    e[18]
  ), m = [];
  for (let g = 0; g < p.length; g += 1)
    m[g] = pl(_l(e, p, g));
  return {
    c() {
      t = K("button"), n = K("div"), w && w.c(), i = ye(), Ce(l.$$.fragment), r = ye(), o = K("button"), u = K("img"), c = ye(), E && E.c(), h = ye(), _ = K("div");
      for (let g = 0; g < m.length; g += 1)
        m[g].c();
      I(n, "class", "icon-buttons svelte-yk2d08"), I(u, "data-testid", "detailed-image"), xt(u.src, s = /*selected_image*/
      e[23].image.url) || I(u, "src", s), I(u, "alt", a = /*selected_image*/
      e[23].caption || ""), I(u, "title", f = /*selected_image*/
      e[23].caption || null), I(u, "loading", "lazy"), I(u, "class", "svelte-yk2d08"), oe(u, "with-caption", !!/*selected_image*/
      e[23].caption), I(o, "class", "image-button svelte-yk2d08"), Re(o, "height", "calc(100% - " + /*selected_image*/
      (e[23].caption ? "80px" : "60px") + ")"), I(o, "aria-label", "detailed view of selected image"), I(_, "class", "thumbnails scroll-hide svelte-yk2d08"), I(_, "data-testid", "container_el"), I(t, "class", "preview svelte-yk2d08");
    },
    m(g, T) {
      me(g, t, T), X(t, n), w && w.m(n, null), X(n, i), Pe(l, n, null), X(t, r), X(t, o), X(o, u), X(t, c), E && E.m(t, null), X(t, h), X(t, _);
      for (let S = 0; S < m.length; S += 1)
        m[S] && m[S].m(_, null);
      e[43](_), d = !0, v || (A = [
        qt(
          o,
          "click",
          /*click_handler_1*/
          e[40]
        ),
        qt(
          t,
          "keydown",
          /*on_keydown*/
          e[26]
        )
      ], v = !0);
    },
    p(g, T) {
      var z;
      /*show_download_button*/
      g[13] ? w ? (w.p(g, T), T[0] & /*show_download_button*/
      8192 && M(w, 1)) : (w = bl(g), w.c(), M(w, 1), w.m(n, i)) : w && (ze(), G(w, 1, 1, () => {
        w = null;
      }), xe());
      const S = {};
      if (T[0] & /*i18n*/
      16384 && (S.i18n = /*i18n*/
      g[14]), l.$set(S), (!d || T[0] & /*selected_image*/
      8388608 && !xt(u.src, s = /*selected_image*/
      g[23].image.url)) && I(u, "src", s), (!d || T[0] & /*selected_image*/
      8388608 && a !== (a = /*selected_image*/
      g[23].caption || "")) && I(u, "alt", a), (!d || T[0] & /*selected_image*/
      8388608 && f !== (f = /*selected_image*/
      g[23].caption || null)) && I(u, "title", f), (!d || T[0] & /*selected_image*/
      8388608) && oe(u, "with-caption", !!/*selected_image*/
      g[23].caption), (!d || T[0] & /*selected_image*/
      8388608) && Re(o, "height", "calc(100% - " + /*selected_image*/
      (g[23].caption ? "80px" : "60px") + ")"), /*selected_image*/
      (z = g[23]) != null && z.caption ? E ? E.p(g, T) : (E = gl(g), E.c(), E.m(t, h)) : E && (E.d(1), E = null), T[0] & /*resolved_value, el, selected_index*/
      2359297) {
        p = Vt(
          /*resolved_value*/
          g[18]
        );
        let R;
        for (R = 0; R < p.length; R += 1) {
          const q = _l(g, p, R);
          m[R] ? m[R].p(q, T) : (m[R] = pl(q), m[R].c(), m[R].m(_, null));
        }
        for (; R < m.length; R += 1)
          m[R].d(1);
        m.length = p.length;
      }
    },
    i(g) {
      d || (M(w), M(l.$$.fragment, g), d = !0);
    },
    o(g) {
      G(w), G(l.$$.fragment, g), d = !1;
    },
    d(g) {
      g && _e(t), w && w.d(), Ie(l), E && E.d(), mr(m, g), e[43](null), v = !1, V0(A);
    }
  };
}
function bl(e) {
  let t, n, i;
  return n = new We({
    props: {
      show_label: !0,
      label: (
        /*i18n*/
        e[14]("common.download")
      ),
      Icon: _s
    }
  }), n.$on(
    "click",
    /*click_handler*/
    e[38]
  ), {
    c() {
      t = K("div"), Ce(n.$$.fragment), I(t, "class", "download-button-container svelte-yk2d08");
    },
    m(l, r) {
      me(l, t, r), Pe(n, t, null), i = !0;
    },
    p(l, r) {
      const o = {};
      r[0] & /*i18n*/
      16384 && (o.label = /*i18n*/
      l[14]("common.download")), n.$set(o);
    },
    i(l) {
      i || (M(n.$$.fragment, l), i = !0);
    },
    o(l) {
      G(n.$$.fragment, l), i = !1;
    },
    d(l) {
      l && _e(t), Ie(n);
    }
  };
}
function gl(e) {
  let t, n = (
    /*selected_image*/
    e[23].caption + ""
  ), i;
  return {
    c() {
      t = K("caption"), i = br(n), I(t, "class", "caption svelte-yk2d08");
    },
    m(l, r) {
      me(l, t, r), X(t, i);
    },
    p(l, r) {
      r[0] & /*selected_image*/
      8388608 && n !== (n = /*selected_image*/
      l[23].caption + "") && dr(i, n);
    },
    d(l) {
      l && _e(t);
    }
  };
}
function pl(e) {
  let t, n, i, l, r, o, u = (
    /*i*/
    e[59]
  ), s, a;
  const f = () => (
    /*button_binding*/
    e[41](t, u)
  ), c = () => (
    /*button_binding*/
    e[41](null, u)
  );
  function h() {
    return (
      /*click_handler_2*/
      e[42](
        /*i*/
        e[59]
      )
    );
  }
  return {
    c() {
      t = K("button"), n = K("img"), r = ye(), xt(n.src, i = /*entry*/
      e[57].image.url) || I(n, "src", i), I(n, "title", l = /*entry*/
      e[57].caption || null), I(n, "data-testid", "thumbnail " + /*i*/
      (e[59] + 1)), I(n, "alt", ""), I(n, "loading", "lazy"), I(n, "class", "svelte-yk2d08"), I(t, "class", "thumbnail-item thumbnail-small svelte-yk2d08"), I(t, "aria-label", o = "Thumbnail " + /*i*/
      (e[59] + 1) + " of " + /*resolved_value*/
      e[18].length), oe(
        t,
        "selected",
        /*selected_index*/
        e[0] === /*i*/
        e[59]
      );
    },
    m(_, d) {
      me(_, t, d), X(t, n), X(t, r), f(), s || (a = qt(t, "click", h), s = !0);
    },
    p(_, d) {
      e = _, d[0] & /*resolved_value*/
      262144 && !xt(n.src, i = /*entry*/
      e[57].image.url) && I(n, "src", i), d[0] & /*resolved_value*/
      262144 && l !== (l = /*entry*/
      e[57].caption || null) && I(n, "title", l), d[0] & /*resolved_value*/
      262144 && o !== (o = "Thumbnail " + /*i*/
      (e[59] + 1) + " of " + /*resolved_value*/
      e[18].length) && I(t, "aria-label", o), u !== /*i*/
      e[59] && (c(), u = /*i*/
      e[59], f()), d[0] & /*selected_index*/
      1 && oe(
        t,
        "selected",
        /*selected_index*/
        e[0] === /*i*/
        e[59]
      );
    },
    d(_) {
      _ && _e(t), c(), s = !1, a();
    }
  };
}
function vl(e) {
  let t, n, i;
  return n = new na({
    props: {
      i18n: (
        /*i18n*/
        e[14]
      ),
      value: (
        /*resolved_value*/
        e[18]
      ),
      formatter: A0
    }
  }), n.$on(
    "share",
    /*share_handler*/
    e[44]
  ), n.$on(
    "error",
    /*error_handler*/
    e[45]
  ), {
    c() {
      t = K("div"), Ce(n.$$.fragment), I(t, "class", "icon-button svelte-yk2d08");
    },
    m(l, r) {
      me(l, t, r), Pe(n, t, null), i = !0;
    },
    p(l, r) {
      const o = {};
      r[0] & /*i18n*/
      16384 && (o.i18n = /*i18n*/
      l[14]), r[0] & /*resolved_value*/
      262144 && (o.value = /*resolved_value*/
      l[18]), n.$set(o);
    },
    i(l) {
      i || (M(n.$$.fragment, l), i = !0);
    },
    o(l) {
      G(n.$$.fragment, l), i = !1;
    },
    d(l) {
      l && _e(t), Ie(n);
    }
  };
}
function wl(e) {
  let t, n, i, l, r;
  function o() {
    return (
      /*click_handler_3*/
      e[46](
        /*i*/
        e[59]
      )
    );
  }
  function u() {
    return (
      /*label_click_handler*/
      e[47](
        /*i*/
        e[59],
        /*entry*/
        e[57]
      )
    );
  }
  function s(...a) {
    return (
      /*like_handler*/
      e[48](
        /*i*/
        e[59],
        /*entry*/
        e[57],
        ...a
      )
    );
  }
  return n = new H0({
    props: {
      likeable: (
        /*likeable*/
        e[11]
      ),
      clickable: (
        /*clickable*/
        e[12]
      ),
      value: (
        /*entry*/
        e[57]
      ),
      action_label: (
        /*action_label*/
        e[6]
      )
    }
  }), n.$on("click", o), n.$on("label_click", u), n.$on("like", s), {
    c() {
      t = K("div"), Ce(n.$$.fragment), i = ye(), I(t, "class", "thumbnail-item thumbnail-lg svelte-yk2d08"), I(t, "aria-label", l = "Thumbnail " + /*i*/
      (e[59] + 1) + " of " + /*resolved_value*/
      e[18].length), oe(
        t,
        "selected",
        /*selected_index*/
        e[0] === /*i*/
        e[59]
      );
    },
    m(a, f) {
      me(a, t, f), Pe(n, t, null), X(t, i), r = !0;
    },
    p(a, f) {
      e = a;
      const c = {};
      f[0] & /*likeable*/
      2048 && (c.likeable = /*likeable*/
      e[11]), f[0] & /*clickable*/
      4096 && (c.clickable = /*clickable*/
      e[12]), f[0] & /*resolved_value*/
      262144 && (c.value = /*entry*/
      e[57]), f[0] & /*action_label*/
      64 && (c.action_label = /*action_label*/
      e[6]), n.$set(c), (!r || f[0] & /*resolved_value*/
      262144 && l !== (l = "Thumbnail " + /*i*/
      (e[59] + 1) + " of " + /*resolved_value*/
      e[18].length)) && I(t, "aria-label", l), (!r || f[0] & /*selected_index*/
      1) && oe(
        t,
        "selected",
        /*selected_index*/
        e[0] === /*i*/
        e[59]
      );
    },
    i(a) {
      r || (M(n.$$.fragment, a), r = !0);
    },
    o(a) {
      G(n.$$.fragment, a), r = !1;
    },
    d(a) {
      a && _e(t), Ie(n);
    }
  };
}
function Q0(e) {
  let t, n;
  const i = [
    /*load_more_button_props*/
    e[15]
  ];
  let l = {
    $$slots: { default: [Y0] },
    $$scope: { ctx: e }
  };
  for (let r = 0; r < i.length; r += 1)
    l = O0(l, i[r]);
  return t = new ou({ props: l }), t.$on(
    "click",
    /*click_handler_4*/
    e[50]
  ), {
    c() {
      Ce(t.$$.fragment);
    },
    m(r, o) {
      Pe(t, r, o), n = !0;
    },
    p(r, o) {
      const u = o[0] & /*load_more_button_props*/
      32768 ? U0(i, [D0(
        /*load_more_button_props*/
        r[15]
      )]) : {};
      o[0] & /*i18n, load_more_button_props*/
      49152 | o[1] & /*$$scope*/
      1073741824 && (u.$$scope = { dirty: o, ctx: r }), t.$set(u);
    },
    i(r) {
      n || (M(t.$$.fragment, r), n = !0);
    },
    o(r) {
      G(t.$$.fragment, r), n = !1;
    },
    d(r) {
      Ie(t, r);
    }
  };
}
function J0(e) {
  let t, n;
  return t = new Il({ props: { margin: !1 } }), {
    c() {
      Ce(t.$$.fragment);
    },
    m(i, l) {
      Pe(t, i, l), n = !0;
    },
    p: j0,
    i(i) {
      n || (M(t.$$.fragment, i), n = !0);
    },
    o(i) {
      G(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Ie(t, i);
    }
  };
}
function Y0(e) {
  let t = (
    /*i18n*/
    e[14](
      /*load_more_button_props*/
      e[15].value || /*load_more_button_props*/
      e[15].label || "Load More"
    ) + ""
  ), n;
  return {
    c() {
      n = br(t);
    },
    m(i, l) {
      me(i, n, l);
    },
    p(i, l) {
      l[0] & /*i18n, load_more_button_props*/
      49152 && t !== (t = /*i18n*/
      i[14](
        /*load_more_button_props*/
        i[15].value || /*load_more_button_props*/
        i[15].label || "Load More"
      ) + "") && dr(n, t);
    },
    d(i) {
      i && _e(n);
    }
  };
}
function K0(e) {
  let t, n;
  return t = new Al({}), {
    c() {
      Ce(t.$$.fragment);
    },
    m(i, l) {
      Pe(t, i, l), n = !0;
    },
    i(i) {
      n || (M(t.$$.fragment, i), n = !0);
    },
    o(i) {
      G(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Ie(t, i);
    }
  };
}
function $0(e) {
  let t, n, i, l, r, o, u;
  _r(
    /*onwindowresize*/
    e[37]
  );
  let s = (
    /*show_label*/
    e[2] && ml(e)
  );
  const a = [W0, Z0], f = [];
  function c(h, _) {
    return !/*value*/
    h[7] || !/*resolved_value*/
    h[18] || /*resolved_value*/
    h[18].length === 0 ? 0 : 1;
  }
  return n = c(e), i = f[n] = a[n](e), {
    c() {
      s && s.c(), t = ye(), i.c(), l = R0();
    },
    m(h, _) {
      s && s.m(h, _), me(h, t, _), f[n].m(h, _), me(h, l, _), r = !0, o || (u = qt(
        Gn,
        "resize",
        /*onwindowresize*/
        e[37]
      ), o = !0);
    },
    p(h, _) {
      /*show_label*/
      h[2] ? s ? (s.p(h, _), _[0] & /*show_label*/
      4 && M(s, 1)) : (s = ml(h), s.c(), M(s, 1), s.m(t.parentNode, t)) : s && (ze(), G(s, 1, 1, () => {
        s = null;
      }), xe());
      let d = n;
      n = c(h), n === d ? f[n].p(h, _) : (ze(), G(f[d], 1, 1, () => {
        f[d] = null;
      }), xe(), i = f[n], i ? i.p(h, _) : (i = f[n] = a[n](h), i.c()), M(i, 1), i.m(l.parentNode, l));
    },
    i(h) {
      r || (M(s), M(i), r = !0);
    },
    o(h) {
      G(s), G(i), r = !1;
    },
    d(h) {
      h && (_e(t), _e(l)), s && s.d(h), f[n].d(h), o = !1, u();
    }
  };
}
function je(e, t) {
  return e ?? t();
}
function He(e) {
  let t, n = e[0], i = 1;
  for (; i < e.length; ) {
    const l = e[i], r = e[i + 1];
    if (i += 2, (l === "optionalAccess" || l === "optionalCall") && n == null)
      return;
    l === "access" || l === "optionalAccess" ? (t = n, n = r(n)) : (l === "call" || l === "optionalCall") && (n = r((...o) => n.call(t, ...o)), t = void 0);
  }
  return n;
}
async function ec(e, t) {
  let n;
  try {
    n = await fetch(e);
  } catch (o) {
    if (o instanceof TypeError) {
      window.open(e, "_blank", "noreferrer");
      return;
    }
    throw o;
  }
  const i = await n.blob(), l = URL.createObjectURL(i), r = document.createElement("a");
  r.href = l, r.download = t, r.click(), URL.revokeObjectURL(l);
}
function tc(e, t, n) {
  let i, l, r, { object_fit: o = "cover" } = t, { show_label: u = !0 } = t, { has_more: s = !1 } = t, { label: a } = t, { pending: f } = t, { action_label: c } = t, { value: h = null } = t, { columns: _ = [2] } = t, { height: d = "auto" } = t, { preview: v } = t, { root: A } = t, { proxy_url: w } = t, { allow_preview: E = !0 } = t, { show_share_button: p = !1 } = t, { likeable: m } = t, { clickable: k } = t, { show_download_button: g = !1 } = t, { i18n: T } = t, { selected_index: S = null } = t, { gap: z = 8 } = t, { load_more_button_props: R = {} } = t, q, x = [], W, ee = 0, te = 0, Ee = 0;
  const de = x0();
  let be = !0, ke = null, Q = null, Ge = h;
  S == null && v && He([h, "optionalAccess", (b) => b.length]) && (S = 0);
  let Fe = S;
  function H(b) {
    const V = b.target, ae = b.clientX, $t = V.offsetWidth / 2;
    ae < $t ? n(0, S = i) : n(0, S = l);
  }
  function Kt(b) {
    switch (b.code) {
      case "Escape":
        b.preventDefault(), n(0, S = null);
        break;
      case "ArrowLeft":
        b.preventDefault(), n(0, S = i);
        break;
      case "ArrowRight":
        b.preventDefault(), n(0, S = l);
        break;
    }
  }
  let y = [], Le;
  async function gr(b) {
    if (typeof b != "number" || (await X0(), y[b] === void 0))
      return;
    He([
      y,
      "access",
      (ct) => ct[b],
      "optionalAccess",
      (ct) => ct.focus,
      "call",
      (ct) => ct()
    ]);
    const { left: V, width: ae } = Le.getBoundingClientRect(), { left: Jn, width: $t } = y[b].getBoundingClientRect(), Yn = Jn - V + $t / 2 - ae / 2 + Le.scrollLeft;
    Le && typeof Le.scrollTo == "function" && Le.scrollTo({
      left: Yn < 0 ? 0 : Yn,
      behavior: "smooth"
    });
  }
  function pr() {
    He([ke, "optionalAccess", (b) => b.unmount, "call", (b) => b()]), ke = new P0(q, { cols: W, gap: z });
  }
  z0(() => {
    He([ke, "optionalAccess", (b) => b.unmount, "call", (b) => b()]);
  });
  function vr() {
    n(20, te = Gn.innerHeight), n(17, Ee = Gn.innerWidth);
  }
  const wr = () => {
    const b = r == null ? void 0 : r.image;
    if (!b)
      return;
    const { url: V, orig_name: ae } = b;
    V && ec(V, ae ?? "image");
  }, yr = () => n(0, S = null), Er = (b) => H(b);
  function kr(b, V) {
    kn[b ? "unshift" : "push"](() => {
      y[V] = b, n(21, y);
    });
  }
  const Hr = (b) => n(0, S = b);
  function Sr(b) {
    kn[b ? "unshift" : "push"](() => {
      Le = b, n(22, Le);
    });
  }
  const Ar = (b) => {
    S0(b.detail.description);
  };
  function Tr(b) {
    M0.call(this, e, b);
  }
  const Br = (b) => n(0, S = b), Cr = (b, V) => {
    de("click", { index: b, value: V });
  }, Ir = (b, V, ae) => {
    de("like", { index: b, value: V, liked: ae.detail });
  };
  function Pr(b) {
    kn[b ? "unshift" : "push"](() => {
      q = b, n(16, q);
    });
  }
  const Lr = () => {
    de("load_more");
  };
  function Nr() {
    ee = this.clientHeight, n(19, ee);
  }
  return e.$$set = (b) => {
    "object_fit" in b && n(1, o = b.object_fit), "show_label" in b && n(2, u = b.show_label), "has_more" in b && n(3, s = b.has_more), "label" in b && n(4, a = b.label), "pending" in b && n(5, f = b.pending), "action_label" in b && n(6, c = b.action_label), "value" in b && n(7, h = b.value), "columns" in b && n(27, _ = b.columns), "height" in b && n(8, d = b.height), "preview" in b && n(28, v = b.preview), "root" in b && n(29, A = b.root), "proxy_url" in b && n(30, w = b.proxy_url), "allow_preview" in b && n(9, E = b.allow_preview), "show_share_button" in b && n(10, p = b.show_share_button), "likeable" in b && n(11, m = b.likeable), "clickable" in b && n(12, k = b.clickable), "show_download_button" in b && n(13, g = b.show_download_button), "i18n" in b && n(14, T = b.i18n), "selected_index" in b && n(0, S = b.selected_index), "gap" in b && n(31, z = b.gap), "load_more_button_props" in b && n(15, R = b.load_more_button_props);
  }, e.$$.update = () => {
    if (e.$$.dirty[0] & /*columns*/
    134217728)
      if (typeof _ == "object" && _ !== null)
        if (Array.isArray(_)) {
          const b = _.length;
          n(32, x = En.map((V, ae) => [
            V.width,
            je(_[ae], () => _[b - 1])
          ]));
        } else {
          let b = 0;
          n(32, x = En.map((V) => {
            const ae = _[V.key];
            return b = je(ae, () => b), [V.width, b];
          }));
        }
      else
        n(32, x = En.map((b) => [b.width, _]));
    if (e.$$.dirty[0] & /*window_width*/
    131072 | e.$$.dirty[1] & /*breakpointColumns*/
    2) {
      for (const [b, V] of [...x].reverse())
        if (Ee >= b) {
          n(33, W = V);
          break;
        }
    }
    e.$$.dirty[0] & /*value*/
    128 | e.$$.dirty[1] & /*was_reset*/
    8 && n(34, be = h == null || h.length === 0 ? !0 : be), e.$$.dirty[0] & /*value, root, proxy_url*/
    1610612864 && n(18, Q = h == null ? null : h.map((b) => (b.image = Fl(b.image, A, w), b))), e.$$.dirty[0] & /*value, preview, selected_index*/
    268435585 | e.$$.dirty[1] & /*prev_value, was_reset*/
    24 && (mt(Ge, h) || (be ? (n(0, S = v && He([h, "optionalAccess", (b) => b.length]) ? 0 : null), n(34, be = !1), ke = null) : n(
      0,
      S = S != null && h != null && S < h.length ? S : null
    ), de("change"), n(35, Ge = h))), e.$$.dirty[0] & /*selected_index, resolved_value*/
    262145 && (i = (je(S, () => 0) + je(He([Q, "optionalAccess", (b) => b.length]), () => 0) - 1) % je(He([Q, "optionalAccess", (b) => b.length]), () => 0)), e.$$.dirty[0] & /*selected_index, resolved_value*/
    262145 && (l = (je(S, () => 0) + 1) % je(He([Q, "optionalAccess", (b) => b.length]), () => 0)), e.$$.dirty[0] & /*selected_index, resolved_value*/
    262145 | e.$$.dirty[1] & /*old_selected_index*/
    32 && S !== Fe && (n(36, Fe = S), S !== null && de("select", {
      index: S,
      value: He([Q, "optionalAccess", (b) => b[S]])
    })), e.$$.dirty[0] & /*allow_preview, selected_index*/
    513 && E && gr(S), e.$$.dirty[0] & /*waterfall_grid_el*/
    65536 | e.$$.dirty[1] & /*cols*/
    4 && q && pr(), e.$$.dirty[0] & /*selected_index, resolved_value*/
    262145 && n(23, r = S != null && Q != null ? Q[S] : null);
  }, [
    S,
    o,
    u,
    s,
    a,
    f,
    c,
    h,
    d,
    E,
    p,
    m,
    k,
    g,
    T,
    R,
    q,
    Ee,
    Q,
    ee,
    te,
    y,
    Le,
    r,
    de,
    H,
    Kt,
    _,
    v,
    A,
    w,
    z,
    x,
    W,
    be,
    Ge,
    Fe,
    vr,
    wr,
    yr,
    Er,
    kr,
    Hr,
    Sr,
    Ar,
    Tr,
    Br,
    Cr,
    Ir,
    Pr,
    Lr,
    Nr
  ];
}
class nc extends L0 {
  constructor(t) {
    super(), F0(
      this,
      t,
      tc,
      $0,
      q0,
      {
        object_fit: 1,
        show_label: 2,
        has_more: 3,
        label: 4,
        pending: 5,
        action_label: 6,
        value: 7,
        columns: 27,
        height: 8,
        preview: 28,
        root: 29,
        proxy_url: 30,
        allow_preview: 9,
        show_share_button: 10,
        likeable: 11,
        clickable: 12,
        show_download_button: 13,
        i18n: 14,
        selected_index: 0,
        gap: 31,
        load_more_button_props: 15
      },
      null,
      [-1, -1]
    );
  }
}
const {
  SvelteComponent: ic,
  add_flush_callback: lc,
  assign: rc,
  bind: oc,
  binding_callbacks: sc,
  check_outros: ac,
  create_component: Zn,
  destroy_component: Wn,
  detach: uc,
  get_spread_object: fc,
  get_spread_update: cc,
  group_outros: hc,
  init: _c,
  insert: mc,
  mount_component: Qn,
  safe_not_equal: dc,
  space: bc,
  transition_in: et,
  transition_out: bt
} = window.__gradio__svelte__internal, { createEventDispatcher: gc } = window.__gradio__svelte__internal;
function yl(e) {
  let t, n;
  const i = [
    {
      autoscroll: (
        /*gradio*/
        e[25].autoscroll
      )
    },
    { i18n: (
      /*gradio*/
      e[25].i18n
    ) },
    /*loading_status*/
    e[1],
    {
      show_progress: (
        /*loading_status*/
        e[1].show_progress === "hidden" ? "hidden" : (
          /*has_more*/
          e[3] ? "minimal" : (
            /*loading_status*/
            e[1].show_progress
          )
        )
      )
    }
  ];
  let l = {};
  for (let r = 0; r < i.length; r += 1)
    l = rc(l, i[r]);
  return t = new za({ props: l }), {
    c() {
      Zn(t.$$.fragment);
    },
    m(r, o) {
      Qn(t, r, o), n = !0;
    },
    p(r, o) {
      const u = o[0] & /*gradio, loading_status, has_more*/
      33554442 ? cc(i, [
        o[0] & /*gradio*/
        33554432 && {
          autoscroll: (
            /*gradio*/
            r[25].autoscroll
          )
        },
        o[0] & /*gradio*/
        33554432 && { i18n: (
          /*gradio*/
          r[25].i18n
        ) },
        o[0] & /*loading_status*/
        2 && fc(
          /*loading_status*/
          r[1]
        ),
        o[0] & /*loading_status, has_more*/
        10 && {
          show_progress: (
            /*loading_status*/
            r[1].show_progress === "hidden" ? "hidden" : (
              /*has_more*/
              r[3] ? "minimal" : (
                /*loading_status*/
                r[1].show_progress
              )
            )
          )
        }
      ]) : {};
      t.$set(u);
    },
    i(r) {
      n || (et(t.$$.fragment, r), n = !0);
    },
    o(r) {
      bt(t.$$.fragment, r), n = !1;
    },
    d(r) {
      Wn(t, r);
    }
  };
}
function pc(e) {
  var s;
  let t, n, i, l, r = (
    /*loading_status*/
    e[1] && yl(e)
  );
  function o(a) {
    e[29](a);
  }
  let u = {
    pending: (
      /*loading_status*/
      ((s = e[1]) == null ? void 0 : s.status) === "pending"
    ),
    likeable: (
      /*likeable*/
      e[10]
    ),
    clickable: (
      /*clickable*/
      e[11]
    ),
    label: (
      /*label*/
      e[4]
    ),
    action_label: (
      /*action_label*/
      e[5]
    ),
    value: (
      /*value*/
      e[9]
    ),
    root: (
      /*root*/
      e[23]
    ),
    proxy_url: (
      /*proxy_url*/
      e[24]
    ),
    show_label: (
      /*show_label*/
      e[2]
    ),
    object_fit: (
      /*object_fit*/
      e[21]
    ),
    load_more_button_props: (
      /*_load_more_button_props*/
      e[26]
    ),
    has_more: (
      /*has_more*/
      e[3]
    ),
    columns: (
      /*columns*/
      e[15]
    ),
    height: (
      /*height*/
      e[17]
    ),
    preview: (
      /*preview*/
      e[18]
    ),
    gap: (
      /*gap*/
      e[16]
    ),
    allow_preview: (
      /*allow_preview*/
      e[19]
    ),
    show_share_button: (
      /*show_share_button*/
      e[20]
    ),
    show_download_button: (
      /*show_download_button*/
      e[22]
    ),
    i18n: (
      /*gradio*/
      e[25].i18n
    )
  };
  return (
    /*selected_index*/
    e[0] !== void 0 && (u.selected_index = /*selected_index*/
    e[0]), n = new nc({ props: u }), sc.push(() => oc(n, "selected_index", o)), n.$on(
      "click",
      /*click_handler*/
      e[30]
    ), n.$on(
      "change",
      /*change_handler*/
      e[31]
    ), n.$on(
      "like",
      /*like_handler*/
      e[32]
    ), n.$on(
      "select",
      /*select_handler*/
      e[33]
    ), n.$on(
      "share",
      /*share_handler*/
      e[34]
    ), n.$on(
      "error",
      /*error_handler*/
      e[35]
    ), n.$on(
      "load_more",
      /*load_more_handler*/
      e[36]
    ), {
      c() {
        r && r.c(), t = bc(), Zn(n.$$.fragment);
      },
      m(a, f) {
        r && r.m(a, f), mc(a, t, f), Qn(n, a, f), l = !0;
      },
      p(a, f) {
        var h;
        /*loading_status*/
        a[1] ? r ? (r.p(a, f), f[0] & /*loading_status*/
        2 && et(r, 1)) : (r = yl(a), r.c(), et(r, 1), r.m(t.parentNode, t)) : r && (hc(), bt(r, 1, 1, () => {
          r = null;
        }), ac());
        const c = {};
        f[0] & /*loading_status*/
        2 && (c.pending = /*loading_status*/
        ((h = a[1]) == null ? void 0 : h.status) === "pending"), f[0] & /*likeable*/
        1024 && (c.likeable = /*likeable*/
        a[10]), f[0] & /*clickable*/
        2048 && (c.clickable = /*clickable*/
        a[11]), f[0] & /*label*/
        16 && (c.label = /*label*/
        a[4]), f[0] & /*action_label*/
        32 && (c.action_label = /*action_label*/
        a[5]), f[0] & /*value*/
        512 && (c.value = /*value*/
        a[9]), f[0] & /*root*/
        8388608 && (c.root = /*root*/
        a[23]), f[0] & /*proxy_url*/
        16777216 && (c.proxy_url = /*proxy_url*/
        a[24]), f[0] & /*show_label*/
        4 && (c.show_label = /*show_label*/
        a[2]), f[0] & /*object_fit*/
        2097152 && (c.object_fit = /*object_fit*/
        a[21]), f[0] & /*_load_more_button_props*/
        67108864 && (c.load_more_button_props = /*_load_more_button_props*/
        a[26]), f[0] & /*has_more*/
        8 && (c.has_more = /*has_more*/
        a[3]), f[0] & /*columns*/
        32768 && (c.columns = /*columns*/
        a[15]), f[0] & /*height*/
        131072 && (c.height = /*height*/
        a[17]), f[0] & /*preview*/
        262144 && (c.preview = /*preview*/
        a[18]), f[0] & /*gap*/
        65536 && (c.gap = /*gap*/
        a[16]), f[0] & /*allow_preview*/
        524288 && (c.allow_preview = /*allow_preview*/
        a[19]), f[0] & /*show_share_button*/
        1048576 && (c.show_share_button = /*show_share_button*/
        a[20]), f[0] & /*show_download_button*/
        4194304 && (c.show_download_button = /*show_download_button*/
        a[22]), f[0] & /*gradio*/
        33554432 && (c.i18n = /*gradio*/
        a[25].i18n), !i && f[0] & /*selected_index*/
        1 && (i = !0, c.selected_index = /*selected_index*/
        a[0], lc(() => i = !1)), n.$set(c);
      },
      i(a) {
        l || (et(r), et(n.$$.fragment, a), l = !0);
      },
      o(a) {
        bt(r), bt(n.$$.fragment, a), l = !1;
      },
      d(a) {
        a && uc(t), r && r.d(a), Wn(n, a);
      }
    }
  );
}
function vc(e) {
  let t, n;
  return t = new Qr({
    props: {
      visible: (
        /*visible*/
        e[8]
      ),
      variant: "solid",
      padding: !1,
      elem_id: (
        /*elem_id*/
        e[6]
      ),
      elem_classes: (
        /*elem_classes*/
        e[7]
      ),
      container: (
        /*container*/
        e[12]
      ),
      scale: (
        /*scale*/
        e[13]
      ),
      min_width: (
        /*min_width*/
        e[14]
      ),
      allow_overflow: !1,
      $$slots: { default: [pc] },
      $$scope: { ctx: e }
    }
  }), {
    c() {
      Zn(t.$$.fragment);
    },
    m(i, l) {
      Qn(t, i, l), n = !0;
    },
    p(i, l) {
      const r = {};
      l[0] & /*visible*/
      256 && (r.visible = /*visible*/
      i[8]), l[0] & /*elem_id*/
      64 && (r.elem_id = /*elem_id*/
      i[6]), l[0] & /*elem_classes*/
      128 && (r.elem_classes = /*elem_classes*/
      i[7]), l[0] & /*container*/
      4096 && (r.container = /*container*/
      i[12]), l[0] & /*scale*/
      8192 && (r.scale = /*scale*/
      i[13]), l[0] & /*min_width*/
      16384 && (r.min_width = /*min_width*/
      i[14]), l[0] & /*loading_status, likeable, clickable, label, action_label, value, root, proxy_url, show_label, object_fit, _load_more_button_props, has_more, columns, height, preview, gap, allow_preview, show_share_button, show_download_button, gradio, selected_index*/
      134188607 | l[1] & /*$$scope*/
      128 && (r.$$scope = { dirty: l, ctx: i }), t.$set(r);
    },
    i(i) {
      n || (et(t.$$.fragment, i), n = !0);
    },
    o(i) {
      bt(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Wn(t, i);
    }
  };
}
function wc(e, t, n) {
  let { loading_status: i } = t, { show_label: l } = t, { has_more: r } = t, { label: o } = t, { action_label: u } = t, { elem_id: s = "" } = t, { elem_classes: a = [] } = t, { visible: f = !0 } = t, { value: c = null } = t, { likeable: h } = t, { clickable: _ } = t, { container: d = !0 } = t, { scale: v = null } = t, { min_width: A = void 0 } = t, { columns: w = [2] } = t, { gap: E = 8 } = t, { height: p = "auto" } = t, { preview: m } = t, { allow_preview: k = !0 } = t, { selected_index: g = null } = t, { show_share_button: T = !1 } = t, { object_fit: S = "cover" } = t, { show_download_button: z = !1 } = t, { root: R } = t, { proxy_url: q } = t, { gradio: x } = t, { load_more_button_props: W = {} } = t, ee = {};
  const te = gc(), Ee = (y) => {
    x.dispatch("like", y);
  };
  function de(y) {
    g = y, n(0, g);
  }
  const be = (y) => x.dispatch("click", y.detail), ke = () => x.dispatch("change", c), Q = (y) => Ee(y.detail), Ge = (y) => x.dispatch("select", y.detail), Fe = (y) => x.dispatch("share", y.detail), H = (y) => x.dispatch("error", y.detail), Kt = () => {
    x.dispatch("load_more", c);
  };
  return e.$$set = (y) => {
    "loading_status" in y && n(1, i = y.loading_status), "show_label" in y && n(2, l = y.show_label), "has_more" in y && n(3, r = y.has_more), "label" in y && n(4, o = y.label), "action_label" in y && n(5, u = y.action_label), "elem_id" in y && n(6, s = y.elem_id), "elem_classes" in y && n(7, a = y.elem_classes), "visible" in y && n(8, f = y.visible), "value" in y && n(9, c = y.value), "likeable" in y && n(10, h = y.likeable), "clickable" in y && n(11, _ = y.clickable), "container" in y && n(12, d = y.container), "scale" in y && n(13, v = y.scale), "min_width" in y && n(14, A = y.min_width), "columns" in y && n(15, w = y.columns), "gap" in y && n(16, E = y.gap), "height" in y && n(17, p = y.height), "preview" in y && n(18, m = y.preview), "allow_preview" in y && n(19, k = y.allow_preview), "selected_index" in y && n(0, g = y.selected_index), "show_share_button" in y && n(20, T = y.show_share_button), "object_fit" in y && n(21, S = y.object_fit), "show_download_button" in y && n(22, z = y.show_download_button), "root" in y && n(23, R = y.root), "proxy_url" in y && n(24, q = y.proxy_url), "gradio" in y && n(25, x = y.gradio), "load_more_button_props" in y && n(28, W = y.load_more_button_props);
  }, e.$$.update = () => {
    e.$$.dirty[0] & /*_load_more_button_props, load_more_button_props*/
    335544320 && n(26, ee = {
      ...ee,
      ...W
    }), e.$$.dirty[0] & /*selected_index*/
    1 && te("prop_change", { selected_index: g });
  }, [
    g,
    i,
    l,
    r,
    o,
    u,
    s,
    a,
    f,
    c,
    h,
    _,
    d,
    v,
    A,
    w,
    E,
    p,
    m,
    k,
    T,
    S,
    z,
    R,
    q,
    x,
    ee,
    Ee,
    W,
    de,
    be,
    ke,
    Q,
    Ge,
    Fe,
    H,
    Kt
  ];
}
class kc extends ic {
  constructor(t) {
    super(), _c(
      this,
      t,
      wc,
      vc,
      dc,
      {
        loading_status: 1,
        show_label: 2,
        has_more: 3,
        label: 4,
        action_label: 5,
        elem_id: 6,
        elem_classes: 7,
        visible: 8,
        value: 9,
        likeable: 10,
        clickable: 11,
        container: 12,
        scale: 13,
        min_width: 14,
        columns: 15,
        gap: 16,
        height: 17,
        preview: 18,
        allow_preview: 19,
        selected_index: 0,
        show_share_button: 20,
        object_fit: 21,
        show_download_button: 22,
        root: 23,
        proxy_url: 24,
        gradio: 25,
        load_more_button_props: 28
      },
      null,
      [-1, -1]
    );
  }
}
export {
  nc as BaseGallery,
  kc as default
};
