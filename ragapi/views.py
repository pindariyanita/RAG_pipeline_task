from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .pipeline import Generator

chunks, metadata = Generator().load_pdf("https://www.medicare.gov/publications/10050-medicare-and-you.pdf")
gen = Generator()

SIMILARITY_THRESHOLD = 0.3
@require_POST
def query_view(request):
    try:
        body = json.loads(request.body)
        query = body.get("query", "").strip()

        if not query:
            return JsonResponse({"error": "Query cannot be empty."}, status=400)

        if not gen or not chunks:
            return JsonResponse({"error": "RAG system not initialized."}, status=500)

        best_chunk, page_number, similarity_score, chunk_size = gen.get_best_chunk(query, chunks, metadata)
        if not best_chunk or similarity_score < SIMILARITY_THRESHOLD:
            return JsonResponse({"error": "No relevant information found for the given query."}, status=404)

        result = gen.generate(query, best_chunk, page_number, chunk_size, similarity_score)
        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

