from django.shortcuts import render
from django.views import View
from importfile.constants import NAME_TO_FIELD, DEFAULT_INFO
from medicine.models import Medicine
import pandas as pd


class ImportFileView(View):
    """
    - 导入文件
    """

    def get(self, request, *args, **kwargs):
        context = {
            'site_header': '汉典云健康系统',
        }
        return render(request, template_name='admin/importdb.html', context=context)

    def post(self, request, *args, **kwargs):
        file_data = request.FILES
        a = file_data.get('file')
        context = {
            'site_header': '汉典云健康系统',
        }

        if not a:
            context.update({'error_msg': '未选择文件'})
            return render(request, template_name='admin/importdb.html', context=context)

        demo_file_path = './importfile/medicine-file.xls'

        with open('{}'.format(demo_file_path), 'wb') as f:
            for i in a.chunks():
                f.write(i)

        res = pd.read_excel(demo_file_path, index_col=None, header=None)

        start_row = 6
        index_field = dict()
        field_to_name = {value: key for key, value in NAME_TO_FIELD.items()}

        # 简单的模板验证
        if len(res.columns) != 10:
            context.update({'error_msg': '文件不符合模板'})
            return render(request, template_name='admin/importdb.html', context=context)

        for col in res.columns:
            val = res.iat[start_row, col]
            v = None
            if not pd.isna(val):
                v = val.replace('\n', '')

            if v in field_to_name.keys():
                index_field.update({
                    '{}'.format(field_to_name.get(v)): '{}'.format(col)
                })

        for row in res.index[start_row + 1:]:
            a = dict()
            for field_name, index in index_field.items():
                value = res.iat[row, int(index)]

                if isinstance(value, str):
                    value = value.replace('\n', '')

                if pd.isna(value) or pd.isnull(value):
                    continue

                a.update({
                    field_name: value
                })

            a.update({
                'good_for': a.get('officical_name'),
                'detail': a.get('officical_name'),
            })

            a.update(DEFAULT_INFO)

            obj = Medicine.objects.filter(product_name=a.get('product_name'), officical_name=a.get('officical_name'))
            if obj and len(obj) == 1:
                try:
                    obj.update(**a)
                except Exception as e:
                    context.update({'error_msg': '保存错误,错误信息:{}'.format(e)})
                    return render(request, template_name='admin/importdb.html', context=context)
                continue
            else:
                continue

            if len(a) == 11:
                try:
                    Medicine.objects.create(**a)
                except Exception as e:
                    context.update({'error_msg': '保存错误,错误信息:{}'.format(e)})
                    return render(request, template_name='admin/importdb.html', context=context)
        context.update({'success_msg': '导入成功'})
        return render(request, template_name='admin/importdb.html', context=context)
