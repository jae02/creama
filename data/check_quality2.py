from models import *
from sqlalchemy import text

s = get_session()

result = s.execute(text(
    "SELECT vibe_keywords, COUNT(*) as cnt FROM sensory_data GROUP BY vibe_keywords ORDER BY cnt DESC LIMIT 8"
)).fetchall()
print('Top vibe_keywords values:')
for row in result:
    vk = str(row[0])[:50] if row[0] else 'NULL'
    print(f'  [{vk}] -> {row[1]}')

default_check = s.execute(text(
    "SELECT COUNT(*) FROM sensory_data WHERE noise_level=50 AND lighting=50 AND comfort=50 AND acidity=3.0 AND body=3.0"
)).scalar()
total = s.query(SensoryData).count()
print(f'\nAll-defaults cafes: {default_check} / {total}')
print(f'Real-data cafes:    {total - default_check} / {total}')
s.close()
