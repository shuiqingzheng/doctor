import operator
from rest_framework import filters
from django.db import models
from functools import reduce
from myuser.models import PatientUser


class SearchDiaDetail(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        print(search_terms)

        if not search_terms:
            return queryset

        # 查询姓名 or 手机号
        orm_lookups = [
            'owner__username__icontains', 'owner__phone__icontains'
        ]
        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))

        patient_list = PatientUser.objects.filter(reduce(operator.and_, conditions))
        queryset = queryset.filter(patient_id__in=[p.id for p in patient_list])
        return queryset
