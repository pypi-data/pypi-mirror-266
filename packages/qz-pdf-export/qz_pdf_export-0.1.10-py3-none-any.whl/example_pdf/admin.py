from django.contrib import admin

from pdfExport.admin import PdfAdmin
from .models import ModelA, ModelB, ModelType, ModelX, ModelC


# Register your models here.
@admin.register(ModelType)
class ModelTypeAdmin(PdfAdmin):
    list_display = ('name',)


@admin.register(ModelX)
class ModelXAdmin(PdfAdmin):
    list_display = ('model_filed1', 'model_filed2', 'model_filed3', 'pdf_show')
    pdf_fields = (('model_filed1', 'model_filed2'),
                  ('组标题1', {('model_filed3', 'model_filed4')}),
                  'model_filed5',
                  ('组标题2', {('model_filed6',)}),
                  'model_filed7')
    option_fields = ('model_filed7',)


class ModelBInline(admin.TabularInline):
    model = ModelB
    extra = 1  # 默认显示的空白关联对象数量

class ModelCInline(admin.TabularInline):
    model = ModelC
    extra = 1  # 默认显示的空白关联对象数量


class ModelAAdmin(PdfAdmin):
    list_display = ('name', 'description', 'pdf_show')  # 在Admin列表页显示的字段
    inlines = [ModelBInline, ModelCInline]  # 在ModelA的编辑页面嵌入ModelB的编辑表单
    # pdf要显示的字段
    pdf_related_fields = [

        ('modelx', '自定义标题x', (('model_filed1', 'model_filed2'),
                  ('组标题1', {('model_filed3', 'model_filed4')}),
                  'model_filed5',
                  ('组标题2', {('model_filed6',)}),
                  'model_filed7')),
        ('model_bs', '自定义标题b', ('title', 'content')),
        ('model_cs', '自定义标题c', ('title', 'content')),
    ]
    option_fields = ('model_filed7',)

    # pdf_related_fields = ('model_bs', 'model_cs')
    pdf_fields = (('name', 'description'),)
    # pdf标题
    pdf_title = 'pdf标题'
    # 要显示所有选项的字段
    # 左右上方小标题
    left_tip = ''
    right_tip = ''


# 注册ModelA到admin中，并使用ModelAAdmin进行定制
admin.site.register(ModelA, ModelAAdmin)


# 如果你还希望单独管理ModelB，也可以注册ModelB
class ModelBAdmin(PdfAdmin):
    list_display = ('title', 'content', 'model_a')  # 在Admin列表页显示的字段
    list_filter = ('model_a',)  # 列表页过滤器

class ModelCAdmin(PdfAdmin):
    list_display = ('title', 'content', 'model_a')  # 在Admin列表页显示的字段
    list_filter = ('model_a',)  # 列表页过滤器


admin.site.register(ModelB, ModelBAdmin)
admin.site.register(ModelC, ModelCAdmin)
