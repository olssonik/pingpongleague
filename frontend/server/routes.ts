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
  players: {
    "0": {
      username: "Oli", 
      elo: 531,
      achievements: [
        { badge_id: "mvp_2024", name: "MVP 2024", description: "Most Valuable Player of 2024", icon_url: "🏆" },
        { badge_id: "winning_streak", name: "Winning Streak", description: "Won 5 games in a row", icon_url: "🔥" }
      ]
    },
    "1": {
      username: "Jack", 
      elo: 347,
      achievements: [
        { badge_id: "sportsmanship", name: "Sportsmanship", description: "Great attitude and fair play", icon_url: "⭐" }
      ]
    },
    "2": {
      username: "Ed", 
      elo: 403,
      achievements: []
    },
    "3": {
      username: "Jake", 
      elo: 366,
      achievements: [
        { badge_id: "rookie_2024", name: "Rookie of the Year", description: "Outstanding performance as a new player", icon_url: "🌟" }
      ]
    }
  }
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

  // API endpoint for tournaments
  app.get("/api/get_tournaments", async (req, res) => {
    try {
      // Attempt to forward the request to the Python server
      const response = await axios.get("http://localhost:3000/api/get_tournaments", { timeout: 1000 });
      res.json(response.data);
    } catch (error) {
      // When Python server is not available, return empty tournaments
      console.log("Python server not available for tournaments");
      return res.json({ tournaments: [] });
    }
  });

  // API endpoint for individual tournament details
  app.get("/api/tournament/:id", async (req, res) => {
    try {
      // Attempt to forward the request to the Python server
      const response = await axios.get(`http://localhost:3000/api/tournament/${req.params.id}`, { timeout: 1000 });
      res.json(response.data);
    } catch (error) {
      // When Python server is not available, return not found
      console.log("Python server not available for tournament details");
      return res.json({ message: "Tournament not found or server unavailable" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
