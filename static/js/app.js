document.addEventListener("alpine:init", () => {

  // Sidebar collapse/expand
  // Desktop (≥1024px): colapsa/expande a rail (w-14 / w-64)
  // Mobile (<1024px): abre/fecha como overlay por cima do conteúdo
  Alpine.store("sidebar", {
    collapsed: false,
    mobileOpen: false,
    get isMobile() {
      return window.innerWidth < 1024;
    },
    toggle() {
      if (this.isMobile) {
        this.mobileOpen = !this.mobileOpen;
      } else {
        this.collapsed = !this.collapsed;
      }
    },
    close() {
      this.mobileOpen = false;
    },
  });

  // Tabs em páginas de detalhe (turma, atividade, etc.)
  Alpine.store("tabs", {
    active: "aulas",
    set(tab) {
      this.active = tab;
    },
    is(tab) {
      return this.active === tab;
    },
  });

  // Confirmação de ações destrutivas (exclusão, arquivamento)
  Alpine.store("confirm", {
    show: false,
    message: "",
    action: null,
    open(message, fn) {
      this.message = message;
      this.action = fn;
      this.show = true;
    },
    confirm() {
      if (typeof this.action === "function") {
        this.action();
      }
      this.show = false;
    },
    cancel() {
      this.show = false;
    },
  });

});

document.addEventListener("htmx:afterSwap", (event) => {
  if (!window.Alpine || !event.target) {
    return;
  }

  window.Alpine.initTree(event.target);
});
