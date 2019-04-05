from PIL import Image
import pathlib

image = '/home/shailesh/Pictures/dataset'

path = pathlib.Path(image)
print(path)

items = [item for item in path.glob('**/*') if item.is_file()]

for each in items:
    img = Image.open(each).convert('RGB')
    img = img.resize((256, 256))
    img.save(each)
