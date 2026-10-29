-- =====================================================
-- Insert Bins
-- =====================================================

INSERT INTO bins (name, colour, description)
VALUES
('Mixed Dry Recycling', 'green', 'Rinsed plastic bottles & containers, aluminium & steel cans, empty aerosols.'),
('Paper & Card', 'blue', 'Clean paper, cardboard, magazines, newspaper, office paper.'),
('Glass', 'bottle bank', 'Glass bottles and jars (rinsed).'),
('Food / Organic', 'brown', 'Food scraps, coffee grounds, eggshells, tea bags.'),
('General Waste', 'black', 'Non-recyclables: styrofoam, straws, cutlery, lined paper cups.'),
('Textiles', 'textile bank', 'Clothing and shoes (re-use / donation / textile bank).'),
('Plastic & Cans', 'red sack', 'Plastic film & bags, plastic packaging and cans.');



-- =====================================================
-- Insert Categories
-- =====================================================

INSERT INTO categories (name, display_name, model_label_index)
VALUES
('aerosol_cans', 'Aerosol can', 0),
('aluminum_food_cans', 'Aluminium food can', 1),
('aluminum_soda_cans', 'Aluminium soda can', 2),
('cardboard_boxes', 'Cardboard box', 3),
('cardboard_packaging', 'Cardboard packaging', 4),
('clothing', 'Clothing', 5),
('coffee_grounds', 'Coffee grounds', 6),
('disposable_plastic_cutlery', 'Disposable plastic cutlery', 7),
('eggshells', 'Eggshells', 8),
('food_waste', 'Food waste', 9),
('glass_beverage_bottles', 'Glass beverage bottle', 10),
('glass_cosmetic_containers', 'Glass cosmetic container', 11),
('glass_food_jars', 'Glass food jar', 12),
('magazines', 'Magazine', 13),
('newspaper', 'Newspaper', 14),
('office_paper', 'Office paper', 15),
('paper_cups', 'Paper cup', 16),
('plastic_cup_lids', 'Plastic cup lid', 17),
('plastic_detergent_bottles', 'Plastic detergent bottle', 18),
('plastic_food_containers', 'Plastic food container', 19),
('plastic_shopping_bags', 'Plastic shopping bag', 20),
('plastic_soda_bottles', 'Plastic soda bottle', 21),
('plastic_straws', 'Plastic straw', 22),
('plastic_trash_bags', 'Plastic trash bag', 23),
('plastic_water_bottles', 'Plastic water bottle', 24),
('shoes', 'Shoes', 25),
('steel_food_cans', 'Steel food can', 26),
('styrofoam_cups', 'Styrofoam cup', 27),
('styrofoam_food_containers', 'Styrofoam food container', 28),
('tea_bags', 'Tea bags', 29);