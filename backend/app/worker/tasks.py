from app.worker.celery_app import celery_app
@celery_app.task(queue="documents")
def process_document(document_id: str):
    # Lo implementamos en el Punto 7
    print(f"Processing document: {document_id}")
    return {"status": "ok"}


@celery_app.task(queue="agents")
def run_agent(agent_type: str, document_id: str):
    # Lo implementamos en el Punto 11
    print(f"Running agent {agent_type} on {document_id}")
    return {"status": "ok"}