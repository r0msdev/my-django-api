import math

from .errors import error_response

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def parse_pagination(request):
    """Parse ?page and ?pageSize query params from request.
    Returns (page, page_size, error_response). error_response is None on success."""
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except ValueError:
        return None, None, error_response('page must be a positive integer.')
    try:
        page_size = min(
            PAGE_SIZE_MAX,
            max(1, int(request.GET.get('pageSize', PAGE_SIZE_DEFAULT))),
        )
    except ValueError:
        return None, None, error_response('pageSize must be a positive integer.')
    return page, page_size, None


def paginate_queryset(queryset, page, page_size):
    """Slice a queryset and return (items, meta dict)."""
    total = queryset.count()
    total_pages = max(1, math.ceil(total / page_size))
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    items = queryset[offset: offset + page_size]
    meta = {
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': total_pages,
    }
    return items, meta
