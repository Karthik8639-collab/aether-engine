"""
Example 02: Zero-Latency Speculative LLM Token Generation with Remote VRAM Refinement
"""

import sys
import os
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aether.core.speculative import SpeculativeEngine
from aether.workers.llm_worker import LLMWorker


async def main():
    print("Aether Engine Example 02: Zero-Latency Speculative Stream")
    print("=" * 60)

    def instant_local_preview(payload):
        return f"Instant Speculative Preview for prompt '{payload.get('prompt')}'"

    engine = SpeculativeEngine(local_preview_fn=instant_local_preview)
    worker = LLMWorker()

    prompt = "How does Aether Engine optimize basic laptops?"

    print(f"Prompt: {prompt}\n")
    print("Streaming Tokens (Notice [SPECULATIVE] instant preview followed by [REFINED] remote VRAM stream):\n")

    async for chunk in engine.execute_hybrid_stream({"prompt": prompt}, worker.stream_inference(prompt)):
        tag = "[SPECULATIVE 0ms]" if chunk.is_speculative else "[REFINED VRAM]"
        print(f"{tag} Chunk #{chunk.chunk_index}: {chunk.content}")
        await asyncio.sleep(0.02)


if __name__ == "__main__":
    asyncio.run(main())
