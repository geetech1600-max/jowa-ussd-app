-- Sample data for JOWA application
INSERT INTO users (phone_number, full_name, skills, location) VALUES
('+260971234567', 'John Banda', 'Construction, Carpentry, Painting', 'Lusaka'),
('+260972345678', 'Mary Phiri', 'Cleaning, Cooking, Childcare', 'Ndola'),
('+260973456789', 'Peter Mwale', 'Farming, Gardening, Driving', 'Kitwe')
ON CONFLICT (phone_number) DO NOTHING;

INSERT INTO employers (phone_number, company_name, business_type) VALUES
('+260974567890', 'BuildRight Construction', 'Construction'),
('+260975678901', 'CleanSweep Services', 'Cleaning'),
('+260976789012', 'GreenThumb Farming', 'Agriculture')
ON CONFLICT (phone_number) DO NOTHING;

INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
SELECT e.id, 'Construction Helper', 'Need helper for construction site. Must be strong and reliable.', 'Lusaka', 80.00, 'daily'
FROM employers e WHERE e.phone_number = '+260974567890'
ON CONFLICT DO NOTHING;

INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
SELECT e.id, 'Office Cleaner', 'Cleaning office building in town center. Evening shifts.', 'Ndola', 50.00, 'daily'
FROM employers e WHERE e.phone_number = '+260975678901'
ON CONFLICT DO NOTHING;

INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
SELECT e.id, 'Farm Worker', 'General farm work including planting and harvesting.', 'Kitwe', 60.00, 'daily'
FROM employers e WHERE e.phone_number = '+260976789012'
ON CONFLICT DO NOTHING;