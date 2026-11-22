/* La guía orienta la actividad; las herramientas conservan el seguimiento local. */
(() => {
  "use strict";
  let refresh = () => {};
  const byId = id => document.getElementById(id);
  function focusControl(control) {
    if (!control) return;
    const content = byId("teacherDialog").querySelector(".teacher-body");
    control.focus({preventScroll:true});
    const offset = control.getBoundingClientRect().top - content.getBoundingClientRect().top;
    content.scrollTop += offset - 14;
  }

  function show(name, {focus = true} = {}) {
    const selected = name === "tools" ? "tools" : "guide";
    const tabs = [...document.querySelectorAll("[data-teacher-tab]")];
    tabs.forEach(tab => {
      const active = tab.dataset.teacherTab === selected;
      tab.setAttribute("aria-selected",String(active));
      tab.tabIndex = active ? 0 : -1;
      byId(tab.getAttribute("aria-controls")).hidden = !active;
      if (active && focus) tab.focus({preventScroll:true});
    });
    byId("teacherDialog").querySelector(".teacher-body").scrollTop = 0;
    if (selected === "tools") requestAnimationFrame(refresh);
  }
  function filterIslands() {
    const select = byId("teacherIslandFilter");
    const rows = [...byId("teacherProgressBody").rows];
    let visibleCount = 0;
    rows.forEach(row => {
      row.hidden = Boolean(select.value && row.dataset.teacherIsland !== select.value);
      if (!row.hidden) visibleCount++;
    });
    const status = byId("teacherIslandFilterStatus");
    const message = select.value ? `Mostrando 1 de ${rows.length} islas.` : `Mostrando las ${visibleCount} islas.`;
    if (status.textContent !== message) status.textContent = message;
  }

  function init(context) {
    refresh = context.refresh || refresh;
    const filter = byId("teacherIslandFilter");
    context.routes.forEach(({id,island}) => filter.add(new Option(island,id)));
    filter.addEventListener("change",filterIslands);
    const tabs = [...document.querySelectorAll("[data-teacher-tab]")];
    tabs.forEach((tab,index) => {
      tab.addEventListener("click",() => show(tab.dataset.teacherTab));
      tab.addEventListener("keydown",event => {
        let next;
        if (event.key === "ArrowRight") next = (index+1)%tabs.length;
        else if (event.key === "ArrowLeft") next = (index+tabs.length-1)%tabs.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = tabs.length-1;
        else return;
        event.preventDefault();show(tabs[next].dataset.teacherTab);
      });
    });
    byId("teacherGuidePanel").querySelectorAll("[data-learning-level]").forEach(button => {
      button.addEventListener("click",() => context.setLevel(button.dataset.learningLevel));
    });
    byId("teacherChangeStage").addEventListener("click",() => {
      const stage = byId("teacherGuidePanel").querySelector("[data-learning-level][aria-pressed='true']");
      const target = stage || byId("teacherGuidePanel").querySelector("[data-learning-level]");
      show("guide",{focus:false});
      target.closest("details").open = true;
      focusControl(target);
    });
    byId("teacherToolsPanel").querySelectorAll("[data-teacher-jump]").forEach(button => {
      button.addEventListener("click",() => {
        const id = button.dataset.teacherJump;
        if (id === "teacherRouteTitle") byId("agreedRouteSettings").open = true;
        focusControl(byId(id));
      });
    });
    show("guide",{focus:false});
  }
  window.MitoMapaTeacher = {init,show,focusControl,filterIslands};
})();
