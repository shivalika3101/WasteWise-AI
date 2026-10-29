INSERT INTO disposal_instructions (category_id, instructions, notes)
VALUES

(
    (SELECT id FROM categories WHERE name = 'aerosol_cans'),
    'Empty completely. If possible, rinse the aerosol can and place it in the Mixed Dry Recycling bin.',
    'Must be completely empty. Do not puncture or crush. Partially full cans may require hazardous waste disposal depending on local rules.'
),

(
    (SELECT id FROM categories WHERE name = 'aluminum_food_cans'),
    'Empty and rinse, then place in the Mixed Dry Recycling bin.',
    'Remove food residue before recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'aluminum_soda_cans'),
    'Empty and rinse, then place in the Mixed Dry Recycling bin.',
    'Crush only if accepted locally.'
),

(
    (SELECT id FROM categories WHERE name = 'cardboard_boxes'),
    'Flatten the cardboard box and place it in the Paper & Card bin.',
    'Keep dry. Remove excessive plastic tape or packaging if possible.'
),

(
    (SELECT id FROM categories WHERE name = 'cardboard_packaging'),
    'Flatten if possible and place it in the Paper & Card bin.',
    'Keep clean and dry. Remove plastic inserts where practical.'
),

(
    (SELECT id FROM categories WHERE name = 'clothing'),
    'Place clean, dry clothing in the Textiles bin.',
    'Donate reusable clothing whenever possible. Wet or contaminated clothing should go to General Waste.'
),

(
    (SELECT id FROM categories WHERE name = 'coffee_grounds'),
    'Place coffee grounds in the Food / Organic bin.',
    'Remove from plastic or metal coffee pods before disposal.'
),

(
    (SELECT id FROM categories WHERE name = 'disposable_plastic_cutlery'),
    'Dispose of disposable plastic cutlery in the General Waste bin.',
    'Not commonly recyclable due to size and material.'
),

(
    (SELECT id FROM categories WHERE name = 'eggshells'),
    'Place eggshells in the Food / Organic bin.',
    'Remove any packaging first.'
),

(
    (SELECT id FROM categories WHERE name = 'food_waste'),
    'Place food scraps in the Food / Organic bin.',
    'Remove all plastic, metal, or glass packaging before disposal.'
),

(
    (SELECT id FROM categories WHERE name = 'glass_beverage_bottles'),
    'Empty and rinse the bottle, then place it in the Glass bin.',
    'Remove lids or caps if required by local recycling guidelines.'
),

(
    (SELECT id FROM categories WHERE name = 'glass_cosmetic_containers'),
    'Empty and rinse the container, then place it in the Glass bin.',
    'Remove pumps, plastic lids, or dispensers before recycling where applicable.'
),

(
    (SELECT id FROM categories WHERE name = 'glass_food_jars'),
    'Empty and rinse the jar, then place it in the Glass bin.',
    'Remove metal lids if collected separately.'
),

(
    (SELECT id FROM categories WHERE name = 'magazines'),
    'Keep clean and dry, then place in the Paper & Card bin.',
    'Avoid recycling glossy magazines if prohibited locally.'
),

(
    (SELECT id FROM categories WHERE name = 'newspaper'),
    'Keep clean and dry, then place in the Paper & Card bin.',
    'Do not recycle wet or heavily soiled newspapers.'
),

(
    (SELECT id FROM categories WHERE name = 'office_paper'),
    'Place clean office paper in the Paper & Card bin.',
    'Remove plastic sleeves or bindings before recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'paper_cups'),
    'Dispose of used paper cups in the General Waste bin.',
    'Paper cups often contain a plastic lining and are not accepted in standard paper recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_cup_lids'),
    'Dispose of plastic cup lids in the General Waste bin.',
    'Small plastic items are often not accepted in recycling streams.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_detergent_bottles'),
    'Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.',
    'Replace the cap if accepted locally or dispose of it separately according to local guidance.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_food_containers'),
    'Empty and rinse the container, then place it in the Mixed Dry Recycling bin.',
    'Remove leftover food before recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_shopping_bags'),
    'Place clean plastic shopping bags in the Plastic & Cans collection.',
    'Keep bags clean and dry. Do not include heavily contaminated bags.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_soda_bottles'),
    'Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.',
    'Crush if accepted locally to save space.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_straws'),
    'Dispose of plastic straws in the General Waste bin.',
    'Too small for most recycling systems.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_trash_bags'),
    'Place clean plastic trash bags in the Plastic & Cans collection.',
    'Only if clean and free from household waste residue. Dirty bags belong in General Waste.'
),

(
    (SELECT id FROM categories WHERE name = 'plastic_water_bottles'),
    'Empty and rinse the bottle, then place it in the Mixed Dry Recycling bin.',
    'Remove caps if required by your local recycling program.'
),

(
    (SELECT id FROM categories WHERE name = 'shoes'),
    'Place reusable shoes in the Textiles bin.',
    'Tie pairs together where possible. Damaged shoes may need General Waste disposal if textile recycling is unavailable.'
),

(
    (SELECT id FROM categories WHERE name = 'steel_food_cans'),
    'Empty and rinse the can, then place it in the Mixed Dry Recycling bin.',
    'Remove food residue before recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'styrofoam_cups'),
    'Dispose of styrofoam cups in the General Waste bin.',
    'Styrofoam is generally not accepted in curbside recycling.'
),

(
    (SELECT id FROM categories WHERE name = 'styrofoam_food_containers'),
    'Dispose of styrofoam food containers in the General Waste bin.',
    'Remove food scraps before disposal.'
),

(
    (SELECT id FROM categories WHERE name = 'tea_bags'),
    'Place tea bags in the Food / Organic bin.',
    'Remove staples or plastic components if present.'
);