<script>
  let {
    showEcg = true,
    showTicks = true,
    showStamp = true,
    opacity = 0.5,
    mode = "emerald",
  } = $props();
</script>

<div
  class="absolute inset-0 pointer-events-none overflow-hidden select-none -z-10"
  style="opacity: {opacity};"
  aria-hidden="true"
>
  <!-- Dual-Tier Veterinary ECG Millimeter Paper Grid (12px minor, 60px major) -->
  <div
    class="absolute inset-0 [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_90%)]"
    style="
      background-image:
        linear-gradient(to right, color-mix(in srgb, var(--color-primary) 8%, transparent) 1px, transparent 1px),
        linear-gradient(to bottom, color-mix(in srgb, var(--color-primary) 8%, transparent) 1px, transparent 1px),
        linear-gradient(to right, color-mix(in srgb, var(--color-primary) 22%, transparent) 1.5px, transparent 1.5px),
        linear-gradient(to bottom, color-mix(in srgb, var(--color-primary) 22%, transparent) 1.5px, transparent 1.5px);
      background-size:
        12px 12px,
        12px 12px,
        60px 60px,
        60px 60px;
    "
  ></div>
</div>
