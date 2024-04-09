<script>
  import { createEventDispatcher, afterUpdate } from "svelte";

  const dispatch = createEventDispatcher();
  import Dmol from "3dmol";

  // export let whichCovMod = 0;

  let viewer = null;

  let attachmentIndex = null;
  let deleteIndexes = [];

  let mode = "attach";

  function updateReps(viewer) {
    viewer.setStyle({ stick: {} });
    if (showCovMod > -1) {
      if (attachmentIndex !== null) {
        viewer.addStyle(
          { index: attachmentIndex },
          { sphere: { color: "blue", scale: 0.5 } }
        );
      }

      viewer.addStyle(
        { index: deleteIndexes },
        { sphere: { color: "red", scale: 0.5 } }
      );

      dispatch("updateMol", {
        attachmentIndex: attachmentIndex,
        deleteIndexes: deleteIndexes,
        index: showCovMod,
        mol: viewer.exportJSON(),
      });
    }
  }
  function initializeMoleculeViewer(molecule, container) {
    let viewer = Dmol.createViewer(container, {});
    viewer.addModel(molecule, "sdf");
    updateReps(viewer);
    viewer.setBackgroundColor("white");
    viewer.zoomTo();

    viewer
      .getModel(0)
      .setClickable({}, true, function (atom, viewer, event, container) {
        if (showCovMod > -1) {
          if (mode === "attach") {
            attachmentIndex = atom.serial;
          } else {
            if (deleteIndexes.includes(atom.serial)) {
              deleteIndexes = deleteIndexes.filter(
                (index) => index !== atom.serial
              );
            } else {
              deleteIndexes.push(atom.serial);
            }
            deleteIndexes = deleteIndexes;
            updateReps(viewer);
          }
        }
      });
    viewer.render();

    return viewer;
  }
  export let molvalue = "";
  export let showCovMod = -1;
  let molcontainer = null;
  afterUpdate(() => {
    viewer = initializeMoleculeViewer(molvalue, molcontainer);
  });
</script>

<div class="mol-wrapper">
  <div class="relative">
    <div class="mol-canvas" bind:this={molcontainer}></div>
  </div>
  <div class="flex flex-col justify-center">
    {#if showCovMod > -1}
      <div class="w-full text-center text-lg mb-2">Covalent Modification</div>
      <div class="flex items-center space-x-2 justify-center mb-2 text-xs">
        <svg
          data-slot="icon"
          fill="none"
          stroke-width="1.5"
          class="w-4 h-4"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15.042 21.672 13.684 16.6m0 0-2.51 2.225.569-9.47 5.227 7.917-3.286-.672Zm-7.518-.267A8.25 8.25 0 1 1 20.25 10.5M8.288 14.212A5.25 5.25 0 1 1 17.25 10.5"
          ></path>
        </svg> <span class="px-2">click on atoms in viewer to select them</span>
      </div>
      <div
        class="flex rounded-full border-2 border-gray-200 bg-gray-200 text-sm leading-none text-gray-500"
      >
        <button
          class="w-1/2 flex items-center rounded-l-full px-4 py-2 transition-colors duration-300 ease-in hover:text-orange-600 focus:text-orange-600 focus:outline-none"
          id="attach"
          class:active={mode === "attach"}
          on:click={() => (mode = "attach")}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="mx-1 h-4 w-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m18.375 12.739-7.693 7.693a4.5 4.5 0 0 1-6.364-6.364l10.94-10.94A3 3 0 1 1 19.5 7.372L8.552 18.32m.009-.01-.01.01m5.699-9.941-7.81 7.81a1.5 1.5 0 0 0 2.112 2.13"
            />
          </svg>

          <span>Attachment atom</span>
        </button>
        <button
          class="w-1/2 flex items-center rounded-r-full px-4 py-2 transition-colors duration-300 ease-in hover:text-orange-600 focus:text-orange-600 focus:outline-none"
          id="delete"
          class:active={mode === "delete"}
          on:click={() => (mode = "delete")}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="mx-1 h-4 w-4"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
            />
          </svg>

          <span>Atoms to delete</span>
        </button>
      </div>

      <div class="relative overflow-x-auto mt-3">
        <table
          class="w-full text-sm text-left rtl:text-right text-gray-500 dark:text-gray-400"
        >
          <thead
            class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400"
          >
            <tr>
              <th scope="col" class="px-6 py-3"> </th>
              <th scope="col" class="px-6 py-3"> index </th>
            </tr>
          </thead>
          <tbody>
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
              <th
                scope="row"
                class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white text-right"
              >
                Attachment atom
              </th>
              <td class="px-6 py-4 font-mono">
                {#if attachmentIndex !== null}
                  {attachmentIndex}
                {:else}
                  not selected
                {/if}
              </td>
            </tr>

            <tr class="bg-white dark:bg-gray-800">
              <th
                scope="row"
                class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white text-right"
              >
                Deleted atoms
              </th>
              <td class="px-6 py-4 font-mono">
                {#if deleteIndexes.length > 0}
                  {deleteIndexes.join(", ")}
                {:else}
                  no atoms are deleted
                {/if}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

<style>
  .active {
    background: white;
    border-radius: 9999px;
    color: rgb(234, 88, 12);
  }
  .mol-canvas {
    width: 200px;
    height: 200px;
    margin: 0 auto;
  }
  .mol-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
  }
  /*
! tailwindcss v3.4.3 | MIT License | https://tailwindcss.com
*/

  /*
1. Prevent padding and border from affecting element width. (https://github.com/mozdevs/cssremedy/issues/4)
2. Allow adding a border to an element by just adding a border-width. (https://github.com/tailwindcss/tailwindcss/pull/116)
*/

  *,
  ::before,
  ::after {
    box-sizing: border-box;
    /* 1 */
    border-width: 0;
    /* 2 */
    border-style: solid;
    /* 2 */
    border-color: #e5e7eb;
    /* 2 */
  }

  ::before,
  ::after {
    --tw-content: "";
  }

  /*
1. Use a consistent sensible line-height in all browsers.
2. Prevent adjustments of font size after orientation changes in iOS.
3. Use a more readable tab size.
4. Use the user's configured `sans` font-family by default.
5. Use the user's configured `sans` font-feature-settings by default.
6. Use the user's configured `sans` font-variation-settings by default.
7. Disable tap highlights on iOS
*/

  html,
  :host {
    line-height: 1.5;
    /* 1 */
    -webkit-text-size-adjust: 100%;
    /* 2 */
    -moz-tab-size: 4;
    /* 3 */
    tab-size: 4;
    /* 3 */
    font-family: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji",
      "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
    /* 4 */
    font-feature-settings: normal;
    /* 5 */
    font-variation-settings: normal;
    /* 6 */
    -webkit-tap-highlight-color: transparent;
    /* 7 */
  }

  /*
1. Remove the margin in all browsers.
2. Inherit line-height from `html` so users can set them as a class directly on the `html` element.
*/

  body {
    margin: 0;
    /* 1 */
    line-height: inherit;
    /* 2 */
  }

  /*
1. Add the correct height in Firefox.
2. Correct the inheritance of border color in Firefox. (https://bugzilla.mozilla.org/show_bug.cgi?id=190655)
3. Ensure horizontal rules are visible by default.
*/

  hr {
    height: 0;
    /* 1 */
    color: inherit;
    /* 2 */
    border-top-width: 1px;
    /* 3 */
  }

  /*
Add the correct text decoration in Chrome, Edge, and Safari.
*/

  abbr:where([title]) {
    text-decoration: underline dotted;
  }

  /*
Remove the default font size and weight for headings.
*/

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-size: inherit;
    font-weight: inherit;
  }

  /*
Reset links to optimize for opt-in styling instead of opt-out.
*/

  a {
    color: inherit;
    text-decoration: inherit;
  }

  /*
Add the correct font weight in Edge and Safari.
*/

  b,
  strong {
    font-weight: bolder;
  }

  /*
1. Use the user's configured `mono` font-family by default.
2. Use the user's configured `mono` font-feature-settings by default.
3. Use the user's configured `mono` font-variation-settings by default.
4. Correct the odd `em` font sizing in all browsers.
*/

  code,
  kbd,
  samp,
  pre {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
    /* 1 */
    font-feature-settings: normal;
    /* 2 */
    font-variation-settings: normal;
    /* 3 */
    font-size: 1em;
    /* 4 */
  }

  /*
Add the correct font size in all browsers.
*/

  small {
    font-size: 80%;
  }

  /*
Prevent `sub` and `sup` elements from affecting the line height in all browsers.
*/

  sub,
  sup {
    font-size: 75%;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
  }

  sub {
    bottom: -0.25em;
  }

  sup {
    top: -0.5em;
  }

  /*
1. Remove text indentation from table contents in Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=999088, https://bugs.webkit.org/show_bug.cgi?id=201297)
2. Correct table border color inheritance in all Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=935729, https://bugs.webkit.org/show_bug.cgi?id=195016)
3. Remove gaps between table borders by default.
*/

  table {
    text-indent: 0;
    /* 1 */
    border-color: inherit;
    /* 2 */
    border-collapse: collapse;
    /* 3 */
  }

  /*
1. Change the font styles in all browsers.
2. Remove the margin in Firefox and Safari.
3. Remove default padding in all browsers.
*/

  button,
  input,
  optgroup,
  select,
  textarea {
    font-family: inherit;
    /* 1 */
    font-feature-settings: inherit;
    /* 1 */
    font-variation-settings: inherit;
    /* 1 */
    font-size: 100%;
    /* 1 */
    font-weight: inherit;
    /* 1 */
    line-height: inherit;
    /* 1 */
    letter-spacing: inherit;
    /* 1 */
    color: inherit;
    /* 1 */
    margin: 0;
    /* 2 */
    padding: 0;
    /* 3 */
  }

  /*
Remove the inheritance of text transform in Edge and Firefox.
*/

  button,
  select {
    text-transform: none;
  }

  /*
1. Correct the inability to style clickable types in iOS and Safari.
2. Remove default button styles.
*/

  button,
  input:where([type="button"]),
  input:where([type="reset"]),
  input:where([type="submit"]) {
    -webkit-appearance: button;
    /* 1 */
    background-color: transparent;
    /* 2 */
    background-image: none;
    /* 2 */
  }

  /*
Use the modern Firefox focus style for all focusable elements.
*/

  :-moz-focusring {
    outline: auto;
  }

  /*
Remove the additional `:invalid` styles in Firefox. (https://github.com/mozilla/gecko-dev/blob/2f9eacd9d3d995c937b4251a5557d95d494c9be1/layout/style/res/forms.css#L728-L737)
*/

  :-moz-ui-invalid {
    box-shadow: none;
  }

  /*
Add the correct vertical alignment in Chrome and Firefox.
*/

  progress {
    vertical-align: baseline;
  }

  /*
Correct the cursor style of increment and decrement buttons in Safari.
*/

  ::-webkit-inner-spin-button,
  ::-webkit-outer-spin-button {
    height: auto;
  }

  /*
1. Correct the odd appearance in Chrome and Safari.
2. Correct the outline style in Safari.
*/

  [type="search"] {
    -webkit-appearance: textfield;
    /* 1 */
    outline-offset: -2px;
    /* 2 */
  }

  /*
Remove the inner padding in Chrome and Safari on macOS.
*/

  ::-webkit-search-decoration {
    -webkit-appearance: none;
  }

  /*
1. Correct the inability to style clickable types in iOS and Safari.
2. Change font properties to `inherit` in Safari.
*/

  ::-webkit-file-upload-button {
    -webkit-appearance: button;
    /* 1 */
    font: inherit;
    /* 2 */
  }

  /*
Add the correct display in Chrome and Safari.
*/

  summary {
    display: list-item;
  }

  /*
Removes the default spacing and border for appropriate elements.
*/

  blockquote,
  dl,
  dd,
  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  hr,
  figure,
  p,
  pre {
    margin: 0;
  }

  fieldset {
    margin: 0;
    padding: 0;
  }

  legend {
    padding: 0;
  }

  ol,
  ul,
  menu {
    list-style: none;
    margin: 0;
    padding: 0;
  }

  /*
Reset default styling for dialogs.
*/

  dialog {
    padding: 0;
  }

  /*
Prevent resizing textareas horizontally by default.
*/

  textarea {
    resize: vertical;
  }

  /*
1. Reset the default placeholder opacity in Firefox. (https://github.com/tailwindlabs/tailwindcss/issues/3300)
2. Set the default placeholder color to the user's configured gray 400 color.
*/

  input::placeholder,
  textarea::placeholder {
    opacity: 1;
    /* 1 */
    color: #9ca3af;
    /* 2 */
  }

  /*
Set the default cursor for buttons.
*/

  button,
  [role="button"] {
    cursor: pointer;
  }

  /*
Make sure disabled buttons don't get the pointer cursor.
*/

  :disabled {
    cursor: default;
  }

  /*
1. Make replaced elements `display: block` by default. (https://github.com/mozdevs/cssremedy/issues/14)
2. Add `vertical-align: middle` to align replaced elements more sensibly by default. (https://github.com/jensimmons/cssremedy/issues/14#issuecomment-634934210)
   This can trigger a poorly considered lint error in some tools but is included by design.
*/

  img,
  svg,
  video,
  canvas,
  audio,
  iframe,
  embed,
  object {
    display: block;
    /* 1 */
    vertical-align: middle;
    /* 2 */
  }

  /*
Constrain images and videos to the parent width and preserve their intrinsic aspect ratio. (https://github.com/mozdevs/cssremedy/issues/14)
*/

  img,
  video {
    max-width: 100%;
    height: auto;
  }

  /* Make elements with the HTML hidden attribute stay hidden by default */

  [hidden] {
    display: none;
  }

  *,
  ::before,
  ::after {
    --tw-border-spacing-x: 0;
    --tw-border-spacing-y: 0;
    --tw-translate-x: 0;
    --tw-translate-y: 0;
    --tw-rotate: 0;
    --tw-skew-x: 0;
    --tw-skew-y: 0;
    --tw-scale-x: 1;
    --tw-scale-y: 1;
    --tw-pan-x:  ;
    --tw-pan-y:  ;
    --tw-pinch-zoom:  ;
    --tw-scroll-snap-strictness: proximity;
    --tw-gradient-from-position:  ;
    --tw-gradient-via-position:  ;
    --tw-gradient-to-position:  ;
    --tw-ordinal:  ;
    --tw-slashed-zero:  ;
    --tw-numeric-figure:  ;
    --tw-numeric-spacing:  ;
    --tw-numeric-fraction:  ;
    --tw-ring-inset:  ;
    --tw-ring-offset-width: 0px;
    --tw-ring-offset-color: #fff;
    --tw-ring-color: rgb(59 130 246 / 0.5);
    --tw-ring-offset-shadow: 0 0 #0000;
    --tw-ring-shadow: 0 0 #0000;
    --tw-shadow: 0 0 #0000;
    --tw-shadow-colored: 0 0 #0000;
    --tw-blur:  ;
    --tw-brightness:  ;
    --tw-contrast:  ;
    --tw-grayscale:  ;
    --tw-hue-rotate:  ;
    --tw-invert:  ;
    --tw-saturate:  ;
    --tw-sepia:  ;
    --tw-drop-shadow:  ;
    --tw-backdrop-blur:  ;
    --tw-backdrop-brightness:  ;
    --tw-backdrop-contrast:  ;
    --tw-backdrop-grayscale:  ;
    --tw-backdrop-hue-rotate:  ;
    --tw-backdrop-invert:  ;
    --tw-backdrop-opacity:  ;
    --tw-backdrop-saturate:  ;
    --tw-backdrop-sepia:  ;
    --tw-contain-size:  ;
    --tw-contain-layout:  ;
    --tw-contain-paint:  ;
    --tw-contain-style:                                         
;
  }

  ::backdrop {
    --tw-border-spacing-x: 0;
    --tw-border-spacing-y: 0;
    --tw-translate-x: 0;
    --tw-translate-y: 0;
    --tw-rotate: 0;
    --tw-skew-x: 0;
    --tw-skew-y: 0;
    --tw-scale-x: 1;
    --tw-scale-y: 1;
    --tw-pan-x:  ;
    --tw-pan-y:  ;
    --tw-pinch-zoom:  ;
    --tw-scroll-snap-strictness: proximity;
    --tw-gradient-from-position:  ;
    --tw-gradient-via-position:  ;
    --tw-gradient-to-position:  ;
    --tw-ordinal:  ;
    --tw-slashed-zero:  ;
    --tw-numeric-figure:  ;
    --tw-numeric-spacing:  ;
    --tw-numeric-fraction:  ;
    --tw-ring-inset:  ;
    --tw-ring-offset-width: 0px;
    --tw-ring-offset-color: #fff;
    --tw-ring-color: rgb(59 130 246 / 0.5);
    --tw-ring-offset-shadow: 0 0 #0000;
    --tw-ring-shadow: 0 0 #0000;
    --tw-shadow: 0 0 #0000;
    --tw-shadow-colored: 0 0 #0000;
    --tw-blur:  ;
    --tw-brightness:  ;
    --tw-contrast:  ;
    --tw-grayscale:  ;
    --tw-hue-rotate:  ;
    --tw-invert:  ;
    --tw-saturate:  ;
    --tw-sepia:  ;
    --tw-drop-shadow:  ;
    --tw-backdrop-blur:  ;
    --tw-backdrop-brightness:  ;
    --tw-backdrop-contrast:  ;
    --tw-backdrop-grayscale:  ;
    --tw-backdrop-hue-rotate:  ;
    --tw-backdrop-invert:  ;
    --tw-backdrop-opacity:  ;
    --tw-backdrop-saturate:  ;
    --tw-backdrop-sepia:  ;
    --tw-contain-size:  ;
    --tw-contain-layout:  ;
    --tw-contain-paint:  ;
    --tw-contain-style:                                         
;
  }

  .relative {
    position: relative;
  }

  .mx-1 {
    margin-left: 0.25rem;
    margin-right: 0.25rem;
  }

  .mb-2 {
    margin-bottom: 0.5rem;
  }

  .mt-3 {
    margin-top: 0.75rem;
  }

  .flex {
    display: flex;
  }

  .table {
    display: table;
  }

  .grid {
    display: grid;
  }

  .h-4 {
    height: 1rem;
  }

  .w-1\/2 {
    width: 50%;
  }

  .w-4 {
    width: 1rem;
  }

  .w-full {
    width: 100%;
  }

  .flex-col {
    flex-direction: column;
  }

  .items-center {
    align-items: center;
  }

  .justify-center {
    justify-content: center;
  }

  .overflow-x-auto {
    overflow-x: auto;
  }

  .whitespace-nowrap {
    white-space: nowrap;
  }

  .rounded-full {
    border-radius: 9999px;
  }

  .rounded-l-full {
    border-top-left-radius: 9999px;
    border-bottom-left-radius: 9999px;
  }

  .rounded-r-full {
    border-top-right-radius: 9999px;
    border-bottom-right-radius: 9999px;
  }

  .border-2 {
    border-width: 2px;
  }

  .border-b {
    border-bottom-width: 1px;
  }

  .border-gray-200 {
    --tw-border-opacity: 1;
    border-color: rgb(229 231 235 / var(--tw-border-opacity));
  }

  .bg-gray-200 {
    --tw-bg-opacity: 1;
    background-color: rgb(229 231 235 / var(--tw-bg-opacity));
  }

  .bg-gray-50 {
    --tw-bg-opacity: 1;
    background-color: rgb(249 250 251 / var(--tw-bg-opacity));
  }

  .bg-white {
    --tw-bg-opacity: 1;
    background-color: rgb(255 255 255 / var(--tw-bg-opacity));
  }

  .px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .px-6 {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .py-2 {
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }

  .py-3 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }

  .py-4 {
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .text-left {
    text-align: left;
  }

  .text-center {
    text-align: center;
  }

  .text-right {
    text-align: right;
  }

  .font-mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
  }

  .text-lg {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }

  .text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }

  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }

  .font-medium {
    font-weight: 500;
  }

  .uppercase {
    text-transform: uppercase;
  }

  .leading-none {
    line-height: 1;
  }

  .text-blue-400 {
    --tw-text-opacity: 1;
    color: rgb(96 165 250 / var(--tw-text-opacity));
  }

  .text-gray-500 {
    --tw-text-opacity: 1;
    color: rgb(107 114 128 / var(--tw-text-opacity));
  }

  .text-gray-700 {
    --tw-text-opacity: 1;
    color: rgb(55 65 81 / var(--tw-text-opacity));
  }

  .text-gray-900 {
    --tw-text-opacity: 1;
    color: rgb(17 24 39 / var(--tw-text-opacity));
  }

  .transition-colors {
    transition-property: color, background-color, border-color,
      text-decoration-color, fill, stroke;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
  }

  .duration-300 {
    transition-duration: 300ms;
  }

  .ease-in {
    transition-timing-function: cubic-bezier(0.4, 0, 1, 1);
  }

  .hover\:text-orange-600:hover {
    --tw-text-opacity: 1;
    color: rgb(234 88 12 / var(--tw-text-opacity));
  }

  .focus\:text-orange-600:focus {
    --tw-text-opacity: 1;
    color: rgb(234 88 12 / var(--tw-text-opacity));
  }

  .focus\:outline-none:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
  }

  .rtl\:text-right:where([dir="rtl"], [dir="rtl"] *) {
    text-align: right;
  }

  @media (prefers-color-scheme: dark) {
    .dark\:border-gray-700 {
      --tw-border-opacity: 1;
      border-color: rgb(55 65 81 / var(--tw-border-opacity));
    }

    .dark\:bg-gray-700 {
      --tw-bg-opacity: 1;
      background-color: rgb(55 65 81 / var(--tw-bg-opacity));
    }

    .dark\:bg-gray-800 {
      --tw-bg-opacity: 1;
      background-color: rgb(31 41 55 / var(--tw-bg-opacity));
    }

    .dark\:text-gray-400 {
      --tw-text-opacity: 1;
      color: rgb(156 163 175 / var(--tw-text-opacity));
    }

    .dark\:text-white {
      --tw-text-opacity: 1;
      color: rgb(255 255 255 / var(--tw-text-opacity));
    }
  }
</style>
