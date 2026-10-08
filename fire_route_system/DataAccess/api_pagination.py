from django.core.paginator import Paginator
from django.http import JsonResponse


def list_response(request, queryset, serialize):
    """Keep legacy JSON arrays while bounding each response to 100 rows."""
    try:
        size = max(1, min(100, int(request.GET.get('page_size', 100))))
    except (TypeError, ValueError):
        size = 100
    page = Paginator(queryset.order_by('pk'), size).get_page(request.GET.get('page'))
    response = JsonResponse([serialize(item) for item in page], safe=False)
    response['X-Total-Count'] = str(page.paginator.count)
    response['X-Page'] = str(page.number)
    response['X-Page-Size'] = str(size)
    response['X-Total-Pages'] = str(page.paginator.num_pages)
    links = []
    for relation, number in [('next', page.number + 1), ('prev', page.number - 1)]:
        if 1 <= number <= page.paginator.num_pages:
            query = request.GET.copy()
            query['page'] = number
            query['page_size'] = size
            links.append(f'<{request.path}?{query.urlencode()}>; rel="{relation}"')
    if links:
        response['Link'] = ', '.join(links)
    return response
