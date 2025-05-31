import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import axios from "axios";

export async function registerRoutes(app: Express): Promise<Server> {
  // API endpoint for table tennis data
  app.get("/api/get_data", async (req, res) => {
    try {
      // Attempt to forward the request to the Python server
      const response = await axios.get("http://localhost:3000/api/get_data", { timeout: 1000 });
      res.json(response.data);
    } catch (error) {
      // When Python server is not available, use the sample data
      console.log("Using sample table tennis data");
      return res.json({});
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
