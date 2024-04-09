<script>
  import { createEventDispatcher } from "svelte";

  import Sequence from "./Sequence.svelte";
  import SearchInput from "./SearchInput.svelte";
  import Molecule from "./Molecule.svelte";

  const dispatch = createEventDispatcher();

  export let vals = [];

  export let covMods = [];

  let showCovModVals = [];
  $: {
    if (covMods) {
      // iterate over each val
      showCovModVals = vals.map((val) => {
        // check if val is in covMods and return index in CovMods or null
        return covMods.findIndex((covMod) => covMod.ligand === val.chain);
        // if index is not -1 return true else false

        // return covMods.some((covMod) => covMod.ligand === val.chain);
      });

      // dispatch("updateCovMod", covMods);
    }
  }

  let labels = {
    DNA: "NA sequence",
    RNA: "NA sequence",
    protein: "Protein sequence",
    ligand: "Small molecule",
  };

  let colorCode = {
    DNA: "bg-green-200 text-blue-800",
    RNA: "bg-green-200 text-blue-800",
    protein: "bg-blue-200 text-blue-800",
    ligand: "bg-orange-200 text-blue-800",
  };

  let metals = [
    "ZN",
    "MG",
    "CA",
    "FE",
    "NA",
    "K",
    "CL",
    "CU",
    "MN",
    "CO",
    "NI",
  ];

  let proteinChains = [];

  $: proteinChains = vals
    .filter((val) => val.class === "protein")
    .map((val) => val.chain);

  let ligandChains = [];

  $: ligandChains = vals
    .filter((val) => val.class === "ligand")
    .map((val) => val.chain);

  let residue_atoms = {
    A: ["C", "CA", "CB", "N", "O"],
    R: ["C", "CA", "CB", "CG", "CD", "CZ", "N", "NE", "O", "NH1", "NH2"],
    D: ["C", "CA", "CB", "CG", "N", "O", "OD1", "OD2"],
    N: ["C", "CA", "CB", "CG", "N", "ND2", "O", "OD1"],
    C: ["C", "CA", "CB", "N", "O", "SG"],
    E: ["C", "CA", "CB", "CG", "CD", "N", "O", "OE1", "OE2"],
    N: ["C", "CA", "CB", "CG", "CD", "N", "NE2", "O", "OE1"],
    G: ["C", "CA", "N", "O"],
    H: ["C", "CA", "CB", "CG", "CD2", "CE1", "N", "ND1", "NE2", "O"],
    I: ["C", "CA", "CB", "CG1", "CG2", "CD1", "N", "O"],
    L: ["C", "CA", "CB", "CG", "CD1", "CD2", "N", "O"],
    K: ["C", "CA", "CB", "CG", "CD", "CE", "N", "NZ", "O"],
    M: ["C", "CA", "CB", "CG", "CE", "N", "O", "SD"],
    F: ["C", "CA", "CB", "CG", "CD1", "CD2", "CE1", "CE2", "CZ", "N", "O"],
    P: ["C", "CA", "CB", "CG", "CD", "N", "O"],
    S: ["C", "CA", "CB", "N", "O", "OG"],
    T: ["C", "CA", "CB", "CG2", "N", "O", "OG1"],
    W: [
      "C",
      "CA",
      "CB",
      "CG",
      "CD1",
      "CD2",
      "CE2",
      "CE3",
      "CZ2",
      "CZ3",
      "CH2",
      "N",
      "NE1",
      "O",
    ],
    Y: [
      "C",
      "CA",
      "CB",
      "CG",
      "CD1",
      "CD2",
      "CE1",
      "CE2",
      "CZ",
      "N",
      "O",
      "OH",
    ],
    V: ["C", "CA", "CB", "CG1", "CG2", "N", "O"],
  };

  let resmap = {
    H: "HIS",
    A: "ALA",
    R: "ARG",
    N: "ASN",
    D: "ASP",
    C: "CYS",
    E: "GLU",
    Q: "GLN",
    G: "GLY",
    H: "HIS",
    I: "ILE",
    L: "LEU",
    K: "LYS",
    M: "MET",
    F: "PHE",
    P: "PRO",
    S: "SER",
    T: "THR",
    W: "TRP",
    Y: "TYR",
    V: "VAL",
  };

  function getResAtoms(covMod) {
    // get sequence of matching protein chain
    let seq = vals.find((val) => val.chain === covMod.protein).sequence;

    //do something if sequence is too short
    if (seq.length < covMod.residue) {
      alert("Residue number is too high");
      return [];
    }
    // get residue
    let residue = seq[covMod.residue - 1];
    // get atoms
    return residue_atoms[residue];
  }

  function getResidues(covMod) {
    // get sequence of matching protein chain
    let seq = vals.find((val) => val.chain === covMod.protein).sequence;

    // map single letters to three letter residues
    return Array.from(seq).map((residue) => resmap[residue]);
  }

  function getResname(covMod) {
    // get sequence of matching protein chain
    let seq = vals.find((val) => val.chain === covMod.protein).sequence;
    // get residue
    let residue = seq[covMod.residue - 1];
    // get atoms
    return resmap[residue];
  }

  function updateMol(event) {
    let index = event.detail.index;
    covMods[index].mol = event.detail.mol;
    covMods[index].attachmentIndex = event.detail.attachmentIndex;
    covMods[index].deleteIndexes = event.detail.deleteIndexes;

    dispatch("updateCovMod", covMods);
  }

  function handleMessage(event) {
    // fetch sdf content from https://files.rcsb.org/ligands/download/{name}_ideal.sdf
    // alert(event.detail.text);

    fetch(
      `https://files.rcsb.org/ligands/download/${event.detail.text}_ideal.sdf`
    )
      .then((response) => {
        if (!response.ok) {
          // Check if the status code is 200
          throw new Error("Network response was not ok");
        }
        return response.text();
      })
      .then((data) => {
        dispatch("updateVals", {
          sdf: data,
          index: event.detail.index,
          close: true,
        });
      })
      .catch((error) => {
        alert("Error fetching sdf file");
      });
  }
</script>

<div id="accordion-collapse" data-accordion="collapse">
  {#each vals as item, i}
    <h2 id={`accordion-collapse-heading-${i}`}>
      <button
        type="button"
        class="flex items-center justify-between w-full p-5 font-medium rtl:text-right text-gray-500 border border-gray-200 dark:border-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 gap-3"
        data-accordion-target={`#accordion-collapse-body-${i}`}
        class:rounded-t-xl={i === 0}
        class:rounded-b-xl={i == vals.length - 1}
        class:border-b-0={i != vals.length - 1}
        aria-expanded={item.open}
        aria-controls={`accordion-collapse-body-${i}`}
        on:click={() => (item.open = !item.open)}
      >
        <div>
          <span
            class="inline-flex items-center justify-center p-1 px-2 text-xs font-semibold rounded-full {colorCode[
              item.class
            ]}"
          >
            {item.chain}
          </span>
          <span>{labels[item.class]}</span>
          <span class="px-2 text-gray-800 font-bold">
            {#if !item.open && item.class === "ligand"}
              {#if metals.includes(item.name)}
                {item.name}
              {:else}
                {item.smiles}
              {/if}
            {/if}
          </span>
        </div>

        <div class="flex items-center space-x-2">
          <svg
            data-slot="icon"
            fill="none"
            stroke-width="3"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
            class="w-4 h-4 text-red-800"
            on:click={(e) => {
              dispatch("removeVal", i);
            }}
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18 18 6M6 6l12 12"
            ></path>
          </svg>

          <svg
            data-accordion-icon
            class="w-3 h-3 shrink-0"
            class:rotate-180={item.open}
            class:-rotate-90={!item.open}
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 10 6"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5 5 1 1 5"
            />
          </svg>
        </div>
      </button>
    </h2>

    {#if item.open}
      <div
        id={`accordion-collapse-body-${i}`}
        aria-labelledby={`accordion-collapse-heading-${i}`}
      >
        <div
          class="p-5 border border-t-0 border-gray-200 dark:border-gray-700 dark:bg-gray-900"
        >
          {#if ["DNA", "RNA", "protein"].includes(item.class)}
            <textarea
              id="message"
              rows="4"
              class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="MSAVGH..."
              value={item.sequence}
              on:input={(e) => {
                //   vals[i].sequence = e.target.value;
                dispatch("updateVals", { sequence: e.target.value, index: i });
              }}
            ></textarea>
          {:else if item.class === "ligand"}
            <textarea
              rows="1"
              class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="SMILES like CCC ..."
              value={item.smiles}
              on:input={(e) => {
                //   vals[i].sequence = e.target.value;
                dispatch("updateVals", { smiles: e.target.value, index: i });
              }}
            ></textarea>

            <div class="text-center text-gray-400 w-full my-2">- or -</div>

            <SearchInput
              database="rcsb-3ligand"
              index={i}
              on:triggerFetch={handleMessage}
            />

            <div class="text-center text-gray-400 w-full my-2">- or -</div>

            <textarea
              rows="3"
              class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
              placeholder="SDF format 3D molecule ..."
              value={item.sdf}
              on:input={(e) => {
                //   vals[i].sequence = e.target.value;
                dispatch("updateVals", { sdf: e.target.value, index: i });
              }}
            ></textarea>

            <div class="text-center text-gray-400 w-full my-2">- or -</div>

            <div class="text-center text-gray-600 font-bold mb-2">
              Metal ion
            </div>

            <div class="flex justify-center space-x-2">
              {#each metals as metal}
                <button
                  class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden rounded-full dark:bg-gray-600"
                  class:bg-blue-200={item.name === metal}
                  class:bg-violet-100={item.name !== metal}
                  on:click={() =>
                    dispatch("updateVals", { name: metal, index: i })}
                >
                  <span class="font-medium text-gray-600 dark:text-gray-300"
                    >{metal}</span
                  >
                </button>
              {/each}
            </div>
          {/if}

          <!-- <div class="text-center text-gray-400 w-full my-2">- or -</div>

          <label
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white hidden"
            for="file_input">Upload file</label
          >
          <input
            class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
            aria-describedby="file_input_help"
            id="file_input"
            type="file"
          />
          <p
            class="mt-1 text-sm text-gray-500 dark:text-gray-300"
            id="file_input_help"
          >
            .fasta files
          </p> -->
        </div>
      </div>
    {/if}
    {#if !item.open}
      {#if ["DNA", "RNA", "protein"].includes(item.class)}
        <div
          id={`accordion-collapse-body-${i}`}
          aria-labelledby={`accordion-collapse-heading-${i}`}
        >
          <div
            class="p-5 border border-t-0 border-gray-200 dark:border-gray-700"
            class:border-b-0={i != vals.length - 1}
          >
            {#if item.sequence !== ""}
              <Sequence seq={item.sequence} />
            {/if}
          </div>
        </div>
      {:else if item.class === "ligand"}
        {#if item.sdf !== ""}
          <div
            class="p-5 border border-t-0 border-gray-200 dark:border-gray-700"
            class:border-b-0={i != vals.length - 1}
          >
            <div class="relative">
              <Molecule
                molvalue={item.sdf}
                showCovMod={showCovModVals[i]}
                on:updateMol={updateMol}
              />
            </div>
          </div>
          <!-- {:else if metals.includes(item.name)}
          {item.name}
        {:else}
          {item.smiles} -->
        {/if}
      {/if}
    {/if}
  {/each}

  <div
    class="p-5 border border-t-0 border-gray-200 dark:border-gray-700 w-full"
  >
    {#if covMods.length > 0}
      <h4 class="text-center font-bold text-xl">Covalent Modification</h4>
      {#each covMods as covMod, i}
        <div class="flex p-10">
          <div class="flex divide-x rounded border p-1 w-full">
            <div class="w-3/5 flex-col px-2">
              <div class="flex justify-center">
                <span class="text-base font-medium text-gray-900">Protein</span>
              </div>
              <div class="grid grid-cols-4 font-bold">
                <span>Chain</span>
                <span>Residue</span>
                <span>Atom</span>
                <span>Chirality</span>
              </div>
              <div class="grid grid-cols-4">
                <select
                  name=""
                  id=""
                  bind:value={covMods[i].protein}
                  on:change={() => dispatch("updateCovMod", covMods)}
                >
                  {#each proteinChains as chain}
                    <option value={chain}>{chain}</option>
                  {/each}
                </select>

                <select
                  name=""
                  id=""
                  bind:value={covMods[i].residue}
                  on:change={() => dispatch("updateCovMod", covMods)}
                >
                  {#each getResidues(covMod) as resi, i}
                    <option value={i + 1}>{i + 1} {resi}</option>
                  {/each}
                </select>

                <select
                  name=""
                  id=""
                  bind:value={covMods[i].atom}
                  on:change={() => dispatch("updateCovMod", covMods)}
                >
                  {#if covMod.residue != ""}
                    {#each getResAtoms(covMod) as atom}}
                      <option value={atom}>{getResname(covMod)}:{atom}</option>
                    {/each}
                  {:else}
                    <option disabled></option>
                  {/if}
                </select>

                <select
                  name=""
                  id=""
                  bind:value={covMods[i].protein_symmetry}
                  on:change={() => dispatch("updateCovMod", covMods)}
                >
                  <option value="">no chirality defined</option>
                  <option value="CW">CW</option>
                  <option value="CCW">CCW</option>
                </select>
              </div>
            </div>

            <div class="w-2/5 px-2">
              <div class="flex-col p-1">
                <div class="flex justify-center">
                  <span
                    class="w-full whitespace-nowrap text-center text-base font-medium text-gray-900"
                    >Small molecule</span
                  >
                </div>
                <div class="grid grid-cols-3 font-bold">
                  <span>Chain</span>
                  <span title="click on atom in structure">Atom index </span>

                  <span>Chirality</span>
                </div>
                <div class="grid grid-cols-3">
                  <select
                    name=""
                    id=""
                    title="click on atom in structure"
                    bind:value={covMods[i].ligand}
                    on:change={() => dispatch("updateCovMod", covMods)}
                  >
                    {#each ligandChains as chain}
                      <option value={chain} selected={chain === covMod.ligand}
                        >{chain}</option
                      >
                    {/each}
                  </select>
                  <div>
                    {#if covMod.attachmentIndex}
                      <p class="font-mono">index {covMod.attachmentIndex}</p>
                    {:else}
                      <p class="font-mono">click on atom</p>
                    {/if}
                  </div>

                  <select
                    name=""
                    id=""
                    bind:value={covMods[i].ligand_symmetry}
                    on:change={() => dispatch("updateCovMod", covMods)}
                  >
                    <option value="">no chirality defined</option>
                    <option value="CW">CW</option>
                    <option value="CCW">CCW</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center p-2">
            <svg
              data-slot="icon"
              fill="none"
              stroke-width="2"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
              class="w-8 h-8 text-red-800 cursor-pointer"
              on:click={(e) => {
                dispatch("removeCovMod", i);
              }}
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M6 18 18 6M6 6l12 12"
              ></path>
            </svg>
          </div>
        </div>
      {/each}
    {/if}
  </div>
  <!-- 
  <h2 id="accordion-collapse-heading-2">
    <button
      type="button"
      class="flex items-center justify-between w-full p-5 font-medium rtl:text-right text-gray-500 border border-b-0 border-gray-200 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-800 dark:border-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 gap-3"
      data-accordion-target="#accordion-collapse-body-2"
      aria-expanded="false"
      aria-controls="accordion-collapse-body-2"
    >
      <div>
        <span
          class="inline-flex items-center justify-center p-1 px-2 text-xs font-semibold text-blue-800 bg-blue-200 rounded-full"
        >
          A
        </span>
        <span>NA sequence</span>
      </div>
      <svg
        data-accordion-icon
        class="w-3 h-3 -rotate-90 shrink-0"
        aria-hidden="true"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 10 6"
      >
        <path
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 5 5 1 1 5"
        />
      </svg>
    </button>
    <div class="px-2">
      <Sequence />
    </div>
  </h2>

  <div
    id="accordion-collapse-body-2"
    class="hidden"
    aria-labelledby="accordion-collapse-heading-2"
  >
    <div
      class="p-5 border border-b-0 border-gray-200 dark:border-gray-700"
    ></div>
  </div>
  <h2 id="accordion-collapse-heading-3">
    <button
      type="button"
      class="flex items-center justify-between w-full p-5 font-medium rtl:text-right text-gray-500 border border-gray-200 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-800 dark:border-gray-700 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 gap-3"
      data-accordion-target="#accordion-collapse-body-3"
      aria-expanded="false"
      aria-controls="accordion-collapse-body-3"
    >
      <div>
        <span
          class="inline-flex items-center justify-center p-1 px-2 text-xs font-semibold text-blue-800 bg-orange-200 rounded-full"
        >
          C
        </span>
        <span>Small molecule</span>
      </div>
      <svg
        data-accordion-icon
        class="w-3 h-3 rotate-180 shrink-0"
        aria-hidden="true"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 10 6"
      >
        <path
          stroke="currentColor"
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 5 5 1 1 5"
        />
      </svg>
    </button>
  </h2>
  <div
    id="accordion-collapse-body-3"
    aria-labelledby="accordion-collapse-heading-3"
  >
    <div class="p-5 border border-t-0 border-gray-200 dark:border-gray-700">
      <label
        class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
        for="file_input">Upload file</label
      >
      <input
        class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
        aria-describedby="file_input_help"
        id="file_input"
        type="file"
      />
      <p
        class="mt-1 text-sm text-gray-500 dark:text-gray-300"
        id="file_input_help"
      >
        SVG, PNG, JPG or GIF (MAX. 800x400px).
      </p>
      <div class="text-center text-gray-400 w-full my-2">- or -</div>

      <textarea
        id="message"
        rows="4"
        class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        placeholder="SMILES like CCC ..."
      ></textarea>

      <div class="text-center text-gray-400 w-full my-2">- or -</div>

      <SearchInput database="rcsb-3ligand" />

      <div class="text-center text-gray-400 w-full my-2">- or -</div>

      <div class="text-center text-gray-600 font-bold mb-2">Metal ion</div>
      <div class="flex justify-center space-x-2">
        <div
          class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden bg-violet-100 rounded-full dark:bg-gray-600"
        >
          <span class="font-medium text-gray-600 dark:text-gray-300">ZN</span>
        </div>

        <div
          class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden bg-green-100 rounded-full dark:bg-gray-600"
        >
          <span class="font-medium text-gray-600 dark:text-gray-300">MG</span>
        </div>

        <div
          class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden bg-green-100 rounded-full dark:bg-gray-600"
        >
          <span class="font-medium text-gray-600 dark:text-gray-300">CA</span>
        </div>

        <div
          class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden bg-violet-100 rounded-full dark:bg-gray-600"
        >
          <span class="font-medium text-gray-600 dark:text-gray-300">FE</span>
        </div>

        <div
          class="relative inline-flex items-center justify-center w-10 h-10 overflow-hidden bg-yellow-100 rounded-full dark:bg-gray-600"
        >
          <span class="font-medium text-gray-600 dark:text-gray-300">NA</span>
        </div>
      </div>
    </div>
  </div> 

   -->
</div>

<style>
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

  .collapse {
    visibility: collapse;
  }

  .relative {
    position: relative;
  }

  .my-2 {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .mb-2 {
    margin-bottom: 0.5rem;
  }

  .mt-1 {
    margin-top: 0.25rem;
  }

  .block {
    display: block;
  }

  .flex {
    display: flex;
  }

  .inline-flex {
    display: inline-flex;
  }

  .grid {
    display: grid;
  }

  .hidden {
    display: none;
  }

  .h-10 {
    height: 2.5rem;
  }

  .h-3 {
    height: 0.75rem;
  }

  .h-4 {
    height: 1rem;
  }

  .w-10 {
    width: 2.5rem;
  }

  .w-2\/5 {
    width: 40%;
  }

  .w-3 {
    width: 0.75rem;
  }

  .w-3\/5 {
    width: 60%;
  }

  .w-4 {
    width: 1rem;
  }

  .w-8 {
    width: 2rem;
  }

  .w-full {
    width: 100%;
  }

  .shrink-0 {
    flex-shrink: 0;
  }

  .-rotate-90 {
    --tw-rotate: -90deg;
    transform: translate(var(--tw-translate-x), var(--tw-translate-y))
      rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
      scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  }

  .rotate-180 {
    --tw-rotate: 180deg;
    transform: translate(var(--tw-translate-x), var(--tw-translate-y))
      rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y))
      scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
  }

  .cursor-pointer {
    cursor: pointer;
  }

  .grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
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

  .justify-between {
    justify-content: space-between;
  }

  .gap-3 {
    gap: 0.75rem;
  }

  .space-x-2 > :not([hidden]) ~ :not([hidden]) {
    --tw-space-x-reverse: 0;
    margin-right: calc(0.5rem * var(--tw-space-x-reverse));
    margin-left: calc(0.5rem * calc(1 - var(--tw-space-x-reverse)));
  }

  .divide-x > :not([hidden]) ~ :not([hidden]) {
    --tw-divide-x-reverse: 0;
    border-right-width: calc(1px * var(--tw-divide-x-reverse));
    border-left-width: calc(1px * calc(1 - var(--tw-divide-x-reverse)));
  }

  .overflow-hidden {
    overflow: hidden;
  }

  .whitespace-nowrap {
    white-space: nowrap;
  }

  .rounded {
    border-radius: 0.25rem;
  }

  .rounded-full {
    border-radius: 9999px;
  }

  .rounded-lg {
    border-radius: 0.5rem;
  }

  .border {
    border-width: 1px;
  }

  .border-b-0 {
    border-bottom-width: 0px;
  }

  .border-t-0 {
    border-top-width: 0px;
  }

  .border-gray-200 {
    --tw-border-opacity: 1;
    border-color: rgb(229 231 235 / var(--tw-border-opacity));
  }

  .border-gray-300 {
    --tw-border-opacity: 1;
    border-color: rgb(209 213 219 / var(--tw-border-opacity));
  }

  .bg-blue-200 {
    --tw-bg-opacity: 1;
    background-color: rgb(191 219 254 / var(--tw-bg-opacity));
  }

  .bg-gray-50 {
    --tw-bg-opacity: 1;
    background-color: rgb(249 250 251 / var(--tw-bg-opacity));
  }

  .bg-green-100 {
    --tw-bg-opacity: 1;
    background-color: rgb(220 252 231 / var(--tw-bg-opacity));
  }

  .bg-orange-200 {
    --tw-bg-opacity: 1;
    background-color: rgb(254 215 170 / var(--tw-bg-opacity));
  }

  .bg-violet-100 {
    --tw-bg-opacity: 1;
    background-color: rgb(237 233 254 / var(--tw-bg-opacity));
  }

  .bg-yellow-100 {
    --tw-bg-opacity: 1;
    background-color: rgb(254 249 195 / var(--tw-bg-opacity));
  }

  .p-1 {
    padding: 0.25rem;
  }

  .p-10 {
    padding: 2.5rem;
  }

  .p-2 {
    padding: 0.5rem;
  }

  .p-2\.5 {
    padding: 0.625rem;
  }

  .p-5 {
    padding: 1.25rem;
  }

  .px-2 {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }

  .px-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }

  .text-center {
    text-align: center;
  }

  .font-mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
      "Liberation Mono", "Courier New", monospace;
  }

  .text-base {
    font-size: 1rem;
    line-height: 1.5rem;
  }

  .text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }

  .text-xl {
    font-size: 1.25rem;
    line-height: 1.75rem;
  }

  .text-xs {
    font-size: 0.75rem;
    line-height: 1rem;
  }

  .font-bold {
    font-weight: 700;
  }

  .font-medium {
    font-weight: 500;
  }

  .font-semibold {
    font-weight: 600;
  }

  .text-blue-800 {
    --tw-text-opacity: 1;
    color: rgb(30 64 175 / var(--tw-text-opacity));
  }

  .text-gray-400 {
    --tw-text-opacity: 1;
    color: rgb(156 163 175 / var(--tw-text-opacity));
  }

  .text-gray-500 {
    --tw-text-opacity: 1;
    color: rgb(107 114 128 / var(--tw-text-opacity));
  }

  .text-gray-600 {
    --tw-text-opacity: 1;
    color: rgb(75 85 99 / var(--tw-text-opacity));
  }

  .text-gray-800 {
    --tw-text-opacity: 1;
    color: rgb(31 41 55 / var(--tw-text-opacity));
  }

  .text-gray-900 {
    --tw-text-opacity: 1;
    color: rgb(17 24 39 / var(--tw-text-opacity));
  }

  .text-red-800 {
    --tw-text-opacity: 1;
    color: rgb(153 27 27 / var(--tw-text-opacity));
  }

  .hover\:bg-gray-100:hover {
    --tw-bg-opacity: 1;
    background-color: rgb(243 244 246 / var(--tw-bg-opacity));
  }

  .focus\:border-blue-500:focus {
    --tw-border-opacity: 1;
    border-color: rgb(59 130 246 / var(--tw-border-opacity));
  }

  .focus\:outline-none:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
  }

  .focus\:ring-4:focus {
    --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0
      var(--tw-ring-offset-width) var(--tw-ring-offset-color);
    --tw-ring-shadow: var(--tw-ring-inset) 0 0 0
      calc(4px + var(--tw-ring-offset-width)) var(--tw-ring-color);
    box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow),
      var(--tw-shadow, 0 0 #0000);
  }

  .focus\:ring-blue-500:focus {
    --tw-ring-opacity: 1;
    --tw-ring-color: rgb(59 130 246 / var(--tw-ring-opacity));
  }

  .focus\:ring-gray-200:focus {
    --tw-ring-opacity: 1;
    --tw-ring-color: rgb(229 231 235 / var(--tw-ring-opacity));
  }

  .rtl\:text-right:where([dir="rtl"], [dir="rtl"] *) {
    text-align: right;
  }

  @media (prefers-color-scheme: dark) {
    .dark\:border-gray-600 {
      --tw-border-opacity: 1;
      border-color: rgb(75 85 99 / var(--tw-border-opacity));
    }

    .dark\:border-gray-700 {
      --tw-border-opacity: 1;
      border-color: rgb(55 65 81 / var(--tw-border-opacity));
    }

    .dark\:bg-gray-600 {
      --tw-bg-opacity: 1;
      background-color: rgb(75 85 99 / var(--tw-bg-opacity));
    }

    .dark\:bg-gray-700 {
      --tw-bg-opacity: 1;
      background-color: rgb(55 65 81 / var(--tw-bg-opacity));
    }

    .dark\:bg-gray-900 {
      --tw-bg-opacity: 1;
      background-color: rgb(17 24 39 / var(--tw-bg-opacity));
    }

    .dark\:text-gray-300 {
      --tw-text-opacity: 1;
      color: rgb(209 213 219 / var(--tw-text-opacity));
    }

    .dark\:text-gray-400 {
      --tw-text-opacity: 1;
      color: rgb(156 163 175 / var(--tw-text-opacity));
    }

    .dark\:text-white {
      --tw-text-opacity: 1;
      color: rgb(255 255 255 / var(--tw-text-opacity));
    }

    .dark\:placeholder-gray-400::placeholder {
      --tw-placeholder-opacity: 1;
      color: rgb(156 163 175 / var(--tw-placeholder-opacity));
    }

    .dark\:hover\:bg-gray-800:hover {
      --tw-bg-opacity: 1;
      background-color: rgb(31 41 55 / var(--tw-bg-opacity));
    }

    .dark\:focus\:border-blue-500:focus {
      --tw-border-opacity: 1;
      border-color: rgb(59 130 246 / var(--tw-border-opacity));
    }

    .dark\:focus\:ring-blue-500:focus {
      --tw-ring-opacity: 1;
      --tw-ring-color: rgb(59 130 246 / var(--tw-ring-opacity));
    }

    .dark\:focus\:ring-gray-800:focus {
      --tw-ring-opacity: 1;
      --tw-ring-color: rgb(31 41 55 / var(--tw-ring-opacity));
    }
  }
</style>
