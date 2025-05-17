import { useQuery } from "@tanstack/react-query";
import { calculatePlayerStats } from "@/lib/utils";
import { PingPongData, ApiResponse } from "@/types";

// Real API request function that fetches from the /get_data endpoint
const fetchPingPongData = async (): Promise<PingPongData> => {
  try {
    const response = await fetch('/get_data');
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    const data: ApiResponse = await response.json();
    // Process the data
    return calculatePlayerStats(data);
  } catch (error) {
    console.error('Error fetching ping pong data:', error);
    throw error;
  }
};

export function usePingPongData() {
  return useQuery({
    queryKey: ['/get_data'],
    queryFn: fetchPingPongData,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
