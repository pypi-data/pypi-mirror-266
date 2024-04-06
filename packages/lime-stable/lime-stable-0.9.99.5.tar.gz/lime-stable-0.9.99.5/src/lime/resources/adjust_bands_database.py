import lime

db = lime.load_frame('parent_bands.txt')

db.insert(9, 'units_wave', 'Angstrom')
lime.save_frame('parent_bands.txt', db)

print(db)