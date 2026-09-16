<script>
  import { onMount, onDestroy } from "svelte";
  import { fly } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";

  let {
    nextSectionMeta = null,
    prevSectionMeta = null,
    onAdvance = null,
    onPrevious = null,
  } = $props();

  let isAdvancing = $state(false);
  let isSwipingFurther = $state(false);
  let activeDirection = $state("next"); // "next" | "prev"
  let pullProgress = $state(0);

  let activeMeta = $derived(
    activeDirection === "prev" ? prevSectionMeta : nextSectionMeta,
  );

  let isAtBottom = false;
  let readyForPullBottom = false;
  let settleBottomTimer = null;
  let bottomReachedTime = 0;

  let isAtTop = false;
  let readyForPullTop = false;
  let settleTopTimer = null;
  let topReachedTime = 0;

  let advanceTimeout = null;

  function checkTop() {
    if (typeof window === "undefined") return false;
    const scrollY = window.scrollY || window.pageYOffset || 0;
    return scrollY <= 4;
  }

  function checkBottom() {
    if (typeof window === "undefined") return false;
    const scrollY = window.scrollY || window.pageYOffset || 0;
    const viewportHeight = window.innerHeight || 0;
    const docHeight = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight,
    );
    return scrollY + viewportHeight >= docHeight - 6;
  }

  function resetBottomSettleTimer() {
    readyForPullBottom = false;
    if (settleBottomTimer) clearTimeout(settleBottomTimer);
    settleBottomTimer = setTimeout(() => {
      if (checkBottom() && Date.now() - bottomReachedTime >= 100) {
        readyForPullBottom = true;
      }
    }, 150);
  }

  function resetTopSettleTimer() {
    readyForPullTop = false;
    if (settleTopTimer) clearTimeout(settleTopTimer);
    settleTopTimer = setTimeout(() => {
      if (checkTop() && Date.now() - topReachedTime >= 100) {
        readyForPullTop = true;
      }
    }, 150);
  }

  function handleScroll() {
    if (typeof window === "undefined" || isAdvancing) return;

    const atBottom = checkBottom();
    const atTop = checkTop();

    if (atBottom) {
      if (!isAtBottom) {
        isAtBottom = true;
        bottomReachedTime = Date.now();
      }
      resetBottomSettleTimer();
    } else {
      isAtBottom = false;
      readyForPullBottom = false;
      bottomReachedTime = 0;
      if (settleBottomTimer) clearTimeout(settleBottomTimer);
      if (isSwipingFurther && activeDirection === "next" && !isAdvancing) {
        dismiss();
      }
    }

    if (atTop) {
      if (!isAtTop) {
        isAtTop = true;
        topReachedTime = Date.now();
      }
      resetTopSettleTimer();
    } else {
      isAtTop = false;
      readyForPullTop = false;
      topReachedTime = 0;
      if (settleTopTimer) clearTimeout(settleTopTimer);
      if (isSwipingFurther && activeDirection === "prev" && !isAdvancing) {
        dismiss();
      }
    }
  }

  function handleWheel(e) {
    if (typeof window === "undefined" || isAdvancing) return;

    // Upward scroll / pull top
    if (e.deltaY < -5) {
      if (isSwipingFurther && activeDirection === "next") {
        dismiss();
        return;
      }

      if (!prevSectionMeta?.isUnlocked) return;

      const atTop = checkTop();
      if (!atTop) {
        isAtTop = false;
        readyForPullTop = false;
        return;
      }

      if (!isAtTop) {
        isAtTop = true;
        topReachedTime = Date.now();
      }

      if (!readyForPullTop) {
        resetTopSettleTimer();
        return;
      }

      // Deliberate upward stroke while settled at top
      if (e.deltaY < -18) {
        executePrevious();
      }
      return;
    }

    // Downward scroll / pull bottom
    if (e.deltaY > 5) {
      if (isSwipingFurther && activeDirection === "prev") {
        dismiss();
        return;
      }

      if (!nextSectionMeta?.isUnlocked) return;

      const atBottom = checkBottom();
      if (!atBottom) {
        isAtBottom = false;
        readyForPullBottom = false;
        return;
      }

      if (!isAtBottom) {
        isAtBottom = true;
        bottomReachedTime = Date.now();
      }

      if (!readyForPullBottom) {
        resetBottomSettleTimer();
        return;
      }

      // Deliberate downward stroke while settled at bottom
      if (e.deltaY > 18) {
        executeAdvance();
      }
      return;
    }
  }

  let touchStartY = 0;
  function handleTouchStart(e) {
    if (typeof window === "undefined" || isAdvancing) return;
    if (e.touches && e.touches.length > 0) {
      touchStartY = e.touches[0].clientY;
    }
  }

  function handleTouchMove(e) {
    if (typeof window === "undefined" || isAdvancing || !touchStartY) return;

    const currentY = e.touches[0].clientY;
    const diff = touchStartY - currentY;
    // diff > 0: finger dragged up (scrolling down / pulling bottom)
    // diff < 0: finger dragged down (scrolling up / pulling top)

    // Pull top: dragging down at top (diff < -15)
    if (diff < -15) {
      if (isSwipingFurther && activeDirection === "next") {
        dismiss();
        return;
      }

      if (!prevSectionMeta?.isUnlocked) return;

      const atTop = checkTop();
      if (!atTop) {
        isAtTop = false;
        readyForPullTop = false;
        return;
      }

      if (!readyForPullTop) {
        resetTopSettleTimer();
        return;
      }

      if (diff < -30) {
        executePrevious();
      }
      return;
    }

    // Pull bottom: dragging up at bottom (diff > 15)
    if (diff > 15) {
      if (isSwipingFurther && activeDirection === "prev") {
        dismiss();
        return;
      }

      if (!nextSectionMeta?.isUnlocked) return;

      const atBottom = checkBottom();
      if (!atBottom) {
        isAtBottom = false;
        readyForPullBottom = false;
        return;
      }

      if (!readyForPullBottom) {
        resetBottomSettleTimer();
        return;
      }

      if (diff > 30) {
        executeAdvance();
      }
      return;
    }
  }

  function handleTouchEnd() {
    touchStartY = 0;
  }

  function executeAdvance() {
    if (isAdvancing || !nextSectionMeta) return;
    isAdvancing = true;
    isSwipingFurther = true;
    activeDirection = "next";
    pullProgress = 1;

    if (advanceTimeout) clearTimeout(advanceTimeout);
    advanceTimeout = setTimeout(() => {
      if (onAdvance) onAdvance(nextSectionMeta.id);
      setTimeout(() => {
        dismiss();
      }, 250);
    }, 280);
  }

  function executePrevious() {
    if (isAdvancing || !prevSectionMeta) return;
    isAdvancing = true;
    isSwipingFurther = true;
    activeDirection = "prev";
    pullProgress = 1;

    if (advanceTimeout) clearTimeout(advanceTimeout);
    advanceTimeout = setTimeout(() => {
      if (onPrevious) onPrevious(prevSectionMeta.id);
      setTimeout(() => {
        dismiss();
      }, 250);
    }, 280);
  }

  function dismiss() {
    if (advanceTimeout) clearTimeout(advanceTimeout);
    if (settleBottomTimer) clearTimeout(settleBottomTimer);
    if (settleTopTimer) clearTimeout(settleTopTimer);
    isAdvancing = false;
    isSwipingFurther = false;
    pullProgress = 0;
    readyForPullBottom = false;
    readyForPullTop = false;
    bottomReachedTime = 0;
    topReachedTime = 0;
  }

  $effect(() => {
    const _nextId = nextSectionMeta?.id;
    const _prevId = prevSectionMeta?.id;
    dismiss();
  });

  onMount(() => {
    handleScroll();
  });

  onDestroy(() => {
    if (advanceTimeout) clearTimeout(advanceTimeout);
    if (settleBottomTimer) clearTimeout(settleBottomTimer);
    if (settleTopTimer) clearTimeout(settleTopTimer);
  });
</script>

<svelte:window
  onscroll={handleScroll}
  onwheel={handleWheel}
  ontouchstart={handleTouchStart}
  ontouchmove={handleTouchMove}
  ontouchend={handleTouchEnd}
/>

{#if activeMeta && activeMeta.isUnlocked && (isSwipingFurther || isAdvancing)}
  <div
    class="fixed {activeDirection === 'prev'
      ? 'top-[200px]'
      : 'bottom-6'} left-1/2 -translate-x-1/2 z-150 w-[92%] max-w-md pointer-events-auto"
    in:fly={{
      y: activeDirection === "prev" ? -50 : 50,
      duration: 350,
      easing: cubicInOut,
    }}
    out:fly={{
      y: activeDirection === "prev" ? -50 : 50,
      duration: 250,
      easing: cubicInOut,
    }}
  >
    <div
      class="p-4 rounded-3xl backdrop-blur-xl border shadow-2xl transition-all duration-300 ease-in-out select-none bg-white/40 border-primary shadow-primary/30 scale-[1.02]"
    >
      <!-- Pull Bar Grip Handle -->
      <div class="flex justify-center mb-2">
        <div
          class="h-1.5 rounded-full bg-primary transition-all duration-150 ease-out w-32 opacity-90 shadow-sm"
        ></div>
      </div>

      <!-- Header with Step Info & Dismiss Button -->
      <div class="flex items-center justify-between gap-2 mb-2.5">
        <div class="flex items-center gap-2">
          <span class="text-xl transition-transform duration-300 scale-125">
            {activeMeta.icon}
          </span>
          <div>
            <div class="flex items-center gap-1.5">
              <span
                class="badge badge-primary badge-xs font-mono font-bold text-[10px]"
              >
                {activeMeta.step}
              </span>
              <span class="text-xs font-black font-display text-base-content">
                {activeMeta.name}
              </span>
            </div>
            <p class="text-[11px] text-base-content/70 mt-0.5 font-medium">
              <span class="text-primary font-bold">
                {#if activeDirection === "prev"}
                  Swiping back to {activeMeta.step}...
                {:else}
                  Swiping into {activeMeta.step}...
                {/if}
              </span>
            </p>
          </div>
        </div>

        <button
          type="button"
          class="btn btn-ghost btn-circle btn-xs text-base-content/50 hover:text-base-content cursor-pointer"
          onclick={dismiss}
          title="Dismiss pull gesture"
        >
          ✕
        </button>
      </div>

      <!-- Live Advancement Progress Bar -->
      <div
        class="w-full bg-base-300/80 h-2 rounded-full overflow-hidden mb-2.5 relative"
      >
        <div
          class="h-full bg-primary rounded-full transition-all duration-200 ease-out relative w-full"
        >
          <!-- Glowing leading pulse -->
          <div
            class="absolute right-0 top-0 bottom-0 w-2 bg-white/80 rounded-full shadow-[0_0_8px_white]"
          ></div>
        </div>
      </div>

      <!-- Pull Swipe Track Button with Fluid Progress Fill -->
      <button
        type="button"
        class="w-full relative overflow-hidden rounded-2xl p-3 border transition-all duration-200 ease-in-out cursor-pointer flex items-center justify-between bg-primary text-white border-primary shadow-md"
        onclick={activeDirection === "prev" ? executePrevious : executeAdvance}
        title={activeDirection === "prev"
          ? "Navigate to previous section"
          : "Advance to next section"}
      >
        <!-- Gauge Fill -->
        <div class="absolute inset-0 bg-primary/30 w-full"></div>

        <div class="relative z-10 flex items-center gap-2">
          <div
            class="w-8 h-8 rounded-xl bg-white text-primary flex items-center justify-center font-black text-sm shadow-sm transition-transform duration-200 scale-110"
          >
            <span>{activeDirection === "prev" ? "←" : "✓"}</span>
          </div>
          <div class="text-left">
            <div class="text-xs font-black leading-tight text-white">
              <span>
                {#if activeDirection === "prev"}
                  Returning to previous section
                {:else}
                  Transitioning section
                {/if}
              </span>
            </div>
            <div class="text-[10px] opacity-90 font-mono text-white/80">
              <span>
                {#if activeDirection === "prev"}
                  Back to {activeMeta.name}...
                {:else}
                  Loading {activeMeta.name}...
                {/if}
              </span>
            </div>
          </div>
        </div>

        <div
          class="relative z-10 flex items-center gap-1.5 font-mono text-[10px] font-bold"
        >
          <span
            class="badge badge-sm bg-white text-primary font-black border-none"
          >
            100%
          </span>
          <span class="text-white font-bold text-sm">
            {activeDirection === "prev" ? "⬅" : "➔"}
          </span>
        </div>
      </button>
    </div>
  </div>
{/if}
