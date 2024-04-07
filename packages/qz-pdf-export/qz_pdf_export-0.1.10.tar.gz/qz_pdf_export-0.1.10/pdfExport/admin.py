from django.apps import apps
from django.contrib import admin, messages
from django.urls import path, reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html

from django.core.exceptions import FieldDoesNotExist
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render


class OptionsShow:
    """
    一个用于标记字段需要特殊显示逻辑的标志类。
    """
    pass


class PdfAdmin(admin.ModelAdmin):
    pdf_fields = []
    option_fields = []
    pdf_related_fields = []
    pdf_title = ''
    right_tip = ''
    left_tip = ''
    pdf_template = 'pdfExport/base_pdf_template.html'
    change_form_template = 'pdfExport/pdf_export_change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('pdf_export/<int:pk>/', self.admin_site.admin_view(self.pdf_export), name='pdf_export'),
        ]
        return custom_urls + urls

    def pdf_show(self, obj):
        # 获取当前模型的 app_label 和 model_name
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        # 构建 URL
        url = f'/admin/{app_label}/{model_name}/pdf_export/{obj.pk}/'

        return format_html('<a class="button" href="{}">PDF导出</a>', url)

    pdf_show.short_description = 'PDF导出'
    pdf_show.allow_tags = True

    def pdf_export(self, request, pk):
        context = self.get_pdf_context(pk)
        context['title'] = self.pdf_title
        context['right_tip'] = self.right_tip
        context['left_tip'] = self.left_tip
        return render(request, self.pdf_template, context)



    def get_pdf_context(self, pk):
        model = self.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        context = {}
        context['grouped_fields'] = self.extract_pdf_data(app_label, model_name, pk)
        if self.pdf_related_fields:
            context['related_grouped_fields'] = self.extract_pdf_related_data(app_label, model_name, pk)
        return context

    def extract_pdf_related_data(self, app_label, model_name, pk):
        model = apps.get_model(app_label, model_name)
        instance = model.objects.get(pk=pk)

        related_data = {}
        for field_name, custom_title, fields_structure in self.pdf_related_fields:
            related_objects = getattr(instance, field_name).all()
            data_list = []
            for obj in related_objects:
                data_list.append(self.process_fields_structure_for_related(obj, fields_structure))
            related_data[custom_title] = data_list

        return related_data

    def process_fields_structure_for_related(self, obj, fields_structure):
        group_data = []
        option_fields = getattr(self, 'option_fields', [])
        for item in fields_structure:
            if isinstance(item, tuple):
                # 处理字段组或单个字段组合
                if isinstance(item[1], set):
                    # 处理具有自定义组标题的字段组
                    group_title, fields_set = item
                    field_group = {"group_title": group_title, "fields": []}
                    for sub_field_tuple in fields_set:
                        for sub_field in sub_field_tuple:
                            field_data = self.process_field(obj._meta.get_field(sub_field), obj, sub_field, option_fields)
                            field_group["fields"].append(field_data)
                    group_data.append(field_group)
                else:
                    # 处理没有自定义组标题的字段组合
                    field_group = {"group_title": None, "fields": []}
                    for field_name in item:
                        field_data = self.process_field(obj._meta.get_field(field_name), obj, field_name, option_fields)
                        field_group["fields"].append(field_data)
                    group_data.append(field_group)
            else:
                # 处理单个字段
                field_data = self.process_field(obj._meta.get_field(item), obj, item, option_fields)
                group_data.append({"group_title": None, "fields": [field_data]})
        return group_data

    def extract_pdf_data(self, app_label, model_name, pk):
        model = apps.get_model(app_label=app_label, model_name=model_name)
        obj = model.objects.get(pk=pk)
        grouped_fields = []
        option_fields = getattr(self, 'option_fields', [])

        for item in self.pdf_fields:
            if isinstance(item, tuple):
                if isinstance(item[1], set):
                    group_title, fields_set = item
                    field_group = {"group_title": group_title, "fields": []}
                    for sub_field_tuple in fields_set:
                        for sub_field in sub_field_tuple:
                            field_obj = model._meta.get_field(sub_field)
                            field_data = self.process_field(field_obj, obj, sub_field, option_fields)
                            field_group["fields"].append(field_data)
                    grouped_fields.append(field_group)
                else:
                    field_group = {"group_title": None, "fields": []}
                    for sub_field in item:
                        field_obj = model._meta.get_field(sub_field)
                        field_data = self.process_field(field_obj, obj, sub_field, option_fields)
                        field_group["fields"].append(field_data)
                    grouped_fields.append(field_group)
            else:
                field_obj = model._meta.get_field(item)
                field_data = self.process_field(field_obj, obj, item, option_fields)
                grouped_fields.append({"group_title": None, "fields": [field_data]})

        return grouped_fields

    def process_field(self, field_obj, obj, field_name, option_fields):
        """处理单个字段，获取其详细信息"""
        if field_name in option_fields:
            # 选项字段处理逻辑
            all_options = field_obj.related_model.objects.all()
            current_option = getattr(obj, field_name, None)
            options_list = [{'name': str(option), 'selected': (option == current_option)} for option in all_options]
            return {
                "verbose_name": field_obj.verbose_name,
                "value": options_list,
                "is_option_field": True
            }
        else:
            # 非选项字段处理逻辑
            return {
                "verbose_name": field_obj.verbose_name,
                "value": getattr(obj, field_name, ''),
                "is_option_field": False
            }
