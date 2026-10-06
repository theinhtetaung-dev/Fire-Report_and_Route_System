"""Rebuild the renamed OFL font with Myanmar and Latin coverage."""
from pathlib import Path
from fontTools.merge import Merger

root = Path(__file__).resolve().parent
font = Merger().merge([str(root / 'NotoSansMyanmar-Regular.ttf'), str(root / 'NotoSans-Regular.ttf')])
names = {1: 'Emergency Demo', 2: 'Regular', 3: 'Emergency Demo Regular',
         4: 'Emergency Demo Regular', 6: 'EmergencyDemo-Regular',
         16: 'Emergency Demo', 17: 'Regular'}
for record in font['name'].names:
    if record.nameID in names:
        record.string = names[record.nameID].encode(record.getEncoding())
font.save(root / 'NotoEmergency-Regular.ttf')
