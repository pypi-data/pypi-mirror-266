import os
from PIL import Image


class ImageCropper:
    def __init__(self, width=None, height=None, ratio=None, resize=None):
        self.width = width
        self.height = height
        self.resize = False
        if ratio:
            self.ratio_width, self.ratio_height = map(int, ratio.split(":"))
            self.ratio = self.ratio_width / self.ratio_height
        else:
            self.ratio = None
            if resize:
                self.resize = True

    def crop_image(self, path, file_path=None):
        output_path = None
        if file_path:
            output_path = file_path.copy()
        if file_path:
            arquivo = path.split("/")[-1].split(".")
        else:
            arquivo = path.split(".")
        nome_arquivo = arquivo[-2]
        tipo_arquivo = arquivo[-1]
        image = Image.open(path)
        if self.ratio:
            case = "change_height"
            if image.width / image.height >= self.ratio:
                case = "change_width"
            if case == "change_width":
                # if landscape
                self.height = image.height
                self.width = image.height / self.ratio_height * self.ratio_width
            else:
                self.width = image.width
                self.height = image.width / self.ratio_width * self.ratio_height
        else:
            if self.resize:
                # this probably can be easier
                if self.height > self.width:
                    scale_case = "height"
                elif self.height < self.width:
                    scale_case = "width"
                else:
                    if image.height > image.width:
                        scale_case = "width"
                    else:
                        scale_case = "height"
                if scale_case == "height":
                    scale = image.height / self.height
                else:
                    scale = image.width / self.width
                image = image.resize(
                    (int(image.width / scale), int(image.height / scale)),
                    resample=Image.Resampling.LANCZOS,
                )

        start_w = image.width / 2 - self.width / 2
        end_w = image.width / 2 + self.width / 2
        start_h = image.height / 2 - self.height / 2
        end_h = image.height / 2 + self.height / 2
        image = image.crop((start_w, start_h, end_w, end_h))

        if output_path is not None:
            output_path[0] = output_path[0] + "-crop"
            filepath = ""
            for subpath in output_path:
                filepath += subpath
                filepath += "/"

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(
                f"{filepath}{nome_arquivo}-{int(self.width)}x{int(self.height)}.{tipo_arquivo}",
                "wb",
            ) as f:
                image.save(f)
        else:
            image.save(
                f"{nome_arquivo}-{int(self.width)}x{int(self.height)}.{tipo_arquivo}"
            )
