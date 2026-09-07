try:
    from PIL import Image
except ImportError:
    Image = None

def tile_image(image_path: str, tile_size: int = 512, overlap: int = 64) -> list[dict]:
    """Splits an image into overlapping tiles."""
    if not Image:
        return [{"image": None, "x": 0, "y": 0, "w": tile_size, "h": tile_size, "tile_idx": 0}]
        
    try:
        img = Image.open(image_path)
    except Exception:
        return [{"image": None, "x": 0, "y": 0, "w": tile_size, "h": tile_size, "tile_idx": 0}]
        
    width, height = img.size
    stride = tile_size - overlap
    
    tiles = []
    tile_idx = 0
    
    for y in range(0, height, stride):
        for x in range(0, width, stride):
            w = min(tile_size, width - x)
            h = min(tile_size, height - y)
            
            box = (x, y, x + w, y + h)
            tile_img = img.crop(box)
            
            tiles.append({
                "image": tile_img,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "tile_idx": tile_idx
            })
            tile_idx += 1
            
    return tiles
