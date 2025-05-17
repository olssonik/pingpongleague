import { ApiResponse } from "@/types";

// Mock API data that would come from a real backend
export const mockApiData: ApiResponse = {
  players: [
    { username: "jack", elo: 330 },
    { username: "oli", elo: 470 }
  ],
  games: [
    { players: ["jack", "oli"], winner: "oli", date: "Today, 14:30" }
  ]
};
