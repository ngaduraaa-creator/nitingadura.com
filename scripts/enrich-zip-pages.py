#!/usr/bin/env python3
"""Enrich thin ZIP-level pages with hyperlocal content.

Google flagged 12 "Discovered - currently not indexed" + 2 "Crawled - currently
not indexed" pages on nitingadura.com. The ZIP-level pages are 400-420 words of
near-identical templated content. This script adds a substantive, ZIP-specific
"Insider's Guide" block (~600 additional words per page) so each page becomes
genuinely unique content Google will index.

Idempotent — uses a marker comment to detect prior injection.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER_START = "<!-- NITIN_ZIP_INSIDER_START -->"
MARKER_END = "<!-- NITIN_ZIP_INSIDER_END -->"

# Per-ZIP hyperlocal data. Each entry has 4 unique paragraphs covering:
# (a) submarket breakdown by streets/blocks
# (b) housing stock mix and typical price bands
# (c) buyer profile fit
# (d) honest tradeoffs / warnings
ZIP_DATA: dict[str, dict[str, str]] = {
    "11414": {
        "name": "Howard Beach",
        "submarkets": "Howard Beach (11414) splits into three distinct submarkets: <strong>Old Howard Beach</strong> south of the Belt Parkway has the best Jamaica Bay water frontage and the strongest sense of community, with deep family roots; <strong>Lindenwood</strong> north of the Belt is dominated by mid-century attached and semi-attached homes with a strong owner-occupant base; <strong>Hamilton Beach</strong> is a smaller waterfront pocket with the highest flood-zone exposure but interesting waterfront opportunities for buyers comfortable with FEMA insurance costs.",
        "housing": "Detached single-family homes in Old Howard Beach typically run $1.05M–$1.6M for renovated 3-bedroom homes; Lindenwood semi-attached homes run $750K–$950K; 2-family brick homes in either submarket run $950K–$1.3M depending on lot size and rental income. Inventory turns slowly — many homes have been in the same family 30+ years.",
        "buyer": "Best fit for: families looking for backyard space and water access, multi-generational South Asian and Italian-American buyers, and small-business owners who need garage parking. JFK airport workers and air-traffic controllers are a meaningful share of demand. The neighborhood is not a fit for buyers who need a fast Manhattan commute or who want walkable nightlife.",
        "tradeoffs": "Honest tradeoffs: flood insurance is mandatory for any property in FEMA Special Flood Hazard Area X or AE — get a current FIRM-panel quote before you offer, not after. The A train is the only subway option and runs ~50–60 minutes to Midtown; LIRR access requires driving to Locust Manor or Lindenwood. Restaurants and nightlife are limited to Cross Bay Boulevard and Crossbay/Belt area pizza and red-sauce institutions.",
    },
    "11415": {
        "name": "Kew Gardens",
        "submarkets": "Kew Gardens (11415) breaks into <strong>north of Queens Boulevard</strong> with classic Tudor and English-style detached homes on tree-lined blocks, <strong>the Forest Park edge</strong> where larger detached homes back onto the park itself, and <strong>the Lefferts/Metropolitan corridor</strong> with mid-rise prewar co-op buildings. Each submarket prices and feels noticeably different.",
        "housing": "Detached Tudor-style homes north of Queens Blvd run $1.2M–$1.7M; prewar co-op 1-bedrooms in elevator buildings run $250K–$400K; 2-bedroom co-ops run $425K–$650K with maintenance typically $850–$1,400/month. Property tax for Class 1 detached homes averages $9,000–$15,000/year with strong assessment-cap protection on long-held homes.",
        "buyer": "Best fit for: families wanting detached or semi-detached character homes at meaningfully lower prices than Forest Hills, co-op buyers wanting express E/F access without Forest Hills premiums, and Bukharian Jewish community ties. The Kew Gardens–Union Turnpike E/F express stop puts Midtown at ~30 minutes.",
        "tradeoffs": "Honest tradeoffs: the LIRR Kew Gardens station has fewer trains than Forest Hills, so most LIRR commuters either use Forest Hills or drive to Jamaica. Some prewar co-op buildings have older mechanicals and may have flip taxes or strict subletting policies — read the proprietary lease and offering plan amendments carefully with a NY-licensed attorney before offering.",
    },
    "11416": {
        "name": "Ozone Park",
        "submarkets": "Ozone Park (11416) covers Old Ozone Park north of Liberty Avenue and the area east toward Woodhaven Boulevard. The blocks <strong>between 80th Street and Cross Bay Boulevard</strong> are dense with attached and semi-attached row homes; <strong>north of Liberty Avenue</strong> the housing stock turns more 2-family with deeper lots; <strong>south of Liberty toward 101st Avenue</strong> picks up commercial-residential mixed-use buildings.",
        "housing": "1-family attached row homes typically run $725K–$925K; 2-family brick homes are the dominant investment play at $1.0M–$1.4M, often with strong rental income from one unit; semi-attached 1-family homes with private driveways are the premium tier at $850K–$1.1M. Garages and private driveways are a meaningful price differentiator on tighter lots.",
        "buyer": "Best fit for: South Asian (Punjabi, Bengali, Indo-Guyanese), Latin American, and South Asian Caribbean families looking for multi-generational housing or rental income; FHA buyers using the 2-family multi-unit owner-occupant program; first-time buyers wanting a low-six-figure entry into Queens.",
        "tradeoffs": "Honest tradeoffs: the A train is the primary subway with 45–55 minute Midtown commutes during rush hour. Many 2-family homes have illegal basement units that complicate mortgage underwriting and DOB compliance — request a Certificate of Occupancy match and walk the basement with the inspector. Flood-zone overlap exists in pockets near 91st Avenue.",
    },
    "11417": {
        "name": "Tudor Village / Ozone Park",
        "submarkets": "ZIP 11417 covers <strong>Tudor Village</strong> with its distinctive Tudor-style detached homes on cul-de-sacs near 80th–84th Streets, <strong>the central Ozone Park grid</strong> with predominantly attached and semi-attached row housing, and the eastern blocks bordering Howard Beach where lots get slightly larger and detached homes appear more frequently.",
        "housing": "Tudor Village detached homes run $850K–$1.2M; attached row homes throughout the rest of 11417 run $750K–$950K; 2-family brick homes are common at $1.0M–$1.35M; semi-attached homes with private driveways command $50–$100K premiums over equivalent attached homes.",
        "buyer": "Best fit for: South Asian (Punjabi, Indian, Bangladeshi, Indo-Guyanese), Caribbean (Trinidadian, Guyanese, Jamaican), Italian-American, and South American (Ecuadorian, Colombian) families. House-hack first-time buyers using FHA on 2-family homes are a meaningful and growing buyer segment in 11417.",
        "tradeoffs": "Honest tradeoffs: A train commute, parking pressure on tighter blocks, and the same illegal-basement-unit risk found across the broader Ozone Park area. Long Island Expressway noise affects blocks near North Conduit Avenue. Flood zones touch parts of the southern blocks closer to Howard Beach.",
    },
    "11418": {
        "name": "Richmond Hill",
        "submarkets": "Richmond Hill (11418) splits between <strong>North Richmond Hill</strong> with its famous Victorian-era painted-lady detached homes from the 1880s–1920s, <strong>Central Richmond Hill</strong> along Lefferts Boulevard with a denser mix of attached row homes and 2-family brick, and the <strong>border with Forest Park</strong> where large detached homes back onto the park itself.",
        "housing": "Restored Victorian detached homes run $1.05M–$1.6M+ depending on condition and historic features; standard attached row homes run $750K–$925K; 2-family Victorian and brick homes are a strong investor and house-hacker target at $1.0M–$1.4M. Many original homes still have the wraparound porches, leaded-glass windows, and original woodwork that drive premiums.",
        "buyer": "Best fit for: Punjabi Sikh and Indian families (the area is the eastern U.S. hub for Punjabi-American real estate), Indo-Caribbean Guyanese families, Italian-American multi-generational buyers, and architecture enthusiasts willing to invest in restoration of older homes.",
        "tradeoffs": "Honest tradeoffs: Victorian homes often need substantial mechanical and electrical updates — knob-and-tube wiring, oil-to-gas conversion, and lead-paint remediation are common scope items in homes that haven't been substantially renovated since the 1980s. Pre-purchase inspection should be by an inspector who specializes in pre-1940 houses, not a general inspector.",
    },
    "11419": {
        "name": "South Richmond Hill",
        "submarkets": "South Richmond Hill (11419) is denser and more commercial than 11418. <strong>Liberty Avenue</strong> is the spine — the eastern Punjabi-American business district, with restaurants, gurdwaras, and South Asian retail. <strong>South of 101st Avenue</strong> the housing stock turns to attached and semi-attached row homes on tighter lots. <strong>Toward South Ozone Park</strong> on the western edge, 2-family brick homes dominate.",
        "housing": "1-family attached row homes typically $700K–$875K; semi-attached 1-family with private driveway $800K–$1.0M; 2-family brick $950K–$1.3M with the higher end on blocks closer to Lefferts Boulevard. Inventory is generally smaller and tighter than 11418 next door, with shorter days-on-market.",
        "buyer": "Best fit for: Punjabi, Sikh, and broader South Asian families specifically wanting walkable proximity to Liberty Avenue community life; Indo-Caribbean Guyanese families; first-time buyers using FHA on 2-family homes for the multi-unit house-hack play.",
        "tradeoffs": "Honest tradeoffs: parking pressure on Liberty Avenue corridor blocks; A train and J/Z trains run on slow schedules, with rush-hour Midtown commutes typically 50–60 minutes; some pockets have older homes with deferred maintenance requiring careful inspection.",
    },
    "11420": {
        "name": "South Ozone Park",
        "submarkets": "South Ozone Park (11420) is the heart of multi-family Queens. <strong>The Rockaway Boulevard corridor</strong> is dense commercial-residential. <strong>South of Rockaway Boulevard toward JFK</strong> the housing stock turns predominantly 2-family brick with attached driveways. <strong>The blocks closer to Aqueduct Racetrack</strong> trend toward larger 1-family and 2-family detached lots.",
        "housing": "2-family brick homes are the dominant product at $950K–$1.3M, often purchased for owner-occupant + rental income; 1-family attached row $700K–$850K; semi-attached 1-family with garage $800K–$975K. Strong rental demand from JFK workforce keeps 2-family cash flow attractive.",
        "buyer": "Best fit for: Punjabi, Indian, Indo-Guyanese, Caribbean (Trinidadian, Guyanese), and Hispanic (Ecuadorian, Dominican, Colombian) families using FHA multi-unit programs to house-hack; investor buyers targeting rental yield close to JFK; multi-generational South Asian families wanting separate-entrance basement or upstairs units.",
        "tradeoffs": "Honest tradeoffs: A train commute, JFK aircraft noise on certain wind days, ongoing illegal-conversion enforcement in pockets — verify all units have valid Certificate of Occupancy. Some blocks back onto industrial uses or commercial corridors which affects long-term resale.",
    },
    "11421": {
        "name": "Woodhaven",
        "submarkets": "Woodhaven (11421) sits between Forest Park and Atlantic Avenue. <strong>North of Jamaica Avenue</strong> blocks pick up larger detached and semi-attached homes closer to Forest Park; <strong>the Jamaica Avenue corridor</strong> mixes commercial-residential with the J/Z line elevated structure overhead; <strong>south of Atlantic Avenue</strong> attached row homes dominate, with some 2-family conversions.",
        "housing": "Detached single-family near Forest Park run $900K–$1.2M; attached row homes south of Jamaica Ave run $725K–$900K; 2-family brick run $950K–$1.25M; semi-attached homes with driveways run $800K–$1.0M. Inventory is moderate with reasonable selection.",
        "buyer": "Best fit for: South Asian (Bangladeshi, Indo-Guyanese, Indian), Caribbean, and South American families wanting Forest Park access and a J/Z train option to Manhattan; first-time buyers stepping up from co-ops; FHA 2-family house-hackers; remote-work families who only commute 1–2 days per week.",
        "tradeoffs": "Honest tradeoffs: J/Z trains run elevated above Jamaica Avenue with associated noise on north-side blocks; Atlantic Avenue commercial traffic affects southern blocks; 1880s–1920s detached homes near Forest Park often need mechanical upgrades and historic preservation considerations.",
    },
    "11423": {
        "name": "Hollis / Holliswood",
        "submarkets": "ZIP 11423 covers <strong>Hollis</strong> with its denser mix of 1-family detached on smaller lots, <strong>Holliswood</strong> further north with larger detached homes on hillier, more spacious lots, and the border zones along Hillside Avenue. The two halves price meaningfully differently — Holliswood typically commands a premium of $200–$400K over equivalent Hollis homes.",
        "housing": "Hollis 1-family detached run $725K–$925K; Holliswood detached homes on larger lots run $1.05M–$1.5M+ with some Tudor-style homes commanding $1.6M+; 2-family homes are less common in 11423 than in adjacent ZIPs. Hilly topography in Holliswood gives some blocks Manhattan skyline views.",
        "buyer": "Best fit for: Indian and Bangladeshi families (the area has deep South Asian community roots with multiple gurdwaras and mandirs), Black professional families with established neighborhood ties, families prioritizing larger lot sizes within NYC limits, and music-industry families with historical connections to the area.",
        "tradeoffs": "Honest tradeoffs: F train at 179th–Hillside is the primary subway with 35–45 minute Midtown commute; LIRR access requires driving to Hollis station; some hillier blocks have steep driveways and parking challenges; school-district variation by exact address — verify zoned schools on every offer.",
    },
    "11426": {
        "name": "Bellerose",
        "submarkets": "Bellerose (11426) is one of the easternmost Queens neighborhoods, bordering Nassau County. <strong>Bellerose Manor</strong> in the southwest pocket has the densest housing stock with attached and semi-attached homes; <strong>Central Bellerose</strong> is dominated by 1-family detached homes on standard lots with mature street trees; <strong>the Cross Island Parkway corridor</strong> has slightly larger lots and quieter blocks.",
        "housing": "Detached 1-family homes run $850K–$1.1M for standard 3–4 bedroom homes; semi-attached 1-family with driveway run $800K–$950K; the rare 2-family in 11426 commands $1.05M–$1.3M. Property tax for Class 1 is favorable thanks to long-held assessment caps on many homes.",
        "buyer": "Best fit for: families prioritizing District 26 schools (one of NYC's strongest), Indian and Bangladeshi multi-generational families, Sikh and Punjabi families, and buyers wanting suburb-feel within NYC limits with the option of LIRR Bellerose or Floral Park stations for fast Manhattan commutes.",
        "tradeoffs": "Honest tradeoffs: Manhattan commute by F train is 50–60 minutes from Hillside Avenue; LIRR Bellerose station is faster (~35 min) but adds monthly cost; the dividing line with Nassau County's Bellerose village is a few blocks away — buyers sometimes confuse the two and tax/service-area implications differ significantly.",
    },
    "11427": {
        "name": "Queens Village",
        "submarkets": "ZIP 11427 covers western and central Queens Village. <strong>Holliswood border blocks</strong> in the north have larger detached homes; <strong>the central area around Hollis Avenue</strong> has dense 1-family and semi-attached row homes; <strong>blocks closer to Jamaica</strong> in the south transition to a mix of 1-family and small 2-family.",
        "housing": "Detached 1-family homes typically run $650K–$850K; semi-attached 1-family with driveway run $675K–$825K; the rarer 2-family in 11427 runs $850K–$1.1M. Inventory is generally moderate with slow turnover from long-tenured families.",
        "buyer": "Best fit for: Black professional families with multi-generational ties, Caribbean (Jamaican, Trinidadian, Haitian) families, Indo-Caribbean families, and first-time buyers stepping up from Brooklyn or Bronx co-ops looking for a NYC-limit detached home under $850K.",
        "tradeoffs": "Honest tradeoffs: F train at Jamaica–179 is 5–10 minutes by bus or drive; LIRR Queens Village station is faster (~35 min Penn) but adds cost; school-district variation by block — confirm zoned schools per address; some pockets have older homes with deferred maintenance.",
    },
    "11428": {
        "name": "Queens Village",
        "submarkets": "ZIP 11428 covers central Queens Village. The blocks <strong>north of Hempstead Avenue</strong> have the most 1-family detached homes on standard lots; <strong>south of Hempstead Avenue</strong> attached row homes and small 2-family appear more frequently; <strong>blocks closer to the Cross Island Parkway</strong> on the eastern edge trend toward slightly larger lots.",
        "housing": "Detached 1-family homes run $700K–$900K; attached row homes run $625K–$775K; 2-family brick (when available) run $850K–$1.1M; semi-attached homes with driveways run $700K–$850K. Lot sizes are slightly smaller than in adjacent 11427.",
        "buyer": "Best fit for: Black, Caribbean (Guyanese, Jamaican, Trinidadian, Haitian), and Indo-Caribbean families with deep neighborhood roots; first-time buyers using FHA on small 2-family homes; LIRR commuters working in Manhattan or Hicksville/Garden City.",
        "tradeoffs": "Honest tradeoffs: parking pressure in denser pockets; school-district variation by block — verify zoning before offer; some 2-family conversions may have illegal basement units requiring DOB compliance review; ongoing investment cycle as long-tenured owners sell to younger families.",
    },
    "11429": {
        "name": "Queens Village",
        "submarkets": "ZIP 11429 covers eastern Queens Village near the Nassau County border. The blocks <strong>around Cambria Heights border</strong> on the north have larger detached homes on better-sized lots; <strong>central 11429</strong> has 1-family and semi-attached row homes; <strong>the Belt Parkway corridor</strong> on the south has heavier traffic noise but typically lower entry prices.",
        "housing": "Detached 1-family homes run $725K–$925K with the higher end near the Cambria Heights border; semi-attached 1-family run $675K–$825K; 2-family homes run $875K–$1.15M. Garages and finished basements are meaningful price differentiators.",
        "buyer": "Best fit for: Caribbean (Guyanese, Jamaican, Trinidadian, Haitian), Black professional, and Indo-Caribbean families; multi-generational buyers wanting separate-entrance basement units; first-time buyers stepping up from rentals to ownership; LIRR commuters using Queens Village station.",
        "tradeoffs": "Honest tradeoffs: Belt Parkway traffic noise on southern blocks; school-district variation by exact address — always verify zoned schools; F train commute is 50+ minutes via bus connection; LIRR is faster but adds cost; some homes still have original 1950s mechanicals requiring updates.",
    },
    "11432": {
        "name": "Jamaica / Jamaica Estates",
        "submarkets": "ZIP 11432 covers parts of Jamaica and Jamaica Estates. <strong>Jamaica Estates north of Hillside</strong> is a premium detached-home submarket with large lots and Tudor-revival houses; <strong>central 11432 near Hillside Avenue</strong> has the F-train density and smaller-lot 1-family stock; <strong>the South Jamaica border blocks</strong> trend toward 2-family brick and attached row homes.",
        "housing": "Jamaica Estates detached homes range $1.1M–$2.0M+ with Tudor-revival originals at the top end; Jamaica 1-family detached homes run $700K–$875K; 2-family brick run $850K–$1.15M; some blocks near Hillside have prewar co-op buildings with 1BRs $200K–$325K.",
        "buyer": "Best fit for: Indian, Bangladeshi, Punjabi, and Pakistani families wanting larger detached homes with established South Asian community infrastructure; St. John's University faculty and graduate students in the central blocks; multi-generational buyers wanting Jamaica Estates' larger lots; first-time buyers in the more affordable central Jamaica blocks.",
        "tradeoffs": "Honest tradeoffs: F train and E/J/Z at Sutphin–Archer offer ~25–35 min Midtown commute; school-district lines run through 11432 — Jamaica Estates blocks zone to higher-rated schools while central Jamaica blocks may zone differently; some pockets have ongoing development pressure from St. John's expansion.",
    },
    "11433": {
        "name": "South Jamaica",
        "submarkets": "ZIP 11433 covers South Jamaica. <strong>The blocks near Sutphin Boulevard</strong> are denser with attached row homes and 2-family brick; <strong>central South Jamaica</strong> has 1-family detached and semi-attached homes; <strong>the blocks near 165th Street</strong> on the east side have a mix of 1-family detached and semi-attached homes on slightly larger lots.",
        "housing": "1-family detached homes typically run $625K–$800K; attached row homes run $550K–$700K; 2-family brick are common at $775K–$1.05M and serve as the primary investor and house-hacker product; semi-attached homes with driveways run $650K–$825K.",
        "buyer": "Best fit for: Caribbean (Guyanese, Jamaican, Trinidadian), Black professional, and Indo-Caribbean families with multi-generational roots; FHA 2-family house-hackers entering homeownership; first-time buyers using SONYMA and HomeFirst down-payment-assistance programs; LIRR commuters using Jamaica hub.",
        "tradeoffs": "Honest tradeoffs: Sutphin Boulevard commercial corridor has heavy traffic; some blocks have ongoing investment cycle and condition variation house-to-house; verify Certificate of Occupancy on all 2-family purchases; school-district variation requires per-address verification.",
    },
    "11434": {
        "name": "South Jamaica / Springfield Gardens",
        "submarkets": "ZIP 11434 spans parts of South Jamaica, Springfield Gardens, and edge blocks of Rochdale Village. <strong>The Rochdale Village blocks</strong> have a large prewar co-op community; <strong>central 11434</strong> mixes 1-family detached and semi-attached homes; <strong>Springfield Gardens blocks toward JFK</strong> trend toward 2-family brick and detached homes on slightly larger lots.",
        "housing": "Rochdale Village co-op 1-bedrooms run $115K–$185K (some of NYC's most affordable co-op stock); 1-family detached homes run $625K–$800K; 2-family brick run $800K–$1.05M; semi-attached homes with driveways run $675K–$850K.",
        "buyer": "Best fit for: Black, Caribbean (Guyanese, Trinidadian, Jamaican, Haitian), and Indo-Caribbean families; co-op buyers entering NYC ownership at sub-$200K price points (Rochdale Village); JFK workforce families wanting short commute to airport; FHA 2-family house-hackers.",
        "tradeoffs": "Honest tradeoffs: Rochdale Village co-ops have specific resale rules and income/asset restrictions worth reviewing carefully with a NY-licensed attorney; JFK aircraft noise affects southern blocks; A and E train commute is moderate to long; verify school zoning per address.",
    },
    "11435": {
        "name": "Jamaica / Briarwood",
        "submarkets": "ZIP 11435 covers parts of Jamaica, Briarwood, and Kew Gardens Hills. <strong>Briarwood</strong> in the western portion has dense prewar co-op buildings near the F train; <strong>central 11435</strong> mixes 1-family detached and semi-attached homes; <strong>Jamaica blocks near Sutphin Boulevard</strong> trend denser with 2-family and row homes.",
        "housing": "Briarwood co-op 1-bedrooms run $200K–$325K with maintenance $700–$1,000/month; 1-family detached homes run $675K–$850K; 2-family brick run $850K–$1.1M; some prewar elevator buildings have meaningful flip-tax provisions worth reviewing.",
        "buyer": "Best fit for: Bukharian Jewish, Indian, and Bangladeshi families with neighborhood ties; first-time co-op buyers entering Queens at sub-$300K price points via Briarwood; F-train commuters wanting express service; St. John's University adjacent buyers.",
        "tradeoffs": "Honest tradeoffs: F train is the primary subway with ~30 min Midtown commute; school-district variation by exact address; some prewar co-op buildings have older mechanicals and capital-improvement assessments worth investigating; verify zoned schools per offer.",
    },
    "11436": {
        "name": "South Jamaica",
        "submarkets": "ZIP 11436 covers a smaller portion of South Jamaica including parts of Baisley Park. <strong>Blocks near Baisley Pond Park</strong> have a quieter residential feel with 1-family detached homes; <strong>central 11436</strong> mixes attached row homes and 2-family brick; <strong>blocks closer to Rockaway Boulevard</strong> on the south side trend more commercial-residential mixed-use.",
        "housing": "1-family detached homes run $600K–$775K; attached row homes run $550K–$700K; 2-family brick run $775K–$1.0M; semi-attached homes with driveways run $625K–$800K.",
        "buyer": "Best fit for: Black, Caribbean (Guyanese, Jamaican, Trinidadian, Haitian), and South Asian Caribbean families with multi-generational roots; FHA first-time buyers using 2-family house-hack strategy; SONYMA and HomeFirst program participants; JFK workforce families wanting short airport commute.",
        "tradeoffs": "Honest tradeoffs: A train commute via Lefferts Boulevard or Rockaway Boulevard is 50+ minutes to Midtown; some blocks have ongoing investment-cycle condition variation; verify Certificate of Occupancy on all 2-family purchases; school zoning varies — verify per-address.",
    },
    "11580": {
        "name": "Valley Stream",
        "submarkets": "ZIP 11580 covers central Valley Stream. <strong>North Valley Stream</strong> has tighter lots and smaller homes near Sunrise Highway; <strong>central Valley Stream</strong> has the densest residential blocks with 1-family detached homes on standard lots; <strong>South Valley Stream / Gibson</strong> on the southern blocks has slightly larger lots and quieter feel.",
        "housing": "Detached 1-family homes run $625K–$825K; the rare 2-family in 11580 runs $800K–$1.05M; semi-attached homes with driveways are uncommon. Property tax in Nassau is meaningfully higher than NYC — typical 11580 home tax bills run $9,000–$13,000/year.",
        "buyer": "Best fit for: families prioritizing strong Nassau public schools (Valley Stream Central HS District), South Asian (Indian, Bangladeshi, Pakistani, Sikh), Caribbean, and African-American families with strong community presence; LIRR commuters using Valley Stream station for fast Penn Station access (~25 min).",
        "tradeoffs": "Honest tradeoffs: Nassau property taxes are meaningfully higher than NYC — budget for $9K–$13K/year and consider Article 7 grievance/appeal annually; Belt Parkway and Sunrise Highway noise affects some blocks; commute by car has Cross Island Parkway traffic at peak hours.",
    },
    "11581": {
        "name": "Valley Stream / Gibson",
        "submarkets": "ZIP 11581 covers the Gibson and South Valley Stream submarkets. <strong>Gibson</strong> has larger lots and a quieter, more suburban feel with 1-family detached homes on 60x100 lots; <strong>South Valley Stream</strong> is similarly residential with larger homes; <strong>blocks near Mill Brook Park</strong> are particularly desirable for families wanting park access.",
        "housing": "1-family detached homes typically run $700K–$925K with the larger Gibson lots commanding the higher end; the rare 2-family runs $850K–$1.1M; updated mid-century ranches and split-levels are the most common housing type. Property taxes run $10,000–$14,500/year.",
        "buyer": "Best fit for: families prioritizing the strongest Valley Stream school zones, larger-lot suburban feel within 25 minutes of Penn Station by LIRR, South Asian (Indian, Sikh, Bangladeshi, Pakistani) and Caribbean families, and buyers stepping up from Queens looking for backyard space.",
        "tradeoffs": "Honest tradeoffs: Nassau property taxes are higher than equivalent Queens homes — file annual Article 7 grievance to manage; Sunrise Highway noise affects some blocks; older homes (1940s–1960s) may need furnace and electrical updates; verify school-zone lines as district borders run through the ZIP.",
    },
    "11582": {
        "name": "Valley Stream",
        "submarkets": "ZIP 11582 is a smaller portion of Valley Stream. The blocks within 11582 are predominantly residential single-family and trend smaller in inventory volume than 11580/11581 next door.",
        "housing": "1-family detached homes run $625K–$800K. Inventory is limited and turnover is slow with many homes held by long-tenured families. Property taxes run $9,000–$12,500/year.",
        "buyer": "Best fit for: families wanting Valley Stream schools at slightly lower entry prices than 11581, LIRR commuters, and Caribbean and South Asian families with neighborhood ties.",
        "tradeoffs": "Honest tradeoffs: limited inventory means buyers may need to wait for the right home; Nassau property taxes are higher than NYC; Sunrise Highway and Belt Parkway proximity affects certain blocks; verify school zone with district before offer.",
    },
    "11040": {
        "name": "New Hyde Park / Floral Park (Nassau border)",
        "submarkets": "ZIP 11040 spans parts of New Hyde Park and the Nassau-side Floral Park. <strong>The Floral Park village portion</strong> has mature, tree-lined blocks with prewar Tudor and English-style homes; <strong>central New Hyde Park</strong> has post-WWII Cape Cods, ranches, and split-levels on standard lots; <strong>blocks near Long Island Jewish Medical Center</strong> have a mix of 1950s ranches and updated modernized homes.",
        "housing": "Floral Park village detached homes run $850K–$1.25M; New Hyde Park ranches and split-levels run $725K–$925K; updated post-WWII homes run $800K–$1.05M; rare 2-family is $1.0M–$1.3M. Nassau property taxes run $11,000–$16,000/year.",
        "buyer": "Best fit for: families prioritizing strong Sewanhaka or Floral Park-Bellerose school districts, South Asian (Indian, Bangladeshi, Pakistani, Sikh) and Italian-American families, healthcare professionals working at LIJ, and LIRR commuters using New Hyde Park or Floral Park stations for fast Penn Station access.",
        "tradeoffs": "Honest tradeoffs: Nassau property taxes are meaningfully higher than NYC — file annual grievance; school district lines run through 11040 — verify zoning per address (Floral Park-Bellerose vs. Sewanhaka districts price differently); LIE/Cross Island traffic affects rush-hour commute by car.",
    },
    "11042": {
        "name": "New Hyde Park / Lake Success",
        "submarkets": "ZIP 11042 covers parts of New Hyde Park and Lake Success. <strong>Lake Success village</strong> has the highest-end detached homes on larger lots, often $1.3M+; <strong>central New Hyde Park</strong> has standard 1950s–1970s ranches and split-levels; <strong>blocks near LIJ Medical Center</strong> have a mix of housing stock with healthcare-professional buyer demand.",
        "housing": "Lake Success village detached homes run $1.25M–$2.0M+ on larger lots; New Hyde Park standard detached homes run $775K–$975K; updated ranches and split-levels run $850K–$1.1M; rare 2-family $1.05M–$1.35M. Property taxes run $13,000–$22,000/year depending on assessment.",
        "buyer": "Best fit for: families prioritizing top-rated Great Neck and Herricks school districts, South Asian and Asian-American families, healthcare and finance professionals working at LIJ or commuting to Manhattan via LIRR, and buyers stepping up from Queens to Nassau for larger-lot suburban feel.",
        "tradeoffs": "Honest tradeoffs: Nassau property taxes in Lake Success are among the highest in the area — careful budgeting required; school districts vary (Great Neck vs. Herricks vs. New Hyde Park-Garden City Park) — verify per-address as pricing differs by district by 10–15%; LIE traffic at peak times affects commute by car.",
    },
}


def slug_to_zip(slug: str) -> str | None:
    """Extract '11432' from 'zip-11432'."""
    m = re.match(r"zip-(\d{5})", slug)
    return m.group(1) if m else None


def insider_block(neighborhood: str, zipcode: str, data: dict[str, str]) -> str:
    """Render the unique insider's-guide block."""
    return f"""
{MARKER_START}
<section style="margin-top:36px;padding-top:8px;border-top:1px solid #e5e0d8;">
  <h2 style="color:#1a1a2e;font-family:'Playfair Display',serif;">An Insider's Look at {data['name']} (ZIP {zipcode})</h2>
  <p style="color:#777;font-style:italic;">Block-level perspective from a broker who actively works this ZIP — not boilerplate.</p>

  <h3 style="color:#1a1a2e;margin-top:24px;font-family:'Playfair Display',serif;">Submarket Breakdown</h3>
  <p>{data['submarkets']}</p>

  <h3 style="color:#1a1a2e;margin-top:24px;font-family:'Playfair Display',serif;">Housing Stock &amp; Typical Price Bands</h3>
  <p>{data['housing']}</p>

  <h3 style="color:#1a1a2e;margin-top:24px;font-family:'Playfair Display',serif;">Who This ZIP Fits Best</h3>
  <p>{data['buyer']}</p>

  <h3 style="color:#1a1a2e;margin-top:24px;font-family:'Playfair Display',serif;">Honest Tradeoffs I Tell My Clients</h3>
  <p>{data['tradeoffs']}</p>

  <div style="background:linear-gradient(135deg,#1a1a2e,#2d1b69);color:#fff;padding:20px 24px;border-radius:8px;margin-top:24px;">
    <h3 style="color:#D4A017;margin:0 0 8px;font-family:'Playfair Display',serif;">Looking in {data['name']} (ZIP {zipcode})?</h3>
    <p style="margin:0 0 8px;"><strong>Nitin Gadura · (917) 705-0132</strong></p>
    <p style="margin:0 0 8px;font-size:.92rem;">I'll pull current sold comps for the specific blocks you're considering and walk you through honest per-square-foot pricing. Free 15-minute consult, no pressure.</p>
    <p style="margin:0;"><a href="tel:+19177050132" style="color:#D4A017;font-weight:700;">Call (917) 705-0132</a> · <a href="/contact.html" style="color:#D4A017;font-weight:700;">Request consult →</a></p>
  </div>

  <p style="margin-top:18px;font-size:.85rem;color:#666;">Note: price ranges and submarket characterizations are directional based on recent OneKey® MLS activity and on-the-ground experience as of 2026; confirm live sold comps for any specific block before offering. This is general education, not legal or tax advice — retain a NY-licensed real estate attorney for every transaction.</p>
</section>
{MARKER_END}
"""


def find_insertion_point(html: str) -> int | None:
    """Insert before the closing </div> of the main content column.

    The pages have a structure like:
      <div style="flex:1;min-width:280px;">
        ... content ...
      </div>  (this is the main content column)
      <aside ...> (sidebar)

    We want to inject right before that main column's closing </div> — i.e., right
    before the <aside.
    """
    aside_match = re.search(r"<aside\b", html)
    if not aside_match:
        return None
    # Find the last </div> before the aside
    region = html[: aside_match.start()]
    last_div = region.rfind("</div>")
    return last_div if last_div != -1 else None


def process_page(page: Path) -> str:
    text = page.read_text(encoding="utf-8")

    if MARKER_START in text:
        return "already-enriched"

    # Determine ZIP from path
    parent_slug = page.parent.name  # e.g., "zip-11432"
    grandparent_slug = page.parent.parent.name  # e.g., "jamaica"
    zipcode = slug_to_zip(parent_slug)
    if zipcode is None:
        return "not-a-zip-page"
    if zipcode not in ZIP_DATA:
        return f"no-data-for-zip-{zipcode}"

    block = insider_block(grandparent_slug, zipcode, ZIP_DATA[zipcode])

    insert_at = find_insertion_point(text)
    if insert_at is None:
        return "no-insertion-point-found"

    new_text = text[:insert_at] + block + text[insert_at:]
    page.write_text(new_text, encoding="utf-8")
    return "enriched"


def main() -> None:
    targets = list(ROOT.glob("neighborhoods/*/zip-*/index.html"))
    print(f"Found {len(targets)} ZIP-level pages")
    counts: dict[str, int] = {}
    for page in targets:
        result = process_page(page)
        counts[result] = counts.get(result, 0) + 1
        print(f"  [{result:>22}]  {page.relative_to(ROOT)}")
    print("\nSummary:")
    for k, v in sorted(counts.items()):
        print(f"  {k:>24}: {v}")


if __name__ == "__main__":
    main()
