import math


class FilterPagination:

    '''
    # Custom Filter & Pagination
    @request: request (object), model_refrence (object)
    @response: dataset (dictionary)
    '''
    def filter_and_pagination(request, model_refrence):
        model_fields = [field.name for field in model_refrence._meta.get_fields()]
        filter_params = request.GET
        custom_filter = {}

        if filter_params:
            for k, v in filter_params.items():
                if k in model_fields:
                    if 'ForeignKey' == model_refrence._meta.get_field(k).get_internal_type():
                        custom_filter.update({k : v})
                    else:
                        custom_filter.update({k + '__icontains': v})
                else:
                    k_rsplit = k.rsplit('__', 1)
                    if (k_rsplit[-1] in ['from', 'to']):
                        k_type = model_refrence._meta.get_field(k_rsplit[0]).get_internal_type()
                        if (k_type in ['DateField', 'DateTimeField', 'DecimalField', 'FloatField', 'IntegerField', 'PositiveIntegerField']):
                            compare = '__gte' if 'from' == k_rsplit[1] else '__lte'
                            if 'DateTimeField' == k_type:
                                v = v + ' 00:00:00' if 'from' == k_rsplit[-1] else v + ' 23:59:59'
                            custom_filter.update({k_rsplit[0] + compare: v})
                    elif ('array' == k_rsplit[-1]):
                        custom_filter.update({k_rsplit[0] + '__in': v})
                    elif ('exact' == k_rsplit[-1]):
                        custom_filter.update({k_rsplit[0] + '__exact': v})
                    else:
                        pass

        queryset_filter = model_refrence.objects.filter(**custom_filter)
                    
        order_by_field = filter_params['order_by'] if (('order_by' in filter_params) and (filter_params['order_by'] in model_fields)) else 'id'
        order_type = '' if 'order_type' in filter_params else '-'
        order_by = order_type + order_by_field

        per_page = filter_params['per_page'] if 'per_page' in filter_params else 20
        page_no = filter_params['page_no'] if 'page_no' in filter_params else 1
    
        start_limit = ((int(per_page) * int(page_no)) - int(per_page))
        end_limit = int(per_page) * int(page_no)

        total_object_count = queryset_filter.count()
        total_pages = math.ceil( int(total_object_count) / int(per_page) )

        queryset = queryset_filter.order_by(order_by)[start_limit:end_limit]
        
        dataset = {
            'queryset': queryset,
            'pagination': {
                'per_page': per_page,
                'current_page': page_no,
                'total_count': total_object_count,
                'total_pages': total_pages
            }
        }
        return dataset