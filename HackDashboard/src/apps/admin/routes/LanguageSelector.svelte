<script>
  import { fly } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";
  import { i18nState, setLocale, supportedLocales } from "$lib";

  let isOpen = $state(false);

  function toggleDropdown() {
    isOpen = !isOpen;
  }

  function selectLanguage(code) {
    setLocale(code);
    isOpen = false;
  }

  function handleKeydown(event) {
    if (event.key === "Escape") isOpen = false;
  }

  function clickOutside(node) {
    function handle(e) {
      if (!node.contains(e.target)) isOpen = false;
    }
    document.addEventListener("pointerdown", handle, true);
    return { destroy() { document.removeEventListener("pointerdown", handle, true); } };
  }

  let current = $derived(
    supportedLocales.find((l) => l.code === i18nState.locale) || supportedLocales[0]
  );
</script>

<svelte:window onkeydown={handleKeydown} />

<div class="relative inline-block text-left" use:clickOutside>
  <!-- Trigger Button -->
  <button
    type="button"
    onclick={toggleDropdown}
    class="btn btn-sm btn-ghost border border-base-content/15 hover:border-primary/40 bg-base-100/80 hover:bg-base-200/90 text-base-content rounded-xl px-2.5 sm:px-3 gap-1.5 shadow-xs transition-all duration-200 ease-in-out cursor-pointer flex items-center font-medium"
    aria-haspopup="true"
    aria-expanded={isOpen}
    title="Change Language / Cambia Lingua"
  >
    <span class="text-base leading-none select-none">{current.flag}</span>
    <span class="font-mono text-xs font-bold uppercase tracking-wider">{current.code}</span>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-3 w-3 opacity-60 transition-transform duration-250 ease-in-out {isOpen ? 'rotate-180' : ''}"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
    </svg>
  </button>

  <!-- Dropdown Menu with fancy cubic easing -->
  {#if isOpen}
    <div
      transition:fly={{ y: -6, duration: 220, easing: cubicInOut }}
      class="absolute right-0 mt-2 w-44 rounded-2xl bg-base-100/95 backdrop-blur-xl border border-base-content/15 shadow-xl p-1.5 z-50 flex flex-col gap-1"
      role="menu"
    >
      <div class="px-2.5 py-1 text-[10px] font-mono uppercase tracking-widest text-base-content/50 border-b border-base-content/10">
        Select Language
      </div>

      {#each supportedLocales as loc}
        <button
          type="button"
          role="menuitem"
          onclick={() => selectLanguage(loc.code)}
          class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all duration-200 ease-in-out cursor-pointer hover:scale-[1.02] active:scale-[0.98] {i18nState.locale === loc.code ? 'bg-primary/15 text-primary font-bold shadow-xs' : 'hover:bg-base-200/80 text-base-content'}"
        >
          <div class="flex items-center gap-2.5">
            <span class="text-base">{loc.flag}</span>
            <span>{loc.nativeName}</span>
          </div>

          {#if i18nState.locale === loc.code}
            <span class="text-primary font-bold text-xs">✓</span>
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>
