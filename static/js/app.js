document.addEventListener("alpine:init", () => {

  // Sidebar collapse/expand
  Alpine.store("sidebar", {
    collapsed: false,
    toggle() {
      this.collapsed = !this.collapsed;
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
