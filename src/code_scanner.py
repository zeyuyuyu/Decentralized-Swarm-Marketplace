import time
import random
import requests
from typing import List

class ScrapingSwarm:
    def __init__(self, urls: List[str], num_agents: int = 10, delay: float = 0.1):
        self.urls = urls
        self.num_agents = num_agents
        self.delay = delay
        self.agents = [ScrapeAgent(self.urls, self.delay) for _ in range(self.num_agents)]

    def start(self):
        for agent in self.agents:
            agent.start()

    def stop(self):
        for agent in self.agents:
            agent.stop()

class ScrapeAgent:
    def __init__(self, urls: List[str], delay: float):
        self.urls = urls
        self.delay = delay
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            self.scrape()
            time.sleep(self.delay)

    def stop(self):
        self.running = False

    def scrape(self):
        url = random.choice(self.urls)
        try:
            response = requests.get(url)
            print(f"Scraped data from: {url}")
        except:
            print(f"Failed to scrape data from: {url}")
