"""
Tests for Speculative Local Execution Engine
"""

import sys
import os
import asyncio
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.speculative import SpeculativeEngine


@pytest.mark.asyncio
async def test_speculative_stream():
    engine = SpeculativeEngine(local_preview_fn=lambda p: "Local Preview")

    async def dummy_remote():
        yield "Remote Result"

    chunks = []
    async for chunk in engine.execute_hybrid_stream({}, dummy_remote()):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].is_speculative is True
    assert chunks[0].content == "Local Preview"
    assert chunks[1].is_speculative is False
    assert chunks[1].content == "Remote Result"
