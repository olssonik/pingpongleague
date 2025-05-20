import type { Express } from "express";
import { createServer, type Server } from "http";

export async function registerRoutes(app: Express): Promise<Server> {

  app.get('/api/get_data', async (req, res) => {
    try {
      const response = await fetch('/api/get_data'); // your python server URL
      if (!response.ok) throw new Error('Failed to fetch data');
      const data = await response.json();
      res.json(data);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  app.get('/api/get_data', async (req, res) => {
    try {
      const response = await fetch('/api/get_data');
      if (!response.ok) throw new Error('Failed to fetch data');
      const data = await response.json();
      res.json(data);
    } catch (err) {
      res.status(500).json({ error: err.message });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
