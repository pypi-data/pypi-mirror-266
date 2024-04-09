<svelte:options accessors={true} />

<script context="module" lang="ts">
  export { default as BaseTextbox } from "./shared/Textbox.svelte";
  export { default as BaseExample } from "./Example.svelte";
</script>

<script lang="ts">
  import { onMount } from "svelte";
  import type { Gradio, SelectData } from "@gradio/utils";
  import { BlockTitle } from "@gradio/atoms";

  import SequenceInput from "./shared/SequenceInput.svelte";
  import { Block } from "@gradio/atoms";
  import { StatusTracker } from "@gradio/statustracker";
  import type { LoadingStatus } from "@gradio/statustracker";

  export let gradio: Gradio<{
    change: string;
    submit: never;
    blur: never;
    select: SelectData;
    input: never;
    focus: never;
  }>;
  export let label = "CofoldingInput";
  export let info: string | undefined = undefined;
  export let elem_id = "";
  export let elem_classes: string[] = [];
  export let visible = true;
  export let value = { chains: [], covMods: [] };
  export let show_label: boolean;
  export let container = true;
  export let scale: number | null = null;
  export let min_width: number | undefined = undefined;
  export let loading_status: LoadingStatus | undefined = undefined;

  function syncValue(event) {
    //remove empty values and open attributes
    let entries = event.detail.map((entry) =>
      Object.fromEntries(
        Object.entries(entry).filter(
          ([key, value]) => key !== "open" && value !== ""
        )
      )
    );
    value["chains"] = entries;
  }

  function syncCovMod(event) {
    value["covMods"] = event.detail;
  }

  onMount(() => {});
</script>

<Block
  {visible}
  {elem_id}
  {elem_classes}
  {scale}
  {min_width}
  allow_overflow={false}
  padding={container}
>
  {#if loading_status}
    <StatusTracker
      autoscroll={gradio.autoscroll}
      i18n={gradio.i18n}
      {...loading_status}
    />
  {/if}

  <BlockTitle {show_label} {info}>{label}</BlockTitle>

  <SequenceInput
    bind:value
    on:updateVals={syncValue}
    on:updateCovMod={syncCovMod}
  />
</Block>
