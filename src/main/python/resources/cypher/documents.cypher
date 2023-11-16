UNWIND $params AS param
MERGE (d:Document {index: param.index})
SET
    d.text = param.chunk_text,
    d.text_len = param.chunk_len,
    d.url = param.chunk_url,
    d.source_type = param.source_type,
    d.topic = param.topic,
    d.embedding = param.embedding