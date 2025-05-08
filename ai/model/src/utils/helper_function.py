def extract_image_url(item):
    if isinstance(item.get("image_url"), str) and item.get("image_url"):
        return item.get("image_url")
    
    if isinstance(item.get("imageUrl"), str) and item.get("imageUrl"):
        return item.get("imageUrl")
    if isinstance(item.get("image"), str) and item.get("image"):
        return item.get("image")
    
    # Check for array-based image fields
    for field in ["image_url", "imageUrl", "image", "images"]:
        # If the field exists and is a list/array
        if isinstance(item.get(field), list) and len(item.get(field)) > 0:
            first_image = item.get(field)[0]
            # If the item is a string, use it directly
            if isinstance(first_image, str):
                return first_image
            # If the item is a dict with a url field
            elif isinstance(first_image, dict) and first_image.get("url"):
                return first_image.get("url")
    
    # Nothing found
    return ""
def to_dict(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    elif isinstance(obj, dict):
        return obj
    else:
        return {}