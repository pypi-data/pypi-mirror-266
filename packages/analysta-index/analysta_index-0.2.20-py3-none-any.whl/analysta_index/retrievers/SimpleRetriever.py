# Copyright (c) 2023 Artem Rozumenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from langchain_core.retrievers import BaseRetriever
from typing import Any, Dict, List, Optional
from langchain_core.callbacks.manager import Callbacks
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from ..tools.log import print_log


class SimpleRetriever(BaseRetriever):
    vectorstore: Any  # Instance of vectorstore
    doc_library: str  # Name of the document library
    top_k: int  # Number of documents to return
    page_top_k: int = 10
    weights: Dict[str, float] = {
        'keywords': 0.2,
        'document_summary': 0.5,
        'data': 0.3,
    }
    fetch_k: int = 10
    lower_score_better: bool = True
    document_debug: bool = False
    no_cleanse: bool = False

    class Config:
        arbitrary_types_allowed = True

    def _rerank_documents(self, documents: List[tuple]):
        """ Rerank documents """
        _documents = []
        #
        for (document, score) in documents:
            item = {
                "page_content": document.page_content,
                "metadata": document.metadata,
                "score": score * self.weights.get(document.metadata['type'], 1.0),
            }
            #
            if "data" in item["metadata"]:
                item["page_content"] = item["metadata"].pop("data")
            #
            _documents.append(item)
        #
        return sorted(
            _documents,
            key=lambda x: x["score"],
            reverse=not self.lower_score_better,
        )

    def _make_documents(self, docs):
        _documents = []
        #
        for doc in docs:
            _documents.append(
                Document(
                    page_content=doc["page_content"],
                    metadata=doc["metadata"],
                )
            )
        #
        return _documents

    def get_relevant_documents(
        self,
        input: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs: Any,
    ) -> List[Document]:
        docs = self.vectorstore.similarity_search_with_score(
            input,
            filter={'library': self.doc_library},
            k=self.fetch_k,
        )
        #
        if self.document_debug:
            print_log("similarity_search =", docs)
        #
        docs = self._rerank_documents(docs)
        #
        if self.document_debug:
            print_log("rerank_documents =", docs)
        #
        docs = self._make_documents(docs[:self.top_k])
        #
        if self.document_debug:
            print_log("make_documents =", docs)
        #
        return docs
