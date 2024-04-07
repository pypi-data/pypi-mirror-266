from django.db import models


class ModelType(models.Model):
    name = models.CharField(max_length=100, verbose_name='名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '选项类型'
        verbose_name_plural = verbose_name


class ModelX(models.Model):
    model_filed1 = models.CharField(max_length=100, verbose_name="模型X字段1")
    model_filed2 = models.CharField(max_length=100, verbose_name="模型X字段2")
    model_filed3 = models.CharField(max_length=100, verbose_name="模型X字段3")
    model_filed4 = models.CharField(max_length=100, verbose_name="模型X字段4")
    model_filed5 = models.CharField(max_length=100, verbose_name="模型X字段5")
    model_filed6 = models.CharField(max_length=100, verbose_name="模型X字段6")
    model_filed7 = models.ForeignKey(ModelType, on_delete=models.CASCADE, blank=True, null=True,
                                          verbose_name="模型X字段7")

    def __str__(self):
        return self.model_filed1


class ModelA(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    modelx = models.ManyToManyField(ModelX, related_name='model_as')

    def __str__(self):
        return self.name


class ModelB(models.Model):
    model_a = models.ForeignKey(ModelA, on_delete=models.CASCADE, related_name='model_bs')
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title


class ModelC(models.Model):
    model_a = models.ForeignKey(ModelA, on_delete=models.CASCADE, related_name='model_cs')
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return self.title
