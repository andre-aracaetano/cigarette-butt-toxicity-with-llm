# -*- coding: utf-8 -*-

import pandas as pd
import ollama
import os

output_path = "extractions_gpt_120_medium.xlsx"


df = pd.read_excel(
    "df_benchmark.xlsx",
    engine="openpyxl"
)

if os.path.exists(output_path):
    out_df = pd.read_excel(output_path, engine="openpyxl")
    start_index = len(out_df)
    results = out_df.to_dict("records")
else:
    start_index = 0
    results = []

instructions = """ROLE
You extract experimental configurations from scientific abstracts about Solid Oxide Fuel Cells (SOFCs).

OBJECTIVE
Return every experimental configuration that is explicitly tested/used in the abstract-linking cathode, anode, electrolyte, and (when reported) its power density and measurement temperature.

STRICT OUTPUT CONTRACT
- Output a single JSON object with exactly these keys:
  { "cathode": [...], "anode": [...], "electrolyte": [...], "power_density": [...], "temperature": [...] }
- All arrays must have the same length. Index i across arrays refers to the same configuration.
- Use null (not the string "None") when a field is unknown/missing for a given configuration.
- No extra text before or after the JSON.

HOW TO FORM CONFIGURATIONS
1) Pair only what the abstract explicitly links experimentally. Do not infer pairings from background or unrelated mentions.
2) Prefer full triplets (cathode-anode-electrolyte). If a role is not stated, create a partial configuration with null in that role.
3) If the text tests multiple options for a single role against fixed counterparts, emit one configuration per option (preserving any stated pairings).
4) Never "cross-match" materials that the text does not explicitly test together.
5) Composite within a single role: represent as "A + B" (e.g., "Ni + Yttria-stabilized zirconia (YSZ)").

POWER DENSITY & TEMPERATURE (PER CONFIGURATION)
- Extract power density only if it is clearly attributable to that configuration.
- Accept and normalize unit strings to "mW/cm2" or "W/cm2" (e.g., convert "mW cm-2", "mW/cm^2", "mW cm(-2)" -> "mW/cm2"). Keep the reported numeric value.
- Temperature format: "<number> degrees C" (convert from "degrees C" to the text form).
- If multiple PD/temperature pairs are given for the same configuration, choose the numerically highest PD; on ties, choose the lowest temperature among tied PDs.
- If PD is present without temperature, set temperature to null; if temperature is present without PD, set power_density to null.

MATERIAL NAMING (EACH MENTION)
- Goal: "Formula (ABBR)" whenever possible.
  - If an explicit formula appears, prefer it: e.g., "La0.6Sr0.4Co0.2Fe0.8O3 (LSCF)".
  - If no formula is given or unambiguous, use a canonical chemical name + abbreviation: e.g., "Yttria-stabilized zirconia (YSZ)".
  - If a standard abbreviation is known or given, include it in parentheses.
  - If no abbreviation is standard or provided, output just the formula or canonical name (no parentheses), e.g., "Ni".
- Do not invent stoichiometries, d values, or site occupancies absent from the text. If only "Gd-doped ceria" is stated, do not fabricate ratios.
- Grouped dopants/families (e.g., "Ce(Ln)O2-d (Ln = Pr, Sm, Gd)"):
  Expand into distinct variants and emit separate configurations when those variants are actually tested; otherwise emit separate material mentions within the appropriate role with other roles set to null.

SCOPE & CAUTION
- Extract only materials used/tested as cathode, anode, or electrolyte in the experiments described in the abstract.
- Do not infer roles, compositions, or pairings without explicit experimental context.
- Preserve the order of first appearance of configurations in the abstract.

KNOWN ABBREVIATION MAP (apply when applicable)
YSZ - Yttria-stabilized zirconia
GDC - Gd-doped ceria (gadolinia-doped ceria)
SDC - Sm-doped ceria (samaria-doped ceria)
LSM - Lanthanum strontium manganite
LSCF - Lanthanum strontium cobalt ferrite
BSCF - Barium strontium cobalt ferrite
(If an abbreviation is not in this list and not provided in the abstract, do not coin a new one.)

IF NOTHING RELEVANT IS FOUND
Return:
{"cathode": [], "anode": [], "electrolyte": [], "power_density": [], "temperature": []}

EXAMPLES

Example A (multiple cathodes; only one with PD/T)
Abstract: "The study analyzed LSM, LSCF, and BSCF as cathodes, concluding that BSCF reached 1200 mW/cm2 at 750 degrees C."
Output:
{
  "cathode": [
    "Lanthanum strontium manganite (LSM)",
    "Lanthanum strontium cobalt ferrite (LSCF)",
    "Barium strontium cobalt ferrite (BSCF)"
  ],
  "anode": [null, null, null],
  "electrolyte": [null, null, null],
  "power_density": [null, null, "1200 mW/cm2"],
  "temperature": [null, null, "750 degrees C"]
}

Example B (full triplet with PD/T)
Abstract: "A cell using La0.6Sr0.4Co0.2Fe0.8O3 (LSCF) as cathode, Ni as anode, and YSZ as electrolyte achieved 900 mW/cm(2) at 750 degrees C."
Output:
{
  "cathode": ["La0.6Sr0.4Co0.2Fe0.8O3 (LSCF)"],
  "anode": ["Ni"],
  "electrolyte": ["Yttria-stabilized zirconia (YSZ)"],
  "power_density": ["900 mW/cm2"],
  "temperature": ["750 degrees C"]
}

Example C (two anodes; best reported for one)
Abstract: "Cells with Ni-YSZ and Ni-GDC anodes were tested. The highest power density was 1.2 W/cm2 at 700 degrees C for Ni-GDC."
Output:
{
  "cathode": [null, null],
  "anode": [
    "Ni + Yttria-stabilized zirconia (YSZ)",
    "Ni + Gd-doped ceria (GDC)"
  ],
  "electrolyte": [null, null],
  "power_density": [null, "1.2 W/cm2"],
  "temperature": [null, "700 degrees C"]
}

Example D (grouped dopants; no PD/T)
Abstract: "Cathodes comprising LaNi0.6Fe0.4O3 with Ce(Ln)O2-d (Ln = Pr, Sm, Gd) were investigated."
Output:
{
  "cathode": [
    "LaNi0.6Fe0.4O3 + Pr-doped ceria (PDC)",
    "LaNi0.6Fe0.4O3 + Sm-doped ceria (SDC)",
    "LaNi0.6Fe0.4O3 + Gd-doped ceria (GDC)"
  ],
  "anode": [null, null, null],
  "electrolyte": [null, null, null],
  "power_density": [null, null, null],
  "temperature": [null, null, null]
}"""


for i in range(start_index, len(df)):
    
    
    abstract = str(df.loc[i, "abstract"]).strip()
    #phase = str(df.loc[i, "phase"]).strip()
    input_str = f"{abstract}"

    print(f"Processing {i + 1}/{len(df)}: {input_str}")

    try:
        response = ollama.chat(
            model='gpt-oss:120b',
            messages=[
                {'role': 'system', 'content': instructions},
                {'role': 'user', 'content': input_str}
            ],
            stream=False,
            think='medium',
            options={
                "temperature": 0.0,
                "seed": 42,
                "num_ctx": 23456,
            }
        )


        full_response_str = str(response)


        json_output = response.message.content.strip()

    except Exception as e:
        print(f"Erro no indice {i}: {e}")
        json_output = f"ERROR: {str(e)}"
        full_response_str = json_output


    results.append({
        "gpt_extractions": json_output,
        "gpt_full_response": full_response_str
    })

    pd.DataFrame(results).to_excel(output_path, index=False, engine="openpyxl")

print("Finalizado Resultados salvos em:", output_path)
