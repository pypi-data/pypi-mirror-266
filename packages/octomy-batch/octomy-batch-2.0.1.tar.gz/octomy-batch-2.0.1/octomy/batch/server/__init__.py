from multiprocessing import Process, connection
import asyncio
import logging
import octomy.batch
import octomy.config
import octomy.db
import os
import signal

logger = logging.getLogger(__name__)


class Server:
	
	config:octomy.config.OctomyConfig
	
	def __init__(self, config:octomy.config.OctomyConfig):
		self.config = config
		self.term_received = False

		def handler(signum, frame):
			logger.info(f"{signum} signal received, terminating gracefully")
			self.term_received = True

		signal.signal(signal.SIGABRT, handler)

	async def verify(self):
		db:octomy.db.Database = octomy.db.get_database(self.config)
		bp:octomy.batch.Processor = octomy.batch.Processor(self.config, db)
		return await bp.verify()


	def sync_wrapper(self, num):
		asyncio.run(self.wrapper(num))

	async def wrapper(self, num):
		logger.info(f"Batch worker {num} started with id:{os.getpid()}, parent:{os.getppid()}")
		# Each instance must have a separate database connection and processor
		db:octomy.db.Database = octomy.db.get_database(self.config)
		bp:octomy.batch.Processor = octomy.batch.Processor(self.config, db)
		while not self.term_received:
			# Do some work
			await bp.process()
		logger.info(f"Worker {num} stopped")

	def start(self, num):
		logger.info(f"Batch worker {num} starting...")
		worker = Process(target=self.sync_wrapper, args=(num,))
		self.workers.append(worker)
		worker.start()
		return worker

	# Start server and serve forever
	async def run(self):
		self.workers = []
		workers_count = self.config.get("batch-workers", 1)
		logger.info(f"Starting {workers_count} workers")
		num = 0
		for _ in range(workers_count):
			self.start(num)
			num += 1
		# Restart workes that terminate for whatever reason (they will self terminate on errors)
		while not self.term_received:
			connection.wait(worker.sentinel for worker in self.workers)
			for worker in self.workers:
				logger.info(f"Batch worker terminating...")
				worker.join()
				self.workers.remove(worker)
				logger.info(f"Batch worker terminated")
				self.start(num)
				num += 1
		logger.info(f"Server stopping:")
		for worker in self.workers:
			logger.info(f"Batch worker terminating...")
			worker.join()
			self.workers.remove(worker)
		logger.info(f"Server stopped")
