<script>
  let {
    src = "",
    alt = "",
    class: className = "",
    wrapperClass = "",
    loading = "lazy",
    decoding = "async",
    ...restProps
  } = $props();

  let loaded = $state(false);
  let hasError = $state(false);

  // Check if image is already cached upon mounting
  function init(node) {
    if (node.complete && node.naturalWidth > 0) {
      loaded = true;
    }
  }

  // Derive wrapper layout classes (dimensions, aspect ratio, rounding, shrink/grow)
  let computedWrapperClass = $derived.by(() => {
    if (wrapperClass) return wrapperClass;
    const tokens = className.split(/\s+/).filter(Boolean);
    const layout = tokens.filter(t =>
      t.startsWith("w-") ||
      t.startsWith("h-") ||
      t.startsWith("max-") ||
      t.startsWith("min-") ||
      t.startsWith("rounded") ||
      t.startsWith("shrink") ||
      t.startsWith("grow") ||
      t.startsWith("aspect-")
    );
    return layout.length > 0 ? layout.join(" ") : "w-full h-full";
  });
</script>

<div class="relative overflow-hidden {computedWrapperClass}">
  <!-- Placeholder Skeleton with pulse and subtle veterinary icon -->
  {#if !loaded && !hasError}
    <div
      class="absolute inset-0 z-0 flex items-center justify-center bg-base-300/40 backdrop-blur-xs animate-pulse transition-opacity duration-500 ease-in-out"
    >
      <div class="flex items-center justify-center w-full h-full text-base-content/25">
        <svg
          class="w-6 h-6 max-w-[45%] max-h-[45%] stroke-current animate-pulse opacity-50"
          viewBox="0 0 24 24"
          fill="none"
          stroke-width="1.5"
        >
          <rect x="3" y="3" width="18" height="18" rx="3" ry="3" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>
    </div>
  {/if}

  <!-- Error state fallback -->
  {#if hasError}
    <div
      class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-base-200/90 text-base-content/40 p-1 text-center"
    >
      <svg
        class="w-5 h-5 text-warning/70 mb-0.5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span class="text-[9px] font-mono opacity-70 truncate max-w-full">Image unavailable</span>
    </div>
  {/if}

  <!-- Target Image with smooth fade & scale-in -->
  <img
    {src}
    {alt}
    {loading}
    {decoding}
    use:init
    onload={() => (loaded = true)}
    onerror={() => {
      hasError = true;
      loaded = true;
    }}
    class="{className} transition-all duration-500 ease-in-out {loaded ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}"
    {...restProps}
  />
</div>
