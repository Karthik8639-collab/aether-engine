"""
Speculative Local Execution & Remote Stream Synchronizer Engine
Generates 0ms local speculative previews while seamlessly merging high-precision remote GPU streams.
"""

import time
import asyncio
from typing import AsyncGenerator, Callable, Any, Dict, Optional


class SpeculativeStreamChunk:
    def __init__(self, content: Any, is_speculative: bool, chunk_index: int):
        self.content = content
        self.is_speculative = is_speculative
        self.chunk_index = chunk_index
        self.timestamp = time.time()


class SpeculativeEngine:
    """Manages 0ms speculative local preview and asynchronous remote stream synchronization."""

    def __init__(self, local_preview_fn: Optional[Callable[[Dict[str, Any]], Any]] = None):
        self.local_preview_fn = local_preview_fn

    async def execute_hybrid_stream(
        self,
        task_payload: Dict[str, Any],
        remote_stream_generator: AsyncGenerator[Any, None]
    ) -> AsyncGenerator[SpeculativeStreamChunk, None]:
        chunk_idx = 0

        # Step 1: Yield instant speculative local output if local fn provided
        if self.local_preview_fn:
            try:
                spec_content = self.local_preview_fn(task_payload)
                yield SpeculativeStreamChunk(
                    content=spec_content,
                    is_speculative=True,
                    chunk_index=chunk_idx
                )
                chunk_idx += 1
            except Exception:
                pass

        # Step 2: Stream refined remote chunks
        async for remote_chunk in remote_stream_generator:
            yield SpeculativeStreamChunk(
                content=remote_chunk,
                is_speculative=False,
                chunk_index=chunk_idx
            )
            chunk_idx += 1
