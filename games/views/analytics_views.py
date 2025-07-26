
try:
    from .analytics.genre_views import graphs_by_gender, genre_performance_report
except ImportError:
    # Fallback temporal si hay problemas con la nueva estructura
    def graphs_by_gender(request):
        from django.http import HttpResponse

        return HttpResponse("Vista en mantenimiento - Refactorización en progreso")

    def genre_performance_report(request):
        from django.http import JsonResponse

        return JsonResponse({"error": "Vista en mantenimiento"}, status=503)


