<script>
  import { onMount, onDestroy } from "svelte";
  import { fly, fade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";

  let { nextSectionMeta = null, onAdvance = null } = $props();

  let isAdvancing = $state(false);
  let isSwipingFurther = $state(false); // True ONLY when user actively initiates downward pull at bottom
  let pullProgress = $state(0); // 0.0 to 1.0 (elapsed time / REQUIRED_DURATION_MS)

  let holdSecondsDisplay = $derived(
    (pullProgress * (REQUIRED_DURATION_MS / 1000)).toFixed(1),
  );

  // Time required for sustained downward pull (in milliseconds)
  const REQUIRED_DURATION_MS = 200;

  let swipeStartTime = null;
  let lastWheelEventTime = 0;
  let rafId = null;
  let pullInactivityTimer = null;
  let gestureIdleTimer = null;

  // Track gesture initiation and pull accumulation
  let wasAtBottomWhenGestureStarted = false;
  let isGestureActive = false;
  let accumulatedPullDelta = 0;

  function isPageAtBottom() {
    if (typeof window === "undefined") return false;
    const scrollY = window.scrollY || window.pageYOffset || 0;
    const viewportHeight = window.innerHeight || 0;
    const docHeight = Math.max(
      document.documentElement.scrollHeight,
      document.body.scrollHeight,
    );
    // True bottom: within 4px margin of error for subpixel calculations
    return scrollY + viewportHeight >= docHeight - 4;
  }

  function handleScroll() {
    if (typeof window === "undefined" || isAdvancing) return;

    // If user scrolls back up away from the bottom while pull card is open, dismiss it
    if (!isPageAtBottom() && isSwipingFurther) {
      dismiss();
    }
  }

  function handleWheel(e) {
    if (
      typeof window === "undefined" ||
      isAdvancing ||
      !nextSectionMeta?.isUnlocked
    )
      return;

    const now = Date.now();
    const timeSinceLastWheel = now - lastWheelEventTime;
    lastWheelEventTime = now;

    // If more than 280ms elapsed since previous wheel event, this is the start of a brand NEW wheel gesture
    if (!isGestureActive || timeSinceLastWheel > 280) {
      isGestureActive = true;
      accumulatedPullDelta = 0;
      // KEY DISCRIMINATOR:
      // Was the document ALREADY resting at the bottom when this wheel gesture began?
      // - If user is scrolling down through the page, isPageAtBottom() is false -> wasAtBottom = false.
      //   Even as the page reaches the bottom during this scroll, wasAtBottom remains false!
      // - Only if the user is already sitting at the bottom before touching the wheel is this true.
      wasAtBottomWhenGestureStarted = isPageAtBottom();
    }

    // Reset gesture idle timer
    if (gestureIdleTimer) clearTimeout(gestureIdleTimer);
    gestureIdleTimer = setTimeout(() => {
      isGestureActive = false;
      wasAtBottomWhenGestureStarted = false;
      accumulatedPullDelta = 0;
    }, 320);

    // If user scrolls up, immediately dismiss and cancel
    if (e.deltaY < -6) {
      dismiss();
      return;
    }

    // Handle downward movement (wheel down / two fingers moving up):
    if (e.deltaY > 0) {
      const atBottom = isPageAtBottom();

      // If document is not at the bottom yet, normal scrolling occurs; never trigger pull
      if (!atBottom) {
        if (isSwipingFurther) dismiss();
        return;
      }

      // If at bottom, but this gesture started while scrolling down the page:
      // IGNORE IT! Absorbs all momentum, inertia, and continuous flings.
      if (!wasAtBottomWhenGestureStarted) {
        return;
      }

      // Accumulate downward intent to filter out accidental micro-jitters (< 10px)
      accumulatedPullDelta += e.deltaY;
      if (accumulatedPullDelta < 10 && !isSwipingFurther) {
        return;
      }

      // User was resting at bottom and deliberately initiated a downward pull:
      if (!isSwipingFurther) {
        isSwipingFurther = true;
        swipeStartTime = now;
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(updateDurationProgress);
      }

      // Reset pull inactivity timer (allows smooth transitions between trackpad strokes)
      if (pullInactivityTimer) clearTimeout(pullInactivityTimer);
      pullInactivityTimer = setTimeout(() => {
        if (!isAdvancing) {
          dismiss();
        }
      }, 400);
    }
  }

  function updateDurationProgress() {
    if (!isPageAtBottom() || !isSwipingFurther || isAdvancing) return;
    const now = Date.now();

    // If user ceased pulling for > 400ms, dismiss
    if (now - lastWheelEventTime > 400) {
      dismiss();
      return;
    }

    const elapsed = now - swipeStartTime;
    pullProgress = Math.min(elapsed / REQUIRED_DURATION_MS, 1);

    if (elapsed >= REQUIRED_DURATION_MS) {
      triggerAdvance();
      return;
    }

    rafId = requestAnimationFrame(updateDurationProgress);
  }

  // Touch gesture support (mobile / touch displays)
  let touchStartY = 0;
  let wasAtBottomWhenTouchStarted = false;

  function handleTouchStart(e) {
    if (
      typeof window === "undefined" ||
      isAdvancing ||
      !nextSectionMeta?.isUnlocked
    )
      return;
    if (e.touches && e.touches.length > 0) {
      touchStartY = e.touches[0].clientY;
      wasAtBottomWhenTouchStarted = isPageAtBottom();
    }
  }

  function handleTouchMove(e) {
    if (
      typeof window === "undefined" ||
      isAdvancing ||
      !touchStartY ||
      !nextSectionMeta?.isUnlocked
    )
      return;

    const currentY = e.touches[0].clientY;
    const diff = touchStartY - currentY; // positive = dragging finger upward to pull page down

    if (diff < -15) {
      dismiss();
      return;
    }

    if (diff > 15) {
      const atBottom = isPageAtBottom();
      if (!atBottom) {
        if (isSwipingFurther) dismiss();
        return;
      }

      // If touch began while not at bottom, it's normal page scrolling
      if (!wasAtBottomWhenTouchStarted) {
        return;
      }

      const now = Date.now();
      lastWheelEventTime = now;

      if (!isSwipingFurther) {
        isSwipingFurther = true;
        swipeStartTime = now;
        if (rafId) cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(updateDurationProgress);
      }

      if (pullInactivityTimer) clearTimeout(pullInactivityTimer);
      pullInactivityTimer = setTimeout(() => {
        if (!isAdvancing) {
          dismiss();
        }
      }, 400);
    }
  }

  function handleTouchEnd() {
    touchStartY = 0;
    wasAtBottomWhenTouchStarted = false;
    if (!isAdvancing) {
      dismiss();
    }
  }

  function triggerAdvance() {
    if (isAdvancing || !nextSectionMeta) return;
    isAdvancing = true;
    pullProgress = 1;
    if (rafId) cancelAnimationFrame(rafId);
    if (pullInactivityTimer) clearTimeout(pullInactivityTimer);
    if (gestureIdleTimer) clearTimeout(gestureIdleTimer);

    setTimeout(() => {
      if (onAdvance) onAdvance(nextSectionMeta.id);
      setTimeout(() => {
        isAdvancing = false;
        isSwipingFurther = false;
        pullProgress = 0;
        swipeStartTime = null;
        isGestureActive = false;
        wasAtBottomWhenGestureStarted = false;
        accumulatedPullDelta = 0;
      }, 250);
    }, 320);
  }

  function dismiss() {
    if (rafId) cancelAnimationFrame(rafId);
    if (pullInactivityTimer) clearTimeout(pullInactivityTimer);
    if (gestureIdleTimer) clearTimeout(gestureIdleTimer);
    isSwipingFurther = false;
    pullProgress = 0;
    swipeStartTime = null;
    isGestureActive = false;
    wasAtBottomWhenGestureStarted = false;
    accumulatedPullDelta = 0;
  }

  // Reset automatically when switching sections
  $effect(() => {
    const _sectionId = nextSectionMeta?.id;
    dismiss();
  });

  onDestroy(() => {
    if (rafId) cancelAnimationFrame(rafId);
    if (pullInactivityTimer) clearTimeout(pullInactivityTimer);
    if (gestureIdleTimer) clearTimeout(gestureIdleTimer);
  });
</script>

<svelte:window
  onscroll={handleScroll}
  onwheel={handleWheel}
  ontouchstart={handleTouchStart}
  ontouchmove={handleTouchMove}
  ontouchend={handleTouchEnd}
/>

{#if nextSectionMeta && nextSectionMeta.isUnlocked && (isSwipingFurther || isAdvancing)}
  <div
    class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-md pointer-events-auto"
    in:fly={{ y: 50, duration: 350, easing: cubicInOut }}
    out:fly={{ y: 50, duration: 250, easing: cubicInOut }}
  >
    <div
      class="p-4 rounded-3xl backdrop-blur-xl border shadow-2xl transition-all duration-300 ease-in-out select-none {isAdvancing
        ? 'bg-primary/25 border-primary shadow-primary/30 scale-[1.02]'
        : isSwipingFurther
          ? 'bg-base-100/98 border-primary shadow-2xl ring-2 ring-primary/30'
          : 'bg-base-100/95 border-primary/40 shadow-xl'}"
    >
      <!-- Pull Bar Grip Handle with live stretch -->
      <div class="flex justify-center mb-2">
        <div
          class="h-1.5 rounded-full bg-primary transition-all duration-150 ease-out"
          style="width: {Math.max(
            48,
            Math.round(pullProgress * 150),
          )}px; opacity: {0.4 + pullProgress * 0.6}"
        ></div>
      </div>

      <!-- Header with Step Info & Dismiss Button -->
      <div class="flex items-center justify-between gap-2 mb-2.5">
        <div class="flex items-center gap-2">
          <span
            class="text-xl transition-transform duration-300 {isAdvancing
              ? 'scale-125'
              : isSwipingFurther
                ? 'scale-115'
                : 'scale-100'}"
          >
            {nextSectionMeta.icon}
          </span>
          <div>
            <div class="flex items-center gap-1.5">
              <span
                class="badge badge-primary badge-xs font-mono font-bold text-[10px]"
              >
                {nextSectionMeta.step}
              </span>
              <span class="text-xs font-black font-display text-base-content">
                {nextSectionMeta.name}
              </span>
            </div>
            <p class="text-[11px] text-base-content/70 mt-0.5 font-medium">
              {#if isAdvancing}
                <span class="text-primary font-bold"
                  >Swiping into {nextSectionMeta.step}...</span
                >
              {:else if pullProgress >= 0.85}
                <span class="text-primary font-bold animate-pulse"
                  >Almost there! Keep swiping...</span
                >
              {:else if isSwipingFurther}
                <span class="text-primary font-bold"
                  >Swiping further: {Math.round(pullProgress * 100)}% ({holdSecondsDisplay}s
                  / {(REQUIRED_DURATION_MS / 1000).toFixed(1)}s)</span
                >
              {:else}
                <span>Bottom reached — swipe further down to advance</span>
              {/if}
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
      {#if isSwipingFurther || isAdvancing}
        <div
          class="w-full bg-base-300/80 h-2 rounded-full overflow-hidden mb-2.5 relative"
        >
          <div
            class="h-full bg-primary rounded-full transition-all duration-100 ease-out relative"
            style="width: {Math.min(pullProgress * 100, 100)}%"
          >
            <!-- Glowing leading pulse -->
            <div
              class="absolute right-0 top-0 bottom-0 w-2 bg-white/80 rounded-full shadow-[0_0_8px_white]"
            ></div>
          </div>
        </div>
      {/if}

      <!-- Sustained Pull-Down Swipe Track with Fluid Progress Fill -->
      <button
        type="button"
        class="w-full relative overflow-hidden rounded-2xl p-3 border transition-all duration-200 ease-in-out cursor-pointer flex items-center justify-between {isAdvancing
          ? 'bg-primary text-white border-primary shadow-md'
          : isSwipingFurther
            ? 'bg-primary/10 border-primary/50'
            : 'bg-base-200/90 border-base-300'}"
        onclick={triggerAdvance}
        title="Swipe or click to advance to next section"
      >
        <!-- Sustained Swipe Gauge Fill -->
        <div
          class="absolute inset-0 bg-primary/20 transition-all duration-100 ease-out"
          style="width: {Math.min(pullProgress * 100, 100)}%"
        ></div>

        <div class="relative z-10 flex items-center gap-2">
          <div
            class="w-8 h-8 rounded-xl bg-primary text-white flex items-center justify-center font-bold text-sm shadow-sm transition-transform duration-200 {isAdvancing
              ? 'scale-125'
              : pullProgress > 0.5
                ? 'scale-110'
                : ''}"
          >
            {#if isAdvancing}
              <span>✓</span>
            {:else}
              <span
                class="transition-transform duration-150"
                style="transform: translateY({Math.round(pullProgress * 4)}px)"
                >↓</span
              >
            {/if}
          </div>
          <div class="text-left">
            <div class="text-xs font-bold leading-tight">
              {#if isAdvancing}
                <span>Transitioning section</span>
              {:else if pullProgress >= 0.9}
                <span class="text-primary font-black">Release to advance!</span>
              {:else if isSwipingFurther}
                <span class="text-primary font-bold">Keep swiping down...</span>
              {:else}
                <span>Swipe further down to switch</span>
              {/if}
            </div>
            <div class="text-[10px] opacity-75 font-mono">
              {#if isAdvancing}
                <span>Loading views...</span>
              {:else if isSwipingFurther}
                <span class="text-primary font-bold"
                  >{Math.round(pullProgress * 100)}% ({holdSecondsDisplay}s / {(
                    REQUIRED_DURATION_MS / 1000
                  ).toFixed(1)}s)</span
                >
              {:else}
                <span
                  >Hold swipe for {(REQUIRED_DURATION_MS / 1000).toFixed(1)}s to
                  advance</span
                >
              {/if}
            </div>
          </div>
        </div>

        <div
          class="relative z-10 flex items-center gap-1.5 font-mono text-[10px] font-bold"
        >
          <span
            class="badge badge-sm {isSwipingFurther
              ? 'badge-primary font-black'
              : 'badge-outline border-primary/40 bg-base-100/60'}"
          >
            {Math.round(pullProgress * 100)}%
          </span>
          <span
            class="text-primary font-bold text-sm transition-transform duration-200 {pullProgress >
            0.5
              ? 'translate-x-1'
              : ''}">➔</span
          >
        </div>
      </button>
    </div>
  </div>
{/if}
