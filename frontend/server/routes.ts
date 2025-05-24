import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import axios from "axios";

// Sample data as specified in the user's request
const sampleData = {
  games: [
    { id: 1, players: ["Oli", "Jack"], winner: "Oli", date: null },
    { id: 2, players: ["Ed", "Jake"], winner: "Ed", date: null },
    { id: 3, players: ["Oli", "Ed"], winner: "Oli", date: null },
    { id: 4, players: ["Jack", "Jake"], winner: "Jack", date: null },
    { id: 5, players: ["Oli", "Jake"], winner: "Oli", date: null },
    { id: 6, players: ["Ed", "Jack"], winner: "Ed", date: null },
    { id: 7, players: ["Jake", "Oli"], winner: "Oli", date: null },
    { id: 8, players: ["Jack", "Ed"], winner: "Jack", date: null }
  ],
  players: [
    { username: "Oli", elo: 531 },
    { username: "Jack", elo: 347 },
    { username: "Ed", elo: 403 },
    { username: "Jake", elo: 366 }
  ]
};

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
      return res.json(sampleData);
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
