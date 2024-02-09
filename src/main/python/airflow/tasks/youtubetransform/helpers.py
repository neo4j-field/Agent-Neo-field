import time
from typing import List, Dict
from uuid import uuid4

def batch_method(lst, batch_size=500):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def prepare_new_nodes(data: List, embedding_service, playlist_id: str = "") -> List[Dict]:
    """
    format chunked data to be uploaded into neo4j graph.
    embedding must abide by rate limits: 60 requests / minute
    """

    total = len(data)
    new_nodes = data.copy()

    i = 0
    # print("total chunks to process: ", total)
    for chunk in new_nodes:
        

            # try:
        start = time.time()

        # make request
        # print("batch percent: ", str(round((i+1) / total, 4)*100)[:4], "%", " request", i+1, end="\r")
        chunk.update({  "index": str(uuid4()),
                        "playlist_id": playlist_id,
                        "embedding": embedding_service.generate_embedding(chunk['transcript'])})
        
        stop = time.time()
        # abide by rate limit (1 per sec)
        while stop - start < 1:
            stop = time.time()

        i+=1

            # except Exception as e:

                # if i < try_limit:
                #     i+=1
                #     time.sleep(i+1)
                #     continue
                # else:
                # print(e)
                # return new_nodes, i
            
    return new_nodes, i