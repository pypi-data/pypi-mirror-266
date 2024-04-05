from typing import Optional

from django.http import HttpRequest, HttpResponse

from rules.contrib.views import permission_required

from aleksis.core.decorators import pwa_cache
from aleksis.core.util.pdf import render_pdf

from .util.chronos_helpers import (
    get_substitutions_context_data,
)


@pwa_cache
@permission_required("chronos.view_substitutions_rule")
def substitutions_print(
    request: HttpRequest,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
) -> HttpResponse:
    """View all substitutions on a specified day."""
    context = get_substitutions_context_data(request, year, month, day, is_print=True)
    return render_pdf(request, "chronos/substitutions_print.html", context)
