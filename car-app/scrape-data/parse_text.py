import re

CAR_MAKES = ['Acura', 'Audi', 'BMW', 'Buick', 'Cadillac', 'Chevrolet', 'Chrysler', 'Dodge', 'Ford', 'Genesis', 'GMC', 'Honda', 'Hyundai', 'INFINITI', 'Jaguar', 'Jeep', 'Kia', 'Land Rover', 'Lexus', 'Lincoln', 'Mazda', 'Mercedes-Benz', 'MINI', 'Mitsubishi', 'Nissan', 'Porsche', 'RAM', 'Subaru', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo', 'AC', 'Alfa Romeo', 'Am General', 'American Motors', 'Aston Martin', 'Austin', 'Austin-Healey', 'Avanti Motors', 'Bentley', 'Bremen', 'Bricklin', 'Bugatti', 'Citroen', 'Cord', 'Datsun', 'Delahaye', 'Delorean', 'Desoto', 'DeTomaso', 'Eagle', 'Edsel', 'Excalibur', 'Facel-Vega', 'Ferrari', 'FIAT', 'Fisker', 'GAZ', 'Geo', 'Hudson', 'Hummer', 'INEOS', 'International', 'Isuzu', 'Jensen', 'Kaiser', 'Karma', 'Koenigsegg', 'Lamborghini', 'Lancia', 'Lotus', 'Lucid', 'Maserati', 'Maybach', 'McLaren', 'Mercury', 'MG', 'Nash', 'Oldsmobile', 'Packard', 'Pagani', 'Panoz', 'Plymouth', 'Polestar', 'Pontiac', 'Rambler', 'Renault', 'Rivian', 'Rolls-Royce', 'Saab', 'Saturn', 'Scion', 'smart', 'Studebaker', 'Sunbeam', 'Suzuki', 'Triumph', 'VinFast', 'Willys']

def parse_vehicle_title(title):
    make_pattern = "|".join([re.escape(make) for make in CAR_MAKES])

    title_match = re.match(rf"(\d{{4}})\s+({make_pattern})\s+(.+)", title)
    if title_match:
        year = title_match.group(1)
        make = title_match.group(2).strip()
        model_trim = title_match.group(3)
        return {'year': year, 'make': make, 'model_trim': model_trim}
    else:
        return None

def clean_location(location):
    return re.sub(r"\s*\(\d+\s*mi\.\)", "", location).strip()