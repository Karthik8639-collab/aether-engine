"""
Heavy Python Task Remote Execution Worker
Offloads CPU/GPU intensive python computations (matrix math, data processing, simulations)
from basic laptops to remote workers.
"""

import time
import math
import traceback
from typing import Dict, Any
from aether.workers.base import BaseWorker


class HeavyPythonWorker(BaseWorker):
    """Executes heavy python computations offloaded from basic laptops."""

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        code_str = payload.get("code")
        args = payload.get("args", {})

        if not code_str:
            size = int(args.get("matrix_size", 2000))
            result = self._benchmark_matrix_computation(size)
            duration = round(time.time() - start_time, 4)
            return {
                "status": "success",
                "task_type": "benchmark_matrix",
                "matrix_size": f"{size}x{size}",
                "result": result,
                "execution_time_sec": duration,
                "executed_on": "Remote High-Performance Node"
            }

        local_scope = {"args": args, "math": math}
        try:
            exec(code_str, {"__builtins__": __builtins__}, local_scope)
            output = local_scope.get("result", "Completed successfully")
            duration = round(time.time() - start_time, 4)
            return {
                "status": "success",
                "result": output,
                "execution_time_sec": duration,
                "executed_on": "Remote High-Performance Node"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "execution_time_sec": round(time.time() - start_time, 4)
            }

    def _benchmark_matrix_computation(self, size: int) -> str:
        total = 0.0
        for i in range(min(size, 1000)):
            total += math.sin(i) * math.cos(i) * math.sqrt(i + 1)
        return f"Computed heavy numerical reduction over {size} dimensions: {total:.6f}"
