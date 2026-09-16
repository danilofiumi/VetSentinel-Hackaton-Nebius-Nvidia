<script>
  import Layout from "../../admin/routes/+layout.svelte";
  let { children } = $props();
</script>

<Layout>
  {@render children()}
</Layout>
