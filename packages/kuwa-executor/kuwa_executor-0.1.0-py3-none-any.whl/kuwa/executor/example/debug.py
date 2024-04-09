import os
import sys
import asyncio
import logging
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kuwa.executor import LLMExecutor

logger = logging.getLogger(__name__)

class DebugExecutor(LLMExecutor):
    def __init__(self):
        super().__init__()

    def extend_arguments(self, parser):
        """
        Override this method to add custom command-line arguments.
        """
        parser.add_argument('--delay', type=float, default=0.02, help='Inter-token delay')

    def setup(self):
        if not self.LLM_name:
            self.LLM_name = "debug"

        self.stop = False

    async def llm_compute(self, data):
        try:
            self.stop = False
            for i in "".join([i['msg'] for i in json.loads(data.get("input"))]).strip():
                yield i
                if self.stop:
                    self.stop = False
                    break
                await asyncio.sleep(self.args.delay)
        except Exception as e:
            logger.exception("Error occurs during generation.")
            yield str(e)
        finally:
            logger.debug("finished")

    async def abort(self):
        self.stop = True
        logger.debug("aborted")
        return "Aborted"

if __name__ == "__main__":
    executor = DebugExecutor()
    executor.run()