# =====================================================
# Seed Data
# WasteWise AI
# =====================================================

# -----------------------------
# Bins
# -----------------------------

BINS = [
    {
        "name": "Mixed Dry Recycling",
        "colour": "green",
        "description": "Rinsed plastic bottles & containers, aluminium & steel cans, empty aerosols.",
    },
    {
        "name": "Paper & Card",
        "colour": "blue",
        "description": "Clean paper, cardboard, magazines, newspaper, office paper.",
    },
    {
        "name": "Glass",
        "colour": "bottle bank",
        "description": "Glass bottles and jars (rinsed).",
    },
    {
        "name": "Food / Organic",
        "colour": "brown",
        "description": "Food scraps, coffee grounds, eggshells, tea bags.",
    },
    {
        "name": "General Waste",
        "colour": "black",
        "description": "Non-recyclables: styrofoam, straws, cutlery, lined paper cups.",
    },
    {
        "name": "Textiles",
        "colour": "textile bank",
        "description": "Clothing and shoes (re-use / donation / textile bank).",
    },
    {
        "name": "Plastic & Cans",
        "colour": "red sack",
        "description": "Plastic film & bags, plastic packaging and cans.",
    },
]

# -----------------------------
# Categories
# -----------------------------

CATEGORIES = [
    {"name": "aerosol_cans", "display_name": "Aerosol can", "model_label_index": 0},
    {"name": "aluminum_food_cans", "display_name": "Aluminium food can", "model_label_index": 1},
    {"name": "aluminum_soda_cans", "display_name": "Aluminium soda can", "model_label_index": 2},
    {"name": "cardboard_boxes", "display_name": "Cardboard box", "model_label_index": 3},
    {"name": "cardboard_packaging", "display_name": "Cardboard packaging", "model_label_index": 4},
    {"name": "clothing", "display_name": "Clothing", "model_label_index": 5},
    {"name": "coffee_grounds", "display_name": "Coffee grounds", "model_label_index": 6},
    {"name": "disposable_plastic_cutlery", "display_name": "Disposable plastic cutlery", "model_label_index": 7},
    {"name": "eggshells", "display_name": "Eggshells", "model_label_index": 8},
    {"name": "food_waste", "display_name": "Food waste", "model_label_index": 9},
    {"name": "glass_beverage_bottles", "display_name": "Glass beverage bottle", "model_label_index": 10},
    {"name": "glass_cosmetic_containers", "display_name": "Glass cosmetic container", "model_label_index": 11},
    {"name": "glass_food_jars", "display_name": "Glass food jar", "model_label_index": 12},
    {"name": "magazines", "display_name": "Magazine", "model_label_index": 13},
    {"name": "newspaper", "display_name": "Newspaper", "model_label_index": 14},
    {"name": "office_paper", "display_name": "Office paper", "model_label_index": 15},
    {"name": "paper_cups", "display_name": "Paper cup", "model_label_index": 16},
    {"name": "plastic_cup_lids", "display_name": "Plastic cup lid", "model_label_index": 17},
    {"name": "plastic_detergent_bottles", "display_name": "Plastic detergent bottle", "model_label_index": 18},
    {"name": "plastic_food_containers", "display_name": "Plastic food container", "model_label_index": 19},
    {"name": "plastic_shopping_bags", "display_name": "Plastic shopping bag", "model_label_index": 20},
    {"name": "plastic_soda_bottles", "display_name": "Plastic soda bottle", "model_label_index": 21},
    {"name": "plastic_straws", "display_name": "Plastic straw", "model_label_index": 22},
    {"name": "plastic_trash_bags", "display_name": "Plastic trash bag", "model_label_index": 23},
    {"name": "plastic_water_bottles", "display_name": "Plastic water bottle", "model_label_index": 24},
    {"name": "shoes", "display_name": "Shoes", "model_label_index": 25},
    {"name": "steel_food_cans", "display_name": "Steel food can", "model_label_index": 26},
    {"name": "styrofoam_cups", "display_name": "Styrofoam cup", "model_label_index": 27},
    {"name": "styrofoam_food_containers", "display_name": "Styrofoam food container", "model_label_index": 28},
    {"name": "tea_bags", "display_name": "Tea bags", "model_label_index": 29},
]

# -----------------------------
# Category -> Bin Mapping
# -----------------------------

CATEGORY_BINS = [
    ("aerosol_cans", "Mixed Dry Recycling"),
    ("aluminum_food_cans", "Mixed Dry Recycling"),
    ("aluminum_soda_cans", "Mixed Dry Recycling"),
    ("cardboard_boxes", "Paper & Card"),
    ("cardboard_packaging", "Paper & Card"),
    ("clothing", "Textiles"),
    ("coffee_grounds", "Food / Organic"),
    ("disposable_plastic_cutlery", "General Waste"),
    ("eggshells", "Food / Organic"),
    ("food_waste", "Food / Organic"),
    ("glass_beverage_bottles", "Glass"),
    ("glass_cosmetic_containers", "Glass"),
    ("glass_food_jars", "Glass"),
    ("magazines", "Paper & Card"),
    ("newspaper", "Paper & Card"),
    ("office_paper", "Paper & Card"),
    ("paper_cups", "General Waste"),
    ("plastic_cup_lids", "General Waste"),
    ("plastic_detergent_bottles", "Mixed Dry Recycling"),
    ("plastic_food_containers", "Mixed Dry Recycling"),
    ("plastic_shopping_bags", "Plastic & Cans"),
    ("plastic_soda_bottles", "Mixed Dry Recycling"),
    ("plastic_straws", "General Waste"),
    ("plastic_trash_bags", "Plastic & Cans"),
    ("plastic_water_bottles", "Mixed Dry Recycling"),
    ("shoes", "Textiles"),
    ("steel_food_cans", "Mixed Dry Recycling"),
    ("styrofoam_cups", "General Waste"),
    ("styrofoam_food_containers", "General Waste"),
    ("tea_bags", "Food / Organic"),
]

# -----------------------------
# Disposal Instructions
# -----------------------------

DISPOSAL_INSTRUCTIONS = [
    {
        "category": "aerosol_cans",
        "instructions": "Empty completely. If possible, rinse the aerosol can and place it in the Mixed Dry Recycling bin.",
        "notes": "Must be completely empty. Do not puncture or crush. Partially full cans may require hazardous waste disposal depending on local rules.",
    },
    {
        "category": "aluminum_food_cans",
        "instructions": "Empty and rinse, then place in the Mixed Dry Recycling bin.",
        "notes": "Remove food residue before recycling.",
    },
    {
        "category": "aluminum_soda_cans",
        "instructions": "Empty and rinse, then place in the Mixed Dry Recycling bin.",
        "notes": "Crush only if accepted locally.",
    },
    {
        "category": "cardboard_boxes",
        "instructions": "Flatten the cardboard box and place it in the Paper & Card bin.",
        "notes": "Keep dry. Remove excessive plastic tape or packaging if possible.",
    },
    {
        "category": "cardboard_packaging",
        "instructions": "Flatten if possible and place it in the Paper & Card bin.",
        "notes": "Keep clean and dry. Remove plastic inserts where practical.",
    },
    {
        "category": "clothing",
        "instructions": "Place clean, dry clothing in the Textiles bin.",
        "notes": "Donate reusable clothing whenever possible. Wet or contaminated clothing should go to General Waste.",
    },
    {
        "category": "coffee_grounds",
        "instructions": "Place coffee grounds in the Food / Organic bin.",
        "notes": "Remove from plastic or metal coffee pods before disposal.",
    },
    {
        "category": "disposable_plastic_cutlery",
        "instructions": "Dispose of disposable plastic cutlery in the General Waste bin.",
        "notes": "Not commonly recyclable due to size and material.",
    },
    {
        "category": "eggshells",
        "instructions": "Place eggshells in the Food / Organic bin.",
        "notes": "Remove any packaging first.",
    },
    {
        "category": "food_waste",
        "instructions": "Place food scraps in the Food / Organic bin.",
        "notes": "Remove all plastic, metal, or glass packaging before disposal.",
    },
    {
        "category": "glass_beverage_bottles",
        "instructions": "Empty and rinse the bottle, then place it in the Glass bin.",
        "notes": "Remove lids or caps if required by local recycling guidelines.",
    },
    {
        "category": "glass_cosmetic_containers",
        "instructions": "Empty and rinse the container, then place it in the Glass bin.",
        "notes": "Remove pumps, plastic lids, or dispensers before recycling where applicable.",
    },
    {
        "category": "glass_food_jars",
        "instructions": "Empty and rinse the jar, then place it in the Glass bin.",
        "notes": "Remove metal lids if collected separately.",
    },
    {
        "category": "magazines",
        "instructions": "Keep clean and dry, then place in the Paper & Card bin.",
        "notes": "Avoid recycling glossy magazines if prohibited locally.",
    },
    {
        "category": "newspaper",
        "instructions": "Keep clean and dry, then place in the Paper & Card bin.",
        "notes": "Do not recycle wet or heavily soiled newspapers.",
    },
    {
        "category": "office_paper",
        "instructions": "Place clean office paper in the Paper & Card bin.",
        "notes": "Remove plastic sleeves or bindings before recycling.",
    },
    {
        "category": "paper_cups",
        "instructions": "Dispose of used paper cups in the General Waste bin.",
        "notes": "Paper cups often contain a plastic lining and are not accepted in standard paper recycling.",
    },
    {
        "category": "plastic_cup_lids",
        "instructions": "Dispose of plastic cup lids in the General Waste bin.",
        "notes": "Small plastic items are often not accepted in recycling streams.",
    },
    {
        "category": "plastic_detergent_bottles",
        "instructions": "Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.",
        "notes": "Replace the cap if accepted locally or dispose of it separately according to local guidance.",
    },
    {
        "category": "plastic_food_containers",
        "instructions": "Empty and rinse the container, then place it in the Mixed Dry Recycling bin.",
        "notes": "Remove leftover food before recycling.",
    },
    {
        "category": "plastic_shopping_bags",
        "instructions": "Place clean plastic shopping bags in the Plastic & Cans collection.",
        "notes": "Keep bags clean and dry. Do not include heavily contaminated bags.",
    },
    {
        "category": "plastic_soda_bottles",
        "instructions": "Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.",
        "notes": "Crush if accepted locally to save space.",
    },
    {
        "category": "plastic_straws",
        "instructions": "Dispose of plastic straws in the General Waste bin.",
        "notes": "Too small for most recycling systems.",
    },
    {
        "category": "plastic_trash_bags",
        "instructions": "Place clean plastic trash bags in the Plastic & Cans collection.",
        "notes": "Only if clean and free from household waste residue. Dirty bags belong in General Waste.",
    },
    {
        "category": "plastic_water_bottles",
        "instructions": "Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.",
        "notes": "Remove caps if required by your local recycling program.",
    },
    {
        "category": "shoes",
        "instructions": "Place reusable shoes in the Textiles bin.",
        "notes": "Tie pairs together where possible. Damaged shoes may need General Waste disposal if textile recycling is unavailable.",
    },
    {
        "category": "steel_food_cans",
        "instructions": "Empty and rinse the can, then place it in the Mixed Dry Recycling bin.",
        "notes": "Remove food residue before recycling.",
    },
    {
        "category": "styrofoam_cups",
        "instructions": "Dispose of styrofoam cups in the General Waste bin.",
        "notes": "Styrofoam is generally not accepted in curbside recycling.",
    },
    {
        "category": "styrofoam_food_containers",
        "instructions": "Dispose of styrofoam food containers in the General Waste bin.",
        "notes": "Remove food scraps before disposal.",
    },
    {
        "category": "tea_bags",
        "instructions": "Place tea bags in the Food / Organic bin.",
        "notes": "Remove staples or plastic components if present.",
    },
]

# -----------------------------
# Blog Posts
# -----------------------------

BLOG_POSTS = [
    {
        "slug": "contamination-prevention",
        "title": "One Greasy Box Can Take Down a Whole Load",
        "summary": (
            "Recycling isn't sorted item by item at your bin — it's sorted by machines "
            "further down the line, and grease, liquid, and food waste are what throw them off."
        ),
        "body": (
            "Recycling doesn't get sorted the moment it leaves your bin. It gets compacted with "
            "everyone else's on the same truck, then tipped out at a materials recovery facility "
            "where conveyor belts, magnets, and optical scanners do the actual separating — "
            "plastics from paper, aluminium from steel, and so on.\n\n"
            "Grease is the recurring problem. A pizza box that's clean on top but soaked through "
            "underneath doesn't get quietly set aside; the paper fibres have already absorbed oil, "
            "which means that section of card can't be pulped into new paper the normal way. If it "
            "ends up baled together with genuinely clean cardboard, the easiest thing for a facility "
            "to do is treat the whole bale as contaminated rather than pick through it by hand.\n\n"
            "Liquid does something similar. A yoghurt pot with the last inch still in it, or a bottle "
            "with a mouthful of drink left, can soak into paper and cardboard sitting nearby in the "
            "same bin. That's why 'empty and rinse' matters more than it sounds like it should — "
            "it's not about the one container, it's about what it does to everything touching it on "
            "the way to the facility.\n\n"
            "A few habits make a bigger difference than most people expect:\n"
            "- Tear the greasy corner off a pizza box and bin that part with food waste; recycle the rest.\n"
            "- Give containers a quick rinse, not a full wash — you're removing residue, not sterilising them.\n"
            "- Keep recycling loose rather than bagged in plastic — most facilities can't open bags on "
            "the line, so a bagged batch of good recycling often gets landfilled unopened.\n"
            "- Whether bottle lids should stay on or come off varies by area, so it's worth checking "
            "your own collection rather than assuming.\n\n"
            "None of this needs to be perfect. The goal is fewer items that spoil the ones around them, "
            "not a flawless bin."
        ),
        "status": "published",
    },
    {
        "slug": "common-recycling-mistakes",
        "title": "The Recycling Habits That Are Quietly Wrong",
        "summary": (
            "Wishcycling, bagging your recyclables, and 'if in doubt, chuck it in' all feel "
            "responsible. They usually aren't."
        ),
        "body": (
            "Most recycling mistakes aren't careless — they come from good intentions applied to the "
            "wrong item. A few show up often enough to be worth calling out directly.\n\n"
            "Wishcycling is the biggest one: putting something in the recycling bin because it feels "
            "like it should be recyclable, not because you know it is. Black plastic trays are a "
            "common example — many optical sorters can't detect black plastic at all, because the "
            "sensors rely on light bouncing back off the material, and black absorbs it. A tray that "
            "looks identical to a clear one can be invisible to the machine that's supposed to sort it.\n\n"
            "Bagging recyclables in a plastic bag before putting them in the bin is another one. It "
            "feels tidier, but most sorting facilities can't safely open bags on a moving line, so a "
            "bag of otherwise-perfect recycling is often pulled and binned as general waste without "
            "ever being opened. Loose is almost always better than bagged.\n\n"
            "Small items are a quieter problem: bottle caps, plastic cutlery, and anything smaller "
            "than roughly a credit card tends to fall through the gaps in sorting screens built for "
            "bottles and boxes, and ends up in the wrong stream or jams the equipment.\n\n"
            "And then there's textiles and electronics — old clothing or a broken charger cable that "
            "end up in general recycling out of convenience. These usually have their own separate "
            "collection points because mixing them in can damage sorting machinery, not just fail to "
            "be recycled.\n\n"
            "None of this is about getting it perfect every time. It's about recognising that "
            "'probably fine' and 'actually recyclable' aren't the same thing, and that the more "
            "confident-feeling guess is often the wrong one."
        ),
        "status": "published",
    },
    {
        "slug": "understanding-confidence-scores",
        "title": "What That Confidence Percentage Actually Means",
        "summary": (
            "WasteWise doesn't rely on one model — it combines the probability estimates from four. "
            "Here's what the resulting confidence score is actually telling you."
        ),
        "body": (
            "When you upload a photo, WasteWise doesn't run it through a single model and take "
            "whatever comes out. It sends the same image to four separately trained models, each of "
            "which independently produces a probability for every supported waste category. Those "
            "probability vectors are normalised and averaged class by class. The category with the "
            "highest average probability is the result you see.\n\n"
            "The displayed confidence is that highest average probability, expressed as a percentage. "
            "A higher value means the ensemble placed more of its combined probability on the displayed "
            "category. A lower value means its combined probability was spread more widely, which can "
            "happen with poor lighting, an unusual angle, similar-looking categories, or an object "
            "outside the categories it was trained to recognise.\n\n"
            "Low confidence isn't a system malfunction. It's the system telling you something honest: "
            "this one is a judgement call. In that situation, treat the suggested bin as a starting "
            "point rather than an instruction — a second look at the item, or checking it against a "
            "couple of examples of the category shown, usually resolves it faster than trying to force "
            "a clearer photo.\n\n"
            "It's also worth knowing what confidence doesn't tell you. It isn't a measure of how "
            "common the item is, and it isn't a guarantee the category itself is right — it's "
            "the ensemble's averaged probability for the displayed category, not a calibrated guarantee "
            "that the answer is correct. If a photo is "
            "dark, blurry, or shows more than one item at once, expect the score to reflect that "
            "uncertainty honestly rather than assume the model is simply wrong."
        ),
        "status": "published",
    },
]
