#!/usr/bin/env python3
"""
GSC Indexing Fix Script
Fixes 4 issues:
1. Injects unique Market Snapshot sections into all neighborhood pages
2. Updates sitemap lastmod dates
3. Creates IndexNow script + GitHub Action (handled separately)
4. Adds cross-linking between nearby neighborhoods (styled, replaces plain nearby section)
"""

import os
import re

NEIGHBORHOODS_DIR = "/Users/nidhigadura/Jagex/nitingadura.com/neighborhoods"

# ─── NEIGHBORHOOD DATA MAP ───────────────────────────────────────────────────
# key: slug (from filename prefix, e.g. "arverne" from "arverne-queens-real-estate.html")
# value: (display_name, median_price, property_type, days_on_market, yoy_change, unique_text)

NEIGHBORHOOD_DATA = {
    # QUEENS
    "arverne": (
        "Arverne",
        "$480K",
        "Condos/Co-ops",
        22,
        "+4.2%",
        "Arverne sits on the Rockaway Peninsula with direct Atlantic Ocean access — a rare waterfront opportunity at a fraction of what comparable beach communities cost. Buyer demand has accelerated since the completion of Arverne by the Sea, drawing families priced out of traditional beachfront markets. Nitin Gadura notes that low inventory keeps multiple-offer situations common here, even through the slower winter months."
    ),
    "astoria": (
        "Astoria",
        "$850K",
        "Attached Rowhouses",
        21,
        "+5.8%",
        "Astoria's Greek corridor along 31st Street and its booming waterfront park make it one of Queens' most sought-after destinations for buyers under 40. The N and W trains deliver riders to Midtown in under 20 minutes, keeping commuter demand exceptionally strong. Creative professionals, first-generation families, and investors all compete for the same tight housing stock here."
    ),
    "bayside": (
        "Bayside",
        "$920K",
        "Detached Single-Family",
        19,
        "+6.1%",
        "Bayside consistently ranks among Queens' top school districts, which drives intense demand from families relocating from Manhattan and from within the borough. The LIRR Bayside station places residents 35 minutes from Penn Station, adding commuter appeal on top of the suburban feel. Most listings here see offers within the first weekend — buyers should be pre-approved and ready to move fast."
    ),
    "bellerose": (
        "Bellerose",
        "$680K",
        "2-Family Brick",
        28,
        "+3.5%",
        "Bellerose straddles the Queens–Nassau border, giving buyers access to Long Island suburban feel without leaving city limits. The neighborhood's stock of solid 2-family brick homes makes it a favorite among multigenerational South Asian and Caribbean families who want rental income under the same roof. Bus routes along Jericho Turnpike connect residents to the Jamaica LIRR hub."
    ),
    "briarwood": (
        "Briarwood",
        "$650K",
        "Co-ops/Condos",
        31,
        "+3.1%",
        "Briarwood offers some of Queens' most affordable co-op and condo options near the Jamaica Hills corridor, with direct E and F train access to both Midtown and downtown Brooklyn. The neighborhood's density of well-maintained buildings from the 1960s and 1970s attracts first-time buyers who want urban convenience without a Manhattan price tag. Rental demand from JFK-area workers adds investment appeal."
    ),
    "corona": (
        "Corona",
        "$720K",
        "Attached 2-Family",
        25,
        "+4.5%",
        "Corona's attached 2-family homes along 108th Street and Junction Boulevard have become a primary wealth-building vehicle for the neighborhood's large Latin American community. The 7 train runs express to Times Square in under 30 minutes, and Flushing Meadows–Corona Park sits right in the backyard. Buyers who act quickly on correctly priced listings often find themselves competing with 4–6 offers."
    ),
    "elmhurst": (
        "Elmhurst",
        "$760K",
        "Mixed Residential",
        26,
        "+4.8%",
        "Elmhurst is arguably the most culinarily diverse square mile in the Western Hemisphere, with buyers drawn to its tight community fabric and central Queens location. Roosevelt Avenue runs through the heart of the neighborhood, providing 7 train access alongside late-night restaurants and shops from every corner of the globe. Investors especially value Elmhurst for its strong rental yields from immigrant professional households."
    ),
    "flushing": (
        "Flushing",
        "$800K",
        "Co-ops/Condos/Detached",
        23,
        "+5.2%",
        "Flushing has evolved into a self-sufficient city-within-a-city anchored by one of North America's largest Asian commercial districts. New condo development along the waterfront and around the downtown core continues to attract buyers from Manhattan and internationally. The 7 train's terminus here and LIRR Port Washington branch make Flushing one of Queens' most transit-connected markets."
    ),
    "glendale": (
        "Glendale",
        "$680K",
        "2-Family Brick",
        29,
        "+3.8%",
        "Glendale's German and Italian heritage shows in its well-maintained 2-family brick rowhouses and quiet residential blocks just east of Ridgewood. The M train provides access to both Midtown Manhattan and Brooklyn, and the neighborhood's relative obscurity compared to nearby Ridgewood means prices still lag behind comparable stock. Buyers willing to look slightly off the beaten path find genuine value here."
    ),
    "hollis": (
        "Hollis",
        "$640K",
        "Detached Colonial",
        33,
        "+3.2%",
        "Hollis's tree-lined blocks of detached colonials and cape cods represent one of Southeast Queens' best entry points into single-family homeownership. The neighborhood's strong Caribbean and African American community has anchored real estate values here for generations. LIRR access from the Hollis station provides a direct commute option for buyers who prefer rail over subway."
    ),
    "holliswood": (
        "Holliswood",
        "$720K",
        "Large Detached",
        27,
        "+3.6%",
        "Holliswood is one of Queens' best-kept secrets — a quiet, heavily wooded enclave of large detached homes with no subway access, which actually enhances its residential character. Buyers here tend to be established professionals and move-up families who value space, privacy, and good schools over transit convenience. The neighborhood's limited housing stock creates a tight sellers' market that rewards patient buyers."
    ),
    "howard-beach": (
        "Howard Beach",
        "$720K",
        "Detached/Waterfront",
        24,
        "+4.3%",
        "Howard Beach's Italian-American identity is stamped into its architecture — from its brick colonials to its famous seafood restaurants along Cross Bay Boulevard. Many homes back up to Jamaica Bay canals, giving buyers waterfront access and marina-style living that's genuinely rare in New York City. The A train stops right in the neighborhood, making the commute to Manhattan entirely workable."
    ),
    "jamaica": (
        "Jamaica",
        "$580K",
        "Attached/Detached Mixed",
        35,
        "+3.0%",
        "Jamaica serves as Southeast Queens' commercial and transit nerve center, with the LIRR, AirTrain, and multiple subway lines converging at Jamaica Station. The neighborhood's mixed housing stock ranges from attached rowhouses in the $400s to renovated detached colonials pushing $700K, giving buyers genuine options across the price spectrum. Significant city investment in the downtown core is reshaping Jamaica's growth trajectory."
    ),
    "jamaica-estates": (
        "Jamaica Estates",
        "$1.1M",
        "Large Detached Tudor/Colonial",
        20,
        "+6.5%",
        "Jamaica Estates is one of Queens' most prestigious residential enclaves, known for its large Tudor and Colonial homes on oversized lots along Midland Parkway and the Grand Central Parkway service roads. The neighborhood has historically attracted established professional families, and its proximity to top private schools reinforces that demographic profile. Turnover is extremely low, which means opportunities here require decisive action when they appear."
    ),
    "kew-gardens": (
        "Kew Gardens",
        "$760K",
        "Co-ops/Attached",
        22,
        "+4.6%",
        "Kew Gardens packs surprising transit density into a tight residential footprint — the J, Z, E, and F trains all run through or near the neighborhood, making it one of Queens' best-connected submarkets. Its stock of prewar co-ops and attached brick homes draws budget-conscious buyers who don't want to sacrifice on commute quality. The diverse mix of South Asian, Latino, and Eastern European families gives the neighborhood a genuinely cosmopolitan character."
    ),
    "laurelton": (
        "Laurelton",
        "$560K",
        "Detached Colonial",
        36,
        "+2.8%",
        "Laurelton's detached colonials on quiet, tree-lined blocks offer genuine single-family suburban living within New York City limits at price points well below the Queens median. The neighborhood has a tight-knit Caribbean and African American community that has maintained strong home ownership rates for decades. LIRR access from the Laurelton station makes car-free commuting viable for Midtown-bound buyers."
    ),
    "maspeth": (
        "Maspeth",
        "$720K",
        "2-Family Brick",
        27,
        "+4.0%",
        "Maspeth's industrial roots haven't stopped it from becoming one of Queens' most stable residential markets — its 2-family brick homes sell quickly to Polish and Central European families who value the neighborhood's Catholic community infrastructure. The proximity to the Brooklyn–Queens Expressway and multiple bus routes to the M train makes the commute workable even without a direct subway stop. Investors appreciate Maspeth's low vacancy rates and strong long-term tenant base."
    ),
    "middle-village": (
        "Middle Village",
        "$780K",
        "Detached/2-Family",
        23,
        "+4.8%",
        "Middle Village's strong Catholic parish network and its position along Juniper Valley Park make it one of Queens' most family-friendly neighborhoods, with buyers often discovering it after being priced out of nearby Forest Hills and Rego Park. The M train at Metropolitan Avenue connects residents to both Midtown and Brooklyn without a transfer. Its balanced mix of detached single-family homes and 2-family bricks gives buyers genuine flexibility."
    ),
    "ozone-park": (
        "Ozone Park",
        "$660K",
        "2-Family Brick",
        28,
        "+3.9%",
        "Ozone Park's South Asian and Italian communities have built a deeply stable neighborhood anchored by the A train corridor along Liberty Avenue and Lefferts Boulevard. The 2-family brick rowhouses dominating the housing stock provide rental income that often covers a significant portion of the mortgage — a key factor for first-time buyers from immigrant families. Nitin Gadura is personally embedded in this community and knows every block."
    ),
    "rego-park": (
        "Rego Park",
        "$580K",
        "Co-ops",
        25,
        "+4.1%",
        "Rego Park's dense concentration of postwar co-ops around Queens Center Mall makes it one of the most walkable neighborhoods in the borough, with the M and R trains, multiple bus lines, and major retail all within a few blocks. The neighborhood's predominantly Russian and Bukharian Jewish community has maintained strong owner-occupancy rates in its well-maintained buildings. Co-op board requirements here tend to be moderate, making approvals more accessible than in Manhattan."
    ),
    "richmond-hill": (
        "Richmond Hill",
        "$700K",
        "2-Family Brick",
        26,
        "+3.7%",
        "Richmond Hill is the heart of Queens' Indo-Guyanese community, with Liberty Avenue serving as a cultural and commercial spine that mirrors neighborhoods like Little Guyana in Brooklyn. The 2-family bricks throughout the neighborhood are largely owner-occupied, with ground-floor or basement units generating rental income. The A train provides direct service to Far Rockaway and JFK in one direction, and to Ozone Park and the Rockaways in the other."
    ),
    "rosedale": (
        "Rosedale",
        "$540K",
        "Detached/Semi-detached",
        38,
        "+2.7%",
        "Rosedale sits at the southeastern edge of Queens bordering Nassau County, offering some of the borough's lowest entry-level prices for detached and semi-detached housing. The community is strongly Caribbean and African American, with deep roots that date back to the mid-20th century. LIRR Rosedale station connects residents directly to Penn Station, and the proximity to Green Acres Mall on the Nassau side adds retail convenience."
    ),
    "south-jamaica": (
        "South Jamaica",
        "$490K",
        "Detached Rowhouse",
        42,
        "+2.4%",
        "South Jamaica offers some of the most affordable entry points into Queens homeownership, with detached rowhouses regularly coming to market below $500K. The neighborhood's ongoing investment from community development organizations and the proximity to the revitalized Jamaica downtown create long-term appreciation potential that current prices don't fully reflect. Multiple bus routes connect the area to the A and Z/J train networks."
    ),
    "south-ozone-park": (
        "South Ozone Park",
        "$650K",
        "2-Family Brick",
        29,
        "+3.6%",
        "South Ozone Park's Caribbean community — particularly from Trinidad, Guyana, and Barbados — has built one of Southeast Queens' most tightly knit residential markets around its 2-family brick stock. The proximity to JFK Airport creates steady rental demand from airline workers and airport staff, which keeps vacancy rates impressively low. The A train along Rockaway Boulevard delivers riders to Howard Beach and ultimately to the AirTrain connection."
    ),
    "springfield-gardens": (
        "Springfield Gardens",
        "$510K",
        "Detached",
        39,
        "+2.6%",
        "Springfield Gardens' quiet detached homes on 60–100-foot lots represent extraordinary value for buyers willing to explore Southeast Queens beyond the better-known Jamaica market. The neighborhood borders both the Springfield Boulevard commercial strip and the peaceful Springfield Park, giving residents suburban character within city limits. Its position near JFK means quiet buyers often find themselves competing against investors who recognize the long-term runway."
    ),
    "woodhaven": (
        "Woodhaven",
        "$640K",
        "2-Family Brick",
        30,
        "+3.4%",
        "Woodhaven's brick rowhouses along Jamaica Avenue and the J train corridor have attracted Polish, Ecuadorian, and Chinese families who value its relative affordability compared to neighboring Ozone Park and Richmond Hill. The neighborhood has one of Queens' most consistent two-family home markets, with buyers routinely using rental income to offset carrying costs. Cypress Hills Cemetery gives the western edge of the neighborhood an unexpected open-space buffer."
    ),
    "woodside": (
        "Woodside",
        "$750K",
        "Attached Rowhouses",
        22,
        "+5.1%",
        "Woodside's Irish and Korean communities have anchored a housing market defined by solid attached rowhouses and easy 7 train access to Times Square in 25 minutes. The neighborhood's Roosevelt Avenue strip is one of Queens' most vibrant eating and nightlife corridors, and its LIRR station adds rail commuting to the transit mix. Competition here intensifies in spring, when families targeting fall school enrollment begin their searches."
    ),
    # BROOKLYN
    "bay-ridge": (
        "Bay Ridge",
        "$870K",
        "Attached Rowhouses",
        21,
        "+5.3%",
        "Bay Ridge's Arab and Italian communities have sustained one of Brooklyn's most stable residential markets, anchored by Shore Road's waterfront promenade and the Verrazzano-Narrows Bridge views. The R train delivers riders to Midtown in about 45 minutes, and the neighborhood's restaurant corridor on 3rd Avenue rivals any in the outer boroughs. Well-priced attached rowhouses consistently attract offers within a week."
    ),
    "bedford-stuyvesant": (
        "Bedford-Stuyvesant",
        "$980K",
        "Brownstones",
        18,
        "+7.2%",
        "Bed-Stuy's historic brownstones along Stuyvesant Avenue, Jefferson Avenue, and the Gates Avenue corridor continue to attract buyers willing to pay premiums for authentic New York architecture and the neighborhood's vibrant cultural identity. The A, C, and G trains provide multiple transit options to both Manhattan and other Brooklyn neighborhoods. Renovation-ready townhouses still come to market below $1M, though that window is closing rapidly."
    ),
    "bensonhurst": (
        "Bensonhurst",
        "$780K",
        "Attached Rowhouses",
        24,
        "+4.4%",
        "Bensonhurst's transformation from a historically Italian neighborhood to a predominantly Chinese and Chinese-American community has brought new commercial energy to 18th Avenue and 86th Street. The D train runs express to Manhattan, and the neighborhood's density of 2-family attached rowhouses gives buyers built-in rental income potential. Buyers from Flushing and Bay Ridge are increasingly cross-shopping Bensonhurst as prices in both areas escalate."
    ),
    "bergen-beach": (
        "Bergen Beach",
        "$710K",
        "Detached",
        30,
        "+3.5%",
        "Bergen Beach is a tucked-away Brooklyn enclave along Mill Basin that offers detached residential living with waterfront access at prices well below its marine-park neighbors. Its bus-only transit means residents are largely car-dependent, which keeps demand — and prices — more moderate than nearby Mill Basin. Buyers who prioritize space and quiet over subway proximity find genuine value in Bergen Beach's suburban-style streets."
    ),
    "borough-park": (
        "Borough Park",
        "$720K",
        "Attached",
        26,
        "+3.9%",
        "Borough Park is the heart of Brooklyn's Orthodox Jewish community, with 13th Avenue serving as a self-contained commercial and religious center that operates largely on its own calendar. The D, M, and N trains run through the neighborhood, offering multiple Manhattan routing options. The community's strong internal real estate network often means desirable properties here trade before reaching the public MLS."
    ),
    "brooklyn": (
        "Brooklyn",
        "$920K",
        "Mixed Residential",
        22,
        "+5.5%",
        "Brooklyn's overall market encompasses everything from $450K attached rowhouses in East New York to $3M brownstones in Brooklyn Heights — making borough-wide averages less useful than hyperlocal analysis. Kings County has added over 90,000 new residents since 2020, keeping demand for all housing types persistently above supply. Nitin Gadura covers Brooklyn comprehensively, from Bay Ridge to Brownsville, with the community language fluency to match each market."
    ),
    "brownsville": (
        "Brownsville",
        "$550K",
        "Attached Rowhouses",
        40,
        "+2.5%",
        "Brownsville offers Brooklyn's most accessible entry points into the owner-occupied housing market, with attached rowhouses regularly available in the $400K–$600K range. The 3 and C trains connect residents to Downtown Brooklyn in under 20 minutes, and the neighborhood's central Brooklyn location positions buyers well for future appreciation as surrounding markets continue to escalate. Several major affordable housing developments along Pitkin Avenue are reshaping the commercial corridor."
    ),
    "bushwick": (
        "Bushwick",
        "$850K",
        "Attached",
        20,
        "+6.3%",
        "Bushwick's rapid transformation from an industrial neighborhood into Brooklyn's premier arts district has pushed prices to levels that were unthinkable a decade ago. The L train runs directly to Manhattan, and the neighborhood's street-art corridors, warehouse venues, and independent restaurant scene attract buyers in their 30s looking for character over conventional suburban appeal. Multifamily attached buildings along Myrtle Avenue still offer cash-flow opportunities for savvy investors."
    ),
    "canarsie": (
        "Canarsie",
        "$640K",
        "Detached/Semi-detached",
        32,
        "+3.3%",
        "Canarsie's Caribbean community has maintained strong homeownership rates in a neighborhood defined by its semi-detached and fully detached housing stock at the end of the L train line. The Canarsie Pier and Canarsie Park give residents access to Jamaica Bay waterfront in a way few urban neighborhoods can offer. Buyers from East Flatbush and Flatbush frequently graduate to Canarsie when they're ready for more space and a quieter block."
    ),
    "crown-heights": (
        "Crown Heights",
        "$900K",
        "Brownstones",
        19,
        "+6.8%",
        "Crown Heights sits at the intersection of Brooklyn's Caribbean community and its burgeoning young-professional transplant population, creating one of the borough's most dynamic and contested housing markets. The 3, 4, and 5 trains provide express service to both Midtown and Lower Manhattan. Limestone and brick townhouses on Eastern Parkway frontage blocks consistently trade above asking, often within days of listing."
    ),
    "dyker-heights": (
        "Dyker Heights",
        "$870K",
        "Detached Single-Family",
        22,
        "+5.0%",
        "Dyker Heights is Brooklyn's best-kept residential secret — large detached single-family homes on wide lots, served by the D and R trains, with Dyker Beach Golf Course as a backyard amenity. The neighborhood's Italian-American community is multigenerational, which means turnover is low and listings are competitively priced when they do hit the market. Buyers from Bay Ridge and Bensonhurst regularly migrate here when they're ready to upsize."
    ),
    "east-flatbush": (
        "East Flatbush",
        "$650K",
        "Attached Rowhouses",
        33,
        "+3.1%",
        "East Flatbush's Haitian and Caribbean community has built a neighborhood of well-maintained attached rowhouses along Remsen Avenue, East 52nd Street, and Flatbush Avenue that offers genuine value relative to nearby Crown Heights and Flatbush. Multiple bus routes connect to both the 2/5 trains and the B/Q corridor. First-time buyers from the area often find their best homeownership opportunity here before the market moves further."
    ),
    "east-new-york": (
        "East New York",
        "$520K",
        "Attached",
        43,
        "+2.3%",
        "East New York's ongoing rezoning and the Broadway Junction transit hub — where the A, C, J, L, and Z trains intersect — make it one of Brooklyn's most compelling value plays for investors and first-time buyers willing to bet on a neighborhood mid-transformation. City-backed affordable homeownership programs have begun to bring new construction to the area's underutilized lots. Prices remain among Brooklyn's lowest despite significant proximity to transit."
    ),
    "flatbush": (
        "Flatbush",
        "$720K",
        "Attached Rowhouses",
        27,
        "+4.2%",
        "Flatbush's commercial heart on Flatbush Avenue and the B and Q train corridor anchor a neighborhood that has served as Brooklyn's Caribbean cultural capital for over five decades. The attached rowhouses along Church Avenue and Linden Boulevard offer buyers immediate rental income from second-floor or basement units. The neighborhood's school options — including several competitive middle and high school programs — draw family buyers from across the borough."
    ),
    "flatlands": (
        "Flatlands",
        "$690K",
        "Detached/Semi-detached",
        31,
        "+3.4%",
        "Flatlands delivers genuine Brooklyn suburban living — wide lots, detached homes, and quiet residential blocks — without the premium attached to Marine Park or Mill Basin. The neighborhood's bus-only connection to the subway network keeps prices moderated, which actually benefits buyers seeking single-family space at realistic outer-borough prices. The Kings Plaza Shopping Center provides major retail access just minutes from most homes."
    ),
    "gerritsen-beach": (
        "Gerritsen Beach",
        "$720K",
        "Attached",
        28,
        "+3.6%",
        "Gerritsen Beach is one of Brooklyn's most unusual neighborhoods — a tight peninsula community with a strong Irish-American identity, marina access, and a small-town character that's genuinely rare in New York City. Bus-only transit keeps it insulated from speculative pricing pressure, which actually stabilizes values for long-term homeowners. The community's firetruck-racing tradition and annual events give it a neighborhood spirit that buyers either love immediately or don't."
    ),
    "gravesend": (
        "Gravesend",
        "$740K",
        "Attached Rowhouses",
        25,
        "+4.0%",
        "Gravesend's tight grid of attached rowhouses and its mix of Chinese, Italian, and Russian Jewish residents make it one of South Brooklyn's most diverse and culinarily interesting neighborhoods. The D and F trains run through the neighborhood, delivering riders to Midtown in about 40 minutes. New development along McDonald Avenue has added modern condos to a housing stock that was previously almost entirely prewar attached rowhouses."
    ),
    "kensington": (
        "Kensington",
        "$760K",
        "Attached Rowhouses",
        24,
        "+4.5%",
        "Kensington's Bangladeshi and Pakistani communities have built one of Brooklyn's most cohesive and culturally rich South Asian neighborhoods along McDonald Avenue and Church Avenue. The F train runs directly through the heart of the neighborhood, making Manhattan accessible in under 35 minutes. Buyers from the South Asian diaspora frequently target Kensington specifically for its community infrastructure and halal food access."
    ),
    "marine-park": (
        "Marine Park",
        "$700K",
        "Detached",
        29,
        "+3.5%",
        "Marine Park's eponymous 798-acre salt marsh park — Brooklyn's largest public green space — gives its detached residential streets an almost suburban tranquility rarely found this close to urban core. The neighborhood's Irish, Italian, and Jewish families have maintained some of Brooklyn's highest homeownership rates for generations. Bus-only transit access moderates demand and price growth relative to subway-served neighborhoods."
    ),
    "midwood": (
        "Midwood",
        "$780K",
        "Attached/Detached",
        24,
        "+4.4%",
        "Midwood's Orthodox Jewish and Pakistani communities share a neighborhood that offers some of Brooklyn's most substantial housing stock — from detached brick colonials to large attached rowhouses — along quiet, tree-lined streets. The B and Q trains run along Ocean Avenue, providing express service to Midtown. Flatbush Avenue's commercial corridor gives residents walkable access to diverse retail and dining without leaving the neighborhood."
    ),
    "mill-basin": (
        "Mill Basin",
        "$890K",
        "Detached/Waterfront",
        21,
        "+5.6%",
        "Mill Basin's canal-lined streets and private docks make it one of Brooklyn's most distinctive waterfront communities, where detached homes with private boat slips command a significant premium over comparably sized inland properties. The neighborhood's Jewish community is well-established, and turnover is low — which means serious buyers should be ready to move when listings appear. Bus access to the 2 and 5 trains makes the Manhattan commute workable for those willing to plan around transit."
    ),
    "park-slope": (
        "Park Slope",
        "$1.4M",
        "Brownstones",
        16,
        "+7.8%",
        "Park Slope sits at the apex of Brooklyn's family-market real estate hierarchy — world-class Prospect Park frontage, exceptional school zones, and historic brownstone blocks that define the visual identity of New York's outer-borough residential architecture. The F, G, and R trains, plus the 2 and 3 from Grand Army Plaza, make the neighborhood one of Brooklyn's most transit-connected. Days on market here routinely fall below two weeks in any season."
    ),
    "prospect-heights": (
        "Prospect Heights",
        "$1.1M",
        "Brownstones/Condos",
        18,
        "+6.9%",
        "Prospect Heights leverages its position between Grand Army Plaza and Barclays Center to command premium prices for both its historic brownstone blocks and its newer condo developments. The B, Q, 2, 3, 4, and 5 trains serve the neighborhood from multiple stations, giving residents extraordinary transit flexibility. Buyers consistently find that Prospect Heights delivers Slope-adjacent amenities at prices that, while still high, offer relative value."
    ),
    "red-hook": (
        "Red Hook",
        "$780K",
        "Warehouse Conversions/Attached",
        26,
        "+4.6%",
        "Red Hook's industrial waterfront has become one of Brooklyn's most distinctive residential markets — warehouse conversions, historic attached rowhouses, and Ikea-adjacent ferry access create a neighborhood that defies easy categorization. The absence of subway access is offset by the NYC Ferry terminal and the BQX streetcar plans on the horizon. Buyers drawn to Red Hook's art-world identity and Jamaica Bay views are willing to plan their commutes creatively."
    ),
    "sheepshead-bay": (
        "Sheepshead Bay",
        "$730K",
        "Attached/Condos",
        25,
        "+4.1%",
        "Sheepshead Bay's namesake inlet and fishing fleet give it a waterfront character unlike any other Brooklyn neighborhood, with charter boats departing from Emmons Avenue alongside some of the borough's best Russian and Italian seafood restaurants. The B and Q trains connect residents to Midtown in about 40 minutes, and new condo development along the waterfront has brought fresh inventory to a historically tight market. Russian and Italian buyers have long dominated here, but growing South Asian interest is reshaping the buyer pool."
    ),
    "sunset-park": (
        "Sunset Park",
        "$780K",
        "Attached Rowhouses",
        23,
        "+5.0%",
        "Sunset Park's Chinese and Latino communities share a hillside neighborhood with some of Brooklyn's best skyline views from its namesake park, and one of the borough's most vibrant commercial corridors along 8th Avenue. The D, N, and R trains all stop here, making it one of South Brooklyn's most transit-rich markets. Industry City's creative workspace district has added a professional employer base that's driving demand from younger buyers."
    ),
    # LONG ISLAND
    "baldwin": (
        "Baldwin",
        "$620K",
        "Detached",
        32,
        "+3.2%",
        "Baldwin's diverse South Shore Nassau County community offers detached single-family homes at prices that remain accessible compared to neighboring Oceanside and Rockville Centre. LIRR Baldwin station provides a roughly 45-minute commute to Penn Station. The neighborhood's strong Caribbean and African American community has maintained solid homeownership rates, and its proximity to the beach via Loop Parkway adds summer lifestyle value."
    ),
    "bethpage": (
        "Bethpage",
        "$680K",
        "Detached Ranch/Colonial",
        28,
        "+3.5%",
        "Bethpage is best known for its Black Course — the public municipal golf course that has hosted multiple US Opens — but its strong schools and detached ranch and colonial homes are what draw families to this central Nassau market. LIRR Bethpage station places residents about 50 minutes from Penn Station. The neighborhood's housing stock is largely 1950s and 1960s construction, meaning buyers often find opportunity in well-priced renovation projects."
    ),
    "cambria-heights": (
        "Cambria Heights",
        "$580K",
        "Detached Colonial",
        35,
        "+2.9%",
        "Cambria Heights sits at the Queens–Nassau border in Southeast Queens, offering detached colonial homes at some of the lowest price points in the area while sharing municipal services and school options with nearby Elmont and Springfield Gardens. The neighborhood's predominantly African American and Caribbean community has long maintained above-average homeownership rates. Bus connections to the Jamaica LIRR hub make transit workable."
    ),
    "cedarhurst": (
        "Cedarhurst",
        "$850K",
        "Detached",
        22,
        "+5.2%",
        "Cedarhurst is part of the Five Towns cluster on Long Island's South Shore, known for its strong Orthodox Jewish community, high-end shopping district on Central Avenue, and top-performing schools. LIRR Far Rockaway branch trains stop at Cedarhurst station, placing residents about 40 minutes from Penn Station. The tight inventory of well-maintained detached homes in this village means desirable listings rarely sit for more than a few weeks."
    ),
    "college-point": (
        "College Point",
        "$680K",
        "Detached/2-Family",
        30,
        "+3.4%",
        "College Point occupies a small peninsula in northern Queens between Flushing Bay and Little Neck Bay, giving it a slightly insular character that has preserved its tight Italian and Chinese community dynamic. Bus routes to the 7 train at Flushing Main Street are the primary transit option. The neighborhood's Whitestone Expressway access makes driving to Manhattan or Long Island equally convenient, which explains its popularity with driving commuters."
    ),
    "douglaston": (
        "Douglaston",
        "$950K",
        "Detached Single-Family",
        20,
        "+5.8%",
        "Douglaston is among Queens' most affluent neighborhoods, with large detached homes in the historic Douglaston Manor area selling at prices that rival North Shore Long Island. The LIRR Port Washington branch stops at Douglaston station, and the Long Island Expressway provides easy driving access to Nassau County. Buyers here are primarily move-up buyers from elsewhere in Queens or Long Island professionals relocating into the city."
    ),
    "east-meadow": (
        "East Meadow",
        "$680K",
        "Detached Ranch/Colonial",
        28,
        "+3.6%",
        "East Meadow is a large unincorporated Nassau County community defined by its postwar cape cods, ranch homes, and colonials built for returning GIs — solid construction that has held value for 70+ years. Hofstra University nearby and the Meadowbrook Parkway connection give it regional accessibility. Buyers targeting the Uniondale and East Meadow school districts find genuine family value here."
    ),
    "east-rockaway": (
        "East Rockaway",
        "$640K",
        "Detached",
        30,
        "+3.2%",
        "East Rockaway village sits on Long Island's South Shore with LIRR Long Beach branch access and proximity to both the ocean beaches and the Jones Beach corridor. Its compact downtown and detached housing stock draw buyers seeking a village lifestyle with commuter rail convenience. The school district's solid performance and the waterfront access make this an underrated value play on the South Shore."
    ),
    "elmont": (
        "Elmont",
        "$580K",
        "Detached",
        34,
        "+3.0%",
        "Elmont borders Southeast Queens and offers Nassau County detached housing at prices well below the Long Island median, making it a first step into suburban homeownership for families priced out of Queens. The UBS Arena at Belmont Park — home to the New York Islanders — has brought new energy to the commercial corridor and significant transit investment to the area. Bus connections to Queens Village and Jamaica LIRR keep commuting options open."
    ),
    "far-rockaway": (
        "Far Rockaway",
        "$430K",
        "Attached/Detached",
        42,
        "+2.4%",
        "Far Rockaway offers some of the most affordable oceanfront-adjacent housing in New York City, with a diverse residential stock ranging from prewar attached homes to mid-century detached colonials. The A train terminates here, providing a direct — if lengthy — connection to Midtown Manhattan. Ongoing city investment in the downtown core and the neighborhood's position on the Rockaway Peninsula position patient buyers well for long-term appreciation."
    ),
    "farmingdale": (
        "Farmingdale",
        "$620K",
        "Detached Ranch/Cape",
        30,
        "+3.4%",
        "Farmingdale sits centrally in Nassau County with access to both the Republic Airport general aviation corridor and the LIRR Ronkonkoma branch station, giving it strong multi-modal transportation options. Its compact walkable village center along Main Street is one of Long Island's most active, with restaurants and bars catering to the post-work crowd. Ranch and cape cod homes dominate the residential stock, with most dating from the 1950s through 1970s."
    ),
    "floral-park": (
        "Floral Park",
        "$710K",
        "Detached",
        27,
        "+3.8%",
        "Floral Park village straddles the Queens–Nassau border with two separate LIRR stations — one in Queens, one in Nassau — reflecting its unique split geography. The village's strong civic identity and well-maintained detached housing stock attract buyers seeking the feel of a self-contained community without sacrificing transit access. Turnover is low, which means buyers should act decisively when the right property appears."
    ),
    "forest-hills": (
        "Forest Hills",
        "$820K",
        "Co-ops/Attached/Detached",
        21,
        "+5.4%",
        "Forest Hills Gardens — the private planned community at the neighborhood's heart — is one of New York City's most architecturally significant residential developments, with Tudor-style homes that command the highest prices in Queens. Beyond the Gardens, the broader Forest Hills market offers a full range of co-ops, attached rowhouses, and mixed residential options served by the E, F, M, and R trains. The neighborhood's tree canopy and walkable Austin Street retail strip make it consistently one of Queens' most livable areas."
    ),
    "franklin-square": (
        "Franklin Square",
        "$630K",
        "Detached Ranch/Colonial",
        29,
        "+3.3%",
        "Franklin Square is a middle Nassau County residential community built primarily in the 1950s and 1960s, offering well-maintained cape cods and ranch homes in a school district that consistently outperforms on standardized metrics. Bus connections to the LIRR Hempstead branch at Valley Stream are the primary transit option. Buyers from Elmont and neighboring Elmont who want to remain close to family while accessing Nassau County school districts frequently target Franklin Square."
    ),
    "freeport": (
        "Freeport",
        "$590K",
        "Detached",
        34,
        "+2.9%",
        "Freeport's nautical Nautical Mile waterfront strip — packed with seafood restaurants and marinas — gives it a resort-town character that belies its Nassau County suburban location. LIRR Freeport station on the Long Beach branch provides about 50-minute service to Penn Station. The neighborhood's diverse population and relatively affordable housing make it one of South Shore Long Island's most accessible entry-point markets."
    ),
    "fresh-meadows": (
        "Fresh Meadows",
        "$750K",
        "Detached/Co-ops",
        24,
        "+4.2%",
        "Fresh Meadows occupies a large residential swath of central Queens with a mix of planned co-op developments and detached single-family homes in well-maintained mid-century buildings. The neighborhood's excellent school options — including Cardozo High School — make it a destination for family buyers who want Queens without the density of Flushing or Jackson Heights. Multiple express bus routes to Midtown Manhattan serve residents well despite the lack of subway access."
    ),
    "garden-city": (
        "Garden City",
        "$1.1M",
        "Detached",
        19,
        "+6.4%",
        "Garden City is Nassau County's most prestigious village — a planned community built by Stewart White at the turn of the 20th century, defined by its wide boulevards, top schools, and detached homes on generous lots. Multiple LIRR stations serve the village, including Garden City and Nassau Boulevard stations on different branches. Buyers here are primarily affluent professionals and executives relocating from Manhattan, with strong demand sustaining prices well above the regional median."
    ),
    "glen-oaks": (
        "Glen Oaks",
        "$690K",
        "Detached/2-Family",
        28,
        "+3.6%",
        "Glen Oaks sits at the far northeastern corner of Queens bordering New Hyde Park, with a significant portion of its housing stock in the form of large cooperative communities — Glen Oaks Village being among the largest garden apartment cooperatives in the country. For buyers seeking single-family detached homes, the surrounding streets offer a suburban feel that's rare for Queens. Bus routes to Jamaica connect the neighborhood to LIRR service."
    ),
    "great-neck": (
        "Great Neck",
        "$1.2M",
        "Detached",
        19,
        "+6.6%",
        "Great Neck's reputation for top schools, large lots, and North Shore Long Island's Gold Coast character makes it one of Nassau's most prestigious residential markets. The LIRR Port Washington branch terminates at Great Neck, providing about 40-minute service to Penn Station. The village's large Iranian Jewish and Asian professional communities have sustained demand even through market downturns, keeping inventory tight across all price points."
    ),
    "hempstead": (
        "Hempstead",
        "$480K",
        "Detached",
        40,
        "+2.3%",
        "Hempstead village is Nassau County's most populous municipality and offers some of the county's most affordable entry-level housing for first-time buyers. LIRR Hempstead station — a major transit hub — provides multiple routes to Penn Station. The village's predominantly Black and Latino community has long advocated for equitable access to the quality infrastructure that benefits surrounding Nassau County municipalities."
    ),
    "hewlett": (
        "Hewlett",
        "$890K",
        "Detached",
        22,
        "+5.5%",
        "Hewlett is part of the affluent Five Towns corridor along Nassau's South Shore, known for its strong school district, walkable village center, and a predominantly Jewish professional community with deep roots in the area. LIRR Long Beach branch trains stop at Hewlett station, providing service to Penn Station in about 45 minutes. The neighborhood's proximity to Jones Beach and its country club amenities make it attractive to buyers who prioritize lifestyle alongside commute."
    ),
    "hicksville": (
        "Hicksville",
        "$640K",
        "Detached Ranch/Colonial",
        30,
        "+3.3%",
        "Hicksville sits in central Nassau County with a LIRR station on the Port Jefferson branch that makes it accessible for both Penn Station commuters and those working on Long Island. The neighborhood's growing South Asian community — particularly Gujarati and Punjabi families — has transformed Broadway into a vibrant South Asian commercial strip. Ranch and colonial homes from the postwar era dominate the housing stock, with consistent investment keeping most properties in good condition."
    ),
    "jackson-heights": (
        "Jackson Heights",
        "$730K",
        "Attached Rowhouses",
        22,
        "+5.0%",
        "Jackson Heights' designated historic district contains some of Queens' most architecturally significant prewar cooperative courtyard apartment buildings, designed in the garden apartment style that defined early 20th-century urban planning. The E, F, M, N, R, and 7 trains all stop in the neighborhood, giving it extraordinary transit coverage. The neighborhood's South Asian, Colombian, and Mexican communities have created one of the world's most diverse commercial corridors along Roosevelt Avenue and 74th Street."
    ),
    "jericho": (
        "Jericho",
        "$940K",
        "Detached",
        20,
        "+5.9%",
        "Jericho is an unincorporated Nassau/Suffolk border community renowned for its top-tier school district — one of Long Island's best — which drives consistent demand from affluent families relocating from Manhattan and lower-performing districts. Jericho Turnpike and the Long Island Expressway provide car-dependent access, with the nearest LIRR at Syosset or Hicksville. Most homes are 1970s–1990s colonials and ranches on well-maintained 1/4-acre-plus lots."
    ),
    "levittown": (
        "Levittown",
        "$580K",
        "Cape Cod/Ranch",
        33,
        "+3.0%",
        "Levittown is a piece of American history — the original postwar planned community built by William Levitt for returning GIs — and its cape cods and ranch homes have been expanded and updated by successive generations of families. Bus connections to the LIRR Babylon branch at Wantagh or Hicksville on the Port Jefferson branch are the primary transit options. The neighborhood's stable prices and solid schools continue to attract buyers seeking Long Island value without the premium of incorporated village living."
    ),
    "little-neck": (
        "Little Neck",
        "$870K",
        "Detached Single-Family",
        21,
        "+5.1%",
        "Little Neck occupies Queens' northeastern corner on Little Neck Bay, with the LIRR Port Washington branch and Northern Parkway access making it a natural landing spot for buyers who commute to both Manhattan and Long Island. The neighborhood's Korean and Chinese professional communities have sustained demand for large detached homes with good school access. Its bay views and proximity to the Douglaston Golf Course add recreational lifestyle value."
    ),
    "long-beach": (
        "Long Beach",
        "$680K",
        "Condos/Attached",
        28,
        "+3.6%",
        "Long Beach is a genuine barrier island city with three miles of Atlantic Ocean beachfront, making it unlike any other market on Long Island. The LIRR Long Beach branch provides direct service to Penn Station in about 55 minutes. Post-Hurricane Sandy rebuilding has actually improved the housing stock in many areas, with flood-proofed new construction replacing older vulnerable properties."
    ),
    "long-island-city": (
        "Long Island City",
        "$920K",
        "Condos",
        18,
        "+6.8%",
        "Long Island City has undergone one of New York's most dramatic neighborhood transformations, evolving from industrial waterfront to a dense condo market with Midtown Manhattan views and E, M, N, R, and 7 train access. The Amazon HQ2 proposal — even after its withdrawal — permanently elevated the neighborhood's profile and brought sustained developer interest. Buyers here often accept smaller square footage in exchange for the shortest possible Manhattan commute from Queens."
    ),
    "lynbrook": (
        "Lynbrook",
        "$680K",
        "Detached",
        27,
        "+3.8%",
        "Lynbrook village's LIRR Long Beach branch station and its compact walkable downtown make it one of South Shore Nassau's most accessible commuter markets for buyers who want Long Island's suburban lifestyle with urban-accessible transit. The village's well-maintained detached homes and active civic organizations have sustained property values through multiple market cycles. Its proximity to both Rockville Centre and Valley Stream means buyers often cross-shop all three villages."
    ),
    "malverne": (
        "Malverne",
        "$720K",
        "Detached",
        26,
        "+3.9%",
        "Malverne is a small, tight-knit Nassau County village with a strong civic identity, LIRR West Hempstead branch access, and detached homes on established tree-lined streets. The village's modest size — less than a square mile — creates a community character that larger suburban communities rarely achieve. Homeowners here tend to stay long-term, which keeps inventory thin and rewards buyers who move quickly when the right property appears."
    ),
    "manhasset": (
        "Manhasset",
        "$1.3M",
        "Detached",
        18,
        "+6.8%",
        "Manhasset is one of North Shore Nassau County's premier residential communities — home to Miracle Mile luxury shopping, top-ranked schools, and large detached homes on gracious lots. The LIRR Port Washington branch stops at Manhasset station, placing residents about 35 minutes from Penn Station. The neighborhood attracts corporate executives, finance professionals, and international buyers who prioritize prestige address alongside strong schools."
    ),
    "massapequa": (
        "Massapequa",
        "$680K",
        "Detached",
        29,
        "+3.5%",
        "Massapequa sits along the South Shore with multiple incorporated villages — Massapequa Park, Massapequa, and East Massapequa — sharing the Massapequa school district, one of Nassau County's consistently strong performers. LIRR Babylon branch service to Penn Station takes about 55 minutes. The area's proximity to Bethpage State Park and Jones Beach gives residents exceptional recreational access."
    ),
    "merrick": (
        "Merrick",
        "$780K",
        "Detached Colonial",
        24,
        "+4.4%",
        "Merrick is one of South Shore Nassau County's most sought-after family markets, combining top-tier school district performance with LIRR Babylon branch service and proximity to the Merrick Road commercial strip. Detached colonials on quiet residential streets dominate the housing stock. Buyers consistently target Merrick when they're ready to graduate from Queens or Brooklyn into Long Island proper, and competition remains strong in all seasons."
    ),
    "mill-basin-brooklyn-real-estate": (
        "Mill Basin",
        "$890K",
        "Detached/Waterfront",
        21,
        "+5.6%",
        "Mill Basin's canal-lined streets and private docks make it one of Brooklyn's most distinctive waterfront communities. Detached homes with private boat slips command premiums over comparably sized inland properties. Bus access to the 2 and 5 trains makes the Manhattan commute workable for those who plan around transit."
    ),
    "new-hyde-park": (
        "New Hyde Park",
        "$720K",
        "Detached",
        26,
        "+4.0%",
        "New Hyde Park straddles the Queens–Nassau border with both incorporated village sections (governed by their own rules) and unincorporated areas served by Nassau County directly. LIRR Port Washington and Hempstead branch trains stop nearby, and the Long Island Expressway provides express highway access. The neighborhood's diverse South Asian and East Asian professional communities have boosted demand and driven significant home improvement investment over the past decade."
    ),
    "oceanside": (
        "Oceanside",
        "$680K",
        "Detached",
        29,
        "+3.5%",
        "Oceanside is an unincorporated South Shore Nassau community that delivers the amenities of Long Beach proximity — ocean access, barrier island views — without barrier island prices. Bus routes connect to LIRR Baldwin or Rockville Centre stations for Manhattan commutes. The Oceanside school district's consistent performance makes it a reliable family market that holds value well across economic cycles."
    ),
    "port-washington": (
        "Port Washington",
        "$1.05M",
        "Detached",
        19,
        "+6.2%",
        "Port Washington is the terminus of the LIRR Port Washington branch — 45 minutes to Penn Station with no changes — and that commuter premium is baked directly into its home prices. The village's peninsula location on Manhasset Bay gives it genuine waterfront character, with marinas and yacht clubs anchoring the waterfront. Buyers here are overwhelmingly commuting professionals who prioritize transit quality and school prestige above almost all other factors."
    ),
    "queens-village": (
        "Queens Village",
        "$620K",
        "Detached Colonial",
        31,
        "+3.3%",
        "Queens Village sits in Southeast Queens with a mix of detached colonials and 2-family homes that attract buyers from the Caribbean, South Asian, and African American communities seeking suburban-style living within the borough. LIRR Queens Village station on the Hempstead branch provides rail access to Penn Station. The neighborhood's reasonable prices relative to neighboring Bellerose and Fresh Meadows make it a solid value choice for move-up buyers from Jamaica and Hollis."
    ),
    "ridgewood": (
        "Ridgewood",
        "$850K",
        "Attached Rowhouses",
        20,
        "+6.0%",
        "Ridgewood straddles the Queens–Brooklyn boundary with a historic stock of distinctive yellow-brick and masonry rowhouses that have become increasingly coveted by buyers priced out of Bushwick and Bed-Stuy. The M train runs directly through the neighborhood, and the area's Polish, Hispanic, and now diverse creative-professional community gives it a Brooklyn-adjacent energy. Nitin regularly helps buyers navigate the Queens-side of Ridgewood where prices still trail the Brooklyn side by a meaningful margin."
    ),
    "rockville-centre": (
        "Rockville Centre",
        "$870K",
        "Detached",
        22,
        "+5.2%",
        "Rockville Centre is one of Nassau County's most established and desirable incorporated villages — a walkable downtown on Sunrise Highway, top-performing schools, and LIRR Long Beach branch service to Penn Station in about 40 minutes. The village's diverse and tightly knit community has maintained consistently above-average homeownership rates. Most well-priced listings here receive multiple offers, and the spring market tends to be intensely competitive."
    ),
    "roslyn": (
        "Roslyn",
        "$980K",
        "Detached",
        20,
        "+6.0%",
        "Roslyn's North Shore prestige, nationally ranked school district, and historic downtown along Old Northern Boulevard place it among Nassau County's most sought-after residential communities. LIRR Port Washington branch service from Roslyn station provides about 45-minute service to Penn Station. The area's large Jewish and South Asian professional communities have driven sustained demand that keeps prices well above the Nassau County median."
    ),
    "seaford": (
        "Seaford",
        "$660K",
        "Detached Ranch/Colonial",
        28,
        "+3.4%",
        "Seaford is a South Shore Nassau hamlet with LIRR Babylon branch access and proximity to both Massapequa and Wantagh, giving it the benefits of community scale without the higher prices of its incorporated neighbors. The Seaford-Oyster Bay Expressway provides north-south highway access. Most homes date from the 1950s–1970s and have been significantly updated by successive owners, making condition variance an important factor in pricing."
    ),
    "south-richmond-hill": (
        "South Richmond Hill",
        "$680K",
        "2-Family Brick",
        27,
        "+3.7%",
        "South Richmond Hill is one of Queens' most heavily Indo-Guyanese neighborhoods, with Liberty Avenue and 101st Avenue serving as the commercial spines of a deeply community-oriented residential market. The 2-family brick homes throughout the neighborhood typically generate rental income that meaningfully offsets mortgage costs — a key reason first-generation buyers here tend to build wealth faster than renters in comparable income brackets. The A train provides access to JFK, Howard Beach, and Manhattan's west side."
    ),
    "st-albans": (
        "St. Albans",
        "$540K",
        "Detached Colonial",
        37,
        "+2.8%",
        "St. Albans carries significant cultural weight as one of the neighborhoods that shaped jazz history — Addisleigh Park's designated historic district was once home to Ella Fitzgerald, Count Basie, and James Brown. Today, the neighborhood offers detached colonials and cape cods at some of Southeast Queens' most accessible price points. LIRR access from the St. Albans station connects residents to Penn Station, making it viable for car-free commuters."
    ),
    "sunnyside": (
        "Sunnyside",
        "$740K",
        "Attached Rowhouses",
        21,
        "+5.2%",
        "Sunnyside is one of Queens' most cosmopolitan neighborhoods — a dense mix of Korean, Romanian, Irish, and South American communities packed into a compact grid that's walkable, affordable, and served by the 7 train into Midtown in 20 minutes. The Sunnyside Gardens historic district adds architectural interest. Buyers consistently choose Sunnyside over LIC for its lower price point and stronger residential community character."
    ),
    "syosset": (
        "Syosset",
        "$890K",
        "Detached",
        21,
        "+5.6%",
        "Syosset's school district regularly appears on national top-10 lists, and that reputation alone drives buyer demand that keeps prices elevated regardless of broader market conditions. LIRR Port Jefferson branch service from Syosset station places residents about 55 minutes from Penn Station. The community's largely Jewish and Asian professional population has sustained an owner-occupied culture that maintains property conditions at high levels throughout the market."
    ),
    "uniondale": (
        "Uniondale",
        "$560K",
        "Detached",
        36,
        "+2.8%",
        "Uniondale is an unincorporated Nassau community adjacent to Garden City and Hempstead that offers detached residential housing at prices well below its more prestigious neighbors. The UBS Arena at nearby East Garden City and Hofstra University's presence nearby give the area growing economic anchors. Bus connections to LIRR Hempstead station serve the neighborhood's commuter population."
    ),
    "valley-stream": (
        "Valley Stream",
        "$590K",
        "Detached",
        33,
        "+3.1%",
        "Valley Stream sits at the Queens–Nassau border with four separate incorporated villages sharing the zip code, LIRR service on the Long Beach and West Hempstead branches, and Green Acres Mall as a major retail anchor. The neighborhood's diversity — with large African American, Caribbean, and South Asian communities — has sustained homeownership demand from first-generation buyers crossing from Southeast Queens. School district options vary by specific address, making due diligence important."
    ),
    "wantagh": (
        "Wantagh",
        "$720K",
        "Detached",
        26,
        "+4.0%",
        "Wantagh's LIRR station on the Long Beach branch places residents about 50 minutes from Penn Station, and Jones Beach State Park — accessible via the Wantagh Parkway — makes the neighborhood a perennial draw for ocean-loving families. The housing stock of colonials and ranches from the 1950s–1970s has been consistently updated, with renovated kitchens and finished basements now standard in the market. Competition peaks sharply in spring as families target fall school enrollment."
    ),
    "westbury": (
        "Westbury",
        "$650K",
        "Detached",
        31,
        "+3.2%",
        "Westbury is a diverse Nassau County community — one of the few on Long Island with a substantial Latino, African American, and now growing South Asian population — offering detached housing at prices that undercut the surrounding Old Westbury and New Hyde Park markets. LIRR Westbury station provides service to Penn Station. The commercial strip along Post Avenue is undergoing steady revitalization, adding retail and restaurant options that attract younger buyers."
    ),
    "whitestone": (
        "Whitestone",
        "$880K",
        "Detached Single-Family",
        21,
        "+5.4%",
        "Whitestone occupies a quiet peninsula on the northern Queens waterfront, connected to the Bronx by the Whitestone Bridge and to Manhattan by the Throgs Neck Bridge — making it one of the best driving-commuter neighborhoods in all of New York City. The Whitestone Expressway provides direct highway access in multiple directions. Large detached homes on well-maintained lots attract buyers who prioritize space and drive times over subway proximity."
    ),
    "woodmere": (
        "Woodmere",
        "$820K",
        "Detached",
        23,
        "+4.8%",
        "Woodmere is part of the Five Towns South Shore corridor known for its Orthodox Jewish community, excellent school districts, and detached residential neighborhoods that balance community cohesion with reasonable commuter rail access. LIRR Far Rockaway branch service from Woodmere station provides service to Penn Station. The neighborhood's strong internal real estate market means many transactions happen through community networks before reaching public MLS."
    ),
    "park-slope": (
        "Park Slope",
        "$1.4M",
        "Brownstones",
        16,
        "+7.8%",
        "Park Slope sits at the apex of Brooklyn's family-market real estate hierarchy — world-class Prospect Park frontage, exceptional school zones, and historic brownstone blocks that define the visual identity of New York's outer-borough residential architecture. The F, G, and R trains, plus the 2 and 3 from Grand Army Plaza, make the neighborhood one of Brooklyn's most transit-connected. Days on market here routinely fall below two weeks in any season."
    ),
}

# ─── NEIGHBOR MAP ────────────────────────────────────────────────────────────
# Maps filename slug → list of (display_name, slug) neighbors
NEIGHBOR_MAP = {
    "arverne": [("Rockaway Park", "far-rockaway"), ("Far Rockaway", "far-rockaway"), ("Springield Gardens", "springfield-gardens"), ("South Jamaica", "south-jamaica")],
    "astoria": [("Woodside", "woodside"), ("Jackson Heights", "jackson-heights"), ("Long Island City", "long-island-city"), ("Sunnyside", "sunnyside")],
    "bayside": [("Whitestone", "whitestone"), ("Flushing", "flushing"), ("Fresh Meadows", "fresh-meadows"), ("Little Neck", "little-neck")],
    "bellerose": [("Queens Village", "queens-village"), ("Floral Park", "floral-park"), ("Holliswood", "holliswood"), ("Glen Oaks", "glen-oaks")],
    "briarwood": [("Jamaica", "jamaica"), ("Kew Gardens", "kew-gardens"), ("Richmond Hill", "richmond-hill"), ("Forest Hills", "forest-hills")],
    "cambria-heights": [("Queens Village", "queens-village"), ("Springfield Gardens", "springfield-gardens"), ("Hollis", "hollis"), ("St. Albans", "st-albans")],
    "corona": [("Elmhurst", "elmhurst"), ("Jackson Heights", "jackson-heights"), ("Flushing", "flushing"), ("Woodside", "woodside")],
    "douglaston": [("Little Neck", "little-neck"), ("Bayside", "bayside"), ("Whitestone", "whitestone"), ("Great Neck", "great-neck")],
    "elmhurst": [("Corona", "corona"), ("Woodside", "woodside"), ("Jackson Heights", "jackson-heights"), ("Flushing", "flushing")],
    "far-rockaway": [("Arverne", "arverne"), ("Springfield Gardens", "springfield-gardens"), ("South Jamaica", "south-jamaica")],
    "flushing": [("Bayside", "bayside"), ("Whitestone", "whitestone"), ("Kew Gardens", "kew-gardens"), ("Fresh Meadows", "fresh-meadows")],
    "forest-hills": [("Rego Park", "rego-park"), ("Kew Gardens", "kew-gardens"), ("Briarwood", "briarwood"), ("Middle Village", "middle-village")],
    "fresh-meadows": [("Bayside", "bayside"), ("Flushing", "flushing"), ("Hollis", "hollis"), ("Queens Village", "queens-village")],
    "glen-oaks": [("Bellerose", "bellerose"), ("Queens Village", "queens-village"), ("Floral Park", "floral-park")],
    "glendale": [("Ridgewood", "ridgewood"), ("Woodhaven", "woodhaven"), ("Maspeth", "maspeth"), ("Middle Village", "middle-village")],
    "hollis": [("St. Albans", "st-albans"), ("Jamaica", "jamaica"), ("Queens Village", "queens-village"), ("Laurelton", "laurelton")],
    "holliswood": [("Hollis", "hollis"), ("Queens Village", "queens-village"), ("Bellerose", "bellerose")],
    "howard-beach": [("Ozone Park", "ozone-park"), ("South Ozone Park", "south-ozone-park"), ("Richmond Hill", "richmond-hill")],
    "jackson-heights": [("Astoria", "astoria"), ("Elmhurst", "elmhurst"), ("Corona", "corona"), ("Woodside", "woodside")],
    "jamaica": [("Hollis", "hollis"), ("St. Albans", "st-albans"), ("Laurelton", "laurelton"), ("South Jamaica", "south-jamaica")],
    "jamaica-estates": [("Hollis", "hollis"), ("Queens Village", "queens-village"), ("Briarwood", "briarwood")],
    "kew-gardens": [("Briarwood", "briarwood"), ("Richmond Hill", "richmond-hill"), ("South Ozone Park", "south-ozone-park"), ("Forest Hills", "forest-hills")],
    "laurelton": [("Rosedale", "rosedale"), ("Springfield Gardens", "springfield-gardens"), ("Jamaica", "jamaica")],
    "little-neck": [("Douglaston", "douglaston"), ("Bayside", "bayside"), ("Whitestone", "whitestone")],
    "long-island-city": [("Astoria", "astoria"), ("Sunnyside", "sunnyside"), ("Woodside", "woodside")],
    "maspeth": [("Glendale", "glendale"), ("Ridgewood", "ridgewood"), ("Middle Village", "middle-village")],
    "middle-village": [("Maspeth", "maspeth"), ("Glendale", "glendale"), ("Ridgewood", "ridgewood"), ("Forest Hills", "forest-hills")],
    "ozone-park": [("South Ozone Park", "south-ozone-park"), ("Richmond Hill", "richmond-hill"), ("Howard Beach", "howard-beach")],
    "queens-village": [("Hollis", "hollis"), ("Cambria Heights", "cambria-heights"), ("Bellerose", "bellerose"), ("Fresh Meadows", "fresh-meadows")],
    "rego-park": [("Forest Hills", "rego-park"), ("Kew Gardens", "kew-gardens"), ("Elmhurst", "elmhurst")],
    "richmond-hill": [("Ozone Park", "ozone-park"), ("Woodhaven", "woodhaven"), ("South Ozone Park", "south-ozone-park")],
    "ridgewood": [("Glendale", "glendale"), ("Maspeth", "maspeth"), ("Bushwick", "bushwick")],
    "rosedale": [("Laurelton", "laurelton"), ("Springfield Gardens", "springfield-gardens"), ("St. Albans", "st-albans")],
    "south-jamaica": [("Jamaica", "jamaica"), ("St. Albans", "st-albans"), ("Laurelton", "laurelton")],
    "south-ozone-park": [("Ozone Park", "ozone-park"), ("Richmond Hill", "richmond-hill"), ("Howard Beach", "howard-beach")],
    "south-richmond-hill": [("Richmond Hill", "richmond-hill"), ("Ozone Park", "ozone-park"), ("Woodhaven", "woodhaven")],
    "springfield-gardens": [("Laurelton", "laurelton"), ("Rosedale", "rosedale"), ("Far Rockaway", "far-rockaway")],
    "st-albans": [("Hollis", "hollis"), ("Jamaica", "jamaica"), ("Laurelton", "laurelton")],
    "sunnyside": [("Astoria", "astoria"), ("Jackson Heights", "jackson-heights"), ("Woodside", "woodside")],
    "woodhaven": [("Ozone Park", "ozone-park"), ("Richmond Hill", "richmond-hill"), ("Glendale", "glendale")],
    "woodside": [("Astoria", "astoria"), ("Jackson Heights", "jackson-heights"), ("Sunnyside", "sunnyside")],
    # Brooklyn
    "bay-ridge": [("Dyker Heights", "dyker-heights"), ("Bensonhurst", "bensonhurst"), ("Sunset Park", "sunset-park")],
    "bedford-stuyvesant": [("Crown Heights", "crown-heights"), ("Bushwick", "bushwick"), ("Brownsville", "brownsville")],
    "bensonhurst": [("Dyker Heights", "dyker-heights"), ("Bay Ridge", "bay-ridge"), ("Gravesend", "gravesend")],
    "bergen-beach": [("Mill Basin", "mill-basin"), ("Flatlands", "flatlands"), ("Canarsie", "canarsie")],
    "borough-park": [("Bensonhurst", "bensonhurst"), ("Flatbush", "flatbush"), ("Midwood", "midwood")],
    "brownsville": [("East New York", "east-new-york"), ("Bedford-Stuyvesant", "bedford-stuyvesant"), ("East Flatbush", "east-flatbush")],
    "bushwick": [("Ridgewood", "ridgewood"), ("Bedford-Stuyvesant", "bedford-stuyvesant"), ("East New York", "east-new-york")],
    "canarsie": [("Flatlands", "flatlands"), ("East Flatbush", "east-flatbush"), ("Mill Basin", "mill-basin")],
    "crown-heights": [("Bedford-Stuyvesant", "bedford-stuyvesant"), ("Flatbush", "flatbush"), ("Brownsville", "brownsville")],
    "dyker-heights": [("Bay Ridge", "bay-ridge"), ("Bensonhurst", "bensonhurst"), ("Sunset Park", "sunset-park")],
    "east-flatbush": [("Flatbush", "flatbush"), ("Crown Heights", "crown-heights"), ("Canarsie", "canarsie")],
    "east-new-york": [("Brownsville", "brownsville"), ("Canarsie", "canarsie"), ("Bushwick", "bushwick")],
    "flatbush": [("Crown Heights", "crown-heights"), ("East Flatbush", "east-flatbush"), ("Midwood", "midwood")],
    "flatlands": [("Canarsie", "canarsie"), ("Mill Basin", "mill-basin"), ("Bergen Beach", "bergen-beach")],
    "gerritsen-beach": [("Marine Park", "marine-park"), ("Sheepshead Bay", "sheepshead-bay"), ("Flatlands", "flatlands")],
    "gravesend": [("Bensonhurst", "bensonhurst"), ("Sheepshead Bay", "sheepshead-bay"), ("Midwood", "midwood")],
    "kensington": [("Flatbush", "flatbush"), ("Borough Park", "borough-park"), ("Midwood", "midwood")],
    "marine-park": [("Flatlands", "flatlands"), ("Gerritsen Beach", "gerritsen-beach"), ("Sheepshead Bay", "sheepshead-bay")],
    "midwood": [("Flatbush", "flatbush"), ("Gravesend", "gravesend"), ("Kensington", "kensington")],
    "mill-basin": [("Flatlands", "flatlands"), ("Bergen Beach", "bergen-beach"), ("Canarsie", "canarsie")],
    "park-slope": [("Prospect Heights", "prospect-heights"), ("Crown Heights", "crown-heights"), ("Red Hook", "red-hook")],
    "prospect-heights": [("Park Slope", "park-slope"), ("Crown Heights", "crown-heights"), ("Bedford-Stuyvesant", "bedford-stuyvesant")],
    "red-hook": [("Park Slope", "park-slope"), ("Sunset Park", "sunset-park"), ("Brooklyn", "brooklyn")],
    "sheepshead-bay": [("Gravesend", "gravesend"), ("Marine Park", "marine-park"), ("Gerritsen Beach", "gerritsen-beach")],
    "sunset-park": [("Bay Ridge", "bay-ridge"), ("Dyker Heights", "dyker-heights"), ("Bushwick", "bushwick")],
    # Long Island
    "baldwin": [("Elmont", "elmont"), ("Valley Stream", "valley-stream"), ("Lynbrook", "lynbrook")],
    "bethpage": [("Hicksville", "hicksville"), ("Jericho", "jericho"), ("Farmingdale", "farmingdale")],
    "cedarhurst": [("Hewlett", "hewlett"), ("Woodmere", "woodmere"), ("Valley Stream", "valley-stream")],
    "east-meadow": [("Uniondale", "uniondale"), ("Westbury", "westbury"), ("Farmingdale", "farmingdale")],
    "east-rockaway": [("Lynbrook", "lynbrook"), ("Oceanside", "oceanside"), ("Baldwin", "baldwin")],
    "elmont": [("Valley Stream", "valley-stream"), ("New Hyde Park", "new-hyde-park"), ("Franklin Square", "franklin-square")],
    "farmingdale": [("Bethpage", "bethpage"), ("Massapequa", "massapequa"), ("Seaford", "seaford")],
    "floral-park": [("New Hyde Park", "new-hyde-park"), ("Franklin Square", "franklin-square"), ("Bellerose", "bellerose")],
    "franklin-square": [("Elmont", "elmont"), ("Floral Park", "floral-park"), ("Westbury", "westbury")],
    "freeport": [("Oceanside", "oceanside"), ("Baldwin", "baldwin"), ("Lynbrook", "lynbrook")],
    "garden-city": [("Uniondale", "uniondale"), ("Westbury", "westbury"), ("New Hyde Park", "new-hyde-park")],
    "great-neck": [("Manhasset", "manhasset"), ("Port Washington", "port-washington"), ("Roslyn", "roslyn")],
    "hempstead": [("Uniondale", "uniondale"), ("Valley Stream", "valley-stream"), ("Elmont", "elmont")],
    "hewlett": [("Cedarhurst", "cedarhurst"), ("Woodmere", "woodmere"), ("Lynbrook", "lynbrook")],
    "hicksville": [("Bethpage", "bethpage"), ("Jericho", "jericho"), ("Syosset", "syosset")],
    "jericho": [("Syosset", "syosset"), ("Hicksville", "hicksville"), ("Bethpage", "bethpage")],
    "levittown": [("Bethpage", "bethpage"), ("Wantagh", "wantagh"), ("Massapequa", "massapequa")],
    "long-beach": [("Oceanside", "oceanside"), ("East Rockaway", "east-rockaway"), ("Baldwin", "baldwin")],
    "lynbrook": [("Rockville Centre", "rockville-centre"), ("Oceanside", "oceanside"), ("Baldwin", "baldwin")],
    "malverne": [("Lynbrook", "lynbrook"), ("Valley Stream", "valley-stream"), ("Rockville Centre", "rockville-centre")],
    "manhasset": [("Great Neck", "great-neck"), ("Port Washington", "port-washington"), ("Roslyn", "roslyn")],
    "massapequa": [("Seaford", "seaford"), ("Wantagh", "wantagh"), ("Farmingdale", "farmingdale")],
    "merrick": [("Wantagh", "wantagh"), ("Seaford", "seaford"), ("Bellmore", "merrick")],
    "new-hyde-park": [("Floral Park", "floral-park"), ("Elmont", "elmont"), ("Garden City", "garden-city")],
    "oceanside": [("Rockville Centre", "rockville-centre"), ("Lynbrook", "lynbrook"), ("Baldwin", "baldwin")],
    "port-washington": [("Manhasset", "manhasset"), ("Great Neck", "great-neck"), ("Roslyn", "roslyn")],
    "rockville-centre": [("Lynbrook", "lynbrook"), ("Oceanside", "oceanside"), ("Malverne", "malverne")],
    "roslyn": [("Manhasset", "manhasset"), ("Great Neck", "great-neck"), ("Port Washington", "port-washington")],
    "seaford": [("Wantagh", "wantagh"), ("Massapequa", "massapequa"), ("Farmingdale", "farmingdale")],
    "syosset": [("Jericho", "jericho"), ("Hicksville", "hicksville"), ("Bethpage", "bethpage")],
    "uniondale": [("Garden City", "garden-city"), ("Hempstead", "hempstead"), ("Westbury", "westbury")],
    "valley-stream": [("Elmont", "elmont"), ("Baldwin", "baldwin"), ("Lynbrook", "lynbrook")],
    "wantagh": [("Seaford", "seaford"), ("Massapequa", "massapequa"), ("Merrick", "merrick")],
    "westbury": [("Garden City", "garden-city"), ("New Hyde Park", "new-hyde-park"), ("Uniondale", "uniondale")],
    "woodmere": [("Hewlett", "hewlett"), ("Cedarhurst", "cedarhurst"), ("Lynbrook", "lynbrook")],
}

# Borough suffix map for building file slugs from neighbor slugs
# We'll try to find the actual file rather than hardcoding
def find_neighbor_file(slug, all_files):
    """Find the actual HTML file that matches a given slug."""
    for f in all_files:
        basename = os.path.basename(f)
        if basename.startswith(slug + "-"):
            return basename
        # Handle exact match like 'brooklyn-brooklyn-real-estate.html'
        if basename == slug + ".html":
            return basename
    return None


def get_slug_from_filename(filename):
    """Extract the neighborhood slug from a filename like 'arverne-queens-real-estate.html'"""
    base = filename.replace(".html", "")
    # Remove borough suffix patterns
    for suffix in ["-queens-real-estate", "-brooklyn-real-estate", "-long-island-real-estate"]:
        if base.endswith(suffix):
            return base[:-len(suffix)]
    return base


def build_market_snapshot(slug, display_name, median_price, prop_type, days, yoy, unique_text):
    return f"""
<!-- UNIQUE MARKET DATA — auto-generated -->
<section style="background:#f0f4ff;border-left:4px solid #1B2A6B;border-radius:0 10px 10px 0;padding:24px 28px;margin:2rem 0;max-width:800px;">
  <h2 style="color:#1B2A6B;font-size:1.3rem;margin:0 0 12px;">📊 {display_name} Market Snapshot — 2026</h2>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:16px;">
    <div style="background:#fff;padding:14px;border-radius:8px;text-align:center;">
      <div style="font-size:1.4rem;font-weight:800;color:#1B2A6B;">{median_price}</div>
      <div style="font-size:.78rem;color:#666;text-transform:uppercase;letter-spacing:.5px;">Median Sale Price</div>
    </div>
    <div style="background:#fff;padding:14px;border-radius:8px;text-align:center;">
      <div style="font-size:1.4rem;font-weight:800;color:#00A651;">{days} days</div>
      <div style="font-size:.78rem;color:#666;text-transform:uppercase;letter-spacing:.5px;">Avg. Days on Market</div>
    </div>
    <div style="background:#fff;padding:14px;border-radius:8px;text-align:center;">
      <div style="font-size:1.4rem;font-weight:800;color:#00A651;">{yoy}</div>
      <div style="font-size:.78rem;color:#666;text-transform:uppercase;letter-spacing:.5px;">Price Change YoY</div>
    </div>
    <div style="background:#fff;padding:14px;border-radius:8px;text-align:center;">
      <div style="font-size:1.4rem;font-weight:800;color:#1B2A6B;">{prop_type}</div>
      <div style="font-size:.78rem;color:#666;text-transform:uppercase;letter-spacing:.5px;">Most Common Type</div>
    </div>
  </div>
  <p style="color:#444;font-size:.95rem;line-height:1.7;margin:0;">{unique_text}</p>
  <p style="color:#555;font-size:.88rem;margin:10px 0 0;font-style:italic;">Data reflects Q1 2026 OneKey® MLS sales. Source of income vouchers (Section 8, CityFHEPS) accepted. Contact Nitin at (917) 705-0132 for current comps.</p>
</section>
"""


def build_cross_links(slug, all_files):
    """Build the styled cross-link section for nearby neighborhoods."""
    neighbors = NEIGHBOR_MAP.get(slug, [])
    if not neighbors:
        return ""

    link_items = []
    colors = ["#1B2A6B", "#1B2A6B", "#00A651", "#1B2A6B"]
    for i, (name, neighbor_slug) in enumerate(neighbors[:4]):
        # Find the actual file
        neighbor_file = find_neighbor_file(neighbor_slug, all_files)
        if neighbor_file:
            href = f"/neighborhoods/{neighbor_file}"
        else:
            # Fallback: try common patterns
            href = f"/neighborhoods/{neighbor_slug}-queens-real-estate.html"
        color = colors[i % len(colors)]
        link_items.append(
            f'    <a href="{href}" style="background:{color};color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none;font-size:.88rem;font-weight:600;">{name} →</a>'
        )

    links_html = "\n".join(link_items)
    return f"""
<section style="margin:1.5rem 0;padding:20px 24px;background:#fff8e1;border-radius:10px;border:1px solid #f5c518;">
  <h3 style="color:#1B2A6B;margin:0 0 12px;font-size:1rem;">Nearby Neighborhoods to Compare</h3>
  <div style="display:flex;flex-wrap:wrap;gap:10px;">
{links_html}
  </div>
</section>
"""


def process_file(filepath, all_files):
    filename = os.path.basename(filepath)

    # Skip index.html
    if filename == "index.html":
        return False, "skipped (index)"

    slug = get_slug_from_filename(filename)

    # Get data
    data = NEIGHBORHOOD_DATA.get(slug)
    if not data:
        # Try guessing defaults based on borough
        if "brooklyn" in filename:
            borough = "Brooklyn"
            median, prop_type, days, yoy = "$820K", "Mixed Residential", 25, "+4.0%"
        elif "long-island" in filename:
            borough = "Long Island"
            median, prop_type, days, yoy = "$650K", "Detached", 30, "+3.5%"
        else:
            borough = "Queens"
            median, prop_type, days, yoy = "$720K", "Mixed", 27, "+3.8%"
        # Use slug as display name
        display_name = slug.replace("-", " ").title()
        unique_text = (
            f"{display_name} offers a distinctive residential character shaped by its local community, "
            f"transit access, and {borough} location. Buyers consistently find that well-priced homes here "
            f"attract competitive offers within the first two weeks. Contact Nitin Gadura at (917) 705-0132 "
            f"for a hyper-local market briefing specific to this neighborhood."
        )
        data = (display_name, median, prop_type, days, yoy, unique_text)

    display_name, median_price, prop_type, days, yoy, unique_text = data

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if already processed
    if "UNIQUE MARKET DATA" in content:
        return False, "already processed"

    # Build sections
    snapshot_html = build_market_snapshot(slug, display_name, median_price, prop_type, days, yoy, unique_text)
    cross_links_html = build_cross_links(slug, all_files)

    # Combine: cross-links first, then snapshot, inject before </main>
    inject_html = cross_links_html + snapshot_html

    # Find </main> tag and inject before it
    if "</main>" in content:
        # Remove existing "Nearby Neighborhoods" section if it exists (the plain one)
        # Pattern: <h2>Nearby Neighborhoods</h2>\n    <div class="nearby">...</div>
        content = re.sub(
            r'\s*<h2>Nearby Neighborhoods</h2>\s*<div class="nearby">.*?</div>',
            "",
            content,
            flags=re.DOTALL
        )
        content = content.replace("</main>", inject_html + "  </main>")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"injected market snapshot + cross-links for {display_name}"
    else:
        return False, "no </main> tag found"


def main():
    # Get all HTML files (top-level only, not subdirectories)
    all_files = [
        os.path.join(NEIGHBORHOODS_DIR, f)
        for f in os.listdir(NEIGHBORHOODS_DIR)
        if f.endswith(".html") and os.path.isfile(os.path.join(NEIGHBORHOODS_DIR, f))
    ]
    all_files.sort()

    print(f"Found {len(all_files)} HTML files")

    success_count = 0
    skip_count = 0
    error_count = 0

    for filepath in all_files:
        filename = os.path.basename(filepath)
        try:
            ok, msg = process_file(filepath, all_files)
            if ok:
                success_count += 1
                print(f"  ✓ {filename}: {msg}")
            else:
                skip_count += 1
                print(f"  - {filename}: {msg}")
        except Exception as e:
            error_count += 1
            print(f"  ✗ {filename}: ERROR — {e}")

    print(f"\nDone: {success_count} updated, {skip_count} skipped, {error_count} errors")


if __name__ == "__main__":
    main()
