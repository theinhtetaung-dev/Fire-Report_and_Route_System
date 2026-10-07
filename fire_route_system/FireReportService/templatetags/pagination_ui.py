from django import template

register = template.Library()


@register.inclusion_tag('pagination_controls.html', takes_context=True)
def compact_pagination(context, show_per_page=False):
    page = context.get('page_obj')
    if page is None:
        return {}
    request = context.get('request')
    query = request.GET.copy() if request else None

    def url(number):
        if query is None:
            return f'?page={number}'
        params = query.copy()
        params['page'] = number
        return '?' + params.urlencode()

    pages = [
        {'number': number, 'url': url(number) if number != page.paginator.ELLIPSIS else '',
         'current': number == page.number}
        for number in page.paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=3)
    ]
    return {
        'page_obj': page, 'pages': pages,
        'previous_url': url(page.previous_page_number()) if page.has_previous() else '',
        'next_url': url(page.next_page_number()) if page.has_next() else '',
        'query_pairs': [(key, value) for key, values in query.lists() if key != 'page'
                        for value in values] if query is not None else [],
        'show_per_page': show_per_page, 'per_page': page.paginator.per_page,
    }
