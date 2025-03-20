def paginate_query(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return pagination.items, pagination.page, pagination.per_page, pagination.pages, pagination.total