/* La guía orienta la actividad; las herramientas conservan el seguimiento local. */
(() => {
  "use strict";
  let refresh = () => {};
  const byId = id => document.getElementById(id);
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
    byId("teacherDialog").scrollTop = 0;
    if (selected === "tools") requestAnimationFrame(refresh);
  }
  function init(context) {
    refresh = context.refresh || refresh;
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
    show("guide",{focus:false});
  }
  window.MitoMapaTeacher = {init,show};
})();
