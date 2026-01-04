from flask import Blueprint, request, jsonify
from app.database import db
from app.models.knowledge_doc import KnowledgeDoc
from app.services.knowledge_service import KnowledgeService

knowledge_bp = Blueprint("knowledge", __name__, url_prefix="/api/knowledge")

@knowledge_bp.route("/docs", methods=["POST"])
def create_doc():
    data = request.get_json(force=True)
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return jsonify({"error": "title and content are required"}), 400

    doc = KnowledgeDoc(
        title=title,
        content=content,
        source=data.get("source"),
        tags=data.get("tags"),
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(doc.to_dict()), 201

@knowledge_bp.route("/query", methods=["GET"])
def query_knowledge():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400

    result = KnowledgeService.query(q, top_k=int(request.args.get("top_k", 5)))
    return jsonify(result)
