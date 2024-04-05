import skimage.io as io
from ciliaseg.state.image import SEMImage
import os.path

def save_image_as_csv(image: SEMImage, path: str):
    assert path.endswith('.csv'), 'save path filename must end in ".csv"'

    with open(path, 'w') as file:
        file.write('image_name,type,x_vertices,y_vertices,n_vertices,score,bbox\n')

        for s in image.get_stereocilia():
            xstr = str(s.x())
            ystr = str(s.y())

            xstr = xstr.replace(',', ' ')
            ystr = ystr.replace(',', ' ')

            bboxstr = str(s.bbox()).replace(',', ' ')
            file.write(f'{image.filepath},{s.get_label_str()},{xstr},{ystr},{len(s.x())},{s.get_score()},{bboxstr}\n')


def load_stereocilia_from_csv(path: str) -> SEMImage:

    assert os.path.exists(path), f'{path=} does not exist'

    with open(path, 'r') as file:
        line0 = file.readline()
        line1 = file.readline()
        if line1 is None:
            return None
        path = line1.split(',')[0]

    assert os.path.exists(), f'{path=} does not exist'

    image = SEMImage().load_image(path)






