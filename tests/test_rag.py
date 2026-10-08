from sentinelia.rag import DocumentStore


def test_retrieval_orders_relevant_chunk_first():
    store = DocumentStore()
    store.add("contrat.txt", b"Le contrat de maintenance ascenseur est confie a LiftAzur.")
    store.add("devis.txt", b"La toiture sera reparee par ToitPro pour 12000 euros.")
    results = store.search("Quel prestataire repare la toiture ?", 2)
    assert results[0].filename == "devis.txt"


def test_capacity_limit():
    store = DocumentStore(max_documents=1)
    store.add("one.txt", b"Premier document suffisamment detaille.")
    try:
        store.add("two.txt", b"Second document suffisamment detaille.")
    except ValueError as exc:
        assert "capacity" in str(exc).lower()
    else:
        raise AssertionError("Expected the capacity limit")

