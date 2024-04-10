from PIL import Image


class photoUtil:
    target_width = 295
    target_height = 413

    def __init__(self, target_width, target_height):
        self.target_width = target_width
        self.target_height = target_height

    def trans(self, source, target):
        # 打开原始图片
        image = Image.open(source)
        # # 定义目标尺寸
        # target_width = 800
        # target_height = 600
        # 调整图片尺寸
        resized_image = image.resize((self.target_width, self.target_height))
        if str(source).upper().endswith(".PNG"):
            # 调整图片格式
            resized_image_rgb = resized_image.convert("RGB")
            resized_image_rgb.save(target)
        else:
            try:
                # 保存调整后的图片
                resized_image.save(target)
            except OSError:
                print("Failed to open file:" + source)
                resized_image_rgb2 = resized_image.convert("RGB")
                resized_image_rgb2.save(target)
                print("success to tran file:" + source)
            except  Exception as e:
                print("error:source:" + source + ",target:" + target + ",error:" + e)

    def png2jpg(self, source, target):
        image = Image.open(source)
        rgb_image = image.convert("RGB")
        rgb_image.save(target)
