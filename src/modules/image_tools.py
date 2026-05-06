try:
    import imageio.v3 as iio
except ImportError:
    iio = None

try:
    from PIL import Image
except ImportError:
    Image = None

def check_flag_size(image_path, expected_width=256, expected_height=160):
    '''Check if the image has the expected dimensions.'''
    if Image is None:
        print("Pillow not installed. Skipping flag size check.")
        return True
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"Image size: {width}x{height}")
            return width == expected_width and height == expected_height
    except Exception as e:
        print(f"Error: {e}")
        return False
    

def png_to_dds(png_path, dds_path):
    '''Convert a PNG image to DDS format.'''
    if iio is None:
        print("imageio not installed. Skipping DDS conversion.")
        return False
    try:
        img = iio.imread(png_path)
        iio.imwrite(dds_path, img, format='dds')
        return True
    except Exception as e:
        print(f"Error converting PNG to DDS: {e}")
        return False


    

