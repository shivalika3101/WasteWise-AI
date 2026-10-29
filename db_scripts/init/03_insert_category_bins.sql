INSERT INTO category_bins (category_id, bin_id, is_primary)
VALUES

((SELECT id FROM categories WHERE name='aerosol_cans'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='aluminum_food_cans'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='aluminum_soda_cans'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='cardboard_boxes'),
 (SELECT id FROM bins WHERE name='Paper & Card'), TRUE),

((SELECT id FROM categories WHERE name='cardboard_packaging'),
 (SELECT id FROM bins WHERE name='Paper & Card'), TRUE),

((SELECT id FROM categories WHERE name='clothing'),
 (SELECT id FROM bins WHERE name='Textiles'), TRUE),

((SELECT id FROM categories WHERE name='coffee_grounds'),
 (SELECT id FROM bins WHERE name='Food / Organic'), TRUE),

((SELECT id FROM categories WHERE name='disposable_plastic_cutlery'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='eggshells'),
 (SELECT id FROM bins WHERE name='Food / Organic'), TRUE),

((SELECT id FROM categories WHERE name='food_waste'),
 (SELECT id FROM bins WHERE name='Food / Organic'), TRUE),

((SELECT id FROM categories WHERE name='glass_beverage_bottles'),
 (SELECT id FROM bins WHERE name='Glass'), TRUE),

((SELECT id FROM categories WHERE name='glass_cosmetic_containers'),
 (SELECT id FROM bins WHERE name='Glass'), TRUE),

((SELECT id FROM categories WHERE name='glass_food_jars'),
 (SELECT id FROM bins WHERE name='Glass'), TRUE),

((SELECT id FROM categories WHERE name='magazines'),
 (SELECT id FROM bins WHERE name='Paper & Card'), TRUE),

((SELECT id FROM categories WHERE name='newspaper'),
 (SELECT id FROM bins WHERE name='Paper & Card'), TRUE),

((SELECT id FROM categories WHERE name='office_paper'),
 (SELECT id FROM bins WHERE name='Paper & Card'), TRUE),

((SELECT id FROM categories WHERE name='paper_cups'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='plastic_cup_lids'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='plastic_detergent_bottles'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='plastic_food_containers'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='plastic_shopping_bags'),
 (SELECT id FROM bins WHERE name='Plastic & Cans'), TRUE),

((SELECT id FROM categories WHERE name='plastic_soda_bottles'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='plastic_straws'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='plastic_trash_bags'),
 (SELECT id FROM bins WHERE name='Plastic & Cans'), TRUE),

((SELECT id FROM categories WHERE name='plastic_water_bottles'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='shoes'),
 (SELECT id FROM bins WHERE name='Textiles'), TRUE),

((SELECT id FROM categories WHERE name='steel_food_cans'),
 (SELECT id FROM bins WHERE name='Mixed Dry Recycling'), TRUE),

((SELECT id FROM categories WHERE name='styrofoam_cups'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='styrofoam_food_containers'),
 (SELECT id FROM bins WHERE name='General Waste'), TRUE),

((SELECT id FROM categories WHERE name='tea_bags'),
 (SELECT id FROM bins WHERE name='Food / Organic'), TRUE);